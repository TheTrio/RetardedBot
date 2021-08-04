from discord import Embed, Color
from discord.errors import InvalidArgument
from discord.ext import commands
from discord.ext import tasks
import discord
from datetime import datetime, timedelta
import os
import random
from collections import defaultdict

from discord.flags import Intents

from src import Utils, Message, data, user_ids, ENV

intents = Intents.all()
bot = commands.Bot(command_prefix='ret ', intents=intents)

# EVENTS


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    check_ded_chat.start()
    thought_of_the_day.start()
    get_gifs.start()
    bot.last_deleted_message = {}
    bot.last_message_edited = {}
    bot.authorized_users = [
        user_ids['vroon'],
        user_ids['shashwat']
    ]
    bot.current_vc_time = defaultdict(lambda: timedelta(days=0, seconds=0))
    bot.general_id = 850286477660389396 if ENV == 'PRODUCTION' else 821455617309933638
    bot.time_spent = Utils.get_time_data()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name=" with ur mom"),
        status=discord.Status.dnd
    )


@bot.event
async def on_message(message):
    # do nothing when the message a) originated from the bot itself
    #                             b) was in a specific chat group
    if message.author == bot.user:
        return
    if message.guild is None:
        if message.author.id in bot.authorized_users or message.author.id == 785231710638833714:
            try:
                embed = Utils.notice_to_embed(message.content, message.attachments)
                await send_notice(embed=embed)
            except InvalidArgument:
                await message.channel.send("That doesn't seem like the right format")
        else:
            await message.channel.send("I'm sorry. You don't seem to have the permission to do that")
        return
    if message.channel.id == 824588988287287317:
        return
    bot.last_message = message
    if hasattr(bot, 'messages_in_a_minute_count'):
        if message.created_at.minute == getattr(bot, 'last_message_minute', None):
            bot.messages_in_a_minute_count += 1
            if bot.messages_in_a_minute_count % 15 == 0:
                await message.channel.send('alive chet')
        else:
            bot.messages_in_a_minute_count = 0
    else:
        bot.messages_in_a_minute_count = 0
    bot.last_message_minute = message.created_at.minute
    if check_ded_chat.seconds == 15:
        check_ded_chat.change_interval(seconds=5)

    await Message.process_message(message, bot, data)

    message.content = message.content.lower()
    await bot.process_commands(message)


@ bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    bot.last_deleted_message[message.channel.id] = Message(message)
    if Utils.happens(0.5):
        await message.channel.send(data['images']['tananun'])


@bot.event
async def on_message_edit(before, after):
    if not before.author.bot:
        bot.last_message_edited[before.channel.id] = Message(before)


@bot.event
async def on_voice_state_update(member, before, after):
    # don't count time of bots
    if member.bot:
        return
    if Utils.vc_joined(before, after):
        bot.current_vc_time[member.id] = datetime.now()
    elif Utils.vc_left(before, after):
        if member.id in bot.current_vc_time:
            bot.current_vc_time[member.id] = datetime.now() - bot.current_vc_time[member.id]
            bot.time_spent[member.id] += bot.current_vc_time[member.id]
            bot.time_spent = Utils.sort_default_dict(bot.time_spent)
            Utils.update_time_data(bot.time_spent)
            del bot.current_vc_time[member.id]
        else:
            # Not much to do
            print('In VC before bot started')


# TASKS

@ tasks.loop(minutes=5.0)
async def check_ded_chat():
    if hasattr(bot, 'last_message'):
        if datetime.now() - bot.last_message.created_at >= timedelta(minutes=30):
            await bot.last_message.channel.send(random.choice(data['available_choices']['ded']))
            check_ded_chat.change_interval(hours=3)


@ tasks.loop(hours=24)
async def thought_of_the_day():
    '''Sets a thought for the current day. Sends the same when called ret thought'''
    while True:
        temp = random.choice(data['available_choices']['thought'])
        if temp != getattr(bot, 'thought_of_the_day', None):
            bot.thought_of_the_day = temp
            break

    embed = Embed(
        description='This should work',
        title='Thought of the day',
        color=Color.blue()
    )

    await bot.get_channel(bot.general_id).send(embed=embed)


@ tasks.loop(hours=24)
async def get_gifs():
    '''updates cat gifs. Runs every 24 hours'''
    bot.gifs = Utils.get_random_gifs(os.environ['TENOR_API_KEY'])

# COMMANDS


@ bot.command()
async def snipe(ctx):
    '''finds the last deleted message in the given channel'''
    if ctx.channel.id in bot.last_deleted_message:
        if Utils.happens(0.5) or ctx.author.id in bot.authorized_users:
            msg: Message = bot.last_deleted_message[ctx.channel.id]
            embed = Embed(
                description=msg.message.content,
                type='rich',
                color=Color.blue()
            )
            embed.set_author(
                name=msg.author.display_name,
                icon_url=msg.author.avatar_url,
            )
            if msg.image is not None:
                embed.set_image(url=msg.image)
            await ctx.send(embed=embed)
        else:
            await ctx.reply('ask again later when I\'m less busy with ur mum')
    else:
        await ctx.send('Nothing to see here')


