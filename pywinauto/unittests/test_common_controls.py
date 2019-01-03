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

"""Tests for classes in controls\common_controls.py"""
from __future__ import print_function

import sys
#import ctypes
import unittest
import time
from datetime import datetime
#import pdb
import os
import win32api
import six

sys.path.append(".")
from pywinauto.application import Application  # noqa: E402
from pywinauto.win32structures import RECT  # noqa: E402
from pywinauto import win32defines  # noqa: E402
from pywinauto import findbestmatch  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.remote_memory_block import RemoteMemoryBlock  # noqa: E402
from pywinauto.actionlogger import ActionLogger  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from pywinauto.timings import wait_until  # noqa: E402
from pywinauto import mouse  # noqa: E402


controlspy_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\controlspy0998")
controlspy_folder_32 = controlspy_folder
mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_samples")
mfc_samples_folder_32 = mfc_samples_folder
winforms_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WinForms_samples")
winforms_folder_32 = winforms_folder
if is_x64_Python():
    controlspy_folder = os.path.join(controlspy_folder, 'x64')
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
    winforms_folder = os.path.join(winforms_folder, 'x64')


class RemoteMemoryBlockTestCases(unittest.TestCase):
    def test__init__fail(self):
        self.assertRaises(AttributeError, RemoteMemoryBlock, 0)


