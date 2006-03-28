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

from  pywinauto.controls import common_controls
from pywinauto.controls.common_controls import *
from pywinauto.win32structures import RECT
from pywinauto.controls import WrapHandle

import ctypes

import unittest
import time
import pprint
import pdb

controlspy_folder = r"C:\.projects\py_pywinauto\controlspy0798\\"


class RemoteMemoryBlockTestCases(unittest.TestCase):
    def test__init__fail(self):
        self.assertRaises(AccessDenied, common_controls._RemoteMemoryBlock, 0)

    def test__init__fail(self):
        self.assertRaises(AccessDenied, common_controls._RemoteMemoryBlock, 0)





class ListViewTestCases(unittest.TestCase):
    "Unit tests for the ListViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "List View.exe")

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
        "Make sure the ListView friendly class is set correctly"
        self.assertEquals (self.ctrl.FriendlyClassName(), "ListView")

    def testColumnCount(self):
        "Test the ListView ColumnCount method"
        self.assertEquals (self.ctrl.ColumnCount(), 4)

    def testItemCount(self):
        "Test the ListView ItemCount method"
        self.assertEquals (self.ctrl.ItemCount(), 9)

    def testItemText(self):
        "Test the ListView item.Text property"
        item = self.ctrl.GetItem(1)

        self.assertEquals(item['text'], "Venus")

    def testItems(self):
        "Test the ListView Items method"

        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        for i, item in enumerate(self.ctrl.Items()):
            self.assertEquals(item['text'], flat_texts[i])


    def testTexts(self):
        "Test the ListView Texts method"

        flat_texts = []
        for row in self.texts:
            flat_texts.extend(row)

        self.assertEquals(flat_texts, self.ctrl.Texts()[1:])



    def testGetItem(self):
        "Test the ListView GetItem method"

        for row in range(self.ctrl.ItemCount()):
            for col in range(self.ctrl.ColumnCount()):
                self.assertEquals(
                    self.ctrl.GetItem(row, col)['text'], self.texts[row][col])


    def testColumn(self):
        "Test the ListView Columns method"

        cols = self.ctrl.Columns()
        self.assertEqual (len(cols), self.ctrl.ColumnCount())

        # TODO: add more checking of column values
        #for col in cols:
        #    print col


    def testGetSelectionCount(self):
        "Test the ListView GetSelectedCount method"

        self.assertEquals(self.ctrl.GetSelectedCount(), 0)

        self.ctrl.Select(1)
        self.ctrl.Select(7)
        self.ctrl.Select(12)

        self.assertEquals(self.ctrl.GetSelectedCount(), 2)


    def testIsSelected(self):
        "Test ListView IsSelected for some items"

        # ensure that the item is not selected
        self.assertEquals(self.ctrl.IsSelected(1), False)

        # select an item
        self.ctrl.Select(1)

        # now ensure that the item is selected
        self.assertEquals(self.ctrl.IsSelected(1), True)


    def _testFocused(self):
        "Test checking the focus of some ListView items"

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
        "Test ListView Selecting some items"
        self.ctrl.Select(1)
        self.ctrl.Select(3)
        self.ctrl.Select(4)

        self.assertEquals(self.ctrl.GetSelectedCount(), 3)


    def testGetProperties(self):
        "Test getting the properties for the listview control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            "ListView", props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

        self.assertEquals(props['ColumnCount'], 4)
        self.assertEquals(props['ItemCount'], 9)



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
        app.start_(controlspy_folder + "Tree View.exe")

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
        "Test the TreeView ItemCount method"
        self.assertEquals (self.ctrl.ItemCount(), 37)


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


    def testGetProperties(self):
        "Test getting the properties for the treeview control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            "TreeView", props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])


class HeaderTestCases(unittest.TestCase):
    "Unit tests for the Header class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "Header.exe")

        self.texts = [u'Distance', u'Diameter', u'Mass']
        self.item_rects = [
            RECT(0, 0, 90, 21),
            RECT(90, 0, 180, 21),
            RECT(180, 0, 260, 21)]
        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.Header.ctrl_()


    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testFriendlyClass(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals (self.ctrl.FriendlyClassName(), "Header")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.Texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the header control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testItemCount(self):
        self.assertEquals(3, self.ctrl.ItemCount())

    def testGetColumnRectangle(self):
        for i in range(0, 3):
            self.assertEquals(
                self.item_rects[i],
                self.ctrl.GetColumnRectangle(i))

    def testClientRects(self):
        test_rects = self.item_rects
        test_rects.insert(0, self.ctrl.ClientRect())

        self.assertEquals(
            test_rects,
            self.ctrl.ClientRects())

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

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "Status bar.exe")

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

    def testGetProperties(self):
        "Test getting the properties for the status bar control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

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
            self.assertEquals (self.ctrl.GetPartRect(i), self.part_rects[i])

        self.assertRaises(IndexError, self.ctrl.GetPartRect, 99)

    def testClientRects(self):
        self.assertEquals(self.ctrl.ClientRect(), self.ctrl.ClientRects()[0])
        self.assertEquals(self.part_rects, self.ctrl.ClientRects()[1:])

    def testGetPartText(self):
        self.assertRaises(IndexError, self.ctrl.GetPartText, 99)

        for i, text in enumerate(self.texts):
            self.assertEquals(text, self.ctrl.GetPartText(i))








