"""Tests for WPFWrapper"""
from __future__ import print_function
from __future__ import unicode_literals

import time
import os
import sys
import collections
import unittest
import mock

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.base_application import WindowSpecification  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.timings import Timings, wait_until  # noqa: E402
from pywinauto.actionlogger import ActionLogger  # noqa: E402
from pywinauto import mouse  # noqa: E402

import pywinauto.controls.wpf_controls as wpf_ctls
from pywinauto.controls.wpfwrapper import WPFWrapper
from pywinauto.windows.injected.api import InjectedTargetError
from pywinauto.windows.injected.channel import BrokenPipeError

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
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        self.dlg = self.app.WPFSampleApplication

    def test_get_active_wpf(self):
        focused_element = self.dlg.get_active()
        self.assertTrue(type(focused_element) is WPFWrapper or issubclass(type(focused_element), WPFWrapper))

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_issue_278(self):
        """Test that statement menu = app.MainWindow.Menu works for 'wpf' backend"""
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
        wins = self.app.windows(class_name='MainWindow', name=caption)

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
        # TODO
        # self.assertEqual(label.can_be_label, True)

    def test_control_id(self):
        """Test getting control ID"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertNotEqual(button.control_id(), None)

    def test_automation_id(self):
        """Test getting automation ID"""
        alpha_toolbar = self.dlg.by(name="Alpha", control_type="ToolBar")
        button = alpha_toolbar.by(control_type="Button",
                                  auto_id="toolbar_button1").find()
        self.assertEqual(button.automation_id(), "toolbar_button1")

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

    def test_parent(self):
        """Test getting a parent of a control"""
        toolbar = self.dlg.Alpha.find()
        self.assertEqual(toolbar.parent(), self.dlg.ToolBarTray.find())

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
        tab_ctrl = self.dlg.by(class_name="TabControl").find()
        self.assertEqual(len(tab_ctrl.children()), 3)
        self.assertEqual(tab_ctrl.children()[0].class_name(), "TabItem")

    def test_children_generator(self):
        """Test iterating children of a control"""
        tab_ctrl = self.dlg.by(class_name="TabControl").find()
        children = [child for child in tab_ctrl.iter_children()]
        self.assertEqual(len(children), 3)
        self.assertEqual(children[0].class_name(), "TabItem")

    def test_descendants(self):
        """Test iterating descendants of a control"""
        toolbar = self.dlg.by(class_name="RichTextBox").find()
        descendants = toolbar.descendants()
        self.assertEqual(len(descendants), 11)

    def test_descendants_generator(self):
        toolbar = self.dlg.by(name="Alpha", control_type="ToolBar").find()
        descendants = [desc for desc in toolbar.iter_descendants()]
        self.assertSequenceEqual(toolbar.descendants(), descendants)

    def test_is_child(self):
        """Test is_child method of a control"""
        toolbar = self.dlg.Alpha.find()
        self.assertEqual(toolbar.is_child(self.dlg.ToolBarTray.find()), True)

    def test_equals(self):
        """Test controls comparisons"""
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertNotEqual(button, self.dlg.find())
        self.assertEqual(button, button.element_info)
        self.assertEqual(button, button)

    def test_is_keyboard_focusable(self):
        """Test is_keyboard focusable method of several controls"""
        edit = self.dlg.by(auto_id='edit1').find()
        label = self.dlg.TestLabel.find()
        button = self.dlg.by(class_name="Button",
                             name="OK").find()
        self.assertEqual(button.is_keyboard_focusable(), True)
        self.assertEqual(edit.is_keyboard_focusable(), True)
        self.assertEqual(label.is_keyboard_focusable(), False)

    def test_set_focus(self):
        """Test setting a keyboard focus on a control"""
        edit = self.dlg.by(auto_id='edit1').find()
        edit.set_focus()
        self.assertEqual(edit.has_keyboard_focus(), True)

    def test_type_keys(self):
        """Test sending key types to a control"""
        edit = self.dlg.by(auto_id='edit1').find()
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

    def test_capture_as_image_multi_monitor(self):
        with mock.patch('win32api.EnumDisplayMonitors') as mon_device:
            mon_device.return_value = (1, 2)
            rect = self.dlg.rectangle()
            expected = (rect.width(), rect.height())
            result = self.dlg.capture_as_image().size
            self.assertEqual(expected, result)


class WPFWrapperMouseTests(unittest.TestCase):

    """Unit tests for mouse actions of the WPFWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        dlg = self.app.WPFSampleApplication
        self.button = dlg.by(class_name="Button",
                             name="OK").find()

        self.label = dlg.by(class_name="Label", name="TestLabel").find()
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


