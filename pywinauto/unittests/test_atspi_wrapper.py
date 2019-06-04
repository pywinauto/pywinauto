import os
import sys
import time
import unittest

if sys.platform.startswith("linux"):
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.atspi_element_info import known_control_types
    from pywinauto.linux.application import Application
    from pywinauto.controls.atspiwrapper import AtspiWrapper
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


if sys.platform.startswith("linux"):
    class AtspiWrapperTests(unittest.TestCase):

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

            self.app_wrapper = AtspiWrapper(self.app_info)

        def tearDown(self):
            self.app.kill()

        def test_set_window_focus(self):
            self.app_wrapper.children()[0].set_focus()
            states = self.app_wrapper.children()[0].get_states()
            print(states)
            self.assertTrue("STATE_VISIBLE" in states)
            self.assertTrue("STATE_SHOWING" in states)

        def test_top_level_parent_for_app_return_app(self):
            self.assertEqual(self.app_wrapper.top_level_parent().element_info.control_type, "Application")

        def test_top_level_parent_for_button_return_app(self):
            # TODO replace .children call to wrapper object when wrapper fully implemented
            self.assertEqual(self.app_wrapper.children()[0].children()[0].top_level_parent().element_info.control_type,
                             "Application")

        def test_root_return_desktop(self):
            self.assertEqual(self.app_wrapper.root(), self.desktop_info)

        def test_class_name_return_element_info_class_name(self):
            self.assertEqual(self.app_wrapper.class_name(), "application")

        def test_window_text(self):
            self.assertEqual(self.app_wrapper.window_text(), app_name)

        def test_control_id(self):
            self.assertEqual(self.app_wrapper.control_id(), known_control_types.index("Application"))

        def test_can_get_rectangle(self):
            # TODO replace .children call to wrapper object when wrapper fully implemented
            rect = self.app_wrapper.children()[0].children()[0].rectangle()
            self.assertEqual(rect.width(), 600)
            self.assertEqual(rect.height(), 200)

        def test_can_get_process_id(self):
            self.assertEqual(self.app_wrapper.process_id(), self.app.process)

        def test_is_dialog_for_application_is_true(self):
            self.assertTrue(self.app_wrapper.is_dialog())

        def test_is_dialog_for_button_is_false(self):
            # TODO replace .children call to wrapper object when wrapper fully implemented
            frame_wrapper = self.app_wrapper.children()[0]
            button_wrapper = frame_wrapper.children()[0].children()[0]
            self.assertFalse(button_wrapper.is_dialog())

        def test_can_get_children(self):
            self.assertEqual(self.app_wrapper.children()[0].control_id(), known_control_types.index("Frame"))

        def test_can_get_descendants(self):
            self.assertTrue(len(self.app_wrapper.descendants()) > len(self.app_wrapper.children()))

        def test_can_get_control_count(self):
            self.assertEqual(self.app_wrapper.control_count(), 1)

        def test_can_get_properties(self):
            props = self.app_wrapper.get_properties()
            self.assertEqual(props['class_name'], 'application')
            self.assertEqual(props['friendly_class_name'], 'application')
            self.assertEqual(props['control_id'], known_control_types.index("Application"))

        def test_app_is_child_of_desktop(self):
            self.assertTrue(self.app_wrapper.is_child(self.desktop_wrapper))

if __name__ == "__main__":
    unittest.main()
