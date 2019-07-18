import sys
import os
import unittest
import time

# sys.path.append(".")
if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    sys.path.append(parent_dir + '/macos')
    os.path.join
    # from pywinauto.macos import macos_functions
    from pywinauto.macos.ax_element_info import *
    from pywinauto.macos.ax_element_info_object import known_control_types
    from pywinauto.macos.macos_functions import get_screen_frame
    from pywinauto.macos.application import Application


class AxelementinfoTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):
        self.desktop = AxElementInfo()
        

    def tearDown(self):
        pass

    def test_can_get_control_type_of_all_app_descendants(self):
    	application = Application()
        application.start(bundle_id='com.yourcompany.send-keys-test-app')
        apps = self.desktop.children()
        # time.sleep(5)
        for app in apps:
        	print(app)
        	# print(app.process_id)
        application.kill()

    # def test_can_get_childrens(self):
        apps = self.desktop.children()
        for app in apps:
        	self.assertTrue(app.control_type in ["Application", ""])

    # def test_can_get_name(self):
    	self.assertEqual(self.desktop.name, "Desktop")

    # def test_can_get_parent(self):
    	self.assertEqual(self.desktop.parent, None)

    # def test_can_get_class_name(self):
        self.assertEqual(self.desktop.control_type, "Desktop")

    # def test_can_get_rectangle(self):
    	e = get_screen_frame()
    	self.assertEqual(self.desktop.rectangle,(0, 0, int(float(e.size.width)), int(float(e.size.height))))


    

if __name__ == "__main__":
    unittest.main()