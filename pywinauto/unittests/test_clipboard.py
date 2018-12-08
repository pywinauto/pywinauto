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

"""Tests for clipboard.py"""

import unittest

import sys
import time
sys.path.append(".")
from pywinauto.clipboard import GetClipboardFormats, GetData, GetFormatName, EmptyClipboard  # noqa E402
from pywinauto.application import Application  # noqa E402
from pywinauto.win32structures import RECT  # noqa E402
from pywinauto.timings import Timings  # noqa E402


class ClipboardTestCases(unittest.TestCase):

    """Unit tests for the clipboard"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()
        EmptyClipboard()
        self.app1 = Application().start("notepad.exe")
        self.app2 = Application().start("notepad.exe")

        self.app1.UntitledNotepad.move_window(RECT(0, 0, 200, 200))
        self.app2.UntitledNotepad.move_window(RECT(0, 200, 200, 400))

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.app1.UntitledNotepad.menu_select('File -> Exit')
        if self.app1.Notepad["Do&n't Save"].exists():
            self.app1.Notepad["Do&n't Save"].click()
        self.app1.kill()

        self.app2.UntitledNotepad.menu_select('File -> Exit')
        if self.app2.Notepad["Do&n't Save"].exists():
            self.app2.Notepad["Do&n't Save"].click()
        self.app2.kill()

    def testGetClipBoardFormats(self):
        typetext(self.app1, "here we are")
        copytext(self.app1)

        self.assertEqual(GetClipboardFormats(), [13, 16, 1, 7])

    def testGetFormatName(self):
        typetext(self.app1, "here we are")
        copytext(self.app1)

        self.assertEqual(
            [GetFormatName(f) for f in GetClipboardFormats()],
            ['CF_UNICODETEXT', 'CF_LOCALE', 'CF_TEXT', 'CF_OEMTEXT']
        )

    def testBug1452832(self):
        """Failing test for sourceforge bug 1452832

        Where GetData was not closing the clipboard. FIXED.
        """
        self.app1.UntitledNotepad.menu_select("Edit->Select All Ctrl+A")
        typetext(self.app1, "some text")
        copytext(self.app1)

        # was not closing the clipboard!
        data = GetData()
        self.assertEqual(data, "some text")

        self.assertEqual(gettext(self.app2), "")
        pastetext(self.app2)
        self.assertEqual(gettext(self.app2), "some text")


def gettext(app):
    return app.UntitledNotepad.Edit.texts()[1]


def typetext(app, text):
    app.UntitledNotepad.Edit.wait('enabled')
    app.UntitledNotepad.Edit.set_edit_text(text)
    time.sleep(0.3)


def copytext(app):
    app.UntitledNotepad.wait('enabled')
    app.UntitledNotepad.menu_item("Edit -> Select All").click_input()
    time.sleep(0.7)
    app.UntitledNotepad.wait('enabled')
    app.UntitledNotepad.menu_item("Edit -> Copy").click_input()
    time.sleep(1.0)


def pastetext(app):
    app.UntitledNotepad.wait('enabled')
    app.UntitledNotepad.menu_item("Edit -> Paste").click_input()


if __name__ == "__main__":
    unittest.main()
