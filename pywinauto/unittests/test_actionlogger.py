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

"""Tests for actionlogger.py"""

import unittest

import os
import sys
import logging
import mock
from six.moves import reload_module
sys.path.append(".")
from pywinauto import actionlogger  # noqa: E402
from pywinauto.application import Application  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.sysinfo import is_x64_OS  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402


def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class ActionLoggerOnStadardLoggerTestCases(unittest.TestCase):

    """Unit tests for the actionlogger based on _StandardLogger"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()
        actionlogger.enable()
        self.app = Application().start(_notepad_exe())
        self.logger = logging.getLogger('pywinauto')
        self.out = self.logger.handlers[0].stream
        self.logger.handlers[0].stream = open('test_logging.txt', 'w')

    def tearDown(self):
        """Close the application after tests"""
        self.logger.handlers[0].stream.close()
        self.logger.handlers[0].stream = self.out
        self.app.kill_()

    def __lineCount(self):
        """hack to get line count from current logger stream"""
        self.logger = logging.getLogger('pywinauto')
        self.logger.handlers[0].stream.flush()
        os.fsync(self.logger.handlers[0].stream.fileno())
        with open(self.logger.handlers[0].stream.name, 'r') as f:
            return len(f.readlines())

    def testEnableDisable(self):
        actionlogger.enable()
        prev_line_count = self.__lineCount()
        self.app.UntitledNotepad.type_keys('Test pywinauto logging', with_spaces=True)
        self.assertEqual(self.__lineCount(), prev_line_count + 1)

        actionlogger.disable()
        self.app.UntitledNotepad.MenuSelect('Help->About Notepad')
        self.assertEqual(self.__lineCount(), prev_line_count + 1)

        actionlogger.enable()
        self.app.window(title='About Notepad').OK.Click()
        self.assertEqual(self.__lineCount(), prev_line_count + 2)


class ActionLoggerOnCustomLoggerTestCases(unittest.TestCase):

    """Unit tests for the actionlogger based on _CustomLogger"""

    def setUp(self):
        """Set a mock logger package in modules"""

        # http://www.voidspace.org.uk/python/mock/examples.html#mocking-imports-with-patch-dict
        self.mock_logger = mock.MagicMock()
        self.modules = {
            "logger": self.mock_logger,
        }
        self.module_patcher = mock.patch.dict('sys.modules', self.modules)
        self.module_patcher.start()

        self.logger_patcher = None

    def tearDown(self):
        """Clean ups"""
        if self.logger_patcher:
            self.logger_patcher.stop()

        self.module_patcher.stop()
        reload_module(actionlogger)

    def test_import_clash(self):
        """Test a custom logger import clash: issue #315"""

        # Re-patch for this specific test:
        # we have a module with a name 'logger' and even a 'Logger' object
        # but there is no 'sectionStart' attribute in the object
        self.module_patcher.stop()
        self.mock_logger.Logger.sectionStart = None
        self.module_patcher = mock.patch.dict('sys.modules', self.modules)
        self.module_patcher.start()

        reload_module(actionlogger)
        self.assertEqual(False, actionlogger._found_logger)

        # Verify the fallback to the standard logger
        active_logger = actionlogger.ActionLogger()
        self.assertEqual(actionlogger._StandardLogger, type(active_logger))

    def test_import_custom_logger(self):
        """Test if custom logger class can be imported"""
        reload_module(actionlogger)
        self.assertEqual(True, actionlogger._found_logger)

        # Check there is no instance of logger created on import
        self.mock_logger.Logger.assert_not_called()

        active_logger = actionlogger.ActionLogger()
        self.assertEqual(actionlogger._CustomLogger, type(active_logger))

    def test_logger_disable_and_reset(self):
        """Test if the logger can be disabled and level reset"""
        reload_module(actionlogger)

        # verify on mock
        self.logger_patcher = mock.patch('pywinauto.actionlogger.ActionLogger', spec=True)
        mockLogger = self.logger_patcher.start()

        actionlogger.disable()
        self.assertTrue(mockLogger.disable.called)

        actionlogger.reset_level()
        self.assertTrue(mockLogger.reset_level.called)

    def test_logger_enable_mapped_to_reset_level(self):
        """Test if the logger enable is mapped to reset_level"""
        reload_module(actionlogger)

        # verify on mock
        self.logger_patcher = mock.patch('pywinauto.actionlogger.ActionLogger', spec=True)
        mockLogger = self.logger_patcher.start()

        actionlogger.enable()
        self.assertTrue(mockLogger.reset_level.called)


if __name__ == "__main__":
    unittest.main()
