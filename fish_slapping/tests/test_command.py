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


import xmpp, fudge
from fish_slapping import Bot

def fake_bot(replies):
    bot = Bot('user@server', 'pass', log_path='/tmp/delme.log')
    bot.client = fudge.Fake('client').is_a_stub()
    def send(msg):
        replies.append(msg)
    bot.client.send = send
    return bot
    
def test_new_command_can_be_created():
    replies = []
    bot = fake_bot(replies)

    bot.commands['hello'] = lambda bot, msg: 'Hello back'
    
    message = xmpp.Message('user@server', 'hello', frm='peer@server')
    bot.message_callback(None, message)
    assert len(replies) == 1
    assert replies[-1].getBody() == 'Hello back'

def test_command_is_chosen_based_on_its_name():
    replies = []
    bot = fake_bot(replies)

    bot.commands['hello'] = lambda bot, msg: 'Hello back'
    bot.commands['hi'] = lambda bot, msg: 'Hi back'
    
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

    bot.commands['echo'] = lambda bot, msg: 'you said "%s"' % ','.join(msg)
    
    message = xmpp.Message('user@server', 'echo hello world!', frm='peer@server')
    bot.message_callback(None, message)

    assert len(replies) == 1
    assert replies[-1].getBody() == 'you said "hello,world!"'

#def test_stop():
    
