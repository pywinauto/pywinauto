"""Tests for win32 hooks"""
from __future__ import print_function
from __future__ import unicode_literals

import sys
import time
import unittest
import win32api
# import win32con
from threading import Timer

sys.path.append(".")
import pywinauto.actionlogger
from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent
# from pywinauto.win32_hooks import MouseEvent
from pywinauto.keyboard import SendKeys, KeyAction, VirtualKeyAction


class Win32HooksTests(unittest.TestCase):

    """Unit tests for the Win32Hook class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        pywinauto.actionlogger.enable()
        self.logger = pywinauto.actionlogger.ActionLogger()
        self.hook = Hook()
        self.hook.handler = self.on_hook_event
        self.wait_time = 2.0
        self.timer = None
        self.main_thread_id = win32api.GetCurrentThreadId()

    def tearDown(self):
        """Close the application after tests"""
        if self.timer:
            self.timer.cancel()
        self.unregister_hooks()

    def trace(self, msg, *args):
        """Log the specified message"""
        self.logger.log(msg.format(*args))

    def on_hook_event(self, args):
        """Callback for keyboard and mouse events"""
        self.trace("Win32hooksTest::on_hook_event")
        self.trace("{0}", args)
        if isinstance(args, KeyboardEvent):
            self.trace("Win32hooksTest::on_hook_event got KeyboardEvnent: key={0} type={1}",
                       args.current_key,
                       args.event_type)
            if args.current_key == 'u' and args.event_type == 'key down':
                self.trace("u key is down")

    def unregister_hooks(self):
        """Unregister all hooks"""
        self.trace("Win32HooksTest::unregister_hooks")
        self.hook.unhook_keyboard()
        self.hook.unhook_mouse()

    def type_keys_and_unhook(self):
        """A timer callback to type keys and unhook"""
        SendKeys(u'uk')
        #k = KeyAction('u', down=True, up=False)
        #k.run()
        #k = KeyAction('k', down=True, up=False)
        #k.run()
        #k = KeyAction('k', down=False, up=True)
        #k.run()
        #k = KeyAction('u', down=False, up=True)
        #k.run()
        time.sleep(1)
        self.unregister_hooks()

    def test_keyboard_hook(self):
        """Test setting a keyboard hook"""
        self.timer = Timer(self.wait_time, self.type_keys_and_unhook)
        self.timer.start()
        self.hook.hook(keyboard=True, mouse=False)
        #time.sleep(self.wait_time + 1.2)
        #print("unhook from test")
        #hk.unhook_keyboard()

    # def test_mouse_hook(self):
    #     """Test setting a mouse hook"""
    #     pass

if __name__ == "__main__":
    unittest.main()
