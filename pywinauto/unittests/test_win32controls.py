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

"Tests various standard windows controls"

__revision__ = "$Revision: 234 $"


from pywinauto.controls.win32_controls import *

import unittest

class EditTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()

        import os.path
        path = os.path.split(__file__)[0]

        test_file = os.path.join(path, "test.txt")

        self.test_data = open(test_file, "r").read()
        # remove the BOM if it exists
        self.test_data = self.test_data.replace("\xef\xbb\xbf", "")
        self.test_data = self.test_data.decode('utf-8')

        app.start_("Notepad.exe " + test_file)

        self.app = app
        self.dlg = app.UntitledNotepad
        self.ctrl = self.dlg.Edit.ctrl_()

        self.old_pos = self.dlg.Rectangle

        self.dlg.MoveWindow(10, 10, 400, 400)
        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.TypeKeys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"

        # set it back to it's old position so not to annoy users :-)
        self.old_pos = self.dlg.Rectangle

        # close the application
        self.dlg.MenuSelect("File->Exit")

        if self.app.Notepad.No.Exists():
            self.app.Notepad.No.Click()

    def testSetText(self):
        "Test setting the text of the edit control"
        self.ctrl.SetText("Here is\r\nsome text")
        self.assertEquals(
            "\n".join(self.ctrl.Texts()[1:]), "Here is\nsome text")

    def testTypeKeys(self):
        "Test typing some text into the edit control"
        # typekeys types at the current caret position
        # (start when opening a new file)
        added_text = "Here is some more Text"
        self.ctrl.TypeKeys(added_text, with_spaces = True)
        expected_text = added_text + self.test_data

        self.assertEquals(self.ctrl.TextBlock(), expected_text)

    def testSelect(self):
        "Test selecting some text of the edit control"
        self.ctrl.Select(10, 50)

        self.assertEquals((10, 50), self.ctrl.SelectionIndices())

    def testLineCount(self):
        "Test getting the line count of the edit control"
        for i in range (0, self.ctrl.LineCount()):
            self.assertEquals(
                self.ctrl.LineLength(i),
                len(self.test_data.split("\n")[i]))

    def testGetLine(self):
        "Test getting each line of the edit control"

        #for i in range(0, self.ctrl.LineCount()):
        #    print `self.ctrl.GetLine(i)`

        for i, line in enumerate(self.test_data.split("\n")):
            #print `line`
            #print `self.ctrl.GetLine(i)`
            self.assertEquals(self.ctrl.GetLine(i), line)

    def testTextBlock(self):
        "Test getting the text block of the edit control"
        self.assertEquals(self.ctrl.TextBlock(), self.test_data)


if __name__ == "__main__":
    #_unittests()

    unittest.main()
