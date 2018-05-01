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

"""Tests for HwndWrapper"""
from __future__ import print_function
from __future__ import unicode_literals

import six
import time
#import pprint
#import pdb
#import warnings

import ctypes
import locale

import sys
import os
import unittest
sys.path.append(".")
from pywinauto.application import Application  # noqa E402
from pywinauto.controls.hwndwrapper import HwndWrapper  # noqa E402
from pywinauto.controls.hwndwrapper import InvalidWindowHandle  # noqa E402
from pywinauto.controls.hwndwrapper import GetDialogPropsFromHandle  # noqa E402
from pywinauto import win32structures  # noqa E402
from pywinauto import win32defines  # noqa E402
from pywinauto.findwindows import ElementNotFoundError  # noqa E402
from pywinauto.sysinfo import is_x64_Python  # noqa E402
from pywinauto.sysinfo import is_x64_OS  # noqa E402
from pywinauto.remote_memory_block import RemoteMemoryBlock  # noqa E402
from pywinauto.timings import Timings  # noqa E402
from pywinauto import clipboard  # noqa E402
from pywinauto.base_wrapper import ElementNotEnabled  # noqa E402
from pywinauto.base_wrapper import ElementNotVisible  # noqa E402
from pywinauto import findbestmatch  # noqa E402
from pywinauto import keyboard  # noqa E402


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

    """Unit tests for the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.Command_button_here.handle)

        #self.dlg = self.app.Calculator
        #self.dlg.MenuSelect('View->Scientific\tAlt+2')
        #self.ctrl = HwndWrapper(self.dlg.Button2.handle) # Backspace

    def tearDown(self):
        """Close the application after tests"""
        #self.dlg.type_keys("%{F4}")
        #self.dlg.Close()
        self.app.kill_()

    def test_scroll(self):
        """Test control scrolling"""
        self.dlg.TabControl.Select('CNetworkAddressCtrl')
        ctrl = HwndWrapper(self.dlg.TypeListBox.handle)

        # Check exceptions on wrong arguments
        self.assertRaises(ValueError, ctrl.scroll, "bbbb", "line")
        self.assertRaises(ValueError, ctrl.scroll, "left", "aaaa")

        self.assertEqual(ctrl.item_rect(0).top, 0)
        ctrl.scroll('down', 'page', 2)
        self.assertEqual(ctrl.item_rect(0).top < -10, True)

    def testInvalidHandle(self):
        """Test that an exception is raised with an invalid window handle"""
        self.assertRaises(InvalidWindowHandle, HwndWrapper, -1)

    def testFriendlyClassName(self):
        """Test getting the friendly classname of the control"""
        self.assertEquals(self.ctrl.friendly_class_name(), "Button")

    def testClass(self):
        """Test getting the classname of the control"""
        self.assertEquals(self.ctrl.class_name(), "Button")

    def testWindowText(self):
        """Test getting the window Text of the control"""
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

        #self.assertEquals(self.dlg.ExStyle(),
        #    win32defines.WS_EX_WINDOWEDGE |
        #    win32defines.WS_EX_LEFT |
        #    win32defines.WS_EX_LTRREADING |
        #    win32defines.WS_EX_RIGHTSCROLLBAR |
        #    win32defines.WS_EX_CONTROLPARENT |
        #    win32defines.WS_EX_APPWINDOW)

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
        """Test getting the rectangle of the dialog"""
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

        self.assertEqual(cli.left, 0)
        self.assertEqual(cli.top, 0)

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
        """Test an access to a control by found_index"""

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
        """Test an access to a control by filtering with a predicate function"""

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
        expected = 0x89  # 0x2000 + 0x40
        self.assertEqual(expected, code)

    def test_send_chars(self):
        testString = "Hello World"

        self.dlg.Minimize()
        self.dlg.Edit.send_chars(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_chars_invalid(self):
        with self.assertRaises(keyboard.KeySequenceError):
            testString = "Hello{LEFT 2}{DEL 2}"

            self.dlg.Minimize()
            self.dlg.Edit.send_chars(testString)

    def test_send_keystrokes_multikey_characters(self):
        testString = "Hawaii#{%}@$"

        self.dlg.Minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hawaii#%@$"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_enter(self):
        with self.assertRaises(findbestmatch.MatchError):
            testString = "{ENTER}"

            self.dlg.Minimize()
            self.dlg.Edit.send_keystrokes(testString)

            self.dlg.Restore()

    def test_send_keystrokes_virtual_keys_left_del_back(self):
        testString = "+hello123{LEFT 2}{DEL 2}{BACKSPACE} +world"

        self.dlg.Minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_virtual_keys_shift(self):
        testString = "+hello +world"

        self.dlg.Minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_virtual_keys_ctrl(self):
        testString = "^a^c{RIGHT}^v"

        self.dlg.Minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.Texts()[0]
        expected = "and the note goes here ...and the note goes here ..."
        self.assertEqual(expected, actual)

    def testSendMessageTimeout(self):
        default_timeout = Timings.sendmessagetimeout_timeout
        Timings.sendmessagetimeout_timeout = 0.1
        vk = self.dlg.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Show.SendMessageTimeout(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Button" = 0x2000 # and "Radio" = 0x40
        expected = 0x2000  # + 0x40
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
        """Call NotifyParent to ensure it does not raise"""
        self.ctrl.NotifyParent(1234)
        #self.dlg.NotifyParent(1234)

    def testGetProperties(self):
        """Test getting the properties for the HwndWrapped control"""
        props = self.dlg.GetProperties()

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
        """Test calling movewindow without any parameters"""
        prevRect = self.dlg.rectangle()
        self.dlg.MoveWindow()
        self.assertEquals(prevRect, self.dlg.rectangle())

    def testMoveWindow(self):
        """Test moving the window"""

        dlgClientRect = self.ctrl.parent().rectangle()  # use the parent as a reference

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

    def test_issue_318(self):
        self.dlg.restore()
        self.dlg.minimize()
        self.dlg.set_focus()
        self.assertTrue(self.dlg.is_normal())
        self.assertTrue(self.dlg.is_active())

        self.dlg.maximize()
        self.dlg.minimize()
        self.dlg.set_focus()
        self.assertTrue(self.dlg.is_maximized())
        self.assertTrue(self.dlg.is_active())
        self.dlg.restore()

    def testSetFocus(self):
        self.assertNotEqual(self.dlg.GetFocus(), self.dlg.Set.handle)
        self.dlg.Set.set_focus()
        self.assertEqual(self.dlg.GetFocus(), self.dlg.Set.handle)

    def testHasKeyboardFocus(self):
        self.assertFalse(self.dlg.set.has_keyboard_focus())
        self.dlg.set.set_keyboard_focus()
        self.assertTrue(self.dlg.set.has_keyboard_focus())

    def testSetKeyboardFocus(self):
        self.assertNotEqual(self.dlg.get_focus(), self.dlg.set.handle)
        self.dlg.set.set_keyboard_focus()
        self.assertEqual(self.dlg.get_focus(), self.dlg.set.handle)

    def test_pretty_print(self):
        """Test __str__ method for HwndWrapper based controls"""
        if six.PY3:
            assert_regex = self.assertRegex
        else:
            assert_regex = self.assertRegexpMatches

        wrp = self.dlg.wrapper_object()
        assert_regex(wrp.__str__(), "^hwndwrapper.DialogWrapper - 'Common Controls Sample', Dialog$")
        assert_regex(wrp.__repr__(), "^<hwndwrapper.DialogWrapper - 'Common Controls Sample', Dialog, [0-9-]+>$")

        wrp = self.ctrl
        assert_regex(wrp.__str__(), "^win32_controls.ButtonWrapper - 'Command button here', Button$")
        assert_regex(wrp.__repr__(), "^<win32_controls.ButtonWrapper - 'Command button here', Button, [0-9-]+>$")

        wrp = self.dlg.TabControl.wrapper_object()
        assert_regex(wrp.__str__(), "^common_controls.TabControlWrapper - '', TabControl$")
        assert_regex(wrp.__repr__(), "^<common_controls.TabControlWrapper - '', TabControl, [0-9-]+>$")

    def test_children_generator(self):
        dlg = self.dlg.wrapper_object()
        children = [child for child in dlg.iter_children()]
        self.assertSequenceEqual(dlg.children(), children)


class HwndWrapperMenuTests(unittest.TestCase):

    """Unit tests for menu actions of the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Defaults()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"RowList.exe"))

        self.dlg = self.app.RowListSampleApplication
        self.ctrl = self.app.RowListSampleApplication.ListView.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.SendMessage(win32defines.WM_CLOSE)

    def testMenuItems(self):
        """Test getting menu items"""
        self.assertEqual(self.ctrl.MenuItems(), [])
        self.assertEqual(self.dlg.MenuItems()[1]['text'], '&View')

    def testMenuSelect(self):
        """Test selecting a menu item"""

        if self.dlg.MenuItem("View -> Toolbar").IsChecked():
            self.dlg.MenuSelect("View -> Toolbar")
        self.assertEquals(self.dlg.MenuItem("View -> Toolbar").IsChecked(), False)

        self.dlg.MenuSelect("View -> Toolbar")
        self.assertEquals(self.dlg.MenuItem("View -> Toolbar").IsChecked(), True)

    def testClose(self):
        """Test the Close() method of windows"""
        # open about dialog
        self.dlg.MenuSelect('Help->About RowList...')

        # make sure it is open and visible
        self.app.AboutRowList.Wait("visible", 20)
        self.assertTrue(self.app.Window_(title='About RowList').is_visible(), True)

        # close it
        self.app.Window_(title='About RowList', class_name='#32770').Close(1)

        # make sure that it is not visible
        try:
            #self.assertRaises(ElementNotFoundError,
            #                  self.app.Window_(title='About RowList', class_name='#32770').wrapper_object())
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

    """Unit tests for mouse actions of the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.NoteEdit.handle)

    def tearDown(self):
        """Close the application after tests"""
        try:
            self.dlg.Close(0.5)
        except Exception:  # TimeoutError:
            pass
        finally:
            self.app.kill_()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.window_text(), "Untitled - Notepad")

    def testClick(self):
        self.ctrl.Click(coords=(50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9, 9))

    def testClickInput(self):
        self.ctrl.click_input(coords=(50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (9, 9))

    def testDoubleClick(self):
        self.ctrl.DoubleClick(coords=(50, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (8, 13))

    def testDoubleClickInput(self):
        self.ctrl.double_click_input(coords=(80, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (13, 18))

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
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0, 12))

    def testDragMouse(self):
        self.dlg.NoteEdit.DragMouse(press_coords=(0, 5), release_coords=(65, 5))
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0, 12))

        # continue selection with pressed Shift key
        self.dlg.NoteEdit.DragMouse(press_coords=(65, 5), release_coords=(90, 5), pressed='shift')
        self.assertEquals(self.dlg.Edit.SelectionIndices(), (0, 17))

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


class NonActiveWindowFocusTests(unittest.TestCase):

    """Regression unit tests for setting focus"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))
        self.app2 = Application().start(_notepad_exe())

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()
        self.app2.kill_()

    def test_issue_240(self):
        """Check HwndWrapper.set_focus for a desktop without a focused window"""
        ws = self.app.Common_Controls_Sample
        ws.TabControl.Select('CButton (Command Link)')
        dlg1 = ws.wrapper_object()
        dlg2 = self.app2.Notepad.wrapper_object()
        dlg2.click(coords=(2, 2))
        dlg2.minimize()
        # here is the trick: the window is restored but it isn't activated
        dlg2.restore()
        dlg1.set_focus()
        self.assertEqual(ws.GetFocus(), ws.Edit.wrapper_object())


