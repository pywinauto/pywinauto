# encoding: utf-8
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
from __future__ import unicode_literals

"Tests for HwndWrapper"

import time
#import pprint
#import pdb
#import warnings

#import ctypes
import locale
import re

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.controls.HwndWrapper import HwndWrapper
from pywinauto import win32structures, win32defines
from pywinauto.findwindows import WindowNotFoundError
from pywinauto.sysinfo import is_x64_Python, is_x64_OS


__revision__ = "$Revision: 234 $"

try:
    from pywinauto.controls.HwndWrapper import *
except ImportError:
    # allow it to be imported in a dev environment
    import sys

    pywinauto_imp = "\\".join(__file__.split('\\')[:-3])
    print("sdfdsf", pywinauto_imp)
    sys.path.append(pywinauto_imp)
    from pywinauto.controls.HwndWrapper import *

import unittest

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class HwndWrapperTests(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        if is_x64_Python() or not is_x64_OS():
            self.app.start_(r"C:\Windows\System32\calc.exe")
        else:
            self.app.start_(r"C:\Windows\SysWOW64\calc.exe")

        self.dlg = self.app.Calculator
        self.dlg.MenuSelect('View->Scientific\tAlt+2')
        self.ctrl = HwndWrapper(self.dlg.Button2.handle) # Backspace

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.TypeKeys("%{F4}")
        #self.dlg.Close()
        self.app.kill_()

    def testInvalidHandle(self):
        "Test that an exception is raised with an invalid window handle"
        self.assertRaises(InvalidWindowHandle, HwndWrapper, -1)

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.WindowText(), "Untitled - Notepad")

    def testFriendlyClassName(self):
        "Test getting the friendly classname of the dialog"
        self.assertEquals(self.ctrl.FriendlyClassName(), "Button")


    def testClass(self):
        "Test getting the classname of the dialog"
        self.assertEquals(self.ctrl.Class(), "Button")

    def testWindowText(self):
        "Test getting the window Text of the dialog"
        self.assertEquals(
            HwndWrapper(self.dlg.Degrees.handle).WindowText(), u'Degrees')

    def testStyle(self):

        self.dlg.Style()

        self.assertEquals(self.ctrl.Style(),
            win32defines.WS_CHILD |
            win32defines.WS_VISIBLE |
            win32defines.BS_PUSHBUTTON |
            win32defines.BS_TEXT)


    def testExStyle(self):
        self.assertEquals(self.ctrl.ExStyle(),
            win32defines.WS_EX_NOPARENTNOTIFY |
            win32defines.WS_EX_LEFT |
            win32defines.WS_EX_LTRREADING |
            win32defines.WS_EX_RIGHTSCROLLBAR)

        """self.assertEquals(self.dlg.ExStyle(),
            win32defines.WS_EX_WINDOWEDGE |
            win32defines.WS_EX_LEFT |
            win32defines.WS_EX_LTRREADING |
            win32defines.WS_EX_RIGHTSCROLLBAR |
            win32defines.WS_EX_CONTROLPARENT |
            win32defines.WS_EX_APPWINDOW)"""

    def testControlID(self):
        self.assertEquals(self.ctrl.ControlID(), 83)
        self.dlg.ControlID()

    def testUserData(self):
        self.ctrl.UserData()
        self.dlg.UserData()

    def testContextHelpID(self):
        self.ctrl.ContextHelpID()
        self.dlg.ContextHelpID()

    def testIsVisible(self):
        self.assertEqual(self.ctrl.IsVisible(), True)
        self.assertEqual(self.dlg.IsVisible(), True)

    def testIsUnicode(self):
        self.assertEqual(self.ctrl.IsUnicode(), True)
        self.assertEqual(self.dlg.IsUnicode(), True)

    def testIsEnabled(self):
        self.assertEqual(self.ctrl.IsEnabled(), True)
        self.assertEqual(self.dlg.IsEnabled(), True)
        self.assertEqual(self.dlg.Button26.IsEnabled(), False); # Button26 = '%'

    def testCloseClick_bug(self):
        self.dlg.MenuSelect('Help->About Calculator')
        self.app.AboutCalculator.Wait("visible", 10)
        self.app.AboutCalculator.CloseButton.CloseClick()
        Timings.closeclick_dialog_close_wait = .7
        try:
            self.app.AboutCalculator.CloseClick()
        except timings.TimeoutError:
            pass

        self.app.AboutCalculator.Close()

        #self.assertEquals(self.app.StatisticsBox.Exists(), False)

    def testCloseAltF4(self):
        self.dlg.MenuSelect('Help->About Calculator')
        AboutCalculator = self.app.Window_(title='About Calculator', class_name='#32770')
        AboutWrapper = AboutCalculator.Wait("enabled")
        AboutCalculator.CloseAltF4()
        AboutCalculator.WaitNot('visible')
        self.assertNotEqual(AboutWrapper.IsVisible(), True)

    def testRectangle(self):
        "Test getting the rectangle of the dialog"
        rect = self.dlg.Rectangle()
        self.assertNotEqual(rect.top, None)
        self.assertNotEqual(rect.left, None)
        self.assertNotEqual(rect.bottom, None)
        self.assertNotEqual(rect.right, None)

        if abs(rect.height() - 323) > 2:
            if rect.height() != 310:
                self.assertEqual(rect.height(), 323)
        if abs(rect.width() - 423) > 2:
            if rect.width() != 413:
                self.assertEqual(rect.width(), 423)

    def testClientRect(self):
        rect = self.dlg.Rectangle()
        cli = self.dlg.ClientRect()

        self.assertEqual(cli.left , 0)
        self.assertEqual(cli.top , 0)

        assert(cli.width() < rect.width())
        assert(cli.height() < rect.height())

    def testFont(self):
        self.assertNotEqual(self.dlg.Font(), self.ctrl.Font())

    def ProcessID(self):
        self.assertEqual(self.ctrl.ProcessID(), self.dlg.ProcessID)
        self.assertNotEqual(self.ctrl.ProcessID(), 0)

    def testHasStyle(self):
        self.assertEqual(self.ctrl.HasStyle(win32defines.WS_CHILD), True)
        self.assertEqual(self.dlg.HasStyle(win32defines.WS_CHILD), False)

        self.assertEqual(self.ctrl.HasStyle(win32defines.WS_SYSMENU), False)
        self.assertEqual(self.dlg.HasStyle(win32defines.WS_SYSMENU), True)

    def testHasExStyle(self):
        self.assertEqual(self.ctrl.HasExStyle(win32defines.WS_EX_NOPARENTNOTIFY), True)
        self.assertEqual(self.dlg.HasExStyle(win32defines.WS_EX_NOPARENTNOTIFY), False)

        self.assertEqual(self.ctrl.HasExStyle(win32defines.WS_EX_APPWINDOW), False)
        #self.assertEqual(self.dlg.HasExStyle(win32defines.WS_EX_APPWINDOW), True)

    def testIsDialog(self):
        self.assertEqual(self.ctrl.IsDialog(), False)
        self.assertEqual(self.dlg.IsDialog(), True)

    def testMenuItems(self):
        self.assertEqual(self.ctrl.MenuItems(), [])
        self.assertEqual(self.dlg.MenuItems()[1]['Text'], '&Edit')


    def testParent(self):
        self.assertEqual(self.ctrl.Parent().Parent().Parent(), self.dlg.handle)


    def testTopLevelParent(self):
        self.assertEqual(self.ctrl.TopLevelParent(), self.dlg.handle)
        self.assertEqual(self.dlg.TopLevelParent(), self.dlg.handle)

    def testTexts(self):
        self.assertEqual(self.dlg.Texts(), ['Calculator'])
        self.assertEqual(HwndWrapper(self.dlg.Degrees.handle).Texts(), [u'Degrees'])
        self.assertEqual(self.dlg.ChildWindow(class_name='Static', ctrl_index=5).Texts(), ['0'])

    def testClientRects(self):
        self.assertEqual(self.ctrl.ClientRects()[0], self.ctrl.ClientRect())
        self.assertEqual(self.dlg.ClientRects()[0], self.dlg.ClientRect())

    def testFonts(self):
        self.assertEqual(self.ctrl.Fonts()[0], self.ctrl.Font())
        self.assertEqual(self.dlg.Fonts()[0], self.dlg.Font())

    def testChildren(self):
        self.assertEqual(self.ctrl.Children(), [])
        self.assertNotEqual(self.dlg.Children(), [])


    def testIsChild(self):
        self.assertEqual(self.ctrl.IsChild(self.dlg.WrapperObject()), True)
        self.assertEqual(self.dlg.IsChild(self.ctrl), False)


    def testSendMessage(self):
        vk = self.dlg.SendMessage(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Degrees.SendMessage(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Button" = 0x2000 and "Radio" = 0x40
        expected = 0x2000 + 0x40
        self.assertEqual(expected, code)


    def testSendMessageTimeout(self):

        vk = self.dlg.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Degrees.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Button" = 0x2000 and "Radio" = 0x40
        expected = 0x2000 + 0x40
        self.assertEqual(expected, code)

    def testPostMessage(self):
        self.assertNotEquals(0, self.dlg.PostMessage(win32defines.WM_PAINT))
        self.assertNotEquals(0, self.dlg.Degrees.PostMessage(win32defines.WM_PAINT))

#    def testNotifyMenuSelect(self):
#        "Call NotifyMenuSelect to ensure it does not raise"
#        self.ctrl.NotifyMenuSelect(1234)
#        self.dlg.NotifyMenuSelect(1234)

    def testNotifyParent(self):
        "Call NotifyParent to ensure it does not raise"
        self.ctrl.NotifyParent(1234)
        #self.dlg.NotifyParent(1234)

    def testGetProperties(self):
        "Test getting the properties for the HwndWrapped control"
        props  = self.dlg.GetProperties()

        self.assertEquals(
            self.dlg.FriendlyClassName(), props['FriendlyClassName'])

        self.assertEquals(
            self.dlg.Texts(), props['Texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.dlg, prop_name)(), props[prop_name])

#    def testCaptureAsImage(self):
#        pass

    def testEquals(self):
        self.assertNotEqual(self.ctrl, self.dlg.handle)
        self.assertEqual(self.ctrl, self.ctrl.handle)
        self.assertEqual(self.ctrl, self.ctrl)


#    def testVerifyActionable(self):
#        self.assertRaises()

#    def testVerifyEnabled(self):
#        self.assertRaises()

#    def testVerifyVisible(self):
#        self.assertRaises()


    def testMoveWindow_same(self):
        "Test calling movewindow without any parameters"
        prevRect = self.dlg.Rectangle()
        self.dlg.MoveWindow()
        self.assertEquals(prevRect, self.dlg.Rectangle())

    def testMoveWindow(self):
        "Test moving the window"

        dlgClientRect = self.ctrl.Parent().Rectangle() # use the parent as a reference

        prev_rect = self.ctrl.Rectangle() - dlgClientRect

        new_rect = win32structures.RECT(prev_rect)
        new_rect.left -= 1
        new_rect.top -= 1
        new_rect.right += 2
        new_rect.bottom += 2

        self.ctrl.MoveWindow(
            new_rect.left,
            new_rect.top,
            new_rect.width(),
            new_rect.height(),
            )
        time.sleep(0.1)

        print('prev_rect = ', prev_rect)
        print('new_rect = ', new_rect)
        print('dlgClientRect = ', dlgClientRect)
        print('self.ctrl.Rectangle() = ', self.ctrl.Rectangle())
        self.assertEquals(
            self.ctrl.Rectangle(),
            new_rect + dlgClientRect)

        self.ctrl.MoveWindow(prev_rect)

        self.assertEquals(
            self.ctrl.Rectangle(),
            prev_rect + dlgClientRect)


    def testMaximize(self):
        self.dlg.Maximize()

        self.assertEquals(self.dlg.GetShowState(), win32defines.SW_SHOWMAXIMIZED)
        self.dlg.Restore()

    def testMinimize(self):
        self.dlg.Minimize()
        self.assertEquals(self.dlg.GetShowState(), win32defines.SW_SHOWMINIMIZED)
        self.dlg.Restore()

    def testRestore(self):
        self.dlg.Maximize()
        self.dlg.Restore()
        self.assertEquals(self.dlg.GetShowState(), win32defines.SW_SHOWNORMAL)

        self.dlg.Minimize()
        self.dlg.Restore()
        self.assertEquals(self.dlg.GetShowState(), win32defines.SW_SHOWNORMAL)

    def testGetFocus(self):
        self.assertNotEqual(self.dlg.GetFocus(), None)
        self.assertEqual(self.dlg.GetFocus(), self.ctrl.GetFocus())

        self.dlg.Radians.SetFocus()
        self.assertEqual(self.dlg.GetFocus(), self.dlg.Radians.handle)

    def testSetFocus(self):
        self.assertNotEqual(self.dlg.GetFocus(), self.dlg.Radians.handle)
        self.dlg.Radians.SetFocus()
        self.assertEqual(self.dlg.GetFocus(), self.dlg.Radians.handle)

    def testMenuSelect(self):
        "Test selecting a menu item"

        if not self.dlg.MenuItem("View -> Digit grouping").IsChecked():
            self.dlg.MenuSelect("View -> Digit grouping")

        self.dlg.TypeKeys("1234567")
        self.dlg.MenuSelect("Edit->Copy\tCtrl+C")
        self.dlg.Button8.Click()  # 'Button8' is a class name of the 'CE' button
        self.assertEquals(self.dlg.ChildWindow(class_name='Static', ctrl_index=5).Texts()[0], "0")
        
        # get a pasted text 
        self.dlg.MenuSelect("Edit->Paste\tCtrl+V")
        cur_str = self.dlg.ChildWindow(class_name='Static', ctrl_index=5).Texts()[0]

        # use a regular expression to match the typed string 
        # because on machines with different locales
        # the digit groups can have different spacers. For example:
        # "1,234,567" or "1 234 567" and so on.        
        exp_pattern = u"1.234.567"
        res = re.match(exp_pattern, cur_str)
        self.assertNotEqual(res, None)

    def testClose(self):
        "Test the Close() method of windows"
        # open about dialog
        self.dlg.MenuSelect('Help->About Calculator')
        
        # make sure it is open and visible
        self.app.AboutCalculator.Wait("visible", 20)
        self.assertTrue(self.app.Window_(title='About Calculator').IsVisible(), True)

        # close it
        self.app.Window_(title='About Calculator', class_name='#32770').Close(1)

        # make sure that it is not visible
        try:
            #self.assertRaises(WindowNotFoundError, self.app.Window_(title='About Calculator', class_name='#32770').WrapperObject())
            # vvryabov: TimeoutError is caught by assertRaises, so the second raise is not caught correctly
            self.app.Window_(title='About Calculator', class_name='#32770').WrapperObject()
        except WindowNotFoundError:
            print('WindowNotFoundError exception is raised as expected. OK.')

        # make sure the main calculator dialog is still open
        self.assertEquals(self.dlg.IsVisible(), True)


class HwndWrapperMouseTests(unittest.TestCase):
    "Unit tests for mouse actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application.start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.NoteEdit.handle)

    def tearDown(self):
        "Close the application after tests"

        # close the application
        try:
            self.dlg.Close(0.5)
        except: # timings.TimeoutError:
            pass
        finally:
            self.app.kill_()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.WindowText(), "Untitled - Notepad")


    def testClick(self):
        self.ctrl.Click(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9,9))

    def testClickInput(self):
        self.ctrl.ClickInput(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9,9))

    def testDoubleClick(self):
        self.ctrl.DoubleClick(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (8,13))

    def testDoubleClickInput(self):
        self.ctrl.DoubleClickInput(coords = (80, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (13,18))

#    def testRightClick(self):
#        pass

    def testRightClickInput(self):
        self.dlg.Edit.TypeKeys('{HOME}')
        self.dlg.Edit.Wait('enabled').RightClickInput()
        self.app.PopupMenu.Wait('ready').Menu().GetMenuPath('Select All')[0].Click()
        self.dlg.Edit.TypeKeys('{DEL}')
        self.assertEquals(self.dlg.Edit.TextBlock(), '')

    def testPressMoveRelease(self):
        self.dlg.NoteEdit.PressMouse(coords=(0, 5))
        self.dlg.NoteEdit.MoveMouse(coords=(65, 5))
        self.dlg.NoteEdit.ReleaseMouse(coords=(65, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0,12))

    def testDragMouse(self):
        self.dlg.NoteEdit.DragMouse(press_coords=(0, 5), release_coords=(65, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0,12))
        
        # continue selection with pressed Shift key
        self.dlg.NoteEdit.DragMouse(press_coords=(65, 5), release_coords=(90, 5), pressed='shift')
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0,17))

