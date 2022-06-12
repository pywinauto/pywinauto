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

"""Tests various standard windows controls"""
from __future__ import unicode_literals

# pylint:  disable-msg=W0212,F0401,R0904

import os, sys
import codecs
import unittest
#sys.path.append(".")
sys.path.append("C:\\Users\\user\\pywinauto")
from pywinauto import xml_helpers
from pywinauto.windows import win32defines
from pywinauto.sysinfo import is_x64_Python
from pywinauto.windows.application import Application

# following imports are not required for the tests
# but are useful for debugging
#import pprint

from pywinauto.timings import Timings

def _set_timings_fast():
    """Set Timings.fast() and some slower settings for reliability"""
    Timings.fast()
    Timings.window_find_timeout = 3
    Timings.closeclick_dialog_close_wait = 2.

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\..\apps\MFC_samples")
print('FOLDER: ' + mfc_samples_folder)
MFC_tutorial_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\..\apps\MFC_tutorial")

if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
    MFC_tutorial_folder = os.path.join(MFC_tutorial_folder, 'x64')


class ButtonTestCases(unittest.TestCase):

    """Unit tests for the ButtonWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()
        self.app = self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.app.Common_Controls_Sample.TabControl.select("CDateTimeCtrl")

        self.ctrl = self.app.Common_Controls_Sample

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def testGetProperties(self):
        """Test getting the properties for the button control"""
        props = self.ctrl.Button2.get_properties()

        self.assertEqual(
            "Button", props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.Button2.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(
                getattr(self.ctrl.Button2, prop_name)(), props[prop_name])

    def test_NeedsImageProp(self):
        """Test whether an image needs to be saved with the properties"""
        self.assertEqual(self.ctrl.OKButton._needs_image_prop, True)
        self.assertEqual('image' in self.ctrl.OKButton.get_properties(), True)

    def testFriendlyClass(self):
        """Test the friendly_class_name method"""
        self.assertEqual(self.ctrl.Button2.friendly_class_name(), "Button")
        self.assertEqual(self.ctrl.RadioButton2.friendly_class_name(), "RadioButton")

    def testCheckUncheck(self):
        """Test unchecking a control"""
        self.ctrl.RadioButton2.check()
        self.assertEqual(self.ctrl.RadioButton2.get_check_state(), 1)
        self.ctrl.RadioButton2.uncheck()
        self.assertEqual(self.ctrl.RadioButton2.get_check_state(), 0)

    def testGetCheckState_unchecked(self):
        """Test whether the control is unchecked"""
        self.assertEqual(self.ctrl.RadioButton.get_check_state(), 0)

    def testGetCheckState_checked(self):
        """Test whether the control is checked"""
        self.ctrl.RadioButton2.check()
        self.assertEqual(self.ctrl.RadioButton2.get_check_state(), 1)

#    def testGetCheckState_indeterminate(self):
#        "indeterminate"
#        self.calc.Inv.set_check_indeterminate()
#        self.assertEqual(self.calc.Inv.get_check_state(), 0)

    def testClick(self):
        """Test clicking on buttons"""
        self.ctrl.RadioButton2.click()  # DTS_SHORTDATEFORMAT
        self.ctrl.RadioButton.click()  # DTS_TIMEFORMAT
        self.ctrl.RadioButton3.click()  # DTS_LONGDATEFORMAT
        self.assertEqual(self.ctrl.RadioButton3.get_check_state(), 1)

    def testIsSelected(self):
        """Test whether the control is selected or not"""
        # Todo - I need to find an application where a button can be
        # selected - I don't see one in Calc at least :)
        self.assertEqual(self.ctrl.RadioButton.get_check_state(), 0)

        self.ctrl.RadioButton.click()

        self.assertEqual(self.ctrl.RadioButton.get_check_state(), 1)


class CheckBoxTests(unittest.TestCase):

    """Unit tests for the CheckBox specific methods of the ButtonWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.tree = self.dlg.TreeView.find()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill()

    def testCheckUncheckByClick(self):
        "test for CheckByClick and UncheckByClick"
        self.dlg.TVS_HASLINES.check_by_click()
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_CHECKED)
        self.assertEqual(self.tree.has_style(win32defines.TVS_HASLINES), True)

        self.dlg.TVS_HASLINES.check_by_click() # make sure it doesn't uncheck the box unexpectedly
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_CHECKED)

        self.dlg.TVS_HASLINES.uncheck_by_click()
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_UNCHECKED)
        self.assertEqual(self.tree.has_style(win32defines.TVS_HASLINES), False)

        self.dlg.TVS_HASLINES.uncheck_by_click() # make sure it doesn't check the box unexpectedly
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_UNCHECKED)

    def testCheckUncheckByClickInput(self):
        "test for CheckByClickInput and UncheckByClickInput"
        self.dlg.TVS_HASLINES.check_by_click_input()
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_CHECKED)
        self.assertEqual(self.tree.has_style(win32defines.TVS_HASLINES), True)

        self.dlg.TVS_HASLINES.check_by_click_input() # make sure it doesn't uncheck the box unexpectedly
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_CHECKED)

        self.dlg.TVS_HASLINES.uncheck_by_click_input()
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_UNCHECKED)
        self.assertEqual(self.tree.has_style(win32defines.TVS_HASLINES), False)

        self.dlg.TVS_HASLINES.uncheck_by_click_input() # make sure it doesn't check the box unexpectedly
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_UNCHECKED)

    def testSetCheckIndeterminate(self):
        "test for SetCheckIndeterminate"
        self.dlg.TVS_HASLINES.set_check_indeterminate()
        self.assertEqual(self.dlg.TVS_HASLINES.get_check_state(), win32defines.BST_CHECKED)
        # TODO: find an application with the check box that supports indeterminate state (gray-checked)


