import os
import sys
import subprocess
import time
import unittest

if sys.platform != 'win32':
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo

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
            return [children for children in self.desktop_info.children() if children.name == app_name][0]

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.app = subprocess.Popen(['python3', _test_app()], stdout=subprocess.PIPE, shell=False)
            time.sleep(1)

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
            app_info = self.get_app(app_name)
            parent = app_info.parent
            self.assertEqual(parent.class_name, "desktop frame")

        def test_can_get_process_id(self):
            app_info = self.get_app(app_name)
            self.assertEqual(app_info.process_id, self.app.pid)

        def test_can_get_class_name(self):
            app_info = self.get_app(app_name)
            self.assertEqual(app_info.class_name, "application")

        @unittest.skip("skip for now")
        def test_can_get_rectangle(self):
            app_info = self.get_app(app_name)
            rectangle = app_info.children()[0].children()[0].rectangle
            width = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            height = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            self.assertEqual(rectangle.width, width)
            self.assertEqual(rectangle.height, height)


if __name__ == "__main__":
    unittest.main()
