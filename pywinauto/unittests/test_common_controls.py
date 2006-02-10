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

"Tests for classes in controls\common_controls.py"

__revision__ = "$Revision: 234 $"

from pywinauto.controls.common_controls import *
from pywinauto.win32structures import RECT

import unittest

class ListViewTestCases(unittest.TestCase):
    "Unit tests for the ListViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(r"C:\.projects\py_pywinauto\controlspy0798\List View.exe")

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
        self.ctrl = app.MicrosoftControlSpy.ListView.ctrl_()

        #self.dlg.MenuSelect("Styles")

        # select show selection always!
        #app.ControlStyles.ListBox1.TypeKeys("{UP}" * 26 + "{SPACE}")

        #self.app.ControlStyles.ListBox1.Select("LVS_SHOWSELALWAYS")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()

        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)


    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals (self.ctrl.FriendlyClassName(), "ListView")

    def testColumnCount(self):
        "Test the ColumnCount method"
        self.assertEquals (self.ctrl.ColumnCount(), 4)

    def testItemCount(self):
        "Test the ItemCount method"
        self.assertEquals (self.ctrl.ItemCount(), 9)

    def testItemText(self):
        "Test the item.Text property"
        item = self.ctrl.GetItem(1)

        self.assertEquals(item.Text, "Venus")

    def testItems(self):
        "Test the Items method"

        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        for i, item in enumerate(self.ctrl.Items()):
            self.assertEquals(item.Text, flat_texts[i])


    def testTexts(self):
        "Test the Texts method"

        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        self.assertEquals(flat_texts, self.ctrl.Texts()[1:])



    def testGetItem(self):
        "Test the GetItem method"

        for row in range(self.ctrl.ItemCount()):
            for col in range(self.ctrl.ColumnCount()):
                self.assertEquals(
                    self.ctrl.GetItem(row, col).Text, self.texts[row][col])


    def testColumn(self):
        "Test the Columns method"

        cols = self.ctrl.Columns()
        self.assertEqual (len(cols), self.ctrl.ColumnCount())

        # todo add more checking of column values
        #for col in cols:
        #    print col


    def testGetSelectionCount(self):
        "Test the GetSelectedCount method"

        self.assertEquals(self.ctrl.GetSelectedCount(), 0)

        self.ctrl.Select(1)
        self.ctrl.Select(7)
        self.ctrl.Select(12)

        self.assertEquals(self.ctrl.GetSelectedCount(), 2)


    def testIsSelected(self):
        "Test IsSelected for some items"

        # ensure that the item is not selected
        self.assertEquals(self.ctrl.IsSelected(1), False)

        # select an item
        self.ctrl.Select(1)

        # now ensure that the item is selected
        self.assertEquals(self.ctrl.IsSelected(1), True)


    def _testFocused(self):
        "Test checking the focus of some items"

        print "Select something quick!!"
        import time
        time.sleep(3)
        #self.ctrl.Select(1)

        print self.ctrl.IsFocused(0)
        print self.ctrl.IsFocused(1)
        print self.ctrl.IsFocused(2)
        print self.ctrl.IsFocused(3)
        print self.ctrl.IsFocused(4)
        print self.ctrl.IsFocused(5)
        #for col in cols:
        #    print col


    def testSelect(self):
        "Test Selecting some items"
        self.ctrl.Select(1)
        self.ctrl.Select(3)
        self.ctrl.Select(4)

        self.assertEquals(self.ctrl.GetSelectedCount(), 3)

#
#    def testSubItems(self):
#
#        for row in range(self.ctrl.ItemCount())
#
#        for i in self.ctrl.Items():
#
#            #self.assertEquals(item.Text, texts[i])





class TreeViewTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(r"C:\.projects\py_pywinauto\controlspy0798\Tree View.exe")

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
        self.ctrl = app.MicrosoftControlSpy.TreeView.ctrl_()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.TypeKeys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals (self.ctrl.FriendlyClassName(), "TreeView")

    def testItemCount(self):
        "Test the ItemCount method"
        self.assertEquals (self.ctrl.Count(), 37)


    def testItemText(self):
        "Test the ItemCount method"

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
        self.assertNotEqual(None, self.ctrl.GetItem((0, 8, 2)).Rectangle())







class StatusBarTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(r"C:\.projects\py_pywinauto\controlspy0798\Status bar.exe")

        self.texts = ["Long text", "", "Status Bar"]
        self.part_rects = [
            RECT(0, 2, 65, 20),
            RECT(67, 2, 90, 20),
            RECT(92, 2, 264, 20)]
        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.StatusBar.ctrl_()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.TypeKeys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals (self.ctrl.FriendlyClassName(), "StatusBar")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.Texts()[1:], self.texts)

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

    def testNumParts(self):
        "Make sure the number of parts is retrieved correctly"
        self.assertEquals (self.ctrl.NumParts(), 3)

    def testGetPartRect(self):
        "Make sure the part rectangles are retrieved correctly"

        for i in range(0, self.ctrl.NumParts()):
            self.assertEquals (self.ctrl.GetPartRect(i), self.part_rects[i])

    def testPartRightEdges(self):
        "Make sure the part widths are retrieved correctly"

        for i in range(0, self.ctrl.NumParts()-1):
            self.assertEquals (self.ctrl.PartRightEdges()[i], self.part_rects[i].right)

        self.assertEquals(self.ctrl.PartRightEdges()[i+1], -1)


    def testGetProperties(self):
        "Test getting the properties for the control"
        props  = self.dlg.GetProperties()

        self.assertEquals(
            self.dlg.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.dlg.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.dlg, prop_name)(), props[prop_name])

















#
#def test_header(ctrl):
#    "Not called anymore"
#    print "="*80
#    print "Header"
#    print "="*80
#    header = HeaderWrapper(ctrl)
#
#    for i in range(0, header.Count()):
#        print header.ColumnRectangle(i)
#
#
#def test_statusbar(ctrl):
#    "Not called anymore"
#    print "="*80
#    print "StatusBar"
#    print "="*80
#    stat_bar = StatusBarWrapper(ctrl)
#
#    print stat_bar.NumParts()
#
#    print stat_bar.BorderWidths()
#
#    print stat_bar.PartWidths()
#
#    for i in range(0, stat_bar.NumParts()):
#        print "\t", `stat_bar.GetPartText(i)`
#



if __name__ == "__main__":
    unittest.main()