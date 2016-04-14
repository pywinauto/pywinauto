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

from __future__ import print_function

"Tests for classes in controls\common_controls.py"

import sys
#import ctypes
import unittest
import time
from datetime import datetime
#import pdb
import os
import win32api

sys.path.append(".")
from pywinauto.application import Application
from pywinauto import six
from pywinauto.win32structures import RECT
from pywinauto import win32defines
from pywinauto import findbestmatch
from pywinauto.sysinfo import is_x64_Python
from pywinauto.RemoteMemoryBlock import AccessDenied
from pywinauto.RemoteMemoryBlock import RemoteMemoryBlock
from pywinauto.actionlogger import ActionLogger
from pywinauto import backend
from pywinauto.timings import Timings
Timings.Defaults()


controlspy_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\controlspy0998")
controlspy_folder_32 = controlspy_folder
mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
mfc_samples_folder_32 = mfc_samples_folder
if is_x64_Python():
    controlspy_folder = os.path.join(controlspy_folder, 'x64')
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')


class RemoteMemoryBlockTestCases(unittest.TestCase):
    def test__init__fail(self):
        self.assertRaises(AttributeError, RemoteMemoryBlock, 0)


class TestConfigListView:
    def __init__(self, path):
        self.path = path

    def preprocessing(self):
        self.app = Application()
        self.app.start(self.path)
        self.dlg = self.app.RowListSampleApplication
        self.ctrl = self.app.RowListSampleApplication.ListView.WrapperObject()
        self.dlg.Toolbar.Button(0).Click() # switch to icon view
        self.dlg.Toolbar.Button(6).Click() # switch off states


