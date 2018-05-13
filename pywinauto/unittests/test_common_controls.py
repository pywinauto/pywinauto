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
        Timings.Fast()

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
        self.ctrl = app.RowListSampleApplication.ListView.WrapperObject()
        self.dlg.Toolbar.Button(0).Click()  # switch to icon view
        self.dlg.Toolbar.Button(6).Click()  # switch off states

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the ListView friendly class is set correctly"""
        self.assertEquals(self.ctrl.friendly_class_name(), u"ListView")

    def testColumnCount(self):
        """Test the ListView ColumnCount method"""
        self.assertEquals(self.ctrl.ColumnCount(), 8)

    def testItemCount(self):
        """Test the ListView ItemCount method"""
        self.assertEquals(self.ctrl.ItemCount(), 7)

    def testItemText(self):
        """Test the ListView item.Text property"""
        item = self.ctrl.GetItem(1)

        self.assertEquals(item['text'], u"Red")

    def testItems(self):
        """Test the ListView Items method"""
        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        items = self.ctrl.Items()
        for i, item in enumerate(items):
            self.assertEquals(item['text'], flat_texts[i])
        self.assertEquals(len(items), len(flat_texts))

    def testTexts(self):
        """Test the ListView texts method"""
        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        self.assertEquals(flat_texts, self.ctrl.texts()[1:])

    def testGetItem(self):
        """Test the ListView GetItem method"""
        for row in range(self.ctrl.ItemCount()):
            for col in range(self.ctrl.ColumnCount()):
                self.assertEquals(
                    self.ctrl.GetItem(row, col)['text'], self.texts[row][col])

    def testGetItemText(self):
        """Test the ListView GetItem method - with text this time"""
        for text in [row[0] for row in self.texts]:
            self.assertEquals(
                self.ctrl.GetItem(text)['text'], text)

        self.assertRaises(ValueError, self.ctrl.GetItem, "Item not in this list")

    def testColumn(self):
        """Test the ListView Columns method"""
        cols = self.ctrl.Columns()
        self.assertEqual(len(cols), self.ctrl.ColumnCount())

        # TODO: add more checking of column values
        #for col in cols:
        #    print(col)

    def testGetSelectionCount(self):
        """Test the ListView GetSelectedCount method"""
        self.assertEquals(self.ctrl.GetSelectedCount(), 0)

        self.ctrl.Select(1)
        self.ctrl.Select(6)

        self.assertEquals(self.ctrl.GetSelectedCount(), 2)


#    def testGetSelectionCount(self):
#        "Test the ListView GetSelectedCount method"
#
#        self.assertEquals(self.ctrl.GetSelectedCount(), 0)
#
#        self.ctrl.Select(1)
#        self.ctrl.Select(7)
#
#        self.assertEquals(self.ctrl.GetSelectedCount(), 2)

    def testIsSelected(self):
        """Test ListView IsSelected for some items"""
        # ensure that the item is not selected
        self.assertEquals(self.ctrl.IsSelected(1), False)

        # select an item
        self.ctrl.Select(1)

        # now ensure that the item is selected
        self.assertEquals(self.ctrl.IsSelected(1), True)

    def _testFocused(self):
        """Test checking the focus of some ListView items"""
        print("Select something quick!!")
        time.sleep(3)
        #self.ctrl.Select(1)

        print(self.ctrl.IsFocused(0))
        print(self.ctrl.IsFocused(1))
        print(self.ctrl.IsFocused(2))
        print(self.ctrl.IsFocused(3))
        print(self.ctrl.IsFocused(4))
        print(self.ctrl.IsFocused(5))
        #for col in cols:
        #    print(col)

    def testSelect(self):
        """Test ListView Selecting some items"""
        self.ctrl.Select(1)
        self.ctrl.Select(3)
        self.ctrl.Select(4)

        self.assertRaises(IndexError, self.ctrl.Deselect, 23)

        self.assertEquals(self.ctrl.GetSelectedCount(), 3)

    def testSelectText(self):
        """Test ListView Selecting some items"""
        self.ctrl.Select(u"Green")
        self.ctrl.Select(u"Yellow")
        self.ctrl.Select(u"Gray")

        self.assertRaises(ValueError, self.ctrl.Deselect, u"Item not in list")

        self.assertEquals(self.ctrl.GetSelectedCount(), 3)

    def testDeselect(self):
        """Test ListView Selecting some items"""
        self.ctrl.Select(1)
        self.ctrl.Select(4)

        self.ctrl.Deselect(3)
        self.ctrl.Deselect(4)

        self.assertRaises(IndexError, self.ctrl.Deselect, 23)

        self.assertEquals(self.ctrl.GetSelectedCount(), 1)

    def testGetProperties(self):
        """Test getting the properties for the listview control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            "ListView", props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props.keys():
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

        self.assertEquals(props['column_count'], 8)
        self.assertEquals(props['item_count'], 7)

    def testGetColumnTexts(self):
        """Test columns titles text"""
        self.assertEquals(self.ctrl.GetColumn(0)['text'], u"Color")
        self.assertEquals(self.ctrl.GetColumn(1)['text'], u"Red")
        self.assertEquals(self.ctrl.GetColumn(2)['text'], u"Green")
        self.assertEquals(self.ctrl.GetColumn(3)['text'], u"Blue")

    def testItemRectangles(self):
        """Test getting item rectangles"""
        yellow_rect = self.ctrl.GetItemRect('Yellow')
        gold_rect = RECT(13, 0, 61, 53)
        self.assertEquals(yellow_rect.left, gold_rect.left)
        self.assertEquals(yellow_rect.top, gold_rect.top)
        self.assertEquals(yellow_rect.right, gold_rect.right)
        if yellow_rect.bottom < 53 or yellow_rect.bottom > 55:
            self.assertEquals(yellow_rect.bottom, gold_rect.bottom)

        self.ctrl.GetItem('Green').Click(where='text')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)

        self.ctrl.GetItem('Magenta').Click(where='icon')
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), True)
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), False)

        self.ctrl.GetItem('Green').Click(where='all')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), False)

    def testItemCheck(self):
        """Test checking/unchecking item"""
        if not self.dlg.Toolbar.Button(6).IsChecked():
            self.dlg.Toolbar.Button(6).Click()

        yellow = self.ctrl.GetItem('Yellow')
        yellow.Check()
        self.assertEquals(yellow.IsChecked(), True)

        yellow.UnCheck()
        self.assertEquals(yellow.IsChecked(), False)

        # test legacy deprecated methods (TODO: remove later)
        self.ctrl.Check('Yellow')
        self.assertEquals(self.ctrl.IsChecked('Yellow'), True)

        self.ctrl.UnCheck('Yellow')
        self.assertEquals(self.ctrl.IsChecked('Yellow'), False)

    def testItemClick(self):
        """Test clicking item rectangles by Click() method"""
        self.ctrl.GetItem('Green').Click(where='select')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)

        self.ctrl.GetItem('Magenta').Click(where='select')
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), True)
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), False)
        self.assertEquals(self.ctrl.GetItem('Green').IsFocused(), False)
        self.assertEquals(self.ctrl.GetItem('Green').State() & win32defines.LVIS_FOCUSED, 0)

        self.ctrl.GetItem('Green').Click(where='select')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)
        self.assertEquals(self.ctrl.IsSelected('Green'), True)  # TODO: deprecated method
        self.assertEquals(self.ctrl.GetItem('Green').IsFocused(), True)
        self.assertEquals(self.ctrl.IsFocused('Green'), True)  # TODO: deprecated method
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), False)

        # Test click on checkboxes
        if not self.dlg.Toolbar.Button(6).IsChecked():  # switch on states
            self.dlg.Toolbar.Button(6).Click()

        for i in range(1, 6):
            self.dlg.Toolbar.Button(i - 1).Click()

            self.ctrl.GetItem(i).Click(where='check')  # check item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), True)
            self.assertEquals(self.ctrl.GetItem(i - 1).IsChecked(), False)

            self.ctrl.GetItem(i).Click(where='check')  # uncheck item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), False)

            self.ctrl.GetItem(i).Click(where='check')  # recheck item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), True)

        self.dlg.Toolbar.Button(6).Click()  # switch off states

        self.assertRaises(RuntimeError, self.ctrl.GetItem(6).Click, where="check")

    def testItemClickInput(self):
        """Test clicking item rectangles by click_input() method"""
        Timings.Defaults()

        self.ctrl.GetItem('Green').click_input(where='select')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)

        self.ctrl.GetItem('Magenta').click_input(where='select')
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), True)
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), False)
        self.assertEquals(self.ctrl.GetItem('Green').IsFocused(), False)
        self.assertEquals(self.ctrl.GetItem('Green').State() & win32defines.LVIS_FOCUSED, 0)

        self.ctrl.GetItem('Green').click_input(where='select')
        self.assertEquals(self.ctrl.GetItem('Green').IsSelected(), True)
        self.assertEquals(self.ctrl.IsSelected('Green'), True)  # TODO: deprecated method
        self.assertEquals(self.ctrl.GetItem('Green').IsFocused(), True)
        self.assertEquals(self.ctrl.IsFocused('Green'), True)  # TODO: deprecated method
        self.assertEquals(self.ctrl.GetItem('Magenta').IsSelected(), False)

        # Test click on checkboxes
        if not self.dlg.Toolbar.Button(6).IsChecked():  # switch on states
            self.dlg.Toolbar.Button(6).Click()

        for i in range(1, 6):
            self.dlg.Toolbar.Button(i - 1).Click()

            self.ctrl.GetItem(i).click_input(where='check')  # check item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), True)
            self.assertEquals(self.ctrl.GetItem(i - 1).IsChecked(), False)

            self.ctrl.GetItem(i).click_input(where='check')  # uncheck item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), False)

            self.ctrl.GetItem(i).click_input(where='check')  # recheck item
            time.sleep(0.5)
            self.assertEquals(self.ctrl.GetItem(i).IsChecked(), True)

        self.dlg.Toolbar.Button(6).Click()  # switch off states

        self.assertRaises(RuntimeError, self.ctrl.GetItem(6).click_input, where="check")

    def testItemMethods(self):
        """Test short item methods like Text(), State() etc"""
        self.assertEquals(self.ctrl.GetItem('Green').Text(), 'Green')
        self.assertEquals(self.ctrl.GetItem('Green').Image(), 2)
        self.assertEquals(self.ctrl.GetItem('Green').Indent(), 0)

    def test_ensure_visible(self):
        self.dlg.MoveWindow(width=300)

        # Gray is selected by click because ensure_visible() is called inside
        self.ctrl.GetItem('Gray').Click()
        self.assertEquals(self.ctrl.GetItem('Gray').IsSelected(), True)
        self.dlg.set_focus()  # just in case

        self.ctrl.GetItem('Green').EnsureVisible()
        self.ctrl.GetItem('Red').Click()
        self.assertEquals(self.ctrl.GetItem('Gray').IsSelected(), False)
        self.assertEquals(self.ctrl.GetItem('Red').IsSelected(), True)

