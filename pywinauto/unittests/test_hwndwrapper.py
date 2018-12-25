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

import mock
from pywinauto.application import Application  # noqa E402
from pywinauto.controls.hwndwrapper import HwndWrapper  # noqa E402
from pywinauto.controls.hwndwrapper import InvalidWindowHandle  # noqa E402
from pywinauto.controls.hwndwrapper import get_dialog_props_from_handle  # noqa E402
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
        Timings.fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.Command_button_here.handle)

        #self.dlg = self.app.Calculator
        #self.dlg.menu_select('View->Scientific\tAlt+2')
        #self.ctrl = HwndWrapper(self.dlg.Button2.handle) # Backspace

    def tearDown(self):
        """Close the application after tests"""
        #self.dlg.type_keys("%{F4}")
        #self.dlg.close()
        self.app.kill()

    def test_scroll(self):
        """Test control scrolling"""
        self.dlg.TabControl.select('CNetworkAddressCtrl')
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
        self.assertEqual(self.ctrl.friendly_class_name(), "Button")

    def testClass(self):
        """Test getting the classname of the control"""
        self.assertEqual(self.ctrl.class_name(), "Button")

    def testWindowText(self):
        """Test getting the window Text of the control"""
        self.assertEqual(
            HwndWrapper(self.dlg.Set.handle).window_text(), u'Set')

    def testStyle(self):
        self.dlg.style()
        self.assertEqual(self.ctrl.style(),
                          win32defines.WS_CHILD |
                          win32defines.WS_VISIBLE |
                          win32defines.WS_TABSTOP |
                          win32defines.BS_COMMANDLINK)

    def testExStyle(self):
        self.assertEqual(self.ctrl.exstyle(),
                          win32defines.WS_EX_NOPARENTNOTIFY |
                          win32defines.WS_EX_LEFT |
                          win32defines.WS_EX_LTRREADING |
                          win32defines.WS_EX_RIGHTSCROLLBAR)

        #self.assertEqual(self.dlg.exstyle(),
        #    win32defines.WS_EX_WINDOWEDGE |
        #    win32defines.WS_EX_LEFT |
        #    win32defines.WS_EX_LTRREADING |
        #    win32defines.WS_EX_RIGHTSCROLLBAR |
        #    win32defines.WS_EX_CONTROLPARENT |
        #    win32defines.WS_EX_APPWINDOW)

    def testControlID(self):
        self.assertEqual(self.ctrl.control_id(), 1037)
        self.dlg.control_id()

    def testUserData(self):
        self.ctrl.user_data()
        self.dlg.user_data()

    def testContextHelpID(self):
        self.ctrl.context_help_id()
        self.dlg.context_help_id()

    def testIsVisible(self):
        self.assertEqual(self.ctrl.is_visible(), True)
        self.assertEqual(self.dlg.is_visible(), True)

    def testIsUnicode(self):
        self.assertEqual(self.ctrl.is_unicode(), True)
        self.assertEqual(self.dlg.is_unicode(), True)

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
        cli = self.dlg.client_rect()

        self.assertEqual(cli.left, 0)
        self.assertEqual(cli.top, 0)

        assert(cli.width() < rect.width())
        assert(cli.height() < rect.height())

    def testFont(self):
        self.assertNotEqual(self.dlg.font(), self.ctrl.font())

    def testProcessID(self):
        self.assertEqual(self.ctrl.process_id(), self.dlg.process_id())
        self.assertNotEqual(self.ctrl.process_id(), 0)

    def testHasStyle(self):
        self.assertEqual(self.ctrl.has_style(win32defines.WS_CHILD), True)
        self.assertEqual(self.dlg.has_style(win32defines.WS_CHILD), False)

        self.assertEqual(self.ctrl.has_style(win32defines.WS_SYSMENU), False)
        self.assertEqual(self.dlg.has_style(win32defines.WS_SYSMENU), True)

    def testHasExStyle(self):
        self.assertEqual(self.ctrl.has_exstyle(win32defines.WS_EX_NOPARENTNOTIFY), True)
        self.assertEqual(self.dlg.has_exstyle(win32defines.WS_EX_NOPARENTNOTIFY), False)

        self.assertEqual(self.ctrl.has_exstyle(win32defines.WS_EX_APPWINDOW), False)
        #self.assertEqual(self.dlg.has_exstyle(win32defines.WS_EX_APPWINDOW), True)

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
        self.assertEqual(self.dlg.child_window(class_name='Button', found_index=2).texts(), [u'Elevation Icon'])

    def testFoundIndex(self):
        """Test an access to a control by found_index"""

        ctl = self.dlg.child_window(class_name='Button', found_index=3)
        self.assertEqual(ctl.texts(), [u'Show'])
        ctl.draw_outline('blue')  # visualize

        # Test an out-of-range access
        # Notice:
        # A ChildWindow call only creates a WindowSpecification object.
        # The exception is raised later when we try to find the window.
        # For this reason we can't use an assertRaises statement here because
        # the exception is raised before actual call to DrawOutline
        ctl = self.dlg.child_window(class_name='Button', found_index=3333)
        self.assertRaises(ElementNotFoundError, ctl.wrapper_object)

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

        ctl = self.dlg.child_window(predicate_func=is_checkbox)
        self.assertEqual(ctl.texts(), [u'Show'])
        ctl.draw_outline('red')  # visualize

    def testClientRects(self):
        self.assertEqual(self.ctrl.client_rects()[0], self.ctrl.client_rect())
        self.assertEqual(self.dlg.client_rects()[0], self.dlg.client_rect())

    def testFonts(self):
        self.assertEqual(self.ctrl.fonts()[0], self.ctrl.font())
        self.assertEqual(self.dlg.fonts()[0], self.dlg.font())

    def testChildren(self):
        self.assertEqual(self.ctrl.children(), [])
        self.assertNotEqual(self.dlg.children(), [])

    def testIsChild(self):
        self.assertEqual(self.ctrl.is_child(self.dlg.wrapper_object()), True)
        self.assertEqual(self.dlg.is_child(self.ctrl), False)

    def testSendMessage(self):
        vk = self.dlg.send_message(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Edit.send_message(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Edit" ? # "Button" = 0x2000 and "Radio" = 0x40
        expected = 0x89  # 0x2000 + 0x40
        self.assertEqual(expected, code)

    def test_send_chars(self):
        testString = "Hello World"

        self.dlg.minimize()
        self.dlg.Edit.send_chars(testString)

        actual = self.dlg.Edit.texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_chars_invalid(self):
        with self.assertRaises(keyboard.KeySequenceError):
            testString = "Hello{LEFT 2}{DEL 2}"

            self.dlg.minimize()
            self.dlg.Edit.send_chars(testString)

    def test_send_keystrokes_multikey_characters(self):
        testString = "Hawaii#{%}@$"

        self.dlg.minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.texts()[0]
        expected = "Hawaii#%@$"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_enter(self):
        with self.assertRaises(findbestmatch.MatchError):
            testString = "{ENTER}"

            self.dlg.minimize()
            self.dlg.Edit.send_keystrokes(testString)

            self.dlg.restore()

    def test_send_keystrokes_virtual_keys_left_del_back(self):
        testString = "+hello123{LEFT 2}{DEL 2}{BACKSPACE} +world"

        self.dlg.minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_virtual_keys_shift(self):
        testString = "+hello +world"

        self.dlg.minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.texts()[0]
        expected = "Hello World"
        self.assertEqual(expected, actual)

    def test_send_keystrokes_virtual_keys_ctrl(self):
        testString = "^a^c{RIGHT}^v"

        self.dlg.minimize()
        self.dlg.Edit.send_keystrokes(testString)

        actual = self.dlg.Edit.texts()[0]
        expected = "and the note goes here ...and the note goes here ..."
        self.assertEqual(expected, actual)

    def testSendMessageTimeout(self):
        default_timeout = Timings.sendmessagetimeout_timeout
        Timings.sendmessagetimeout_timeout = 0.1
        vk = self.dlg.send_message_timeout(win32defines.WM_GETDLGCODE)
        self.assertEqual(0, vk)

        code = self.dlg.Show.send_message_timeout(win32defines.WM_GETDLGCODE)
        # The expected return code is: "Button" = 0x2000 # and "Radio" = 0x40
        expected = 0x2000  # + 0x40
        Timings.sendmessagetimeout_timeout = default_timeout
        self.assertEqual(expected, code)

    def testPostMessage(self):
        self.assertNotEqual(0, self.dlg.post_message(win32defines.WM_PAINT))
        self.assertNotEqual(0, self.dlg.Show.post_message(win32defines.WM_PAINT))

#    def testNotifyMenuSelect(self):
#        "Call NotifyMenuSelect to ensure it does not raise"
#        self.ctrl.NotifyMenuSelect(1234)
#        self.dlg.NotifyMenuSelect(1234)

    def testNotifyParent(self):
        """Call notify_parent to ensure it does not raise"""
        self.ctrl.notify_parent(1234)
        #self.dlg.notify_parent(1234)

    def testGetProperties(self):
        """Test getting the properties for the HwndWrapped control"""
        props = self.dlg.get_properties()

        self.assertEqual(
            self.dlg.friendly_class_name(), props['friendly_class_name'])

        self.assertEqual(
            self.dlg.texts(), props['texts'])

        for prop_name in props:
            self.assertEqual(getattr(self.dlg, prop_name)(), props[prop_name])

    def test_capture_as_image_multi_monitor(self):
        with mock.patch('win32api.EnumDisplayMonitors') as mon_device:
            mon_device.return_value = (1, 2)
            rect = self.dlg.rectangle()
            expected = (rect.width(), rect.height())
            result = self.dlg.capture_as_image().size
            self.assertEqual(expected, result)

    # def testDrawOutline(self):
    #     """Test the outline was drawn."""
    #     # make sure window is ready
    #     self.dlg.wait('active')
    #     self.dlg.Show.click()
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
        self.dlg.move_window()
        self.assertEqual(prevRect, self.dlg.rectangle())

    def testMoveWindow(self):
        """Test moving the window"""

        dlgClientRect = self.ctrl.parent().rectangle()  # use the parent as a reference

        prev_rect = self.ctrl.rectangle() - dlgClientRect

        new_rect = win32structures.RECT(prev_rect)
        new_rect.left -= 1
        new_rect.top -= 1
        new_rect.right += 2
        new_rect.bottom += 2

        self.ctrl.move_window(
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
        self.assertEqual(
            self.ctrl.rectangle(),
            new_rect + dlgClientRect)

        self.ctrl.move_window(prev_rect)

        self.assertEqual(
            self.ctrl.rectangle(),
            prev_rect + dlgClientRect)

    def testMaximize(self):
        self.dlg.maximize()

        self.assertEqual(self.dlg.get_show_state(), win32defines.SW_SHOWMAXIMIZED)
        self.dlg.restore()

    def testMinimize(self):
        self.dlg.minimize()
        self.assertEqual(self.dlg.get_show_state(), win32defines.SW_SHOWMINIMIZED)
        self.dlg.restore()

    def testRestore(self):
        self.dlg.maximize()
        self.dlg.restore()
        self.assertEqual(self.dlg.get_show_state(), win32defines.SW_SHOWNORMAL)

        self.dlg.minimize()
        self.dlg.restore()
        self.assertEqual(self.dlg.get_show_state(), win32defines.SW_SHOWNORMAL)

    def testGetFocus(self):
        self.assertNotEqual(self.dlg.get_focus(), None)
        self.assertEqual(self.dlg.get_focus(), self.ctrl.get_focus())

        self.dlg.Set.set_focus()
        self.assertEqual(self.dlg.get_focus(), self.dlg.Set.handle)

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
        self.assertNotEqual(self.dlg.get_focus(), self.dlg.Set.handle)
        self.dlg.Set.set_focus()
        self.assertEqual(self.dlg.get_focus(), self.dlg.Set.handle)

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
        Timings.defaults()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"RowList.exe"))

        self.dlg = self.app.RowListSampleApplication
        self.ctrl = self.app.RowListSampleApplication.ListView.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)

    def testMenuItems(self):
        """Test getting menu items"""
        self.assertEqual(self.ctrl.menu_items(), [])
        self.assertEqual(self.dlg.menu_items()[1]['text'], '&View')

    def testMenuSelect(self):
        """Test selecting a menu item"""

        if self.dlg.menu_item("View -> Toolbar").is_checked():
            self.dlg.menu_select("View -> Toolbar")
        self.assertEqual(self.dlg.menu_item("View -> Toolbar").is_checked(), False)

        self.dlg.menu_select("View -> Toolbar")
        self.assertEqual(self.dlg.menu_item("View -> Toolbar").is_checked(), True)

    def testClose(self):
        """Test the Close() method of windows"""
        # open about dialog
        self.dlg.menu_select('Help->About RowList...')

        # make sure it is open and visible
        self.app.AboutRowList.wait("visible", 20)
        self.assertTrue(self.app.window(title='About RowList').is_visible(), True)

        # close it
        self.app.window(title='About RowList', class_name='#32770').close(1)

        # make sure that it is not visible
        try:
            #self.assertRaises(ElementNotFoundError,
            #                  self.app.window(title='About RowList', class_name='#32770').wrapper_object())
            # vvryabov: TimeoutError is caught by assertRaises, so the second raise is not caught correctly
            self.app.window(title='About RowList', class_name='#32770').wrapper_object()
        except ElementNotFoundError:
            print('ElementNotFoundError exception is raised as expected. OK.')

        # make sure the main RowList dialog is still open
        self.assertEqual(self.dlg.is_visible(), True)

    def testCloseClick_bug(self):
        self.dlg.menu_select('Help->About RowList...')
        self.app.AboutRowList.wait("visible", 10)

        self.assertEqual(self.app.AboutRowList.exists(), True)
        self.app.AboutRowList.CloseButton.close_click()
        self.assertEqual(self.app.AboutRowList.exists(), False)

        #Timings.closeclick_dialog_close_wait = .7
        #try:
        #    self.app.AboutRowList.CloseButton.close_click()
        #except TimeoutError:
        #    pass
        #self.app.AboutRowList.close()

    def testCloseAltF4(self):
        self.dlg.menu_select('Help->About RowList...')
        AboutRowList = self.app.window(title='About RowList', active_only=True, class_name='#32770')
        AboutWrapper = AboutRowList.wait("enabled")
        AboutRowList.close_alt_f4()
        AboutRowList.wait_not('visible')
        self.assertNotEqual(AboutWrapper.is_visible(), True)