class ListViewTestCases32(unittest.TestCase):
    """Unit tests for the ListViewWrapper class"""

    path = os.path.join(mfc_samples_folder_32, u"RowList.exe")

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        app = Application()
        app.start(self.path)

        self.texts = [
            (u"Yellow",  u"255", u"255", u"0",   u"40",  u"240", u"120", u"Neutral"),
            (u"Red",     u"255", u"0",   u"0",   u"0",   u"240", u"120", u"Warm"),
            (u"Green",   u"0",   u"255", u"0",   u"80",  u"240", u"120", u"Cool"),
            (u"Magenta", u"255", u"0",   u"255", u"200", u"240", u"120", u"Warm"),
            (u"Cyan",    u"0",   u"255", u"255", u"120", u"240", u"120", u"Cool"),
            (u"Blue",    u"0",   u"0",   u"255", u"160", u"240", u"120", u"Cool"),
            (u"Gray",    u"192", u"192", u"192", u"160", u"0",   u"181", u"Neutral")
        ]

        self.app = app
        self.dlg = app.RowListSampleApplication
        self.ctrl = app.RowListSampleApplication.ListView.wrapper_object()
        self.dlg.Toolbar.button(0).click()  # switch to icon view
        self.dlg.Toolbar.button(6).click()  # switch off states

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the ListView friendly class is set correctly"""
        self.assertEqual(self.ctrl.friendly_class_name(), u"ListView")

    def testColumnCount(self):
        """Test the ListView ColumnCount method"""
        self.assertEqual(self.ctrl.column_count(), 8)

    def testItemCount(self):
        """Test the ListView ItemCount method"""
        self.assertEqual(self.ctrl.item_count(), 7)

    def testItemText(self):
        """Test the ListView item.Text property"""
        item = self.ctrl.get_item(1)

        self.assertEqual(item.text(), u"Red")

    def testItems(self):
        """Test the ListView Items method"""
        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        items = self.ctrl.items()
        for i, item in enumerate(items):
            self.assertEqual(item.text(), flat_texts[i])
        self.assertEqual(len(items), len(flat_texts))

    def testTexts(self):
        """Test the ListView texts method"""
        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        self.assertEqual(flat_texts, self.ctrl.texts()[1:])

    def testGetItem(self):
        """Test the ListView get_item method"""
        for row in range(self.ctrl.item_count()):
            for col in range(self.ctrl.column_count()):
                self.assertEqual(
                    self.ctrl.get_item(row, col).text(), self.texts[row][col])

    def testGetItemText(self):
        """Test the ListView get_item method - with text this time"""
        for text in [row[0] for row in self.texts]:
            self.assertEqual(
                self.ctrl.get_item(text).text(), text)

        self.assertRaises(ValueError, self.ctrl.get_item, "Item not in this list")

    def testColumn(self):
        """Test the ListView columns method"""
        cols = self.ctrl.columns()
        self.assertEqual(len(cols), self.ctrl.column_count())

        # TODO: add more checking of column values
        #for col in cols:
        #    print(col)

    def testGetSelectionCount(self):
        """Test the ListView get_selected_count method"""
        self.assertEqual(self.ctrl.get_selected_count(), 0)

        self.ctrl.get_item(1).select()
        self.ctrl.get_item(6).select()

        self.assertEqual(self.ctrl.get_selected_count(), 2)


#    def testGetSelectionCount(self):
#        "Test the ListView get_selected_count method"
#
#        self.assertEqual(self.ctrl.get_selected_count(), 0)
#
#        self.ctrl.select(1)
#        self.ctrl.select(7)
#
#        self.assertEqual(self.ctrl.get_selected_count(), 2)

    def testIsSelected(self):
        """Test ListView IsSelected for some items"""
        # ensure that the item is not selected
        self.assertEqual(self.ctrl.get_item(1).is_selected(), False)

        # select an item
        self.ctrl.get_item(1).select()

        # now ensure that the item is selected
        self.assertEqual(self.ctrl.get_item(1).is_selected(), True)

    def _testFocused(self):
        """Test checking the focus of some ListView items"""
        print("Select something quick!!")
        time.sleep(3)
        #self.ctrl.select(1)

        print(self.ctrl.is_focused(0))
        print(self.ctrl.is_focused(1))
        print(self.ctrl.is_focused(2))
        print(self.ctrl.is_focused(3))
        print(self.ctrl.is_focused(4))
        print(self.ctrl.is_focused(5))
        #for col in cols:
        #    print(col)

    def testSelect(self):
        """Test ListView Selecting some items"""
        self.ctrl.get_item(1).select()
        self.ctrl.get_item(3).select()
        self.ctrl.get_item(4).select()

        self.assertRaises(IndexError, self.ctrl.get_item(23).select)

        self.assertEqual(self.ctrl.get_selected_count(), 3)

    def testSelectText(self):
        """Test ListView Selecting some items"""
        self.ctrl.get_item(u"Green").select()
        self.ctrl.get_item(u"Yellow").select()
        self.ctrl.get_item(u"Gray").select()

        self.assertRaises(ValueError, self.ctrl.get_item, u"Item not in list")

        self.assertEqual(self.ctrl.get_selected_count(), 3)

    def testDeselect(self):
        """Test ListView Selecting some items"""
        self.ctrl.get_item(1).select()
        self.ctrl.get_item(4).select()

        self.ctrl.get_item(3).deselect()
        self.ctrl.get_item(4).deselect()

        self.assertRaises(IndexError, self.ctrl.get_item(23).deselect)

        self.assertEqual(self.ctrl.get_selected_count(), 1)

    def testGetProperties(self):
        """Test getting the properties for the listview control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            "ListView", props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props.keys():
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

        self.assertEqual(props['column_count'], 8)
        self.assertEqual(props['item_count'], 7)

    def testGetColumnTexts(self):
        """Test columns titles text"""
        self.assertEqual(self.ctrl.get_column(0)['text'], u"Color")
        self.assertEqual(self.ctrl.get_column(1)['text'], u"Red")
        self.assertEqual(self.ctrl.get_column(2)['text'], u"Green")
        self.assertEqual(self.ctrl.get_column(3)['text'], u"Blue")

    def testItemRectangles(self):
        """Test getting item rectangles"""
        yellow_rect = self.ctrl.get_item_rect('Yellow')
        gold_rect = RECT(13, 0, 61, 53)
        self.assertEqual(yellow_rect.left, gold_rect.left)
        self.assertEqual(yellow_rect.top, gold_rect.top)
        self.assertEqual(yellow_rect.right, gold_rect.right)
        if yellow_rect.bottom < 53 or yellow_rect.bottom > 55:
            self.assertEqual(yellow_rect.bottom, gold_rect.bottom)

        self.ctrl.get_item('Green').click(where='text')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)

        self.ctrl.get_item('Magenta').click(where='icon')
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), True)
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), False)

        self.ctrl.get_item('Green').click(where='all')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), False)

    def testItemCheck(self):
        """Test checking/unchecking item"""
        if not self.dlg.Toolbar.button(6).is_checked():
            self.dlg.Toolbar.button(6).click()

        yellow = self.ctrl.get_item('Yellow')
        yellow.check()
        self.assertEqual(yellow.is_checked(), True)

        yellow.uncheck()
        self.assertEqual(yellow.is_checked(), False)

        # test legacy deprecated methods (TODO: remove later)
        self.ctrl.get_item('Yellow').check()
        self.assertEqual(self.ctrl.get_item('Yellow').is_checked(), True)

        self.ctrl.get_item('Yellow').uncheck()
        self.assertEqual(self.ctrl.get_item('Yellow').is_checked(), False)

    def testItemClick(self):
        """Test clicking item rectangles by click() method"""
        self.ctrl.get_item('Green').click(where='select')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)

        self.ctrl.get_item('Magenta').click(where='select')
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), True)
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), False)
        self.assertEqual(self.ctrl.get_item('Green').is_focused(), False)
        self.assertEqual(self.ctrl.get_item('Green').state() & win32defines.LVIS_FOCUSED, 0)

        self.ctrl.get_item('Green').click(where='select')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)
        self.assertEqual(self.ctrl.is_selected('Green'), True)  # TODO: deprecated method
        self.assertEqual(self.ctrl.get_item('Green').is_focused(), True)
        self.assertEqual(self.ctrl.is_focused('Green'), True)  # TODO: deprecated method
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), False)

        # Test click on checkboxes
        if not self.dlg.Toolbar.button(6).is_checked():  # switch on states
            self.dlg.Toolbar.button(6).click()

        for i in range(1, 6):
            self.dlg.Toolbar.button(i - 1).click()

            self.ctrl.get_item(i).click(where='check')  # check item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), True)
            self.assertEqual(self.ctrl.get_item(i - 1).is_checked(), False)

            self.ctrl.get_item(i).click(where='check')  # uncheck item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), False)

            self.ctrl.get_item(i).click(where='check')  # recheck item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), True)

        self.dlg.Toolbar.button(6).click()  # switch off states

        self.assertRaises(RuntimeError, self.ctrl.get_item(6).click, where="check")

    def testItemClickInput(self):
        """Test clicking item rectangles by click_input() method"""
        Timings.defaults()

        self.ctrl.get_item('Green').click_input(where='select')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)

        self.ctrl.get_item('Magenta').click_input(where='select')
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), True)
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), False)
        self.assertEqual(self.ctrl.get_item('Green').is_focused(), False)
        self.assertEqual(self.ctrl.get_item('Green').state() & win32defines.LVIS_FOCUSED, 0)

        self.ctrl.get_item('Green').click_input(where='select')
        self.assertEqual(self.ctrl.get_item('Green').is_selected(), True)
        self.assertEqual(self.ctrl.is_selected('Green'), True)  # TODO: deprecated method
        self.assertEqual(self.ctrl.get_item('Green').is_focused(), True)
        self.assertEqual(self.ctrl.is_focused('Green'), True)  # TODO: deprecated method
        self.assertEqual(self.ctrl.get_item('Magenta').is_selected(), False)

        # Test click on checkboxes
        if not self.dlg.Toolbar.button(6).is_checked():  # switch on states
            self.dlg.Toolbar.button(6).click()

        for i in range(1, 6):
            self.dlg.Toolbar.button(i - 1).click()

            self.ctrl.get_item(i).click_input(where='check')  # check item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), True)
            self.assertEqual(self.ctrl.get_item(i - 1).is_checked(), False)

            self.ctrl.get_item(i).click_input(where='check')  # uncheck item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), False)

            self.ctrl.get_item(i).click_input(where='check')  # recheck item
            time.sleep(0.5)
            self.assertEqual(self.ctrl.get_item(i).is_checked(), True)

        self.dlg.Toolbar.button(6).click()  # switch off states

        self.assertRaises(RuntimeError, self.ctrl.get_item(6).click_input, where="check")

    def testItemMethods(self):
        """Test short item methods like Text(), State() etc"""
        self.assertEqual(self.ctrl.get_item('Green').text(), 'Green')
        self.assertEqual(self.ctrl.get_item('Green').image(), 2)
        self.assertEqual(self.ctrl.get_item('Green').indent(), 0)

    def test_ensure_visible(self):
        self.dlg.move_window(width=300)

        # Gray is selected by click because ensure_visible() is called inside
        self.ctrl.get_item('Gray').click()
        self.assertEqual(self.ctrl.get_item('Gray').is_selected(), True)
        self.dlg.set_focus()  # just in case

        self.ctrl.get_item('Green').ensure_visible()
        self.ctrl.get_item('Red').click()
        self.assertEqual(self.ctrl.get_item('Gray').is_selected(), False)
        self.assertEqual(self.ctrl.get_item('Red').is_selected(), True)