class WindowWithoutMessageLoopFocusTests(unittest.TestCase):

    """
    Regression unit tests for setting focus when window does not have
    a message loop.
    """

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app1 = Application().start(u"cmd.exe",
                                        create_new_console=True,
                                        wait_for_idle=False)
        self.app2 = Application().start(os.path.join(
            mfc_samples_folder, u"CmnCtrl2.exe"))
        self.app2.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1)

    def tearDown(self):
        """Close the application after tests"""
        self.app1.kill_()
        self.app2.kill_()

    def test_issue_270(self):
        """
        Set focus to a window without a message loop, then switch to a window
        with one and type in it.
        """
        self.app1.window().set_focus()
        self.app1.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1)
        # pywintypes.error:
        #     (87, 'AttachThreadInput', 'The parameter is incorrect.')

        self.app2.window().edit.type_keys("1")
        # cmd.exe into python.exe;  pywintypes.error:
        #     (87, 'AttachThreadInput', 'The parameter is incorrect.')
        # python.exe on its own;  pywintypes.error:
        #     (0, 'SetForegroundWindow', 'No error message is available')
        self.assertTrue(self.app2.window().is_active())


class NotepadRegressionTests(unittest.TestCase):

    """Regression unit tests for Notepad"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.Window_(title='Untitled - Notepad', class_name='Notepad')
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)
        self.dlg.Edit.SetEditText("Here is some text\r\n and some more")

        self.app2 = Application().start(_notepad_exe())

    def tearDown(self):
        """Close the application after tests"""
        try:
            self.dlg.Close(0.5)
            if self.app.Notepad["Do&n't Save"].Exists():
                self.app.Notepad["Do&n't Save"].Click()
                self.app.Notepad["Do&n't Save"].WaitNot('visible')
        except Exception:  # TimeoutError:
            pass
        finally:
            self.app.kill_()
        self.app2.kill_()

    def testMenuSelectNotepad_bug(self):
        """In notepad - MenuSelect Edit->Paste did not work"""
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

        self.assertEquals(self.dlg.Edit.TextBlock().encode(locale.getpreferredencoding()), text * 3)


class ControlStateTests(unittest.TestCase):

    """Unit tests for control states"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it.
        """

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.ctrl = self.dlg.EditBox.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()

    def test_VerifyEnabled(self):
        """Test for verify_enabled"""
        self.assertRaises(ElementNotEnabled, self.ctrl.verify_enabled)

    def test_VerifyVisible(self):
        """Test for verify_visible"""
        self.dlg.TabControl.Select(3)
        self.assertRaises(ElementNotVisible, self.ctrl.verify_visible)


class DragAndDropTests(unittest.TestCase):

    """Unit tests for mouse actions like drag-n-drop"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Defaults()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()

    #def testDragMouse(self):
    #    """DragMouse works! But CmnCtrl1.exe crashes in infinite recursion."""
    #    birds = self.ctrl.GetItem(r'\Birds')
    #    dogs = self.ctrl.GetItem(r'\Dogs')
    #    self.ctrl.DragMouse("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
    #    dogs = self.ctrl.GetItem(r'\Dogs')
    #    self.assertEquals([child.Text() for child in dogs.children()],
    #                      [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])

    def testDragMouseInput(self):
        """Test for drag_mouse_input"""
        birds = self.ctrl.GetItem(r'\Birds')
        dogs = self.ctrl.GetItem(r'\Dogs')
        #birds.Select()
        birds.click_input()
        time.sleep(5)  # enough pause to prevent double click detection
        self.ctrl.drag_mouse_input(dst=dogs.client_rect().mid_point(),
                                   src=birds.client_rect().mid_point(),
                                   absolute=False)
        dogs = self.ctrl.GetItem(r'\Dogs')
        self.assertEquals([child.Text() for child in dogs.children()],
                          [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])


