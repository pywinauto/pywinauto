"Tests for mouse.py"

import time
import ctypes
import locale
import re
import subprocess
import sys
import os
import win32clipboard
import unittest

sys.path.append(".")
from pywinauto.application import Application
from pywinauto.SendKeysCtypes import SendKeys
from pywinauto import mouse


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/MouseTester")
    if sys.platform == 'win32':
        return os.path.join(test_folder, "mousebuttons.exe")
    else:
        return os.path.join(test_folder, "mousebuttons")


class MouseTests(unittest.TestCase):

    def setUp(self):
        self.app = Application()
        self.app.start(_test_app())
        self.dlg = self.app.mousebuttons

    def tearDown(self):
        time.sleep(1)
        self.app.kill_()

    def __get_pos(self, shift):
        rect = self.dlg.rectangle()
        return rect.left + shift, rect.top + shift

    def __get_text(self):
        SendKeys('^a')
        SendKeys('^c')
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data

    def test_position(self):
        left, top = self.__get_pos(60)
        mouse.click(coords=(left, top))
        data = self.__get_text()
        self.assertTrue(str(top) in data)
        self.assertTrue(str(left) in data)

    def test_click(self):
        mouse.click(coords=(self.__get_pos(50)))
        data = self.__get_text()
        self.assertTrue("LeftButton" in data)
        self.assertTrue("Mouse Press" in data)
        self.assertTrue("Mouse Release" in data)

    def test_double_click(self):
        mouse.double_click(coords=(self.__get_pos(50)))
        data = self.__get_text()
        self.assertTrue("Mouse DoubleClick" in data)

    def test_press_release(self):
        left, top = self.__get_pos(50)
        left1, top1 = self.__get_pos(20)
        mouse.press(coords=(left, top))
        mouse.release(coords=(left1, top1))
        data = self.__get_text()
        self.assertEqual(str(top) in data, str(top1) in data)
        self.assertEqual(str(left) in data, str(left1) in data)

    def test_right_click(self):
        mouse.right_click((self.__get_pos(50)))
        data = self.__get_text()
        self.assertTrue("Mouse Press" in data)
        self.assertTrue("Mouse Release" in data)
        self.assertTrue("RightButton" in data)

    def test_vertical_scroll(self):
        mouse.scroll((self.__get_pos(50)), 5)
        mouse.scroll((self.__get_pos(50)), -5)
        data = self.__get_text()
        self.assertTrue("UP" in data)
        self.assertTrue("DOWN" in data)

    def test_wheel_click(self):
        mouse.wheel_click((self.__get_pos(50)))
        data = self.__get_text()
        self.assertTrue("Mouse Press" in data)
        self.assertTrue("Mouse Release" in data)
        self.assertTrue("MiddleButton" in data)

if __name__ == "__main__":
    unittest.main()
