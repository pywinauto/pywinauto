# -*- coding: utf-8 -*-
"""Linux wrapper tests for the Qt6 backend."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest


if sys.platform == "win32":
    raise unittest.SkipTest("Linux Qt tests require Linux")

sys.path.append(".")
from pywinauto import Application  # noqa: E402
from pywinauto.base_application import WindowSpecification  # noqa: E402
from pywinauto.controls.qt6_controls import (  # noqa: E402
    ButtonWrapper, ComboBoxWrapper, EditWrapper, ListViewWrapper, PaneWrapper,
    SliderWrapper, TabControlWrapper, TableWrapper, TreeViewWrapper,
    WindowWrapper,
)
from pywinauto.controls.qt6wrapper import Qt6Wrapper  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from injectlib.api import InjectedBaseError  # noqa: E402


qt_samples_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "apps", "Qt6_samples_linux"))
qt_gallery_app = os.path.join(qt_samples_folder, "gallery")
qt_tree_app = os.path.join(qt_samples_folder, "editabletreemodel")
qt_spreadsheet_app = os.path.join(qt_samples_folder, "spreadsheet")
qt_quick_samples_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "apps", "Qt6_quick_samples_linux"))
qt_quick_mousearea_app = os.path.join(qt_quick_samples_folder, "mouseareaexample")
qt_quick_widget_opengl_app = os.path.join(
    qt_quick_samples_folder, "qquickwidgetversuswindow_opengl")


def _set_timings():
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt6GalleryWrapperLinuxTests(unittest.TestCase):
    """Wrapper tests for the Qt6 gallery example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_gallery_app)
        time.sleep(2)
        self.dlg = self.app.window()
        self.root = self.dlg.find(timeout=15)

    def tearDown(self):
        self.app.kill()

    def test_window_specification_binding(self):
        combo_spec = self.dlg.ComboBox
        self.assertTrue(isinstance(combo_spec, WindowSpecification))
        self.assertTrue(combo_spec.app, self.app)

    def test_find_controls_by_class_name_and_title(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertEqual(combo.window_text(), combo.selected_text())

        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertEqual(self.root.class_name(), "WidgetGallery")
        self.assertTrue(self.root.window_text().startswith("Widget Gallery Qt "))
        self.assertEqual(self.root.friendly_class_name(), "Window")

        group = self.dlg.by(class_name="QGroupBox", name="Buttons").find(timeout=10)
        self.assertTrue(isinstance(group, PaneWrapper))
        self.assertEqual(group.window_text(), "Buttons")

    def test_wrapper_registry_is_qt6_specific(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        self.assertTrue(type(combo) is ComboBoxWrapper)
        self.assertTrue(type(combo) is not Qt6Wrapper)

    def test_common_value_and_selection_methods(self):
        slider = self.dlg.by(control_type="Slider", class_name="QSlider").find(timeout=10)
        radio = self.dlg.by(control_type="RadioButton", name="Radio button 2").find(timeout=10)

        self.assertTrue(isinstance(slider, SliderWrapper))
        self.assertTrue(isinstance(radio, ButtonWrapper))
        self.assertEqual(Qt6Wrapper.get_value(slider), "40")
        Qt6Wrapper.set_value(slider, 46)
        self.assertEqual(Qt6Wrapper.get_value(slider), "46")

        Qt6Wrapper.select(radio)
        self.assertTrue(Qt6Wrapper.is_selected(radio))

    def test_button_combo_tab_and_table_wrappers(self):
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertTrue(isinstance(self.dlg.ComboBox, WindowSpecification))
        self.assertTrue(self.root.window_text().startswith("Widget Gallery Qt "))
        self.assertEqual(self.root.class_name(), "WidgetGallery")

        button = self.dlg.by(control_type="Button", name="Default Push Button").find(timeout=10)
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        checkbox = self.dlg.by(name="&Disable widgets").find(timeout=10)
        tab = self.dlg.by(control_type="TabControl", class_name="QTabWidget").find(timeout=10)
        table = self.dlg.by(control_type="Table", class_name="QTableWidget").find(timeout=10)

        self.assertTrue(isinstance(button, ButtonWrapper))
        self.assertTrue(isinstance(combo, ComboBoxWrapper))
        self.assertTrue(isinstance(checkbox, ButtonWrapper))
        self.assertTrue(isinstance(tab, TabControlWrapper))
        self.assertTrue(isinstance(table, TableWrapper))

        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.UNCHECKED)
        checkbox.toggle()
        self.assertEqual(checkbox.get_toggle_state(), ButtonWrapper.CHECKED)

        self.assertGreaterEqual(combo.item_count(), 1)
        self.assertEqual(combo.item_count(), len(combo.texts()))
        self.assertIn(combo.selected_text(), combo.texts())
        combo.expand()
        combo.collapse()
        self.assertGreaterEqual(tab.tab_count(), 1)
        self.assertGreater(table.row_count(), 0)
        self.assertGreater(table.column_count(), 0)
        self.assertGreater(table.cell_rectangle(0, 0).width(), 0)

    def test_list_wrapper_in_gallery(self):
        list_views = self.root.descendants(control_type="List", class_name="QListView")
        self.assertTrue(any(isinstance(list_view, ListViewWrapper) for list_view in list_views))

    def test_window_wrapper_close(self):
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertTrue(self.root.is_dialog())
        self.root.close()


class Qt6EditableTreeWrapperLinuxTests(unittest.TestCase):
    """Tree wrapper tests for the Qt6 editable tree model example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_tree_app)
        time.sleep(2)
        self.root = self.app.window().find(timeout=15)
        self.tree = self.root.by(control_type="Tree", class_name="QTreeView").find(timeout=10)

    def tearDown(self):
        self.app.kill()

    def test_editable_tree_model_starts(self):
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertEqual(self.root.class_name(), "MainWindow")
        self.assertEqual(self.root.window_text(), "Editable Tree Model")

    def test_tree_path_actions(self):
        self.assertTrue(isinstance(self.tree, TreeViewWrapper))
        self.assertEqual(self.tree.element_info.auto_id, "view")
        self.assertEqual(self.tree.item_text((0,)), "Getting Started")
        self.assertEqual(self.tree.item_text(r"\Getting Started"), "Getting Started")
        self.assertEqual(self.tree.item_text((0, 0)), "Launching Designer")
        self.tree.collapse((0,))
        self.assertTrue(self.tree.is_collapsed((0,)))
        self.tree.expand((0,))
        self.assertTrue(self.tree.is_expanded((0,)))
        self.tree.collapse(r"\Getting Started")
        self.assertTrue(self.tree.is_collapsed(r"\Getting Started"))
        self.tree.expand(r"\Getting Started")
        self.assertTrue(self.tree.is_expanded(r"\Getting Started"))
        self.assertRaises(InjectedBaseError, self.tree.expand, r"\__missing__")

    def test_tree_deep_path_actions(self):
        self.assertEqual(self.tree.item_text((0, 0)), "Launching Designer")
        self.assertEqual(self.tree.item_text(r"\Getting Started\Launching Designer"),
                         "Launching Designer")
        self.tree.collapse((0, 0))
        self.assertTrue(self.tree.is_collapsed((0, 0)))
        self.tree.expand((0, 0))
        self.assertTrue(self.tree.is_expanded((0, 0)))
        self.tree.collapse(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree.is_collapsed(r"\Getting Started\Launching Designer"))
        self.tree.expand(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree.is_expanded(r"\Getting Started\Launching Designer"))


class Qt6SpreadsheetWrapperLinuxTests(unittest.TestCase):
    """Table wrapper tests for the Qt6 spreadsheet example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_spreadsheet_app)
        time.sleep(2)
        self.root = self.app.window().find(timeout=15)
        self.table = self.root.by(control_type="Table", class_name="QTableWidget").find(timeout=10)

    def tearDown(self):
        self.app.kill()

    def test_table_cell_actions(self):
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