#
#    def testSubItems(self):
#
#        for row in range(self.ctrl.ItemCount())
#
#        for i in self.ctrl.Items():
#
#            #self.assertEquals(item.Text, texts[i])

    def testEqualsItems(self):
        """
        Test __eq__ and __ne__ cases for _listview_item.
        """
        item1 = self.ctrl.GetItem(0, 0)
        item1_copy = self.ctrl.GetItem(0, 0)
        item2 = self.ctrl.GetItem(1, 0)

        self.assertEqual(item1, item1_copy)
        self.assertNotEqual(item1, "Not _listview_item")
        self.assertNotEqual(item1, item2)

    def test_cells_rectangles(self):
        """Test the ListView get_item rectangle method for cells"""
        if not self.dlg.Toolbar.Button(4).is_checked():
            self.dlg.Toolbar.Button(4).click()

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
        Timings.Defaults()

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
        Timings.Fast()

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
        self.ctrl = self.app.MicrosoftControlSpy.TreeView.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def test_friendly_class_name(self):
        """Make sure the friendly class name is set correctly (TreeView)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "TreeView")

    def testItemCount(self):
        """Test the TreeView ItemCount method"""
        self.assertEquals(self.ctrl.ItemCount(), 37)

    def testGetItem(self):
        """Test the GetItem method"""
        self.assertRaises(RuntimeError, self.ctrl.GetItem, "test\here\please")

        self.assertRaises(IndexError, self.ctrl.GetItem, r"\test\here\please")

        self.assertEquals(
            self.ctrl.GetItem((0, 1, 2)).Text(), self.texts[1][3] + " kg")

        self.assertEquals(
            self.ctrl.GetItem(r"\The Planets\Venus\4.869e24 kg", exact=True).Text(), self.texts[1][3] + " kg")

        self.assertEquals(
            self.ctrl.GetItem(["The Planets", "Venus", "4.869"]).Text(),
            self.texts[1][3] + " kg"
        )

    def testItemText(self):
        """Test the TreeView item Text() method"""
        self.assertEquals(self.ctrl.Root().Text(), self.root_text)

        self.assertEquals(
            self.ctrl.GetItem((0, 1, 2)).Text(), self.texts[1][3] + " kg")

    def testSelect(self):
        """Test selecting an item"""
        self.ctrl.Select((0, 1, 2))

        self.ctrl.GetItem((0, 1, 2)).State()

        self.assertEquals(True, self.ctrl.IsSelected((0, 1, 2)))

    def testEnsureVisible(self):
        """make sure that the item is visible"""
        # TODO: note this is partially a fake test at the moment because
        # just by getting an item - we usually make it visible
        self.ctrl.EnsureVisible((0, 8, 2))

        # make sure that the item is not hidden
        self.assertNotEqual(None, self.ctrl.GetItem((0, 8, 2)).client_rect())

    def testGetProperties(self):
        """Test getting the properties for the treeview control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            "TreeView", props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemsClick(self):
        """Test clicking of items and sub-items in the treeview control"""
        planets_item_path = (0, 0)
        mercury_diam_item_path = (0, 0, 1)
        mars_dist_item_path = (0, 3, 0)

        itm = self.ctrl.GetItem(planets_item_path)
        itm.EnsureVisible()
        time.sleep(1)
        itm.Click(button='left')
        self.assertEquals(True, self.ctrl.IsSelected(planets_item_path))

        itm = self.ctrl.GetItem(mars_dist_item_path)
        itm.EnsureVisible()
        time.sleep(1)
        itm.Click(button='left')
        self.assertEquals(True, self.ctrl.IsSelected(mars_dist_item_path))

        itm = self.ctrl.GetItem(mercury_diam_item_path)
        itm.EnsureVisible()
        time.sleep(1)
        itm.Click(button='left')
        self.assertEquals(True, self.ctrl.IsSelected(mercury_diam_item_path))
        self.assertEquals(False, self.ctrl.IsSelected(mars_dist_item_path))

        itm = self.ctrl.GetItem(planets_item_path)
        itm.EnsureVisible()
        time.sleep(1)
        itm.Click(button='left')
        self.assertEquals(True, self.ctrl.IsSelected(planets_item_path))
        self.assertEquals(False, self.ctrl.IsSelected(mercury_diam_item_path))