#    def testSetWindowText(self):
#        pass
#
#    def testTypeKeys(self):
#        pass
#
#    def testDebugMessage(self):
#        pass
#
#    def testDrawOutline(self):
#        pass
#

class NotepadRegressionTests(unittest.TestCase):
    "Regression unit tests for Notepad"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        self.app.start_(_notepad_exe())

        self.dlg = self.app.Window_(title='Untitled - Notepad', class_name='Notepad')
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)
        self.dlg.edit.SetEditText("Here is some text\r\n and some more")

        self.app2 = Application.start(_notepad_exe())


    def tearDown(self):
        "Close the application after tests"

        # close the application
        try:
            self.dlg.Close(0.5)
            if self.app.Notepad["Do&n't Save"].Exists():
                self.app.Notepad["Do&n't Save"].Click()
                self.app.Notepad["Do&n't Save"].WaitNot('visible')
        except: # timings.TimeoutError:
            pass
        finally:
            self.app.kill_()
        self.app2.kill_()

    def testMenuSelectNotepad_bug(self):
        "In notepad - MenuSelect Edit->Paste did not work"

        text = b'Here are some unicode characters \xef\xfc\r\n'
        self.app2.UntitledNotepad.Edit.SetEditText(text)

        self.app2.UntitledNotepad.MenuSelect("Edit->Select All")
        self.app2.UntitledNotepad.MenuSelect("Edit->Copy")

        Timings.after_menu_wait = .7
        self.dlg.MenuSelect("Edit->Select All")
        self.dlg.MenuSelect("Edit->Paste")
        self.dlg.MenuSelect("Edit->Paste")
        self.dlg.MenuSelect("Edit->Paste")

        self.app2.UntitledNotepad.MenuSelect("File->Exit")
        self.app2.Window_(title='Notepad', class_name='#32770')["Don't save"].Click()

        self.assertEquals(self.dlg.Edit.TextBlock().encode(locale.getpreferredencoding()), text*3)


