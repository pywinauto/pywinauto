import os
import sys
import subprocess
import time
import unittest
import re

from ctypes import *

if sys.platform != 'win32':
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.atspi_element_info import known_control_types
    from pywinauto.linux.application import Application
    from pywinauto.controls.atspiwrapper import AtspiWrapper
    from pywinauto.controls.atspi_controls import ButtonWrapper
    from pywinauto.linux.atspi_objects import known_control_types

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


def print_tree(start_el_info, level_shifter=""):
    if level_shifter == "":
        print(start_el_info.control_type, "  ", start_el_info.control_id, "!")
        level_shifter += "-"

    for children in start_el_info.children():
        print(level_shifter, "  ", children.control_type, "    ", children.control_id, "!")
        print_tree(children, level_shifter+"-")


if sys.platform != 'win32':
    class AtspiControlTests(unittest.TestCase):

        """Unit tests for the AtspiWrapper class"""

        def get_app(self, name):
            for children in self.desktop_info.children():
                if children.name == name:
                    return children
            else:
                raise Exception("Application not found")

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.desktop_wrapper = AtspiWrapper(self.desktop_info)
            self.app = Application()
            self.app.start("python3 " + _test_app())
            time.sleep(1)
            self.app_info = self.get_app(app_name)

            self.button_info = self.app_info.children()[0].children()[0].children()[0]
            self.button_wrapper = ButtonWrapper(self.button_info)

            self.app_wrapper = AtspiWrapper(self.app_info)

        def tearDown(self):
            self.app.kill()

        def _get_state_label_text(self):
            return self.app_info.children()[0].children()[0].children()[5].rich_text

        def test_get_action(self):
            actions_count = self.button_wrapper.action.get_n_actions()
            print("Button actions count is: {}".format(actions_count))
            for i in range(actions_count):
                print("action {} is: {}. Description: {}".format(i, self.button_wrapper.action.get_action_name(i), self.button_wrapper.action.get_action_description(i)))

            self.assertEqual(self.button_wrapper.action.get_localized_name(0).decode('utf-8'), "Click")

        def test_do_action(self):
            status = self.button_wrapper.action.do_action(0)
            print("Action invoked, action status is: {}".format(status))
            self.assertTrue(status)

        def test_button_click(self):
            self.assertEqual(self.button_info.rich_text, "Click")
            self.button_wrapper.click()
            self.assertEqual(self.button_info.rich_text, "Click clicked")
            self.assertEqual(self._get_state_label_text(), "\"Click\" clicked")

        def test_button_toggle(self):
            toggle_button_info = self.app_info.children()[0].children()[0].children()[3]
            toggle_button_wrapper = ButtonWrapper(toggle_button_info)
            toggle_button_wrapper.click()
            self.assertEqual(self._get_state_label_text(), "Button 1 turned on")

        def test_button_toggle_state(self):
            toggle_button_info = self.app_info.children()[0].children()[0].children()[3]
            toggle_button_wrapper = ButtonWrapper(toggle_button_info)
            self.assertFalse(toggle_button_wrapper.get_toggle_state())
            toggle_button_wrapper.click()
            self.assertTrue(toggle_button_wrapper.get_toggle_state())


if __name__ == "__main__":
    unittest.main()
