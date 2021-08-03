from discord.embeds import Embed
from discord.errors import InvalidArgument
from src import Utils
from unittest.mock import MagicMock, Mock, patch
import pytest
from datetime import timedelta

img_link = "https://tenor.com/view/jaspreet-singh-beta-tu-toh-chup-hi-raha-kr-beta-tu-toh-chup-hi-rha-kr-jaspreet-sigh-stand-up-comedy-gif-16842763"  # noqa: E501


def test_json():
    return {'results': [{'media': [{'gif': {'url': 'abcd.xyz'}}]}]}


class Test_Utils:

    @patch('src.utils.requests.get')
    def test_get_image_url(self, mock_get):
        '''
        Tests the get_image_url function

        Tests 3 cases -

        1) When no image is found,
        2) when tenor image is found,
        3) when jpg/png/gif is found
        '''

        # Testing result when no image is found
        mock_get.return_value = MagicMock(status_code=200, json=test_json)
        mock_message = MagicMock(content='Test')

        assert Utils.get_image_url(mock_message, 'key') is None

        # Testing when tenor image is found
        mock_message.content = img_link
        params = {
            'key': 'key',
            'ids': '16842763',
            'limit': 1
        }

        assert Utils.get_image_url(mock_message, 'key') == 'abcd.xyz'
        mock_get.assert_called_with('https://g.tenor.com/v1/gifs', params=params)

        # Testing when jpg/png/gif is found
        mock_message.content = 'helo https://i.com/vnR3ERq.png testing'
        assert Utils.get_image_url(mock_message, 'key') == 'https://i.com/vnR3ERq.png'

    @patch('src.utils.requests.get')
    def test_get_random_gif(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {'results': 'test'})
        assert Utils.get_random_gifs('key') == 'test'

        params = {
            'key': 'key',
            'limit': 20,
            'media_filter': 'minimal',
            'q': 'cute kitten',
            'contentfilter': 'high'
        }
        mock_get.assert_called_with('https://g.tenor.com/v1/random', params=params)

    @pytest.mark.parametrize("text, title, description", [
        ('ok,ok,ok', 'ok just posted something on ok', 'ok'),
        ('   ok   ,   ok   ,   ok   ', 'ok just posted something on ok', 'ok'),
        ('titlectic, Facebook, hello', 'titlectic just posted something on Facebook', 'hello')
    ])
    def test_notice_to_embed_success(self, text, title, description):
        embed = Utils.notice_to_embed(text, random_image=False)
        assert type(embed) is Embed

        assert embed.title == title
        assert embed.description == description

    @pytest.mark.parametrize("text", [
        ('ok'),
        ('TITLECTIC,facebook,how are you guys,'),
        (',,'),
        (',')
    ])
    def test_notice_to_embed_failure(self, text):
        with pytest.raises(InvalidArgument):
            Utils.notice_to_embed(text, random_image=False)

    def test_vc_joined(self):
        before = Mock()
        after = Mock()

        # Testing all failing cases
        assert not Utils.vc_joined(before, after)
        before.channel = True
        assert not Utils.vc_joined(before, after)
        after.channel = True
        assert not Utils.vc_joined(before, after)

        # Testing success
        before.channel = None
        assert Utils.vc_joined(before, after)

    def test_vc_left(self):
        before = Mock()
        after = Mock()

        # Testing all failing cases
        assert not Utils.vc_left(before, after)
        before.channel = None
        assert not Utils.vc_left(before, after)
        after.channel = True
        assert not Utils.vc_left(before, after)

        # Testing success

        before.channel = True
        after.channel = None
        assert Utils.vc_left(before, after)

    @pytest.mark.parametrize("time, expected", [
        (timedelta(days=1, seconds=23, minutes=10), '1 days and 10 minutes'),
        (timedelta(days=1, seconds=23, minutes=10, hours=1), '1 days, 1 hours and 10 minutes'),
        (timedelta(days=0, seconds=23, minutes=10), '10 minutes'),
        (timedelta(days=0, seconds=23, minutes=10, hours=5), '5 hours and 10 minutes'),
        (timedelta(seconds=70), '1 minutes'),
        (timedelta(hours=25), '1 days, 1 hours and 0 minutes'),
        (timedelta(minutes=120), '2 hours and 0 minutes')
    ])
    def test_convert_to_human_time(self, time, expected):
        output = Utils.convert_to_human_time(time)
        assert output == expected

    @patch('src.utils.requests.get')
    def test_get_random_unsplash_image(self, mock_get):
        def dummy(): return {'urls': {'raw': True}}
        mock_get.return_value = MagicMock(status_code=200, json=dummy)
        assert Utils.get_random_unsplash_image(query='Nature')

    def test_is_in_vc(self):
        mock_user = Mock()
        mock_user.id = 1
        assert Utils.is_in_vc(mock_user, {1: 'ok'})
        assert not Utils.is_in_vc(mock_user, {2: 'ok'})