class ButtonOwnerdrawTestCases(unittest.TestCase):

    """Unit tests for the ButtonWrapper(ownerdraw button)"""

    def setUp(self):
        """Start the sample application. Open a tab with ownerdraw button."""
        _set_timings_fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))
        # open the needed tab
        self.app.active().TabControl.select(1)

    def tearDown(self):

        """Close the application after tests"""

        self.app.kill()

    def test_NeedsImageProp(self):

        """test whether an image needs to be saved with the properties"""

        active_window = self.app.active()
        self.assertEqual(active_window.Button2._needs_image_prop, True)
        self.assertEqual('image' in active_window.Button2.get_properties(), True)
        #self.assertIn('image', active_window.Button2.get_properties())
        # assertIn and assertNotIn are not supported in Python 2.6


class ComboBoxTestCases(unittest.TestCase):

    """Unit tests for the ComboBoxWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"))
        self.app.Common_Controls_Sample.TabControl.select("CSpinButtonCtrl")

        self.ctrl = self.app.Common_Controls_Sample.AlignmentComboBox.find()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill()

    def testGetProperties(self):
        "Test getting the properties for the combobox control"
        props = self.ctrl.get_properties()

        self.assertEqual(
            "ComboBox", props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(
                getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        "Test that ItemCount returns the correct number of items"
        self.assertEqual(self.ctrl.item_count(), 3)

    def testDroppedRect(self):
        "Test that the dropped rect is correct"
        rect = self.ctrl.dropped_rect()
        #import pdb;pdb.set_trace()
        self.assertEqual(rect.left, 0)
        self.assertEqual(rect.top, 0)
        self.assertEqual(rect.right, self.ctrl.client_rect().right)
        self.assertEqual(rect.bottom, self.ctrl.rectangle().height() + 48)

    def testSelectedIndex(self):
        "That the control returns the correct index for the selected item"
        self.ctrl.select(1)
        self.assertEqual(self.ctrl.selected_index(), 1)
        #self.assertEqual(self.ctrl.texts()[3], self.app.Font.Edit2.texts()[1])

    def testSelect_negative(self):
        "Test that the Select method correctly handles negative indices"
        self.ctrl.select(-1)
        self.assertEqual(self.ctrl.selected_index(), 2)

    def testSelect_toohigh(self):
        "Test that the Select correctly raises if the item is too high"
        self.assertRaises(IndexError, self.ctrl.select, 211)

    def testSelect_string(self):
        "Test that we can select based on a string"
        self.ctrl.select(0)
        self.assertEqual(self.ctrl.selected_index(), 0)
        self.ctrl.select("Left (UDS_ALIGNLEFT)")
        self.assertEqual(self.ctrl.selected_index(), 1)
        self.assertEqual(self.ctrl.selected_text(), "Left (UDS_ALIGNLEFT)")

        # now do it with a typo
        self.assertRaises(ValueError, self.ctrl.select, "Right (UDS_ALIGNRIGT)")

    def testSelect_simpleCombo(self):
        "Test selection for a simple combo"
        self.app.Common_Controls_Sample.OrientationComboBox.select(0)
        self.assertEqual(self.app.Common_Controls_Sample.OrientationComboBox.selected_index(), 0)
        self.app.Common_Controls_Sample.OrientationComboBox.select(1)
        self.assertEqual(self.app.Common_Controls_Sample.OrientationComboBox.selected_index(), 1)

    def testItemData(self):
        "Test that it doesn't raise"
        self.ctrl.item_data(0)
        self.ctrl.item_data(1)
        self.ctrl.item_data("Right (UDS_ALIGNRIGHT)")
        self.ctrl.item_data(self.ctrl.item_count() - 1)


class ListBoxTestCases(unittest.TestCase):

    """Unit tests for the ListBoxWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()

        app_path = os.path.join(MFC_tutorial_folder, "MFC_Tutorial9.exe")
        self.app.start(app_path)

        self.dlg = self.app.MFC_Tutorial9
        self.dlg.wait('ready', timeout=20)
        self.dlg.TypeYourTextEdit.type_keys('qqq')
        self.dlg.Add.click()

        self.dlg.TypeYourTextEdit.select()
        self.dlg.TypeYourTextEdit.type_keys('123')
        self.dlg.Add.click()

        self.dlg.TypeYourTextEdit.select()
        self.dlg.TypeYourTextEdit.type_keys('third item', with_spaces=True)
        self.dlg.Add.click()

        self.ctrl = self.dlg.ListBox.find()

    def tearDown(self):
        "Close the application after tests"

        #self.dlg.Cancel.click()

        # close the application
        self.app.kill()

    def testGetProperties(self):
        "Test getting the properties for the list box control"
        props = self.ctrl.get_properties()

        self.assertEqual(
            "ListBox", props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(
                getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        "test that the count of items is correct"
        self.assertEqual(self.ctrl.item_count(), 3)

    def testItemData(self):
        "For the moment - just test that it does not raise"
        self.ctrl.item_data(1)
        self.ctrl.item_data(self.ctrl.item_count() - 1)

    def testSelectedIndices(self):
        "test that the selected indices are correct"
        self.assertEqual(self.ctrl.selected_indices(), (-1,))
        self.ctrl.select(2)
        self.assertEqual(self.ctrl.selected_indices(), (2, ))

        self.assertTrue(isinstance(self.ctrl.selected_indices(), tuple))

    def testSelect(self):
        "Test selecting an item"
        self.ctrl.select(1)
        self.assertEqual(self.ctrl.selected_indices(), (1, ))

        # get the text of the 2nd item (3rd item in list
        # because of empty window_text)
        item_to_select = self.ctrl.texts()[2]

        self.ctrl.select(item_to_select)
        self.assertEqual(self.ctrl.selected_indices(), (1, ))

    def testGetSetItemFocus(self):
        "Test setting and getting the focus of a particular item"
        self.ctrl.set_item_focus(0)
        self.assertEqual(self.ctrl.get_item_focus(), 0)

        self.ctrl.set_item_focus(2)
        self.assertEqual(self.ctrl.get_item_focus(), 2)


class EditTestCases(unittest.TestCase):

    """Unit tests for the EditWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.defaults()

        app = Application()

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
        self.ctrl = self.dlg.Edit.find()

        self.old_pos = self.dlg.rectangle

        self.dlg.move_window(10, 10, 400, 400)
        #self.dlg.menu_select("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        """Close the application after tests"""
        # set it back to it's old position so not to annoy users :-)
        self.old_pos = self.dlg.rectangle

        # close the application
        self.dlg.menu_select("File->Exit")

        try:
            if self.app.UntitledNotepad["Do&n't Save"].exists():
                self.app.UntitledNotepad["Do&n't Save"].click()
                self.app.UntitledNotepad.wait_not('visible')
        except Exception:
            pass
        finally:
            self.app.kill()

    def test_dump_tree(self):
        """Test that dump_tree() doesn't crash with the non-English characters"""
        self.dlg.dump_tree()

    def test_set_text(self):
        """Test setting the text of the edit control"""
        self.ctrl.set_text("Here is\r\nsome text")
        self.assertEqual(
            "\n".join(self.ctrl.texts()[1:]), "Here is\nsome text")

    def test_type_keys(self):
        """Test typing some text into the edit control"""
        # typekeys types at the current caret position
        # (start when opening a new file)
        added_text = "Here is some more Text"
        self.ctrl.type_keys("%{HOME}" + added_text, with_spaces = True)
        expected_text = added_text + self.test_data

        self.assertEqual(self.ctrl.text_block(), expected_text)

    def test_type_keys_up_down_group_of_keys(self):
        """Test typing some text into the edit control"""
        self.ctrl.type_keys("{VK_SHIFT down}12345{VK_SHIFT up}12345 {VK_SPACE} {h down}{e down}{h up} {e up}llo")
        expected_text = "!@#$%12345 hello" + self.test_data

        self.assertEqual(self.ctrl.text_block(), expected_text)

    def testSelect(self):
        "Test selecting some text of the edit control"
        self.ctrl.select(10, 50)

        self.assertEqual((10, 50), self.ctrl.selection_indices())

    def testLineCount(self):
        "Test getting the line count of the edit control"
        self.dlg.maximize()
        for i in range(0, self.ctrl.line_count()):
            self.assertEqual(
                self.ctrl.line_length(i),
                len(self.test_data.split("\r\n")[i]))

    def testGetLine(self):
        "Test getting each line of the edit control"

        #for i in range(0, self.ctrl.line_count()):
        #    print `self.ctrl.get_line(i)`

        self.dlg.maximize()
        for i, line in enumerate(self.test_data.split("\r\n")):
            #print `line`
            #print `self.ctrl.get_line(i)`
            self.assertEqual(self.ctrl.get_line(i), line)

    def testTextBlock(self):
        "Test getting the text block of the edit control"
        self.assertEqual(self.ctrl.text_block(), self.test_data)

    def testSelection(self):
        "Test selecting text in the edit control in various ways"

        self.ctrl.select(0, 0)
        self.assertEqual((0, 0), self.ctrl.selection_indices())

        self.ctrl.select()
        self.assertEqual(
            (0, len(self.test_data)), self.ctrl.selection_indices())

        self.ctrl.select(10, 25)
        self.assertEqual((10, 25), self.ctrl.selection_indices())

        self.ctrl.select(18, 7)
        self.assertEqual((7, 18), self.ctrl.selection_indices())

        txt = b"\xc7a-va? Et".decode('utf-8', 'ignore')
        self.test_data.index(txt)

        self.ctrl.select(txt)
        start = self.test_data.index(txt)
        end = start + len(txt)
        self.assertEqual((start, end), self.ctrl.selection_indices())


class UnicodeEditTestCases(unittest.TestCase):

    """Unit tests for the EditWrapper class using Unicode strings"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.select("CAnimateCtrl")

        self.ctrl = self.dlg.AnimationFileEdit.find()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill()

    def testSetEditTextWithUnicode(self):
        "Test setting Unicode text by the SetEditText method of the edit control"
        self.ctrl.select()
        self.ctrl.set_edit_text(579)
        self.assertEqual("\n".join(self.ctrl.texts()[1:]), "579")

        self.ctrl.set_edit_text(333, pos_start=1, pos_end=2)
        self.assertEqual("\n".join(self.ctrl.texts()[1:]), "53339")

        #self.ctrl.select()
        #self.ctrl.set_edit_text(u'\u0421\u043f\u0430\u0441\u0438\u0431\u043e!') # u'Spasibo!' in Russian symbols
        #self.assertEqual(self.ctrl.text_block(), u'\u0421\u043f\u0430\u0441\u0438\u0431\u043e!')

        #self.ctrl.select(start=b'\xd1\xef\xe0\xf1') # u'Spas'
        #self.assertEqual(self.ctrl.selection_indices(), (0, 4))
        #self.ctrl.set_edit_text(u'', pos_start=u'\u0421\u043f\u0430\u0441')
        ##self.ctrl.set_edit_text(u'\u0438\u0431\u043e!')
        #self.assertEqual(self.ctrl.text_block(), u'\u0438\u0431\u043e!') # u'ibo!'

        #self.ctrl.select()
        #self.ctrl.set_edit_text(u'', pos_start=3)
        #self.assertEqual(self.ctrl.text_block(), u'\u0438\u0431\u043e') # u'ibo'

        #self.ctrl.select()
        #self.ctrl.set_edit_text(u'\u043d\u0435\u0447\u0442', pos_end=2) # u'necht'
        #self.assertEqual(self.ctrl.text_block(), u'\u043d\u0435\u0447\u0442\u043e') # u'nechto'


class DialogTestCases(unittest.TestCase):

    """Unit tests for the DialogWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()
        self.app = self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.cmn_ctrl = self.app.Common_Controls_Sample

        # write out the XML so that we can read it in later
        self.app.Common_Controls_Sample.write_to_xml("ref_controls.xml")

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def testGetProperties(self):
        """Test getting the properties for the dialog box"""
        props = self.cmn_ctrl.get_properties()

        self.assertEqual(
            "Dialog", props['friendly_class_name'])

        self.assertEqual(self.cmn_ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(
                getattr(self.cmn_ctrl, prop_name)(), props[prop_name])

    def testRunTests(self):
        """Test running the UI tests on the dialog"""
        bugs = self.cmn_ctrl.run_tests()
        from pywinauto.controls.hwndwrapper import HwndWrapper
        self.assertEqual(True, isinstance(bugs[0][0][0], HwndWrapper))

    def testRunTestsWithReference(self):
        """Add a ref control, get the bugs and validate that the hande"""
        from pywinauto import controlproperties
        ref_controls = [controlproperties.ControlProps(ctrl) for
                ctrl in xml_helpers.ReadPropertiesFromFile("ref_controls.xml")]

        bugs = self.cmn_ctrl.run_tests(ref_controls = ref_controls)
        from pywinauto import tests
        tests.print_bugs(bugs)
        from pywinauto.controls.hwndwrapper import HwndWrapper
        self.assertEqual(True, isinstance(bugs[0][0][0], HwndWrapper))

    def testWriteToXML(self):
        """Write the output and validate that it is the same as the test output"""
        self.cmn_ctrl.write_to_xml("test_output.xml")

        all_props = [self.cmn_ctrl.get_properties()]
        all_props.extend([c.get_properties() for c in self.cmn_ctrl.children()])

        props = xml_helpers.ReadPropertiesFromFile("test_output.xml")
        for i, ctrl in enumerate(props):

            for key, ctrl_value in ctrl.items():
                expected_value = all_props[i][key]

                if "Image" in expected_value.__class__.__name__:
                    expected_value = expected_value.tobytes()
                    ctrl_value = ctrl_value.tobytes()

                if isinstance(ctrl_value, (list, tuple)):
                    ctrl_value = list(ctrl_value)
                    expected_value = list(expected_value)

                if ctrl_value == 'None':
                    ctrl_value = None

                self.assertEqual(ctrl_value, expected_value)

        os.unlink("test_output.xml")

    def testClientAreaRect(self):
        """Validate that the client area rect is the right size
        (comparing against the full rectangle)
        Notice that we run an approximate comparison as the actual
        area size depends on Windows OS and a current desktop theme"""
        clientarea = self.cmn_ctrl.client_area_rect()
        rectangle = self.cmn_ctrl.rectangle()
        self.assertFalse((clientarea.left - rectangle.left) > 10)
        self.assertFalse((clientarea.top - rectangle.top) > 60)
        self.assertFalse((rectangle.right - clientarea.right) > 10)
        self.assertFalse((rectangle.bottom - clientarea.bottom) > 10)

    def testHideFromTaskbar(self):
        """Test that a dialog can be hidden from the Windows taskbar"""
        self.assertEqual(self.cmn_ctrl.is_in_taskbar(), True)
        self.cmn_ctrl.hide_from_taskbar()
        self.assertEqual(self.cmn_ctrl.is_in_taskbar(), False)
        self.cmn_ctrl.show_in_taskbar()
        self.assertEqual(self.cmn_ctrl.is_in_taskbar(), True)


class PopupMenuTestCases(unittest.TestCase):

    """Unit tests for the PopupMenuWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings_fast()

        self.app = Application()

        self.app.start("notepad.exe")
        self.app.Notepad.Edit.right_click()
        self.popup = self.app.PopupMenu.find()

    def tearDown(self):
        "Close the application after tests"
        self.popup.type_keys("{ESC}")
        self.app.kill() #.Notepad.type_keys("%{F4}")

    def testGetProperties(self):
        "Test getting the properties for the PopupMenu"
        props = self.popup.get_properties()

        self.assertEqual(
            "PopupMenu", props['friendly_class_name'])

        self.assertEqual(self.popup.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(
                getattr(self.popup, prop_name)(), props[prop_name])

    def testIsDialog(self):
        "Ensure that is_dialog works correctly"
        self.assertEqual(True, self.popup.is_dialog())

    def test_menu_handle(self):
        "Ensure that the menu handle is returned"
        handle = self.popup._menu_handle()
        self.assertNotEqual(0, handle)


class StaticTestCases(unittest.TestCase):

    """Unit tests for the StaticWrapper class"""

    def setUp(self):
        """Start the sample application. Open a tab with ownerdraw button."""
        Timings.defaults()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"RebarTest.exe"))
        # open the Help dailog
        self.app.active().type_keys('%h{ENTER}')

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_NeedsImageProp(self):
        """test a regular static has no the image property"""
        active_window = self.app.active()
        self.assertEqual(active_window.Static2._needs_image_prop, False)
        self.assertEqual('image' in active_window.Static2.get_properties(), False)
        #self.assertNotIn('image', active_window.Static2.get_properties())
        # assertIn and assertNotIn are not supported in Python 2.6

    def test_NeedsImageProp_ownerdraw(self):
        """test whether an image needs to be saved with the properties"""
        active_window = self.app.active()
        self.assertEqual(active_window.Static._needs_image_prop, True)
        self.assertEqual('image' in active_window.Static.get_properties(), True)
        #self.assertIn('image', active_window.Static.get_properties())
        # assertIn and assertNotIn are not supported in Python 2.6


if __name__ == "__main__":
    unittest.main()
