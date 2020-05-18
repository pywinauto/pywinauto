import sys
import os
import time
import unittest
from CoreFoundation import CFNumberCreate
if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    sys.path.append(parent_dir + '/macos')
    os.path.join
    # from pywinauto.macos import macos_functions
    from pywinauto.macos.ax_element_info import AXError, _cf_attr_to_py_object, AxElementInfo
    from pywinauto.macos.ax_element_info_object import known_control_types
    from pywinauto.macos.macos_functions import get_screen_frame
    from pywinauto.macos.application import Application

class AxElementInfoDesktopSpecificTestCases(unittest.TestCase):
    def setUp(self):
        self.desktop = AxElementInfo()

    def test_can_get_childrens_desktop(self):
        apps = self.desktop.children()
        for app in apps:
            self.assertTrue(app.control_type in ["Application", "InvalidControlType"])

    def test_repr_desktop(self):
        self.assertEqual(repr(AxElementInfo()),"<pywinauto.macos.ax_element_info.AxElementInfo Desktop 'Desktop'>")

    def test_can_get_name_desktop(self):
        self.assertEqual(self.desktop.name, "Desktop")

    def test_can_get_parent_desktop(self):
        self.assertEqual(self.desktop.parent, None)

    def test_can_get_process_id_desktop(self):
        self.assertEqual(self.desktop.process_id, None)

    def test_can_get_class_name_desktop(self):
        self.assertEqual(self.desktop.control_type, "Desktop")

    def test_can_get_rectangle_desktop(self):
        e = get_screen_frame()
        self.assertEqual(self.desktop.rectangle, (0, 0, int(float(e.size.width)), int(float(e.size.height))))

    def test_is_instance(self):
        element = AxElementInfo(self.desktop.children()[0])
        self.assertTrue(element.control_type in ["Application", "InvalidControlType"])


class AxelementinfoTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""
    def setUp(self):
        self.app = Application()
        self.app.start(bundle_id = 'pywinauto.testapps.send-keys-test-app')

    def tearDown(self):
        self.app.kill()

    def test_can_get_control_type_of_all_app_descendants_app(self):
        elem = AxElementInfo(self.app.ns_app)
        for children in elem.descendants():
            self.assertTrue(children.control_type in known_control_types)

    def test_can_get_name_application(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).name, "send_keys_test_app")

    def test_can_get_class_name_application(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).control_type, "Application")

    def test_can_get_class_parent_application(self):
        elem = AxElementInfo(self.app.ns_app)
        kid = elem.children()
        self.assertEqual(kid[0].parent.control_type, "Application")

    def test_can_get_process_id(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).process_id, self.app.ns_app.processIdentifier())

    def test_return_full_screen_rectangle_app(self):
        elem = AxElementInfo(self.app.ns_app)
        e = get_screen_frame()
        time.sleep(3)
        self.assertEqual(elem.children()[0].rectangle, (0, 0, int(float(e.size.width)), int(float(e.size.height))))

    def test_return_size_and_position_app(self):
        elem = AxElementInfo(self.app.ns_app)
        e = get_screen_frame()
        time.sleep(3)
        self.assertEqual(elem.children()[0].size, (float(e.size.width), float(e.size.height)))
        self.assertEqual(elem.children()[0].position, (0.0,0.0))

    def test_is_enabled_app(self):
        elem = AxElementInfo(self.app.ns_app)
        for child in elem.descendants():
            attribute = child._get_ax_attributes()
            if 'AXEnabled' in attribute:
                self.assertTrue(child.is_enabled)
                break 

    def test_is_enabled_not_anapp(self):
        elem = AxElementInfo(self.app.ns_app)
        for child in elem.descendants():
            attribute = child._get_ax_attributes()
            if 'AXEnabled' in attribute:
                self.assertTrue(child.is_enabled)
                break 

    def test_is_selected_app(self):
        elem = AxElementInfo(self.app.ns_app)
        for child in elem.descendants():
            attribute = child._get_ax_attributes()
            if 'AXSelected' not in attribute:
                self.assertFalse(child.is_selected)
            if 'AXSelected' in attribute:
                self.assertFalse(child.is_selected)
                break 


if __name__ == "__main__":
    unittest.main()
