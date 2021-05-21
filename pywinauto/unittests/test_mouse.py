"""Tests for mouse.py"""

import time
import copy
import sys
import os
import unittest
if sys.platform == 'win32':
    import win32clipboard
    sys.path.append(".")
    from pywinauto.application import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import mouse
    from pywinauto.timings import Timings
else:
    import subprocess
    from Xlib.display import Display
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    import mouse
    send_keys_dir = os.path.join(parent_dir, r"linux")
    sys.path.insert(0, send_keys_dir)
    from keyboard import send_keys
    import clipboard


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
        """Set some data and ensure the application is in the state we want"""
        if sys.platform == 'win32':
            Timings.defaults()
            self.app = Application()
            self.app.start(_test_app())
            self.dlg = self.app.mousebuttons
        else:
            self.display = Display()
            self.app = subprocess.Popen("exec " + _test_app(), shell=True)
            time.sleep(1)

    def tearDown(self):
        self.app.kill()

    def __get_pos(self, shift):
        if sys.platform == 'win32':
            rect = self.dlg.rectangle()
            center = rect.mid_point()
            return center.x + shift, center.y + shift
        else:
            root = self.display.screen().root
            left_pos = root.get_geometry().width / 2
            top_pos = root.get_geometry().height / 2
            return left_pos - shift, top_pos - shift

    def __get_text(self):
        data = ''
        time.sleep(1)
        send_keys('^a^c', pause=0.2)
        if sys.platform == 'win32':
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
        else:
            data = clipboard.get_data()
        return data

    def test_left_click(self):
        left, top = self.__get_pos(50)
        mouse.click(coords=(left, top))
        print(left, top)
        data = self.__get_text()
        print(data)
        self.assertTrue(str(int(top)) in data)
        self.assertTrue(str(int(left)) in data)
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

    def test_vertical_scroll_up(self):
        mouse.click(coords=(self.__get_pos(50)))
        mouse.scroll(self.__get_pos(50), 1)
        data = self.__get_text()
        self.assertTrue("UP" in data)

    def test_vertical_scroll_down(self):
        mouse.click(coords=(self.__get_pos(50)))
        mouse.scroll(self.__get_pos(50), -1)
        data = self.__get_text()
        self.assertTrue("DOWN" in data)

    def test_wheel_click(self):
        mouse.wheel_click((self.__get_pos(50)))
        data = self.__get_text()
        self.assertTrue("Mouse Press" in data)
        self.assertTrue("Mouse Release" in data)
        self.assertTrue("MiddleButton" in data)

    # TODO: make the feature and the tests cross-platform (duration param)
    if sys.platform == "win32":
        def test_mouse_can_move_cursor(self):
            coord = (0, 1)
            mouse.move(coord)
            self.assertEqual(coord, mouse._get_cursor_pos())

            mouse.move((-200, -300))
            self.assertEqual((0, 0), mouse._get_cursor_pos())

        def test_mouse_fail_on_int_duration_and_float_coord(self):
            self.assertRaises(TypeError, mouse.move, coord=(0, 0), duration=1)
            self.assertRaises(TypeError, mouse.move, coord=(0.0, 0))

        def test_mouse_tween(self):
            coord = (401, 301)
            mouse.move(coord, duration=0.5)
            self.assertEqual(coord, mouse._get_cursor_pos())

            mouse.move(coord, duration=0.5)
            self.assertEqual(coord, mouse._get_cursor_pos())

        def test_move_mouse_input_tween(self):
            coord = (1, 2)
            self.dlg.move_mouse_input(coords=coord, absolute=True)
            self.assertEqual(coord, mouse._get_cursor_pos())
            coord = (501, 401)
            self.dlg.move_mouse_input(coords=coord, absolute=True, duration=0.5)
            self.assertEqual(coord, mouse._get_cursor_pos())
            self.dlg.move_mouse_input(coords=coord, absolute=True, duration=0.5)
            self.assertEqual(coord, mouse._get_cursor_pos())

        def test_drag_mouse_input_tween(self):
            rect = self.dlg.rectangle()
            x0, y0 = rect.left, rect.top
            x1, y1 = 10, 50
            x0_curs, y0_curs = (rect.left + rect.right) // 2, rect.top + 10
            x1_curs, y1_curs = (rect.right - rect.left) // 2 + x1, 10 + y1

            mouse.move((x0_curs, y0_curs))
            self.assertEqual((x0_curs, y0_curs), mouse._get_cursor_pos())

            self.dlg.drag_mouse_input(src=(x0_curs, y0_curs), dst=(x1_curs, y1_curs), absolute=True)
            rect = self.dlg.rectangle()
            self.assertEqual((rect.left, rect.top), (x1, y1))

            self.dlg.drag_mouse_input(src=(x1_curs, y1_curs), dst=(x0_curs, y0_curs), absolute=True, duration=1.0)
            rect = self.dlg.rectangle()
            self.assertEqual((rect.left, rect.top), (x0, y0))

    if sys.platform != 'win32':
        def test_swapped_buttons(self):
            current_map = self.display.get_pointer_mapping()
            swapped_map = copy.copy(current_map)
            swapped_map[0], swapped_map[2] = swapped_map[2], swapped_map[0]
            self.display.set_pointer_mapping(swapped_map)
            try:
                mouse.right_click((self.__get_pos(50)))
                data = self.__get_text()
                self.assertTrue("RightButton" in data)
            finally:
                self.display.set_pointer_mapping(current_map)

if __name__ == "__main__":
    unittest.main()