@ bot.command()
async def ping(ctx):
    '''responds with the bots latency'''
    embed = Embed(description=f'{int(bot.latency*1000)}ms', color=Color.blue())
    await ctx.send(embed=embed)


@ bot.command()
async def pussy(ctx):
    '''sends random cat gif'''
    gif_link = bot.gifs[random.randint(0, 19)]['media'][0]['gif']['url']
    embed = Embed(title="Here's a good pussy")
    embed.set_image(url=gif_link)
    await ctx.send(embed=embed)


@ bot.command()
async def thought(ctx):
    '''sends thought of the day'''
    if Utils.happens(1):
        embed = Embed(
            description=bot.thought_of_the_day,
            title='Thought of the day',
            color=Color.blue()
        )
        await ctx.reply(embed=embed)
    else:
        await ctx.reply('ask again later when I\'m less busy with ur mum')


@bot.command()
async def vc(ctx, arg=None):
    '''
    By default, shows the time spent by the current user in VC
    If however another user is tagged, shows their statistics
    If given argument is not valid, resorts to the default behavior mentioned above
    '''
    if arg is None:
        user = ctx.author
    else:
        try:
            user = bot.get_user(int(arg[3:-1]))
        except KeyError:
            # if the provided user doesn't exist
            user = ctx.author

    embed = Embed(
        title=f"{user.name}'s activity",
        color=Color.blue()
    )
    if user.bot:
        await ctx.reply(data['images']['bot_vc'])
        return
    elif Utils.is_in_vc(user, bot.current_vc_time):
        time_spent_str = Utils.convert_to_human_time(
            bot.time_spent[user.id] + (datetime.now() - bot.current_vc_time[user.id])
        )
    else:
        time_spent_str = Utils.convert_to_human_time(bot.time_spent[user.id])

    description = f'Time Spent in VC: {time_spent_str}'
    embed.description = description

    await ctx.reply(embed=embed)


@bot.command()
async def busy(ctx):
    '''
    Displays a list of the 5 people who have spent
    the most time in the VC
    '''
    embed = Embed(
        color=Color.blue(),
        title='Busiest people in TIT REGION'
    )
    out_str = ''
    emojis = [
        ':first_place:', ':second_place:',
        ':third_place:', ':small_orange_diamond:',
        ':small_orange_diamond:'
    ]

    # since the time_spent data might be outdated, combine the dict with
    # current_vc_time

    # I'm still not sure if we should do the sorting every time the command is called
    # or after a specific time period, like every hour or something
    # For now, sorting everytime the command is called

    total_vc_time = Utils.combine_time_dicts(bot.time_spent, bot.current_vc_time)

    for (k, v), emoji in zip(total_vc_time.items(), emojis):
        user = bot.get_user(k)
        if user is not None and not user.bot:
            out_str += f'{emoji} {user.name} - {Utils.convert_to_human_time(v)}\n'
    embed.description = out_str
    await ctx.channel.send(embed=embed)


@bot.command()
async def warn(ctx, arg=None):
    '''Warns the provided user. Can only be accessed by authorized users'''
    if ctx.author.id in bot.authorized_users:
        if arg is None:
            embed = Embed(
                title='Missing arguments',
                description='You must specify a member to warn',
                color=Color.blue()
            )
            await ctx.channel.send(embed=embed)
        else:
            try:
                user = bot.get_user(int(arg[3:-1]))

                if user.bot:
                    await ctx.reply(data['images']['bot_vc'])
                else:
                    embed = Embed(
                        title=f'{user.name} warned',
                    )

                    bot.current_vc_time.pop(user.id, None)
                    if bot.time_spent[user.id].seconds >= 60*60*3:
                        bot.time_spent[user.id] -= timedelta(hours=3)
                        embed.description = 'Warned for farming VC time. Deducted 3 hours'
                    else:
                        embed.description = 'Warned for farming VC time.'

                    await ctx.channel.send(embed=embed)
            except KeyError:
                embed = Embed(
                    title='Invalid arguments',
                    description='This member does not exist',
                    color=Color.blue()
                )
                await ctx.channel.send(embed=embed)
    else:
        embed = Embed(title='Unauthorized author')
        embed.set_image(url=data['images']['unworthy'])
        await ctx.reply(embed=embed)


@bot.command()
async def edit(ctx):
    '''Displays the last edited message'''
    if ctx.channel.id in bot.last_message_edited:
        msg: Message = bot.last_message_edited[ctx.channel.id]
        embed = Embed(
            description=msg.message.content,
            type='rich',
            color=Color.blue()
        )
        embed.set_author(
            name=msg.author.display_name,
            icon_url=msg.message.author.avatar_url,
        )
        if msg.image is not None:
            embed.set_image(url=msg.image)
        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send('Nothing to see here')


async def send_notice(embed):
    '''Sends a notice to the general channel'''
    await bot.get_channel(bot.general_id).send(content='@everyone', embed=embed)

bot.run(os.environ['DISCORD_API_TOKEN'])
