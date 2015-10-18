# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
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

"Tests various standard windows controls"
from __future__ import unicode_literals

# pylint:  disable-msg=W0212,F0401,R0904

import os, sys
import codecs
sys.path.append(".")
from pywinauto import XMLHelpers, win32defines #, six
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto.application import Application

import unittest

# following imports are not required for the tests
# but are useful for debugging
#import pprint

from pywinauto.timings import Timings
Timings.Fast()
Timings.window_find_timeout = 3
Timings.closeclick_dialog_close_wait = .5

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_samples")
MFC_tutorial_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_tutorial")

if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
    MFC_tutorial_folder = os.path.join(MFC_tutorial_folder, 'x64')


class ButtonTestCases(unittest.TestCase):

    """Unit tests for the ButtonWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        if is_x64_Python() or not is_x64_OS():
            self.app.start(r"C:\Windows\System32\calc.exe")
        else:
            self.app.start(r"C:\Windows\SysWOW64\calc.exe")
        self.calc = self.app.Calculator
        self.calc.MenuSelect("View->Scientific")

    def tearDown(self):
        "Close the application after tests"

        self.app.kill_()
        #self.calc.TypeKeys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the button control"
        props = self.calc.Degrees.GetProperties()

        self.assertEquals(
            "RadioButton", props['FriendlyClassName'])

        self.assertEquals(
            self.calc.Degrees.Texts(), ['Degrees'])

        self.assertEquals(
            self.calc.Degrees.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(
                getattr(self.calc.Degrees, prop_name)(), props[prop_name])

    def test_NeedsImageProp(self):

        """test whether an image needs to be saved with the properties"""

        self.assertEquals(self.calc.Button5._NeedsImageProp, False)
        self.assertEquals('Image' in self.calc.Button5.GetProperties(), False)
        #self.assertNotIn('Image', self.calc.Button5.GetProperties())
        # assertIn and assertNotIn are not supported in Python 2.6

    def testFriendlyClass(self):
        "Test the FriendlyClassName method"
        self.assertEquals(self.calc.Button9.FriendlyClassName(), "Button")
        self.assertEquals(self.calc.Degree.FriendlyClassName(), "RadioButton")
        #self.assertEquals(self.calc.Hex.FriendlyClassName(), "CheckBox")

        #children = self.calc.Children()
        #no_text_buttons = [
        #    c for c in children
        #        if not c.WindowText() and c.Class() == "Button"]

        #first_group = no_text_buttons[0]

        #self.assertEquals(first_group.FriendlyClassName(), "GroupBox")

    def testCheckUncheck(self):
        "Test unchecking a control"

        self.calc.Grads.Check()
        self.assertEquals(self.calc.Grads.GetCheckState(), 1)
        self.calc.Grads.UnCheck()
        self.assertEquals(self.calc.Grads.GetCheckState(), 0)

    def testGetCheckState_unchecked(self):
        "unchecked"
        self.assertEquals(self.calc.Grads.GetCheckState(), 0)

    def testGetCheckState_checked(self):
        "checked"
        self.calc.Grads.Check()
        self.assertEquals(self.calc.Grads.GetCheckState(), 1)

#    def testGetCheckState_indeterminate(self):
#        "indeterminate"
#        self.calc.Inv.SetCheckIndeterminate()
#        self.assertEquals(self.calc.Inv.GetCheckState(), 0)

    def testClick(self):
        "Test clicking on buttons"
        self.calc.Button15.Click()  # "6"
        self.calc.Button10.Click()  # "5"
        self.calc.Button23.Click()  # "+"
        self.calc.Button4.Click()   # "4"
        self.calc.Button16.Click()  # "3"
        self.calc.Button28.Click()  # "="
        self.assertEquals(self.calc.ChildWindow(class_name='Static', ctrl_index=5).Texts()[0], "108")

    def testIsSelected(self):
        "Test whether the control is selected or not"
        # Todo - I need to find an application where a button can be
        # selected - I don't see one in Calc at least :)
        self.assertEquals(self.calc.Radians.GetCheckState(), 0)

        self.calc.Radians.Click()

        self.assertEquals(self.calc.Radians.GetCheckState(), 1)


class CheckBoxTests(unittest.TestCase):
    "Unit tests for the CheckBox specific methods of the ButtonWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.tree = self.dlg.TreeView.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

    def testCheckUncheckByClick(self):
        "test for CheckByClick and UncheckByClick"
        self.dlg.TVS_HASLINES.CheckByClick()
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_CHECKED)
        self.assertEquals(self.tree.HasStyle(win32defines.TVS_HASLINES), True)
        
        self.dlg.TVS_HASLINES.CheckByClick() # make sure it doesn't uncheck the box unexpectedly
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_CHECKED)
        
        self.dlg.TVS_HASLINES.UncheckByClick()
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_UNCHECKED)
        self.assertEquals(self.tree.HasStyle(win32defines.TVS_HASLINES), False)
        
        self.dlg.TVS_HASLINES.UncheckByClick() # make sure it doesn't check the box unexpectedly
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_UNCHECKED)

    def testCheckUncheckByClickInput(self):
        "test for CheckByClickInput and UncheckByClickInput"
        self.dlg.TVS_HASLINES.CheckByClickInput()
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_CHECKED)
        self.assertEquals(self.tree.HasStyle(win32defines.TVS_HASLINES), True)
        
        self.dlg.TVS_HASLINES.CheckByClickInput() # make sure it doesn't uncheck the box unexpectedly
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_CHECKED)
        
        self.dlg.TVS_HASLINES.UncheckByClickInput()
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_UNCHECKED)
        self.assertEquals(self.tree.HasStyle(win32defines.TVS_HASLINES), False)
        
        self.dlg.TVS_HASLINES.UncheckByClickInput() # make sure it doesn't check the box unexpectedly
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_UNCHECKED)

    def testSetCheckIndeterminate(self):
        "test for SetCheckIndeterminate"
        self.dlg.TVS_HASLINES.SetCheckIndeterminate()
        self.assertEquals(self.dlg.TVS_HASLINES.GetCheckState(), win32defines.BST_CHECKED)
        # TODO: find an application with the check box that supports indeterminate state (gray-checked)


class ButtonOwnerdrawTestCases(unittest.TestCase):

    """Unit tests for the ButtonWrapper(ownerdraw button)"""

    def setUp(self):

        """Start the sample application. Open a tab with ownerdraw button."""

        # start the application
        self.app = Application().Start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))
        # open the needed tab
        self.app.active_().TabControl.Select(1)

    def tearDown(self):

        """Close the application after tests"""

        self.app.kill_()

    def test_NeedsImageProp(self):

        """test whether an image needs to be saved with the properties"""

        active_window = self.app.active_()
        self.assertEquals(active_window.Button2._NeedsImageProp, True)
        self.assertEquals('Image' in active_window.Button2.GetProperties(), True)
        #self.assertIn('Image', active_window.Button2.GetProperties())
        # assertIn and assertNotIn are not supported in Python 2.6


class ComboBoxTestCases(unittest.TestCase):

    """Unit tests for the ComboBoxWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()

        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"))

        self.app.Common_Controls_Sample.TabControl.Select("CSpinButtonCtrl")

        self.ctrl = self.app.Common_Controls_Sample.AlignmentComboBox.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

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
        self.assertEquals(self.ctrl.ItemCount(), 3)

    def testDroppedRect(self):
        "Test that the dropped rect is correct"
        rect = self.ctrl.DroppedRect()
        #import pdb;pdb.set_trace()
        self.assertEquals(rect.left, 0)
        self.assertEquals(rect.top, 0)
        self.assertEquals(rect.right, self.ctrl.ClientRect().right)
        self.assertEquals(rect.bottom, self.ctrl.Rectangle().height() + 48)

    def testSelectedIndex(self):
        "That the control returns the correct index for the selected item"
        self.ctrl.Select(1)
        self.assertEquals(self.ctrl.SelectedIndex(), 1)
        #self.assertEquals(self.ctrl.Texts()[3], self.app.Font.Edit2.Texts()[1])

    def testSelect_negative(self):
        "Test that the Select method correctly handles negative indices"
        self.ctrl.Select(-1)
        self.assertEquals(self.ctrl.SelectedIndex(), 2)

    def testSelect_toohigh(self):
        "Test that the Select correctly raises if the item is too high"
        self.assertRaises(IndexError, self.ctrl.Select, 211)

    def testSelect_string(self):
        "Test that we can select based on a string"
        self.ctrl.Select(0)
        self.assertEquals(self.ctrl.SelectedIndex(), 0)
        self.ctrl.Select("Left (UDS_ALIGNLEFT)")
        self.assertEquals(self.ctrl.SelectedIndex(), 1)
        self.assertEquals(self.ctrl.SelectedText(), "Left (UDS_ALIGNLEFT)")

        # now do it with a typo
        self.assertRaises(ValueError, self.ctrl.Select, "Right (UDS_ALIGNRIGT)")

    def testSelect_simpleCombo(self):
        "Test selection for a simple combo"
        self.app.Common_Controls_Sample.OrientationComboBox.Select(0)
        self.assertEquals(self.app.Common_Controls_Sample.OrientationComboBox.SelectedIndex(), 0)
        self.app.Common_Controls_Sample.OrientationComboBox.Select(1)
        self.assertEquals(self.app.Common_Controls_Sample.OrientationComboBox.SelectedIndex(), 1)

    def testItemData(self):
        "Test that it doesn't raise"
        self.ctrl.ItemData(0)
        self.ctrl.ItemData(1)
        self.ctrl.ItemData("Right (UDS_ALIGNRIGHT)")
        self.ctrl.ItemData(self.ctrl.ItemCount() - 1)


