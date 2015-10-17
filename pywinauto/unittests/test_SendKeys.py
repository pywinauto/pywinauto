# -*- coding: latin-1 -*-
# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2012 Michael Herrmann
# Copyright (C) 2010 Mark Mc Mahon
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
from __future__ import unicode_literals
from __future__ import print_function

"""Module containing tests for SendKeys Module

>>> from SendKeys import *
>>> SendKeys("a\\r\\n")
>>> val = input()
>>> print val
a
>>>
>>> SendKeys(u"\x01\\r\\n")
>>> val = input()
>>> print val
u"\x01"
>>>
"""

import sys
sys.path.append(".")
from pywinauto.SendKeysCtypes import SendKeys, DEBUG, KeySequenceError, KeyAction
from pywinauto import six
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto.application import Application
from pywinauto.actionlogger import ActionLogger
import os
import locale
import unittest

# Fix Python 2.x.
if six.PY2:
    input_func = raw_input
else:
    input_func = input

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class SendKeysTests(unittest.TestCase):
    "Unit tests for the Sendkeys module"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application()
        self.app.start(_notepad_exe())
        
        self.dlg = self.app.UntitledNotepad
        self.ctrl = self.dlg.Edit

    def tearDown(self):
        "Close the application after tests"
        try:
            self.dlg.Close(0.1)
        except Exception: # TimeoutError:
            pass
        try:
            if self.app.Notepad["Do&n't Save"].Exists():
                self.app.Notepad["Do&n't Save"].Click()
                self.app.Notepad["Do&n't Save"].WaitNot('visible')
        except Exception: # TimeoutError:
            pass
        finally:
            if self.dlg.Exists(timeout=0.1):
                self.app.kill_()

    def __run_NormalCharacters_with_options(self, **args):
        "Make sure that sending any character in range "

        #unused var: missed = []
        for i in range(32, 127):

            # skip characters that must be escaped
            if chr(i) in (' ', '%', '^', '+', '(', ')', '{', '}', '~'):
                continue

            SendKeys(chr(i), pause = .001, **args)
            received = self.ctrl.TextBlock()[-1]

            self.assertEquals(i, ord(received))

    # Space tests
    def testNormalWithSpaces(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_spaces = True)

    def testNormalWithoutSpaces(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_spaces = False)

    def testSpaceWithSpaces(self):
        "Make sure that with spaces option works"
        SendKeys(" \t \t ", pause = .001, with_spaces = True)
        received = self.ctrl.TextBlock()
        self.assertEquals("   ", received)

    def testSpaceWithoutSpaces(self):
        "Make sure that with spaces option works"
        SendKeys(" \t \t ", pause = .001, with_spaces = False)
        received = self.ctrl.TextBlock()
        self.assertEquals("", received)


    # Tab tests
    def testNormalWithTabs(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_tabs = True)

    def testNormalWithoutTabs(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_tabs = False)

    def testTabWithTabs(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t", pause = .1, with_tabs = True)
        received = self.ctrl.TextBlock()
        self.assertEquals("\t\t\t", received)

    def testTabWithoutTabs(self):
        "Make sure that with spaces option works"
        SendKeys("\t a\t b\t", pause = .1, with_tabs = False)
        received = self.ctrl.TextBlock()
        self.assertEquals("ab", received)


    def testTab(self):
        "Make sure that with spaces option works"
        SendKeys("{TAB}  {TAB} ", pause = .3)
        received = self.ctrl.TextBlock()
        self.assertEquals("\t\t", received)


    # Newline tests
    def testNormalWithNewlines(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_newlines = True)

    def testNormalWithoutNewlines(self):
        "Make sure that with_newlines option works"
        self.__run_NormalCharacters_with_options(with_newlines = False)

    def testNewlinesWithNewlines(self):
        "Make sure that with_newlines option works"
        SendKeys("\t \t \t a~\tb\nc", pause = .5, with_newlines = True)
        received = self.ctrl.TextBlock()
        self.assertEquals("a\r\nb\r\nc", received)

    def testNewlinesWithoutNewlines(self):
        "Make sure that with_newlines option works"
        SendKeys("\t \t \t\na", pause = .01, with_newlines = False)
        received = self.ctrl.TextBlock()
        self.assertEquals("a", received)


    #def testANSIExtendedCharacters(self):
    #    "Make sure that sending any character in range "
    #    #self.cmd = Application()
    #    #self.cmd.start("cmd.exe", create_new_console=True, wait_for_idle=False)
    #    ActionLogger().log('Preferred encoding: ' + locale.getpreferredencoding())
    #    
    #    #os.system("chcp 850")
    #    matched = 0
    #    extended_chars = b"\x81\x82\x83\xa1\xe1\xff"
    #    for char in extended_chars:

    #        if six.PY3:
    #            c = str(char)
    #        else:
    #            c = char.decode(locale.getpreferredencoding()) #'cp850')
    #        SendKeys(c, pause = .01)
    #        received = self.ctrl.TextBlock()[-1]

    #        if c == received:
    #            matched += 1
    #        else:
    #            print("expected %s, recieved %s"% (
    #                repr(c), repr(received)))

    #    self.assertEquals(matched, len(extended_chars))

    def testCharsThatMustBeEscaped(self):
        "Make sure that escaping characters works"
        SendKeys("{%}{^}{+}{(}{)}{{}{}}{~}")
        received = self.ctrl.TextBlock()
        self.assertEquals("%^+(){}~", received)

    def testIncorrectCases(self):
        "Make sure that incorrect key sequences raise an exception"
        DEBUG = 1
        self.assertRaises(KeySequenceError, SendKeys, "{ENTER")
        self.assertRaises(RuntimeError, SendKeys, "%{Enterius}")
        try:
            SendKeys("ENTER}")
        except KeySequenceError as exc:
            self.assertEquals("`}` should be preceeded by `{`", str(exc))


#====================================================================
if __name__ == "__main__":
    unittest.main()

    #import doctest
    #doctest.testmod()