#
#    def testSubItems(self):
#
#        for row in range(self.ctrl.item_count())
#
#        for i in self.ctrl.items():
#
#            #self.assertEqual(item.Text, texts[i])

    def testEqualsItems(self):
        """
        Test __eq__ and __ne__ cases for _listview_item.
        """
        item1 = self.ctrl.get_item(0, 0)
        item1_copy = self.ctrl.get_item(0, 0)
        item2 = self.ctrl.get_item(1, 0)

        self.assertEqual(item1, item1_copy)
        self.assertNotEqual(item1, "Not _listview_item")
        self.assertNotEqual(item1, item2)

    def test_cells_rectangles(self):
        """Test the ListView get_item rectangle method for cells"""
        if not self.dlg.Toolbar.button(4).is_checked():
            self.dlg.Toolbar.button(4).click()

        for row in range(self.ctrl.item_count() - 1):
            for col in range(self.ctrl.column_count() - 1):
                self.assertEqual(
                    self.ctrl.get_item(row, col).rectangle(area="text").right,
                    self.ctrl.get_item(row, col + 1).rectangle(area="text").left)
                self.assertEqual(
                    self.ctrl.get_item(row, col).rectangle(area="text").bottom,
                    self.ctrl.get_item(row + 1, col).rectangle(area="text").top)

        self.assertEqual(self.ctrl.get_item(1, 2).rectangle(area="text"),
                                RECT(200, 36, 250, 53))
        self.assertEqual(self.ctrl.get_item(3, 4).rectangle(area="text"),
                                RECT(300, 70, 400, 87))

    def test_inplace_control(self):
        """Test the ListView inplace_control method for item"""
        # Item is not editable so it will raise timeout error
        with self.assertRaises(Exception) as context:
            self.ctrl.get_item(0).inplace_control()
        self.assertTrue('In-place-edit control for item' in str(context.exception))


if is_x64_Python():

    class ListViewTestCases64(ListViewTestCases32):

        """Unit tests for the 64-bit ListViewWrapper on a 32-bit sample"""

        path = os.path.join(mfc_samples_folder, u"RowList.exe")


class ListViewWinFormTestCases32(unittest.TestCase):

    """Unit tests for the ListViewWrapper class with WinForm applications"""

    path = os.path.join(winforms_folder_32, u"ListView_TestApp.exe")

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.defaults()

        app = Application()
        app.start(self.path)

        self.dlg = app.ListViewEx
        self.ctrl = app.ListViewEx.ListView.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)

    def test_cell_click_input(self):
        """Test the ListView get_item click_input method"""
        self.ctrl.get_item(0,2).click_input(double=True, where="text")
        self.dlg.type_keys("{ENTER}")
        # For make sure the input is finished, click to another place
        self.ctrl.get_item(0,3).click_input(double=False, where="text")
        self.assertEqual(str(self.ctrl.get_item(0,2).text()), u"Clicked!")

    def test_get_editor_of_datetimepicker(self):
        """Test the ListView inplace_control method using DateTimePicker"""
        dt_picker = self.ctrl.get_item(2,0).inplace_control("DateTimePicker")
        dt_picker.set_time(year=2017, month=5, day=23)
        cur_time = dt_picker.get_time();
        self.assertEqual(cur_time.wYear, 2017)
        self.assertEqual(cur_time.wMonth, 5)
        self.assertEqual(cur_time.wDay, 23)

    def test_get_editor_of_combobox(self):
        """Test the ListView inplace_control method using ComboBox"""
        combo_box = self.ctrl.get_item(1,1).inplace_control("ComboBox")
        combo_box.select(combo_box.selected_index() - 1)
        self.assertEqual(combo_box.selected_index(), 2)

    def test_get_editor_of_editwrapper(self):
        """Test the ListView inplace_control method using EditWrapper"""
        dt_picker = self.ctrl.get_item(3,4).inplace_control("Edit")
        dt_picker.set_text("201")
        self.assertEqual(dt_picker.text_block(), u"201")

    def test_get_editor_wrong_args(self):
        """Test the ListView inplace_control case when used wrong friendly class name"""
        with self.assertRaises(Exception) as context:
            self.ctrl.get_item(1,1).inplace_control("Edit")
        self.assertTrue('In-place-edit control "Edit"' in str(context.exception))

    def test_automation_id_by_win32(self):
        list_view = self.dlg.child_window(auto_id="listViewEx1").wait('visible')
        self.assertEqual(list_view.automation_id(), "listViewEx1")

        check_box = self.dlg.child_window(auto_id="checkBoxDoubleClickActivation").wait('visible')
        self.assertEqual(check_box.automation_id(), "checkBoxDoubleClickActivation")

        check_box = self.dlg.checkBoxDoubleClickActivation.wait('visible')
        self.assertEqual(check_box.automation_id(), "checkBoxDoubleClickActivation")

    def test_win32_control_type(self):
        list_view = self.dlg.child_window(control_type="ListViewEx.ListViewEx").wait('visible')
        self.assertEqual(list_view.control_type(), "ListViewEx.ListViewEx")
        self.assertEqual(list_view.full_control_type(),
                         "ListViewEx.ListViewEx, ListViewEx, Version=1.0.6520.42612, " \
                         "Culture=neutral, PublicKeyToken=null")

        check_box = self.dlg.child_window(control_type="System.Windows.Forms.CheckBox").wait('visible')
        self.assertEqual(check_box.control_type(), "System.Windows.Forms.CheckBox")
        self.assertEqual(check_box.full_control_type(),
                         "System.Windows.Forms.CheckBox, System.Windows.Forms, " \
                         "Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")

if is_x64_Python():

    class ListViewWinFormTestCases64(ListViewWinFormTestCases32):

        """Unit tests for the 64-bit ListViewWrapper on a 32-bit sample"""

        path = os.path.join(winforms_folder, u"ListView_TestApp.exe")


