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

if UIA_support:

    def _set_timings():
        """Setup timings for UIA related tests"""
        Timings.Defaults()
        Timings.window_find_timeout = 20

    class UIAWrapperTests(unittest.TestCase):

        """Unit tests for the UIAWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

        def test_issue_296(self):
            """Test handling of disappered descendants"""
            wrp = self.dlg.wrapper_object()
            orig = wrp.element_info._element.FindAll
            wrp.element_info._element.FindAll = mock.Mock(side_effect=ValueError("Mocked value error"),
                                                          return_value=[])  # empty list
            self.assertEqual([], wrp.descendants())
            wrp.element_info._element.FindAll = mock.Mock(side_effect=comtypes.COMError("Mocked COM error", 0, 0),
                                                          return_value=[])  # empty list
            self.assertEqual([], wrp.descendants())
            wrp.element_info._element = orig  # restore the original method

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
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.class_name(), "Button")

        def test_window_text(self):
            """Test getting the window Text of the dialog"""
            label = self.dlg.TestLabel.wrapper_object()
            self.assertEqual(label.window_text(), u"TestLabel")

        def test_control_id(self):
            """Test getting control ID"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.control_id(), None)

        def test_is_visible(self):
            """Test is_visible method of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.is_visible(), True)

        def test_is_enabled(self):
            """Test is_enabled method of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.is_enabled(), True)

        def test_process_id(self):
            """Test process_id method of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.process_id(), self.dlg.process_id())
            self.assertNotEqual(button.process_id(), 0)

        def test_is_dialog(self):
            """Test is_dialog method of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.is_dialog(), False)

        def test_parent(self):
            """Test getting a parent of a control"""
            button = self.dlg.Alpha.wrapper_object()
            self.assertEqual(button.parent(), self.dlg.wrapper_object())

        def test_top_level_parent(self):
            """Test getting a top-level parent of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.top_level_parent(), self.dlg.wrapper_object())

        def test_texts(self):
            """Test getting texts of a control"""
            self.assertEqual(self.dlg.texts(), ['WPF Sample Application'])

        def test_children(self):
            """Test getting children of a control"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(len(button.children()), 1)
            self.assertEqual(button.children()[0].class_name(), "TextBlock")

        def test_is_child(self):
            """Test is_child method of a control"""
            button = self.dlg.Alpha.wrapper_object()
            self.assertEqual(button.is_child(self.dlg.wrapper_object()), True)

        def test_equals(self):
            """Test controls comparisons"""
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertNotEqual(button, self.dlg.wrapper_object())
            self.assertEqual(button, button.element_info)
            self.assertEqual(button, button)

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
            button = self.dlg.window(class_name="Button",
                                     title="OK").wrapper_object()
            self.assertEqual(button.is_keyboard_focusable(), True)
            self.assertEqual(edit.is_keyboard_focusable(), True)
            self.assertEqual(label.is_keyboard_focusable(), False)

        def test_has_keyboard_focus(self):
            """Test verifying a keyboard focus on a control"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
            edit.set_focus()
            self.assertEqual(edit.has_keyboard_focus(), True)

        def test_set_focus(self):
            """Test setting a keyboard focus on a control"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
            edit.set_focus()
            self.assertEqual(edit.has_keyboard_focus(), True)

        def test_type_keys(self):
            """Test sending key types to a control"""
            edit = self.dlg.TestLabelEdit.wrapper_object()
            edit.type_keys("testTypeKeys")
            self.assertEqual(edit.window_text(), "testTypeKeys")

        def test_no_pattern_interface_error(self):
            """Test a query interface exception handling"""
            button = self.dlg.window(class_name="Button",
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
            self.assertEqual(wrp.iface_window.CurrentWindowVisualState,
                             uia_defs.window_visual_state_minimized)
            wrp.maximize()
            self.dlg.wait('active')
            self.assertEqual(wrp.iface_window.CurrentWindowVisualState,
                             uia_defs.window_visual_state_maximized)
            wrp.minimize()
            self.dlg.wait_not('active')
            wrp.restore()
            self.dlg.wait('active')
            self.assertEqual(wrp.iface_window.CurrentWindowVisualState,
                             uia_defs.window_visual_state_normal)

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
            expected_properties = {'Value' : '',
                                   'DefaultAction': 'Press',
                                   'Description': '',
                                   'Name': 'OK',
                                   'Help': '',
                                   'ChildId': 0,
                                   'KeyboardShortcut': '',
                                   'State': 1048576,
                                   'Role': 43}
            button_wrp = self.dlg.window(class_name="Button",
                                       title="OK").wrapper_object()

            actual_properties = button_wrp.legacy_properties()

            self.assertEqual(actual_properties, expected_properties)

    class UIAWrapperMouseTests(unittest.TestCase):

        """Unit tests for mouse actions of the UIAWrapper class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            _set_timings()

            self.app = Application(backend='uia')
            self.app = self.app.start(wpf_app_1)

            dlg = self.app.WPFSampleApplication
            self.button = dlg.window(class_name="Button",
                                     title="OK").wrapper_object()

            self.label = dlg.window(class_name="Text", title="TestLabel").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

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
            self.app.kill_()

        def test_pretty_print(self):
            """Test __str__ method for UIA based controls"""
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
            assert_regex(wrp.__str__(), "^uia_controls\.TabControlWrapper - 'General', TabControl$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.TabControlWrapper - 'General', TabControl, [0-9-]+>$")

            wrp = self.dlg.MenuBar.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.MenuWrapper - 'System', Menu$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.MenuWrapper - 'System', Menu, [0-9-]+>$")

            wrp = self.dlg.Slider.wrapper_object()
            assert_regex(wrp.__str__(), "^uia_controls\.SliderWrapper - '', Slider$")
            assert_regex(wrp.__repr__(), "^<uia_controls\.SliderWrapper - '', Slider, [0-9-]+>$")

            wrp = self.dlg.wrapper_object()
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - 'WPF Sample Application', Dialog$")
            assert_regex(wrp.__repr__(), "^<uiawrapper\.UIAWrapper - 'WPF Sample Application', Dialog, [0-9-]+>$")

            # ElementInfo.__str__
            assert_regex(wrp.element_info.__str__(),
                         "^uia_element_info.UIAElementInfo - 'WPF Sample Application', Window$")
            assert_regex(wrp.element_info.__repr__(),
                         "^<uia_element_info.UIAElementInfo - 'WPF Sample Application', Window, [0-9-]+>$")

            # mock a failure in texts() method
            orig = wrp.texts
            wrp.texts = mock.Mock(return_value=[])  # empty texts
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - '', Dialog$")
            assert_regex(wrp.__repr__(), "^<uiawrapper\.UIAWrapper - '', Dialog, [0-9-]+>$")
            wrp.texts.return_value = [u'\xd1\xc1\\\xa1\xb1\ua000']  # unicode string
            assert_regex(wrp.__str__(), "^uiawrapper\.UIAWrapper - '.+', Dialog$")
            wrp.texts = orig  # restore the original method

            # mock a failure in element_info.name property (it's based on _get_name())
            orig = wrp.element_info._get_name
            wrp.element_info._get_name = mock.Mock(return_value=None)
            assert_regex(wrp.element_info.__str__(), "^uia_element_info\.UIAElementInfo - 'None', Window$")
            assert_regex(wrp.element_info.__repr__(), "^<uia_element_info\.UIAElementInfo - 'None', Window, [0-9-]+>$")
            wrp.element_info._get_name = orig

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
            label = self.dlg.window(class_name="Text",
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

            # Mock a combobox without "ExpandCollapse" pattern
            combo_box.expand = mock.Mock(side_effect=uia_defs.NoPatternInterfaceError())  # empty texts
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
            self.ctrl = dlg.window(class_name="TabControl").wrapper_object()
            self.texts = [u"General", u"Tree and List Views", u"ListBox and Grid"]

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

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

            self.edit = self.dlg.window(class_name="TextBox").wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

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
            self.app.kill_()

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
            self.app.kill_()

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
            """Test getting a Header control of the ListView control"""
            # ListView
            self.listview_tab.set_focus()
            listview = self.listview_tab.children(class_name=u"ListView")[0]
            self.assertTrue(isinstance(listview.get_header_control(), uia_ctls.HeaderWrapper))

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
            self.app.kill_()

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
            self.app.kill_()

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
            Timings.Defaults()

            # start the application
            self.app = Application(backend='uia')
            self.app = self.app.start("notepad.exe")
            self.dlg = self.app.UntitledNotepad
            ActionLogger().log("MenuWrapperNotepadTests::setUp, wait till Notepad dialog is ready")
            self.dlg.wait("ready")

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

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
            self.app.kill_()

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
            Timings.Defaults()

            self.app = Application(backend='uia')
            self.app.start(os.path.join(mfc_samples_folder, u"RowList.exe"))
            self.dlg = self.app.RowListSampleApplication
            self.ctrl = self.dlg.ToolBar.wrapper_object()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

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
            self.app.kill_()

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


if __name__ == "__main__":
    if UIA_support:
        unittest.main()
