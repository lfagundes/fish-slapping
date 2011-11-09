# -*- coding: utf-8 -*-

# Copyright (c) 2011, Luis Henrique Cassis Fagundes <lhfagundes@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import xmpp, fudge, os
from fish_slapping import Bot

def fake_bot(replies):
    tmp_log = '/tmp/fish-slapping-test-delme.log'
    if os.path.exists(tmp_log):
        os.remove(tmp_log)
    bot = Bot('user@server', 'pass', log_path=tmp_log)
    bot.client = fudge.Fake('client').is_a_stub()
    def send(msg):
        replies.append(msg)
    bot.client.send = send
    return bot
    
def test_new_command_can_be_created():
    replies = []
    bot = fake_bot(replies)

    bot.commands['hello'] = lambda sender, msg: 'Hello back'
    
    message = xmpp.Message('user@server', 'hello', frm='peer@server')
    bot.message_callback(None, message)
    assert len(replies) == 1
    assert replies[-1].getBody() == 'Hello back'

def test_command_is_chosen_based_on_its_name():
    replies = []
    bot = fake_bot(replies)

    bot.commands['hello'] = lambda sender, msg: 'Hello back'
    bot.commands['hi'] = lambda sender, msg: 'Hi back'
    
    message = xmpp.Message('user@server', 'hello', frm='peer@server')
    bot.message_callback(None, message)
    assert len(replies) == 1
    assert replies[-1].getBody() == 'Hello back'

    message = xmpp.Message('user@server', 'hi', frm='peer@server')
    bot.message_callback(None, message)
    assert len(replies) == 2
    assert replies[-1].getBody() == 'Hi back'

def test_original_message_is_passed_as_parameter():
    replies = []
    bot = fake_bot(replies)

    bot.commands['echo'] = lambda sender, msg: 'you said "%s"' % ','.join(msg)
    
    message = xmpp.Message('user@server', 'echo hello world!', frm='peer@server')
    bot.message_callback(None, message)

    assert len(replies) == 1
    assert replies[-1].getBody() == 'you said "hello,world!"'

def test_sender_is_sent_as_parameter():
    replies = []
    bot = fake_bot(replies)

    bot.commands['hello'] = lambda sender, msg: 'hello %s' % sender

    message = xmpp.Message('user@server', 'hello', frm='peer@server')
    bot.message_callback(None, message)

    assert len(replies) == 1
    assert replies[-1].getBody() == 'hello peer@server'                 

def test_show_logs_and_stop():
    replies = []
    bot = fake_bot(replies)

    bot.logger.info('Just a test message')

    message = xmpp.Message('user@server', 'show fish-slapping', frm='peer@server')
    bot.message_callback(None, message)
    bot.flush_logs()
    assert len(replies) == 1
    assert 'Just a test message' in replies[-1].getBody()

    bot.logger.info('Another test message')
    bot.flush_logs()
    assert len(replies) == 2
    assert 'Another test message' in replies[-1].getBody()

    bot.flush_logs()
    assert len(replies) == 2

    message = xmpp.Message('user@server', 'stop', frm='peer@server')
    bot.message_callback(None, message)
    assert len(replies) == 3
    assert replies[-1].getBody() == '--- end of logs'

    bot.logger.info('This is not supposed to be sent as msg')
    bot.flush_logs()
    assert len(replies) == 3

def test_help():

    def my_command(sender, message):
        """
        This is the help text of my command.
        It is available through the help command
        """

    replies = []
    bot = fake_bot(replies)

    bot.commands['test'] = my_command

    message = xmpp.Message('user@server', 'help', frm='peer@server')
    bot.message_callback(None, message)

    assert len(replies) == 1
    assert 'test\n    This is the help text of my command.\n    It is available' in replies[-1].getBody()
    
    
    
    

    
    
    
