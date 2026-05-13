# -*- coding: utf-8 -*-
"""Linux wrapper tests for the Qt5 backend."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest
from contextlib import redirect_stdout
from io import StringIO


if sys.platform == "win32":
    raise unittest.SkipTest("Linux Qt tests require Linux")

sys.path.append(".")
from pywinauto import Application  # noqa: E402
from pywinauto.base_application import WindowSpecification  # noqa: E402
from pywinauto.controls.qt5_controls import (  # noqa: E402
    ButtonWrapper, ComboBoxWrapper, EditWrapper, ListViewWrapper,
    SliderWrapper, TabControlWrapper, TableWrapper, TreeViewWrapper,
    WindowWrapper,
)
from pywinauto.controls.qt5wrapper import Qt5Wrapper  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from injectlib.api import InjectedBaseError  # noqa: E402


qt_samples_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "apps", "Qt5_samples_linux"))
qt_styles_app = os.path.join(qt_samples_folder, "styles")
qt_interview_app = os.path.join(qt_samples_folder, "interview")


def _set_timings():
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt5StylesWrapperLinuxTests(unittest.TestCase):
    """Wrapper tests for the Qt5 styles example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt5").start(qt_styles_app)
        time.sleep(2)
        self.dlg = self.app.window()
        self.root = self.dlg.find(timeout=15)

    def tearDown(self):
        self.app.kill()

    def test_basic_wrapper_behavior(self):
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertTrue(isinstance(self.dlg.ComboBox, WindowSpecification))
        self.assertEqual(self.root.class_name(), "WidgetGallery")
        self.assertEqual(self.root.window_text(), "Styles")
        self.assertIsNone(self.root.handle)
        self.assertEqual(self.root.process_id(), self.app.process)
        self.assertTrue(self.root.is_dialog())
        self.assertTrue(self.root.is_visible())
        self.assertTrue(self.root.is_enabled())
        self.assertEqual(self.root.children_texts()[:2], ["&Style:", "NorwegianWood"])

    def test_window_specification_binding(self):
        combo_spec = self.dlg.ComboBox
        self.assertTrue(isinstance(combo_spec, WindowSpecification))
        self.assertTrue(combo_spec.app, self.app)

    def test_find_controls_by_class_name_and_title(self):
        combo = self.dlg.by(class_name="QComboBox", name="NorwegianWood").find(timeout=10)
        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertEqual(combo.window_text(), "NorwegianWood")

        group = self.dlg.by(class_name="QGroupBox", name="Group 1").find(timeout=10)
        self.assertEqual(group.class_name(), "QGroupBox")
        self.assertEqual(group.window_text(), "Group 1")

    def test_parent_and_children(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)

        self.assertIsNone(self.root.parent())
        self.assertEqual(combo.top_level_parent(), self.root)
        self.assertIn(combo, self.root.children())
        self.assertEqual(
            self.root.children_texts()[:4],
            ["&Style:", "NorwegianWood", "&Use style's standard palette", "&Disable widgets"],
        )

    def test_texts_and_descendants(self):
        self.assertEqual(self.root.texts(), ["Styles"])

        radio_buttons = self.root.descendants(control_type="RadioButton")
        for button in radio_buttons:
            self.assertTrue(isinstance(button, ButtonWrapper))
        self.assertEqual(
            [button.window_text() for button in radio_buttons],
            ["Radio button 1", "Radio button 2", "Radio button 3"],
        )
        self.assertSequenceEqual(
            self.root.descendants(depth=2),
            [item for item in self.root.iter_descendants(depth=2)],
        )

    def test_native_properties(self):
        checkbox = self.dlg.by(name="&Disable widgets").find(timeout=10)
        self.assertTrue(isinstance(checkbox, ButtonWrapper))
        self.assertEqual(checkbox.get_native_property("checked"), False)

        checkbox.set_native_property("checked", True)
        self.assertEqual(checkbox.get_native_property("checked"), True)

    def test_edit_wrapper(self):
        edit = self.dlg.by(control_type="Edit", class_name="QLineEdit", name="s3cRe7").find(timeout=10)
        self.assertTrue(isinstance(edit, EditWrapper))

        self.assertEqual(edit.window_text(), "s3cRe7")
        self.assertEqual(edit.get_value(), "s3cRe7")
        self.assertEqual(edit.line_count(), 1)
        self.assertEqual(edit.texts(), ["s3cRe7"])

        edit.set_edit_text("secret")
        self.assertEqual(edit.window_text(), "secret")
        edit.set_window_text("42", append=True)
        self.assertEqual(edit.window_text(), "secret42")
        edit.set_edit_text("AB", pos_start=1, pos_end=4)
        self.assertEqual(edit.window_text(), "sABet42")

    def test_generic_value_and_selection_methods(self):
        slider = self.dlg.by(control_type="Slider", class_name="QSlider").find(timeout=10)
        radio = self.dlg.by(name="Radio button 2").find(timeout=10)

        self.assertTrue(isinstance(slider, SliderWrapper))
        self.assertTrue(isinstance(radio, ButtonWrapper))
        self.assertEqual(Qt5Wrapper.get_value(slider), "40")
        Qt5Wrapper.set_value(slider, 46)
        self.assertEqual(Qt5Wrapper.get_value(slider), "46")

        Qt5Wrapper.select(radio)
        self.assertTrue(Qt5Wrapper.is_selected(radio))

    def test_button_wrappers(self):
        button = self.dlg.by(name="Default Push Button").find(timeout=10)
        self.assertTrue(isinstance(button, ButtonWrapper))
        button.click()

        checkbox = self.dlg.by(name="&Disable widgets").find(timeout=10)
        self.assertTrue(isinstance(checkbox, ButtonWrapper))
        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.UNCHECKED)
        checkbox.toggle()
        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.CHECKED)
        self.assertTrue(checkbox.is_checked())
        checkbox.uncheck()
        self.assertFalse(checkbox.is_checked())
        checkbox.check()
        self.assertTrue(checkbox.is_checked())

        radio = self.dlg.by(name="Radio button 2").find(timeout=10)
        self.assertTrue(isinstance(radio, ButtonWrapper))
        self.assertFalse(radio.is_selected())
        radio.select()
        self.assertTrue(radio.is_selected())

    def test_combo_box_wrapper(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)

        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertGreaterEqual(combo.item_count(), 3)
        self.assertEqual(combo.item_count(), len(combo.texts()))
        self.assertEqual(combo.texts()[0], "NorwegianWood")
        self.assertIn("Fusion", combo.texts())
        self.assertEqual(combo.selected_index(), 0)
        self.assertEqual(combo.selected_text(), "NorwegianWood")
        self.assertFalse(combo.is_editable())

        combo.select("Fusion")
        self.assertEqual(combo.selected_text(), "Fusion")
        combo.select(0)
        self.assertEqual(combo.selected_text(), "NorwegianWood")
        combo.expand()
        combo.collapse()

    def test_expanded_combo_popup_is_child_and_dump_tree_works(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        combo.expand()
        time.sleep(1)

        self.assertEqual(len(combo.children()), 1)

        with redirect_stdout(StringIO()):
            self.dlg.dump_tree(depth=None, max_width=None)

    def test_group_box_name_appears_in_dump_tree(self):
        output = StringIO()

        with redirect_stdout(output):
            self.dlg.dump_tree(depth=None, max_width=None)

        content = output.getvalue()
        self.assertIn("GroupBox - 'Group 1'", content)
        self.assertIn(".by(name='Group 1', class_name='QGroupBox'", content)

    def test_tab_control_wrapper(self):
        tab = self.dlg.by(control_type="TabControl", class_name="QTabWidget").find(timeout=10)
        self.assertTrue(isinstance(tab, TabControlWrapper))
        self.assertEqual(tab.tab_count(), 2)
        self.assertEqual(tab.get_selected_tab(), 0)
        self.assertEqual(tab.texts(), ["&Table", "Text &Edit"])

        tab.select("Text &Edit")
        self.assertEqual(tab.get_selected_tab(), 1)
        tab.select(0)
        self.assertEqual(tab.get_selected_tab(), 0)

    def test_slider_spinner_and_progress_wrappers(self):
        spinner = self.dlg.by(control_type="Spinner", class_name="QSpinBox").find(timeout=10)
        self.assertTrue(isinstance(spinner, SliderWrapper))
        self.assertEqual(spinner.min_value(), 0)
        self.assertEqual(spinner.max_value(), 99)
        self.assertEqual(spinner.value(), "50")
        spinner.set_value(55)
        self.assertEqual(spinner.value(), "55")

        slider = self.dlg.by(control_type="Slider", class_name="QSlider").find(timeout=10)
        self.assertTrue(isinstance(slider, SliderWrapper))
        self.assertEqual(slider.min_value(), 0)
        self.assertEqual(slider.max_value(), 99)
        self.assertEqual(slider.value(), "40")
        slider.set_value(45)
        self.assertEqual(slider.value(), "45")

        progress = self.dlg.by(control_type="ProgressBar").find(timeout=10)
        self.assertTrue(isinstance(progress, SliderWrapper))
        self.assertGreaterEqual(int(progress.value()), 0)
        self.assertGreater(progress.max_value(), progress.min_value())

    def test_table_wrapper(self):
        table = self.dlg.by(control_type="Table").find(timeout=10)
        self.assertTrue(isinstance(table, TableWrapper))
        self.assertEqual(table.row_count(), 10)
        self.assertEqual(table.column_count(), 10)
        self.assertEqual(table.item_count(), 100)
        self.assertEqual(len(table.texts()), 10)
        self.assertEqual([len(row) for row in table.texts()], [10] * 10)

        original_text = table.cell_text(0, 0)
        original_value = table.cell_value(0, 0)
        self.assertTrue(original_text == "" or isinstance(original_text, str))
        self.assertTrue(original_value is None or isinstance(original_value, str))

        rect = table.cell_rectangle(0, 0)
        self.assertGreater(rect.width(), 0)
        self.assertGreater(rect.height(), 0)

        table.select(0, 0)
        self.assertTrue(table.is_cell_selected(0, 0))
        table.click(0, 0)
        self.assertTrue(table.is_cell_selected(0, 0))

        table.set_cell_value(0, 0, "changed")
        self.assertEqual(table.cell_text(0, 0), "changed")
        self.assertEqual(table.cell_value(0, 0), "changed")

        self.assertRaises(IndexError, table.cell_text, -1, 0)
        self.assertRaises(IndexError, table.cell_text, 0, 10)

    def test_dump_tree_and_close(self):
        with redirect_stdout(StringIO()):
            self.dlg.dump_tree(depth=None, max_width=None)

        self.root.close()


class Qt5InterviewWrapperLinuxTests(unittest.TestCase):
    """List/tree/table wrapper tests for the Qt5 interview example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt5").start(qt_interview_app)
        time.sleep(2)
        self.dlg = self.app.window()
        self.root = self.dlg.find(timeout=15)

    def tearDown(self):
        self.app.kill()

    def test_list_view_wrapper(self):
        list_view = self.dlg.by(control_type="List").find(timeout=10)
        self.assertTrue(isinstance(list_view, ListViewWrapper))
        self.assertEqual(list_view.class_name(), "QListView")
        self.assertEqual(list_view.item_count(), 1000)
        self.assertEqual(
            list_view.texts()[:5],
            ["Item 0:0", "Item 1:0", "Item 2:0", "Item 3:0", "Item 4:0"],
        )
        list_view.select(1)
        self.assertSequenceEqual(list_view.get_items(), list_view.children())
        self.assertSequenceEqual(list_view.items(), list_view.children())

    def test_tree_view_wrapper(self):
        tree_view = self.dlg.by(control_type="Tree").find(timeout=10)
        self.assertTrue(isinstance(tree_view, TreeViewWrapper))
        self.assertEqual(tree_view.class_name(), "QTreeView")
        self.assertEqual(tree_view.item_count(depth=1), len(tree_view.children()))
        self.assertEqual(tree_view.item_count(), len(tree_view.descendants()))
        self.assertSequenceEqual(tree_view.roots(), tree_view.children())

    def test_tree_view_expand_collapse(self):
        tree_view = self.dlg.by(control_type="Tree").find(timeout=10)
        tree_view.expand()
        tree_view.collapse()

    def test_tree_view_expand_collapse_specific_item(self):
        tree_view = self.dlg.by(control_type="Tree").find(timeout=10)
        self.assertTrue(tree_view.is_collapsed((1,)))
        self.assertEqual(tree_view.item_text((1,)), "Item 1:0")
        self.assertEqual(tree_view.item_text(r"\Item 1:0"), "Item 1:0")
        tree_view.expand((1,))
        self.assertTrue(tree_view.is_expanded((1,)))
        tree_view.collapse((1,))
        self.assertTrue(tree_view.is_collapsed((1,)))

        tree_view.expand(r"\Item 1:0")
        self.assertTrue(tree_view.is_expanded(r"\Item 1:0"))
        tree_view.collapse(r"\Item 1:0")
        self.assertTrue(tree_view.is_collapsed(r"\Item 1:0"))
        self.assertRaises(InjectedBaseError, tree_view.expand, r"\__missing__")

    def test_tree_view_expand_collapse_deep_item(self):
        tree_view = self.dlg.by(control_type="Tree").find(timeout=10)
        tree_view.expand((2,))
        tree_view.expand((2, 2))
        self.assertEqual(tree_view.item_text((2, 2, 2)), "Item 2:0")
        self.assertTrue(tree_view.is_collapsed((2, 2, 2)))
        tree_view.expand((2, 2, 2))
        self.assertTrue(tree_view.is_expanded((2, 2, 2)))
        tree_view.collapse((2, 2, 2))
        self.assertTrue(tree_view.is_collapsed((2, 2, 2)))

        tree_view.expand(r"\Item 2:0")
        tree_view.expand(r"\Item 2:0\Item 2:0")
        self.assertEqual(tree_view.item_text(r"\Item 2:0\Item 2:0\Item 2:0"), "Item 2:0")
        tree_view.expand(r"\Item 2:0\Item 2:0\Item 2:0")
        self.assertTrue(tree_view.is_expanded(r"\Item 2:0\Item 2:0\Item 2:0"))
        tree_view.collapse(r"\Item 2:0\Item 2:0\Item 2:0")
        self.assertTrue(tree_view.is_collapsed(r"\Item 2:0\Item 2:0\Item 2:0"))

    def test_model_table_wrapper(self):
        table = self.dlg.by(control_type="Table", class_name="QTableView").find(timeout=10)
        self.assertTrue(isinstance(table, TableWrapper))
        self.assertEqual(table.class_name(), "QTableView")
        self.assertEqual(table.row_count(), 1000)
        self.assertEqual(table.column_count(), 10)
        self.assertEqual(table.item_count(), 10000)


if __name__ == "__main__":
    unittest.main()
