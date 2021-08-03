from src import Message
import os
from unittest.mock import Mock


class Test_Message:

    def test_has_word(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.id = int(os.environ['sarvesh_id'])
        mock_user.name = 'Sarvesh'

        mock_message.content = 'Hello guys are you ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert msg.has_word('hello')
        assert msg.has_word('ok')

    def test_has_words(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.id = int(os.environ['sarvesh_id'])
        mock_user.name = 'Sarvesh'

        mock_message.content = 'Hello guys are you ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert msg.has_words('guys', 'not')
        assert not msg.has_words('guys', 'not', all=True)

    def test_is_word(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.id = int(os.environ['sarvesh_id'])
        mock_user.name = 'Sarvesh'

        mock_message.content = 'Hello guys are you ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert not msg.is_word('guys')
        assert not msg.is_words('guys', 'not')
        mock_message.content = 'ok'
        msg = Message(mock_message)
        assert msg.is_word('Ok')
        assert msg.is_words('ok', 'hello')

    def test_matches_regex(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.return_value.id = int(os.environ['sarvesh_id'])
        mock_user.return_value.name = 'Sarvesh'

        mock_message.content = 'hmmmmmmmmmmm'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert msg.matches_regex('[hH]+[mM]+')
        mock_message.content = 'ok Hmmmmmmm ok'
        msg = Message(mock_message)
        assert msg.matches_regex('[hH]+[mM]+', contains=True)
        assert not msg.matches_regex('[hH]+[mM]+', contains=False)

    def test_matches_regexes(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.return_value.id = int(os.environ['sarvesh_id'])
        mock_user.return_value.name = 'Sarvesh'

        mock_message.content = 'ok Hmmmmmmm ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert not msg.matches_regexes(['[hH]+[mM]', 'g(o)?(o|u)d bot'])
        assert not msg.matches_regexes(['sad', 'bot'])
        assert msg.matches_regexes(['[hH]+[mM]', 'bot'], contains=True)

    def test_is_author(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.id = int(os.environ['sarvesh_id'])
        mock_user.name = 'sarvesh'

        mock_message.content = 'Hello guys are you ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = []
        mock_message.attachments = []
        msg = Message(mock_message)
        assert msg.is_author('sarvesh')

    def test_is_tagged(self):
        mock_message = Mock()
        mock_user = Mock()
        mock_user.id = int(os.environ['sarvesh_id'])
        mock_user.name = 'sarvesh'

        mock_message.content = 'Hello guys are you ok'
        mock_message.author = mock_user
        mock_message.raw_mentions = [int(os.environ['tanay_id'])]
        mock_message.attachments = []
        msg = Message(mock_message)
        assert msg.is_tagged('tanay')
        mock_message.raw_mentions = [int(os.environ['sarvesh_id'])]
        msg = Message(mock_message)
        assert not msg.is_tagged('tanay')
        mock_message.raw_mentions.append(int(os.environ['tanay_id']))
        msg = Message(mock_message)
        assert msg.is_tagged('tanay')
