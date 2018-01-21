# -*- coding: latin-1 -*-
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

"""Module containing tests for keyboard module"""

from __future__ import unicode_literals
from __future__ import print_function

import sys
import os
import unittest
import subprocess
import time
sys.path.append(".")
if sys.platform == 'win32':
    from pywinauto.keyboard import SendKeys, KeySequenceError
    from pywinauto.keyboard import KeyAction, VirtualKeyAction, PauseAction
    from pywinauto.sysinfo import is_x64_Python, is_x64_OS
    from pywinauto.application import Application
else:
    from pywinauto import mouse
    from pywinauto.linux.keyboard import SendKeys, KeySequenceError, KeyAction
    from pywinauto.linux import clipboard

def mfc_samples():
    mfc_samples_folder = os.path.join(
       os.path.dirname(__file__), r"..\..\apps\MFC_samples")
    if is_x64_Python():
        mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
    return mfc_samples_folder

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"

def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/SendKeysTester")
    return os.path.join(test_folder, r"send_keys_test_app")

class SendKeysTests(unittest.TestCase):
    """Unit tests for the Sendkeys module"""

    def setUp(self):
        """Start the application set some data and ensure the application is in the state we want it."""
        if sys.platform == 'win32':
            self.app = Application()
            self.app.start(_notepad_exe())
            self.dlg = self.app.UntitledNotepad
            self.ctrl = self.dlg.Edit
        else:
            self.app = subprocess.Popen("exec " + _test_app(), shell=True)
            time.sleep(0.1)
            mouse.click(coords=(300, 300))
            time.sleep(0.1)

    def tearDown(self):
        """Close the application after tests"""
        if sys.platform == 'win32':
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
        else:
            # call Popen.kill() on Linux since Application.kill_() is not implemented yet
            self.app.kill()

    def receive_text(self):
        """Receive data from text field"""
        received = ' '
        if sys.platform == 'win32':
            received = self.ctrl.TextBlock()
        else:
            time.sleep(0.2)
            SendKeys('^a')
            time.sleep(0.2)
            SendKeys('^c')
            SendKeys('{RIGHT}')
            received = clipboard.get_data()
        return received

    def __run_NormalCharacters_with_options(self, **args):
        """Make sure that sending any character in range """
        #unused var: missed = []
        for i in range(32, 127):

            # skip characters that must be escaped
            if chr(i) in '~!@#$%^&*()_+{}|:"<>? ':
                continue

            SendKeys(chr(i), pause = .001, **args)
            received = self.receive_text()[-1]

            self.assertEqual(i, ord(received))

    # Space tests
    def testNormalWithSpaces(self):
        """Make sure that with spaces option works"""
        self.__run_NormalCharacters_with_options(with_spaces = True)

    def testNormalWithoutSpaces(self):
        """Make sure that with spaces option works"""
        self.__run_NormalCharacters_with_options(with_spaces = False)


    def testSpaceWithSpaces(self):
        """Make sure that with spaces option works"""
        SendKeys(" \t \t ", pause = .001, with_spaces = True)
        received = self.receive_text()
        self.assertEqual("   ", received)

    def testSpaceWithoutSpaces(self):
        """Make sure that with spaces option works"""
        SendKeys(" \t \t ", pause = .001, with_spaces = False)
        received = self.receive_text()
        self.assertEqual("", received)


    # Tab tests
    def testNormalWithTabs(self):
        """Make sure that with spaces option works"""
        self.__run_NormalCharacters_with_options(with_tabs = True)

    def testNormalWithoutTabs(self):
        """Make sure that with spaces option works"""
        self.__run_NormalCharacters_with_options(with_tabs = False)

    def testTabWithTabs(self):
        """Make sure that with spaces option works"""
        SendKeys("\t \t \t", pause = .1, with_tabs = True)
        received = self.receive_text()
        self.assertEqual("\t\t\t", received)

    def testTabWithoutTabs(self):
        """Make sure that with spaces option works"""
        SendKeys("\t a\t b\t", pause = .1, with_tabs = False)
        received = self.receive_text()
        self.assertEqual("ab", received)


    def testTab(self):
        """Make sure that with spaces option works"""
        SendKeys("{TAB}  {TAB} ", pause = .3)
        received = self.receive_text()
        self.assertEqual("\t\t", received)


    # Newline tests
    def testNormalWithNewlines(self):
        """Make sure that with spaces option works"""
        self.__run_NormalCharacters_with_options(with_newlines = True)

    def testNormalWithoutNewlines(self):
        """Make sure that with_newlines option works"""
        self.__run_NormalCharacters_with_options(with_newlines = False)

    def testNewlinesWithNewlines(self):
        """Make sure that with_newlines option works"""
        SendKeys("\t \t \t a~\tb\nc", pause = .5, with_newlines = True)
        received = self.receive_text()
        if sys.platform == 'win32':
            self.assertEqual("a\r\nb\r\nc", received)
        else:
            self.assertEqual("a\nb\nc", received)

    def testNewlinesWithoutNewlines(self):
        """"Make sure that with_newlines option works"""
        SendKeys("\t \t \t\na", pause = .01, with_newlines = False)
        received = self.receive_text()
        self.assertEqual("a", received)


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
    #        received = self.receive_text()[-1]

    #        if c == received:
    #            matched += 1
    #        else:
    #            print("expected %s, recieved %s"% (
    #                repr(c), repr(received)))

    #    self.assertEqual(matched, len(extended_chars))

    def testCharsThatMustBeEscaped(self):
        """Make sure that escaping characters works"""
        SendKeys("{%}{^}{+}{(}{)}{{}{}}{~}")
        received = self.receive_text()
        self.assertEqual("%^+(){}~", received)

    def testIncorrectCases(self):
        """Make sure that incorrect key sequences raise an exception"""
        self.assertRaises(KeySequenceError, SendKeys, "{ENTER")
        self.assertRaises(KeySequenceError, SendKeys, "ENTER)")
        self.assertRaises(RuntimeError, SendKeys, "%{Enterius}")
        self.assertRaises(KeySequenceError, SendKeys, "{PAUSE small}")

        try:
            SendKeys("{ENTER five}")
        except KeySequenceError as exc:
            self.assertEqual("invalid repetition count five", str(exc))

        try:
            SendKeys("ENTER}")
        except KeySequenceError as exc:
            self.assertEqual("`}` should be preceeded by `{`", str(exc))

    def testKeyDescription(self):
        """Test KeyAction._"""
        self.assertEqual("<X>", str(KeyAction("X")))
        self.assertEqual("<Y down>", str(KeyAction("Y", up=False)))
        self.assertEqual("<Y up>", str(KeyAction("Y", down=False)))
        #self.assertEqual("<ENTER>", str(VirtualKeyAction(13))) # == "<VK_RETURN>" in Python 2.7 (TODO)
        if sys.platform == 'win32':
            self.assertEqual("<PAUSE 1.00>", str(PauseAction(1.0)))

    def testRepetition(self):
        """Make sure that repeated action works"""
        SendKeys("{TAB 3}{PAUSE 0.5}{F 3}", pause = .3)
        received = self.receive_text()
        self.assertEqual("\t\t\tFFF", received)

    def testShiftModifier(self):
        """Make sure that Shift modifier works"""
        SendKeys("+(a)")
        received = self.receive_text()
        self.assertEqual("A", received)

    if sys.platform != 'win32':
        def testAltModifier(self):
            """Make sure that alt modifier works"""
            clipboard.set_data('abc')
            # check alt via opening edit menu and paste text from clipboard
            time.sleep(0.3)
            SendKeys('%(e)')
            time.sleep(0.3)
            SendKeys('{ENTER}')
            received = self.receive_text()
            self.assertEqual('abc', received)


if sys.platform == 'win32':
    class SendKeysModifiersTests(unittest.TestCase):
        """Unit tests for the Sendkeys module (modifiers)"""

        def setUp(self):
            """Start the application and ensure it's in the state we want"""
            self.app = Application().start(os.path.join(mfc_samples(), u"CtrlTest.exe"))
            self.dlg = self.app.Control_Test_App

        def tearDown(self):
            """Close the application after tests"""
            try:
                self.dlg.Close(0.5)
            except Exception:
                pass
            finally:
                self.app.kill_()

        def testModifiersForFewChars(self):
            """Make sure that repeated action works"""
            SendKeys("%(SC)", pause = .3)
            dlg = self.app.Window_(title='Using C++ Derived Class')
            dlg.Wait('ready')
            dlg.Done.CloseClick()
            dlg.WaitNot('visible')

            SendKeys("%(H{LEFT}{UP}{ENTER})", pause = .3)
            dlg = self.app.Window_(title='Sample Dialog with spin controls')
            dlg.Wait('ready')
            dlg.Done.CloseClick()
            dlg.WaitNot('visible')


#====================================================================
if __name__ == "__main__":
    unittest.main()

    #import doctest
    #doctest.testmod()