class WindowWrapperTests(unittest.TestCase):

    """Unit tests for the WPFWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()
        mouse.move((-500, 500))  # remove the mouse from the screen to avoid side effects

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        self.dlg = self.app.WPFSampleApplication

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_close(self):
        """Test close method of a control"""
        wrp = self.dlg.find()
        wrp.close()

        try:
            # process can be in the termination state at this moment
            self.assertEqual(self.dlg.exists(), False)
        except (InjectedTargetError, BrokenPipeError):
            pass

    def test_move_window(self):
        """Test move_window without any parameters"""

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


class ButtonWrapperTests(unittest.TestCase):

    """Unit tests for the WPF controls inherited from ButtonBase"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        self.dlg = self.app.WPFSampleApplication

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_check_box(self):
        """Test 'toggle' and 'toggle_state' for the check box control"""
        # Get a current state of the check box control
        check_box = self.dlg.CheckBox.find()
        cur_state = check_box.get_toggle_state()
        self.assertEqual(cur_state, wpf_ctls.ButtonWrapper.INDETERMINATE)

        # Toggle the next state
        cur_state = check_box.toggle().get_toggle_state()

        # Get a new state of the check box control
        self.assertEqual(cur_state, wpf_ctls.ButtonWrapper.UNCHECKED)

        cur_state = check_box.select().get_toggle_state()
        self.assertEqual(cur_state, wpf_ctls.ButtonWrapper.CHECKED)

    def test_toggle_button(self):
        """Test 'toggle' and 'toggle_state' for the toggle button control"""
        # Get a current state of the check box control
        button = self.dlg.ToggleMe.find()
        cur_state = button.get_toggle_state()
        self.assertEqual(cur_state, button.CHECKED)

        # Toggle the next state
        cur_state = button.toggle().get_toggle_state()

        # Get a new state of the check box control
        self.assertEqual(cur_state, button.UNCHECKED)

        # Toggle the next state
        cur_state = button.toggle().get_toggle_state()
        self.assertEqual(cur_state, button.CHECKED)

    def test_button_click(self):
        """Test the click method for the Button control"""
        label = self.dlg.by(class_name="Label",
                            name="TestLabel").find()
        self.dlg.Apply.click()
        self.assertEqual(label.window_text(), "ApplyClick")

    def test_radio_button(self):
        """Test 'select' and 'is_selected' for the radio button control"""
        yes = self.dlg.Yes.find()
        cur_state = yes.is_selected()
        self.assertEqual(cur_state, False)

        cur_state = yes.select().is_selected()
        self.assertEqual(cur_state, True)

        no = self.dlg.No.find()
        cur_state = no.select().is_selected()
        self.assertEqual(cur_state, True)