class ListBoxTestCases(unittest.TestCase):

    """Unit tests for the ListBoxWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        app_path = os.path.join(MFC_tutorial_folder, "MFC_Tutorial9.exe")
        self.app.start(app_path)

        self.dlg = self.app.MFC_Tutorial9
        self.dlg.Wait('ready', timeout=20)
        self.dlg.TypeYourTextEdit.TypeKeys('qqq')
        self.dlg.Add.Click()
        
        self.dlg.TypeYourTextEdit.Select()
        self.dlg.TypeYourTextEdit.TypeKeys('123')
        self.dlg.Add.Click()
        
        self.dlg.TypeYourTextEdit.Select()
        self.dlg.TypeYourTextEdit.TypeKeys('third item', with_spaces=True)
        self.dlg.Add.Click()
        
        self.ctrl = self.dlg.ListBox.WrapperObject()

    def tearDown(self):
        "Close the application after tests"

        #self.dlg.Cancel.Click()

        # close the application
        self.app.kill_()

    def testGetProperties(self):
        "Test getting the properties for the list box control"
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
        self.assertEquals(self.ctrl.ItemCount(), 3)

    def testItemData(self):
        "For the moment - just test that it does not raise"
        self.ctrl.ItemData(1)
        self.ctrl.ItemData(self.ctrl.ItemCount() - 1)

    def testSelectedIndices(self):
        "test that the selected indices are correct"
        self.assertEquals(self.ctrl.SelectedIndices(), (-1,))
        self.ctrl.Select(2)
        self.assertEquals(self.ctrl.SelectedIndices(), (2, ))

        self.assertTrue(type(self.ctrl.SelectedIndices()) == tuple)

    def testSelect(self):
        "Test selecting an item"
        self.ctrl.Select(1)
        self.assertEquals(self.ctrl.SelectedIndices(), (1, ))

        # get the text of the 2nd item (3rd item in list
        # because of empty WindowText)
        item_to_select = self.ctrl.Texts()[2]

        self.ctrl.Select(item_to_select)
        self.assertEquals(self.ctrl.SelectedIndices(), (1, ))

    def testGetSetItemFocus(self):
        "Test setting and getting the focus of a particular item"
        self.ctrl.SetItemFocus(0)
        self.assertEquals(self.ctrl.GetItemFocus(), 0)

        self.ctrl.SetItemFocus(2)
        self.assertEquals(self.ctrl.GetItemFocus(), 2)


class EditTestCases(unittest.TestCase):

    """Unit tests for the EditWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()

        import os.path
        path = os.path.split(__file__)[0]

        test_file = os.path.join(path, "test.txt")

        with codecs.open(test_file, mode="rb", encoding='utf-8') as f:
            self.test_data = f.read()
        # remove the BOM if it exists
        self.test_data = self.test_data.replace(repr("\xef\xbb\xbf"), "")
        #self.test_data = self.test_data.encode('utf-8', 'ignore') # XXX: decode raises UnicodeEncodeError even if 'ignore' is used!
        print('self.test_data:')
        print(self.test_data.encode('utf-8', 'ignore'))

        app.start("Notepad.exe " + test_file, timeout=20)

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

        if self.app.UntitledNotepad["Do&n't Save"].Exists():
            self.app.UntitledNotepad["Do&n't Save"].Click()
        self.app.kill_()

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
        self.ctrl.TypeKeys("%{HOME}" + added_text, with_spaces = True)
        expected_text = added_text + self.test_data

        self.assertEquals(self.ctrl.TextBlock(), expected_text)

    def testSelect(self):
        "Test selecting some text of the edit control"
        self.ctrl.Select(10, 50)

        self.assertEquals((10, 50), self.ctrl.SelectionIndices())

    def testLineCount(self):
        "Test getting the line count of the edit control"
        self.dlg.Maximize()
        for i in range(0, self.ctrl.LineCount()):
            self.assertEquals(
                self.ctrl.LineLength(i),
                len(self.test_data.split("\r\n")[i]))

    def testGetLine(self):
        "Test getting each line of the edit control"

        #for i in range(0, self.ctrl.LineCount()):
        #    print `self.ctrl.GetLine(i)`

        self.dlg.Maximize()
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

        txt = b"\xc7a-va? Et".decode('utf-8', 'ignore')
        self.test_data.index(txt)

        self.ctrl.Select(txt)
        start = self.test_data.index(txt)
        end = start + len(txt)
        self.assertEquals((start, end), self.ctrl.SelectionIndices())


