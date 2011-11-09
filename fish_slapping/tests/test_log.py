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

import os
from fish_slapping.tests import BaseTest
from fish_slapping import Log

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

        self.set_date('2011-09-21 01:00:03')
        open(filename, 'w').write('2011-09-21 01:00:02,854 - basic - ERROR - Some error message\n')

        log = Log(filename, error_timeout=120)

        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:02')
        self.assertEquals(log.error.message, 'Some error message')
        
        self.set_date('2011-09-21 01:04:03')

        self.assertTrue(not log.error)

    def test_recent_error_messages_will_set_error_status_on_startup(self):
        filename = '/tmp/jabber_test/basic.log'

        self.set_date('2011-09-21 01:00:10')
        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                                  '2011-09-21 01:00:02,854 - basic - ERROR - Line 02\n' +
                                  '2011-09-21 01:00:03,854 - basic - INFO - Line 03\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Line 04\n' +
                                  '2011-09-21 01:00:05,854 - basic - INFO - Line 05\n'
                                  )

        log = Log(filename, error_timeout=120)

        self.assertTrue(log.error)
        self.assertEquals(log.error.time, '2011-09-21 01:00:04')
        self.assertEquals(log.error.message, 'Line 04')
        
    def test_old_error_messages_will_be_ignored_on_startup(self):
        filename = '/tmp/jabber_test/basic.log'


        self.set_date('2011-09-21 01:05:10')
        open(filename, 'w').write('2011-09-21 01:00:01,854 - basic - INFO - Line 01\n' +
                                  '2011-09-21 01:00:02,854 - basic - ERROR - Line 02\n' +
                                  '2011-09-21 01:00:03,854 - basic - INFO - Line 03\n' +
                                  '2011-09-21 01:00:04,854 - basic - ERROR - Line 04\n' +
                                  '2011-09-21 01:00:05,854 - basic - INFO - Line 05\n'
                                  )

        log = Log(filename, error_timeout=120)

        self.assertTrue(not log.error)

    def test_last_info_message_will_be_in_status(self):
        filename = '/tmp/jabber_test/basic.log'

        log = Log(filename, error_timeout=120)

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