if is_x64_Python():

    class TreeViewTestCases64(TreeViewTestCases32):

        """Unit tests for the 64-bit TreeViewWrapper on a 32-bit sample"""

        path = os.path.join(controlspy_folder, "Tree View.exe")


class TreeViewAdditionalTestCases(unittest.TestCase):

    """More unit tests for the TreeViewWrapper class (CmnCtrl1.exe)"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.dlg = self.app.CommonControlsSample
        self.ctrl = self.app.CommonControlsSample.TreeView.WrapperObject()
        self.app.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1)

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)
        self.app.kill_()

    def testCheckBoxes(self):
        """Make sure tree view item method IsChecked() works as expected"""
        self.dlg.set_focus()
        self.dlg.TVS_CHECKBOXES.check_by_click()
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Click(where='check')
        self.assertEqual(birds.IsChecked(), True)
        birds.click_input(where='check')
        wait_until(3, 0.4, birds.IsChecked, value=False)

    def testPrintItems(self):
        """Test TreeView method PrintItems()"""
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        items_str = self.ctrl.PrintItems()
        self.assertEquals(items_str, "Treeview1\nBirds\n Eagle\n Hummingbird\n Pigeon\n" +
                                     "Dogs\n Dalmatian\n German Shepherd\n Great Dane\n" +
                                     "Fish\n Salmon\n Snapper\n Sole\n")

    def testIsSelected(self):
        """Make sure tree view item method IsSelected() works as expected"""
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        eagle = self.ctrl.GetItem(r'\Birds\Eagle')
        eagle.Select()
        self.assertEquals(eagle.IsSelected(), True)

    def test_expand_collapse(self):
        """Make sure tree view item methods Expand() and Collapse() work as expected"""
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        self.assertEquals(birds.IsExpanded(), True)

        birds.Collapse()
        self.assertEquals(birds.IsExpanded(), False)

    def test_expand_collapse_buttons(self):
        """Make sure correct area is clicked"""
        self.dlg.TVS_HASBUTTONS.click_input()
        self.dlg.TVS_HASLINES.click_input()
        self.dlg.TVS_LINESATROOT.click_input()
        birds = self.ctrl.GetItem(r'\Birds')

        birds.Click(where='button')
        self.assertEquals(birds.IsExpanded(), True)
        birds.Click(double=True, where='icon')
        self.assertEquals(birds.IsExpanded(), False)

        birds.click_input(where='button')
        self.assertEquals(birds.IsExpanded(), True)
        birds.click_input(double=True, where='icon')
        self.assertEquals(birds.IsExpanded(), False)

    def testIncorrectAreas(self):
        """Make sure incorrect area raises an exception"""
        birds = self.ctrl.GetItem(r'\Birds')
        self.assertRaises(RuntimeError, birds.Click, where='radiob')
        self.assertRaises(RuntimeError, birds.click_input, where='radiob')

    def testStartDraggingAndDrop(self):
        """Make sure tree view item methods StartDragging() and Drop() work as expected"""
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()

        pigeon = self.ctrl.GetItem(r'\Birds\Pigeon')
        pigeon.StartDragging()

        eagle = self.ctrl.GetItem(r'\Birds\Eagle')
        eagle.Drop()

        self.assertRaises(IndexError, birds.GetChild, 'Pigeon')
        self.assertRaises(IndexError, self.ctrl.GetItem, r'\Birds\Pigeon')
        self.assertRaises(IndexError, self.ctrl.GetItem, [0, 2])
        self.assertRaises(IndexError, self.ctrl.GetItem, r'\Bread', exact=True)

        new_pigeon = self.ctrl.GetItem(r'\Birds\Eagle\Pigeon')
        self.assertEquals(len(birds.children()), 2)
        self.assertEquals(new_pigeon.children(), [])


class HeaderTestCases(unittest.TestCase):

    """Unit tests for the Header class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

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
        self.ctrl = app.RowListSampleApplication.Header.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (Header)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "Header")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEquals(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the header control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        self.assertEquals(8, self.ctrl.ItemCount())

    def testGetColumnRectangle(self):
        for i in range(0, 3):
            self.assertEquals(self.item_rects[i].left, self.ctrl.GetColumnRectangle(i).left)
            self.assertEquals(self.item_rects[i].right, self.ctrl.GetColumnRectangle(i).right)
            self.assertEquals(self.item_rects[i].top, self.ctrl.GetColumnRectangle(i).top)
            self.failIf(abs(self.item_rects[i].bottom - self.ctrl.GetColumnRectangle(i).bottom) > 2)

    def testClientRects(self):
        test_rects = self.item_rects
        test_rects.insert(0, self.ctrl.client_rect())

        client_rects = self.ctrl.client_rects()
        self.assertEquals(len(test_rects), len(client_rects))
        for i, r in enumerate(test_rects):
            self.assertEquals(r.left, client_rects[i].left)
            self.assertEquals(r.right, client_rects[i].right)
            self.assertEquals(r.top, client_rects[i].top)
            self.failIf(abs(r.bottom - client_rects[i].bottom) > 2)  # may be equal to 17 or 19

    def testGetColumnText(self):
        for i in range(0, 3):
            self.assertEquals(
                self.texts[i],
                self.ctrl.GetColumnText(i))


class StatusBarTestCases(unittest.TestCase):

    """Unit tests for the TreeViewWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        app = Application()
        app.start(os.path.join(controlspy_folder, "Status bar.exe"))

        self.texts = ["Long text", "", "Status Bar"]
        self.part_rects = [
            RECT(0, 2, 65, 22),
            RECT(67, 2, 90, 22),
            RECT(92, 2, 261, 22)]
        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.StatusBar.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def test_friendly_class_name(self):
        """Make sure the friendly class name is set correctly (StatusBar)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "StatusBar")

    def test_texts(self):
        """Make sure the texts are set correctly"""
        self.assertEquals(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the status bar control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testBorderWidths(self):
        """Make sure the border widths are retrieved correctly"""
        self.assertEquals(
            self.ctrl.BorderWidths(),
            dict(
                Horizontal=0,
                Vertical=2,
                Inter=2,
            )
        )

    def testPartCount(self):
        "Make sure the number of parts is retrieved correctly"
        self.assertEquals(self.ctrl.PartCount(), 3)

    def testPartRightEdges(self):
        "Make sure the part widths are retrieved correctly"

        for i in range(0, self.ctrl.PartCount() - 1):
            self.assertEquals(self.ctrl.PartRightEdges()[i], self.part_rects[i].right)

        self.assertEquals(self.ctrl.PartRightEdges()[i + 1], -1)

    def testGetPartRect(self):
        "Make sure the part rectangles are retrieved correctly"

        for i in range(0, self.ctrl.PartCount()):
            part_rect = self.ctrl.GetPartRect(i)
            self.assertEquals(part_rect.left, self.part_rects[i].left)
            if i != self.ctrl.PartCount() - 1:
                self.assertEquals(part_rect.right, self.part_rects[i].right)
            self.assertEquals(part_rect.top, self.part_rects[i].top)
            self.failIf(abs(part_rect.bottom - self.part_rects[i].bottom) > 2)

        self.assertRaises(IndexError, self.ctrl.GetPartRect, 99)

    def testClientRects(self):
        self.assertEquals(self.ctrl.ClientRect(), self.ctrl.ClientRects()[0])
        client_rects = self.ctrl.ClientRects()[1:]
        for i, client_rect in enumerate(client_rects):
            self.assertEquals(self.part_rects[i].left, client_rect.left)
            if i != len(client_rects) - 1:
                self.assertEquals(self.part_rects[i].right, client_rect.right)
            self.assertEquals(self.part_rects[i].top, client_rect.top)
            self.failIf(abs(self.part_rects[i].bottom - client_rect.bottom) > 2)

    def testGetPartText(self):
        self.assertRaises(IndexError, self.ctrl.GetPartText, 99)

        for i, text in enumerate(self.texts):
            self.assertEquals(text, self.ctrl.GetPartText(i))


class TabControlTestCases(unittest.TestCase):

    """Unit tests for the TreeViewWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()
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
        self.ctrl = app.CommonControlsSample.TabControl.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (TabControl)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "TabControl")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEquals(self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        """Test getting the properties for the tabcontrol"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testRowCount(self):
        self.assertEquals(1, self.ctrl.RowCount())

        dlgClientRect = self.ctrl.parent().rectangle()  # use the parent as a reference
        prev_rect = self.ctrl.rectangle() - dlgClientRect

        # squeeze the tab control to force two rows
        new_rect = RECT(prev_rect)
        new_rect.right = int(new_rect.width() / 2)

        self.ctrl.MoveWindow(
            new_rect.left,
            new_rect.top,
            new_rect.width(),
            new_rect.height(),
        )
        time.sleep(0.1)

        # verify two tab rows
        self.assertEquals(2, self.ctrl.RowCount())

        # restore back the original size of the control
        self.ctrl.MoveWindow(prev_rect)
        self.assertEquals(1, self.ctrl.RowCount())

    def testGetSelectedTab(self):
        self.assertEquals(0, self.ctrl.GetSelectedTab())
        self.ctrl.Select(1)
        self.assertEquals(1, self.ctrl.GetSelectedTab())
        self.ctrl.Select(u"CMonthCalCtrl")
        self.assertEquals(4, self.ctrl.GetSelectedTab())

    def testTabCount(self):
        """Make sure the number of parts is retrieved correctly"""
        self.assertEquals(self.ctrl.TabCount(), 5)

    def testGetTabRect(self):
        """Make sure the part rectangles are retrieved correctly"""
        for i, _ in enumerate(self.rects):
            self.assertEquals(self.ctrl.GetTabRect(i), self.rects[i])

        self.assertRaises(IndexError, self.ctrl.GetTabRect, 99)

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
#        self.assertEquals(self.ctrl.GetTabState(1), 1)
#
#    def testTabStates(self):
#        print(self.ctrl.TabStates())
#        raise "tabstates hiay"

    def testGetTabText(self):
        for i, text in enumerate(self.texts):
            self.assertEquals(text, self.ctrl.GetTabText(i))

        self.assertRaises(IndexError, self.ctrl.GetTabText, 99)

    def testClientRects(self):
        self.assertEquals(self.ctrl.client_rect(), self.ctrl.client_rects()[0])
        self.assertEquals(self.rects, self.ctrl.client_rects()[1:])

    def testSelect(self):
        self.assertEquals(0, self.ctrl.GetSelectedTab())

        self.ctrl.Select(1)
        self.assertEquals(1, self.ctrl.GetSelectedTab())
        self.ctrl.Select(u"CToolBarCtrl")
        self.assertEquals(2, self.ctrl.GetSelectedTab())

        self.assertRaises(IndexError, self.ctrl.Select, 99)


class ToolbarTestCases(unittest.TestCase):

    """Unit tests for the ToolbarWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.app = app
        self.dlg = app.CommonControlsSample

        # select a tab with toolbar controls
        self.dlg.SysTabControl.Select(u"CToolBarCtrl")

        # see identifiers available at that tab
        #self.dlg.PrintControlIdentifiers()

        # The sample app has two toolbars. The first toolbar can be
        # addressed as Toolbar, Toolbar0 and Toolbar1.
        # The second control goes as Toolbar2
        self.ctrl = app.CommonControlsSample.ToolbarNew.WrapperObject()
        self.ctrl2 = app.CommonControlsSample.ToolbarErase.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (Toolbar)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "Toolbar")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        for txt in self.ctrl.texts():
            self.assertEquals(isinstance(txt, six.string_types), True)

    def testGetProperties(self):
        """Test getting the properties for the toolbar control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        self.assertEquals(
            self.ctrl.ButtonCount(), props['button_count'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testButtonCount(self):
        """Test the button count method of the toolbar"""
        # TODO: for a some reason the first toolbar returns button count = 12
        # The same as in the second toolbar, even though their handles are different.
        # Maybe the test app itself has to be fixed too.
        #self.assertEquals(self.ctrl.ButtonCount(), 9)

        self.assertEquals(self.ctrl2.ButtonCount(), 12)

    def testGetButton(self):
        self.assertRaises(IndexError, self.ctrl.GetButton, 29)

    def testGetButtonRect(self):
        rect_ctrl = self.ctrl.GetButtonRect(0)
        self.assertEquals((rect_ctrl.left, rect_ctrl.top), (0, 0))
        self.failIf((rect_ctrl.right - rect_ctrl.left) > 40)
        self.failIf((rect_ctrl.right - rect_ctrl.left) < 36)
        self.failIf((rect_ctrl.bottom - rect_ctrl.top) > 38)
        self.failIf((rect_ctrl.bottom - rect_ctrl.top) < 36)
        #self.assertEquals(rect_ctrl, RECT(0, 0, 40, 38))

        rect_ctrl2 = self.ctrl2.GetButtonRect(0)
        self.assertEquals((rect_ctrl2.left, rect_ctrl2.top), (0, 0))
        self.failIf((rect_ctrl2.right - rect_ctrl2.left) > 70)
        self.failIf((rect_ctrl2.right - rect_ctrl2.left) < 64)
        self.failIf((rect_ctrl2.bottom - rect_ctrl2.top) > 38)
        self.failIf((rect_ctrl2.bottom - rect_ctrl2.top) < 36)
        #self.assertEquals(rect_ctrl2, RECT(0, 0, 70, 38))

    def testGetToolTipsControls(self):
        tips = self.ctrl.GetToolTipsControl()
        tt = tips.texts()
        self.assertEquals(u"New" in tt, True)
        self.assertEquals(u"About" in tt, True)

        tips = self.ctrl2.GetToolTipsControl()
        tt = tips.texts()
        self.assertEquals(u"Pencil" in tt, True)
        self.assertEquals(u"Ellipse" in tt, True)

    def testPressButton(self):

        self.ctrl.PressButton(0)

        #print(self.ctrl.texts())
        self.assertRaises(
            findbestmatch.MatchError,
            self.ctrl.PressButton,
            "asdfdasfasdf")

        # todo more tests for pressbutton
        self.ctrl.PressButton(u"Open")

    def testCheckButton(self):
        self.ctrl2.CheckButton('Erase', True)
        self.assertEquals(self.ctrl2.Button('Erase').IsChecked(), True)

        self.ctrl2.CheckButton('Pencil', True)
        self.assertEquals(self.ctrl2.Button('Erase').IsChecked(), False)

        self.ctrl2.CheckButton('Erase', False)
        self.assertEquals(self.ctrl2.Button('Erase').IsChecked(), False)

        # try to check separator
        self.assertRaises(RuntimeError, self.ctrl.CheckButton, 3, True)

    def testIsCheckable(self):
        self.assertNotEqual(self.ctrl2.Button('Erase').IsCheckable(), False)
        self.assertEquals(self.ctrl.Button('New').IsCheckable(), False)

    def testIsPressable(self):
        self.assertEquals(self.ctrl.Button('New').IsPressable(), True)

    def testButtonByTooltip(self):
        self.assertEquals(self.ctrl.Button('New', by_tooltip=True).Text(), 'New')
        self.assertEquals(self.ctrl.Button('About', exact=False, by_tooltip=True).Text(), 'About')


class RebarTestCases(unittest.TestCase):

    """Unit tests for the UpDownWrapper class"""

    def setUp(self):
        """Start the application, set some data and wait for the state we want

        The app title can be tricky. If no document is opened the title is just: "RebarTest"
        However if an document is created/opened in the child frame
        the title is appended with a document name: "RebarTest - RebarTest1"
        A findbestmatch proc does well here with guessing the title
        even though the app is started with a short title "RebarTest".
        """
        Timings.Fast()
        app = Application()
        app.start(os.path.join(mfc_samples_folder, "RebarTest.exe"))
        mouse.move((-500, 200))  # remove the mouse from the screen to avoid side effects
        self.app = app
        self.dlg = app.RebarTest_RebarTest
        self.dlg.Wait('ready', 20)
        self.ctrl = app.RebarTest_RebarTest.Rebar.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.app.kill()

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ReBar)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "ReBar")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        for txt in self.ctrl.texts():
            self.assertEquals(isinstance(txt, six.string_types), True)

    def testBandCount(self):
        """Make sure BandCount() returns 2"""
        self.assertEquals(self.ctrl.BandCount(), 2)

    def testGetBand(self):
        """Check that GetBand() is working corectly"""
        self.assertRaises(IndexError, self.ctrl.GetBand, 99)
        self.assertRaises(IndexError, self.ctrl.GetBand, 2)

        band = self.ctrl.GetBand(0)

        self.assertEquals(band.hwndChild, self.dlg.MenuBar.handle)

        self.assertEquals(self.ctrl.GetBand(1).text, u"Tools band:")
        self.assertEquals(self.ctrl.GetBand(0).text, u"Menus band:")

    def testGetToolTipsControl(self):
        """Make sure GetToolTipsControl() returns None"""
        self.assertEquals(self.ctrl.GetToolTipsControl(), None)

    def testAfxToolBarButtons(self):
        """Make sure we can click on Afx ToolBar button by index"""
        Timings.closeclick_dialog_close_wait = 2.
        self.dlg.StandardToolbar.Button(1).Click()
        self.app.Window_(title='Open').Wait('ready', timeout=30)
        self.app.Window_(title='Open').Cancel.CloseClick()

    def testMenuBarClickInput(self):
        """Make sure we can click on Menu Bar items by indexed path"""
        self.assertRaises(TypeError, self.dlg.MenuBar.MenuBarClickInput, '#one->#0', self.app)

        self.dlg.MenuBar.MenuBarClickInput('#1->#0->#0', self.app)
        self.app.Customize.CloseButton.Click()
        self.app.Customize.WaitNot('visible')

        self.dlg.MenuBar.MenuBarClickInput([2, 0], self.app)
        self.app.Window_(title='About RebarTest').OK.Click()
        self.app.Window_(title='About RebarTest').WaitNot('visible')


class DatetimeTestCases(unittest.TestCase):

    """Unit tests for the DateTimePicker class"""

    def setUp(self):
        """Start the application and get 'Date Time Picker' control"""
        Timings.Fast()
        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.app = app
        self.dlg = app.CommonControlsSample
        self.dlg.Wait('ready', 20)
        tab = app.CommonControlsSample.TabControl.WrapperObject()
        tab.Select(3)
        self.ctrl = self.dlg.DateTimePicker

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (DateTimePicker)"""
        self.assertEqual(self.ctrl.friendly_class_name(), "DateTimePicker")

    def testGetTime(self):
        """Test reading a date from a 'Date Time Picker' control"""

        # No check for seconds and milliseconds as it can slip
        # These values are verified in the next 'testSetTime'
        test_date_time = self.ctrl.GetTime()
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
        self.ctrl.SetTime(
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
        test_date_time = self.ctrl.GetTime()
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
        Timings.Fast()
        self.texts = [u'', u'New', u'Open', u'Save', u'Cut', u'Copy', u'Paste', u'Print', u'About', u'Help']

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))
        #app.start_(os.path.join(controlspy_folder, "Tooltip.exe"))

        self.app = app
        self.dlg = app.Common_Controls_Sample

        # Make sure the mouse doesn't hover over tested controls
        # so it won't generate an unexpected tooltip
        self.dlg.move_mouse_input(coords=(-100, -100), absolute=True)

        self.dlg.TabControl.Select(u'CToolBarCtrl')

        self.ctrl = self.dlg.Toolbar.GetToolTipsControl()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.app.kill_()

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ToolTips)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "ToolTips")

    def testGetProperties(self):
        """Test getting the properties for the tooltips control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetTip(self):
        """Test that GetTip() returns correct ToolTip object"""
        self.assertRaises(IndexError, self.ctrl.GetTip, 99)
        tip = self.ctrl.GetTip(1)
        self.assertEquals(tip.text, self.texts[1])

    def testToolCount(self):
        """Test that ToolCount() returns correct value"""
        self.assertEquals(10, self.ctrl.ToolCount())

    def testGetTipText(self):
        """Test that GetTipText() returns correct text"""
        self.assertEquals(self.texts[1], self.ctrl.GetTipText(1))

    def testTexts(self):
        """Make sure the texts are set correctly"""
        # just to make sure a tooltip is not shown
        self.dlg.move_mouse_input(coords=(0, 0), absolute=False)
        ActionLogger().log('ToolTips texts = ' + ';'.join(self.ctrl.texts()))
        self.assertEquals(self.ctrl.texts()[0], '')
        self.assertEquals(self.ctrl.texts()[1:], self.texts)


class UpDownTestCases(unittest.TestCase):

    """Unit tests for the UpDownWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()
        app = Application()
        app.start(os.path.join(controlspy_folder, "Up-Down.exe"))

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.UpDown2.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (UpDown)"""
        self.assertEquals(self.ctrl.friendly_class_name(), "UpDown")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEquals(self.ctrl.texts()[1:], [])

    def testGetProperties(self):
        """Test getting the properties for the updown control"""
        props = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetValue(self):
        """Test getting up-down position"""
        self.assertEquals(self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals(self.ctrl.GetValue(), 23)

    def testSetValue(self):
        """Test setting up-down position"""
        self.assertEquals(self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals(self.ctrl.GetValue(), 23)
        self.assertEquals(
            int(self.ctrl.GetBuddyControl().texts()[1]),
            23)

    def testGetBase(self):
        """Test getting the base of the up-down control"""
        self.assertEquals(self.ctrl.GetBase(), 10)
        #self.dlg.StatementEdit.SetEditText ("MSG (UDM_SETBASE, 16, 0)")

        # use CloseClick to allow the control time to respond to the message
        #self.dlg.Send.click_input()
        self.ctrl.SetBase(16)

        self.assertEquals(self.ctrl.GetBase(), 16)

    def testGetRange(self):
        """Test getting the range of the up-down control"""
        self.assertEquals((0, 9999), self.ctrl.GetRange())

    def testGetBuddy(self):
        """Test getting the buddy control"""
        self.assertEquals(self.ctrl.GetBuddyControl().handle, self.dlg.Edit6.handle)

    def testIncrement(self):
        """Test incremementing up-down position"""
        Timings.Defaults()
        self.ctrl.Increment()
        self.assertEquals(self.ctrl.GetValue(), 1)

    def testDecrement(self):
        """Test decrementing up-down position"""
        Timings.Defaults()
        self.ctrl.SetValue(23)
        self.ctrl.Decrement()
        self.assertEquals(self.ctrl.GetValue(), 22)


class TrackbarWrapperTestCases(unittest.TestCase):

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        app = Application()
        app.start(os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"))
        dlg = app.top_window()
        dlg.TabControl.Select(1)

        ctrl = dlg.Trackbar.WrapperObject()
        self.app = app
        self.dlg = dlg
        self.ctrl = ctrl

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.send_message(win32defines.WM_CLOSE)

    def test_friendly_class(self):
        """Make sure the Trackbar friendly class is set correctly"""
        self.assertEquals(self.ctrl.friendly_class_name(), u"Trackbar")

    def test_get_range_max(self):
        """Test the get_range_max method"""
        self.ctrl.set_range_max(100)
        self.assertEquals(self.ctrl.get_range_max(), 100)

    def test_get_range_min(self):
        """Test the get_range_min method"""
        self.ctrl.set_range_min(25)
        self.assertEquals(self.ctrl.get_range_min(), 25)

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
        self.assertEquals(self.ctrl.get_line_size(), 10)

    def test_get_page_size(self):
        """Test the set_page_size method"""
        self.ctrl.set_page_size(14)
        self.assertEquals(self.ctrl.get_page_size(), 14)

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
