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

import ctypes
import locale
import re
import win32clipboard

import sys, os
import unittest
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.controls.HwndWrapper import HwndWrapper, \
                InvalidWindowHandle, GetDialogPropsFromHandle
from pywinauto import win32structures, win32defines
from pywinauto.findwindows import ElementNotFoundError, ElementNotFoundError
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto.RemoteMemoryBlock import RemoteMemoryBlock
from pywinauto.timings import Timings, TimeoutError
from pywinauto import clipboard
from pywinauto import backend
from pywinauto.base_wrapper import ElementNotEnabled, ElementNotVisible
from pywinauto import findbestmatch
from pywinauto.SendKeysCtypes import SendKeys

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

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.Command_button_here.handle)

        #self.dlg = self.app.Calculator
        #self.dlg.MenuSelect('View->Scientific\tAlt+2')
        #self.ctrl = HwndWrapper(self.dlg.Button2.handle) # Backspace

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.type_keys("%{F4}")
        #self.dlg.Close()
        self.app.kill_()

    def testInvalidHandle(self):
        "Test that an exception is raised with an invalid window handle"
        self.assertRaises(InvalidWindowHandle, HwndWrapper, -1)

    def testFriendlyClassName(self):
        "Test getting the friendly classname of the control"
        self.assertEquals(self.ctrl.friendly_class_name(), "Button")


    def testClass(self):
        "Test getting the classname of the control"
        self.assertEquals(self.ctrl.class_name(), "Button")

    def testWindowText(self):
        "Test getting the window Text of the control"
        self.assertEquals(
            HwndWrapper(self.dlg.Set.handle).window_text(), u'Set')

    def testStyle(self):

        self.dlg.Style()

        self.assertEquals(self.ctrl.Style(),
            win32defines.WS_CHILD |
            win32defines.WS_VISIBLE |
            win32defines.WS_TABSTOP |
            win32defines.BS_COMMANDLINK)


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
        self.assertEquals(self.ctrl.control_id(), 1037)
        self.dlg.control_id()

    def testUserData(self):
        self.ctrl.UserData()
        self.dlg.UserData()

    def testContextHelpID(self):
        self.ctrl.ContextHelpID()
        self.dlg.ContextHelpID()

    def testIsVisible(self):
        self.assertEqual(self.ctrl.is_visible(), True)
        self.assertEqual(self.dlg.is_visible(), True)

    def testIsUnicode(self):
        self.assertEqual(self.ctrl.IsUnicode(), True)
        self.assertEqual(self.dlg.IsUnicode(), True)

    def testIsEnabled(self):
        self.assertEqual(self.ctrl.is_enabled(), True)
        self.assertEqual(self.dlg.is_enabled(), True)
        #self.assertEqual(self.dlg.Note.is_enabled(), False); # Button26 = '%'

    def testRectangle(self):
        "Test getting the rectangle of the dialog"
        rect = self.dlg.rectangle()
        
        self.assertNotEqual(rect.top, None)
        self.assertNotEqual(rect.left, None)
        self.assertNotEqual(rect.bottom, None)
        self.assertNotEqual(rect.right, None)

        if abs(rect.height() - 423) > 5:
            self.assertEqual(rect.height(), 423)
        if abs(rect.width() - 506) > 5:
            self.assertEqual(rect.width(), 506)

    def testClientRect(self):
        rect = self.dlg.rectangle()
        cli = self.dlg.ClientRect()

        self.assertEqual(cli.left , 0)
        self.assertEqual(cli.top , 0)

        assert(cli.width() < rect.width())
        assert(cli.height() < rect.height())

    def testFont(self):
        self.assertNotEqual(self.dlg.Font(), self.ctrl.Font())

    def testProcessID(self):
        self.assertEqual(self.ctrl.process_id(), self.dlg.process_id())
        self.assertNotEqual(self.ctrl.process_id(), 0)

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
        self.assertEqual(self.ctrl.is_dialog(), False)
        self.assertEqual(self.dlg.is_dialog(), True)

    def testParent(self):
        self.assertEqual(self.ctrl.parent().parent(), self.dlg.handle)

    def testTopLevelParent(self):
        self.assertEqual(self.ctrl.top_level_parent(), self.dlg.handle)
        self.assertEqual(self.dlg.top_level_parent(), self.dlg.handle)

    def testTexts(self):
        self.assertEqual(self.dlg.texts(), ['Common Controls Sample'])
        self.assertEqual(HwndWrapper(self.dlg.Show.handle).texts(), [u'Show'])
        self.assertEqual(self.dlg.ChildWindow(class_name='Button', found_index=2).texts(), [u'Elevation Icon'])

    def testFoundIndex(self):
        "test an access to a control by found_index"

        ctl = self.dlg.ChildWindow(class_name='Button', found_index=3)
        self.assertEqual(ctl.texts(), [u'Show'])
        ctl.DrawOutline('blue')  # visualize
        
        # Test an out-of-range access
        # Notice:
        # A ChildWindow call only creates a WindowSpecification object.
        # The exception is raised later when we try to find the window.
        # For this reason we can't use an assertRaises statement here because
        # the exception is raised before actual call to DrawOutline
        ctl = self.dlg.ChildWindow(class_name='Button', found_index=3333)
        self.assertRaises(ElementNotFoundError, ctl.WrapperObject)

    def testSearchWithPredicateFunc(self):
        "test an access to a control by filtering with a predicate function"

        def is_checkbox(elem):
            res = False
            if elem.handle is None:
                return False
            hwwrp = HwndWrapper(elem.handle)
            if hwwrp.friendly_class_name() == u'CheckBox':
                if hwwrp.texts() == [u'Show']:
                    res = True
            return res

        ctl = self.dlg.ChildWindow(predicate_func=is_checkbox)
        self.assertEqual(ctl.texts(), [u'Show'])
        ctl.DrawOutline('red')  # visualize

    def testClientRects(self):
        self.assertEqual(self.ctrl.ClientRects()[0], self.ctrl.ClientRect())
        self.assertEqual(self.dlg.ClientRects()[0], self.dlg.ClientRect())

    def testFonts(self):
        self.assertEqual(self.ctrl.Fonts()[0], self.ctrl.Font())
        self.assertEqual(self.dlg.Fonts()[0], self.dlg.Font())

    def testChildren(self):
        self.assertEqual(self.ctrl.children(), [])
        self.assertNotEqual(self.dlg.children(), [])


    def testIsChild(self):
        self.assertEqual(self.ctrl.is_child(self.dlg.WrapperObject()), True)
        self.assertEqual(self.dlg.is_child(self.ctrl), False)


    def testSendMessage(self):
        vk = self.dlg.SendMessage(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Edit.SendMessage(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Edit" ? # "Button" = 0x2000 and "Radio" = 0x40
        expected = 0x89 # 0x2000 + 0x40
        self.assertEqual(expected, code)

    def test_send_chars_simple(self):
        testString = "Hello World"

        self.dlg.Minimize()
        self.dlg.Edit.send_chars(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    # def test_send_chars_enter(self):
    #     with self.assertRaises(findbestmatch.MatchError):
    #         testString = "{ENTER}"
    #
    #         self.dlg.Minimize()
    #         self.dlg.Edit.send_chars(testString)
    #
    #         actual = self.dlg.Edit.Texts()[0]

    def test_send_chars_virtual_keys_left_del_back(self):
        testString = "Hello123{LEFT 2}{DEL 2}{BACKSPACE} World"

        self.dlg.Minimize()
        self.dlg.Edit.send_chars(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_chars_virtual_keys_shift(self):
        testString = "+hello +world"

        self.dlg.Minimize()
        self.dlg.Edit.send_chars(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    # def test_send_chars_virtual_keys_ctrl(self):
    #     testString = "^a^c{RIGHT}^v"
    #
    #     self.dlg.Minimize()
    #     self.dlg.Edit.send_chars(testString)
    #
    #     actual = self.dlg.Edit.Texts()[0]
    #     expected = "and the note goes here ...and the note goes here ..."
    #     self.assertEqual(expected, actual)

    def testSendMessageTimeout(self):
        default_timeout = Timings.sendmessagetimeout_timeout
        Timings.sendmessagetimeout_timeout = 0.1
        vk = self.dlg.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Show.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Button" = 0x2000 # and "Radio" = 0x40
        expected = 0x2000 #+ 0x40
        Timings.sendmessagetimeout_timeout = default_timeout
        self.assertEqual(expected, code)

    def testPostMessage(self):
        self.assertNotEquals(0, self.dlg.PostMessage(win32defines.WM_PAINT))
        self.assertNotEquals(0, self.dlg.Show.PostMessage(win32defines.WM_PAINT))

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
            self.dlg.friendly_class_name(), props['friendly_class_name'])

        self.assertEquals(
            self.dlg.texts(), props['texts'])

        for prop_name in props:
            self.assertEquals(getattr(self.dlg, prop_name)(), props[prop_name])

#    def testCaptureAsImage(self):
#        pass

    # def testDrawOutline(self):
    #     """Test the outline was drawn."""
    #     # make sure window is ready
    #     self.dlg.Wait('active')
    #     self.dlg.Show.Click()
    #
    #     # not sure why, but this extra call makes the test stable
    #     self.dlg.draw_outline()
    #
    #     # outline control
    #     self.dlg.Show.draw_outline()
    #     img1 = self.dlg.Show.capture_as_image()
    #     self.assertEqual(img1.getpixel((0, 0)), (0, 255, 0))  # green
    #
    #     # outline window
    #     self.dlg.draw_outline(colour="red")
    #     img2 = self.dlg.capture_as_image()
    #     self.assertEqual(img2.getpixel((0, 0)), (255, 0, 0))  # red

    def testEquals(self):
        self.assertNotEqual(self.ctrl, self.dlg.handle)
        self.assertEqual(self.ctrl, self.ctrl.handle)
        self.assertEqual(self.ctrl, self.ctrl)


#    def testVerifyActionable(self):


    def testMoveWindow_same(self):
        "Test calling movewindow without any parameters"
        prevRect = self.dlg.rectangle()
        self.dlg.MoveWindow()
        self.assertEquals(prevRect, self.dlg.rectangle())

    def testMoveWindow(self):
        "Test moving the window"

        dlgClientRect = self.ctrl.parent().rectangle() # use the parent as a reference

        prev_rect = self.ctrl.rectangle() - dlgClientRect

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
        print('self.ctrl.rectangle() = ', self.ctrl.rectangle())
        self.assertEquals(
            self.ctrl.rectangle(),
            new_rect + dlgClientRect)

        self.ctrl.MoveWindow(prev_rect)

        self.assertEquals(
            self.ctrl.rectangle(),
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

        self.dlg.Set.set_focus()
        self.assertEqual(self.dlg.GetFocus(), self.dlg.Set.handle)

    def testSetFocus(self):
        self.assertNotEqual(self.dlg.GetFocus(), self.dlg.Set.handle)
        self.dlg.Set.set_focus()
        self.assertEqual(self.dlg.GetFocus(), self.dlg.Set.handle)


class HwndWrapperMenuTests(unittest.TestCase):
    "Unit tests for menu actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application().start(os.path.join(mfc_samples_folder, u"RowList.exe"))
        
        self.dlg = self.app.RowListSampleApplication
        self.ctrl = self.app.RowListSampleApplication.ListView.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testMenuItems(self):
        self.assertEqual(self.ctrl.MenuItems(), [])
        self.assertEqual(self.dlg.MenuItems()[1]['text'], '&View')

    def testMenuSelect(self):
        "Test selecting a menu item"

        if self.dlg.MenuItem("View -> Toolbar").IsChecked():
            self.dlg.MenuSelect("View -> Toolbar")
        self.assertEquals(self.dlg.MenuItem("View -> Toolbar").IsChecked(), False)

        self.dlg.MenuSelect("View -> Toolbar")
        self.assertEquals(self.dlg.MenuItem("View -> Toolbar").IsChecked(), True)

    def testClose(self):
        "Test the Close() method of windows"
        # open about dialog
        self.dlg.MenuSelect('Help->About RowList...')
        
        # make sure it is open and visible
        self.app.AboutRowList.Wait("visible", 20)
        self.assertTrue(self.app.Window_(title='About RowList').is_visible(), True)

        # close it
        self.app.Window_(title='About RowList', class_name='#32770').Close(1)

        # make sure that it is not visible
        try:
            #self.assertRaises(ElementNotFoundError, self.app.Window_(title='About RowList', class_name='#32770').WrapperObject())
            # vvryabov: TimeoutError is caught by assertRaises, so the second raise is not caught correctly
            self.app.Window_(title='About RowList', class_name='#32770').WrapperObject()
        except ElementNotFoundError:
            print('ElementNotFoundError exception is raised as expected. OK.')

        # make sure the main RowList dialog is still open
        self.assertEquals(self.dlg.is_visible(), True)

    def testCloseClick_bug(self):
        self.dlg.MenuSelect('Help->About RowList...')
        self.app.AboutRowList.Wait("visible", 10)

        self.assertEqual(self.app.AboutRowList.Exists(), True)
        self.app.AboutRowList.CloseButton.CloseClick()
        self.assertEqual(self.app.AboutRowList.Exists(), False)

        #Timings.closeclick_dialog_close_wait = .7
        #try:
        #    self.app.AboutRowList.CloseButton.CloseClick()
        #except TimeoutError:
        #    pass
        #self.app.AboutRowList.Close()

    def testCloseAltF4(self):
        self.dlg.MenuSelect('Help->About RowList...')
        AboutRowList = self.app.Window_(title='About RowList', active_only=True, class_name='#32770')
        AboutWrapper = AboutRowList.Wait("enabled")
        AboutRowList.CloseAltF4()
        AboutRowList.WaitNot('visible')
        self.assertNotEqual(AboutWrapper.is_visible(), True)



class HwndWrapperMouseTests(unittest.TestCase):
    "Unit tests for mouse actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.NoteEdit.handle)

    def tearDown(self):
        "Close the application after tests"

        # close the application
        try:
            self.dlg.Close(0.5)
        except Exception: # TimeoutError:
            pass
        finally:
            self.app.kill_()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.window_text(), "Untitled - Notepad")


    def testClick(self):
        self.ctrl.Click(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9,9))

    def testClickInput(self):
        self.ctrl.click_input(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9,9))

    def testDoubleClick(self):
        self.ctrl.DoubleClick(coords = (50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (8,13))

    def testDoubleClickInput(self):
        self.ctrl.double_click_input(coords = (80, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (13,18))

#    def testRightClick(self):
#        pass

    def testRightClickInput(self):
        self.dlg.Edit.type_keys('{HOME}')
        self.dlg.Edit.Wait('enabled').right_click_input()
        self.app.PopupMenu.Wait('ready').Menu().GetMenuPath('Select All')[0].click_input()
        self.dlg.Edit.type_keys('{DEL}')
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

    def testDebugMessage(self):
        self.dlg.NoteEdit.DebugMessage('Test message')
        # TODO: add screenshots comparison

    #def testDrawOutline(self):
    #    # TODO: add screenshots comparison
    #    self.dlg.DrawOutline()

#    def testSetWindowText(self):
#        pass
#
#    def testTypeKeys(self):
#        pass

    def testSetTransparency(self):
        self.dlg.SetTransparency()
        self.assertRaises(ValueError, self.dlg.SetTransparency, 256)


class HwndWrapperMouseWheelTests(unittest.TestCase):
    "Unit tests for mouse wheel actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start(os.path.join(mfc_samples_folder, u"RowList.exe"))
        self.dlg = self.app.RowListSampleApplication
        self.dlg.MenuSelect("View -> Large Icons")
        prev_rect = self.dlg.rectangle()
        list_view_r = self.dlg.ListViewRed.rectangle()
        new_rect = win32structures.RECT(prev_rect)
        new_rect.right -= list_view_r.right
        new_rect.bottom -= list_view_r.bottom
        self.dlg.MoveWindow(
            new_rect.left,
            new_rect.top,
            new_rect.width(),
            new_rect.height(),
            )

    def tearDown(self):
        "Close the application after tests"
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testWheelMouse(self):
        prev_pos = self.dlg.get_scroll_pos(win32defines.SB_VERT)
        self.dlg.wheel_mouse(-120, "control")
        cur_pos = self.dlg.get_scroll_pos(win32defines.SB_VERT)
        self.assertNotEquals(prev_pos, cur_pos)

    def testGetScrollInfo(self):
        self.dlg.scroll("right", "page")
        self.assertTrue(self.dlg.get_scroll_info(win32defines.SB_HORZ))

    def testGetScrollPos(self):
        self.dlg.scroll("right", "page")
        scr_info = self.dlg.get_scroll_info(win32defines.SB_HORZ)
        pos = scr_info.nPos
        self.assertEquals(pos, self.dlg.get_scroll_pos(win32defines.SB_HORZ))

    def testGetScrollBarInfo(self):
        self.dlg.scroll("right", "page")
        scr_info = self.dlg.get_scroll_bar_info(win32defines.OBJID_CLIENT)
        self.assertTrue(scr_info.dxyLineButton)

class NotepadRegressionTests(unittest.TestCase):
    "Regression unit tests for Notepad"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.Window_(title='Untitled - Notepad', class_name='Notepad')
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)
        self.dlg.Edit.SetEditText("Here is some text\r\n and some more")

        self.app2 = Application().start(_notepad_exe())


    def tearDown(self):
        "Close the application after tests"

        # close the application
        try:
            self.dlg.Close(0.5)
            if self.app.Notepad["Do&n't Save"].Exists():
                self.app.Notepad["Do&n't Save"].Click()
                self.app.Notepad["Do&n't Save"].WaitNot('visible')
        except Exception: # TimeoutError:
            pass
        finally:
            self.app.kill_()
        self.app2.kill_()

    def testMenuSelectNotepad_bug(self):
        "In notepad - MenuSelect Edit->Paste did not work"

        text = b'Here are some unicode characters \xef\xfc\r\n'
        self.app2.UntitledNotepad.Edit.Wait('enabled')
        time.sleep(0.3)
        self.app2.UntitledNotepad.Edit.SetEditText(text)
        time.sleep(0.3)
        self.assertEquals(self.app2.UntitledNotepad.Edit.TextBlock().encode(locale.getpreferredencoding()), text)

        Timings.after_menu_wait = .7
        self.app2.UntitledNotepad.MenuSelect("Edit->Select All")
        time.sleep(0.3)
        self.app2.UntitledNotepad.MenuSelect("Edit->Copy")
        time.sleep(0.3)
        self.assertEquals(clipboard.GetData().encode(locale.getpreferredencoding()), text)

        self.dlg.set_focus()
        self.dlg.MenuSelect("Edit->Select All")
        self.dlg.MenuSelect("Edit->Paste")
        self.dlg.MenuSelect("Edit->Paste")
        self.dlg.MenuSelect("Edit->Paste")

        self.app2.UntitledNotepad.MenuSelect("File->Exit")
        self.app2.Window_(title='Notepad', class_name='#32770')["Don't save"].Click()

        self.assertEquals(self.dlg.Edit.TextBlock().encode(locale.getpreferredencoding()), text*3)
		

class ControlStateTests(unittest.TestCase):
    """Unit tests for control states"""
	
    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.ctrl = self.dlg.EditBox.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()
		
    def test_VerifyEnabled(self):
        """test for verify_enabled"""
        self.assertRaises(ElementNotEnabled, self.ctrl.verify_enabled)

    def test_VerifyVisible(self):
        """test for verify_visible"""
        self.dlg.TabControl.Select(3)
        self.assertRaises(ElementNotVisible, self.ctrl.verify_visible)
		
class DragAndDropTests(unittest.TestCase):
    "Unit tests for mouse actions like drag-n-drop"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

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
        self.ctrl.DragMouse("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.assertEquals([child.Text() for child in dogs.children()], [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])
    '''

    def testDragMouseInput(self):
        "test for drag_mouse_input"
        birds = self.ctrl.GetItem(r'\Birds')
        dogs = self.ctrl.GetItem(r'\Dogs')
        #birds.Select()
        birds.click_input()
        time.sleep(5) # enough pause to prevent double click detection
        self.ctrl.drag_mouse_input("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.assertEquals([child.Text() for child in dogs.children()], [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])


class GetDialogPropsFromHandleTest(unittest.TestCase):
    "Unit tests for mouse actions of the HwndWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.type_keys("%{F4}")
        self.dlg.Close(0.5)
        self.app.kill_()


    def test_GetDialogPropsFromHandle(self):
        "Test some small stuff regarding GetDialogPropsFromHandle"

        props_from_handle = GetDialogPropsFromHandle(self.dlg.handle)

        props_from_dialog = GetDialogPropsFromHandle(self.dlg)

        #unused var: props_from_ctrl = GetDialogPropsFromHandle(self.ctrl)

        self.assertEquals(props_from_handle, props_from_dialog)


class RemoteMemoryBlockTests(unittest.TestCase):
    "Unit tests for RemoteMemoryBlock"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.WrapperObject()

    def tearDown(self):
        "Close the application after tests"
        self.app.kill_()

    def testGuardSignatureCorruption(self):
        mem = RemoteMemoryBlock(self.ctrl, 16)
        buf = ctypes.create_string_buffer(24)
        
        self.assertRaises(Exception, mem.Write, buf)
        
        mem.size = 24 # test hack
        self.assertRaises(Exception, mem.Write, buf)


if __name__ == "__main__":
    unittest.main()

