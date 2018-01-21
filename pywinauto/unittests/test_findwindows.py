# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests for findwindows.py"""
from __future__ import print_function

import unittest

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python
from pywinauto.findwindows import find_window, find_windows
from pywinauto.findwindows import WindowNotFoundError
from pywinauto.findwindows import WindowAmbiguousError
from pywinauto.timings import Timings


mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
mfc_app_1 = os.path.join(mfc_samples_folder, u"CmnCtrl2.exe")


class FindWindowsTestCases(unittest.TestCase):

    """Unit tests for findwindows.py module"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Defaults()

        # start the application
        self.app = Application(backend='win32')
        self.app = self.app.Start(mfc_app_1)

        self.dlg = self.app.CommonControlsSample

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()

    def test_find_window(self):
        """Test if function find_window() works as expected including raising the exceptions"""
        ctrl = self.dlg.OK.WrapperObject()
        handle = find_window(process=self.app.process, best_match='OK', top_level_only=False)

        self.assertEqual(handle, ctrl.handle)

        self.assertRaises(WindowNotFoundError, find_window, process=self.app.process, class_name='OK')

        self.assertRaises(WindowAmbiguousError, find_window,
                          process=self.app.process, class_name='Button', top_level_only=False)

    def test_find_windows(self):
        """Test if function find_windows() works as expected including raising the exceptions"""
        ctrl_hwnds = [elem.handle for elem in self.dlg.children() if elem.class_name() == 'Edit']
        handles = find_windows(process=self.app.process, class_name='Edit', top_level_only=False)

        self.assertEqual(set(handles), set(ctrl_hwnds))

        self.assertRaises(WindowNotFoundError, find_windows,
                          process=self.app.process, class_name='FakeClassName', found_index=1)


if __name__ == "__main__":
    unittest.main()
