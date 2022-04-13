"""Tests for WPFWrapper"""
from __future__ import print_function
from __future__ import unicode_literals

import time
import os
import sys
import collections
import unittest
import mock
import six

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.base_application import WindowSpecification  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.timings import Timings, wait_until  # noqa: E402
from pywinauto.actionlogger import ActionLogger  # noqa: E402
from pywinauto import Desktop
from pywinauto import mouse  # noqa: E402
from pywinauto import WindowNotFoundError  # noqa: E402

import pywinauto.controls.wpf_controls as wpf_ctls
from pywinauto.controls.wpfwrapper import WPFWrapper
from pywinauto.windows.wpf_element_info import WPFElementInfo

wpf_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    wpf_samples_folder = os.path.join(wpf_samples_folder, 'x64')
wpf_app_1 = os.path.join(wpf_samples_folder, u"WpfApplication1.exe")

def _set_timings():
    """Setup timings for WPF related tests"""
    Timings.defaults()
    Timings.window_find_timeout = 20


class WPFWrapperTests(unittest.TestCase):

    """Unit tests for the WPFWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()
        mouse.move((-500, 500))  # remove the mouse from the screen to avoid side effects

        # start the application
        self.app = Application(backend='uia')
        self.app = self.app.start(wpf_app_1)

        self.dlg = self.app.WPFSampleApplication

    def test_get_active_uia(self):
        focused_element = self.dlg.get_active()
        self.assertTrue(type(focused_element) is UIAWrapper or issubclass(type(focused_element), UIAWrapper))

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_issue_278(self):
        """Test that statement menu = app.MainWindow.Menu works for 'uia' backend"""
        menu_spec = self.dlg.Menu
        self.assertTrue(isinstance(menu_spec, WindowSpecification))
        # Also check the app binding
        self.assertTrue(menu_spec.app, self.app)

    def test_find_nontop_ctl_by_class_name_and_title(self):
        """Test getting a non-top control by a class name and a title"""
        # Look up for a non-top button control with 'Apply' caption
        self.dlg.wait('ready')
        caption = 'Apply'
        wins = self.app.windows(top_level_only=False,
                                class_name='Button',
                                name=caption)

        # Verify the number of found wrappers
        self.assertEqual(len(wins), 1)

        # Verify the caption of the found wrapper
        self.assertEqual(wins[0].texts()[0], caption)

    def test_find_top_win_by_class_name_and_title(self):
        """Test getting a top window by a class name and a title"""
        # Since the top_level_only is True by default
        # we don't specify it as a criteria argument
        self.dlg.wait('ready')
        caption = 'WPF Sample Application'
        wins = self.app.windows(class_name='Window', name=caption)

        # Verify the number of found wrappers
        self.assertEqual(len(wins), 1)

        # Verify the caption of the found wrapper
        self.assertEqual(wins[0].texts()[0], caption)

    def test_class(self):
        """Test getting the classname of the dialog"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.class_name(), "Button")

    def test_window_text(self):
        """Test getting the window Text of the dialog"""
        label = self.dlg.TestLabel.find()
        self.assertEqual(label.window_text(), u"TestLabel")
        self.assertEqual(label.can_be_label, True)

    def test_control_id(self):
        """Test getting control ID"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.control_id(), None)

    def test_automation_id(self):
        """Test getting automation ID"""
        alpha_toolbar = self.dlg.by(name="Alpha", control_type="ToolBar")
        button = alpha_toolbar.by(control_type="Button",
                                  auto_id="OverflowButton").find()
        self.assertEqual(button.automation_id(), "OverflowButton")

    def test_value(self):
        """Test find element by value"""
        edit = self.dlg.by(auto_id="edit1").find()
        edit.set_edit_text("Test string")

        edit_by_value = self.dlg.by(value="Test string").find()
        self.assertEqual("edit1", edit_by_value.element_info.auto_id)

    def test_is_visible(self):
        """Test is_visible method of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.is_visible(), True)

    def test_is_enabled(self):
        """Test is_enabled method of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.is_enabled(), True)

    def test_process_id(self):
        """Test process_id method of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.process_id(), self.dlg.process_id())
        self.assertNotEqual(button.process_id(), 0)

    def test_is_dialog(self):
        """Test is_dialog method of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.is_dialog(), False)
        self.assertEqual(self.dlg.is_dialog(), True)

    def test_move_window(self):
        """Test  move_window without any parameters"""

        # move_window with default parameters
        prevRect = self.dlg.rectangle()
        self.dlg.move_window()
        self.assertEqual(prevRect, self.dlg.rectangle())

        # move_window call for a not supported control
        button = self.dlg.by(class_name="Button", name="OK")
        self.assertRaises(AttributeError, button.move_window)

        # Make RECT stub to avoid import win32structures
        Rect = collections.namedtuple('Rect', 'left top right bottom')
        prev_rect = self.dlg.rectangle()
        new_rect = Rect._make([i + 5 for i in prev_rect])

        self.dlg.move_window(
            new_rect.left,
            new_rect.top,
            new_rect.right - new_rect.left,
            new_rect.bottom - new_rect.top
        )
        time.sleep(0.1)
        logger = ActionLogger()
        logger.log("prev_rect = %s", prev_rect)
        logger.log("new_rect = %s", new_rect)
        logger.log("self.dlg.rectangle() = %s", self.dlg.rectangle())
        self.assertEqual(self.dlg.rectangle(), new_rect)

        self.dlg.move_window(prev_rect)
        self.assertEqual(self.dlg.rectangle(), prev_rect)

    def test_close(self):
        """Test close method of a control"""
        wrp = self.dlg.find()

        # mock a failure in get_elem_interface() method only for 'Window' param
        orig_get_elem_interface = uia_defs.get_elem_interface
        with mock.patch.object(uia_defs, 'get_elem_interface') as mock_get_iface:
            def side_effect(elm_info, ptrn_name):
                if ptrn_name == "Window":
                    raise uia_defs.NoPatternInterfaceError()
                else:
                    return orig_get_elem_interface(elm_info, ptrn_name)
            mock_get_iface.side_effect=side_effect
            # also mock a failure in type_keys() method
            with mock.patch.object(UIAWrapper, 'type_keys') as mock_type_keys:
                exception_err = comtypes.COMError(-2147220991, 'An event was unable to invoke any of the subscribers', ())
                mock_type_keys.side_effect = exception_err
                self.assertRaises(WindowNotFoundError, self.dlg.close)

        self.dlg.close()
        self.assertEqual(self.dlg.exists(), False)

    def test_parent(self):
        """Test getting a parent of a control"""
        button = self.dlg.Alpha.find()
        self.assertEqual(button.parent(), self.dlg.find())

    def test_top_level_parent(self):
        """Test getting a top-level parent of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.top_level_parent(), self.dlg.find())

    def test_texts(self):
        """Test getting texts of a control"""
        self.assertEqual(self.dlg.texts(), ['WPF Sample Application'])

    def test_children(self):
        """Test getting children of a control"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(len(button.children()), 1)
        self.assertEqual(button.children()[0].class_name(), "TextBlock")

    def test_children_generator(self):
        """Test iterating children of a control"""
        button = self.dlg.by(class_name="Button", name="OK").find()
        children = [child for child in button.iter_children()]
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].class_name(), "TextBlock")

    def test_descendants(self):
        """Test iterating descendants of a control"""
        toolbar = self.dlg.by(name="Alpha", control_type="ToolBar").find()
        descendants = toolbar.descendants()
        self.assertEqual(len(descendants), 7)

    def test_descendants_generator(self):
        toolbar = self.dlg.by(name="Alpha", control_type="ToolBar").find()
        descendants = [desc for desc in toolbar.iter_descendants()]
        self.assertSequenceEqual(toolbar.descendants(), descendants)

    def test_is_child(self):
        """Test is_child method of a control"""
        button = self.dlg.Alpha.find()
        self.assertEqual(button.is_child(self.dlg.find()), True)

    def test_equals(self):
        """Test controls comparisons"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertNotEqual(button, self.dlg.find())
        self.assertEqual(button, button.element_info)
        self.assertEqual(button, button)

    @unittest.skip("To be solved with issue #790")
    def test_scroll(self):
        """Test scroll"""
        # Check an exception on a non-scrollable control
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        six.assertRaisesRegex(self, AttributeError, "not scrollable",
                              button.scroll, "left", "page")

        # Check an exception on a control without horizontal scroll bar
        tab = self.dlg.Tree_and_List_Views.set_focus()
        listview = tab.children(class_name=u"ListView")[0]
        six.assertRaisesRegex(self, AttributeError, "not horizontally scrollable",
                              listview.scroll, "right", "line")

        # Check exceptions on wrong arguments
        self.assertRaises(ValueError, listview.scroll, "bbbb", "line")
        self.assertRaises(ValueError, listview.scroll, "up", "aaaa")

        # Store a cell position
        cell = listview.cell(3, 0)
        orig_rect = cell.rectangle()
        self.assertEqual(orig_rect.left > 0, True)

        # Trigger a horizontal scroll bar on the control
        hdr = listview.get_header_control()
        hdr_itm = hdr.children()[1]
        trf = hdr_itm.iface_transform
        trf.resize(1000, 20)
        listview.scroll("right", "page", 2)
        self.assertEqual(cell.rectangle().left < 0, True)

        # Check an exception on a control without vertical scroll bar
        tab = self.dlg.ListBox_and_Grid.set_focus()
        datagrid = tab.children(class_name=u"DataGrid")[0]
        six.assertRaisesRegex(self, AttributeError, "not vertically scrollable",
                              datagrid.scroll, "down", "page")

    def test_is_keyboard_focusable(self):
        """Test is_keyboard focusable method of several controls"""
        edit = self.dlg.TestLabelEdit.find()
        label = self.dlg.TestLabel.find()
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.is_keyboard_focusable(), True)
        self.assertEqual(edit.is_keyboard_focusable(), True)
        self.assertEqual(label.is_keyboard_focusable(), False)

    def test_set_focus(self):
        """Test setting a keyboard focus on a control"""
        edit = self.dlg.TestLabelEdit.find()
        edit.set_focus()
        self.assertEqual(edit.has_keyboard_focus(), True)

    def test_get_active_desktop_uia(self):
        focused_element = Desktop(backend="uia").get_active()
        self.assertTrue(type(focused_element) is UIAWrapper or issubclass(type(focused_element), UIAWrapper))

    def test_type_keys(self):
        """Test sending key types to a control"""
        edit = self.dlg.TestLabelEdit.find()
        edit.type_keys("t")
        self.assertEqual(edit.window_text(), "t")
        edit.type_keys("e")
        self.assertEqual(edit.window_text(), "te")
        edit.type_keys("s")
        self.assertEqual(edit.window_text(), "tes")
        edit.type_keys("t")
        self.assertEqual(edit.window_text(), "test")
        edit.type_keys("T")
        self.assertEqual(edit.window_text(), "testT")
        edit.type_keys("y")
        self.assertEqual(edit.window_text(), "testTy")

    def test_minimize_maximize(self):
        """Test window minimize/maximize operations"""
        wrp = self.dlg.minimize()
        self.dlg.wait_not('active')
        self.assertEqual(wrp.is_minimized(), True)
        wrp.maximize()
        self.dlg.wait('active')
        self.assertEqual(wrp.is_maximized(), True)
        wrp.minimize()
        self.dlg.wait_not('active')
        wrp.restore()
        self.dlg.wait('active')
        self.assertEqual(wrp.is_normal(), True)

    def test_capture_as_image_multi_monitor(self):
        with mock.patch('win32api.EnumDisplayMonitors') as mon_device:
            mon_device.return_value = (1, 2)
            rect = self.dlg.rectangle()
            expected = (rect.width(), rect.height())
            result = self.dlg.capture_as_image().size
            self.assertEqual(expected, result)

    def test_set_value(self):
        """Test for UIAWrapper.set_value"""
        edit = self.dlg.by(control_type='Edit', auto_id='edit1').find()
        self.assertEqual(edit.get_value(), '')
        edit.set_value('test')
        self.assertEqual(edit.get_value(), 'test')


class WPFWrapperMouseTests(unittest.TestCase):

    """Unit tests for mouse actions of the WPFWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        dlg = self.app.WPFSampleApplication
        self.button = dlg.by(class_name="System.Windows.Controls.Button",
                             name="OK").find()

        self.label = dlg.by(class_name="System.Windows.Controls.Label", name="TestLabel").find()
        self.app.wait_cpu_usage_lower(threshold=1.5, timeout=30, usage_interval=1.0)

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_click_input(self):
        """Test click_input method of a control"""
        self.button.click_input()
        self.assertEqual(self.label.window_text(), "LeftClick")

    def test_double_click_input(self):
        """Test double_click_input method of a control"""
        self.button.double_click_input()
        self.assertEqual(self.label.window_text(), "DoubleClick")

    def test_right_click_input(self):
        """Test right_click_input method of a control"""
        self.button.right_click_input()
        self.assertEqual(self.label.window_text(), "RightClick")


if __name__ == "__main__":
    unittest.main()
