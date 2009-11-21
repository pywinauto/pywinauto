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

# pylint:  disable-msg=W0212,F0401,R0904

import sys
sys.path.append(".")
from pywinauto.controls.win32_controls import *
from pywinauto import XMLHelpers

import unittest

# following imports are not required for the tests
# but are useful for debugging
import pprint

from pywinauto.timings import Timings
Timings.Fast()
Timings.window_find_timeout = 5


class ButtonTestCases(unittest.TestCase):
    "Unit tests for the ComboBoxWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start_("calc.exe")
        self.calc = self.app.SciCalc
        self.calc.MenuSelect("View->Scientific")

    def tearDown(self):
        "Close the application after tests"

        self.calc.TypeKeys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the button control"
        props = self.calc._6.GetProperties()

        self.assertEquals(
            "Button", props['FriendlyClassName'])

        self.assertEquals(
            self.calc._6.Texts(), ['6'])

        self.assertEquals(
            self.calc._6.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.calc._6, prop_name)(), props[prop_name])

    def test_set_if_needs_image(self):
        "test whether an image needs to be saved with the properties"
        self.assertEquals(self.calc._8._NeedsImageProp, False)

    def testFriendlyClass(self):
        "Test the FriendlyClassName method"
        self.assertEquals(self.calc._8.FriendlyClassName(), "Button")
        self.assertEquals(self.calc.Dec.FriendlyClassName(), "RadioButton")
        self.assertEquals(self.calc.Hyp.FriendlyClassName(), "CheckBox")

        children = self.calc.Children()
        no_text_buttons = [
            c for c in children
                if not c.WindowText() and c.Class() == "Button"]

        first_group = no_text_buttons[0]

        self.assertEquals(first_group.FriendlyClassName(), "GroupBox")

    def testCheckUncheck(self):
        "Test unchecking a control"

        self.calc.Inv.Check()
        self.assertEquals(self.calc.Inv.GetCheckState(), 1)
        self.calc.Inv.UnCheck()
        self.assertEquals(self.calc.Inv.GetCheckState(), 0)

    def testGetCheckState_unchecked(self):
        "unchecked"
        self.assertEquals(self.calc.Inv.GetCheckState(), 0)

    def testGetCheckState_checked(self):
        "checked"
        self.calc.Inv.Check()
        self.assertEquals(self.calc.Inv.GetCheckState(), 1)

#    def testGetCheckState_indeterminate(self):
#        "indeterminate"
#        self.calc.Inv.SetCheckIndeterminate()
#        self.assertEquals(self.calc.Inv.GetCheckState(), 0)

    def testClick(self):
        "Test clicking on buttons"
        self.calc._6.Click()
        self.calc._5.Click()
        self.calc['+'].Click()
        self.calc._4.Click()
        self.calc._3.Click()
        self.calc['='].Click()
        self.assertEquals(self.calc.Edit.Texts()[1], "108. ")

    def testIsSelected(self):
        "Test whether the control is selected or not"
        # Todo - I need to find an application where a button can be
        # selected - I don't see one in Calc at least :)
        self.assertEquals(self.calc.Hex.GetCheckState(), 0)

        self.calc.Hex.Click()

        self.assertEquals(self.calc.Hex.GetCheckState(), 1)


