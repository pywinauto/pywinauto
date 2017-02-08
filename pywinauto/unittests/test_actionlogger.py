# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Tests for actionlogger.py"""

import unittest

import os, sys, logging
sys.path.append(".")
from pywinauto import actionlogger
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python
from pywinauto.sysinfo import is_x64_OS
from pywinauto.timings import Timings


def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class ActionloggerTestCases(unittest.TestCase):

    """Unit tests for the actionlogger"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()
        actionlogger.enable()
        self.app = Application().start(_notepad_exe())
        self.logger = logging.getLogger('pywinauto')
        self.out = self.logger.parent.handlers[0].stream
        self.logger.parent.handlers[0].stream = open('test_logging.txt', 'w')

    def tearDown(self):
        """Close the application after tests"""
        self.logger.parent.handlers[0].stream = self.out
        self.app.kill_()

    def __lineCount(self):
        """hack to get line count from current logger stream"""
        self.logger = logging.getLogger('pywinauto')
        self.logger.parent.handlers[0].stream.flush(); os.fsync(self.logger.parent.handlers[0].stream.fileno())
        with open(self.logger.parent.handlers[0].stream.name, 'r') as f:
            return len(f.readlines())

    def testEnableDisable(self):
        actionlogger.enable()
        prev_line_count = self.__lineCount()
        self.app.UntitledNotepad.type_keys('Test pywinauto logging', with_spaces=True)
        self.assertEquals(self.__lineCount(), prev_line_count+1)

        actionlogger.disable()
        self.app.UntitledNotepad.MenuSelect('Help->About Notepad')
        self.assertEquals(self.__lineCount(), prev_line_count+1)

        actionlogger.enable()
        self.app.window(title='About Notepad').OK.Click()
        self.assertEquals(self.__lineCount(), prev_line_count+2)


if __name__ == "__main__":
    unittest.main()
