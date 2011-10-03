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
from unittest import TestCase

import server_bot
from server_bot import Log, StreamSessionManager, Bot

class BaseTest(TestCase):

    def _rmdir(self):
        os.system('rm -rf /tmp/jabber_test/')

    def setUp(self):
        self.patch = None
        self._rmdir()
        os.mkdir('/tmp/jabber_test')
        fake_sleep = fudge.Fake('sleep', callable=True).returns(None)
        self.sleep_patch = fudge.patch_object(time, 'sleep', fake_sleep)

    def tearDown(self):
        if self.patch:
            self.patch.restore()
        self.sleep_patch.restore()
        self._rmdir()

    def set_date(self, datestr):
        tstamp = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        fake = fudge.Fake('now', callable=True).returns(tstamp)
        if self.patch:
            self.patch.restore()
        self.patch = fudge.patch_object(datetime.datetime, 'now', fake)
    
class LogTest(BaseTest):

    def test_rewind_will_work_with_non_existing_log(self):
        filename = '/tmp/jabber_test/empty.log'
        assert not os.path.exists(filename)

        log = Log(filename)

        self.assertEquals(log.flush(), '')
        self.assertEquals(log.flush(), '')

        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n')

        self.assertEquals(log.flush(),
                          '2011-09-21 01:00:01,854 - basic - INFO - Line 01')
        
        open(filename, 'a').write('2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                                  '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n')

        self.assertEquals(log.flush(),
                          '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                          '2011-09-21 03:00:01,854 - basic - INFO - Line 03')

    def test_log_will_be_reopened_if_rotated(self):
        filename = '/tmp/jabber_test/basic.log'

        log = Log(filename)

        content = ('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                   '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                   '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n')
        
        open(filename, 'w').write(content)
        
        self.assertEquals(log.flush(), content.strip())

        content = ('2011-09-21 04:00:01,854 - basic - INFO - Line 04\n' +
                   '2011-09-21 05:00:01,854 - basic - INFO - Line 05\n')

        # File is rewritten, not appended
        open(filename, 'w').write(content)
        
        self.assertEquals(log.flush(), content.strip())

    def test_log_can_be_rewinded_by_line_number(self):
        filename = '/tmp/jabber_test/basic.log'
        log = Log(filename)

        content = ('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                   '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                   '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n' +
                   '2011-09-21 04:00:01,854 - basic - INFO - Line 04\n' +
                   '2011-09-21 05:00:01,854 - basic - INFO - Line 05\n' +
                   '2011-09-21 06:00:01,854 - basic - INFO - Line 06\n' +
                   '2011-09-21 07:00:01,854 - basic - INFO - Line 07\n' +
                   '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                   '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                   '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n'
                   )
        open(filename, 'w').write(content)

        log.flush()
        self.assertEquals(log.flush(), '')

        log.rewind(1)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')
        
        log.rewind(2)
        self.assertEquals(log.flush(),
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')
        
        log.rewind(3)
        self.assertEquals(log.flush(),
                          '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        open(filename, 'a').write('2011-09-21 11:00:01,854 - basic - INFO - Line 11\n')

        log.rewind(4)
        self.assertEquals(log.flush(),
                          '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n' +
                          '2011-09-21 11:00:01,854 - basic - INFO - Line 11')

    def test_log_can_be_rewinded_by_time_shift(self):
        self.set_date('2011-09-21 10:00:05')

        filename = '/tmp/jabber_test/basic.log'
        log = Log(filename)

        content = ('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                   '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                   '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n' +
                   '2011-09-21 04:00:01,854 - basic - INFO - Line 04\n' +
                   '2011-09-21 05:00:01,854 - basic - INFO - Line 05\n' +
                   '2011-09-21 06:00:01,854 - basic - INFO - Line 06\n' +
                   '2011-09-21 07:00:01,854 - basic - INFO - Line 07\n' +
                   '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                   '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                   '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n'
                   )
        open(filename, 'w').write(content)

        log.flush()
        self.assertEquals(log.flush(), '')

        log.rewind(dtime=5)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3600)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3605)
        self.assertEquals(log.flush(),
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3600)
        log.rewind(dtime=1) #this will override previous rewind
        self.assertEquals(log.flush(), '')

        log.rewind(dtime=3600 * 24)
        self.assertEquals(log.flush(), content.strip())

    def test_rewind_by_time_tolerates_multi_line_logs(self):
        self.set_date('2011-09-21 10:00:05')

        filename = '/tmp/jabber_test/basic.log'
        log = Log(filename)

        content = ('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                   '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                   '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n' +
                   '2011-09-21 04:00:01,854 - basic - INFO - Line 04\n' +
                   '2011-09-21 05:00:01,854 - basic - INFO - Line 05\n' +
                   '2011-09-21 06:00:01,854 - basic - INFO - Line 06\n' +
                   '2011-09-21 07:00:01,854 - basic - INFO - Line 07\n' +
                   '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                   'this is a second line of same log line\n' +
                   'there is even a third line\n' +
                   '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                   '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n'
                   )
        open(filename, 'w').write(content)

        log.flush()
        self.assertEquals(log.flush(), '')

        log.rewind(dtime=5)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3600)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3605)
        self.assertEquals(log.flush(),
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=7205)
        self.assertEquals(log.flush(),
                          '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                          'this is a second line of same log line\n' +
                          'there is even a third line\n' +
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        log.rewind(dtime=3600)
        log.rewind(dtime=1) #this will override previous rewind
        self.assertEquals(log.flush(), '')

        log.rewind(dtime=3600 * 24)
        self.assertEquals(log.flush(), content.strip())


    def test_rewind_by_lines_tolerates_multi_line_logs(self):
        filename = '/tmp/jabber_test/basic.log'
        log = Log(filename)

        content = ('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                   '2011-09-21 02:00:01,854 - basic - INFO - Line 02\n' +
                   '2011-09-21 03:00:01,854 - basic - INFO - Line 03\n' +
                   '2011-09-21 04:00:01,854 - basic - INFO - Line 04\n' +
                   '2011-09-21 05:00:01,854 - basic - INFO - Line 05\n' +
                   '2011-09-21 06:00:01,854 - basic - INFO - Line 06\n' +
                   '2011-09-21 07:00:01,854 - basic - INFO - Line 07\n' +
                   '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                   'this is a second line of same log line\n' +
                   'there is even a third line\n' +
                   '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                   '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n'
                   )
        open(filename, 'w').write(content)

        log.flush()
        self.assertEquals(log.flush(), '')

        log.rewind(1)
        self.assertEquals(log.flush(),
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')
        
        log.rewind(2)
        self.assertEquals(log.flush(),
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')
        
        log.rewind(3)
        self.assertEquals(log.flush(),
                          '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                          'this is a second line of same log line\n' +
                          'there is even a third line\n' +
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10')

        open(filename, 'a').write('2011-09-21 11:00:01,854 - basic - INFO - Line 11\n')

        log.rewind(4)
        self.assertEquals(log.flush(),
                          '2011-09-21 08:00:01,854 - basic - INFO - Line 08\n' +
                          'this is a second line of same log line\n' +
                          'there is even a third line\n' +
                          '2011-09-21 09:00:01,854 - basic - INFO - Line 09\n' +
                          '2011-09-21 10:00:01,854 - basic - INFO - Line 10\n' +
                          '2011-09-21 11:00:01,854 - basic - INFO - Line 11')


    def test_empty_log_will_have_clean_status(self):
        filename = '/tmp/jabber_test/empty.log'
        assert not os.path.exists(filename)

        log = Log(filename)

        self.assertTrue(not log.error)

    def test_error_messages_will_set_error_status(self):
        filename = '/tmp/jabber_test/basic.log'

        log = Log(filename)

        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n')
        self.set_date('2011-09-21 01:00:02')

        log.flush()

        self.assertTrue(not log.error)
        
        open(filename, 'a').write('2011-09-21 01:00:02,854 - basic - ERROR - Some error message\n')
        self.set_date('2011-09-21 01:00:03')

        log.flush()
        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:02')
        self.assertEquals(log.error.message, 'Some error message')
        
        open(filename, 'a').write('2011-09-21 01:00:03,854 - basic - ERROR - Error message #2\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Error message #3\n'
                                  )
        self.set_date('2011-09-21 01:00:04')

        log.flush()
        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:04')
        self.assertEquals(log.error.message, 'Error message #3')

    def test_error_status_will_expire(self):
        filename = '/tmp/jabber_test/basic.log'

        server_bot.ERROR_TIMEOUT = 120

        self.set_date('2011-09-21 01:00:03')
        open(filename, 'w').write('2011-09-21 01:00:02,854 - basic - ERROR - Some error message\n')

        log = Log(filename)

        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:02')
        self.assertEquals(log.error.message, 'Some error message')
        
        self.set_date('2011-09-21 01:04:03')

        self.assertTrue(not log.error)

    def test_recent_error_messages_will_set_error_status_on_startup(self):
        filename = '/tmp/jabber_test/basic.log'

        server_bot.ERROR_TIMEOUT = 120

        self.set_date('2011-09-21 01:00:10')
        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                                  '2011-09-21 01:00:02,854 - basic - ERROR - Line 02\n' +
                                  '2011-09-21 01:00:03,854 - basic - INFO - Line 03\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Line 04\n' +
                                  '2011-09-21 01:00:05,854 - basic - INFO - Line 05\n'
                                  )

        log = Log(filename)

        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:04')
        self.assertEquals(log.error.message, 'Line 04')
        
    def test_old_error_messages_will_be_ignored_on_startup(self):
        filename = '/tmp/jabber_test/basic.log'

        server_bot.ERROR_TIMEOUT = 120

        self.set_date('2011-09-21 01:05:10')
        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                                  '2011-09-21 01:00:02,854 - basic - ERROR - Line 02\n' +
                                  '2011-09-21 01:00:03,854 - basic - INFO - Line 03\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Line 04\n' +
                                  '2011-09-21 01:00:05,854 - basic - INFO - Line 05\n'
                                  )

        log = Log(filename)

        self.assertTrue(not log.error)

    def test_last_info_message_will_be_in_status(self):
        filename = '/tmp/jabber_test/basic.log'

        server_bot.ERROR_TIMEOUT = 120

        log = Log(filename)

        self.assertTrue(not log.status)

        self.set_date('2011-09-21 01:05:10')
        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                                  '2011-09-21 01:00:02,854 - basic - ERROR - Line 02\n' +
                                  '2011-09-21 01:00:03,854 - basic - INFO - Line 03\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Line 04\n' +
                                  '2011-09-21 01:00:05,854 - basic - INFO - Line 05\n'
                                  )

        log.flush()
        self.assertTrue(log.status)
        self.assertEquals(log.status.time, '2011-09-21 01:00:05')
        self.assertEquals(log.status.message, 'Line 05')

        self.set_date('2011-09-21 01:05:10')
        open(filename, 'w').write('2011-09-21 01:05:16,854 - basic - INFO - Line 06\n' +
                                  '2011-09-21 01:05:17,854 - basic - INFO - Line 07\n'
                                  )

        log.flush()
        self.assertTrue(log.status)
        self.assertEquals(log.status.time, '2011-09-21 01:05:17')
        self.assertEquals(log.status.message, 'Line 07')

class StreamSessionManagerTest(BaseTest):

    def test_session_expires_after_timeout(self):
        self.set_date('2011-09-21 01:05:10')

        session = StreamSessionManager()

        session.add('test@domain.com', timeout = 10)

        self.set_date('2011-09-21 01:05:11')

        session.expire()
        self.assertEquals(session.receivers, ['test@domain.com'])
    
        self.set_date('2011-09-21 01:05:21')
        session.expire()
        self.assertEquals(session.receivers, [])

    def test_session_expires_on_given_condition(self):

        control = '/tmp/stream_test'
        open(control, 'w')
        
        session = StreamSessionManager()

        session.add('test@domain.com', condition=lambda: os.path.exists(control))

        session.expire()
        self.assertEquals(session.receivers, ['test@domain.com'])
        session.expire()
        self.assertEquals(session.receivers, ['test@domain.com'])

        os.remove(control)
        session.expire()
        self.assertEquals(session.receivers, [])

    def test_session_support_multiple_jids(self):
        self.set_date('2011-09-21 01:05:10')
        control = '/tmp/stream_test'
        open(control, 'w')

        session = StreamSessionManager()

        session.add('test1@domain.com', timeout = 10)
        session.add('test2@domain.com', timeout = 20, condition = lambda: os.path.exists(control))
        session.add('test3@domain.com', timeout = 30)
        session.add('test3@domain.com', condition = lambda: os.path.exists(control))

        self.set_date('2011-09-21 01:05:11')
        session.expire()
        self.assertEquals(len(session.receivers), 3)
        self.assertTrue('test1@domain.com' in session.receivers)
        self.assertTrue('test2@domain.com' in session.receivers)
        self.assertTrue('test3@domain.com' in session.receivers)

        # test1 expires
        self.set_date('2011-09-21 01:05:21') 
        session.expire()
        self.assertEquals(len(session.receivers), 2)
        self.assertTrue('test1@domain.com' not in session.receivers)
        self.assertTrue('test2@domain.com' in session.receivers)
        self.assertTrue('test3@domain.com' in session.receivers)

        # test2 expires, even if condition is still true
        self.set_date('2011-09-21 01:05:31')
        session.expire()
        self.assertEquals(len(session.receivers), 1)
        self.assertTrue('test1@domain.com' not in session.receivers)
        self.assertTrue('test2@domain.com' not in session.receivers)
        self.assertTrue('test3@domain.com' in session.receivers)

        # test3 expires, but it remains there because there are two sessions
        self.set_date('2011-09-21 01:05:41')
        session.expire()
        self.assertEquals(len(session.receivers), 1)
        self.assertTrue('test1@domain.com' not in session.receivers)
        self.assertTrue('test2@domain.com' not in session.receivers)
        self.assertTrue('test3@domain.com' in session.receivers)

        # condition is false, now all receivers are gone
        os.remove(control)
        session.expire()
        self.assertEquals(len(session.receivers), 0)
        self.assertTrue('test1@domain.com' not in session.receivers)
        self.assertTrue('test2@domain.com' not in session.receivers)
        self.assertTrue('test3@domain.com' not in session.receivers)

    def test_expired_sessions_can_be_obtained(self):
        self.set_date('2011-09-21 01:05:10')
        control = '/tmp/stream_test'
        open(control, 'w')

        session = StreamSessionManager()

        session.add('test1@domain.com', timeout = 10)
        session.add('test2@domain.com', timeout = 20, condition = lambda: os.path.exists(control))
        session.add('test3@domain.com', timeout = 30)
        session.add('test3@domain.com', condition = lambda: os.path.exists(control))

        self.set_date('2011-09-21 01:05:11')
        expired = session.expire()
        self.assertEquals(expired, [])

        # test1 expires
        self.set_date('2011-09-21 01:05:21') 
        expired = session.expire()
        self.assertEquals(expired, ['test1@domain.com'])

        # test2 expires, even if condition is still true
        self.set_date('2011-09-21 01:05:31')
        expired = session.expire()
        self.assertEquals(expired, ['test2@domain.com'])

        # test3 expires, but it remains there because there are two sessions
        self.set_date('2011-09-21 01:05:41')
        expired = session.expire()
        self.assertEquals(expired, [])

        # condition is false, now all receivers are gone
        os.remove(control)
        expired = session.expire()
        self.assertEquals(expired, ['test3@domain.com'])

    def test_one_jid_can_be_removed_from_sessions(self):
        self.set_date('2011-09-21 01:05:10')
        control = '/tmp/stream_test'
        open(control, 'w')

        session = StreamSessionManager()

        session.add('test1@domain.com', timeout = 10)
        session.add('test2@domain.com', timeout = 20, condition = lambda: os.path.exists(control))
        session.add('test3@domain.com', timeout = 30)
        session.add('test3@domain.com', condition = lambda: os.path.exists(control))

        self.set_date('2011-09-21 01:05:11')
        self.assertEquals(len(session.receivers), 3)
        self.assertTrue('test1@domain.com' in session.receivers)
        self.assertTrue('test2@domain.com' in session.receivers)
        self.assertTrue('test3@domain.com' in session.receivers)

        session.remove('test3@domain.com')
        self.assertEquals(len(session.receivers), 2)
        self.assertTrue('test1@domain.com' in session.receivers)
        self.assertTrue('test2@domain.com' in session.receivers)
        self.assertTrue('test3@domain.com' not in session.receivers)

class BotTest(BaseTest):

    class Status(object):
        def __init__(self):
            self.status = 'Ok'
            self.status_show = ''
        def get_status(self):
            return self.status
        def get_status_show(self):
            return self.status_show

    def setUp(self):
        self.original_logs = Bot.LOGS
        super(BotTest, self).setUp()

        fake_logger = fudge.Fake('logger', callable=True).returns_fake().is_a_stub()
        self.logger_patch = fudge.patch_object(Bot, '_get_logger', fake_logger)

        self.connect_patch = None

    def patch_connection(self):
        fake_connect = fudge.Fake('connect', callable=True).returns(True)
        self.connect_patch = fudge.patch_object(Bot, 'connect', fake_connect)
        
    def tearDown(self):
        Bot.LOGS = self.original_logs
        super(BotTest, self).tearDown()
        self.logger_patch.restore()
        if self.connect_patch:
            self.connect_patch.restore()

    def test_status_is_set_according_to_status_class(self):
        self.patch_connection()

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status
        status.status = 'Other status'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Other status')
        self.assertEquals(bot.status_show, '')
        status.status_show = 'away'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Other status')
        self.assertEquals(bot.status_show, 'away')


    def test_status_show_time_when_status_was_last_changed(self):
        self.patch_connection()

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status, with new time
        self.set_date('2011-09-21 01:00:04')
        status.status = 'Other status'
        status.status_show = 'away'
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
        status.status = 'New status'
        status.status_show = 'away'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:06 New status')
        self.assertEquals(bot.status_show, 'away')

    def test_date_of_message_will_be_preserved_if_only_status_show_changes(self):
        self.patch_connection()

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
        bot.client = fudge.Fake('client').is_a_stub()
        
        self.set_date('2011-09-21 01:00:03')

        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

        # Status change should reflect in bot's status, with new time
        self.set_date('2011-09-21 01:00:04')
        status.status_show = 'away'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, 'away')


    def test_error_will_override_status(self):
        self.patch_connection()

        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),
                    Log('/tmp/jabber_test/secnd.log', 'secnd'),
                    )

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
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
        status.status = 'New status'
        status.status_show = ''
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
        self.patch_connection()

        server_bot.ERROR_TIMEOUT = 60
        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),
                    Log('/tmp/jabber_test/secnd.log', 'secnd'),
                    )

        self.set_date('2011-09-21 01:00:03')

        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')
        filename2 = '/tmp/jabber_test/secnd.log'
        log2 = Log('secnd')

        open(filename1, 'w').write('2011-09-21 01:00:01,854 - first - ERROR - Error 01\n')
        open(filename2, 'w').write('2011-09-21 01:00:02,854 - secnd - INFO - Line 02\n')

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
        bot.client = fudge.Fake('client').is_a_stub()

        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:01 first: Error 01')
        self.assertEquals(bot.status_show, 'dnd')

    def test_old_errors_will_not_be_shown_on_initialization(self):
        self.patch_connection()

        server_bot.ERROR_TIMEOUT = 60
        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),
                    Log('/tmp/jabber_test/secnd.log', 'secnd'),
                    )

        self.set_date('2011-09-21 01:00:03')

        filename1 = '/tmp/jabber_test/first.log'
        log1 = Log('first')
        filename2 = '/tmp/jabber_test/secnd.log'
        log2 = Log('secnd')

        open(filename1, 'w').write('2011-09-21 00:30:01,854 - first - ERROR - Error 01\n')
        open(filename2, 'w').write('2011-09-21 00:30:02,854 - secnd - INFO - Line 02\n')

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
        bot.client = fudge.Fake('client').is_a_stub()
        
        # Status should be 'Ok'
        bot.cycle()
        self.assertEquals(bot.status_msg, '2011-09-21 01:00:03 Ok')
        self.assertEquals(bot.status_show, '')

    def test_error_expires(self):
        self.patch_connection()

        server_bot.ERROR_TIMEOUT = 60
        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),
                    )

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
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
        self.patch_connection()

        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),
                    Log('/tmp/jabber_test/secnd.log', 'secnd'),
                    )

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
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
        self.patch_connection()

        self.count = 0
        def message(*args):
            self.count += 1

        server_bot.ERROR_TIMEOUT = 30
        server_bot.PRESENCE_HEARTBEAT = 50
        Bot.LOGS = (Log('/tmp/jabber_test/first.log', 'first'),)

        status = self.Status()
        
        bot = Bot('user@server', 'pass')
        bot.status = status
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
        status.status = 'New status'
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
