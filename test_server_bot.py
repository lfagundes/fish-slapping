# -*- coding: utf-8 -*-

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



if __name__ == "__main__":
    import unittest
    unittest.main()
