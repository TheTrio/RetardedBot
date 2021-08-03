import os
import re
from src import Utils
import random
from discord.abc import User
from src import user_ids


class Message:
    '''
    A wrapper to store a Message sent by a user.

    Attributes
    ----------
    message: discord.Message
        Stores the actual Message object sent by discord.py
    text: str
        Stores the plain text version of the message in lower case
    words: list[str]:
        Stores the list of words in the the plain text version of the message
    author: Discord.abc.User
        The author of the message
    image: str
        Stores the link of the first image(link, attachment or tenor)
    '''

    def __init__(self, message):
        self.message = message
        self.text = message.content.lower()
        # gets all the words separated either by a space, "?", "," or "."
        self.words = list(
            filter(lambda x: x, re.split(r'[\s\.\?,]+', self.text))
        )
        self.author: User = message.author
        self._words_len = len(self.words)
        self._cache = {}
        self.image = Utils.get_image_url(
            self.message,
            os.environ['TENOR_API_KEY']
        )

    def has_word(self, word):
        '''returns True if the message has the given word(case insensitive)'''
        return word.lower() in self.words

    def is_word(self, word):
        ''' returns True if the message just consists of the given word(case insensitive)'''
        return word.lower() == self.text

    def has_words(self, *words, all=False):
        '''
        if all is True, the method will return True only if all the words are present
        if it is False, the method will return True even if only one of the words are present
        '''
        for word in words:
            if all and not self.has_word(word):
                return False
            if not all and self.has_word(word):
                return True
        return all

    def is_words(self, *words):
        '''Returns true if the message has just any of the given words(case insensitive)'''
        for word in words:
            if self.is_word(word):
                return True
        return False

    def matches_regex(self, regex, contains=False):
        '''
        Returns the matched result of a regex search. Provided regex is a string
        If contains is False(as it is by default), the regex is matched from the start of the string
        If contains is True, the regex searches the entire string
        '''
        return self.matches_regexes(regexes=[regex], contains=contains)

    def matches_regexes(self, regexes, contains=False):
        '''
        Returns the matched result of a regex search. Provided regex is a iterable of strings
        If contains is False(as it is by default), the regex is matched from the start of the string
        If contains is True, the regex searches the entire string
        '''
        # checks if the regex is cached. If not, caches it for the next use
        for regex in regexes:
            if regex in self._cache:
                if contains:
                    if search := self._cache[regex].search(self.text):
                        return search
                else:
                    if match := self._cache[regex].match(self.text):
                        return match
            target = re.compile(regex)
            self._cache[regex] = target
            if contains:
                if search := target.search(self.text):
                    return search
            else:
                if match := target.match(self.text):
                    return match
        return False

    def is_author(self, name):
        '''Returns True if the given name is the author of the message'''
        return user_ids[name] == self.author.id

    def is_tagged(self, name=None, id=None):
        '''Returns True if the user given(in the form of a name or an id) is tagged in the message'''
        if name:
            return user_ids[name] in self.message.raw_mentions
        if id:
            return id in self.message.raw_mentions
        raise ValueError('You must provide either an name or id')

    def __len__(self):
        return self._words_len

    @staticmethod
    async def process_message(message, bot, data):
        '''Process the message and sends an appropriate response'''
        msg = Message(message)
        if Utils.happens():
            await message.reply(random.choice(
                data['available_choices']['random']+data['images']['random']),
                mention_author=False
            )

        elif msg.is_tagged(id=bot.user.id):
            if Utils.happens(0.3):
                await message.reply('ask again later when I\'m less busy with ur mum')

        elif msg.has_word('pushkal'):
            await message.reply(random.choice(data['available_choices']['pushkal']), mention_author=False)

        elif msg.has_words('bit', 'legion', all=True):
            await message.reply('TIT REGION REGISTRATIONS ARE OPEN!!', mention_author=False)

        elif msg.has_words('eclectic', 'electic', 'ecletic', 'eletic'):
            await message.reply(data['copy_pasta']['eclectic'], mention_author=False)

        elif msg.matches_regex('[hH]+[mM]+'):
            if Utils.happens(0.5):
                await message.reply(data['copy_pasta']['hmm'], mention_author=False)

        elif msg.has_word('query'):
            await message.reply(random.choice(data['available_choices']['query']), mention_author=False)

        elif msg.is_words('ok', 'omk', 'okay'):
            await message.reply(random.choice(data['available_choices']['ok']), mention_author=False)

        elif msg.has_words('execute', 'compile', 'run'):
            await message.reply(random.choice(data['available_choices']['execute']), mention_author=False)

        elif msg.has_word('gay'):
            await message.reply('Not as gay as ur mom', mention_author=False)

        elif len(msg) >= 30:
            await message.reply(data['images']['behra'][0])

        elif msg.has_words('ppt', 'check', all=True):
            await message.reply("It's not in the ppt", mention_author=False)

        elif msg.has_words('ppt'):
            await message.reply("Let's check the ppt", mention_author=False)

        elif msg.is_words('no', 'non'):
            if Utils.happens(0.3):
                await message.reply(data['images']['no u'], mention_author=False)

        elif msg.matches_regex('know'):
            if Utils.happens():
                mess_str = f"Speaking of knowing things..... <@{user_ids['tanay']}> knows everything"
                await message.reply(mess_str)

        elif msg.has_words('codechef', 'chef', 'codeforces', 'leetcode', 'hackerrank'):
            await message.reply(
                random.choice(data['available_choices']['pogrammer']),
                mention_author=False
            )

        elif msg.matches_regexes(
            data['matches']['profanity'],
            contains=True
        ):
            await message.reply(
                random.choice(data['available_choices']['profanity']),
                mention_author=False
            )

        elif msg.has_word('69'):
            await message.reply(data['images']['noice'], mention_author=False)

        elif msg.is_word(data['images']['ishpreet']):
            await message.reply('ISHI layak hai tu', mention_author=False)

        elif msg.has_word('alcohol'):
            await message.reply(
                data['available_choices']['modi'][0],
                mention_author=False
            )

        elif msg.has_words('drugs', 'drug'):
            await message.reply(
                data['available_choices']['modi'][1],
                mention_author=False
            )

        elif msg.matches_regex('g[uo]o?d bot'):
            await message.reply('themk u :deer:')

        elif msg.has_words('pointless', 'circle', 'circles'):
            await message.reply(
                random.choice(data['available_choices']['pointless'])
            )

        elif msg.matches_regex(r'where \w+'):
            await message.reply('inside ur mom')

        elif msg.is_word(data['images']['kataria_kat']):
            await message.reply(random.choice(data['available_choices']['kat']))

        elif Utils.is_cat_gif(msg.text):
            if Utils.happens():
                await message.reply(bot.gifs[random.randint(0, 19)]['media'][0]['gif']['url'])

        elif msg.is_tagged('tanay'):
            if Utils.happens():
                await message.reply(f"No one teg <@{user_ids['tanay']}>")

        elif msg.is_author('potter'):
            if Utils.happens():
                await message.reply(data['copy_pasta']['potter'])

        elif msg.is_author('sarvesh'):
            if Utils.happens():
                await message.reply('Sarvesh?? Sarvesh is there??')

        elif msg.is_author('kataria'):
            if Utils.happens():
                await message.reply('Sarvesh.... Sarvesh are you OK?')

        elif msg.is_author('ishiboi'):
            if Utils.happens(0.3):
                await message.reply(data['images']['ishpreet'])
