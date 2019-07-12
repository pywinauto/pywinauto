import sys
import os
import unittest

# sys.path.append(".")
if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    sys.path.append(parent_dir + '/macos')
    os.path.join
    # from pywinauto.macos import macos_functions
    from pywinauto.macos.ax_element_info import *
    from pywinauto.macos.ax_element_info_object import known_control_types


class AxelementinfoTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):

        self.app = AxElementInfo()
        self.app.launchAppByBundleId('com.yourcompany.send-keys-test-app')

    def tearDown(self):

        self.app.kill_process()

    def test_can_get_childrens(self):
        apps = [children.name for children in self.app.desktop()]
        while "send_keys_test_app" not in apps:
        	apps = [children.name for children in self.app.desktop()]
        self.assertTrue('send_keys_test_app' in apps)

    def test_can_get_name(self):
    	self.assertEqual(self.app.app_ref().name, "send_keys_test_app")

    def test_can_get_parent(self):
    	self.assertEqual(self.app.app_ref().children()[0].parent.control_type, "Application")

    def test_can_get_class_name(self):
        self.assertEqual(self.app.app_ref().control_type, "Application")

    def test_can_get_control_type_of_all_app_descendants(self):
        for children in self.app.descendants():
            self.assertTrue(children.control_type in known_control_types)


if __name__ == "__main__":
    unittest.main()