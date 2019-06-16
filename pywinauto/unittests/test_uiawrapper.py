"""Tests for UIAWrapper"""
from __future__ import print_function
from __future__ import unicode_literals

import time
import os
import sys
import unittest
import mock
import six

sys.path.append(".")
from pywinauto.application import Application, WindowSpecification  # noqa: E402
from pywinauto.sysinfo import is_x64_Python, UIA_support  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from pywinauto.actionlogger import ActionLogger  # noqa: E402
from pywinauto import Desktop
from pywinauto import mouse  # noqa: E402
if UIA_support:
    import comtypes
    import pywinauto.uia_defines as uia_defs
    import pywinauto.controls.uia_controls as uia_ctls

wpf_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    wpf_samples_folder = os.path.join(wpf_samples_folder, 'x64')
wpf_app_1 = os.path.join(wpf_samples_folder, u"WpfApplication1.exe")

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
mfc_app_rebar_test = os.path.join(mfc_samples_folder, u"RebarTest.exe")

winforms_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WinForms_samples")
if is_x64_Python():
    winforms_folder = os.path.join(winforms_folder, 'x64')
winfoms_app_grid = os.path.join(winforms_folder, u"DataGridView_TestApp.exe")

if UIA_support:

    def _set_timings():
        """Setup timings for UIA related tests"""
        Timings.defaults()
        Timings.window_find_timeout = 20


    class UIAWrapperTests(unittest.TestCase):

        """Unit tests for the UIAWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()
            mouse.move((-500, 500))  # remove the mouse from the screen to avoid side effects

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_issue_296(self):
            """Test handling of disappered descendants"""
            wrp = self.dlg.wrapper_object()
            orig = wrp.element_info._element.FindAll
            wrp.element_info._element.FindAll = mock.Mock(side_effect=ValueError("Mocked value error"),
                                                          return_value=[])  # empty list
            self.assertEqual([], wrp.descendants())
            exception_err = comtypes.COMError(-2147220991, "Mocked COM error", ())
            wrp.element_info._element.FindAll = mock.Mock(side_effect=exception_err,
                                                          return_value=[])  # empty list
            self.assertEqual([], wrp.descendants())
            wrp.element_info._element.FindAll = orig  # restore the original method

        def test_issue_278(self):
            """Test that statement menu = app.MainWindow.Menu works for 'uia' backend"""
            menu_spec = self.dlg.Menu
            self.assertTrue(isinstance(menu_spec, WindowSpecification))

        def test_find_nontop_ctl_by_class_name_and_title(self):
            """Test getting a non-top control by a class name and a title"""
            # Look up for a non-top button control with 'Apply' caption
            self.dlg.wait('ready')
            caption = 'Apply'
            wins = self.app.windows(top_level_only=False,
                                    class_name='Button',
                                    title=caption)

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
            wins = self.app.windows(class_name='Window', title=caption)

            # Verify the number of found wrappers
            self.assertEqual(len(wins), 1)

            # Verify the caption of the found wrapper
            self.assertEqual(wins[0].texts()[0], caption)

        def test_class(self):
            """Test getting the classname of the dialog"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.class_name(), "Button")

        def test_window_text(self):
            """Test getting the window Text of the dialog"""
            label = self.dlg.TestLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"TestLabel")
            self.assertEqual(label.can_be_label, True)

        def test_control_id(self):
            """Test getting control ID"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.control_id(), None)

        def test_runtime_id(self):
            """Test getting runtime ID"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertNotEqual(button.__hash__(), 0)

            orig = button.element_info._element.GetRuntimeId
            exception_err = comtypes.COMError(-2147220991, 'An event was unable to invoke any of the subscribers', ())
            button.element_info._element.GetRuntimeId = mock.Mock(side_effect=exception_err)
            self.assertEqual(button.__hash__(), 0)
            button.element_info._element.GetRuntimeId = orig  # restore the original method

        def test_automation_id(self):
            """Test getting automation ID"""
            alpha_toolbar = self.dlg.child_window(title="Alpha", control_type="ToolBar")
            button = alpha_toolbar.child_window(control_type="Button",
                                                auto_id="OverflowButton").wrapper_object()
            self.assertEqual(button.automation_id(), "OverflowButton")

        def test_is_visible(self):
            """Test is_visible method of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.is_visible(), True)

        def test_is_enabled(self):
            """Test is_enabled method of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.is_enabled(), True)

        def test_process_id(self):
            """Test process_id method of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.process_id(), self.dlg.process_id())
            self.assertNotEqual(button.process_id(), 0)

        def test_is_dialog(self):
            """Test is_dialog method of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.is_dialog(), False)

        def test_parent(self):
            """Test getting a parent of a control"""
            button = self.dlg.Alpha.wrapper_object()
            self.assertEqual(button.parent(), self.dlg.wrapper_object())

        def test_top_level_parent(self):
            """Test getting a top-level parent of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.top_level_parent(), self.dlg.wrapper_object())

        def test_texts(self):
            """Test getting texts of a control"""
            self.assertEqual(self.dlg.texts(), ['WPF Sample Application'])

        def test_children(self):
            """Test getting children of a control"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(len(button.children()), 1)
            self.assertEqual(button.children()[0].class_name(), "TextBlock")

        def test_children_generator(self):
            """Test iterating children of a control"""
            button = self.dlg.child_window(class_name="Button", title="OK").wrapper_object()
            children = [child for child in button.iter_children()]
            self.assertEqual(len(children), 1)
            self.assertEqual(children[0].class_name(), "TextBlock")

        def test_descendants(self):
            """Test iterating descendants of a control"""
            toolbar = self.dlg.child_window(title="Alpha", control_type="ToolBar").wrapper_object()
            descendants = toolbar.descendants()
            self.assertEqual(len(descendants), 7)

        def test_descendants_generator(self):
            toolbar = self.dlg.child_window(title="Alpha", control_type="ToolBar").wrapper_object()
            descendants = [desc for desc in toolbar.iter_descendants()]
            self.assertSequenceEqual(toolbar.descendants(), descendants)

        def test_is_child(self):
            """Test is_child method of a control"""
            button = self.dlg.Alpha.wrapper_object()
            self.assertEqual(button.is_child(self.dlg.wrapper_object()), True)

        def test_equals(self):
            """Test controls comparisons"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertNotEqual(button, self.dlg.wrapper_object())
            self.assertEqual(button, button.element_info)
            self.assertEqual(button, button)

        def test_scroll(self):
            """Test scroll"""
            # Check an exception on a non-scrollable control
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
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

        # def testVerifyActionable(self):
        #    self.assertRaises()

        # def testVerifyEnabled(self):
        #    self.assertRaises()

        # def testVerifyVisible(self):
        #    self.assertRaises()

        def test_is_keyboard_focusable(self):
            """Test is_keyboard focusable method of several controls"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
            label = self.dlg.TestLabel.wrapper_object()
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            self.assertEqual(button.is_keyboard_focusable(), True)
            self.assertEqual(edit.is_keyboard_focusable(), True)
            self.assertEqual(label.is_keyboard_focusable(), False)

        def test_set_focus(self):
            """Test setting a keyboard focus on a control"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
            edit.set_focus()
            self.assertEqual(edit.has_keyboard_focus(), True)

        def test_type_keys(self):
            """Test sending key types to a control"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
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

        def test_no_pattern_interface_error(self):
            """Test a query interface exception handling"""
            button = self.dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()
            elem = button.element_info.element
            self.assertRaises(
                uia_defs.NoPatternInterfaceError,
                uia_defs.get_elem_interface,
                elem,
                "Selection",
            )

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

        def test_get_properties(self):
            """Test getting writeble properties of a control"""
            uia_props = set(['class_name',
                             'friendly_class_name',
                             'texts',
                             'control_id',
                             'rectangle',
                             'is_visible',
                             'is_enabled',
                             'control_count',
                             'is_keyboard_focusable',
                             'has_keyboard_focus',
                             'selection_indices',
                             'automation_id',
                             ])
            edit = self.dlg.TestLabelEdit.wrapper_object()
            props = set(edit.get_properties().keys())
            self.assertEqual(props, uia_props)

            # def test_draw_outline(self):
            #     """Test the outline was drawn."""
            #     # not sure why, but this extra call makes the test stable
            #     self.dlg.draw_outline()
            #
            #     # outline control
            #     button = self.dlg.OK.wrapper_object()
            #     button.draw_outline()
            #     img1 = button.capture_as_image()
            #     self.assertEqual(img1.getpixel((0, 0)), (0, 255, 0))  # green
            #
            #     # outline window
            #     self.dlg.draw_outline(colour="blue")
            #     img2 = self.dlg.capture_as_image()
            #     self.assertEqual(img2.getpixel((0, 0)), (0, 0, 255))  # blue

        def test_get_legacy_properties(self):
            """Test getting legacy properties of a control"""
            expected_properties = {'Value': '',
                                   'DefaultAction': 'Press',
                                   'Description': '',
                                   'Name': 'OK',
                                   'Help': '',
                                   'ChildId': 0,
                                   'KeyboardShortcut': '',
                                   'State': 1048576,
                                   'Role': 43}
            button_wrp = self.dlg.child_window(class_name="Button",
                                               title="OK").wrapper_object()

            actual_properties = button_wrp.legacy_properties()

            self.assertEqual(actual_properties, expected_properties)

        def test_capture_as_image_multi_monitor(self):
            with mock.patch('win32api.EnumDisplayMonitors') as mon_device:
                mon_device.return_value = (1, 2)
                rect = self.dlg.rectangle()
                expected = (rect.width(), rect.height())
                result = self.dlg.capture_as_image().size
                self.assertEqual(expected, result)


    class UIAWrapperMouseTests(unittest.TestCase):

        """Unit tests for mouse actions of the UIAWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)

            dlg = self.app.WPFSampleApplication
            self.button = dlg.child_window(class_name="Button",
                                           title="OK").wrapper_object()

            self.label = dlg.child_window(class_name="Text", title="TestLabel").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        # def test_click(self):
        #    pass

        def test_click_input(self):
            """Test click_input method of a control"""
            time.sleep(0.5)
            self.button.click_input()
            self.assertEqual(self.label.window_text(), "LeftClick")

        # def test_double_click(self):
        #    pass

        def test_double_click_input(self):
            """Test double_click_input method of a control"""
            self.button.double_click_input()
            self.assertEqual(self.label.window_text(), "DoubleClick")

        # def test_right_click(self):
        #    pass

        def test_right_click_input(self):
            """Test right_click_input method of a control"""
            time.sleep(0.5)
            self.button.right_click_input()
            self.assertEqual(self.label.window_text(), "RightClick")

            # def test_press_move_release(self):
            #    pass


    class UiaControlsTests(unittest.TestCase):

        """Unit tests for the UIA control wrappers"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            self.app = app.start(wpf_app_1)
            self.dlg = self.app.WPFSampleApplication

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_pretty_print(self):
            """Test __str__ and __repr__ methods for UIA based controls"""
            if six.PY3:
                assert_regex = self.assertRegex
            else:
                assert_regex = self.assertRegexpMatches

            wrp = self.dlg.OK.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.ButtonWrapper - 'OK', Button$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.ButtonWrapper - 'OK', Button, [0-9-]+>$")

            wrp = self.dlg.CheckBox.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.ButtonWrapper - 'CheckBox', CheckBox$", )
            assert_regex(wrp.__repr__(), "^<uia_controls\.ButtonWrapper - 'CheckBox', CheckBox, [0-9-]+>$", )

            wrp = self.dlg.child_window(class_name="TextBox").wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.EditWrapper - '', Edit$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.EditWrapper - '', Edit, [0-9-]+>$")
            assert_regex(wrp.element_info.__str__(), "^uia_element_info.UIAElementInfo - '', TextBox$")
            assert_regex(wrp.element_info.__repr__(), "^<uia_element_info.UIAElementInfo - '', TextBox, None>$")

            wrp = self.dlg.TabControl.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.TabControlWrapper - '', TabControl$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.TabControlWrapper - '', TabControl, [0-9-]+>$")

            wrp = self.dlg.MenuBar.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.MenuWrapper - 'System', Menu$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.MenuWrapper - 'System', Menu, [0-9-]+>$")

            wrp = self.dlg.Slider.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.SliderWrapper - '', Slider$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.SliderWrapper - '', Slider, [0-9-]+>$")

            wrp = self.dlg.TestLabel.wrapper_object()
            assert_regex(wrp.__str__(),
                         "^uia_controls.StaticWrapper - 'TestLabel', Static$")
            assert_regex(wrp.__repr__(),
                         "^<uia_controls.StaticWrapper - 'TestLabel', Static, [0-9-]+>$")

            wrp = self.dlg.wrapper_object()
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - 'WPF Sample Application', Dialog$")
            assert_regex(wrp.__repr__(), "^<uiawrapper\.UIAWrapper - 'WPF Sample Application', Dialog, [0-9-]+>$")

            # ElementInfo.__str__
            assert_regex(wrp.element_info.__str__(),
                         "^uia_element_info.UIAElementInfo - 'WPF Sample Application', Window$")
            assert_regex(wrp.element_info.__repr__(),
                         "^<uia_element_info.UIAElementInfo - 'WPF Sample Application', Window, [0-9-]+>$")

            # mock a failure in window_text() method
            orig = wrp.window_text
            wrp.window_text = mock.Mock(return_value="")  # empty text
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - '', Dialog$")
            assert_regex(wrp.__repr__(), "^<uiawrapper\.UIAWrapper - '', Dialog, [0-9-]+>$")
            wrp.window_text.return_value = u'\xd1\xc1\\\xa1\xb1\ua000'  # unicode string
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - '.+', Dialog$")
            wrp.window_text = orig  # restore the original method

            # mock a failure in element_info.name property (it's based on _get_name())
            orig = wrp.element_info._get_name
            wrp.element_info._get_name = mock.Mock(return_value=None)
            assert_regex(wrp.element_info.__str__(), "^uia_element_info\.UIAElementInfo - 'None', Window$")
            assert_regex(wrp.element_info.__repr__(), "^<uia_element_info\.UIAElementInfo - 'None', Window, [0-9-]+>$")
            wrp.element_info._get_name = orig

        def test_pretty_print_encode_error(self):
            """Test __repr__ method for BaseWrapper with specific Unicode text (issue #594)"""
            wrp = self.dlg.wrapper_object()
            wrp.window_text = mock.Mock(return_value=u'\xb7')
            print(wrp)
            print(repr(wrp))

        def test_friendly_class_names(self):
            """Test getting friendly class names of common controls"""
            button = self.dlg.OK.wrapper_object()
            self.assertEqual(button.friendly_class_name(), "Button")

            friendly_name = self.dlg.CheckBox.friendly_class_name()
            self.assertEqual(friendly_name, "CheckBox")

            friendly_name = self.dlg.Apply.friendly_class_name()
            self.assertEqual(friendly_name, "Button")

            friendly_name = self.dlg.ToggleMe.friendly_class_name()
            self.assertEqual(friendly_name, "Button")

            friendly_name = self.dlg.Yes.friendly_class_name()
            self.assertEqual(friendly_name, "RadioButton")

            friendly_name = self.dlg.TabControl.friendly_class_name()
            self.assertEqual(friendly_name, "TabControl")

            edit = self.dlg.child_window(class_name="TextBox").wrapper_object()
            self.assertEqual(edit.friendly_class_name(), "Edit")

            slider = self.dlg.Slider.wrapper_object()
            self.assertEqual(slider.friendly_class_name(), "Slider")

            self.assertEqual(self.dlg.MenuBar.friendly_class_name(), "Menu")

            self.assertEqual(self.dlg.Toolbar.friendly_class_name(), "Toolbar")

            # Switch tab view
            tab_item_wrp = self.dlg.TreeAndListViews.set_focus()
            ctrl = tab_item_wrp.children(control_type="DataGrid")[0]
            self.assertEqual(ctrl.friendly_class_name(), "ListView")
            i = ctrl.get_item(1)
            self.assertEqual(i.friendly_class_name(), "DataItem")

            ctrl = tab_item_wrp.children(control_type="Tree")[0]
            self.assertEqual(ctrl.friendly_class_name(), "TreeView")

            ti = self.dlg.Tree_and_List_ViewsTabItem.DateElements
            self.assertEqual(ti.friendly_class_name(), "TreeItem")

        def test_check_box(self):
            """Test 'toggle' and 'toggle_state' for the check box control"""
            # Get a current state of the check box control
            check_box = self.dlg.CheckBox.wrapper_object()
            cur_state = check_box.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_inderteminate)

            # Toggle the next state
            cur_state = check_box.toggle().get_toggle_state()

            # Get a new state of the check box control
            self.assertEqual(cur_state, uia_defs.toggle_state_off)

        def test_toggle_button(self):
            """Test 'toggle' and 'toggle_state' for the toggle button control"""
            # Get a current state of the check box control
            button = self.dlg.ToggleMe.wrapper_object()
            cur_state = button.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_on)

            # Toggle the next state
            cur_state = button.toggle().get_toggle_state()

            # Get a new state of the check box control
            self.assertEqual(cur_state, uia_defs.toggle_state_off)

            # Toggle the next state
            cur_state = button.toggle().get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_on)

        def test_button_click(self):
            """Test the click method for the Button control"""
            label = self.dlg.child_window(class_name="Text",
                                          title="TestLabel").wrapper_object()
            self.dlg.Apply.click()
            self.assertEqual(label.window_text(), "ApplyClick")

        def test_radio_button(self):
            """Test 'select' and 'is_selected' for the radio button control"""
            yes = self.dlg.Yes.wrapper_object()
            cur_state = yes.is_selected()
            self.assertEqual(cur_state, False)

            cur_state = yes.select().is_selected()
            self.assertEqual(cur_state, True)

            no = self.dlg.No.wrapper_object()
            cur_state = no.click().is_selected()
            self.assertEqual(cur_state, True)

        def test_combobox_texts(self):
            """Test items texts for the combo box control"""
            # The ComboBox on the sample app has following items:
            # 0. Combo Item 1
            # 1. Combo Item 2
            ref_texts = ['Combo Item 1', 'Combo Item 2']

            combo_box = self.dlg.ComboBox.wrapper_object()
            self.assertEqual(combo_box.item_count(), len(ref_texts))
            for t in combo_box.texts():
                self.assertEqual((t in ref_texts), True)

            # Mock a 0 pointer to COM element
            combo_box.iface_item_container.FindItemByProperty = mock.Mock(return_value=0)
            self.assertEqual(combo_box.texts(), ref_texts)

            # Mock a combobox without "ItemContainer" pattern
            combo_box.iface_item_container.FindItemByProperty = mock.Mock(side_effect=uia_defs.NoPatternInterfaceError())
            self.assertEqual(combo_box.texts(), ref_texts)

            # Mock a combobox without "ExpandCollapse" pattern
            # Expect empty texts
            combo_box.iface_expand_collapse.Expand = mock.Mock(side_effect=uia_defs.NoPatternInterfaceError())
            self.assertEqual(combo_box.texts(), [])

        def test_combobox_select(self):
            """Test select related methods for the combo box control"""
            combo_box = self.dlg.ComboBox.wrapper_object()

            # Verify combobox properties and an initial state
            self.assertEqual(combo_box.can_select_multiple(), 0)
            self.assertEqual(combo_box.is_selection_required(), False)
            self.assertEqual(len(combo_box.get_selection()), 0)

            # The ComboBox on the sample app has following items:
            # 0. Combo Item 1
            # 1. Combo Item 2
            combo_box.select(0)
            self.assertEqual(combo_box.selected_text(), 'Combo Item 1')
            self.assertEqual(combo_box.selected_index(), 0)

            collapsed = combo_box.is_collapsed()
            self.assertEqual(collapsed, True)

            combo_box.select(1)
            self.assertEqual(combo_box.selected_text(), 'Combo Item 2')
            self.assertEqual(combo_box.selected_index(), 1)

            combo_box.select('Combo Item 1')
            self.assertEqual(combo_box.selected_text(), 'Combo Item 1')

            # Try to use unsupported item type as a parameter for select
            self.assertRaises(ValueError, combo_box.select, 1.2)

            # Try to select a non-existing item,
            # verify the selected item didn't change
            self.assertRaises(IndexError, combo_box.select, 'Combo Item 23455')
            self.assertEqual(combo_box.selected_text(), 'Combo Item 1')

        def test_combobox_expand_collapse(self):
            """Test 'expand' and 'collapse' for the combo box control"""
            combo_box = self.dlg.ComboBox.wrapper_object()

            collapsed = combo_box.is_collapsed()
            self.assertEqual(collapsed, True)

            expanded = combo_box.expand().is_expanded()
            self.assertEqual(expanded, True)

            collapsed = combo_box.collapse().is_collapsed()
            self.assertEqual(collapsed, True)


    class TabControlWrapperTests(unittest.TestCase):

        """Unit tests for the TabControlWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            app = app.start(wpf_app_1)
            dlg = app.WPFSampleApplication

            self.app = app
            self.ctrl = dlg.child_window(class_name="TabControl").wrapper_object()
            self.texts = [u"General", u"Tree and List Views", u"ListBox and Grid"]

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_tab_count(self):
            """Test the tab count in the Tab control"""
            self.assertEqual(self.ctrl.tab_count(), len(self.texts))

        def test_get_selected_tab(self):
            """Test selecting a tab by index or by name and getting an index of the selected tab"""
            # Select a tab by name, use chaining to get the index of the selected tab
            idx = self.ctrl.select(u"Tree and List Views").get_selected_tab()
            self.assertEqual(idx, 1)
            # Select a tab by index
            self.ctrl.select(0)
            self.assertEqual(self.ctrl.get_selected_tab(), 0)

        def test_texts(self):
            """Make sure the tabs captions are read correctly"""
            self.assertEqual(self.ctrl.texts(), self.texts)


    class EditWrapperTests(unittest.TestCase):

        """Unit tests for the EditWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            app = app.start(wpf_app_1)

            self.app = app
            self.dlg = app.WPFSampleApplication

            self.edit = self.dlg.child_window(class_name="TextBox").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_set_window_text(self):
            """Test setting text value of control (the text in textbox itself)"""
            text_to_set = "This test"

            self.assertRaises(UserWarning, self.edit.set_window_text, text_to_set)
            self.assertEqual(self.edit.text_block(), text_to_set)

            self.assertRaises(UserWarning, self.edit.set_window_text, " is done", True)
            self.assertEqual(self.edit.text_block(), text_to_set + " is done")

        def test_set_text(self):
            """Test setting the text of the edit control"""
            self.edit.set_edit_text("Some text")
            self.assertEqual(self.edit.text_block(), "Some text")

            self.edit.set_edit_text(579)
            self.assertEqual(self.edit.text_block(), "579")

            self.edit.set_edit_text(333, pos_start=1, pos_end=2)
            self.assertEqual(self.edit.text_block(), "53339")

        def test_line_count(self):
            """Test getting the line count of the edit control"""
            self.edit.set_edit_text("Here is some text")

            self.assertEqual(self.edit.line_count(), 1)

        def test_cet_line(self):
            """Test getting each line of the edit control"""
            test_data = "Here is some text"
            self.edit.set_edit_text(test_data)

            self.assertEqual(self.edit.get_line(0), test_data)

        def test_get_value(self):
            """Test getting value of the edit control"""
            test_data = "Some value"
            self.edit.set_edit_text(test_data)

            self.assertEqual(self.edit.get_value(), test_data)

        def test_text_block(self):
            """Test getting the text block of the edit control"""
            test_data = "Here is some text"
            self.edit.set_edit_text(test_data)

            self.assertEqual(self.edit.text_block(), test_data)

        def test_select(self):
            """Test selecting text in the edit control in various ways"""
            self.edit.set_edit_text("Some text")

            self.edit.select(0, 0)
            self.assertEqual((0, 0), self.edit.selection_indices())

            self.edit.select()
            self.assertEqual((0, 9), self.edit.selection_indices())

            self.edit.select(1, 7)
            self.assertEqual((1, 7), self.edit.selection_indices())

            self.edit.select(5, 2)
            self.assertEqual((2, 5), self.edit.selection_indices())

            self.edit.select("me t")
            self.assertEqual((2, 6), self.edit.selection_indices())

            self.assertRaises(RuntimeError, self.edit.select, "123")

    class SliderWrapperTests(unittest.TestCase):

        """Unit tests for the EditWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            app = app.start(wpf_app_1)

            self.app = app
            self.dlg = app.WPFSampleApplication

            self.slider = self.dlg.child_window(class_name="Slider").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_min_value(self):
            """Test getting minimum value of the Slider"""
            self.assertEqual(self.slider.min_value(), 0.0)

        def test_max_value(self):
            """Test getting maximum value of the Slider"""
            self.assertEqual(self.slider.max_value(), 100.0)

        def test_small_change(self):
            """Test Getting small change of slider's thumb"""
            self.assertEqual(self.slider.small_change(), 0.1)

        def test_large_change(self):
            """Test Getting large change of slider's thumb"""
            self.assertEqual(self.slider.large_change(), 1.0)

        def test_value(self):
            """Test getting current position of slider's thumb"""
            self.assertEqual(self.slider.value(), 70.0)

        def test_set_value(self):
            """Test setting position of slider's thumb"""
            self.slider.set_value(24)
            self.assertEqual(self.slider.value(), 24.0)

            self.slider.set_value(33.3)
            self.assertEqual(self.slider.value(), 33.3)

            self.slider.set_value("75.4")
            self.assertEqual(self.slider.value(), 75.4)

            self.assertRaises(ValueError, self.slider.set_value, -1)
            self.assertRaises(ValueError, self.slider.set_value, 102)

            self.assertRaises(ValueError, self.slider.set_value, [50, ])

    class ListViewWrapperTests(unittest.TestCase):

        """Unit tests for the ListViewWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            app = app.start(wpf_app_1)
            dlg = app.WPFSampleApplication

            self.app = app

            self.listview_tab = dlg.Tree_and_List_Views
            self.listbox_datagrid_tab = dlg.ListBox_and_Grid

            self.listview_texts = [
                [u"1", u"Tomatoe", u"Red"],
                [u"2", u"Cucumber", u"Green", ],
                [u"3", u"Reddish", u"Purple", ],
                [u"4", u"Cauliflower", u"White", ],
                [u"5", u"Cupsicum", u"Yellow", ],
                [u"6", u"Cupsicum", u"Red", ],
                [u"7", u"Cupsicum", u"Green", ],
            ]

            self.listbox_texts = [
                [u"TextItem 1", ],
                [u"TextItem 2", ],
                [u"ButtonItem", ],
                [u"CheckItem", ],
                [u"TextItem 3", ],
                [u"TextItem 4", ],
                [u"TextItem 5", ],
                [u"TextItem 6", ],
                [u"TextItem 7", ],
                [u"TextItem 8", ],
            ]

            self.datagrid_texts = [
                [u"0", u"A0", u"B0", u"C0", u"D0", u"E0", u"", ],
                [u"1", u"A1", u"B1", u"C1", u"D1", u"E1", u"", ],
                [u"2", u"A2", u"B2", u"C2", u"D2", u"E2", u"", ],
                [u"3", u"A3", u"B3", u"C3", u"D3", u"E3", u"", ],
            ]

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_friendly_class_name(self):
            """Test friendly class name of the ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            self.assertEqual(listview.friendly_class_name(), u"ListView")

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            self.assertEqual(listbox.friendly_class_name(), u"ListBox")

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            self.assertEqual(datagrid.friendly_class_name(), u"ListView")

        def test_item_count(self):
            """Test the items count in the ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            self.assertEqual(listview.item_count(), len(self.listview_texts))

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            #listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            # self.assertEqual(listbox.item_count(), len(self.listbox_texts))

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            self.assertEqual(datagrid.item_count(), len(self.datagrid_texts))

        def test_column_count(self):
            """Test the columns count in the ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            self.assertEqual(listview.column_count(), len(self.listview_texts[0]))

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            self.assertEqual(listbox.column_count(), 0)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            self.assertEqual(datagrid.column_count(), len(self.datagrid_texts[0]) - 1)

        def test_get_header_control(self):
            """Test getting a Header control and Header Item control of ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            hdr_ctl = listview.get_header_control()
            self.assertTrue(isinstance(hdr_ctl, uia_ctls.HeaderWrapper))

            # HeaderItem of ListView
            hdr_itm = hdr_ctl.children()[2]
            self.assertTrue(isinstance(hdr_itm, uia_ctls.HeaderItemWrapper))
            self.assertTrue(hdr_itm.iface_transform.CurrentCanResize, True)

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            self.assertEqual(listbox.get_header_control(), None)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            self.assertTrue(isinstance(datagrid.get_header_control(), uia_ctls.HeaderWrapper))

        def test_get_column(self):
            """Test get_column() method for the ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            listview_col = listview.get_column(1)
            self.assertEqual(listview_col.texts()[0], u"Name")

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            self.assertRaises(IndexError, listbox.get_column, 0)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            datagrid_col = datagrid.get_column(2)
            self.assertEqual(datagrid_col.texts()[0], u"B")

            self.assertRaises(IndexError, datagrid.get_column, 10)

        def test_cell(self):
            """Test getting a cell of the ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            cell = listview.cell(3, 2)
            self.assertEqual(cell.window_text(), self.listview_texts[3][2])

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            cell = listbox.cell(10, 10)
            self.assertEqual(cell, None)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            cell = datagrid.cell(2, 0)
            self.assertEqual(cell.window_text(), self.datagrid_texts[2][0])

            self.assertRaises(TypeError, datagrid.cell, 1.5, 1)

            self.assertRaises(IndexError, datagrid.cell, 10, 10)

        def test_cells(self):
            """Test getting a cells of the ListView controls"""
            def compare_cells(cells, control):
                for i in range(0, control.item_count()):
                    for j in range(0, control.column_count()):
                        self.assertEqual(cells[i][j], control.cell(i, j))

            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            compare_cells(listview.cells(), listview)

            # DataGrid
            self.listbox_datagrid_tab.set_focus()
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            compare_cells(datagrid.cells(), datagrid)

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            cells = listbox.cells()
            self.assertEqual(cells[listbox.item_count() - 1][0].window_text(), "TextItem 7")
            self.assertEqual(cells[3][0].window_text(), "CheckItem")

        def test_get_item(self):
            """Test getting an item of ListView controls"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            item = listview.get_item(u"Reddish")
            self.assertEqual(item.texts(), self.listview_texts[2])

            self.assertRaises(ValueError, listview.get_item, u"Apple")

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            item = listbox.get_item(u"TextItem 2")
            self.assertEqual(item.texts(), self.listbox_texts[1])

            item = listbox.get_item(3)
            self.assertEqual(item.texts(), self.listbox_texts[3])

            item = listbox.get_item(u"TextItem 8")
            self.assertEqual(item.texts(), self.listbox_texts[9])

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            item = datagrid.get_item(u"B2")
            self.assertEqual(item.texts(), self.datagrid_texts[2])

            item = datagrid.get_item(3)
            self.assertEqual(item.texts(), self.datagrid_texts[3])

            self.assertRaises(TypeError, datagrid.get_item, 12.3)

        def test_get_items(self):
            """Test getting all items of ListView controls"""
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            content = [item.texts() for item in listview.get_items()]
            self.assertEqual(content, self.listview_texts)

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            content = [item.texts() for item in listbox.get_items()]
            # self.assertEqual(content, self.listbox_texts)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            content = [item.texts() for item in datagrid.get_items()]
            self.assertEqual(content, self.datagrid_texts)

        def test_texts(self):
            """Test getting all items of ListView controls"""
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            self.assertEqual(listview.texts(), self.listview_texts)

            # ListBox
            self.listbox_datagrid_tab.set_focus()
            #listbox = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0]
            # self.assertEqual(listbox.texts(), self.listbox_texts)

            # DataGrid
            datagrid = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0]
            self.assertEqual(datagrid.texts(), self.datagrid_texts)

        def test_select_and_get_item(self):
            """Test selecting an item of the ListView control"""
            self.listview_tab.set_focus()
            self.ctrl = self.listview_tab.children(class_name=u"ListView")[0]
            # Verify get_selected_count
            self.assertEqual(self.ctrl.get_selected_count(), 0)

            # Select by an index
            row = 1
            i = self.ctrl.get_item(row)
            self.assertEqual(i.is_selected(), False)
            self.assertRaises(uia_defs.NoPatternInterfaceError, i.is_checked)
            i.select()
            self.assertEqual(i.is_selected(), True)
            cnt = self.ctrl.get_selected_count()
            self.assertEqual(cnt, 1)
            rect = self.ctrl.get_item_rect(row)
            self.assertEqual(rect, i.rectangle())

            # Select by text
            row = '3'
            i = self.ctrl.get_item(row)
            i.select()
            self.assertEqual(i.is_selected(), True)
            row = 'White'
            i = self.ctrl.get_item(row)
            i.select()
            i = self.ctrl.get_item(3)  # re-get the item by a row index
            self.assertEqual(i.is_selected(), True)

            row = None
            self.assertRaises(TypeError, self.ctrl.get_item, row)

    class ListViewWrapperTestsWinForms(unittest.TestCase):

        """Unit tests for the ListViewWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            self.app = Application(backend='uia').start(winfoms_app_grid)
            self.dlg = self.app.Dialog

            self.add_col_button = self.dlg.AddCol
            self.add_row_button = self.dlg.AddRow
            self.row_header_button = self.dlg.RowHeader
            self.col_header_button = self.dlg.ColHeader
            self.list_box = self.dlg.ListBox

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_list_box_item_selection(self):
            """Test get_item method"""
            self.list_box.set_focus()
            list_box_item = self.list_box.get_item('item (2)')
            self.assertFalse(list_box_item.is_selected())
            list_box_item.select()
            self.assertTrue(list_box_item.is_selected())

        def test_list_box_getitem_overload(self):
            """Test __getitem__ method"""
            self.list_box.set_focus()
            list_box_item = self.list_box['item (2)']
            self.assertFalse(list_box_item.is_selected())
            list_box_item.select()
            self.assertTrue(list_box_item.is_selected())

        def test_empty_grid(self):
            """Test some error cases handling"""
            self.dlg.set_focus()
            table = self.dlg.Table
            self.assertEqual(len(table.cells()), 0)
            self.assertRaises(IndexError, table.cell, 0, 0)
            self.assertRaises(IndexError, table.get_item, 0)

        def test_skip_headers(self):
            """Test some error cases handling"""
            self.dlg.set_focus()
            self.add_col_button.click()
            table = self.dlg.Table
            cells = table.cells()
            self.assertEqual(len(cells), 1)
            self.assertEqual(len(cells[0]), 1)
            self.assertFalse(isinstance(cells[0][0], uia_ctls.HeaderWrapper))

        def test_cell_and_cells_equals(self):
            """Test equivalence of cell and cells methods"""
            def compare_cells():
                table = self.dlg.Table
                cells = table.cells()
                self.assertEqual(len(cells), 3)
                self.assertEqual(len(cells[0]), 2)
                for row_ind in range(0, 3):
                    for col_ind in range(0, 2):
                        self.assertEqual(cells[row_ind][col_ind], table.cell(row_ind, col_ind))

            self.add_col_button.click()
            self.add_col_button.click()
            self.add_row_button.click()
            self.add_row_button.click()
            compare_cells()

            self.row_header_button.click()
            compare_cells()

            self.row_header_button.click()
            self.col_header_button.click()
            compare_cells()

        def test_unsupported_columns(self):
            """Test raise NotImplemented errors for columns methods"""
            self.dlg.set_focus()
            table = self.dlg.Table
            self.assertRaises(NotImplementedError, table.column_count)
            self.assertRaises(NotImplementedError, table.get_column, 0)

        def test_get_header_controls(self):
            """Test get header controls method"""
            self.add_col_button.click()
            table = self.dlg.Table
            headers = table.get_header_controls()
            self.assertEqual(len(headers), 3)

            self.col_header_button.click()
            headers = table.get_header_controls()
            self.assertEqual(len(headers), 1)

            self.row_header_button.click()
            headers = table.get_header_controls()
            self.assertEqual(len(headers), 0)


    class MenuBarTestsWinForms(unittest.TestCase):

        """Unit tests for the MenuBar class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            self.app = Application(backend='uia').start(winfoms_app_grid)
            self.dlg = self.app.Dialog

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_can_select_multiple_items(self):
            """Test menu_select multimple items with action"""
            table = self.dlg.Table
            cells = table.cells()
            self.assertEqual(len(table.cells()), 0)
            self.dlg.menu_select('#0 -> #1 -> #1 -> #0 -> #0 -> #4 ->#0')
            cells = table.cells()
            self.assertEqual(len(cells), 1)
            self.assertEqual(len(cells[0]), 1)

        def test_can_select_top_menu(self):
            """Test menu_select with single item"""
            first_menu_item = self.dlg['menuStrip1'].children()[0]
            point = first_menu_item.rectangle().mid_point()
            child_from_point = self.dlg.from_point(point.x, point.y + 20)
            self.assertEqual(child_from_point.element_info.name, 'Form1')
            self.dlg.menu_select('tem1')
            time.sleep(0.1)
            child_from_point = self.dlg.from_point(point.x, point.y + 20)
            self.assertEqual(child_from_point.element_info.name, 'tem1DropDown')


    class EditTestsWinForms(unittest.TestCase):

        """Unit tests for the WinFormEdit class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            self.app = Application(backend='uia').start(winfoms_app_grid)
            self.dlg = self.app.Dialog

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_readonly_and_editable_edits(self):
            """Test editable method for editable edit"""
            self.assertEqual(self.dlg.Edit2.get_value(), "Editable")
            self.assertTrue(self.dlg.Edit2.is_editable())
            self.assertEqual(self.dlg.Edit1.get_value(), "ReadOnly")
            self.assertFalse(self.dlg.Edit1.is_editable())


    class ComboBoxTestsWinForms(unittest.TestCase):

        """Unit tests for the ComboBoxWrapper class with WinForms app"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            self.app = app.start(winfoms_app_grid)
            self.dlg = dlg = app.Form1

            self.combo_editable = dlg.child_window(auto_id="comboRowType", control_type="ComboBox").wrapper_object()
            self.combo_fixed = dlg.child_window(auto_id="comboBoxReadOnly", control_type="ComboBox").wrapper_object()
            self.combo_simple = dlg.child_window(auto_id="comboBoxSimple", control_type="ComboBox").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_expand_collapse(self):
            """Test methods .expand() and .collapse() for WinForms combo box"""
            self.dlg.set_focus()
            test_data = [(self.combo_editable, 'editable'), (self.combo_fixed, 'fixed'), (self.combo_simple, 'simple')]
            for combo, combo_name in test_data:
                if combo != self.combo_simple:
                    self.assertFalse(combo.is_expanded(),
                        msg='{} combo box must be collapsed initially'.format(combo_name))
                # test that method allows chaining
                self.assertEqual(combo.expand(), combo,
                    msg='Method .expand() for {} combo box must return self'.format(combo_name))
                self.assertTrue(combo.is_expanded(),
                    msg='{} combo box has not been expanded!'.format(combo_name))

                # .expand() keeps already expanded state (and still allows chaining)
                self.assertEqual(combo.expand(), combo,
                    msg='Method .expand() for {} combo box must return self, always!'.format(combo_name))
                self.assertTrue(combo.is_expanded(),
                    msg='{} combo box does NOT keep expanded state!'.format(combo_name))

                # collapse
                self.assertEqual(combo.collapse(), combo,
                    msg='Method .collapse() for {} combo box must return self'.format(combo_name))
                if combo != self.combo_simple:
                    self.assertFalse(combo.is_expanded(),
                        msg='{} combo box has not been collapsed!'.format(combo_name))

                # collapse already collapsed should keep collapsed state
                self.assertEqual(combo.collapse(), combo,
                    msg='Method .collapse() for {} combo box must return self, always!'.format(combo_name))
                if combo != self.combo_simple:
                    self.assertFalse(combo.is_expanded(),
                        msg='{} combo box does NOT keep collapsed state!'.format(combo_name))

        def test_texts(self):
            """Test method .texts() for WinForms combo box"""
            self.dlg.set_focus()
            editable_texts = [u'Numbers', u'Letters', u'Special symbols']
            fixed_texts = [u'Item 1', u'Item 2', u'Last Item']
            simple_texts = [u'Simple 1', u'Simple Two', u'The Simplest']

            self.assertEqual(self.combo_editable.texts(), editable_texts)
            self.assertEqual(self.combo_editable.expand().texts(), editable_texts)
            self.assertTrue(self.combo_editable.is_expanded())
            self.combo_editable.collapse()

            self.assertEqual(self.combo_fixed.texts(), fixed_texts)
            self.assertEqual(self.combo_fixed.expand().texts(), fixed_texts)
            self.assertTrue(self.combo_fixed.is_expanded())
            self.combo_fixed.collapse()

            self.assertEqual(self.combo_simple.texts(), simple_texts)
            self.assertEqual(self.combo_simple.expand().texts(), simple_texts)
            self.assertTrue(self.combo_simple.is_expanded())
            self.combo_simple.collapse()

        def test_select(self):
            """Test method .select() for WinForms combo box"""
            self.dlg.set_focus()
            self.combo_editable.select(u'Letters')
            self.assertEqual(self.combo_editable.selected_text(), u'Letters')
            self.assertEqual(self.combo_editable.selected_index(), 1)
            self.combo_editable.select(2)
            self.assertEqual(self.combo_editable.selected_text(), u'Special symbols')
            self.assertEqual(self.combo_editable.selected_index(), 2)

            self.combo_fixed.select(u'Last Item')
            self.assertEqual(self.combo_fixed.selected_text(), u'Last Item')
            self.assertEqual(self.combo_fixed.selected_index(), 2)
            self.combo_fixed.select(1)
            self.assertEqual(self.combo_fixed.selected_text(), u'Item 2')
            self.assertEqual(self.combo_fixed.selected_index(), 1)

            self.combo_simple.select(u'The Simplest')
            self.assertEqual(self.combo_simple.selected_text(), u'The Simplest')
            self.assertEqual(self.combo_simple.selected_index(), 2)
            self.combo_simple.select(0)
            self.assertEqual(self.combo_simple.selected_text(), u'Simple 1')
            self.assertEqual(self.combo_simple.selected_index(), 0)

        def test_select_errors(self):
            """Test errors in method .select() for WinForms combo box"""
            self.dlg.set_focus()
            for combo in [self.combo_editable, self.combo_fixed, self.combo_simple]:
                self.assertRaises(IndexError, combo.select, u'FFFF')
                self.assertRaises(IndexError, combo.select, 50)

        def test_item_count(self):
            """Test method .item_count() for WinForms combo box"""
            self.dlg.set_focus()
            self.assertEqual(self.combo_editable.item_count(), 3)
            self.assertEqual(self.combo_fixed.item_count(), 3)
            self.assertEqual(self.combo_simple.item_count(), 3)

        def test_from_point(self):
            """Test method .from_point() for WinForms combo box"""
            self.dlg.set_focus()
            x, y = self.combo_fixed.rectangle().mid_point()
            combo_from_point = self.dlg.from_point(x, y)
            self.assertEqual(combo_from_point, self.combo_fixed)

            combo2_from_point = Desktop(backend="uia").from_point(x, y)
            self.assertEqual(combo2_from_point, self.combo_fixed)

        def test_top_from_point(self):
            """Test method .top_from_point() for WinForms combo box"""
            dlg_wrapper = self.dlg.set_focus()
            x, y = self.combo_fixed.rectangle().mid_point()
            dlg_from_point = self.dlg.top_from_point(x, y)
            self.assertEqual(dlg_from_point, dlg_wrapper)

            dlg2_from_point = Desktop(backend="uia").top_from_point(x, y)
            self.assertEqual(dlg2_from_point, dlg_wrapper)


    class ListItemWrapperTests(unittest.TestCase):

        """Unit tests for the ListItemWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            app = Application(backend='uia')
            app = app.start(wpf_app_1)
            dlg = app.WPFSampleApplication

            self.app = app

            self.listview_tab = dlg.Tree_and_List_Views
            self.listbox_datagrid_tab = dlg.ListBox_and_Grid

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_friendly_class_name(self):
            """Test getting friendly class name"""
            # DataItem
            self.listview_tab.set_focus()
            listview_item = self.listview_tab.children(class_name=u"ListView")[0].get_item(2)
            self.assertEqual(listview_item.friendly_class_name(), u"DataItem")

            # ListBoxItem
            self.listbox_datagrid_tab.set_focus()
            listbox_item = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0].get_item(3)
            self.assertEqual(listbox_item.friendly_class_name(), u"ListItem")

            # DataGridRow
            datagrid_row = self.listbox_datagrid_tab.children(class_name=u"DataGrid")[0].get_item(1)
            self.assertEqual(datagrid_row.friendly_class_name(), u"DataItem")

        def test_selection(self):
            """Test selection of ListItem"""
            self.listview_tab.set_focus()
            listview_item = self.listview_tab.children(class_name=u"ListView")[0].get_item(2)
            self.assertFalse(listview_item.is_selected())
            listview_item.select()
            self.assertTrue(listview_item.is_selected())

        def test_is_checked(self):
            """Test is_checked() method of ListItemWrapper"""
            self.listbox_datagrid_tab.set_focus()
            listbox_item = self.listbox_datagrid_tab.children(class_name=u"ListBox")[0].get_item(u"CheckItem")
            self.assertRaises(uia_defs.NoPatternInterfaceError, listbox_item.is_checked)

        def test_texts(self):
            """Test getting texts of ListItem"""
            self.listview_tab.set_focus()
            listview_item = self.listview_tab.children(class_name=u"ListView")[0].get_item(1)
            texts = [u"2", u"Cucumber", u"Green"]
            self.assertEqual(listview_item.texts(), texts)

    class MenuWrapperWpfTests(unittest.TestCase):

        """Unit tests for the MenuWrapper class on WPF demo"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)
            self.dlg = self.app.WPFSampleApplication

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_menu_by_index(self):
            """Test selecting a WPF menu item by index"""
            path = "#0->#1->#1"  # "File->Close->Later"
            self.dlg.menu_select(path)
            label = self.dlg.MenuLaterClickLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"MenuLaterClick")

            # Non-existing paths
            path = "#5->#1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)
            path = "#0->#1->#1->#2->#3"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

        def test_menu_by_exact_text(self):
            """Test selecting a WPF menu item by exact text match"""
            path = "File->Close->Later"
            self.dlg.menu_select(path, True)
            label = self.dlg.MenuLaterClickLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"MenuLaterClick")

            # A non-exact menu name
            path = "File->About"
            self.assertRaises(IndexError, self.dlg.menu_select, path, True)

        def test_menu_by_best_match_text(self):
            """Test selecting a WPF menu item by best match text"""
            path = "file-> close -> later"
            self.dlg.menu_select(path, False)
            label = self.dlg.MenuLaterClickLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"MenuLaterClick")

        def test_menu_by_mixed_match(self):
            """Test selecting a WPF menu item by a path with mixed specifiers"""
            path = "file-> #1 -> later"
            self.dlg.menu_select(path, False)
            label = self.dlg.MenuLaterClickLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"MenuLaterClick")

            # Bad specifiers
            path = "file-> 1 -> later"
            self.assertRaises(IndexError, self.dlg.menu_select, path)
            path = "#0->#1->1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)
            path = "0->#1->1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

    class MenuWrapperNotepadTests(unittest.TestCase):

        """Unit tests for the MenuWrapper class on Notepad"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            Timings.defaults()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start("notepad.exe")
            self.dlg = self.app.UntitledNotepad
            ActionLogger().log("MenuWrapperNotepadTests::setUp, wait till Notepad dialog is ready")
            self.dlg.wait("ready")

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_friendly_class_name(self):
            """Test getting the friendly class name of the menu"""
            menu = self.dlg.descendants(control_type="MenuBar")[0]
            self.assertEqual(menu.friendly_class_name(), "Menu")

        def test_menu_by_index(self):
            """Test selecting a menu item by index"""
            path = "#4->#1"  # "Help->About Notepad"
            self.dlg.menu_select(path)

            # 'About Notepad' dialog showed upon execution of menu_select
            self.assertEqual(self.dlg.AboutNotepad.is_active(), True)

            # menu_select rises the AttributeError when a dialog doesn't have menus
            self.assertRaises(AttributeError, self.dlg.AboutNotepad.menu_select, "#10->#2")
            self.dlg.AboutNotepad.close()

            # A non-existing path
            path = "#5->#1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

            # Get a menu item by index
            menu = self.dlg.children(control_type="MenuBar")[0]
            item = menu.item_by_index(4)
            self.assertEqual(isinstance(item, uia_ctls.MenuItemWrapper), True)
            self.assertEqual(item.window_text(), 'Help')
            item.select()
            item.close()

        def test_is_dialog(self):
            """Test that method is_dialog() works as expected"""
            self.assertEqual(self.dlg.is_dialog(), True)
            self.assertEqual(self.dlg.Edit.is_dialog(), False)

        def test_issue_532(self):
            """Test selecting a combobox item when it's wrapped in ListView"""
            path = "Format -> Font"
            self.dlg.menu_select(path)
            combo_box = self.app.top_window().Font.ScriptComboBox.wrapper_object()
            combo_box.select('Greek')
            self.assertEqual(combo_box.selected_text(), 'Greek')
            self.assertRaises(IndexError, combo_box.select, 'NonExistingScript')

        def test_menu_by_exact_text(self):
            """Test selecting a menu item by exact text match"""
            path = "Help->About Notepad"
            self.dlg.menu_select(path, True)
            self.assertEqual(self.dlg.AboutNotepad.is_dialog(), True)
            self.dlg.AboutNotepad.close()

            # A non-exact menu name
            path = "help ->About Notepad"
            self.assertRaises(IndexError, self.dlg.menu_select, path, True)

        def test_menu_by_best_match_text(self):
            """Test selecting a Win32 menu item by best match text"""
            path = "help->aboutnotepad"
            self.dlg.menu_select(path, False)
            self.dlg.AboutNotepad.close()

            path = "Help ->about notepad "
            self.dlg.menu_select(path, False)
            self.dlg.AboutNotepad.close()

            # Bad match
            path = "HELP -> About Notepad"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

            path = "help -> ABOUT NOTEPAD"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

            path = "help -> # 2"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

        def test_menu_by_mixed_match(self):
            """Test selecting a menu item by a path with mixed specifiers"""
            path = "#4->aboutnotepad"
            self.dlg.menu_select(path, False)
            self.dlg.AboutNotepad.close()

            # An index and the exact text match
            path = "Help->#1"
            self.dlg.menu_select(path, True)
            self.dlg.AboutNotepad.close()

            # An index and non-exact text match
            path = "#4 -> about notepad "
            self.dlg.menu_select(path, False)
            self.dlg.AboutNotepad.close()

            # Bad specifiers
            path = "#0->#1->1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)
            path = "0->#1->1"
            self.assertRaises(IndexError, self.dlg.menu_select, path)
            path = " -> #1 -> #2"
            self.assertRaises(IndexError, self.dlg.menu_select, path)

    class ToolbarWpfTests(unittest.TestCase):

        """Unit tests for ToolbarWrapper class on WPF demo"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)
            self.dlg = self.app.WPFSampleApplication

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_button_access(self):
            """Test getting access to buttons on Toolbar of WPF demo"""
            # Read a second toolbar with buttons: "button1, button2"
            tb = self.dlg.Toolbar2.wrapper_object()
            self.assertEqual(tb.button_count(), 5)
            self.assertEqual(len(tb.texts()), 5)

            # Test if it's in writable properties
            props = set(tb.get_properties().keys())
            self.assertEqual('button_count' in props, True)

            expect_txt = "button 1"
            self.assertEqual(tb.button(3).window_text(), expect_txt)

            found_txt = tb.button(expect_txt, exact=True).window_text()
            self.assertEqual(found_txt, expect_txt)

            found_txt = tb.button("b 1", exact=False).window_text()
            self.assertEqual(found_txt, expect_txt)

            expect_txt = "button 2"
            found_txt = tb.button(expect_txt, exact=True).window_text()
            self.assertEqual(found_txt, expect_txt)

            expect_txt = ""
            btn = tb.button(expect_txt, exact=True)
            found_txt = btn.window_text()
            self.assertEqual(found_txt, expect_txt)

            # Notice that findbestmatch.MatchError is subclassed from IndexError
            self.assertRaises(IndexError, tb.button, "BaD n_$E ", exact=False)

    class ToolbarNativeTests(unittest.TestCase):

        """Unit tests for ToolbarWrapper class on a native application"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            Timings.defaults()

            self.app = Application(backend='uia')
            self.app.start(os.path.join(mfc_samples_folder, u"RowList.exe"))
            self.dlg = self.app.RowListSampleApplication
            self.ctrl = self.dlg.ToolBar.wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_tooltips(self):
            """Test working with tooltips"""
            self.ctrl.set_focus()
            self.ctrl.move_mouse_input(coords=(10, 10), absolute=False)

            # Find a tooltip by class name
            tt = self.app.window(top_level_only=False,
                                 class_name="tooltips_class32").wait('visible')
            self.assertEqual(isinstance(tt, uia_ctls.TooltipWrapper), True)
            self.assertEqual(tt.window_text(), "Large Icons")

            # Find a tooltip window by control type
            tt = self.app.top_window().children(control_type='ToolTip')[0]
            self.assertEqual(isinstance(tt, uia_ctls.TooltipWrapper), True)
            self.assertEqual(tt.window_text(), "Large Icons")

        def test_button_click(self):
            """Test button click"""
            # Check the "Full Row Details" button
            self.ctrl.check_button("Full Row Details", True)
            lst_ctl = self.dlg.ListBox
            itm = lst_ctl.children()[1]
            self.assertEqual(itm.texts()[0], u'Yellow')

            # Check the second time it shouldn't change
            self.ctrl.check_button("Full Row Details", True)
            self.assertEqual(itm.texts()[0], u'Yellow')

            # Switch to another view
            self.ctrl.check_button("Small Icons", True)
            itm = lst_ctl.children()[1]
            self.assertEqual(itm.texts()[0], u'Red')


    class ToolbarMfcTests(unittest.TestCase):

        """Unit tests for ToolbarWrapper class on MFC demo"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            self.app = Application(backend='uia').start(mfc_app_rebar_test)
            self.dlg = self.app.RebarTest
            self.menu_bar = self.dlg.MenuBar.wrapper_object()
            self.toolbar = self.dlg.StandardToolbar.wrapper_object()
            self.window_edge_point = (self.dlg.rectangle().width() + 50, self.dlg.rectangle().height() + 50)

        def tearDown(self):
            """Close the application after tests"""
            self.menu_bar.move_mouse_input(coords=self.window_edge_point, absolute=False)
            self.app.kill()

        def test_button_access(self):
            """Test getting access to buttons on Toolbar for MFC demo"""
            # Read a first toolbar with buttons: "File, View, Help"
            self.assertEqual(self.menu_bar.button_count(), 4)
            self.assertEqual(self.toolbar.button_count(), 11)

            # Test if it's in writable properties
            props = set(self.menu_bar.get_properties().keys())
            self.assertEqual('button_count' in props, True)
            self.assertEqual("File", self.menu_bar.button(0).window_text())
            self.assertEqual("View", self.menu_bar.button(1).window_text())
            self.assertEqual("Help", self.menu_bar.button(2).window_text())

            found_txt = self.menu_bar.button("File", exact=True).window_text()
            self.assertEqual("File", found_txt)

            found_txt = self.menu_bar.button("File", exact=False).window_text()
            self.assertEqual("File", found_txt)

        def test_texts(self):
            """Test method .texts() for MFC Toolbar"""
            self.assertEqual(self.menu_bar.texts(), [u'File', u'View', u'Help', u'Help'])
            self.assertEqual(self.toolbar.texts(), [u'New', u'Open', u'Save', u'Save',
                u'Cut', u'Copy', u'Paste', u'Paste', u'Print', u'About', u'About'])


    class TreeViewWpfTests(unittest.TestCase):

        """Unit tests for TreeViewWrapper class on WPF demo"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)
            self.dlg = self.app.WPFSampleApplication
            tab_itm = self.dlg.TreeAndListViews.set_focus()
            self.ctrl = tab_itm.children(control_type="Tree")[0]

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_tv_item_count_and_roots(self):
            """Test getting roots and a total number of items in TreeView"""
            # By default the tree view on WPF demo is partially expanded
            # with only 12 visible nodes
            self.assertEqual(self.ctrl.item_count(), 12)

            # Test if it's in writable properties
            props = set(self.ctrl.get_properties().keys())
            self.assertEqual('item_count' in props, True)

            roots = self.ctrl.roots()
            self.assertEqual(len(roots), 1)
            self.assertEqual(roots[0].texts()[0], u'Date Elements')

            sub_items = roots[0].sub_elements()
            self.assertEqual(len(sub_items), 11)
            self.assertEqual(sub_items[0].window_text(), u'Empty Date')
            self.assertEqual(sub_items[-1].window_text(), u'Years')

            expected_str = "Date Elements\n Empty Date\n Week\n  Monday\n  Tuesday\n  Wednsday\n"
            expected_str += "  Thursday\n  Friday\n  Saturday\n  Sunday\n Months\n Years\n"
            self.assertEqual(self.ctrl.print_items(), expected_str)

        def test_tv_item_select(self):
            """Test selecting an item from TreeView"""
            # Find by a path with indexes
            itm = self.ctrl.get_item((0, 2, 3))
            self.assertEqual(itm.is_selected(), False)

            # Select
            itm.select()
            self.assertEqual(itm.is_selected(), True)

            # A second call to Select doesn't remove selection
            itm.select()
            self.assertEqual(itm.is_selected(), True)

            itm = self.ctrl.get_item((0, 3, 2))
            itm.ensure_visible()
            self.assertEqual(itm.is_selected(), False)
            coords = itm.children(control_type='Text')[0].rectangle().mid_point()
            itm.click_input(coords=coords, absolute=True)
            self.assertEqual(itm.is_selected(), True)

        def test_tv_get_item(self):
            """Test getting an item from TreeView"""
            # Find by a path with indexes
            itm = self.ctrl.get_item((0, 2, 3))
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'April')

            # Find by a path with strings
            itm = self.ctrl.get_item('\\Date Elements\\Months\\April', exact=True)
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'April')

            itm = self.ctrl.get_item('\\ Date Elements \\ months \\ april', exact=False)
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'April')

            itm = self.ctrl.get_item('\\Date Elements', exact=False)
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'Date Elements')

            # Try to find the last item in the tree hierarchy
            itm = self.ctrl.get_item('\\Date Elements\\Years\\2018', exact=False)
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'2018')

            itm = self.ctrl.get_item((0, 3, 3))
            self.assertEqual(isinstance(itm, uia_ctls.TreeItemWrapper), True)
            self.assertEqual(itm.window_text(), u'2018')

            # Verify errors handling
            self.assertRaises(uia_defs.NoPatternInterfaceError, itm.is_checked)

            self.assertRaises(RuntimeError,
                              self.ctrl.get_item,
                              'Date Elements\\months',
                              exact=False)

            self.assertRaises(IndexError,
                              self.ctrl.get_item,
                              '\\_X_- \\months',
                              exact=False)

            self.assertRaises(IndexError,
                              self.ctrl.get_item,
                              '\\_X_- \\ months',
                              exact=True)

            self.assertRaises(IndexError,
                              self.ctrl.get_item,
                              '\\Date Elements\\ months \\ aprel',
                              exact=False)

            self.assertRaises(IndexError,
                              self.ctrl.get_item,
                              '\\Date Elements\\ months \\ april\\',
                              exact=False)

            self.assertRaises(IndexError,
                              self.ctrl.get_item,
                              '\\Date Elements\\ months \\ aprel',
                              exact=True)

            self.assertRaises(IndexError, self.ctrl.get_item, (0, 200, 1))

            self.assertRaises(IndexError, self.ctrl.get_item, (130, 2, 1))

        def test_tv_drag_n_drop(self):
            """Test moving an item with mouse over TreeView"""
            # Make sure the both nodes are visible
            self.ctrl.get_item('\\Date Elements\\weeks').collapse()
            itm_from = self.ctrl.get_item('\\Date Elements\\Years')
            itm_to = self.ctrl.get_item('\\Date Elements\\Empty Date')

            itm_from.drag_mouse_input(itm_to)

            # Verify that the item and its sub-items are attached to the new node
            itm = self.ctrl.get_item('\\Date Elements\\Empty Date\\Years')
            self.assertEqual(itm.window_text(), 'Years')
            itm = self.ctrl.get_item((0, 0, 0, 0))
            self.assertEqual(itm.window_text(), '2015')
            itm = self.ctrl.get_item('\\Date Elements\\Empty Date\\Years')
            itm.collapse()

            itm_from = self.ctrl.get_item('\\Date Elements\\Empty Date\\Years')
            itm_to = self.ctrl.get_item(r'\Date Elements\Months')
            self.ctrl.drag_mouse_input(itm_to, itm_from)
            itm = self.ctrl.get_item(r'\Date Elements\Months\Years')
            self.assertEqual(itm.window_text(), 'Years')

            # Error handling: drop on itself
            self.assertRaises(AttributeError,
                              self.ctrl.drag_mouse_input,
                              itm_from, itm_from)

            # Drag-n-drop by manually calculated absolute coordinates
            itm_from = self.ctrl.get_item(r'\Date Elements\Months')
            itm_from.collapse()
            r = itm_from.rectangle()
            coords_from = (int(r.left + (r.width() / 4.0)),
                           int(r.top + (r.height() / 2.0)))

            r = self.ctrl.get_item(r'\Date Elements\Weeks').rectangle()
            coords_to = (int(r.left + (r.width() / 4.0)),
                         int(r.top + (r.height() / 2.0)))

            self.ctrl.drag_mouse_input(coords_to, coords_from)
            itm = self.ctrl.get_item(r'\Date Elements\Weeks\Months')
            self.assertEqual(itm.window_text(), 'Months')

    class WindowWrapperTests(unittest.TestCase):

        """Unit tests for the UIAWrapper class for Window elements"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            test_folder = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))), r"apps/MouseTester")
            self.qt5_app = os.path.join(test_folder, "mousebuttons.exe")

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(self.qt5_app)

            self.dlg = self.app.MouseButtonTester.wrapper_object()
            self.another_app = None

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()
            if self.another_app:
                self.another_app.kill()
                self.another_app = None

        def test_issue_443(self):
            """Test .set_focus() for window that is not keyboard focusable"""
            self.dlg.minimize()
            self.assertEqual(self.dlg.is_minimized(), True)
            self.dlg.set_focus()
            self.assertEqual(self.dlg.is_minimized(), False)
            self.assertEqual(self.dlg.is_normal(), True)

            # run another app instance (in focus now)
            self.another_app = Application(backend="win32").start(self.qt5_app)
            # eliminate clickable point at original app by maximizing second window
            self.another_app.MouseButtonTester.maximize()
            self.another_app.MouseButtonTester.set_focus()
            self.assertEqual(self.another_app.MouseButtonTester.has_focus(), True)

            self.dlg.set_focus()
            # another app instance has lost focus
            self.assertEqual(self.another_app.MouseButtonTester.has_focus(), False)
            # our window has been brought to the focus (clickable point exists)
            self.assertEqual(self.dlg.element_info.element.GetClickablePoint()[-1], 1)


if __name__ == "__main__":
    if UIA_support:
        unittest.main()
