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

"""Tests for Menu"""

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
#from pywinauto.controls.HwndWrapper import HwndWrapper
#from pywinauto import win32structures, win32defines
from pywinauto.controls.menuwrapper import MenuItemNotEnabled

import unittest

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')


class MenuWrapperTests(unittest.TestCase):
    "Unit tests for the Menu and the MenuItem classes"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        self.app.start("Notepad.exe")

        self.dlg = self.app.Notepad

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()


    def testInvalidHandle(self):
        "Test that an exception is raised with an invalid menu handle"
        #self.assertRaises(InvalidWindowHandle, HwndWrapper, -1)
        pass


    def testItemCount(self):
        self.assertEquals(5, self.dlg.Menu().ItemCount())

    def testItem(self):
        self.assertEquals(u'&File', self.dlg.Menu().Item(0).Text())

    def testItems(self):
        self.assertEquals([u'&File', u'&Edit', u'F&ormat', u'&View', u'&Help'],
                          [item.Text() for item in self.dlg.Menu().Items()])

    def testFriendlyClassName(self):
        self.assertEquals('MenuItem', self.dlg.Menu().Item(0).FriendlyClassName())

    def testMenuItemNotEnabled(self):
        self.assertRaises(MenuItemNotEnabled, self.dlg.MenuSelect, 'Edit->Find Next')
        self.assertRaises(MenuItemNotEnabled, self.dlg.MenuItem('Edit->Find Next').Click)
        self.assertRaises(MenuItemNotEnabled, self.dlg.MenuItem('Edit->Find Next').ClickInput)

    def testGetProperties(self):
        self.assertEquals({u'MenuItems': [{u'Index': 0, u'State': 0, u'Type': 0, u'ID': 64, u'Text': u'View &Help'},
                                          {u'Index': 1, u'State': 3, u'Type': 2048, u'ID': 0, u'Text': u''},
                                          {u'Index': 2, u'State': 0, u'Type': 0, u'ID': 65, u'Text': u'&About Notepad'}]},
                          self.dlg.Menu().GetMenuPath('Help')[0].SubMenu().GetProperties())

    def testGetMenuPath(self):
        #print('ID = ' + str(self.dlg.Menu().GetMenuPath('Help->#3')[0].ID()))
        self.assertEquals(u'&About Notepad', self.dlg.Menu().GetMenuPath('Help->#2')[-1].Text())
        self.assertEquals(u'&About Notepad', self.dlg.Menu().GetMenuPath('Help->$65')[-1].Text())
        self.assertEquals(u'&About Notepad', self.dlg.Menu().GetMenuPath('&Help->&About Notepad', exact=True)[-1].Text())
        self.assertRaises(IndexError, self.dlg.Menu().GetMenuPath, '&Help->About what?', exact=True)

    def test__repr__(self):
        print(self.dlg.Menu())
        print(self.dlg.Menu().GetMenuPath('&Help->&About Notepad', exact=True)[-1])

    def testClick(self):
        self.dlg.Menu().GetMenuPath('&Help->&About Notepad')[-1].Click()
        About = self.app.Window_(title='About Notepad')
        About.Wait('ready')
        About.OK.Click()
        About.WaitNot('visible')

    def testClickInput(self):
        self.dlg.Menu().GetMenuPath('&Help->&About Notepad')[-1].ClickInput()
        About = self.app.Window_(title='About Notepad')
        About.Wait('ready')
        About.OK.Click()
        About.WaitNot('visible')


class OwnerDrawnMenuTests(unittest.TestCase):
    "Unit tests for the OWNERDRAW menu items"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application().Start(os.path.join(mfc_samples_folder, u"BCDialogMenu.exe"))

        self.dlg = self.app.BCDialogMenu

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

    def testCorrectText(self):
        self.assertEquals(u'&New', self.dlg.Menu().GetMenuPath('&File->#0')[-1].Text()[:4])
        self.assertEquals(u'&Open...', self.dlg.Menu().GetMenuPath('&File->#1')[-1].Text()[:8])



if __name__ == "__main__":
    unittest.main()