class HwndWrapperMouseTests(unittest.TestCase):

    """Unit tests for mouse actions of the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.select('CButton (Command Link)')
        self.ctrl = HwndWrapper(self.dlg.NoteEdit.handle)

    def tearDown(self):
        """Close the application after tests"""
        try:
            self.dlg.close(0.5)
        except Exception:  # TimeoutError:
            pass
        finally:
            self.app.kill()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEqual(self.dlg.window_text(), "Untitled - Notepad")

    def testClick(self):
        self.ctrl.click(coords=(50, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (9, 9))

    def testClickInput(self):
        self.ctrl.click_input(coords=(50, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (9, 9))

    def testDoubleClick(self):
        self.ctrl.double_click(coords=(50, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (8, 13))

    def testDoubleClickInput(self):
        self.ctrl.double_click_input(coords=(80, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (13, 18))

#    def testRightClick(self):
#        pass

    def testRightClickInput(self):
        self.dlg.Edit.type_keys('{HOME}')
        self.dlg.Edit.wait('enabled').right_click_input()
        self.app.PopupMenu.wait('ready').menu().get_menu_path('Select All')[0].click_input()
        self.dlg.Edit.type_keys('{DEL}')
        self.assertEqual(self.dlg.Edit.text_block(), '')

    def testPressMoveRelease(self):
        self.dlg.NoteEdit.press_mouse(coords=(0, 5))
        self.dlg.NoteEdit.move_mouse(coords=(65, 5))
        self.dlg.NoteEdit.release_mouse(coords=(65, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (0, 12))

    def testDragMouse(self):
        self.dlg.NoteEdit.drag_mouse(press_coords=(0, 5), release_coords=(65, 5))
        self.assertEqual(self.dlg.Edit.selection_indices(), (0, 12))

        # continue selection with pressed Shift key
        self.dlg.NoteEdit.drag_mouse(press_coords=(65, 5), release_coords=(90, 5), pressed='shift')
        self.assertEqual(self.dlg.Edit.selection_indices(), (0, 17))

    def testDebugMessage(self):
        self.dlg.NoteEdit.debug_message('Test message')
        # TODO: add screenshots comparison

    #def testDrawOutline(self):
    #    # TODO: add screenshots comparison
    #    self.dlg.draw_outline()

#    def testSetWindowText(self):
#        pass
#
#    def testTypeKeys(self):
#        pass

    def testSetTransparency(self):
        self.dlg.set_transparency()
        self.assertRaises(ValueError, self.dlg.set_transparency, 256)


class NonActiveWindowFocusTests(unittest.TestCase):

    """Regression unit tests for setting focus"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl3.exe"))
        self.app2 = Application().start(_notepad_exe())

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()
        self.app2.kill()

    def test_issue_240(self):
        """Check HwndWrapper.set_focus for a desktop without a focused window"""
        ws = self.app.Common_Controls_Sample
        ws.TabControl.select('CButton (Command Link)')
        dlg1 = ws.wrapper_object()
        dlg2 = self.app2.Notepad.wrapper_object()
        dlg2.click(coords=(2, 2))
        dlg2.minimize()
        # here is the trick: the window is restored but it isn't activated
        dlg2.restore()
        dlg1.set_focus()
        self.assertEqual(ws.get_focus(), ws.Edit.wrapper_object())


