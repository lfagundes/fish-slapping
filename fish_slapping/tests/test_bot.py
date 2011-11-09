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

import os, time, fudge, datetime
from fish_slapping.tests import BaseTest

from fish_slapping import Log, Bot

class BotTest(BaseTest):

    def setUp(self):
        super(BotTest, self).setUp()

        fake_logger = fudge.Fake('logger', callable=True).returns_fake().is_a_stub()
        self.logger_patch = fudge.patch_object(Bot, '_get_logger', fake_logger)

        fake_connect = fudge.Fake('connect', callable=True).returns(True)
        self.connect_patch = fudge.patch_object(Bot, 'connect', fake_connect)

    def tearDown(self):
        super(BotTest, self).tearDown()
        self.logger_patch.restore()
        self.connect_patch.restore()

    def test_status_is_set_according_to_status_class(self):
        bot = Bot('user@server', 'pass')
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status
        bot.status = lambda: ('', 'Other status')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Other status')
        self.assertEquals(bot.status_show, '')
        bot.status = lambda: ('away', 'Other status')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Other status')
        self.assertEquals(bot.status_show, 'away')


    def test_status_show_time_when_status_was_last_changed(self):
        bot = Bot('user@server', 'pass')
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status, with new time
        self.set_date('2011-09-21 01:00:04')
        bot.status = lambda: ('away', 'Other status')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 Other status')
        self.assertEquals(bot.status_show, 'away')

        # New time won't change status time if message is not changed
        self.set_date('2011-09-21 01:00:05')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 Other status')
        self.assertEquals(bot.status_show, 'away')

        # Status will be changed now
        self.set_date('2011-09-21 01:00:06')
        bot.status = lambda: ('away', 'New status')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:06 New status')
        self.assertEquals(bot.status_show, 'away')

    def test_date_of_message_will_be_preserved_if_only_status_show_changes(self):
        bot = Bot('user@server', 'pass')
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status, with new time
        self.set_date('2011-09-21 01:00:04')
        bot.status = lambda: ('away', 'Ok')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, 'away')


    def test_error_will_override_status(self):
        bot = Bot('user@server', 'pass')
        bot.logs['first'] = Log('/tmp/jabber_test/first.log')
        bot.logs['secnd'] = Log('/tmp/jabber_test/secnd.log')
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')
        filename2 = '/tmp/jabber_test/secnd.log'
        log2 = Log('secnd')

        self.set_date('2011-09-21 01:00:03')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - INFO - Line 01\n')
        open(filename2, 'w').write('2011-09-21 01:00:02,854 - secnd - INFO - Line 02\n')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # One info should not interfere with status
        self.set_date('2011-09-21 01:00:04')
        open(filename1, 'a').write('2011-09-21 01:00:03,854 - first - INFO - Line 03\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Error should change status
        self.set_date('2011-09-21 01:00:05')
        open(filename1, 'a').write('2011-09-21 01:00:04,854 - first - ERROR - Error 01\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

        # Status update won't change bot status, because error is more important
        self.set_date('2011-09-21 01:00:06')
        bot.status = lambda: ('', 'New status')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

        # New error will override previous one
        self.set_date('2011-09-21 01:00:07')
        open(filename2, 'a').write('2011-09-21 01:00:06,854 - secnd - ERROR - Error 02\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:06 secnd: Error 02')
        self.assertEquals(bot.status_show, 'dnd')

        # New error of same log will override previous one
        self.set_date('2011-09-21 01:00:08')
        open(filename2, 'a').write('2011-09-21 01:00:07,854 - secnd - ERROR - Error 03\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:07 secnd: Error 03')
        self.assertEquals(bot.status_show, 'dnd')


    def test_recent_errors_will_be_shown_on_initialization(self):
        self.set_date('2011-09-21 01:00:03')

        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')
        filename2 = '/tmp/jabber_test/secnd.log'
        log2 = Log('secnd')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - ERROR - Error 01\n')
        open(filename2, 'w').write('2011-09-21 01:00:02,854 - secnd - INFO - Line 02\n')

        bot = Bot('user@server', 'pass')
        bot.logs['first'] = Log('/tmp/jabber_test/first.log', error_timeout=60)
        bot.logs['secnd'] = Log('/tmp/jabber_test/secnd.log', error_timeout=60)
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()

        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:01 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

    def test_old_errors_will_not_be_shown_on_initialization(self):
        self.set_date('2011-09-21 01:00:03')

        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')
        filename2 = '/tmp/jabber_test/secnd.log'
        log2 = Log('secnd')

        open(filename1, 'w').write('2011-09-21 00:30:01,854 - first - ERROR - Error 01\n')
        open(filename2, 'w').write('2011-09-21 00:30:02,854 - secnd - INFO - Line 02\n')

        bot = Bot('user@server', 'pass')
        bot.logs['first'] = Log('/tmp/jabber_test/first.log', error_timeout=60)
        bot.logs['secnd'] = Log('/tmp/jabber_test/secnd.log', error_timeout=60)
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

    def test_error_expires(self):
        bot = Bot('user@server', 'pass')
        bot.logs['first'] = Log('/tmp/jabber_test/first.log', error_timeout=60)
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')

        self.set_date('2011-09-21 01:00:03')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - INFO - Line 01\n')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Error should change status
        self.set_date('2011-09-21 01:00:05')
        open(filename1, 'a').write('2011-09-21 01:00:04,854 - first - ERROR - Error 01\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

        # Error expires
        self.set_date('2011-09-21 01:01:08')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')


    def test_status_can_be_cleared(self):
        bot = Bot('user@server', 'pass')
        bot.logs['first'] = Log('/tmp/jabber_test/first.log')
        bot.logs['secnd'] = Log('/tmp/jabber_test/secnd.log')
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        
        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')

        self.set_date('2011-09-21 01:00:03')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - INFO - Line 01\n')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Error will change status
        self.set_date('2011-09-21 01:00:05')
        open(filename1, 'a').write('2011-09-21 01:00:04,854 - first - ERROR - Error 01\n')
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:04 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

        bot.clear()
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

    def test_presence_is_only_sent_when_necessary(self):
        self.count = 0
        def message(*args):
            self.count += 1

        bot = Bot('user@server', 'pass', presence_heartbeat=50)
        bot.logs['first'] = Log('/tmp/jabber_test/first.log', error_timeout=30)
        bot.status = lambda: ('', 'Ok')
        bot.client = fudge.Fake('client').is_a_stub()
        bot.client.provides('send').calls(message)
        
        filename1 = '/tmp/jabber_test/first.log'

        self.set_date('2011-09-21 01:00:03')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - INFO - Line 01\n')

        # Status is 'Ok', only first presence will be sent
        bot.cycle()
        self.assertEquals(self.count, 1)
        bot.cycle()
        self.assertEquals(self.count, 1)

        # Status changes, one presence will be sent
        self.set_date('2011-09-21 01:00:03')
        bot.status = lambda: ('', 'New status')
        bot.cycle()
        self.assertEquals(self.count, 2)
        bot.cycle()
        self.assertEquals(self.count, 2)

        # Error will cause new presence broadcast
        self.set_date('2011-09-21 01:00:05')
        open(filename1, 'a').write('2011-09-21 01:00:04,854 - first - ERROR - Error 01\n')
        bot.cycle()
        self.assertEquals(self.count, 3)

        # Several seconds passes, no presence broadcast
        self.set_date('2011-09-21 01:00:06')
        bot.cycle()
        self.assertEquals(self.count, 3)
        self.set_date('2011-09-21 01:00:07')
        bot.cycle()
        self.assertEquals(self.count, 3)
        self.set_date('2011-09-21 01:00:08')
        bot.cycle()
        self.assertEquals(self.count, 3)
        self.set_date('2011-09-21 01:00:09')
        bot.cycle()
        self.assertEquals(self.count, 3)
        self.set_date('2011-09-21 01:00:10')
        bot.cycle()
        self.assertEquals(self.count, 3)

        # Error expires, one broadcast
        self.set_date('2011-09-21 01:00:35')
        bot.cycle()
        self.assertEquals(self.count, 4)

        # 40 seconds passes, no broadcast
        self.set_date('2011-09-21 01:01:15')
        bot.cycle()
        self.assertEquals(self.count, 4)

        # 11 more seconds and presence heartbeat forces presence broadcast
        self.set_date('2011-09-21 01:01:26')
        bot.cycle()
        self.assertEquals(self.count, 5)




if __name__ == "__main__":
    import unittest
    unittest.main()
