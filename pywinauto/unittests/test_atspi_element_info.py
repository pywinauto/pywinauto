import os
import sys
import subprocess
import time
import unittest

from pywinauto.atspi_element_info import AtspiElementInfo

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

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.app = subprocess.Popen(['python', _test_app()], stdout=subprocess.PIPE, shell=False)
            time.sleep(1)
            self.app_info = [children for children in self.desktop_info.children() if children.name == app_name][0]

        def tearDown(self):
            self.app.kill()

        def test_can_get_desktop(self):
            self.assertEqual(self.desktop_info.class_name, "desktop frame")

        def test_can_get_name(self):
            self.assertEqual(self.desktop_info.name, "main")

        def test_can_get_parent(self):
            parent = self.app_info.parent
            self.assertEqual(parent.class_name, "desktop frame")

        def test_can_get_process_id(self):
            self.assertEqual(self.app_info.process_id, self.app.pid)

        def test_can_get_class_name(self):
            self.assertEqual(self.app_info.class_name, "application")

        def test_can_get_rectangle(self):
            rectangle = self.app_info.children()[0].children()[0].rectangle
            width = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            height = int(self.app.stdout.readline().decode(encoding='UTF-8'))
            self.assertEqual(rectangle.width, width)
            self.assertEqual(rectangle.height, height)
