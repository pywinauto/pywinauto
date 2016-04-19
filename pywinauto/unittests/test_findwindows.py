# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2007 Mark Mc Mahon
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

from __future__ import print_function

"Tests for findwindows.py"

import unittest

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto.findwindows import find_elements, find_element, find_window, find_windows
from pywinauto.findwindows import ElementNotFoundError, WindowNotFoundError
from pywinauto.findwindows import ElementAmbiguousError, WindowAmbiguousError
from pywinauto import backend


mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
mfc_app_1 = os.path.join(mfc_samples_folder, u"CmnCtrl2.exe")


#=========================================================================
def _unittests():
    "Do a quick test of finding some windows"
    windows = find_elements(
        class_name_re = "#32770",
        enabled_only = False,
        visible_only = False)

    for win in windows:
        print("==" * 20)
        print(win.dump_window())

class FindWindowsTestCases(unittest.TestCase):

    """Unit tests for findwindows.py module"""

    def setUp(self):
        """
        Start the application set some data and ensure the application
        is in the state we want it.
        """

        # start the application
        self.app = Application(backend='native')
        self.app = self.app.Start(mfc_app_1)

        self.dlg = self.app.CommonControlsSample

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()

    def testFindWindow(self):
        """
        Test if function find_window() works as expected
        including raising the exceptions
        """
        ctrl = self.dlg.OK.WrapperObject()
        handle = find_window(process=self.app.process, best_match='OK', top_level_only=False)

        self.assertEqual(handle, ctrl.handle)

        self.assertRaises(WindowNotFoundError, find_window, process=self.app.process, class_name='OK')

        self.assertRaises(WindowAmbiguousError, find_window,
                          process=self.app.process, class_name='Button', top_level_only=False)

    def testFindWindows(self):
        """
        Test if function find_window() works as expected
        including raising the exceptions
        """
        ctrl_hwnds = [elem.handle for elem in self.dlg.children() if elem.class_name() == 'Edit']
        handles = find_windows(process=self.app.process, class_name='Edit', top_level_only=False)

        self.assertEqual(set(handles), set(ctrl_hwnds))

        self.assertRaises(WindowNotFoundError, find_windows,
                          process=self.app.process, class_name='FakeClassName', found_index=1)


#class ApplicationTestCases(unittest.TestCase):
#    "Unit tests for the ListViewWrapper class"
#
#    def setUp(self):
#        """Start the application set some data and ensure the application
#        is in the state we want it."""
#        backend.activate("native")
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
    unittest.main()