class TabControlTestCases(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "Tab.exe")

        self.texts = [
            "Pluto", "Neptune", "Uranus",
            "Saturn", "Jupiter", "Mars",
            "Earth", "Venus", "Mercury", "Sun"]

        self.rects = [
            RECT(2,2,80,21),
            RECT(80,2,174,21),
            RECT(174,2,261,21),
            RECT(2,21,91,40),
            RECT(91,21,180,40),
            RECT(180,21,261,40),
            RECT(2,40,64,59),
            RECT(64,40,131,59),
            RECT(131,40,206,59),
            RECT(206,40,261,59),
        ]

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.TabControl.ctrl_()

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
        self.assertEquals (self.ctrl.FriendlyClassName(), "TabControl")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.Texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the tabcontrol"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testRowCount(self):
        self.assertEquals(3, self.ctrl.RowCount())

    def testGetSelectedTab(self):
        self.assertEquals(6, self.ctrl.GetSelectedTab())
        self.ctrl.Select(0)
        self.assertEquals(0, self.ctrl.GetSelectedTab())
        self.ctrl.Select("Jupiter")
        self.assertEquals(4, self.ctrl.GetSelectedTab())

    def testTabCount(self):
        "Make sure the number of parts is retrieved correctly"
        self.assertEquals (self.ctrl.TabCount(), 10)

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
#        print "==\n",self.ctrl.TabStates()
#
#        self.assertEquals (self.ctrl.GetTabState(1), 1)
#
#    def testTabStates(self):
#        print self.ctrl.TabStates()
#        raise "tabstates hiay"


    def testGetTabText(self):
        for i, text in enumerate(self.texts):
            self.assertEquals(text, self.ctrl.GetTabText(i))

        self.assertRaises(IndexError, self.ctrl.GetTabText, 99)

    def testClientRects(self):
        self.assertEquals(self.ctrl.ClientRect(), self.ctrl.ClientRects()[0])
        self.assertEquals(self.rects, self.ctrl.ClientRects()[1:])

    def testSelect(self):
        self.assertEquals(6, self.ctrl.GetSelectedTab())

        self.ctrl.Select(1)
        self.assertEquals(1, self.ctrl.GetSelectedTab())
        self.ctrl.Select("Mercury")
        self.assertEquals(8, self.ctrl.GetSelectedTab())

        self.assertRaises(IndexError, self.ctrl.Select, 99)