class UnicodeEditTestCases(unittest.TestCase):

    """Unit tests for the EditWrapper class using Unicode strings"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application().Start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select("CAnimateCtrl")

        self.ctrl = self.dlg.AnimationFileEdit.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

    def testSetEditTextWithUnicode(self):
        "Test setting Unicode text by the SetEditText method of the edit control"
        self.ctrl.Select()
        self.ctrl.SetEditText(579)
        self.assertEquals("\n".join(self.ctrl.Texts()[1:]), "579")

        self.ctrl.SetEditText(333, pos_start=1, pos_end=2)
        self.assertEquals("\n".join(self.ctrl.Texts()[1:]), "53339")

        #self.ctrl.Select()
        #self.ctrl.SetEditText(u'\u0421\u043f\u0430\u0441\u0438\u0431\u043e!') # u'Spasibo!' in Russian symbols
        #self.assertEquals(self.ctrl.TextBlock(), u'\u0421\u043f\u0430\u0441\u0438\u0431\u043e!')

        #self.ctrl.Select(start=b'\xd1\xef\xe0\xf1') # u'Spas'
        #self.assertEquals(self.ctrl.SelectionIndices(), (0, 4))
        #self.ctrl.SetEditText(u'', pos_start=u'\u0421\u043f\u0430\u0441')
        ##self.ctrl.SetEditText(u'\u0438\u0431\u043e!')
        #self.assertEquals(self.ctrl.TextBlock(), u'\u0438\u0431\u043e!') # u'ibo!'

        #self.ctrl.Select()
        #self.ctrl.SetEditText(u'', pos_start=3)
        #self.assertEquals(self.ctrl.TextBlock(), u'\u0438\u0431\u043e') # u'ibo'

        #self.ctrl.Select()
        #self.ctrl.SetEditText(u'\u043d\u0435\u0447\u0442', pos_end=2) # u'necht'
        #self.assertEquals(self.ctrl.TextBlock(), u'\u043d\u0435\u0447\u0442\u043e') # u'nechto'


class DialogTestCases(unittest.TestCase):

    """Unit tests for the DialogWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        if is_x64_Python() or not is_x64_OS():
            self.app.start(r"C:\Windows\System32\calc.exe")
        else:
            self.app.start(r"C:\Windows\SysWOW64\calc.exe")
        self.calc = self.app.CalcFrame

        # write out the XML so that we can read it in later
        self.app.Calculator.WriteToXML("ref_controls.xml")

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()
        #self.calc.TypeKeys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the dialog box"
        props = self.calc.GetProperties()

        self.assertEquals(
            "CalcFrame", props['FriendlyClassName'])

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
        from pywinauto import controlproperties
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

                if "Image" in expected_value.__class__.__name__:
                    expected_value = expected_value.tobytes()
                    ctrl_value = ctrl_value.tobytes()

                if isinstance(ctrl_value, (list, tuple)):
                    ctrl_value = list(ctrl_value)
                    expected_value = list(expected_value)

                self.assertEquals(ctrl_value, expected_value)

        import os
        os.unlink("test_output.xml")

    def testClientAreaRect(self):
        """Validate that the client area rect is the right size
        (comparing against the full rectangle)
        Notice that we run an approximate comparison as the actual
        area size depends on Windows OS and a current desktop theme"""
        clientarea = self.calc.ClientAreaRect()
        rectangle = self.calc.Rectangle()
        self.failIf((clientarea.left - rectangle.left) > 10)
        self.failIf((clientarea.top - rectangle.top) > 60)
        self.failIf((rectangle.right - clientarea.right) > 10)
        self.failIf((rectangle.bottom - clientarea.bottom) > 10)

    def testHideFromTaskbar(self):
        "Test that a dialog can be hidden from the Windows taskbar"
        self.assertEquals(self.calc.IsInTaskbar(), True)
        self.calc.HideFromTaskbar()
        self.assertEquals(self.calc.IsInTaskbar(), False)
        self.calc.ShowInTaskbar()
        self.assertEquals(self.calc.IsInTaskbar(), True)


