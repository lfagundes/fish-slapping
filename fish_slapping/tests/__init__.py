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
    