class WindowWithoutMessageLoopFocusTests(unittest.TestCase):

    """
    Regression unit tests for setting focus when window does not have
    a message loop.
    """

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app1 = Application().start(u"cmd.exe",
                                        create_new_console=True,
                                        wait_for_idle=False)
        self.app2 = Application().start(os.path.join(
            mfc_samples_folder, u"CmnCtrl2.exe"))
        self.app2.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1)

    def tearDown(self):
        """Close the application after tests"""
        self.app1.kill()
        self.app2.kill()

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
        Timings.fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.window(title='Untitled - Notepad', class_name='Notepad')
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)
        self.dlg.Edit.set_edit_text("Here is some text\r\n and some more")

        self.app2 = Application().start(_notepad_exe())

    def tearDown(self):
        """Close the application after tests"""
        try:
            self.app.UntitledNotepad.menu_select("File->Exit")
            self.app.Notepad["Do&n't Save"].click()
            self.app.Notepad["Do&n't Save"].wait_not('visible')
        except Exception:  # TimeoutError:
            pass
        finally:
            self.app.kill()
        self.app2.kill()

    def testMenuSelectNotepad_bug(self):
        """In notepad - MenuSelect Edit->Paste did not work"""
        text = b'Here are some unicode characters \xef\xfc\r\n'
        self.app2.UntitledNotepad.Edit.wait('enabled')
        time.sleep(0.3)
        self.app2.UntitledNotepad.Edit.set_edit_text(text)
        time.sleep(0.3)
        self.assertEqual(self.app2.UntitledNotepad.Edit.text_block().encode(locale.getpreferredencoding()), text)

        Timings.after_menu_wait = .7
        self.app2.UntitledNotepad.menu_select("Edit->Select All")
        time.sleep(0.3)
        self.app2.UntitledNotepad.menu_select("Edit->Copy")
        time.sleep(0.3)
        self.assertEqual(clipboard.GetData().encode(locale.getpreferredencoding()), text)

        self.dlg.set_focus()
        self.dlg.menu_select("Edit->Select All")
        self.dlg.menu_select("Edit->Paste")
        self.dlg.menu_select("Edit->Paste")
        self.dlg.menu_select("Edit->Paste")

        self.app2.UntitledNotepad.menu_select("File->Exit")
        self.app2.window(title='Notepad', class_name='#32770')["Don't save"].click()

        self.assertEqual(self.dlg.Edit.text_block().encode(locale.getpreferredencoding()), text * 3)