class TreeViewTestCases32(unittest.TestCase):

    """Unit tests for the TreeViewWrapper class"""

    path = os.path.join(controlspy_folder_32, "Tree View.exe")

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.root_text = "The Planets"
        self.texts = [
            ("Mercury", '57,910,000', '4,880', '3.30e23'),
            ("Venus",   '108,200,000', '12,103.6', '4.869e24'),
            ("Earth",   '149,600,000', '12,756.3', '5.9736e24'),
            ("Mars",    '227,940,000', '6,794', '6.4219e23'),
            ("Jupiter", '778,330,000', '142,984', '1.900e27'),
            ("Saturn",  '1,429,400,000', '120,536', '5.68e26'),
            ("Uranus",  '2,870,990,000', '51,118', '8.683e25'),
            ("Neptune", '4,504,000,000', '49,532', '1.0247e26'),
            ("Pluto",   '5,913,520,000', '2,274', '1.27e22'),
        ]

        self.app = Application()
        self.app.start(self.path)
        self.dlg = self.app.MicrosoftControlSpy
        self.ctrl = self.app.MicrosoftControlSpy.TreeView.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)

    def test_friendly_class_name(self):
        """Make sure the friendly class name is set correctly (TreeView)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "TreeView")

    def testItemCount(self):
        """Test the TreeView ItemCount method"""
        self.assertEqual(self.ctrl.item_count(), 37)

    def testGetItem(self):
        """Test the get_item method"""
        self.assertRaises(RuntimeError, self.ctrl.get_item, "test\here\please")

        self.assertRaises(IndexError, self.ctrl.get_item, r"\test\here\please")

        self.assertEqual(
            self.ctrl.get_item((0, 1, 2)).text(), self.texts[1][3] + " kg")

        self.assertEqual(
            self.ctrl.get_item(r"\The Planets\Venus\4.869e24 kg", exact=True).text(), self.texts[1][3] + " kg")

        self.assertEqual(
            self.ctrl.get_item(["The Planets", "Venus", "4.869"]).text(),
            self.texts[1][3] + " kg"
        )

    def testItemText(self):
        """Test the TreeView item Text() method"""
        self.assertEqual(self.ctrl.tree_root().text(), self.root_text)

        self.assertEqual(
            self.ctrl.get_item((0, 1, 2)).text(), self.texts[1][3] + " kg")

    def testSelect(self):
        """Test selecting an item"""
        self.ctrl.select((0, 1, 2))

        self.ctrl.get_item((0, 1, 2)).state()

        self.assertEqual(True, self.ctrl.is_selected((0, 1, 2)))

    def testEnsureVisible(self):
        """make sure that the item is visible"""
        # TODO: note this is partially a fake test at the moment because
        # just by getting an item - we usually make it visible
        self.ctrl.ensure_visible((0, 8, 2))

        # make sure that the item is not hidden
        self.assertNotEqual(None, self.ctrl.get_item((0, 8, 2)).client_rect())

    def testGetProperties(self):
        """Test getting the properties for the treeview control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            "TreeView", props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemsClick(self):
        """Test clicking of items and sub-items in the treeview control"""
        planets_item_path = (0, 0)
        mercury_diam_item_path = (0, 0, 1)
        mars_dist_item_path = (0, 3, 0)

        itm = self.ctrl.get_item(planets_item_path)
        itm.ensure_visible()
        time.sleep(1)
        itm.click(button='left')
        self.assertEqual(True, self.ctrl.is_selected(planets_item_path))

        itm = self.ctrl.get_item(mars_dist_item_path)
        itm.ensure_visible()
        time.sleep(1)
        itm.click(button='left')
        self.assertEqual(True, self.ctrl.is_selected(mars_dist_item_path))

        itm = self.ctrl.get_item(mercury_diam_item_path)
        itm.ensure_visible()
        time.sleep(1)
        itm.click(button='left')
        self.assertEqual(True, self.ctrl.is_selected(mercury_diam_item_path))
        self.assertEqual(False, self.ctrl.is_selected(mars_dist_item_path))

        itm = self.ctrl.get_item(planets_item_path)
        itm.ensure_visible()
        time.sleep(1)
        itm.click(button='left')
        self.assertEqual(True, self.ctrl.is_selected(planets_item_path))
        self.assertEqual(False, self.ctrl.is_selected(mercury_diam_item_path))


if is_x64_Python():

    class TreeViewTestCases64(TreeViewTestCases32):

        """Unit tests for the 64-bit TreeViewWrapper on a 32-bit sample"""

        path = os.path.join(controlspy_folder, "Tree View.exe")