class ComboBoxTests(unittest.TestCase):

    """Unit tests for the ComboBoxWrapper class with WPF app"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)

        self.dlg = self.app.WPFSampleApplication
        self.combo = self.dlg.by(control_type="ComboBox").find()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_expand_collapse(self):
        """Test methods .expand() and .collapse() for WPF combo box"""
        self.dlg.set_focus()

        combo = self.combo
        combo_name = self.combo.element_info.name

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
        self.assertFalse(combo.is_expanded(),
            msg='{} combo box has not been collapsed!'.format(combo_name))

        # collapse already collapsed should keep collapsed state
        self.assertEqual(combo.collapse(), combo,
            msg='Method .collapse() for {} combo box must return self, always!'.format(combo_name))
        self.assertFalse(combo.is_expanded(),
            msg='{} combo box does NOT keep collapsed state!'.format(combo_name))

    def test_texts(self):
        """Test method .texts() for WPF combo box"""
        self.dlg.set_focus()
        texts = [u'Combo Item 1', u'Combo Item 2']

        self.assertEqual(self.combo.texts(), texts)
        self.assertEqual(self.combo.expand().texts(), texts)
        self.assertTrue(self.combo.is_expanded())

    def test_select(self):
        """Test method .select() for WPF combo box"""
        self.dlg.set_focus()

        self.assertEqual(self.combo.selected_index(), -1) # nothing selected
        self.combo.select(u'Combo Item 2')
        self.assertEqual(self.combo.selected_text(), u'Combo Item 2')
        self.assertEqual(self.combo.selected_index(), 1)
        self.combo.select(0)
        self.assertEqual(self.combo.selected_text(), u'Combo Item 1')
        self.assertEqual(self.combo.selected_index(), 0)

    def test_item_count(self):
        """Test method .item_count() for WPF combo box"""
        self.dlg.set_focus()
        self.assertEqual(self.combo.item_count(), 2)


class EditWrapperTests(unittest.TestCase):

    """Unit tests for the EditWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        app = Application(backend='wpf')
        app = app.start(wpf_app_1)

        self.app = app
        self.dlg = app.WPFSampleApplication

        self.edit = self.dlg.by(class_name="TextBox").find()

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_set_window_text(self):
        """Test setting text value of control (the text in textbox itself)"""
        text_to_set = "This test"

        self.edit.set_window_text(text_to_set)
        self.assertEqual(self.edit.text_block(), text_to_set)

        self.edit.set_window_text(" is done", True)
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

    def test_get_line(self):
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


class TabControlWrapperTests(unittest.TestCase):

    """Unit tests for the TabControlWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        app = Application(backend='wpf')
        app = app.start(wpf_app_1)
        dlg = app.WPFSampleApplication

        self.app = app
        self.ctrl = dlg.by(class_name="TabControl").find()
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


class SliderWrapperTests(unittest.TestCase):

    """Unit tests for the SliderWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        app = Application(backend='wpf')
        app = app.start(wpf_app_1)

        self.app = app
        self.dlg = app.WPFSampleApplication

        self.slider = self.dlg.by(class_name="Slider").find()

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