class ListViewTestCases(unittest.TestCase):
    "Unit tests for the ListViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.texts = [
            (u"Yellow",  u"255", u"255", u"0",   u"40",  u"240", u"120", u"Neutral"),
            (u"Red",     u"255", u"0",   u"0",   u"0",   u"240", u"120", u"Warm"),
            (u"Green",   u"0",   u"255", u"0",   u"80",  u"240", u"120", u"Cool"),
            (u"Magenta", u"255", u"0",   u"255", u"200", u"240", u"120", u"Warm"),
            (u"Cyan",    u"0",   u"255", u"255", u"120", u"240", u"120", u"Cool"),
            (u"Blue",    u"0",   u"0",   u"255", u"160", u"240", u"120", u"Cool"),
            (u"Gray",    u"192", u"192", u"192", u"160", u"0",   u"181", u"Neutral")
        ]

        if is_x64_Python():
            self.test_configs = [TestConfigListView(os.path.join(mfc_samples_folder, u"RowList.exe")),
                                 TestConfigListView(os.path.join(mfc_samples_folder_32, u"RowList.exe"))]

        else:
            self.test_configs = [TestConfigListView(os.path.join(mfc_samples_folder, u"RowList.exe"))]
        

    def tearDown(self):
        "Close the application after tests"
        # close the application
        for test_config in self.test_configs:
            test_config.dlg.SendMessage(win32defines.WM_CLOSE)


    def testFriendlyClass(self):
        "Make sure the ListView friendly class is set correctly"
        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals (test_config.ctrl.friendly_class_name(), u"ListView")

    def testColumnCount(self):
        "Test the ListView ColumnCount method"
        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals (test_config.ctrl.ColumnCount(), 8)

    def testItemCount(self):
        "Test the ListView ItemCount method"
        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals (test_config.ctrl.ItemCount(), 7)

    def testItemText(self):
        "Test the ListView item.Text property"
        for test_config in self.test_configs:
            test_config.preprocessing()
            item = test_config.ctrl.GetItem(1)

            self.assertEquals(item['text'], u"Red")

    def testItems(self):
        "Test the ListView Items method"

        for test_config in self.test_configs:
            test_config.preprocessing()

            flat_texts = []
            for row in self.texts:
                flat_texts.extend(row)

            items = test_config.ctrl.Items()
            for i, item in enumerate(items):
                self.assertEquals(item['text'], flat_texts[i])
            self.assertEquals(len(items), len(flat_texts))

    def testTexts(self):
        "Test the ListView texts method"

        for test_config in self.test_configs:
            test_config.preprocessing()
            flat_texts = []
            for row in self.texts:
                flat_texts.extend(row)

            self.assertEquals(flat_texts, test_config.ctrl.texts()[1:])


    def testGetItem(self):
        "Test the ListView GetItem method"

        for test_config in self.test_configs:
            test_config.preprocessing()
            for row in range(test_config.ctrl.ItemCount()):
                for col in range(test_config.ctrl.ColumnCount()):
                    self.assertEquals(
                        test_config.ctrl.GetItem(row, col)['text'], self.texts[row][col])

    def testGetItemText(self):
        "Test the ListView GetItem method - with text this time"

        for test_config in self.test_configs:
            test_config.preprocessing()
            for text in [row[0] for row in self.texts]:
                self.assertEquals(
                    test_config.ctrl.GetItem(text)['text'], text)

            self.assertRaises(ValueError, test_config.ctrl.GetItem, "Item not in this list")

    def testColumn(self):
        "Test the ListView Columns method"

        for test_config in self.test_configs:
            test_config.preprocessing()
            cols = test_config.ctrl.Columns()
            self.assertEqual (len(cols), test_config.ctrl.ColumnCount())

            # TODO: add more checking of column values
            #for col in cols:
            #    print(col)


    def testGetSelectionCount(self):
        "Test the ListView GetSelectedCount method"

        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals(test_config.ctrl.GetSelectedCount(), 0)

            test_config.ctrl.Select(1)
            test_config.ctrl.Select(6)

            self.assertEquals(test_config.ctrl.GetSelectedCount(), 2)


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
        "Test ListView IsSelected for some items"

        for test_config in self.test_configs:
            test_config.preprocessing()
            # ensure that the item is not selected
            self.assertEquals(test_config.ctrl.IsSelected(1), False)

            # select an item
            test_config.ctrl.Select(1)

            # now ensure that the item is selected
            self.assertEquals(test_config.ctrl.IsSelected(1), True)


    def _testFocused(self):
        "Test checking the focus of some ListView items"

        for test_config in self.test_configs:
            test_config.preprocessing()
            print("Select something quick!!")
            time.sleep(3)
            #self.ctrl.Select(1)

            print(test_config.ctrl.IsFocused(0))
            print(test_config.ctrl.IsFocused(1))
            print(test_config.ctrl.IsFocused(2))
            print(test_config.ctrl.IsFocused(3))
            print(test_config.ctrl.IsFocused(4))
            print(test_config.ctrl.IsFocused(5))
            #for col in cols:
            #    print(col)


    def testSelect(self):
        "Test ListView Selecting some items"

        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.ctrl.Select(1)
            test_config.ctrl.Select(3)
            test_config.ctrl.Select(4)

            self.assertRaises(IndexError, test_config.ctrl.Deselect, 23)

            self.assertEquals(test_config.ctrl.GetSelectedCount(), 3)


    def testSelectText(self):
        "Test ListView Selecting some items"

        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.ctrl.Select(u"Green")
            test_config.ctrl.Select(u"Yellow")
            test_config.ctrl.Select(u"Gray")

            self.assertRaises(ValueError, test_config.ctrl.Deselect, u"Item not in list")

            self.assertEquals(test_config.ctrl.GetSelectedCount(), 3)



    def testDeselect(self):
        "Test ListView Selecting some items"

        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.ctrl.Select(1)
            test_config.ctrl.Select(4)

            test_config.ctrl.Deselect(3)
            test_config.ctrl.Deselect(4)

            self.assertRaises(IndexError, test_config.ctrl.Deselect, 23)

            self.assertEquals(test_config.ctrl.GetSelectedCount(), 1)




    def testGetProperties(self):
        "Test getting the properties for the listview control"

        for test_config in self.test_configs:
            test_config.preprocessing()
            props  = test_config.ctrl.GetProperties()

            self.assertEquals(
                "ListView", props['friendly_class_name'])

            self.assertEquals(
                test_config.ctrl.texts(), props['texts'])

            for prop_name in props.keys():
                self.assertEquals(getattr(test_config.ctrl, prop_name)(), props[prop_name])

            self.assertEquals(props['column_count'], 8)
            self.assertEquals(props['item_count'], 7)


    def testGetColumnTexts(self):
        "Test columns titles text"

        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals(test_config.ctrl.GetColumn(0)['text'], u"Color")
            self.assertEquals(test_config.ctrl.GetColumn(1)['text'], u"Red")
            self.assertEquals(test_config.ctrl.GetColumn(2)['text'], u"Green")
            self.assertEquals(test_config.ctrl.GetColumn(3)['text'], u"Blue")


    def testItemRectangles(self):
        "Test getting item rectangles"
        
        for test_config in self.test_configs:
            test_config.preprocessing()
            yellow_rect = test_config.ctrl.GetItemRect('Yellow')
            gold_rect = RECT(13, 0, 61, 53)
            self.assertEquals(yellow_rect.left, gold_rect.left)
            self.assertEquals(yellow_rect.top, gold_rect.top)
            self.assertEquals(yellow_rect.right, gold_rect.right)
            if yellow_rect.bottom < 53 or yellow_rect.bottom > 55:
                self.assertEquals(yellow_rect.bottom, gold_rect.bottom)

            test_config.ctrl.GetItem('Green').Click(where='text')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)

            test_config.ctrl.GetItem('Magenta').Click(where='icon')
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), True)
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), False)

            test_config.ctrl.GetItem('Green').Click(where='all')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), False)


    def testItemCheck(self):
        "Test checking/unchecking item"

        for test_config in self.test_configs:
            test_config.preprocessing()
            if not test_config.dlg.Toolbar.Button(6).IsChecked():
                test_config.dlg.Toolbar.Button(6).Click()

            yellow = test_config.ctrl.GetItem('Yellow')
            yellow.Check()
            self.assertEquals(yellow.IsChecked(), True)

            yellow.UnCheck()
            self.assertEquals(yellow.IsChecked(), False)

            # test legacy deprecated methods (TODO: remove later)
            test_config.ctrl.Check('Yellow')
            self.assertEquals(test_config.ctrl.IsChecked('Yellow'), True)

            test_config.ctrl.UnCheck('Yellow')
            self.assertEquals(test_config.ctrl.IsChecked('Yellow'), False)


    def testItemClick(self):
        "Test clicking item rectangles by Click() method"

        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.ctrl.GetItem('Green').Click(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)

            test_config.ctrl.GetItem('Magenta').Click(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), True)
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), False)
            self.assertEquals(test_config.ctrl.GetItem('Green').IsFocused(), False)
            self.assertEquals(test_config.ctrl.GetItem('Green').State() & win32defines.LVIS_FOCUSED, 0)

            test_config.ctrl.GetItem('Green').Click(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)
            self.assertEquals(test_config.ctrl.IsSelected('Green'), True) # TODO: deprecated method
            self.assertEquals(test_config.ctrl.GetItem('Green').IsFocused(), True)
            self.assertEquals(test_config.ctrl.IsFocused('Green'), True) # TODO: deprecated method
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), False)

            # Test click on checkboxes
            if not test_config.dlg.Toolbar.Button(6).IsChecked(): # switch on states
                test_config.dlg.Toolbar.Button(6).Click()

            for i in range(1, 6):
                test_config.dlg.Toolbar.Button(i - 1).Click()

                test_config.ctrl.GetItem(i).Click(where='check') # check item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), True)
                self.assertEquals(test_config.ctrl.GetItem(i - 1).IsChecked(), False)

                test_config.ctrl.GetItem(i).Click(where='check') # uncheck item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), False)

                test_config.ctrl.GetItem(i).Click(where='check') # recheck item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), True)

            test_config.dlg.Toolbar.Button(6).Click() # switch off states

            self.assertRaises(RuntimeError, test_config.ctrl.GetItem(6).Click, where="check")


    def testItemClickInput(self):
        "Test clicking item rectangles by click_input() method"
        
        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.ctrl.GetItem('Green').click_input(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)

            test_config.ctrl.GetItem('Magenta').click_input(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), True)
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), False)
            self.assertEquals(test_config.ctrl.GetItem('Green').IsFocused(), False)
            self.assertEquals(test_config.ctrl.GetItem('Green').State() & win32defines.LVIS_FOCUSED, 0)

            test_config.ctrl.GetItem('Green').click_input(where='select')
            self.assertEquals(test_config.ctrl.GetItem('Green').IsSelected(), True)
            self.assertEquals(test_config.ctrl.IsSelected('Green'), True) # TODO: deprecated method
            self.assertEquals(test_config.ctrl.GetItem('Green').IsFocused(), True)
            self.assertEquals(test_config.ctrl.IsFocused('Green'), True) # TODO: deprecated method
            self.assertEquals(test_config.ctrl.GetItem('Magenta').IsSelected(), False)

            # Test click on checkboxes
            if not test_config.dlg.Toolbar.Button(6).IsChecked(): # switch on states
                test_config.dlg.Toolbar.Button(6).Click()

            for i in range(1, 6):
                test_config.dlg.Toolbar.Button(i - 1).Click()

                test_config.ctrl.GetItem(i).click_input(where='check') # check item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), True)
                self.assertEquals(test_config.ctrl.GetItem(i - 1).IsChecked(), False)

                test_config.ctrl.GetItem(i).click_input(where='check') # uncheck item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), False)

                test_config.ctrl.GetItem(i).click_input(where='check') # recheck item
                time.sleep(0.5)
                self.assertEquals(test_config.ctrl.GetItem(i).IsChecked(), True)

            test_config.dlg.Toolbar.Button(6).Click() # switch off states

            self.assertRaises(RuntimeError, test_config.ctrl.GetItem(6).click_input, where="check")


    def testItemMethods(self):
        "Test short item methods like Text(), State() etc"

        for test_config in self.test_configs:
            test_config.preprocessing()
            self.assertEquals(test_config.ctrl.GetItem('Green').Text(), 'Green')
            self.assertEquals(test_config.ctrl.GetItem('Green').Image(), 2)
            self.assertEquals(test_config.ctrl.GetItem('Green').Indent(), 0)

    def testEnsureVisible(self):

        for test_config in self.test_configs:
            test_config.preprocessing()
            test_config.dlg.MoveWindow(width=300)

            # Gray is not selected by click because it's not visible
            test_config.ctrl.GetItem('Gray').Click()
            self.assertEquals(test_config.ctrl.GetItem('Gray').IsSelected(), False)
            test_config.dlg.set_focus() # just in case

            test_config.ctrl.GetItem('Gray').EnsureVisible()
            test_config.ctrl.GetItem('Gray').Click()
            self.assertEquals(test_config.ctrl.GetItem('Gray').IsSelected(), True)

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

        for test_config in self.test_configs:
            test_config.preprocessing()
            item1 = test_config.ctrl.GetItem(0, 0)
            item1_copy = test_config.ctrl.GetItem(0, 0)
            item2 = test_config.ctrl.GetItem(1, 0)

            self.assertEqual(item1, item1_copy)
            self.assertNotEqual(item1, "Not _listview_item")
            self.assertNotEqual(item1, item2)


class TreeViewTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        app = Application()
        app.start(os.path.join(controlspy_folder, "Tree View.exe"))

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

        self.app = app
        self.dlg = app.MicrosoftControlSpy #top_window_()
        self.ctrl = app.MicrosoftControlSpy.TreeView.WrapperObject()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly (TreeView)"
        self.assertEquals (self.ctrl.friendly_class_name(), "TreeView")

    def testItemCount(self):
        "Test the TreeView ItemCount method"
        self.assertEquals (self.ctrl.ItemCount(), 37)


    def testGetItem(self):
        "Test the GetItem method"

        self.assertRaises(RuntimeError, self.ctrl.GetItem, "test\here\please")

        self.assertRaises(IndexError, self.ctrl.GetItem, r"\test\here\please")

        self.assertEquals(
            self.ctrl.GetItem((0, 1, 2)).Text(), self.texts[1][3] + " kg")

        self.assertEquals(
            self.ctrl.GetItem(r"\The Planets\Venus\4.869e24 kg", exact=True).Text(), self.texts[1][3] + " kg")

        self.assertEquals(
            self.ctrl.GetItem(
                ["The Planets", "Venus", "4.869"]).Text(),
            self.texts[1][3] + " kg")


    def testItemText(self):
        "Test the TreeView item Text() method"

        self.assertEquals(self.ctrl.Root().Text(), self.root_text)

        self.assertEquals(
            self.ctrl.GetItem((0, 1, 2)).Text(), self.texts[1][3] + " kg")

    def testSelect(self):
        "Test selecting an item"
        self.ctrl.Select((0, 1, 2))

        self.ctrl.GetItem((0, 1, 2)).State()

        self.assertEquals(True, self.ctrl.IsSelected((0, 1, 2)))


    def testEnsureVisible(self):
        "make sure that the item is visible"

        # note this is partially a fake test at the moment because
        # just by getting an item - we usually make it visible
        self.ctrl.EnsureVisible((0, 8, 2))

        # make sure that the item is not hidden
        self.assertNotEqual(None, self.ctrl.GetItem((0, 8, 2)).rectangle())


    def testGetProperties(self):
        "Test getting the properties for the treeview control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            "TreeView", props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemsClick(self):
        "Test clicking of items and sub-items in the treeview control"
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


