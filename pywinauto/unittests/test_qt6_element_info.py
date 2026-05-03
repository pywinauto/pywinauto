# -*- coding: utf-8 -*-
"""Tests for Qt6ElementInfo."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from pywinauto.qt6.element_info import PIDNotFound, Qt6ElementInfo  # noqa: E402
from injectlib.api import InjectedBaseError, InjectedNotFoundError  # noqa: E402


qt_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\Qt6_samples")
qt_gallery_app = os.path.join(qt_samples_folder, "gallery.exe")
qt_tree_app = os.path.join(qt_samples_folder, "editabletreemodel.exe")


def _set_timings():
    """Setup timings for Qt related tests."""
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt6ElementInfoTests(unittest.TestCase):

    """Unit tests for Qt6ElementInfo class."""

    def setUp(self):
        """Start Qt6 gallery sample application."""
        _set_timings()

        self.app = Application(backend="qt6")
        self.app = self.app.start(qt_gallery_app)
        time.sleep(2)

        self.root = self.app.window().find(timeout=10)
        self.ctrl = self.root.element_info

    def tearDown(self):
        """Close application after tests."""
        self.app.kill()

    def test_top_window_properties(self):
        """Test top-level Qt6 window properties."""
        self.assertGreater(self.ctrl.control_id, 0)
        self.assertGreater(self.ctrl.runtime_id, 0)
        self.assertEqual(self.ctrl.process_id, self.app.process)
        self.assertEqual(self.ctrl.pid, self.app.process)
        self.assertEqual(self.ctrl.name, "Widget Gallery Qt 6.9.1")
        self.assertEqual(self.ctrl.class_name, "WidgetGallery")
        self.assertEqual(self.ctrl.control_type, "Window")
        self.assertEqual(self.ctrl.framework_id, "Qt")
        self.assertIsNone(self.ctrl.handle)
        self.assertTrue(self.ctrl.enabled)
        self.assertTrue(self.ctrl.visible)

    def test_synthetic_desktop_root_properties(self):
        """Test synthetic Qt6 desktop root properties."""
        desktop_root = Qt6ElementInfo()

        self.assertIsNone(desktop_root.control_id)
        self.assertIsNone(desktop_root.runtime_id)
        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(desktop_root.name, "--root--")
        self.assertEqual(desktop_root.class_name, "Qt6Desktop")
        self.assertEqual(desktop_root.control_type, "Desktop")
        self.assertEqual(desktop_root.framework_id, "Qt")
        self.assertEqual(desktop_root.auto_id, "Qt6Desktop")
        self.assertEqual(desktop_root.automation_id, "Qt6Desktop")
        self.assertIsNone(desktop_root.handle)
        self.assertIsNone(desktop_root.parent)
        self.assertEqual(desktop_root.value, "")
        self.assertEqual(desktop_root.rich_text, "--root--")

    def test_pid_not_found(self):
        """Test Qt element creation without a required target process id."""
        self.assertRaises(PIDNotFound, Qt6ElementInfo, 1)

    def test_children_and_descendants(self):
        """Test Qt6 child traversal and criteria filtering."""
        children = self.ctrl.children()
        self.assertGreater(len(children), 5)
        self.assertEqual(children[0].name, "&Style:")
        self.assertEqual(children[0].class_name, "QLabel")
        self.assertEqual(children[0].control_type, "Text")

        combos = self.ctrl.children(control_type="ComboBox")
        self.assertEqual(len(combos), 2)
        self.assertEqual(combos[0].name, "windowsvista")

        groups = self.ctrl.children(control_type="GroupBox")
        self.assertEqual([group.name for group in groups], ["Buttons", "Simple Input Widgets"])

        self.assertTrue(self.ctrl.descendants(control_type="Tree", class_name="QTreeView"))
        self.assertTrue(self.ctrl.descendants(control_type="Table", class_name="QTableWidget"))

    def test_desktop_finds_top_window(self):
        """Test Qt6 root finds window through win32 top-level search."""
        desktop_root = Qt6ElementInfo()

        self.assertEqual(desktop_root.children(), [])
        children = desktop_root.children(name="Widget Gallery Qt 6.9.1")
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].process_id, self.app.process)
        self.assertEqual(children[0].class_name, "WidgetGallery")
        self.assertEqual(children[0].control_type, "Window")
        self.assertIsNone(children[0].handle)

    def test_native_property_missing(self):
        """Test missing native Qt property handling."""
        combo = self.root.by(control_type="ComboBox",
                             name="windowsvista").find(timeout=10)

        self.assertIsNone(combo.element_info.get_native_property("__missing__"))
        self.assertRaises(InjectedNotFoundError,
                          combo.element_info.get_native_property,
                          "__missing__",
                          error_if_not_exists=True)

    def test_active_element(self):
        """Test getting focused Qt element."""
        combo = self.root.by(control_type="ComboBox",
                             name="windowsvista").find(timeout=10)
        combo.set_focus()

        active = self.ctrl.get_active(self.app.process)
        self.assertEqual(active, combo.element_info)


class Qt6TreeElementInfoTests(unittest.TestCase):

    """Unit tests for Qt6ElementInfo with Qt editable tree model sample."""

    def setUp(self):
        """Start Qt6 editable tree model sample application."""
        _set_timings()

        self.app = Application(backend="qt6")
        self.app = self.app.start(qt_tree_app)
        time.sleep(2)

        self.root = self.app.window().find(timeout=10)
        self.tree = self.root.by(control_type="Tree",
                                 class_name="QTreeView").find(timeout=10).element_info

    def tearDown(self):
        """Close application after tests."""
        self.app.kill()

    def test_tree_expand_collapse_specific_item_path(self):
        """Test direct Qt6 tree item path expand/collapse calls."""
        self.assertEqual(self.tree.class_name, "QTreeView")
        self.assertEqual(self.tree.auto_id, "view")
        self.assertTrue(self.tree.is_expanded((0,)))
        self.assertEqual(self.tree.item_text((0,)), "Getting Started")
        self.assertEqual(self.tree.item_text(r"\Getting Started"), "Getting Started")

        self.tree.collapse((0,))
        self.assertTrue(self.tree.is_collapsed((0,)))
        self.tree.expand((0,))
        self.assertTrue(self.tree.is_expanded((0,)))

        self.tree.collapse(r"\Getting Started")
        self.assertTrue(self.tree.is_collapsed(r"\Getting Started"))
        self.tree.expand(r"\Getting Started")
        self.assertTrue(self.tree.is_expanded(r"\Getting Started"))
        self.assertRaises(InjectedBaseError, self.tree.expand, r"\__missing__")

    def test_tree_expand_collapse_deep_item_path(self):
        """Test direct Qt6 tree item path handling for a deeper model item."""
        self.assertEqual(self.tree.item_text((0, 0)), "Launching Designer")
        self.tree.collapse((0, 0))
        self.assertTrue(self.tree.is_collapsed((0, 0)))
        self.tree.expand((0, 0))
        self.assertTrue(self.tree.is_expanded((0, 0)))

        self.tree.collapse(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree.is_collapsed(r"\Getting Started\Launching Designer"))
        self.tree.expand(r"\Getting Started\Launching Designer")
        self.assertTrue(self.tree.is_expanded(r"\Getting Started\Launching Designer"))


if __name__ == "__main__":
    unittest.main()
