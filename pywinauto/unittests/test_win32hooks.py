"""Tests for win32 hooks"""
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import time
import unittest
import atexit
import mock
import win32con
from ctypes import windll
from threading import Timer

sys.path.append(".")
import pywinauto.actionlogger
from pywinauto import win32structures
from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent
from pywinauto.win32_hooks import MouseEvent
from pywinauto.keyboard import SendKeys
from pywinauto.mouse import click
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python


def _delete_keys_from_terminal(keys):
    """Emulate BACK key press

    A helper to remove the keys that has been sent to the terminal during a test.
    We don't care if BACK is pressed more than required when special codes were used.
    """
    if keys:
        SendKeys('{BACK ' + str(len(keys)) + '}')


class Win32HooksTests(unittest.TestCase):

    """Unit tests for the Win32Hook class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        self.logger = pywinauto.actionlogger.ActionLogger()
        self.hook = Hook()
        self.hook.handler = self._on_hook_event
        self.wait_time = 0.4
        self.short_wait_time = self.wait_time / 4.0
        self.timer = None
        self.keybd_events = []
        self.mouse_events = []
        self.app = None

        # prevent capturing keyboard keys when launching a test manually
        time.sleep(self.short_wait_time)

    def tearDown(self):
        """Close all hooks after tests"""
        self.keybd_events = []
        self.mouse_events = []
        if self.timer:
            self.timer.cancel()
        self.hook.stop()
        if self.app:
            self.app.kill_()

    def _get_safe_point_to_click(self):
        """Run notepad.exe to have a safe area for mouse clicks"""

        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
        sample_exe = os.path.join(mfc_samples_folder, "CmnCtrl1.exe")
        self.app = Application()
        self.app.start(sample_exe)
        self.app.CommonControlsSample.wait("ready")
        return self.app.CommonControlsSample.rectangle().mid_point()

    def _sleep_and_unhook(self):
        """A helper to remove all hooks after a pause"""
        time.sleep(self.short_wait_time)
        self.hook.stop()

    def trace(self, msg, *args):
        """Log the specified message"""
        self.logger.log(msg.format(*args))

    def _on_hook_event(self, args):
        """Callback for keyboard events"""
        if isinstance(args, KeyboardEvent):
            self.trace(
                "Win32HooksTests::_on_hook_event got KeyboardEvent: key={0} type={1}",
                args.current_key,
                args.event_type)
            self.keybd_events.append(args)
        elif isinstance(args, MouseEvent):
            self.trace(
                "Win32HooksTests::_on_hook_event got MouseEvent: key={0} type={1}",
                args.current_key,
                args.event_type)
            self.mouse_events.append(args)

    def _type_keys_and_unhook(self, key_strokes):
        """A timer callback to type key strokes and unhook"""
        SendKeys(key_strokes)

        # Give a time to process the keys by the hook
        self._sleep_and_unhook()

    def test_keyboard_hook_unicode_sequence(self):
        """Test capturing a sequence of unicode keystrokes by a keyboard hook"""
        keys = u'uk'
        self.timer = Timer(self.wait_time, self._type_keys_and_unhook, [keys])
        self.timer.start()
        self.hook.hook(keyboard=True, mouse=False)
        # Continue here only when the hook will be removed by the timer
        _delete_keys_from_terminal(keys)
        self.assertEqual(len(self.keybd_events), 4)
        self.assertEqual(self.keybd_events[0].current_key, u'u')
        self.assertEqual(self.keybd_events[0].event_type, 'key down')
        self.assertEqual(len(self.keybd_events[0].pressed_key), 0)
        self.assertEqual(self.keybd_events[1].current_key, u'u')
        self.assertEqual(self.keybd_events[1].event_type, 'key up')
        self.assertEqual(len(self.keybd_events[1].pressed_key), 0)
        self.assertEqual(self.keybd_events[2].current_key, u'k')
        self.assertEqual(self.keybd_events[2].event_type, 'key down')
        self.assertEqual(len(self.keybd_events[2].pressed_key), 0)
        self.assertEqual(self.keybd_events[3].current_key, u'k')
        self.assertEqual(self.keybd_events[3].event_type, 'key up')
        self.assertEqual(len(self.keybd_events[3].pressed_key), 0)

    def test_keyboard_hook_parallel_pressed_keys(self):
        """Test capturing parallel pressed keys by a keyboard hook"""
        keys = u'+a'
        self.timer = Timer(self.wait_time, self._type_keys_and_unhook, [keys])
        self.timer.start()
        self.hook.hook(keyboard=True, mouse=False)
        # Continue here only when the hook will be removed by the timer
        _delete_keys_from_terminal(keys)
        self.assertEqual(len(self.keybd_events), 4)
        self.assertEqual(self.keybd_events[0].current_key, u'Lshift')
        self.assertEqual(self.keybd_events[0].event_type, 'key down')
        self.assertEqual(len(self.keybd_events[0].pressed_key), 0)
        self.assertEqual(self.keybd_events[1].current_key, u'A')
        self.assertEqual(self.keybd_events[1].event_type, 'key down')
        self.assertEqual(len(self.keybd_events[1].pressed_key), 0)
        self.assertEqual(self.keybd_events[2].current_key, u'A')
        self.assertEqual(self.keybd_events[2].event_type, 'key up')
        self.assertEqual(len(self.keybd_events[2].pressed_key), 0)
        self.assertEqual(self.keybd_events[3].current_key, u'Lshift')
        self.assertEqual(self.keybd_events[3].event_type, 'key up')
        self.assertEqual(len(self.keybd_events[3].pressed_key), 0)

    def _mouse_click_and_unhook(self, coords):
        """A timer callback to perform a mouse click and unhook"""
        click(coords=coords)

        # Give a time to process the mouse clicks by the hook
        self._sleep_and_unhook()

    def test_mouse_hook(self):
        """Test capturing a sequence of mouse clicks by hook"""

        # Get a safe point to click
        pt = self._get_safe_point_to_click()
        coords = [(pt.x, pt.y)]

        # Set a timer to perform a click and hook the mouse
        self.timer = Timer(self.wait_time, self._mouse_click_and_unhook, coords)
        self.timer.start()
        self.hook.hook(keyboard=False, mouse=True)
        # Continue here only when the hook will be removed by the timer
        self.assertEqual(len(self.mouse_events), 2)
        self.assertEqual(self.mouse_events[0].current_key, u'LButton')
        self.assertEqual(self.mouse_events[0].event_type, 'key down')
        self.assertEqual(self.mouse_events[0].mouse_x, pt.x)
        self.assertEqual(self.mouse_events[0].mouse_y, pt.y)
        self.assertEqual(self.mouse_events[1].current_key, u'LButton')
        self.assertEqual(self.mouse_events[1].event_type, 'key up')
        self.assertEqual(self.mouse_events[1].mouse_x, pt.x)
        self.assertEqual(self.mouse_events[1].mouse_y, pt.y)


def _on_hook_event_with_exception(args):
    """Callback for keyboard and mouse events that raises an exception"""
    raise ValueError()


class Win32HooksWithMocksTests(unittest.TestCase):

    """Unit tests for the Win32Hook class with mocks for low level dependencies"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        self.hook = Hook()

        # Save pointers to original system calls before mocking
        self.CallNextHookEx = windll.user32.CallNextHookEx
        self.PeekMessageW = windll.user32.PeekMessageW
        self.TranslateMessage = windll.user32.TranslateMessage
        self.DispatchMessageW = windll.user32.DispatchMessageW
        self.atexit_register = atexit.register
        self.sys_exit = sys.exit
        self.fake_kbhook_id = 22
        self.fake_mousehook_id = 33

    def tearDown(self):
        """Cleanups after finishing a test"""
        self.hook.stop()

        # Restore the pointers to original system calls after mocking
        windll.user32.CallNextHookEx = self.CallNextHookEx
        windll.user32.PeekMessageW = self.PeekMessageW
        windll.user32.TranslateMessage = self.TranslateMessage
        windll.user32.DispatchMessageW = self.DispatchMessageW
        atexit.register = self.atexit_register
        sys.exit = self.sys_exit

    def test_none_hook_handler(self):
        """Test running a hook without a handler

        The next hook in chain still should be called
        Simulate an odd situation when we got a hook ID (a hook is inserted)
        but a handler for the hook processing wasn't supplied by a user
        """
        self.hook.keyboard_id = self.fake_kbhook_id
        self.hook.mouse_id = self.fake_mousehook_id
        self.hook.handler = None

        # replace the system API with a mock object
        windll.user32.CallNextHookEx = mock.Mock(return_value=0)
        # prepare arguments for _keyboard_ll_hdl call
        kbd = win32structures.KBDLLHOOKSTRUCT(0, 0, 0, 0, 0)
        res = self.hook._keyboard_ll_hdl(-1, 3, id(kbd))
        windll.user32.CallNextHookEx.assert_called_with(self.fake_kbhook_id, -1, 3, id(kbd))
        self.assertEqual(res, 0)

        # Setup a fresh mock object and arguments for _mouse_ll_hdl call
        windll.user32.CallNextHookEx = mock.Mock(return_value=0)
        mouse = win32structures.MSLLHOOKSTRUCT((11, 12), 0, 0, 0, 0)
        res = self.hook._mouse_ll_hdl(-1, 3, id(mouse))
        self.assertEqual(res, 0)
        windll.user32.CallNextHookEx.assert_called_with(self.fake_mousehook_id, -1, 3, id(mouse))

    def test_keyboard_hook_exception(self):
        """Test handling an exception in a keyboard hook"""
        self.hook.handler = _on_hook_event_with_exception
        windll.user32.CallNextHookEx = mock.Mock(return_value=0)
        kbd = win32structures.KBDLLHOOKSTRUCT(0, 0, 0, 0, 0)
        self.hook.keyboard_id = self.fake_kbhook_id

        # Verify CallNextHookEx is called even if there is an exception is raised
        self.assertRaises(ValueError, self.hook._keyboard_ll_hdl, -1, 3, id(kbd))
        windll.user32.CallNextHookEx.assert_called()
        windll.user32.CallNextHookEx.assert_called_with(self.fake_kbhook_id, -1, 3, id(kbd))
        self.assertRaises(ValueError, self.hook._keyboard_ll_hdl, 0, 3, id(kbd))
        windll.user32.CallNextHookEx.assert_called()
        windll.user32.CallNextHookEx.assert_called_with(self.fake_kbhook_id, 0, 3, id(kbd))

    def test_mouse_hook_exception(self):
        """Test handling an exception in a mouse hook"""
        self.hook.handler = _on_hook_event_with_exception
        windll.user32.CallNextHookEx = mock.Mock(return_value=0)
        mouse = win32structures.MSLLHOOKSTRUCT((11, 12), 0, 0, 0, 0)
        self.hook.mouse_id = self.fake_mousehook_id

        # Verify CallNextHookEx is called even if there is an exception is raised
        self.assertRaises(ValueError, self.hook._mouse_ll_hdl, -1, 3, id(mouse))
        windll.user32.CallNextHookEx.assert_called()
        windll.user32.CallNextHookEx.assert_called_with(self.fake_mousehook_id, -1, 3, id(mouse))
        self.assertRaises(ValueError, self.hook._mouse_ll_hdl, 0, 3, id(mouse))
        windll.user32.CallNextHookEx.assert_called()
        windll.user32.CallNextHookEx.assert_called_with(self.fake_mousehook_id, 0, 3, id(mouse))

    @mock.patch.object(Hook, '_process_win_msgs')
    @mock.patch.object(Hook, 'is_hooked')
    def test_listen_loop(self, mock_is_hooked, mock_process_msgs):
        """Test running the main events loop"""
        atexit.register = mock.Mock(return_value=0)
        mock_is_hooked.side_effect = [1, 0]  # exit at a second loop
        mock_process_msgs.return_value = 0

        # mock hook IDs
        self.hook.keyboard_id = self.fake_kbhook_id
        self.hook.mouse_id = self.fake_mousehook_id

        # run the events loop
        self.hook.listen()

        # verify atexit.register calls
        atexit.register.assert_called()
        self.assertEqual(len(atexit.register.mock_calls), 2)
        name, args, kwargs = atexit.register.mock_calls[0]
        self.assertEqual(args[1], self.fake_kbhook_id)
        name, args, kwargs = atexit.register.mock_calls[1]
        self.assertEqual(args[1], self.fake_mousehook_id)

        # verify is_hooked method calls
        mock_is_hooked.assert_called()
        self.assertEqual(len(mock_is_hooked.mock_calls), 2)

        # verify _process_win_msgs method has been called
        mock_process_msgs.assert_called()
        self.assertEqual(len(mock_process_msgs.mock_calls), 1)

    @mock.patch.object(Hook, 'stop')
    def test_process_win_msg(self, mock_stop):
        """Test Hook._process_win_msgs"""
        # Mock external API
        windll.user32.PeekMessageW = mock.Mock(side_effect=[1, 0])
        windll.user32.TranslateMessage = mock.Mock()
        windll.user32.DispatchMessageW = mock.Mock()

        # Test processing the normal messages
        self.hook._process_win_msgs()
        windll.user32.PeekMessageW.assert_called()
        windll.user32.TranslateMessage.assert_called()
        windll.user32.DispatchMessageW.assert_called()

        # Test processing WM_QUIT
        def side_effect(*args):
            """Emulate reception of WM_QUIT"""
            args[0].contents.message = win32con.WM_QUIT
            return 1
        windll.user32.PeekMessageW = mock.Mock(side_effect=side_effect)
        self.assertRaises(SystemExit, self.hook._process_win_msgs)
        mock_stop.assert_called_once()

    def test_is_hooked(self):
        """Verify Hook.is_hooked method"""
        self.assertEqual(self.hook.is_hooked(), False)
        self.hook.mouse_is_hook = True
        self.assertEqual(self.hook.is_hooked(), True)
        self.hook.mouse_is_hook = False
        self.assertEqual(self.hook.is_hooked(), False)
        self.hook.keyboard_is_hook = True
        self.assertEqual(self.hook.is_hooked(), True)
        self.hook.keyboard_is_hook = False
        self.assertEqual(self.hook.is_hooked(), False)
        self.hook.hook(mouse=False, keyboard=False)
        self.assertEqual(self.hook.is_hooked(), False)


if __name__ == "__main__":
    unittest.main()
