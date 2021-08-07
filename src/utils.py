import random
from discord.colour import Color
from discord.embeds import Embed
from discord.errors import InvalidArgument
import requests
import re
from collections import namedtuple
from src import data
import os
from collections import defaultdict
from datetime import datetime, timedelta
import json
from src import file_path

img_pattern = re.compile(r'(https?:\/\/.*\.(?:png|jpg|gif))')
tenor_pattern = re.compile(r'(https://tenor.com/[^\s\d]+-(\d+))')
cat_tenor_pattern = re.compile(r'.*?(tenor.com|giphy.com)/.*?(cat|pussy|kitten|kat|kitty)')


class Utils:
    @staticmethod
    def happens(probability=0.05):
        '''returns True or False based on the given probability'''
        if probability > 1 or probability < 0:
            raise ValueError('Probability must be between 0 and 1(both inclusive)')
        return random.random() < probability

    @staticmethod
    def get_image_url(message, key):
        '''Finds the direct link of the image from the provided message'''
        if len(message.attachments) != 0:
            return message.attachments[0].url
        text = message.content
        if result := img_pattern.search(text):
            return result.group(1)
        elif result := tenor_pattern.search(text):
            tenor_id = result.group(2)
            resp = requests.get(
                'https://g.tenor.com/v1/gifs',
                params={
                    'key': key,
                    'ids': tenor_id,
                    'limit': 1
                }
            )
            if resp.status_code == 200:
                return resp.json()['results'][0]['media'][0]['gif']['url']
            else:
                print('The response was not valid', resp)
        return None

    @staticmethod
    def get_random_gifs(key):
        '''Gets a random cat gif from TENOR'''
        resp = requests.get(
            'https://g.tenor.com/v1/random',
            params={
                'key': key,
                'limit': 20,
                'media_filter': 'minimal',
                'q': 'cute kitten',
                'contentfilter': 'high'
            }
        )

        if resp.status_code == 200:
            return resp.json()['results']
        else:
            # when the request isn't successful
            print('The response was not valid', resp)

    @staticmethod
    def get_random_image():
        '''Gets a random image link from the JSON file'''
        if 'images' in data:
            return random.choice(data['images']['random'])
        return None

    @staticmethod
    def notice_to_embed(text, attachments=False, random_image=True):
        Notice = namedtuple('Notice', 'organization platform description')

        items = [x.strip() for x in text.split(',')]
        if len(items) != 3 or ''.join(items) == '':
            raise InvalidArgument

        notice = Notice._make(items)
        notice_embed = Embed(
            title=f'{notice.organization} just posted something on {notice.platform}',
            description=notice.description,
            color=Color.blue()
        )
        if attachments:
            notice_embed.set_image(url=attachments[0].url)
        elif Utils.happens(0.5) and random_image:
            notice_embed.set_image(url=Utils.get_random_unsplash_image(query='Nature'))
        else:
            notice_embed.set_image(url=Utils.get_random_image())

        return notice_embed

    @staticmethod
    def get_random_unsplash_image(query: str):
        '''Gets a random image about the provided query from UNSPLASH'''
        key = os.environ['UNSPLASH_API_KEY']
        resp = requests.get(f'https://api.unsplash.com/photos/random/?client_id={key}&query={query}')
        if resp.status_code == 200:
            return resp.json()['urls']['raw']

    @staticmethod
    def vc_joined(before, after):
        '''Returns true if someone joined the VC'''
        return before.channel is None and after.channel is not None

    @staticmethod
    def vc_left(before, after):
        '''Returns true if someone left the VC'''
        return before.channel is not None and after.channel is None

    @staticmethod
    def convert_to_human_time(time: timedelta):
        '''Converts a time delta object to human readable time'''
        days = time.days
        seconds = time.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) % 60
        if days != 0:
            if hours != 0:
                return f'{days} days, {hours} hours and {minutes} minutes'
            else:
                return f'{days} days and {minutes} minutes'
        else:
            if hours != 0:
                return f'{hours} hours and {minutes} minutes'
            else:
                return f'{minutes} minutes'

    @staticmethod
    def to_time_delta(time: str):
        '''Converts a string to a time delta object'''
        days, seconds = list(map(int, time.split(':')))
        return timedelta(days=days, seconds=seconds)

    @staticmethod
    def get_time_data():
        '''Returns a default dict created after reading the json file data/time.json'''
        time_spent = defaultdict(lambda: timedelta(days=0, seconds=0))
        if os.path.exists(file_path / 'data/time.json'):
            with open(file_path / 'data/time.json', 'r') as f:
                time_spent.update({int(k): Utils.to_time_delta(v) for (k, v) in json.load(f).items()})
        return time_spent

    @staticmethod
    def update_time_data(time_spent):
        '''Writes the dictionary time_spent to the file data/time.json'''
        def to_human_time(duration: timedelta):
            '''Returns timedelta in format days:seconds'''
            return f'{duration.days}:{duration.seconds}'

        with open(file_path / 'data/time.json', 'w') as f:
            human_time_s = {k: to_human_time(v) for k, v in time_spent.items()}
            f.write(json.dumps(human_time_s))

    @staticmethod
    def is_in_vc(user, current_vc_time: dict):
        return user.id in current_vc_time

    @staticmethod
    def sort_default_dict(d: dict):
        '''Returns a sorted default dict created from the provided dictionary'''
        return defaultdict(
            lambda: timedelta(days=0, seconds=0),
            {
                k: v for k, v in sorted(
                    d.items(),
                    key=lambda item: item[1],
                    reverse=True
                )
            }
        )

    @staticmethod
    def combine_time_dicts(time_spent: dict, current_vc_time: dict):
        '''Combines the two given dicts, sorts the result, and then returns it

        time_spent gets updated whenever a user exits the VC
        current_vc_time stores the time the user entered the vc

        This function returns the sum of both the time delta in time_spent and
        the time delta current_vc_time[key] - Time right now
        '''
        combined_dict = defaultdict(lambda: timedelta(days=0, seconds=0))
        for key, value in time_spent.items():
            if key in current_vc_time:
                combined_dict[key] = value + (datetime.now() - current_vc_time[key])
            else:
                combined_dict[key] = value
        return Utils.sort_default_dict(combined_dict)

    @staticmethod
    def is_cat_gif(gif_link: str):
        return cat_tenor_pattern.match(gif_link)
