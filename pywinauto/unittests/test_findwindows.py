# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"Tests for findwindows.py"

__revision__ = "$Revision: 234 $"

import unittest

import sys
sys.path.append(".")
from pywinauto.findwindows import *


#=========================================================================
def _unittests():
    "Do a quick test of finding some windows"
    windows = find_windows(
        class_name_re = "#32770",
        enabled_only = False,
        visible_only = False)

    for win in windows:
        print "==" * 20
        print handleprops.dumpwindow(win)

#class ApplicationTestCases(unittest.TestCase):
#    "Unit tests for the ListViewWrapper class"
#
#    def setUp(self):
#        """Start the application set some data and ensure the application
#        is in the state we want it."""
#        pass
#
#    def tearDown(self):
#        "Close the application after tests"
#        # close the application
#        #self.dlg.SendMessage(win32defines.WM_CLOSE)
#        pass
#
#    def testNotConnected(self):
#        "Make sure the friendly class is set correctly"
#        self.assertRaises (AppNotConnected, Application().__getattr__, 'Hiya')
#        self.assertRaises (AppNotConnected, Application().__getitem__, 'Hiya')
#        self.assertRaises (AppNotConnected, Application().window_, title = 'Hiya')
#        self.assertRaises (AppNotConnected, Application().top_window_,)
#
#    def testStartProplem(self):
#        "Make sure the friendly class is set correctly"
#        self.assertRaises (AppStartError, Application().start_, 'Hiya')
#
#    #def testStartProplem(self):
#    #    "Make sure the friendly class is set correctly"
#    #    self.assertRaises (AppStartError, Application().start_, 'Hiya')
#


if __name__ == "__main__":
    #_unittests()

    unittest.main()


