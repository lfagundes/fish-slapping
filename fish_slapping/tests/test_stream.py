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
from fish_slapping import StreamSessionManager

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