class Qt6QuickMouseAreaWrapperLinuxTests(unittest.TestCase):
    """Wrapper tests for the Qt6 Quick mousearea example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_quick_mousearea_app)
        time.sleep(2)
        self.dlg = self.app.window(class_name="QQuickView")
        self.root = self.dlg.find(timeout=15)

    def tearDown(self):
        self.app.kill()

    def test_qml_items_are_exposed_as_qt_elements(self):
        self.assertTrue(isinstance(self.root, WindowWrapper))
        self.assertEqual(self.root.class_name(), "QQuickView")

        descendants = self.root.descendants()
        class_names = [item.class_name() for item in descendants]
        self.assertIn("QQuickRootItem", class_names)
        self.assertIn("QQuickRectangle", class_names)
        self.assertIn("QQuickMouseArea_QML_0", class_names)
        self.assertIn("QQuickMouseArea", class_names)

        texts = self.root.descendants(control_type="Text")
        self.assertIn("Click", [item.window_text() for item in texts])
        self.assertIn("Drag", [item.window_text() for item in texts])

    def test_qml_mouse_area_click_changes_qml_state(self):
        mouse_area = self.dlg.by(class_name="QQuickMouseArea_QML_0").find(timeout=10)
        mouse_area.click()
        time.sleep(1)

        texts = [item.window_text()
                 for item in self.root.descendants(control_type="Text")]
        self.assertIn("Pressed (LeftButton shift=false)", texts)
        self.assertIn("Clicked (wasHeld=false)", texts)

    def test_qml_native_property_can_be_changed(self):
        mouse_area = self.dlg.by(class_name="QQuickMouseArea_QML_0").find(timeout=10)
        self.assertTrue(mouse_area.get_native_property("enabled"))

        mouse_area.set_native_property("enabled", False)
        time.sleep(0.5)
        self.assertFalse(mouse_area.get_native_property("enabled"))

        mouse_area.set_native_property("enabled", True)
        time.sleep(0.5)
        self.assertTrue(mouse_area.get_native_property("enabled"))


class Qt6QuickWidgetOpenGLWrapperLinuxTests(unittest.TestCase):
    """Wrapper tests for the mixed Qt6 QWidget/Qt Quick example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_quick_widget_opengl_app)
        time.sleep(2)

    def tearDown(self):
        self.app.kill()

    def _window_by_class(self, class_name):
        for window in self.app.windows():
            if window.class_name() == class_name:
                return window
        self.fail("Top-level window with class '{}' was not found".format(class_name))

    def test_qwidget_shell_still_exposes_controls(self):
        widget_root = self._window_by_class("QWidget")

        self.assertEqual(widget_root.children_texts()[:3],
                         ["Type", "Multisample (4x)",
                          "QQuickWidget status: Ready"])
        descendant_texts = [item.window_text()
                            for item in widget_root.descendants()]
        self.assertIn("QQuickWidget (indirect through framebuffer objects)",
                      descendant_texts)
        self.assertIn("QQuickView in a window container (direct)",
                      descendant_texts)
        self.assertIn("Show widget overlay", descendant_texts)
        self.assertTrue(widget_root.by(class_name="QQuickWidget").exists(timeout=10))

    def test_qml_text_input_can_be_edited(self):
        quick_root = self._window_by_class("QQuickWidgetOffscreenWindow")
        edit = quick_root.by(class_name="QQuickTextInput").find(timeout=10)

        self.assertTrue(isinstance(edit, EditWrapper))
        self.assertEqual(edit.window_text(), "Hello Qt")

        edit.set_edit_text("Backend Qt6Quick")
        time.sleep(1)
        self.assertEqual(edit.window_text(), "Backend Qt6Quick")
        self.assertEqual(edit.get_value(), "Backend Qt6Quick")


if __name__ == "__main__":
    unittest.main()
