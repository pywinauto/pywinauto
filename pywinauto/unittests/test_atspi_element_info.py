import os
import sys
import subprocess
import time
import unittest

if sys.platform != 'win32':
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.atspi_element_info import known_control_types
    from pywinauto.linux.application import Application

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


if sys.platform != 'win32':
    class AtspiElementInfoTests(unittest.TestCase):

        """Unit tests for the AtspiElementInfo class"""

        def get_app(self, name):
            for children in self.desktop_info.children():
                if children.name == name:
                    return children
            else:
                raise Exception("Application not found")

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.app = Application()
            self.app.start("python3 " + _test_app())
            time.sleep(1)
            self.app_info = self.get_app(app_name)

        def tearDown(self):
            self.app.kill()

        def test_can_get_desktop(self):
            self.assertEqual(self.desktop_info.class_name, "desktop frame")

        def test_can_get_childrens(self):
            apps = [children.name for children in self.desktop_info.children()]
            self.assertTrue(app_name in apps)

        def test_can_get_name(self):
            self.assertEqual(self.desktop_info.name, "main")

        def test_can_get_parent(self):
            parent = self.app_info.parent
            self.assertEqual(parent.class_name, "desktop frame")

        def test_can_get_process_id(self):
            self.assertEqual(self.app_info.process_id, self.app.process)

        def test_can_get_class_name(self):
            self.assertEqual(self.app_info.class_name, "application")

        def test_can_get_control_type_property(self):
            self.assertEqual(self.app_info.control_type, "Application")

        def test_can_get_control_type_of_all_app_descendants(self):
            for children in self.app_info.descendants():
                self.assertTrue(children.control_type in known_control_types)

        def test_control_type_equal_class_name(self):
            for children in self.app_info.descendants():
                self.assertEqual(children.control_type.lower().replace("_", " "), children.class_name)

        @unittest.skip("skip for now")
        def test_can_get_rectangle(self):
            app_info = self.get_app(app_name)
            rectangle = app_info.children()[0].children()[0].rectangle
            width = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            height = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            self.assertEqual(rectangle.width(), width)
            self.assertEqual(rectangle.height(), height)


if __name__ == "__main__":
    unittest.main()