class GetDialogPropsFromHandleTest(unittest.TestCase):

    """Unit tests for mouse actions of the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        #self.dlg.type_keys("%{F4}")
        self.dlg.Close(0.5)
        self.app.kill_()

    def test_GetDialogPropsFromHandle(self):
        """Test some small stuff regarding GetDialogPropsFromHandle"""
        props_from_handle = GetDialogPropsFromHandle(self.dlg.handle)
        props_from_dialog = GetDialogPropsFromHandle(self.dlg)
        #unused var: props_from_ctrl = GetDialogPropsFromHandle(self.ctrl)

        self.assertEquals(props_from_handle, props_from_dialog)


class SendEnterKeyTest(unittest.TestCase):
    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        self.dlg.MenuSelect('File -> Exit')
        if self.dlg["Do&n't Save"].Exists():
            self.dlg["Do&n't Save"].Click()
        self.app.kill_()

    def test_sendEnterChar(self):
        self.ctrl.send_chars('Hello{ENTER}World')
        self.assertEquals(['Hello\r\nWorld'], self.dlg.Edit.Texts())


class SendKeystrokesAltComboTests(unittest.TestCase):

    """Unit test for Alt- combos sent via send_keystrokes"""

    def setUp(self):
        Timings.Defaults()

        self.app = Application().start(os.path.join(mfc_samples_folder, u'CtrlTest.exe'))
        self.dlg = self.app.Control_Test_App

    def tearDown(self):
        self.app.kill_()

    def test_send_keystrokes_alt_combo(self):
        self.dlg.send_keystrokes('%(sc)')

        self.assertTrue(self.app['Using C++ Derived Class'].Exists())


class RemoteMemoryBlockTests(unittest.TestCase):

    """Unit tests for RemoteMemoryBlock"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.Fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.WrapperObject()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill_()

    def testGuardSignatureCorruption(self):
        mem = RemoteMemoryBlock(self.ctrl, 16)
        buf = ctypes.create_string_buffer(24)

        self.assertRaises(Exception, mem.Write, buf)

        mem.size = 24  # test hack
        self.assertRaises(Exception, mem.Write, buf)


if __name__ == "__main__":
    unittest.main()
