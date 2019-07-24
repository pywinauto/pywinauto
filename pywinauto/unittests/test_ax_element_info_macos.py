import sys
import os
import unittest
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

def runLoopAndExit():
    AppHelper.stopEventLoop()


class AxelementinfoTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):
        self.desktop = AxElementInfo()

    def tearDown(self):
        pass

    def test_can_get_control_type_of_all_app_descendants_app(self):
    	application = Application()
        application.start(bundle_id = 'com.yourcompany.send-keys-test-app')
        elem = AxElementInfo(application.ns_app)
        for children in elem.ref.descendants():
            self.assertTrue(children.control_type in known_control_types)
        application.kill()

    def test_can_get_childrens_desktop(self):
        apps = self.desktop.children()
        for app in apps:
        	self.assertTrue(app.control_type in ["Application", "InvalidControlType"])

    def test_can_get_name_desktop(self):
    	self.assertEqual(self.desktop.name, "Desktop")

    def test_can_get_parent_desktop(self):
    	self.assertEqual(self.desktop.parent, None)

    def test_can_get_class_name_desktop(self):
        self.assertEqual(self.desktop.control_type, "Desktop")

    def test_can_get_rectangle_desktop(self):
    	e = get_screen_frame()
    	self.assertEqual(self.desktop.rectangle, (0, 0, int(float(e.size.width)), int(float(e.size.height))))

    def test_can_get_name_application(self):
        application = Application()
        application.start(bundle_id='com.yourcompany.send-keys-test-app')
        self.assertEqual(AxElementInfo(application.ns_app).ref.name, "send_keys_test_app")
        application.kill()

    def test_can_get_class_name_application(self):
        application = Application()
        application.start(bundle_id='com.yourcompany.send-keys-test-app')
        self.assertEqual(AxElementInfo(application.ns_app).ref.control_type, "Application")
        application.kill()

    def test_can_get_process_id(self):
        application = Application()
        application.start(bundle_id='com.yourcompany.send-keys-test-app')
        self.assertEqual(AxElementInfo(application.ns_app).ref.process_id, application.ns_app.processIdentifier())
        application.kill()


if __name__ == "__main__":
    unittest.main()