class PopupMenuTestCases(unittest.TestCase):

    """Unit tests for the PopupMenuWrapper class"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        self.app = Application()

        self.app.start("notepad.exe")
        self.app.Notepad.Edit.RightClick()
        self.popup = self.app.PopupMenu.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.popup.TypeKeys("{ESC}")
        self.app.kill_() #.Notepad.TypeKeys("%{F4}")

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


class StaticTestCases(unittest.TestCase):

    """Unit tests for the StaticWrapper class"""

    def setUp(self):

        """Start the sample application. Open a tab with ownerdraw button."""

        # start the application
        self.app = Application().Start(os.path.join(mfc_samples_folder, u"RebarTest.exe"))
        # open the Help dailog
        self.app.active_().TypeKeys('%h{ENTER}')

    def tearDown(self):

        """Close the application after tests"""

        self.app.kill_()

    def test_NeedsImageProp(self):

        """test a regular static has no the image property"""

        active_window = self.app.active_()
        self.assertEquals(active_window.Static2._NeedsImageProp, False)
        self.assertEquals('Image' in active_window.Static2.GetProperties(), False)
        #self.assertNotIn('Image', active_window.Static2.GetProperties())
        # assertIn and assertNotIn are not supported in Python 2.6

    def test_NeedsImageProp_ownerdraw(self):

        """test whether an image needs to be saved with the properties"""

        active_window = self.app.active_()
        self.assertEquals(active_window.Static._NeedsImageProp, True)
        self.assertEquals('Image' in active_window.Static.GetProperties(), True)
        #self.assertIn('Image', active_window.Static.GetProperties())
        # assertIn and assertNotIn are not supported in Python 2.6


if __name__ == "__main__":
    #_unittests()
    unittest.main()
