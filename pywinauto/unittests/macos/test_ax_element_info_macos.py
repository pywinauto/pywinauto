import sys
import time
import unittest

if sys.platform == 'darwin':
    sys.path.append(".")
    from pywinauto.macos.ax_element_info import AXError, AxElementInfo
    from pywinauto.macos.ax_element_info_object import known_control_types, known_top_lvl_control_types
    from pywinauto.macos.macos_functions import get_screen_frame
    from pywinauto.macos.application import Application
    from pywinauto.macos.macos_structures import AX_RECT, AX_SIZE, AX_POINT

class AxElementInfoDesktopSpecificTestCases(unittest.TestCase):
    def setUp(self):
        self.desktop = AxElementInfo()

    def test_can_get_app_top_windows(self):
        top_lvl_windows = self.desktop.children()
        all_control_types_are_known = True
        for top_lvl_window in top_lvl_windows:
            if not top_lvl_window.control_type in known_top_lvl_control_types:
                all_control_types_are_known = False
                break
        self.assertTrue(all_control_types_are_known)

    def test_repr_desktop(self):
        self.assertEqual(repr(AxElementInfo()),"<Class:pywinauto.macos.ax_element_info.AxElementInfo Role:Desktop Subrole: Title'Desktop'>")

    def test_can_get_name_desktop(self):
        self.assertEqual(self.desktop.name, "Desktop")

    def test_can_get_parent_desktop(self):
        self.assertEqual(self.desktop.parent, None)

    def test_can_get_process_id_desktop(self):
        self.assertEqual(self.desktop.process_id, None)

    def test_can_get_class_name_desktop(self):
        self.assertEqual(self.desktop.control_type, "Desktop")

    def test_can_get_rectangle_desktop(self):
        expected_rect = AX_RECT(nsrect=get_screen_frame())
        self.assertEqual(self.desktop.rectangle, expected_rect)

    def test_is_instance(self):
        element = AxElementInfo(self.desktop.children()[0])
        self.assertTrue(element.control_type in known_top_lvl_control_types)

class AxelementinfoTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""
    def setUp(self):
        self.app = Application()
        self.app.start(bundle_id = 'pywinauto.testapps.send-keys-test-app',new_instance = False)

    def tearDown(self):
        self.app.kill()

    def test_can_get_control_type_of_all_app_descendants_app(self):
        elem = AxElementInfo(self.app.ns_app)
        all_control_types_are_known = True
        for children in elem.descendants():
            if not children.control_type in known_control_types:
                all_control_types_are_known = False
                break
        self.assertTrue(all_control_types_are_known)

    def test_child_of_app(self):
        app_info = AxElementInfo(self.app.ns_app)
        windows = app_info.children(control_type='Window')
        menu_bars = app_info.children(control_type='MenuBar')
        self.assertTrue(len(windows) >= 1)
        self.assertTrue(len(menu_bars) == 1)

    def test_can_get_sub_role(self):
        app_info = AxElementInfo(self.app.ns_app)
        children = app_info.children()
        window = list(filter(lambda x: x.control_type == 'Window', children))[0]
        self.assertTrue(window.subrole == 'AXStandardWindow')

    def test_can_get_name_application(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).name, "send_keys_test_app")

    def test_can_get_class_name_application(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).control_type, "Application")

    def test_hidding_the_ns_app_layer(self):
        elem = AxElementInfo(self.app.ns_app)
        kid = elem.children()
        self.assertEqual(kid[0].parent.control_type, "Desktop")
        desktop = AxElementInfo()
        self.assertTrue(desktop.children()[0].control_type in known_top_lvl_control_types)

    def test_can_get_process_id(self):
        self.assertEqual(AxElementInfo(self.app.ns_app).process_id, self.app.ns_app.processIdentifier())

    def test_return_full_screen_rectangle_app(self):
        elem = AxElementInfo(self.app.ns_app)
        time.sleep(3)
        expected_rect = AX_RECT(nsrect=get_screen_frame())
        if (elem.children()[0].rectangle.bottom != expected_rect.bottom):
            self.assertEqual(elem.children()[0].rectangle.bottom + 51, expected_rect.bottom)
            self.assertEqual(elem.children()[0].rectangle.top, expected_rect.top)
            self.assertEqual(elem.children()[0].rectangle.left, expected_rect.left)
            self.assertEqual(elem.children()[0].rectangle.right, expected_rect.right)
        else:
            self.assertEqual(elem.children()[0].rectangle, expected_rect)

    def test_return_size_and_position_app(self):
        elem = AxElementInfo(self.app.ns_app)
        time.sleep(3)
        expected_size = AX_SIZE(nssize=get_screen_frame().size)
        extected_point = AX_POINT(x=0,y=0)
        if (elem.children()[0].size.height != expected_size.height):
            self.assertEqual(elem.children()[0].size.height + 74, expected_size.height)
            self.assertEqual(elem.children()[0].size.weight, expected_size.weight)
        else:
            self.assertEqual(elem.children()[0].size, expected_size)
        self.assertEqual(elem.children()[0].position, extected_point)

    def test_is_enabled_app(self):
        elem = AxElementInfo(self.app.ns_app)
        for child in elem.descendants():
            attribute = child._get_ax_attributes()
            if 'AXEnabled' in attribute:
                self.assertTrue(child.enabled)
                break 

    def test_is_enabled_not_anapp(self):
        elem = AxElementInfo(self.app.ns_app)
        for child in elem.descendants():
            attribute = child._get_ax_attributes()
            if 'AXEnabled' in attribute:
                self.assertTrue(child.enabled)
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