class ToolbarWpfTests(unittest.TestCase):

    """Unit tests for ToolbarWrapper class on WPF demo"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)
        self.dlg = self.app.WPFSampleApplication

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_button_access_wpf(self):
        """Test getting access to buttons on Toolbar of WPF demo"""
        # Read a second toolbar with buttons: "button1, button2"
        tb = self.dlg.Toolbar2.find()
        self.assertEqual(tb.button_count(), 2)
        self.assertEqual(len(tb.texts()), 2)

        # Test if it's in writable properties
        props = set(tb.get_properties().keys())
        self.assertEqual('button_count' in props, True)

        expect_txt = "button 1"
        self.assertEqual(tb.button(0).window_text(), expect_txt)

        found_txt = tb.button(expect_txt, exact=True).window_text()
        self.assertEqual(found_txt, expect_txt)

        found_txt = tb.button("b 1", exact=False).window_text()
        self.assertEqual(found_txt, expect_txt)

        expect_txt = "button 2"
        found_txt = tb.button(expect_txt, exact=True).window_text()
        self.assertEqual(found_txt, expect_txt)

        # Notice that findbestmatch.MatchError is subclassed from IndexError
        self.assertRaises(IndexError, tb.button, "BaD n_$E ", exact=False)

    def test_overflow_area_status(self):
        """Check if overflow area visible (note: OverflowButton is inactive in the sample"""
        tb = self.dlg.Toolbar2.find()
        self.assertTrue(tb.is_expanded())
        self.assertFalse(tb.is_collapsed())


class MenuWrapperWpfTests(unittest.TestCase):

    """Unit tests for the MenuWrapper class on WPF demo"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)
        self.dlg = self.app.WPFSampleApplication

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_menu_by_index(self):
        """Test selecting a WPF menu item by index"""
        path = "#0->#1->#1"  # "File->Close->Later"
        self.dlg.menu_select(path)
        label = self.dlg.MenuLaterClickStatic.find()
        self.assertEqual(label.window_text(), u"MenuLaterClick")

        # Non-existing paths
        path = "#5->#1"
        self.assertRaises(IndexError, self.dlg.menu_select, path)
        path = "#0->#1->#1->#2->#3"
        self.assertRaises(IndexError, self.dlg.menu_select, path)

    def test_menu_by_exact_text(self):
        """Test selecting a WPF menu item by exact text match"""
        path = "_File->_Close->_Later"
        self.dlg.menu_select(path, True)
        label = self.dlg.MenuLaterClickStatic.find()
        self.assertEqual(label.window_text(), u"MenuLaterClick")

        # A non-exact menu name
        path = "File->About"
        self.assertRaises(IndexError, self.dlg.menu_select, path, True)

    def test_menu_by_best_match_text(self):
        """Test selecting a WPF menu item by best match text"""
        path = "file-> close -> later"
        self.dlg.menu_select(path, False)
        label = self.dlg.MenuLaterClickStatic.find()
        self.assertEqual(label.window_text(), u"MenuLaterClick")

    def test_menu_by_mixed_match(self):
        """Test selecting a WPF menu item by a path with mixed specifiers"""
        path = "file-> #1 -> later"
        self.dlg.menu_select(path, False)
        label = self.dlg.MenuLaterClickStatic.find()
        self.assertEqual(label.window_text(), u"MenuLaterClick")

        # Bad specifiers
        path = "file-> 1 -> later"
        self.assertRaises(IndexError, self.dlg.menu_select, path)
        path = "#0->#1->1"
        self.assertRaises(IndexError, self.dlg.menu_select, path)
        path = "0->#1->1"
        self.assertRaises(IndexError, self.dlg.menu_select, path)


class TreeViewWpfTests(unittest.TestCase):

    """Unit tests for TreeViewWrapper class on WPF demo"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        self.app = Application(backend='wpf')
        self.app = self.app.start(wpf_app_1)
        self.dlg = self.app.WPFSampleApplication
        tab_itm = self.dlg.TreeAndListViews.set_focus()
        self.ctrl = tab_itm.descendants(control_type="Tree")[0]

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_tv_item_count_and_roots(self):
        """Test getting roots and a total number of items in TreeView"""
        self.assertEqual(self.ctrl.item_count(), 27)

        # Test if it's in writable properties
        props = set(self.ctrl.get_properties().keys())
        self.assertEqual('item_count' in props, True)

        roots = self.ctrl.roots()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].texts()[0], u'Date Elements')

        sub_items = roots[0].sub_elements(depth=1)
        self.assertEqual(len(sub_items), 4)
        self.assertEqual(sub_items[0].window_text(), u'Empty Date')
        self.assertEqual(sub_items[-1].window_text(), u'Years')

        expected_str = "Date Elements\n Empty Date\n Week\n  Monday\n  Tuesday\n  Wednsday\n"
        expected_str += "  Thursday\n  Friday\n  Saturday\n  Sunday\n "
        expected_str += "Months\n  January\n  February\n  March\n  April\n  June\n  July\n  August\n  Semptember\n  "
        expected_str += "October\n  November\n  December\n Years\n  2015\n  2016\n  2017\n  2018\n"
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
        # coords = itm.children(control_type='Text')[0].rectangle().mid_point()
        # itm.click_input(coords=coords, absolute=True)
        # self.assertEqual(itm.is_selected(), True)

    def test_tv_get_item(self):
        """Test getting an item from TreeView"""
        # Find by a path with indexes
        itm = self.ctrl.get_item((0, 2, 3))
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'April')

        # Find by a path with strings
        itm = self.ctrl.get_item('\\Date Elements\\Months\\April', exact=True)
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'April')

        itm = self.ctrl.get_item('\\ Date Elements \\ months \\ april', exact=False)
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'April')

        itm = self.ctrl.get_item('\\Date Elements', exact=False)
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'Date Elements')

        # Try to find the last item in the tree hierarchy
        itm = self.ctrl.get_item('\\Date Elements\\Years\\2018', exact=False)
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'2018')

        itm = self.ctrl.get_item((0, 3, 3))
        self.assertEqual(isinstance(itm, wpf_ctls.TreeItemWrapper), True)
        self.assertEqual(itm.window_text(), u'2018')

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


class ListViewWrapperTests(unittest.TestCase):

    """Unit tests for the ListViewWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        app = Application(backend='wpf')
        app = app.start(wpf_app_1)
        dlg = app.WPFSampleApplication

        self.app = app

        self.listbox_datagrid_tab = dlg.ListBox_and_Grid

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

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_item_count(self):
        """Test the items count in the ListView controls"""
        # ListBox
        self.listbox_datagrid_tab.set_focus()
        listbox = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        self.assertEqual(listbox.item_count(), len(self.listbox_texts))

    def test_cells(self):
        """Test getting a cells of the ListView controls"""
        # ListBox
        self.listbox_datagrid_tab.set_focus()
        listbox = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        cells = listbox.cells()
        self.assertEqual(cells[listbox.item_count() - 1].window_text(), "TextItem 8")
        self.assertEqual(cells[3].window_text(), "CheckItem")

    def test_get_item(self):
        """Test getting an item of ListView controls"""
        # ListBox
        self.listbox_datagrid_tab.set_focus()
        listbox = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        item = listbox.get_item(u"TextItem 2")
        self.assertEqual(item.texts(), self.listbox_texts[1])

        item = listbox.get_item(3)
        self.assertEqual(item.texts(), self.listbox_texts[3])

        item = listbox.get_item(u"TextItem 8")
        self.assertEqual(item.texts(), self.listbox_texts[9])

    def test_get_items(self):
        """Test getting all items of ListView controls"""
        # ListBox
        self.listbox_datagrid_tab.set_focus()
        listbox = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        content = [item.texts() for item in listbox.get_items()]
        self.assertEqual(content, self.listbox_texts)

    def test_texts(self):
        """Test getting all items of ListView controls"""
        # ListBox
        self.listbox_datagrid_tab.set_focus()
        listbox = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        self.assertEqual(listbox.texts(), self.listbox_texts)

    def test_select_and_get_item(self):
        """Test selecting an item of the ListView control"""
        self.listbox_datagrid_tab.set_focus()
        self.ctrl = self.listbox_datagrid_tab.descendants(class_name=u"ListBox")[0]
        self.assertEqual(self.ctrl.texts(), self.listbox_texts)
        # Verify get_selected_count
        self.assertEqual(self.ctrl.get_selected_count(), 0)

        # Select by an index
        row = 1
        i = self.ctrl.get_item(row)
        self.assertEqual(i.is_selected(), False)
        i.select()
        self.assertEqual(i.is_selected(), True)
        cnt = self.ctrl.get_selected_count()
        self.assertEqual(cnt, 1)
        rect = self.ctrl.get_item_rect(row)
        self.assertEqual(rect, i.rectangle())

        # Select by text
        row = 'TextItem 6'
        i = self.ctrl.get_item(row)
        i.select()
        self.assertEqual(i.is_selected(), True)
        i = self.ctrl.get_item(7)  # re-get the item by a row index
        self.assertEqual(i.is_selected(), True)

        row = None
        self.assertRaises(TypeError, self.ctrl.get_item, row)


class GridListViewWrapperTests(unittest.TestCase):

    """Unit tests for the DataGridWrapper class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        _set_timings()

        # start the application
        app = Application(backend='wpf')
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

        self.datagrid_texts = [
            [u"0", u"A0", u"B0", u"C0", u"D0", u"E0", u"", ],
            [u"1", u"A1", u"B1", u"C1", u"D1", u"E1", u"", ],
            [u"2", u"A2", u"B2", u"C2", u"D2", u"E2", u"", ],
            [u"3", u"A3", u"B3", u"C3", u"D3", u"E3", u"", ],
        ]

    def tearDown(self):
        """Close the application after tests"""
        self.app.kill()

    def test_item_count(self):
        """Test the items count in grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        self.assertEqual(listview.item_count(), len(self.listview_texts))

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        self.assertEqual(datagrid.item_count(), len(self.datagrid_texts))

    def test_column_count(self):
        """Test the columns count in grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        self.assertEqual(listview.column_count(), len(self.listview_texts[0]))

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        self.assertEqual(datagrid.column_count(), len(self.datagrid_texts[0]) - 1)

    def test_get_header_control(self):
        """Test getting a Header control and Header Item control of grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        hdr_itm = listview.get_header_controls()[1]
        # HeaderItem of ListView
        self.assertTrue(isinstance(hdr_itm, wpf_ctls.HeaderItemWrapper))
        self.assertEquals('Name', hdr_itm.element_info.name)

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        grid_hdr_item = datagrid.get_header_controls()[2]
        self.assertEquals('B', grid_hdr_item.element_info.name)
        self.assertTrue(isinstance(grid_hdr_item, wpf_ctls.HeaderItemWrapper))

    def test_get_column(self):
        """Test get_column() method for grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        listview_col = listview.get_column(1)
        self.assertEqual(listview_col.texts()[0], u"Name")

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        datagrid_col = datagrid.get_column(2)
        self.assertEqual(datagrid_col.texts()[0], u"B")

        self.assertRaises(IndexError, datagrid.get_column, 10)

    def test_cell(self):
        """Test getting a cell of grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        cell = listview.cell(3, 2)
        self.assertEqual(cell.window_text(), self.listview_texts[3][2])

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        cell = datagrid.cell(2, 0)
        self.assertEqual(cell.window_text(), self.datagrid_texts[2][0])

        self.assertRaises(TypeError, datagrid.cell, 1.5, 1)

        self.assertRaises(IndexError, datagrid.cell, 10, 10)

    def test_cells(self):
        """Test getting a cells of grid controls"""
        def compare_cells(cells, control):
            for i in range(0, control.item_count()):
                for j in range(0, control.column_count()):
                    self.assertEqual(cells[i][j], control.cell(i, j))

        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        compare_cells(listview.cells(), listview)

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        compare_cells(datagrid.cells(), datagrid)

    def test_get_item(self):
        """Test getting an item of grid controls"""
        # ListView
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        item = listview.get_item(u"Reddish")
        self.assertEqual(item.texts(), self.listview_texts[2])

        self.assertRaises(ValueError, listview.get_item, u"Apple")

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        item = datagrid.get_item(u"B2")
        self.assertEqual(item.texts(), self.datagrid_texts[2])

        item = datagrid.get_item(3)
        self.assertEqual(item.texts(), self.datagrid_texts[3])

        self.assertRaises(TypeError, datagrid.get_item, 12.3)

    def test_get_items(self):
        """Test getting all items of grid controls"""
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        content = [item.texts() for item in listview.get_items()]
        self.assertEqual(content, self.listview_texts)

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        content = [item.texts() for item in datagrid.get_items()]
        self.assertEqual(content, self.datagrid_texts)

    def test_texts(self):
        """Test getting all items of grid controls"""
        self.listview_tab.set_focus()
        listview = self.listview_tab.descendants(class_name=u"ListView")[0]
        self.assertEqual(listview.texts(), self.listview_texts)

        # DataGrid
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        self.assertEqual(datagrid.texts(), self.datagrid_texts)

    def test_select_and_get_item_listview(self):
        """Test selecting an item of the ListView control"""
        self.listview_tab.set_focus()
        self.ctrl = self.listview_tab.descendants(class_name=u"ListView")[0]
        # Verify get_selected_count
        self.assertEqual(self.ctrl.get_selected_count(), 0)

        # Select by an index
        row = 1
        i = self.ctrl.get_item(row)
        self.assertEqual(i.is_selected(), False)
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

    def test_select_and_get_item_datagrid(self):
        """Test selecting an item of the DataGrid control"""
        self.listbox_datagrid_tab.set_focus()
        datagrid = self.listbox_datagrid_tab.descendants(class_name=u"DataGrid")[0]
        # Verify get_selected_count
        self.assertEqual(datagrid.get_selected_count(), 0)

        # Select by an index
        row = 1
        i = datagrid.get_item(row)
        self.assertEqual(i.is_selected(), False)
        i.select()
        self.assertEqual(i.is_selected(), True)
        cnt = datagrid.get_selected_count()
        self.assertEqual(cnt, 1)
        rect = datagrid.get_item_rect(row)
        self.assertEqual(rect, i.rectangle())

        # Select by text
        row = 'A3'
        i = datagrid.get_item(row)
        i.select()
        self.assertEqual(i.is_selected(), True)
        row = 'B0'
        i = datagrid.get_item(row)
        i.select()
        i = datagrid.get_item(3)  # re-get the item by a row index
        self.assertEqual(i.is_selected(), True)

        row = None
        self.assertRaises(TypeError, datagrid.get_item, row)


if __name__ == "__main__":
    unittest.main()