class TreeViewAdditionalTestCases(unittest.TestCase):
    "More unit tests for the TreeViewWrapper class (CmnCtrl1.exe)"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application().start(os.path.join(mfc_samples_folder, "CmnCtrl1.exe"))

        self.dlg = self.app.CommonControlsSample #top_window_()
        self.ctrl = self.app.CommonControlsSample.TreeView.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.dlg.Close()
        self.app.kill_()

    def testCheckBoxes(self):
        "Make sure tree view item method IsChecked() works as expected"
        self.dlg.TVS_CHECKBOXES.click_input()
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Click(where='check')
        self.assertEquals (birds.IsChecked(), True)
        birds.click_input(where='check')
        self.assertEquals (birds.IsChecked(), False)

    def testPrintItems(self):
        "Test TreeView method PrintItems()"
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        items_str = self.ctrl.PrintItems()
        self.assertEquals(items_str, "Treeview1\nBirds\n Eagle\n Hummingbird\n Pigeon\n" +
                                     "Dogs\n Dalmatian\n German Shepherd\n Great Dane\n" +
                                     "Fish\n Salmon\n Snapper\n Sole\n")

    def testIsSelected(self):
        "Make sure tree view item method IsSelected() works as expected"
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        eagle = self.ctrl.GetItem(r'\Birds\Eagle')
        eagle.Select()
        self.assertEquals(eagle.IsSelected(), True)

    def testExpandCollapse(self):
        "Make sure tree view item methods Expand() and Collapse() work as expected"
        birds = self.ctrl.GetItem(r'\Birds')
        birds.Expand()
        self.assertEquals(birds.IsExpanded(), True)
        
        birds.Collapse()
        self.assertEquals(birds.IsExpanded(), False)

    def testCheckBoxes(self):
        "Make sure correct area is clicked"
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
        "Make sure incorrect area raises an exception"
        birds = self.ctrl.GetItem(r'\Birds')
        self.assertRaises(RuntimeError, birds.Click, where='radiob')
        self.assertRaises(RuntimeError, birds.click_input, where='radiob')

    def testStartDraggingAndDrop(self):
        "Make sure tree view item methods StartDragging() and Drop() work as expected"
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
    "Unit tests for the Header class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        app = Application()
        app.start(os.path.join(mfc_samples_folder, "RowList.exe"), timeout=20)

        self.texts = [u'Color', u'Red', u'Green', u'Blue', u'Hue', u'Sat', u'Lum', u'Type']
        self.item_rects = [
            RECT (  0, 0, 150, 19), 
            RECT (150, 0, 200, 19), 
            RECT (200, 0, 250, 19), 
            RECT (250, 0, 300, 19), 
            RECT (300, 0, 400, 19), 
            RECT (400, 0, 450, 19), 
            RECT (450, 0, 500, 19), 
            RECT (500, 0, 650, 19)]
           
        self.app = app
        self.dlg = app.RowListSampleApplication #top_window_()
        self.ctrl = app.RowListSampleApplication.Header.WrapperObject()


    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly (Header)"
        self.assertEquals (self.ctrl.friendly_class_name(), "Header")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the header control"
        props  = self.ctrl.GetProperties()

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
        for i in range(len(test_rects)):
            self.assertEquals(test_rects[i].left, client_rects[i].left)
            self.assertEquals(test_rects[i].right, client_rects[i].right)
            self.assertEquals(test_rects[i].top, client_rects[i].top)
            self.failIf(abs(test_rects[i].bottom - client_rects[i].bottom) > 2) # may be equal to 17 or 19

    def testGetColumnText(self):
        for i in range(0, 3):
            self.assertEquals(
                self.texts[i],
                self.ctrl.GetColumnText(i))




class StatusBarTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

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

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly (StatusBar)"
        self.assertEquals (self.ctrl.friendly_class_name(), "StatusBar")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the status bar control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])


    def testBorderWidths(self):
        "Make sure the border widths are retrieved correctly"
        self.assertEquals (
            self.ctrl.BorderWidths(),
            dict(
                Horizontal = 0,
                Vertical = 2,
                Inter = 2,
                )
            )

    def testPartCount(self):
        "Make sure the number of parts is retrieved correctly"
        self.assertEquals (self.ctrl.PartCount(), 3)

    def testPartRightEdges(self):
        "Make sure the part widths are retrieved correctly"

        for i in range(0, self.ctrl.PartCount()-1):
            self.assertEquals (self.ctrl.PartRightEdges()[i], self.part_rects[i].right)

        self.assertEquals(self.ctrl.PartRightEdges()[i+1], -1)

    def testGetPartRect(self):
        "Make sure the part rectangles are retrieved correctly"

        for i in range(0, self.ctrl.PartCount()):
            part_rect = self.ctrl.GetPartRect(i)
            self.assertEquals (part_rect.left, self.part_rects[i].left)
            if i != self.ctrl.PartCount() - 1:
                self.assertEquals (part_rect.right, self.part_rects[i].right)
            self.assertEquals (part_rect.top, self.part_rects[i].top)
            self.failIf (abs(part_rect.bottom - self.part_rects[i].bottom) > 2)

        self.assertRaises(IndexError, self.ctrl.GetPartRect, 99)

    def testClientRects(self):
        self.assertEquals(self.ctrl.ClientRect(), self.ctrl.ClientRects()[0])
        client_rects = self.ctrl.ClientRects()[1:]
        for i in range(len(client_rects)):
            client_rect = client_rects[i]
            self.assertEquals (self.part_rects[i].left, client_rect.left)
            if i != len(client_rects) - 1:
                self.assertEquals (self.part_rects[i].right, client_rect.right)
            self.assertEquals (self.part_rects[i].top, client_rect.top)
            self.failIf (abs(self.part_rects[i].bottom - client_rect.bottom) > 2)

    def testGetPartText(self):
        self.assertRaises(IndexError, self.ctrl.GetPartText, 99)

        for i, text in enumerate(self.texts):
            self.assertEquals(text, self.ctrl.GetPartText(i))


class TabControlTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
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

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly (TabControl)"
        self.assertEquals (self.ctrl.friendly_class_name(), "TabControl")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the tabcontrol"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testRowCount(self):
        self.assertEquals(1, self.ctrl.RowCount())

        dlgClientRect = self.ctrl.parent().rectangle() # use the parent as a reference
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
        "Make sure the number of parts is retrieved correctly"
        self.assertEquals (self.ctrl.TabCount(), 5)

    def testGetTabRect(self):
        "Make sure the part rectangles are retrieved correctly"

        for i, rect in enumerate(self.rects):
            self.assertEquals (self.ctrl.GetTabRect(i), self.rects[i])

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
#        self.assertEquals (self.ctrl.GetTabState(1), 1)
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
    "Unit tests for the ToolbarWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

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

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly (Toolbar)"
        self.assertEquals (self.ctrl.friendly_class_name(), "Toolbar")

    def testTexts(self):
        "Make sure the texts are set correctly"
        for txt in self.ctrl.texts():
            self.assertEquals (isinstance(txt, six.string_types), True)

    def testGetProperties(self):
        "Test getting the properties for the toolbar control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        self.assertEquals(
            self.ctrl.ButtonCount(), props['button_count'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testButtonCount(self):
        "Test the button count method of the toolbar"
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
        self.assertEquals(u"New" in tt,True)
        self.assertEquals(u"About" in tt,True)

        tips = self.ctrl2.GetToolTipsControl()
        tt = tips.texts()
        self.assertEquals(u"Pencil" in tt,True)
        self.assertEquals(u"Ellipse" in tt,True)


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
        app = Application()
        app.start(os.path.join(mfc_samples_folder, "RebarTest.exe"))

        self.app = app
        self.dlg = app.RebarTest_RebarTest
        self.dlg.Wait('ready', 20)
        self.ctrl = app.RebarTest_RebarTest.Rebar.WrapperObject()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ReBar)"""
        self.assertEquals (self.ctrl.friendly_class_name(), "ReBar")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        for txt in self.ctrl.texts():
            self.assertEquals (isinstance(txt, six.string_types), True)

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
        self.dlg.StandardToolbar.Button(1).Click()
        self.app.Window_(title='Open').Wait('ready')
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
        """Start the application set some data and wait for the state we want"""
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

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.app.kill_()

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (ToolTips)"""
        self.assertEquals (self.ctrl.friendly_class_name(), "ToolTips")

    def testGetProperties(self):
        """Test getting the properties for the tooltips control"""
        props  = self.ctrl.GetProperties()

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
        self.dlg.move_mouse_input(coords=(0, 0)) # just to make sure a tooltip is not shown
        ActionLogger().log('ToolTips texts = ' + ';'.join(self.ctrl.texts()))
        self.assertEquals(self.ctrl.texts()[0], '')
        self.assertEquals(self.ctrl.texts()[1:], self.texts)