class ControlStateTests(unittest.TestCase):

    """Unit tests for control states"""

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it.
        """

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.select(4)
        self.ctrl = self.dlg.EditBox.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_VerifyEnabled(self):
        """Test for verify_enabled"""
        self.assertRaises(ElementNotEnabled, self.ctrl.verify_enabled)

    def test_VerifyVisible(self):
        """Test for verify_visible"""
        self.dlg.TabControl.select(3)
        self.assertRaises(ElementNotVisible, self.ctrl.verify_visible)


class DragAndDropTests(unittest.TestCase):

    """Unit tests for mouse actions like drag-n-drop"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.defaults()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    #def testDragMouse(self):
    #    """drag_mouse works! But CmnCtrl1.exe crashes in infinite recursion."""
    #    birds = self.ctrl.get_item(r'\Birds')
    #    dogs = self.ctrl.get_item(r'\Dogs')
    #    self.ctrl.drag_mouse("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
    #    dogs = self.ctrl.get_item(r'\Dogs')
    #    self.assertEqual([child.Text() for child in dogs.children()],
    #                      [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])

    def testDragMouseInput(self):
        """Test for drag_mouse_input"""
        birds = self.ctrl.get_item(r'\Birds')
        dogs = self.ctrl.get_item(r'\Dogs')
        #birds.select()
        birds.click_input()
        time.sleep(5)  # enough pause to prevent double click detection
        self.ctrl.drag_mouse_input(dst=dogs.client_rect().mid_point(),
                                   src=birds.client_rect().mid_point(),
                                   absolute=False)
        dogs = self.ctrl.get_item(r'\Dogs')
        self.assertEqual([child.text() for child in dogs.children()],
                          [u'Birds', u'Dalmatian', u'German Shepherd', u'Great Dane'])