class ComboBoxTestCases(unittest.TestCase):
    "Unit tests for the ComboBoxWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start_("Notepad.exe")

        self.app.UntitledNotepad.MenuSelect("Format->Font")

        self.ctrl = self.app.Font.ComboBox2.WrapperObject()

    def tearDown(self):
        "Close the application after tests"

        self.app.Font.Cancel.CloseClick()

        # close the application
        self.app.UntitledNotepad.MenuSelect("File->Exit")

        if self.app.Notepad.No.Exists():
            self.app.Notepad.No.Click()

    def testGetProperties(self):
        "Test getting the properties for the combobox control"
        props = self.ctrl.GetProperties()

        self.assertEquals(
            "ComboBox", props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        "Test that ItemCount returns the correct number of items"
        self.assertEquals(self.ctrl.ItemCount(), 4)

    def testDroppedRect(self):
        "Test that the dropped rect is correct"
        rect = self.ctrl.DroppedRect()
        #import pdb;pdb.set_trace()
        self.assertEquals(rect.left, 0)
        self.assertEquals(rect.top, 0)
        self.assertEquals(rect.right, self.ctrl.ClientRect().right)
        self.assertEquals(rect.bottom, self.ctrl.Rectangle().height() - 3)

    def testSelectedIndex(self):
        "That the control returns the correct index for the selected item"
        self.ctrl.Select(2)
        self.assertEquals(self.ctrl.SelectedIndex(), 2)
        self.assertEquals(self.ctrl.Texts()[3], self.app.Font.Edit2.Texts()[1])

    def testSelect_negative(self):
        "Test that the Select method correctly handles negative indices"
        self.ctrl.Select(-1)
        self.assertEquals(self.ctrl.SelectedIndex(), 3)

    def testSelect_toohigh(self):
        "Test that the Select correctly raises if the item is too high"
        self.assertRaises(IndexError, self.ctrl.Select, 211)

    def testSelect_string(self):
        "Test that we can select based on a string"
        self.ctrl.Select(0)
        self.assertEquals(self.ctrl.SelectedIndex(), 0)
        self.ctrl.Select("Italic")
        self.assertEquals(self.ctrl.SelectedIndex(), 1)

        # now do it with a typo
        self.assertRaises(ValueError, self.ctrl.Select, "Bold Italc")

    def testSelect_simpleCombo(self):
        "Test selection for a simple combo"
        self.app.Font.ScriptComboBox.Select(0)
        self.assertEquals(self.app.Font.ScriptComboBox.SelectedIndex(), 0)
        self.app.Font.ScriptComboBox.Select(2)
        self.assertEquals(self.app.Font.ScriptComboBox.SelectedIndex(), 2)

    def testItemData(self):
        "Test that it doesn't raise"
        self.ctrl.ItemData(0)
        self.ctrl.ItemData(1)
        self.ctrl.ItemData("Italic")
        self.ctrl.ItemData(self.ctrl.ItemCount())

#
#    def testTexts(self):
#        pass
#

class ListBoxTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start_(r"c:\Program Files\Windows NT\Accessories\wordpad.exe")
        self.app.DocumentWordPad.MenuSelect("Insert->Date and time...")
        #pdb.set_trace()

        self.dlg = self.app.DateAndTime
        self.ctrl = self.dlg.ListBox.WrapperObject()

    def tearDown(self):
        "Close the application after tests"

        self.dlg.Cancel.Click()

        # close the application
        self.app.DocumentWordPad.MenuSelect("File->Exit")

    def testGetProperties(self):
        "Test getting the properties for the listbox control"
        props = self.ctrl.GetProperties()

        self.assertEquals(
            "ListBox", props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        "test that the count of items is correct"
        self.assertEquals(self.ctrl.ItemCount(), 14)

    def testItemData(self):
        "For the moment - just test that it does not raise"
        self.ctrl.ItemData(1)
        self.ctrl.ItemData(self.ctrl.ItemCount())

    def testSelectedIndices(self):
        "test that the selected indices are correct"
        self.assertEquals(self.ctrl.SelectedIndices(), (0, ))
        self.ctrl.Select(2)
        self.assertEquals(self.ctrl.SelectedIndices(), (2, ))

        self.assertTrue(type(self.ctrl.SelectedIndices()) == tuple)

    def testSelect(self):
        "Test selecting an item"
        self.ctrl.Select(5)
        self.assertEquals(self.ctrl.SelectedIndices(), (5, ))

        # get the text of the 2nd item (3rd item in list
        # because of empty WindowText)
        item_to_select = self.ctrl.Texts()[2]

        self.ctrl.Select(item_to_select)
        self.assertEquals(self.ctrl.SelectedIndices(), (1, ))

    def testGetSetItemFocus(self):
        "Test setting and getting the focus of a particular item"
        self.ctrl.SetItemFocus(0)
        self.assertEquals(self.ctrl.GetItemFocus(), 0)

        self.ctrl.SetItemFocus(5)
        self.assertEquals(self.ctrl.GetItemFocus(), 5)


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

        self.test_data = open(test_file, "rb").read()
        # remove the BOM if it exists
        self.test_data = self.test_data.replace("\xef\xbb\xbf", "")
        self.test_data = self.test_data.decode('utf-8')

        app.start_("Notepad.exe " + test_file)

        self.app = app
        self.dlg = app.UntitledNotepad
        self.ctrl = self.dlg.Edit.WrapperObject()

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
        self.ctrl.SetEditText("Here is\r\nsome text")
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
        for i in range(0, self.ctrl.LineCount()):
            self.assertEquals(
                self.ctrl.LineLength(i),
                len(self.test_data.split("\r\n")[i]))

    def testGetLine(self):
        "Test getting each line of the edit control"

        #for i in range(0, self.ctrl.LineCount()):
        #    print `self.ctrl.GetLine(i)`

        for i, line in enumerate(self.test_data.split("\r\n")):
            #print `line`
            #print `self.ctrl.GetLine(i)`
            self.assertEquals(self.ctrl.GetLine(i), line)

    def testTextBlock(self):
        "Test getting the text block of the edit control"
        self.assertEquals(self.ctrl.TextBlock(), self.test_data)

    def testSelection(self):
        "Test selecting text in the edit control in various ways"

        self.ctrl.Select(0, 0)
        self.assertEquals((0, 0), self.ctrl.SelectionIndices())

        self.ctrl.Select()
        self.assertEquals(
            (0, len(self.test_data)), self.ctrl.SelectionIndices())

        self.ctrl.Select(10, 25)
        self.assertEquals((10, 25), self.ctrl.SelectionIndices())

        self.ctrl.Select(18, 7)
        self.assertEquals((7, 18), self.ctrl.SelectionIndices())

        txt = u"\xc7a-va? Et"
        self.test_data.index(txt)

        self.ctrl.Select(txt)
        start = self.test_data.index(txt)
        end = start + len(txt)
        self.assertEquals((start, end), self.ctrl.SelectionIndices())


class DialogTestCases(unittest.TestCase):
    "Unit tests for the DialogWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start_("calc.exe")
        self.calc = self.app.SciCalc

        # write out the XML so that we can read it in later
        self.app.Calculator.WriteToXML("ref_controls.xml")

    def tearDown(self):
        "Close the application after tests"
        self.calc.TypeKeys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the dialog box"
        props = self.calc.GetProperties()

        self.assertEquals(
            "SciCalc", props['FriendlyClassName'])

        self.assertEquals(self.calc.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.calc, prop_name)(), props[prop_name])

    def testRunTests(self):
        "Test running the UI tests on the dialog"
        bugs = self.calc.RunTests()
        from pywinauto.controls.HwndWrapper import HwndWrapper
        self.assertEquals(True, isinstance(bugs[0][0][0], HwndWrapper))

    def testRunTestsWithReference(self):
        "Add a ref control, get the bugs and validate that the hande "
        import controlproperties
        ref_controls = [controlproperties.ControlProps(ctrl) for
                ctrl in XMLHelpers.ReadPropertiesFromFile("ref_controls.xml")]

        bugs = self.calc.RunTests(ref_controls = ref_controls)
        from pywinauto import tests
        tests.print_bugs(bugs)
        from pywinauto.controls.HwndWrapper import HwndWrapper
        self.assertEquals(True, isinstance(bugs[0][0][0], HwndWrapper))

    def testWriteToXML(self):
        "Write the output and validate that it is the same as the test output"
        self.calc.WriteToXML("test_output.xml")

        all_props = [self.calc.GetProperties()]
        all_props.extend([c.GetProperties() for c in self.calc.Children()])

        props = XMLHelpers.ReadPropertiesFromFile("test_output.xml")
        for i, ctrl in enumerate(props):
            for key, ctrl_value in ctrl.items():
                expected_value = all_props[i][key]
                if isinstance(ctrl_value, (list, tuple)):
                    self.assertEquals(list(ctrl_value), list(expected_value))

                elif "Image" in ctrl_value.__class__.__name__:
                    self.assertEquals(
                        ctrl_value.tostring(), expected_value.tostring())

                else:
                    self.assertEquals(ctrl_value, expected_value)

        import os
        os.unlink("test_output.xml")

    def testClientAreaRect(self):
        """Validate that the client area rect is the right size
        (comparing against the full rectangle)"""
        clientarea = self.calc.ClientAreaRect()
        self.assertEquals(self.calc.Rectangle().left + 3, clientarea.left)
        self.assertEquals(self.calc.Rectangle().top + 41, clientarea.top)
        self.assertEquals(self.calc.Rectangle().right - 3, clientarea.right)
        self.assertEquals(self.calc.Rectangle().bottom - 3, clientarea.bottom)


class PopupMenuTestCases(unittest.TestCase):
    "Unit tests for the DialogWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start_("notepad.exe")
        self.app.Notepad.Edit.RightClick()
        self.popup = self.app.PopupMenu.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.popup.TypeKeys("{ESC}")
        self.app.Notepad.TypeKeys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the PopupMenu"
        props = self.popup.GetProperties()

        self.assertEquals(
            "PopupMenu", props['FriendlyClassName'])

        self.assertEquals(self.popup.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.popup, prop_name)(), props[prop_name])

    def testIsDialog(self):
        "Ensure that IsDialog works correctly"
        self.assertEquals(True, self.popup.IsDialog())

    def test_menu_handle(self):
        "Ensure that the menu handle is returned"
        handle = self.popup._menu_handle()
        self.assertNotEquals(0, handle)


if __name__ == "__main__":
    #_unittests()
    unittest.main()