class UpDownTestCases(unittest.TestCase):

    """Unit tests for the UpDownWrapper class"""

    def setUp(self):
        """Start the application set some data and wait for the state we want"""
        app = Application()
        app.start(os.path.join(controlspy_folder,  "Up-Down.exe"))

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.UpDown2.WrapperObject()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.type_keys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        """Make sure the friendly class is set correctly (UpDown)"""
        self.assertEquals (self.ctrl.friendly_class_name(), "UpDown")

    def testTexts(self):
        """Make sure the texts are set correctly"""
        self.assertEquals (self.ctrl.texts()[1:], [])

    def testGetProperties(self):
        """Test getting the properties for the updown control"""
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.ctrl.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetValue(self):
        """Test getting up-down position"""
        self.assertEquals (self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals (self.ctrl.GetValue(), 23)

    def testSetValue(self):
        """Test setting up-down position"""
        self.assertEquals (self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals (self.ctrl.GetValue(), 23)
        self.assertEquals(
            int(self.ctrl.GetBuddyControl().texts()[1]),
            23)

    def testGetBase(self):
        """Test getting the base of the up-down control"""
        self.assertEquals (self.ctrl.GetBase(), 10)
        #self.dlg.StatementEdit.SetEditText ("MSG (UDM_SETBASE, 16, 0)")

        # use CloseClick to allow the control time to respond to the message
        #self.dlg.Send.click_input()
        self.ctrl.SetBase(16)

        self.assertEquals (self.ctrl.GetBase(), 16)

    def testGetRange(self):
        """Test getting the range of the up-down control"""
        self.assertEquals((0, 9999), self.ctrl.GetRange())

    def testGetBuddy(self):
        """Test getting the buddy control"""
        self.assertEquals (self.ctrl.GetBuddyControl().handle, self.dlg.Edit6.handle)


    def testIncrement(self):
        """Test incremementing up-down position"""
        self.ctrl.Increment()
        self.assertEquals (self.ctrl.GetValue(), 1)

    def testDecrement(self):
        """Test decrementing up-down position"""
        self.ctrl.SetValue(23)
        self.ctrl.Decrement()
        self.assertEquals (self.ctrl.GetValue(), 22)


if __name__ == "__main__":
    unittest.main()