class GetDialogPropsFromHandleTest(unittest.TestCase):

    """Unit tests for mouse actions of the HwndWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        #self.dlg.type_keys("%{F4}")
        self.dlg.close(0.5)
        self.app.kill()

    def test_GetDialogPropsFromHandle(self):
        """Test some small stuff regarding GetDialogPropsFromHandle"""
        props_from_handle = get_dialog_props_from_handle(self.dlg.handle)
        props_from_dialog = get_dialog_props_from_handle(self.dlg)
        #unused var: props_from_ctrl = get_dialog_props_from_handle(self.ctrl)

        self.assertEqual(props_from_handle, props_from_dialog)


class SendEnterKeyTest(unittest.TestCase):
    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application()
        self.app.start(_notepad_exe())

        self.dlg = self.app.UntitledNotepad
        self.ctrl = HwndWrapper(self.dlg.Edit.handle)

    def tearDown(self):
        self.dlg.menu_select('File -> Exit')
        try:
            self.app.Notepad["Do&n't Save"].click()
        except findbestmatch.MatchError:
            self.app.kill()

    def test_sendEnterChar(self):
        self.ctrl.send_chars('Hello{ENTER}World')
        self.assertEqual('Hello\r\nWorld', self.dlg.Edit.window_text())


class SendKeystrokesAltComboTests(unittest.TestCase):

    """Unit test for Alt- combos sent via send_keystrokes"""

    def setUp(self):
        Timings.defaults()

        self.app = Application().start(os.path.join(mfc_samples_folder, u'CtrlTest.exe'))
        self.dlg = self.app.Control_Test_App

    def tearDown(self):
        self.app.kill()

    def test_send_keystrokes_alt_combo(self):
        self.dlg.send_keystrokes('%(sc)')

        self.assertTrue(self.app['Using C++ Derived Class'].exists())


class RemoteMemoryBlockTests(unittest.TestCase):

    """Unit tests for RemoteMemoryBlock"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.fast()

        self.app = Application()
        self.app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.ctrl = self.dlg.TreeView.wrapper_object()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def testGuardSignatureCorruption(self):
        mem = RemoteMemoryBlock(self.ctrl, 16)
        buf = ctypes.create_string_buffer(24)

        self.assertRaises(Exception, mem.Write, buf)

        mem.size = 24  # test hack
        self.assertRaises(Exception, mem.Write, buf)


if __name__ == "__main__":
    unittest.main()
