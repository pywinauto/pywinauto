# -*- coding: utf-8 -*-
"""Tests for Qt6 wrappers."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.base_application import WindowSpecification  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402

from pywinauto.controls.qt6_controls import (  # noqa: E402
    ButtonWrapper,
    ComboBoxWrapper,
    ListViewWrapper,
    PaneWrapper,
    SliderWrapper,
    TabControlWrapper,
    TableWrapper,
    TreeViewWrapper,
    WindowWrapper,
)
from pywinauto.controls.qt6wrapper import Qt6Wrapper  # noqa: E402
from injectlib.api import InjectedBaseError  # noqa: E402


qt_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\Qt6_samples")
qt_gallery_app = os.path.join(qt_samples_folder, "gallery.exe")
qt_tree_app = os.path.join(qt_samples_folder, "editabletreemodel.exe")
qt_spreadsheet_app = os.path.join(qt_samples_folder, "spreadsheet.exe")


def _set_timings():
    """Setup timings for Qt related tests."""
    Timings.defaults()
    Timings.window_find_timeout = 20


def _assert_sample_running(test_case, app, app_path):
    """Fail with a clear message if a Qt6 sample exits before injection."""
    test_case.assertTrue(
        app.is_process_running(),
        "Qt6 sample exited before root lookup: path={!r}, pid={!r}".format(
            app_path,
            app.process,
        ),
    )


@unittest.skipIf(not is_x64_Python(), "Qt6 MSVC test samples are 64-bit only")
class Qt6WrapperTests(unittest.TestCase):

    """Unit tests for Qt6Wrapper class."""

    def setUp(self):
        """Start Qt6 gallery sample application."""
        _set_timings()

        self.app = Application(backend="qt6")
        self.app = self.app.start(qt_gallery_app)
        time.sleep(2)
        _assert_sample_running(self, self.app, qt_gallery_app)

        self.dlg = self.app.window()
        self.root = self.dlg.find(timeout=10)

    def tearDown(self):
        """Close application after tests."""
        self.app.kill()

    def test_window_specification_binding(self):
        """Test attribute lookup for Qt6 backend."""
        combo_spec = self.dlg.ComboBox
        self.assertTrue(isinstance(combo_spec, WindowSpecification))
        self.assertTrue(combo_spec.app, self.app)

    def test_find_controls_by_class_name_and_title(self):
        """Test getting Qt6 controls by class name and title."""
        combo = self.dlg.by(class_name="QComboBox",
                            name="windowsvista").find(timeout=10)
        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertEqual(combo.window_text(), "windowsvista")

        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertEqual(self.root.class_name(), "WidgetGallery")
        self.assertEqual(self.root.window_text(), "Widget Gallery Qt 6.9.1")
        self.assertEqual(self.root.friendly_class_name(), "Window")

        group = self.dlg.by(class_name="QGroupBox",
                            name="Buttons").find(timeout=10)
        self.assertTrue(isinstance(group, PaneWrapper))
        self.assertEqual(group.window_text(), "Buttons")

    def test_wrapper_registry_is_qt6_specific(self):
        """Test Qt6 wrapper uses Qt6 classes."""
        combo = self.dlg.by(control_type="ComboBox",
                            name="windowsvista").find(timeout=10)
        self.assertTrue(type(combo) is ComboBoxWrapper)
        self.assertTrue(type(combo) is not Qt6Wrapper)

    def test_common_value_and_selection_methods(self):
        """Test generic Qt6 wrapper value and selection methods directly."""
        slider = self.dlg.by(control_type="Slider",
                             class_name="QSlider").find(timeout=10)
        radio = self.dlg.by(control_type="RadioButton",
                            name="Radio button 2").find(timeout=10)

        self.assertTrue(isinstance(slider, SliderWrapper))
        self.assertTrue(isinstance(radio, ButtonWrapper))
        self.assertEqual(Qt6Wrapper.get_value(slider), "40")
        Qt6Wrapper.set_value(slider, 46)
        self.assertEqual(Qt6Wrapper.get_value(slider), "46")

        Qt6Wrapper.select(radio)
        self.assertTrue(Qt6Wrapper.is_selected(radio))

    def test_button_combo_tab_and_table_wrappers(self):
        """Test representative Qt6 control-specific wrappers."""
        button = self.dlg.by(control_type="Button",
                             name="Default Push Button").find(timeout=10)
        checkbox = self.dlg.by(name="&Disable widgets").find(timeout=10)
        combo = self.dlg.by(control_type="ComboBox",
                            name="windowsvista").find(timeout=10)
        tab = self.dlg.by(control_type="TabControl",
                          class_name="QTabWidget").find(timeout=10)
        table = self.dlg.by(control_type="Table",
                            class_name="QTableWidget").find(timeout=10)

        self.assertTrue(isinstance(button, ButtonWrapper))
        self.assertTrue(isinstance(checkbox, ButtonWrapper))
        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertTrue(isinstance(tab, TabControlWrapper))
        self.assertTrue(isinstance(table, TableWrapper))

        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.UNCHECKED)
        checkbox.toggle()
        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.CHECKED)

        self.assertGreaterEqual(combo.item_count(), 1)
        self.assertIn(combo.selected_text(), combo.texts())
        self.assertGreaterEqual(tab.tab_count(), 1)

        self.assertGreater(table.row_count(), 0)
        self.assertGreater(table.column_count(), 0)
        self.assertGreater(table.cell_rectangle(0, 0).width(), 0)

    def test_list_wrapper_in_gallery(self):
        """Test Qt6 list wrapper from the gallery sample."""
        list_view = self.dlg.by(control_type="List",
                                class_name="QListView",
                                name="listView").find(timeout=10)

        self.assertTrue(isinstance(list_view, ListViewWrapper))
        self.assertGreaterEqual(list_view.item_count(), 0)

    def test_window_wrapper(self):
        """Test Qt6 window wrapper."""
        window = self.root

        self.assertTrue(isinstance(window, WindowWrapper))
        self.assertTrue(window.is_dialog())
        window.close()
        self.app.wait_for_process_exit(timeout=5, retry_interval=0.2)
        self.assertFalse(self.app.is_process_running())


@unittest.skipIf(not is_x64_Python(), "Qt6 MSVC test samples are 64-bit only")
class Qt6EditableTreeModelTests(unittest.TestCase):

    """Behavior tests for the Qt6 editable tree model sample."""

    def setUp(self):
        """Start the Qt6 editable tree model sample."""
        _set_timings()

        self.app = Application(backend="qt6")
        self.app = self.app.start(qt_tree_app)
        time.sleep(2)
        _assert_sample_running(self, self.app, qt_tree_app)

        self.root = self.app.window().find(timeout=10)
        self.tree_view = self.root.by(
            control_type="Tree",
            class_name="QTreeView",
        ).find(timeout=10)

    def tearDown(self):
        """Close the Qt6 editable tree model sample."""
        self.app.kill()

    def test_editable_tree_model_starts(self):
        """Test Qt6 editable tree model sample is injectable."""
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertEqual(self.root.class_name(), "MainWindow")
        self.assertEqual(self.root.window_text(), "Editable Tree Model")

    def test_editable_tree_view_expand_collapse_specific_item(self):
        """Test Qt6 tree wrapper expand/collapse for a model item path."""
        self.assertTrue(isinstance(self.tree_view, TreeViewWrapper))
        self.assertEqual(self.tree_view.element_info.auto_id, "view")
        self.assertEqual(self.tree_view.item_text((0,)), "Getting Started")
        self.assertEqual(self.tree_view.item_text(r"\Getting Started"), "Getting Started")
        self.tree_view.collapse((0,))
        self.assertTrue(self.tree_view.is_collapsed((0,)))
        self.tree_view.expand((0,))
        self.assertTrue(self.tree_view.is_expanded((0,)))
        self.tree_view.collapse(r"\Getting Started")
        self.assertTrue(self.tree_view.is_collapsed(r"\Getting Started"))
        self.tree_view.expand(r"\Getting Started")
        self.assertTrue(self.tree_view.is_expanded(r"\Getting Started"))
        self.assertRaises(InjectedBaseError, self.tree_view.expand, r"\__missing__")

    def test_editable_tree_view_expand_collapse_deep_item(self):
        """Test Qt6 tree wrapper expand/collapse for a deeper model item path."""
        self.assertEqual(self.tree_view.item_text((0, 0)), "Launching Designer")
        self.assertEqual(self.tree_view.item_text(r"\Getting Started\Launching Designer"),
                         "Launching Designer")
        self.tree_view.collapse((0, 0))
        self.assertTrue(self.tree_view.is_collapsed((0, 0)))
        self.tree_view.expand((0, 0))
        self.assertTrue(self.tree_view.is_expanded((0, 0)))
        self.tree_view.collapse(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree_view.is_collapsed(r"\Getting Started\Launching Designer"))
        self.tree_view.expand(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree_view.is_expanded(r"\Getting Started\Launching Designer"))


@unittest.skipIf(not is_x64_Python(), "Qt6 MSVC test samples are 64-bit only")
class Qt6SpreadsheetTests(unittest.TestCase):

    """Behavior tests for the Qt6 spreadsheet sample."""

    def setUp(self):
        """Start the Qt6 spreadsheet sample."""
        _set_timings()

        self.app = Application(backend="qt6")
        self.app = self.app.start(qt_spreadsheet_app)
        time.sleep(2)
        _assert_sample_running(self, self.app, qt_spreadsheet_app)

        self.root = self.app.window().find(timeout=10)
        self.table = self.root.by(
            control_type="Table",
            class_name="QTableWidget",
        ).find(timeout=10)

    def tearDown(self):
        """Close the Qt6 spreadsheet sample."""
        self.app.kill()

    def test_spreadsheet_table_wrapper(self):
        """Test the Qt6 spreadsheet sample table is injectable."""
        self.assertTrue(isinstance(self.table, TableWrapper))
        self.assertEqual(self.table.row_count(), 10)
        self.assertEqual(self.table.column_count(), 6)
        self.assertEqual(self.table.item_count(), 60)
        self.assertEqual(self.table.cell_text(0, 0), "Item")
        self.assertEqual(self.table.cell_value(0, 0), "Item")
        self.assertGreater(self.table.cell_rectangle(0, 0).width(), 0)
        self.assertGreater(self.table.cell_rectangle(0, 0).height(), 0)
        self.table.select(0, 0)
        self.assertTrue(self.table.is_cell_selected(0, 0))
        self.table.click(1, 0)
        self.assertTrue(self.table.is_cell_selected(1, 0))
        self.table.set_cell_value(0, 0, "changed")
        self.assertEqual(self.table.cell_text(0, 0), "changed")
        self.assertEqual(self.table.cell_value(0, 0), "changed")
        self.assertRaises(IndexError, self.table.cell_text, -1, 0)
        self.assertRaises(IndexError, self.table.cell_text, 0, 6)


if __name__ == "__main__":
    unittest.main()