class DragAndDropTests(unittest.TestCase):
    "Unit tests for mouse actions like drag-n-drop"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        self.app.start_(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

    '''
    def testDragMouse(self):
        "DragMouse works! But CmnCtrl1.exe crashes in infinite recursion."
        birds = self.ctrl.GetItem(r'\Birds')
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.ctrl.DragMouse("left", birds.Rectangle().mid_point(), dogs.Rectangle().mid_point())
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.assertEquals([child.Text() for child in dogs.Children()], [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])
    '''

    def testDragMouseInput(self):
        "test for DragMouseInput"
        birds = self.ctrl.GetItem(r'\Birds')
        dogs = self.ctrl.GetItem(r'\Dogs')
        birds.ClickInput()
        time.sleep(5) # enough pause to prevent double click detection
        self.ctrl.DragMouseInput("left", birds.Rectangle().mid_point(), dogs.Rectangle().mid_point())
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.assertEquals([child.Text() for child in dogs.Children()], [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])


class GetDialogPropsFromHandleTest(unittest.TestCase):
    "Unit tests for mouse actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        self.app = Application()
        if is_x64_Python() or not is_x64_OS():
            self.app.start_(r"C:\Windows\System32\notepad.exe")
        else:
            self.app.start_(r"C:\Windows\SysWOW64\notepad.exe")

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.TypeKeys("%{F4}")
        self.dlg.Close(0.5)
        self.app.kill_()


    def test_GetDialogPropsFromHandle(self):
        "Test some small stuff regarding GetDialogPropsFromHandle"

        props_from_handle = GetDialogPropsFromHandle(self.dlg.handle)

        props_from_dialog = GetDialogPropsFromHandle(self.dlg)

        #unused var: props_from_ctrl = GetDialogPropsFromHandle(self.ctrl)

        self.assertEquals(props_from_handle, props_from_dialog)


if __name__ == "__main__":
    unittest.main()

