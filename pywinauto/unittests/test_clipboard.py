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

'''Tests for clipboard.py'''

import unittest

import sys
import time
sys.path.append(".")
from pywinauto.clipboard import GetClipboardFormats, GetData, GetFormatName, EmptyClipboard
from pywinauto.application import Application
from pywinauto.win32structures import RECT
from pywinauto import backend


class ClipboardTestCases(unittest.TestCase):
    "Unit tests for the clipboard"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        EmptyClipboard()
        self.app1 = Application().start("notepad.exe")
        self.app2 = Application().start("notepad.exe")

        self.app1.UntitledNotepad.MoveWindow(RECT(0, 0, 200, 200))
        self.app2.UntitledNotepad.MoveWindow(RECT(0, 200, 200, 400))


    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.app1.UntitledNotepad.MenuSelect('File -> Exit')
        if self.app1.Notepad["Do&n't Save"].Exists():
            self.app1.Notepad["Do&n't Save"].Click()
        self.app1.kill_()

        self.app2.UntitledNotepad.MenuSelect('File -> Exit')
        if self.app2.Notepad["Do&n't Save"].Exists():
            self.app2.Notepad["Do&n't Save"].Click()
        self.app2.kill_()


    def testGetClipBoardFormats(self):
        typetext(self.app1, "here we are")
        copytext(self.app1)

        self.assertEquals(GetClipboardFormats(), [13, 16, 1, 7])

    def testGetFormatName(self):
        typetext(self.app1, "here we are")
        copytext(self.app1)

        self.assertEquals(
            [GetFormatName(f) for f in GetClipboardFormats()],
            ['CF_UNICODETEXT', 'CF_LOCALE', 'CF_TEXT', 'CF_OEMTEXT']
        )

    def testBug1452832(self):
        """Failing test for sourceforge bug 1452832

        Where GetData was not closing the clipboard. FIXED.
        """
        self.app1.UntitledNotepad.MenuSelect("Edit->Select All Ctrl+A")
        typetext(self.app1, "some text")
        copytext(self.app1)

        # was not closing the clipboard!
        data = GetData()
        self.assertEquals(data, "some text")


        self.assertEquals(gettext(self.app2), "")
        pastetext(self.app2)
        self.assertEquals(gettext(self.app2), "some text")



def gettext(app):
    return app.UntitledNotepad.Edit.texts()[1]

def typetext(app, text):
    app.UntitledNotepad.Edit.Wait('enabled')
    app.UntitledNotepad.Edit.SetEditText(text)
    time.sleep(0.3)


def copytext(app):
    app.UntitledNotepad.Wait('enabled')
    app.UntitledNotepad.MenuItem("Edit -> Select All").click_input()
    time.sleep(0.7)
    app.UntitledNotepad.Wait('enabled')
    app.UntitledNotepad.MenuItem("Edit -> Copy").click_input()
    time.sleep(1.0)

def pastetext(app):
    app.UntitledNotepad.Wait('enabled')
    app.UntitledNotepad.MenuItem("Edit -> Paste").click_input()

if __name__ == "__main__":
    unittest.main()
