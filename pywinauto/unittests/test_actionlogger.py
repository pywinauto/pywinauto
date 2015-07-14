# unit tests for actionlogger module
# Copyright (C) 2015 Intel Corporation
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

"Tests for actionlogger.py"

__revision__ = "$Revision$"

import unittest

import os, sys, logging
sys.path.append(".")
from pywinauto import actionlogger
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python, is_x64_OS


def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class ActionloggerTestCases(unittest.TestCase):
    "Unit tests for the actionlogger"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        actionlogger.enable()
        self.app = Application.start(_notepad_exe())
        self.logger = logging.getLogger('pywinauto')
        self.out = self.logger.parent.handlers[0].stream
        self.logger.parent.handlers[0].stream = open('test_logging.txt', 'w')

    def tearDown(self):
        "Close the application after tests"
        self.logger.parent.handlers[0].stream = self.out
        self.app.kill_()

    def __lineCount(self):
        # hack to get line count from current logger stream
        self.logger = logging.getLogger('pywinauto')
        self.logger.parent.handlers[0].stream.flush(); os.fsync(self.logger.parent.handlers[0].stream.fileno())
        with open(self.logger.parent.handlers[0].stream.name, 'r') as f:
            return len(f.readlines())

    def testEnableDisable(self):
        actionlogger.enable()
        prev_line_count = self.__lineCount()
        self.app.UntitledNotepad.TypeKeys('Test pywinauto logging', with_spaces=True)
        self.assertEquals(self.__lineCount(), prev_line_count+1)
        
        actionlogger.disable()
        self.app.UntitledNotepad.MenuSelect('Help->About Notepad')
        self.assertEquals(self.__lineCount(), prev_line_count+1)
        
        actionlogger.enable()
        self.app.Window_(title='About Notepad').OK.Click()
        self.assertEquals(self.__lineCount(), prev_line_count+2)


if __name__ == "__main__":
    unittest.main()
