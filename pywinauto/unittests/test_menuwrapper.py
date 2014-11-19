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

"Tests for HwndWrapper"

import sys
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.controls.HwndWrapper import HwndWrapper
from pywinauto import win32structures, win32defines
from pywinauto.controls import menuwrapper

import time
import pprint
import pdb
import ctypes

__revision__ = "$Revision: 234 $"

#try:
#    from pywinauto.controls.pywinauto import *
#except ImportError:
#    # allow it to be imported in a dev environment
#    import sys
#
#    pywinauto_imp = "\\".join(__file__.split('\\')[:-3])
#    print "sdfdsf", pywinauto_imp
#    sys.path.append(pywinauto_imp)
#    from pywinauto.controls.HwndWrapper import *

import unittest

class MenuWrapperTests(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        self.app.start_("Notepad.exe")

        self.dlg = self.app.Notepad

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.TypeKeys("%{F4}")


    def testInvalidHandle(self):
        "Test that an exception is raised with an invalid menu handle"
        #self.assertRaises(InvalidWindowHandle, HwndWrapper, -1)
        pass


    def testItemCount(self):
        self.assertEquals(5, self.dlg.Menu().ItemCount())

    def testItem(self):
        pass

    def testItems(self):
        pass
    def testGetProperties(self):
        pass
    def testGetMenuPath(self):
        pass
    def test__repr__(self):
        pass



if __name__ == "__main__":
    unittest.main()