class ToolbarTestCases(unittest.TestCase):
    "Unit tests for the UpDownWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "toolbar.exe")

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.Toolbar.ctrl_()

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
        self.assertEquals (self.ctrl.FriendlyClassName(), "Toolbar")

    def testTexts(self):
        "Make sure the texts are set correctly"
        for txt in self.ctrl.Texts():
            self.assertEquals (isinstance(txt, basestring), True)

    def testGetProperties(self):
        "Test getting the properties for the toolbar control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        self.assertEquals(
            self.ctrl.ButtonCount(), props['ButtonCount'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testButtonCount(self):
        "Test the button count method of the toolbar"
        self.assertEquals(self.ctrl.ButtonCount(), 14)

    def testGetButton(self):
        self.assertRaises(IndexError, self.ctrl.GetButton, 29)

    def testGetButtonRect(self):
        self.assertEquals(self.ctrl.GetButtonRect(1), RECT(91, 0, 114, 22))

    def testGetToolTipsControls(self):
        tips = self.ctrl.GetToolTipsControl()

        self.assertEquals("Button ID 7" in tips.Texts(),True)

    def testPressButton(self):
        self.ctrl.PressButton(0)
        #print self.ctrl.Texts()
        self.ctrl.PressButton("10")
        raise "not fully tested"


class RebarTestCases(unittest.TestCase):
    "Unit tests for the UpDownWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "rebar.exe")

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.Rebar.ctrl_()

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
        self.assertEquals (self.ctrl.FriendlyClassName(), "ReBar")

    def testTexts(self):
        "Make sure the texts are set correctly"
        for txt in self.ctrl.Texts():
            self.assertEquals (isinstance(txt, basestring), True)

    def testBandCount(self):
        self.assertEquals(self.ctrl.BandCount(), 2)

    def testGetBand(self):

        self.assertRaises(IndexError, self.ctrl.GetBand, 99)
        self.assertRaises(IndexError, self.ctrl.GetBand, 2)

        band = self.ctrl.GetBand(0)


        self.assertEquals(band.hwndChild, self.dlg.ToolBar.handle)

        #self.assertEquals(band.text, "blah")

    def testGetToolTipsControl(self):
        self.assertEquals(self.ctrl.GetToolTipsControl(), None)


class ToolTipsTestCases(unittest.TestCase):
    "Unit tests for the tooltips class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.texts = [u'Tooltip Tool 0', u'Tooltip Tool 1', u'Tooltip Tool 2']

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "Tooltip.exe")

        self.app = app
        self.dlg = app.MicrosoftControlSpy

        tips = app.windows_(
            visible_only = False,
            enabled_only = False,
            top_level_only = False,
            class_name = "tooltips_class32")

        self.ctrl = WrapHandle(tips[1])


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
        self.assertEquals (self.ctrl.FriendlyClassName(), "ToolTips")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.Texts()[1:], self.texts)

    def testGetProperties(self):
        "Test getting the properties for the tooltips control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetTip(self):
        self.assertRaises(IndexError, self.ctrl.GetTip, 99)
        tip = self.ctrl.GetTip(1)
        self.assertEquals(tip.text, self.texts[1])

    def testToolCount(self):
        self.assertEquals(3, self.ctrl.ToolCount())

    def testGetTipText(self):
        self.assertEquals(self.texts[1], self.ctrl.GetTipText(1))

    def testTexts(self):
        self.assertEquals(self.ctrl.Texts()[0], '')
        self.assertEquals(self.ctrl.Texts()[1:], self.texts)



class UpDownTestCases(unittest.TestCase):
    "Unit tests for the UpDownWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()
        app.start_(controlspy_folder + "Up-Down.exe")

        self.app = app
        self.dlg = app.MicrosoftControlSpy
        self.ctrl = app.MicrosoftControlSpy.UpDown2.ctrl_()

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
        self.assertEquals (self.ctrl.FriendlyClassName(), "UpDown")

    def testTexts(self):
        "Make sure the texts are set correctly"
        self.assertEquals (self.ctrl.Texts()[1:], [])

    def testGetProperties(self):
        "Test getting the properties for the updown control"
        props  = self.ctrl.GetProperties()

        self.assertEquals(
            self.ctrl.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.ctrl.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.ctrl, prop_name)(), props[prop_name])

    def testGetValue(self):
        "Test getting up-down position"
        self.assertEquals (self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals (self.ctrl.GetValue(), 23)

    def testSetValue(self):
        "Test setting up-down position"
        self.assertEquals (self.ctrl.GetValue(), 0)

        self.ctrl.SetValue(23)
        self.assertEquals (self.ctrl.GetValue(), 23)
        self.assertEquals(
            int(self.ctrl.GetBuddyControl().Texts()[1]),
            23)

    def testGetBase(self):
        "Test getting the base of the up-down control"
        self.assertEquals (self.ctrl.GetBase(), 10)
        self.dlg.StatementEdit.SetEditText ("MSG (UDM_SETBASE, 16, 0)")

        # use CloseClick to allow the control time to respond to the message
        self.dlg.Send.Click()

        self.assertEquals (self.ctrl.GetBase(), 16)

    def testGetRange(self):
        "Test getting the range of the up-down control"
        self.assertEquals((0, 9999), self.ctrl.GetRange())

    def testGetBuddy(self):
        "Test getting the buddy control"
        self.assertEquals (self.ctrl.GetBuddyControl().handle, self.dlg.Edit6.handle)


    def testIncrement(self):
        "Test incremementing up-down position"
        self.ctrl.Increment()
        self.assertEquals (self.ctrl.GetValue(), 1)

    def testDecrement(self):
        "Test decrementing up-down position"
        self.ctrl.SetValue(23)
        self.ctrl.Decrement()
        self.assertEquals (self.ctrl.GetValue(), 22)





if __name__ == "__main__":
    unittest.main()