class TreeViewAdditionalTestCases(unittest.TestCase):

    """More unit tests for the TreeViewWrapper class (CmnCtrl1.exe)"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.dlg = self.app.CommonControlsSample
        self.ctrl = self.app.CommonControlsSample.TreeView.wrapper_object()
        self.app.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1)

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)
        self.app.kill()

    def testCheckBoxes(self):
        """Make sure tree view item method is_checked() works as expected"""
        self.dlg.set_focus()
        self.dlg.TVS_CHECKBOXES.check_by_click()
        birds = self.ctrl.get_item(r'\Birds')
        self.ctrl.set_focus() # to make sure focus is not lost by any accident event
        birds.click(where='check')
        self.assertEqual(birds.is_checked(), True)
        birds.click_input(where='check')
        wait_until(3, 0.4, birds.is_checked, value=False)

    def testPrintItems(self):
        """Test TreeView method print_items()"""
        birds = self.ctrl.get_item(r'\Birds')
        birds.expand()
        items_str = self.ctrl.print_items()
        self.assertEqual(items_str, "Treeview1\nBirds\n Eagle\n Hummingbird\n Pigeon\n" +
                                     "Dogs\n Dalmatian\n German Shepherd\n Great Dane\n" +
                                     "Fish\n Salmon\n Snapper\n Sole\n")

    def testIsSelected(self):
        """Make sure tree view item method IsSelected() works as expected"""
        birds = self.ctrl.get_item(r'\Birds')
        birds.expand()
        eagle = self.ctrl.get_item(r'\Birds\Eagle')
        eagle.select()
        self.assertEqual(eagle.is_selected(), True)

    def test_expand_collapse(self):
        """Make sure tree view item methods Expand() and Collapse() work as expected"""
        birds = self.ctrl.get_item(r'\Birds')
        birds.expand()
        self.assertEqual(birds.is_expanded(), True)

        birds.collapse()
        self.assertEqual(birds.is_expanded(), False)

    def test_expand_collapse_buttons(self):
        """Make sure correct area is clicked"""
        self.dlg.TVS_HASBUTTONS.click_input()
        self.dlg.TVS_HASLINES.click_input()
        self.dlg.TVS_LINESATROOT.click_input()
        birds = self.ctrl.get_item(r'\Birds')

        birds.click(where='button')
        self.assertEqual(birds.is_expanded(), True)
        birds.click(double=True, where='icon')
        self.assertEqual(birds.is_expanded(), False)

        birds.click_input(where='button')
        self.assertEqual(birds.is_expanded(), True)
        birds.click_input(double=True, where='icon')
        self.assertEqual(birds.is_expanded(), False)

    def testIncorrectAreas(self):
        """Make sure incorrect area raises an exception"""
        birds = self.ctrl.get_item(r'\Birds')
        self.assertRaises(RuntimeError, birds.click, where='radiob')
        self.assertRaises(RuntimeError, birds.click_input, where='radiob')

    def testStartDraggingAndDrop(self):
        """Make sure tree view item methods StartDragging() and drop() work as expected"""
        birds = self.ctrl.get_item(r'\Birds')
        birds.expand()

        pigeon = self.ctrl.get_item(r'\Birds\Pigeon')
        pigeon.start_dragging()

        eagle = self.ctrl.get_item(r'\Birds\Eagle')
        eagle.drop()

        self.assertRaises(IndexError, birds.get_child, 'Pigeon')
        self.assertRaises(IndexError, self.ctrl.get_item, r'\Birds\Pigeon')
        self.assertRaises(IndexError, self.ctrl.get_item, [0, 2])
        self.assertRaises(IndexError, self.ctrl.get_item, r'\Bread', exact=True)

        new_pigeon = self.ctrl.get_item(r'\Birds\Eagle\Pigeon')
        self.assertEqual(len(birds.children()), 2)
        self.assertEqual(new_pigeon.children(), [])


class HeaderTestCases(unittest.TestCase):

    """Unit tests for the Header class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "RowList.exe"), timeout=20)

        self.texts = [u'Color', u'Red', u'Green', u'Blue', u'Hue', u'Sat', u'Lum', u'Type']
        self.item_rects = [
            RECT(000, 0, 150, 19),
            RECT(150, 0, 200, 19),
            RECT(200, 0, 250, 19),
            RECT(250, 0, 300, 19),
            RECT(300, 0, 400, 19),
            RECT(400, 0, 450, 19),
            RECT(450, 0, 500, 19),
            RECT(500, 0, 650, 19)]

        self.app = app
        self.dlg = app.RowListSampleApplication
        self.ctrl = app.RowListSampleApplication.Header.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (Header)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "Header")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEqual(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the header control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        self.assertEqual(8, self.ctrl.item_count())

    def testGetColumnRectangle(self):
        for i in range(0, 3):
            self.assertEqual(self.item_rects[i].left, self.ctrl.get_column_rectangle(i).left)
            self.assertEqual(self.item_rects[i].right, self.ctrl.get_column_rectangle(i).right)
            self.assertEqual(self.item_rects[i].top, self.ctrl.get_column_rectangle(i).top)
            self.assertFalse(abs(self.item_rects[i].bottom - self.ctrl.get_column_rectangle(i).bottom) > 2)

    def testClientRects(self):
        test_rects = self.item_rects
        test_rects.insert(0, self.ctrl.client_rect())

        client_rects = self.ctrl.client_rects()
        self.assertEqual(len(test_rects), len(client_rects))
        for i, r in enumerate(test_rects):
            self.assertEqual(r.left, client_rects[i].left)
            self.assertEqual(r.right, client_rects[i].right)
            self.assertEqual(r.top, client_rects[i].top)
            self.assertFalse(abs(r.bottom - client_rects[i].bottom) > 2)  # may be equal to 17 or 19

    def testGetColumnText(self):
        for i in range(0, 3):
            self.assertEqual(
                self.texts[i],
                self.ctrl.get_column_text(i))


class StatusBarTestCases(unittest.TestCase):

    """Unit tests for the TreeViewWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        app = Application()
        app.start(os.path.join(controlspy_folder, "Status bar.exe"))

        self.texts = ["Long text", "", "Status Bar"]
        self.part_rects = [
            RECT(0, 2, 65, 22),
            RECT(67, 2, 90, 22),
            RECT(92, 2, 261, 22)]
        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.StatusBar.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)

    def test_friendly_class_name(self):
        """Make sure the friendly class name is set correctly (StatusBar)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "StatusBar")

    def test_texts(self):
        """Make sure the texts are set correctly"""
        self.assertEqual(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the status bar control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testBorderWidths(self):
        """Make sure the border widths are retrieved correctly"""
        self.assertEqual(
            self.ctrl.border_widths(),
            dict(
                Horizontal=0,
                Vertical=2,
                Inter=2,
            )
        )

    def testPartCount(self):
        "Make sure the number of parts is retrieved correctly"
        self.assertEqual(self.ctrl.part_count(), 3)

    def testPartRightEdges(self):
        "Make sure the part widths are retrieved correctly"

        for i in range(0, self.ctrl.part_count() - 1):
            self.assertEqual(self.ctrl.part_right_edges()[i], self.part_rects[i].right)

        self.assertEqual(self.ctrl.part_right_edges()[i + 1], -1)

    def testGetPartRect(self):
        "Make sure the part rectangles are retrieved correctly"

        for i in range(0, self.ctrl.part_count()):
            part_rect = self.ctrl.get_part_rect(i)
            self.assertEqual(part_rect.left, self.part_rects[i].left)
            if i != self.ctrl.part_count() - 1:
                self.assertEqual(part_rect.right, self.part_rects[i].right)
            self.assertEqual(part_rect.top, self.part_rects[i].top)
            self.assertFalse(abs(part_rect.bottom - self.part_rects[i].bottom) > 2)

        self.assertRaises(IndexError, self.ctrl.get_part_rect, 99)

    def testClientRects(self):
        self.assertEqual(self.ctrl.client_rect(), self.ctrl.client_rects()[0])
        client_rects = self.ctrl.client_rects()[1:]
        for i, client_rect in enumerate(client_rects):
            self.assertEqual(self.part_rects[i].left, client_rect.left)
            if i != len(client_rects) - 1:
                self.assertEqual(self.part_rects[i].right, client_rect.right)
            self.assertEqual(self.part_rects[i].top, client_rect.top)
            self.assertFalse(abs(self.part_rects[i].bottom - client_rect.bottom) > 2)

    def testGetPartText(self):
        self.assertRaises(IndexError, self.ctrl.get_part_text, 99)

        for i, text in enumerate(self.texts):
            self.assertEqual(text, self.ctrl.get_part_text(i))


class TabControlTestCases(unittest.TestCase):

    """Unit tests for the TreeViewWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()
        self.screen_w = win32api.GetSystemMetrics(0)

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.texts = [
            u"CTreeCtrl", u"CAnimateCtrl", u"CToolBarCtrl",
            u"CDateTimeCtrl", u"CMonthCalCtrl"]

        self.rects = [
            RECT(2,   2, 58,  20),
            RECT(58,  2, 130, 20),
            RECT(130, 2, 201, 20),
            RECT(201, 2, 281, 20),
            RECT(281, 2, 360, 20)
        ]

        self.app = app
        self.dlg = app.CommonControlsSample
        self.ctrl = app.CommonControlsSample.TabControl.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (TabControl)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "TabControl")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEqual(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the tabcontrol"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testRowCount(self):
        self.assertEqual(1, self.ctrl.row_count())

        dlgClientRect = self.ctrl.parent().rectangle()  # use the parent as a reference
        prev_rect = self.ctrl.rectangle() - dlgClientRect

        # squeeze the tab control to force two rows
        new_rect = RECT(prev_rect)
        new_rect.right = int(new_rect.width() / 2)

        self.ctrl.move_window(
            new_rect.left,
            new_rect.top,
            new_rect.width(),
            new_rect.height(),
        )
        time.sleep(0.1)

        # verify two tab rows
        self.assertEqual(2, self.ctrl.row_count())

        # restore back the original size of the control
        self.ctrl.move_window(prev_rect)
        self.assertEqual(1, self.ctrl.row_count())

    def testGetSelectedTab(self):
        self.assertEqual(0, self.ctrl.get_selected_tab())
        self.ctrl.select(1)
        self.assertEqual(1, self.ctrl.get_selected_tab())
        self.ctrl.select(u"CMonthCalCtrl")
        self.assertEqual(4, self.ctrl.get_selected_tab())

    def testTabCount(self):
        """Make sure the number of parts is retrieved correctly"""
        self.assertEqual(self.ctrl.tab_count(), 5)

    def testGetTabRect(self):
        """Make sure the part rectangles are retrieved correctly"""
        for i, _ in enumerate(self.rects):
            self.assertEqual(self.ctrl.get_tab_rect(i), self.rects[i])

        self.assertRaises(IndexError, self.ctrl.get_tab_rect, 99)

#    def testGetTabState(self):
#        self.assertRaises(IndexError, self.ctrl.GetTabState, 99)
#
#        self.dlg.StatementEdit.SetEditText ("MSG (TCM_HIGHLIGHTITEM,1,MAKELONG(TRUE,0))")
#
#        time.sleep(.3)
#        # use CloseClick to allow the control time to respond to the message
#        self.dlg.Send.CloseClick()
#        time.sleep(2)
#        print("==\n",self.ctrl.TabStates())
#
#        self.assertEqual(self.ctrl.GetTabState(1), 1)
#
#    def testTabStates(self):
#        print(self.ctrl.TabStates())
#        raise "tabstates hiay"

    def testGetTabText(self):
        for i, text in enumerate(self.texts):
            self.assertEqual(text, self.ctrl.get_tab_text(i))

        self.assertRaises(IndexError, self.ctrl.get_tab_text, 99)

    def testClientRects(self):
        self.assertEqual(self.ctrl.client_rect(), self.ctrl.client_rects()[0])
        self.assertEqual(self.rects, self.ctrl.client_rects()[1:])

    def testSelect(self):
        self.assertEqual(0, self.ctrl.get_selected_tab())

        self.ctrl.select(1)
        self.assertEqual(1, self.ctrl.get_selected_tab())
        self.ctrl.select(u"CToolBarCtrl")
        self.assertEqual(2, self.ctrl.get_selected_tab())

        self.assertRaises(IndexError, self.ctrl.select, 99)


class ToolbarTestCases(unittest.TestCase):

    """Unit tests for the ToolbarWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.app = app
        self.dlg = app.CommonControlsSample

        # select a tab with toolbar controls
        self.dlg.SysTabControl.select(u"CToolBarCtrl")

        # see identifiers available at that tab
        #self.dlg.PrintControlIdentifiers()

        # The sample app has two toolbars. The first toolbar can be
        # addressed as Toolbar, Toolbar0 and Toolbar1.
        # The second control goes as Toolbar2
        self.ctrl = app.CommonControlsSample.ToolbarNew.wrapper_object()
        self.ctrl2 = app.CommonControlsSample.ToolbarErase.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (Toolbar)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "Toolbar")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        for txt in self.ctrl.texts():
            self.assertEqual(isinstance(txt, six.string_types), True)

    def testGetProperties(self):
        """Test getting the properties for the toolbar control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        self.assertEqual(
            self.ctrl.button_count(), props['button_count'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testButtonCount(self):
        """Test the button count method of the toolbar"""
        # TODO: for a some reason the first toolbar returns button count = 12
        # The same as in the second toolbar, even though their handles are different.
        # Maybe the test app itself has to be fixed too.
        #self.assertEqual(self.ctrl.button_count(), 9)

        self.assertEqual(self.ctrl2.button_count(), 12)

    def testGetButton(self):
        self.assertRaises(IndexError, self.ctrl.get_button, 29)

    def testGetButtonRect(self):
        rect_ctrl = self.ctrl.get_button_rect(0)
        self.assertEqual((rect_ctrl.left, rect_ctrl.top), (0, 0))
        self.assertFalse((rect_ctrl.right - rect_ctrl.left) > 40)
        self.assertFalse((rect_ctrl.right - rect_ctrl.left) < 36)
        self.assertFalse((rect_ctrl.bottom - rect_ctrl.top) > 38)
        self.assertFalse((rect_ctrl.bottom - rect_ctrl.top) < 36)
        #self.assertEqual(rect_ctrl, RECT(0, 0, 40, 38))

        rect_ctrl2 = self.ctrl2.get_button_rect(0)
        self.assertEqual((rect_ctrl2.left, rect_ctrl2.top), (0, 0))
        self.assertFalse((rect_ctrl2.right - rect_ctrl2.left) > 70)
        self.assertFalse((rect_ctrl2.right - rect_ctrl2.left) < 64)
        self.assertFalse((rect_ctrl2.bottom - rect_ctrl2.top) > 38)
        self.assertFalse((rect_ctrl2.bottom - rect_ctrl2.top) < 36)
        #self.assertEqual(rect_ctrl2, RECT(0, 0, 70, 38))

    def testGetToolTipsControls(self):
        tips = self.ctrl.get_tool_tips_control()
        tt = tips.texts()
        self.assertEqual(u"New" in tt, True)
        self.assertEqual(u"About" in tt, True)

        tips = self.ctrl2.get_tool_tips_control()
        tt = tips.texts()
        self.assertEqual(u"Pencil" in tt, True)
        self.assertEqual(u"Ellipse" in tt, True)

    def testPressButton(self):

        self.ctrl.press_button(0)

        #print(self.ctrl.texts())
        self.assertRaises(
            findbestmatch.MatchError,
            self.ctrl.press_button,
            "asdfdasfasdf")

        # todo more tests for pressbutton
        self.ctrl.press_button(u"Open")

    def testCheckButton(self):
        self.ctrl2.check_button('Erase', True)
        self.assertEqual(self.ctrl2.button('Erase').is_checked(), True)

        self.ctrl2.check_button('Pencil', True)
        self.assertEqual(self.ctrl2.button('Erase').is_checked(), False)

        self.ctrl2.check_button('Erase', False)
        self.assertEqual(self.ctrl2.button('Erase').is_checked(), False)

        # try to check separator
        self.assertRaises(RuntimeError, self.ctrl.check_button, 3, True)

    def testIsCheckable(self):
        self.assertNotEqual(self.ctrl2.button('Erase').is_checkable(), False)
        self.assertEqual(self.ctrl.button('New').is_checkable(), False)

    def testIsPressable(self):
        self.assertEqual(self.ctrl.button('New').is_pressable(), True)

    def testButtonByTooltip(self):
        self.assertEqual(self.ctrl.button('New', by_tooltip=True).text(), 'New')
        self.assertEqual(self.ctrl.button('About', exact=False, by_tooltip=True).text(), 'About')


class RebarTestCases(unittest.TestCase):

    """Unit tests for the UpDownWrapper class"""

    def setUp(self):
        """Start the application, set some data and wait for the state we want

        The app title can be tricky. If no document is opened the title is just: "RebarTest"
        However if a document is created/opened in the child frame
        the title is appended with a document name: "RebarTest - RebarTest1"
        A findbestmatch proc does well here with guessing the title
        even though the app is started with a short title "RebarTest".
        """
        Timings.fast()
        app = Application()
        app.start(os.path.join(mfc_samples_folder, "RebarTest.exe"))
        mouse.move((-500, 200))  # remove the mouse from the screen to avoid side effects
        self.app = app
        self.dlg = app.RebarTest_RebarTest
        self.dlg.wait('ready', 20)
        self.ctrl = app.RebarTest_RebarTest.Rebar.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill(soft=True)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ReBar)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "ReBar")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        for txt in self.ctrl.texts():
            self.assertEqual(isinstance(txt, six.string_types), True)

    def testBandCount(self):
        """Make sure band_count() returns 2"""
        self.assertEqual(self.ctrl.band_count(), 2)

    def testGetBand(self):
        """Check that get_band() is working corectly"""
        self.assertRaises(IndexError, self.ctrl.get_band, 99)
        self.assertRaises(IndexError, self.ctrl.get_band, 2)

        band = self.ctrl.get_band(0)

        self.assertEqual(band.hwndChild, self.dlg.MenuBar.handle)

        self.assertEqual(self.ctrl.get_band(1).text, u"Tools band:")
        self.assertEqual(self.ctrl.get_band(0).text, u"Menus band:")

    def testGetToolTipsControl(self):
        """Make sure GetToolTipsControl() returns None"""
        self.assertEqual(self.ctrl.get_tool_tips_control(), None)

    def testAfxToolBarButtons(self):
        """Make sure we can click on Afx ToolBar button by index"""
        Timings.closeclick_dialog_close_wait = 2.
        self.dlg.StandardToolbar.button(1).click()
        self.app.window(title='Open').wait('ready', timeout=30)
        self.app.window(title='Open').Cancel.close_click()

    def testMenuBarClickInput(self):
        """Make sure we can click on Menu Bar items by indexed path"""
        self.assertRaises(TypeError, self.dlg.MenuBar.menu_bar_click_input, '#one->#0', self.app)

        self.dlg.MenuBar.menu_bar_click_input('#1->#0->#0', self.app)
        self.app.Customize.CloseButton.click()
        self.app.Customize.wait_not('visible')

        self.dlg.MenuBar.menu_bar_click_input([2, 0], self.app)
        self.app.window(title='About RebarTest').OK.click()
        self.app.window(title='About RebarTest').wait_not('visible')


class DatetimeTestCases(unittest.TestCase):

    """Unit tests for the DateTimePicker class"""

    def setUp(self):
        """Start the application and get 'Date Time Picker' control"""
        Timings.fast()
        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.app = app
        self.dlg = app.CommonControlsSample
        self.dlg.wait('ready', 20)
        tab = app.CommonControlsSample.TabControl.wrapper_object()
        tab.select(3)
        self.ctrl = self.dlg.DateTimePicker

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (DateTimePicker)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "DateTimePicker")

    def testGetTime(self):
        """Test reading a date from a 'Date Time Picker' control"""

        # No check for seconds and milliseconds as it can slip
        # These values are verified in the next 'testSetTime'
        test_date_time = self.ctrl.get_time()
        date_time_now = datetime.now()
        self.assertEqual(test_date_time.wYear, date_time_now.year)
        self.assertEqual(test_date_time.wMonth, date_time_now.month)
        self.assertEqual(test_date_time.wDay, date_time_now.day)
        self.assertEqual(test_date_time.wHour, date_time_now.hour)
        self.assertEqual(test_date_time.wMinute, date_time_now.minute)

    def testSetTime(self):
        """Test setting a date to a 'Date Time Picker' control"""
        year = 2025
        month = 9
        day_of_week = 5
        day = 19
        hour = 1
        minute = 2
        second = 3
        milliseconds = 781
        self.ctrl.set_time(
            year=year,
            month=month,
            day_of_week=day_of_week,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            milliseconds=milliseconds
        )

        # Retrive back the values we set
        test_date_time = self.ctrl.get_time()
        self.assertEqual(test_date_time.wYear, year)
        self.assertEqual(test_date_time.wMonth, month)
        self.assertEqual(test_date_time.wDay, day)
        self.assertEqual(test_date_time.wDayOfWeek, day_of_week)
        self.assertEqual(test_date_time.wHour, hour)
        self.assertEqual(test_date_time.wMinute, minute)
        self.assertEqual(test_date_time.wSecond, second)
        self.assertEqual(test_date_time.wMilliseconds, milliseconds)


class ToolTipsTestCases(unittest.TestCase):

    """Unit tests for the tooltips class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()
        self.texts = [u'', u'New', u'Open', u'Save', u'Cut', u'Copy', u'Paste', u'Print', u'About', u'Help']

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))
        #app.start_(os.path.join(controlspy_folder, "Tooltip.exe"))

        self.app = app
        self.dlg = app.Common_Controls_Sample

        # Make sure the mouse doesn't hover over tested controls
        # so it won't generate an unexpected tooltip
        self.dlg.move_mouse_input(coords=(-100, -100), absolute=True)

        self.dlg.TabControl.select(u'CToolBarCtrl')

        self.ctrl = self.dlg.Toolbar.get_tool_tips_control()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.app.kill()

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ToolTips)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "ToolTips")

    def testGetProperties(self):
        """Test getting the properties for the tooltips control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def test_get_tip(self):
        """Test that get_tip() returns correct ToolTip object"""
        self.assertRaises(IndexError, self.ctrl.get_tip, 99)
        tip = self.ctrl.get_tip(1)
        self.assertEqual(tip.text, self.texts[1])

    def test_tool_count(self):
        """Test that tool_count() returns correct value"""
        self.assertEqual(10, self.ctrl.tool_count())

    def test_get_tip_text(self):
        """Test that get_tip_text() returns correct text"""
        self.assertEqual(self.texts[1], self.ctrl.get_tip_text(1))

    def test_texts(self):
        """Make sure the texts are set correctly"""
        # just to make sure a tooltip is not shown
        self.dlg.move_mouse_input(coords=(0, 0), absolute=False)
        ActionLogger().log('ToolTips texts = ' + ';'.join(self.ctrl.texts()))
        self.assertEqual(self.ctrl.texts()[0], '')
        self.assertEqual(self.ctrl.texts()[1:], self.texts)


class UpDownTestCases(unittest.TestCase):

    """Unit tests for the UpDownWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()
        app = Application()
        app.start(os.path.join(controlspy_folder, "Up-Down.exe"))

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.UpDown2.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (UpDown)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "UpDown")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEqual(self.ctrl.texts()[1:], [])

    def testGetProperties(self):
        """Test getting the properties for the updown control"""
        props = self.ctrl.get_properties()

        self.assertEqual(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetValue(self):
        """Test getting up-down position"""
        self.assertEqual(self.ctrl.get_value(), 0)

        self.ctrl.set_value(23)
        self.assertEqual(self.ctrl.get_value(), 23)

    def testSetValue(self):
        """Test setting up-down position"""
        self.assertEqual(self.ctrl.get_value(), 0)

        self.ctrl.set_value(23)
        self.assertEqual(self.ctrl.get_value(), 23)
        self.assertEqual(
            int(self.ctrl.get_buddy_control().texts()[1]),
            23)

    def testGetBase(self):
        """Test getting the base of the up-down control"""
        self.assertEqual(self.ctrl.get_base(), 10)
        #self.dlg.StatementEdit.SetEditText ("MSG (UDM_SETBASE, 16, 0)")

        # use CloseClick to allow the control time to respond to the message
        #self.dlg.Send.click_input()
        self.ctrl.set_base(16)

        self.assertEqual(self.ctrl.get_base(), 16)

    def testGetRange(self):
        """Test getting the range of the up-down control"""
        self.assertEqual((0, 9999), self.ctrl.get_range())

    def testGetBuddy(self):
        """Test getting the buddy control"""
        self.assertEqual(self.ctrl.get_buddy_control().handle, self.dlg.Edit6.handle)

    def testIncrement(self):
        """Test incremementing up-down position"""
        Timings.defaults()
        self.ctrl.increment()
        self.assertEqual(self.ctrl.get_value(), 1)

    def testDecrement(self):
        """Test decrementing up-down position"""
        Timings.defaults()
        self.ctrl.set_value(23)
        self.ctrl.decrement()
        self.assertEqual(self.ctrl.get_value(), 22)


class TrackbarWrapperTestCases(unittest.TestCase):

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        app = Application()
        app.start(os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"))
        dlg = app.top_window()
        dlg.TabControl.select(1)

        ctrl = dlg.Trackbar.wrapper_object()
        self.app = app
        self.dlg = dlg
        self.ctrl = ctrl

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def test_friendly_class(self):
        """Make sure the Trackbar friendly class is set correctly"""
        self.assertEqual(self.ctrl.friendly_class_name(), u"Trackbar")

    def test_get_range_max(self):
        """Test the get_range_max method"""
        self.ctrl.set_range_max(100)
        self.assertEqual(self.ctrl.get_range_max(), 100)

    def test_get_range_min(self):
        """Test the get_range_min method"""
        self.ctrl.set_range_min(25)
        self.assertEqual(self.ctrl.get_range_min(), 25)

    def test_set_range_min_more_then_range_max(self):
        """Test the set_range_min method with error"""
        self.assertRaises(ValueError, self.ctrl.set_range_min, self.ctrl.get_range_max() + 1)

    def test_set_position_more_than_max_range(self):
        """Test the set_position method with error"""
        self.ctrl.set_range_max(100)
        self.assertRaises(ValueError, self.ctrl.set_position, 110)

    def test_set_position_less_than_min_range(self):
        """Test the set_position method with error"""
        self.assertRaises(ValueError, self.ctrl.set_position, self.ctrl.get_range_min() - 10)

    def test_set_correct_position(self):
        """Test the set_position method"""
        self.ctrl.set_position(23)
        self.assertEqual(self.ctrl.get_position(), 23)

    def test_get_num_ticks(self):
        """Test the get_num_ticks method"""
        self.assertEqual(self.ctrl.get_num_ticks(), 6)

    def test_get_channel_rect(self):
        """Test the get_channel_rect method"""
        system_rect = RECT()
        system_rect.left = 8
        system_rect.top = 19
        system_rect.right = 249
        system_rect.bottom = 23
        self.assert_channel_rect(self.ctrl.get_channel_rect(), system_rect)

    def assert_channel_rect(self, first_rect, second_rect):
        """Compare two rect strucrures"""
        self.assertEqual(first_rect.height(), second_rect.height())
        self.assertEqual(first_rect.width(), second_rect.width())

    def test_get_line_size(self):
        """Test the get_line_size method"""
        self.ctrl.set_line_size(10)
        self.assertEqual(self.ctrl.get_line_size(), 10)

    def test_get_page_size(self):
        """Test the set_page_size method"""
        self.ctrl.set_page_size(14)
        self.assertEqual(self.ctrl.get_page_size(), 14)

    def test_get_tool_tips_control(self):
        """Test the get_tooltips_control method"""
        self.assertRaises(RuntimeError, self.ctrl.get_tooltips_control)

    def test_set_sel(self):
        """Test the set_sel method"""
        self.assertRaises(RuntimeError, self.ctrl.set_sel, 22, 55)

    def test_get_sel_start(self):
        """Test the get_sel_start method"""
        self.assertRaises(RuntimeError, self.ctrl.get_sel_start)

    def test_get_sel_end(self):
        """Test the get_sel_end method"""
        self.assertRaises(RuntimeError, self.ctrl.get_sel_end)


if __name__ == "__main__":
    unittest.main()
