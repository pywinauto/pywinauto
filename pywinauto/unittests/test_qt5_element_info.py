# -*- coding: utf-8 -*-
"""Tests for Qt5ElementInfo."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from pywinauto.qt.qt5_element_info import PIDNotFound, Qt5ElementInfo  # noqa: E402
from injectlib.api import InjectedBaseError, InjectedNotFoundError  # noqa: E402


qt_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\Qt5_samples")
qt_styles_app = os.path.join(qt_samples_folder, "styles.exe")
qt_interview_app = os.path.join(qt_samples_folder, "interview.exe")


def _set_timings():
    """Setup timings for Qt related tests."""
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt5ElementInfoTests(unittest.TestCase):

    """Unit tests for the Qt5ElementInfo class."""

    def setUp(self):
        """Start the Qt sample application."""
        _set_timings()

        self.app = Application(backend="qt5")
        self.app = self.app.start(qt_styles_app)
        time.sleep(2)

        self.root = self.app.window().find(timeout=10)
        self.ctrl = self.root.element_info

    def tearDown(self):
        """Close the application after tests."""
        self.app.kill()

    def test_hash(self):
        """Test element info hashing."""
        elements = {self.ctrl: "elem"}
        self.assertEqual(elements[self.ctrl], "elem")

    def test_top_window_properties(self):
        """Test top-level Qt window properties."""
        self.assertGreater(self.ctrl.control_id, 0)
        self.assertGreater(self.ctrl.runtime_id, 0)
        self.assertEqual(self.ctrl.process_id, self.app.process)
        self.assertEqual(self.ctrl.pid, self.app.process)
        self.assertEqual(self.ctrl.name, "Styles")
        self.assertEqual(self.ctrl.class_name, "WidgetGallery")
        self.assertEqual(self.ctrl.control_type, "Window")
        self.assertEqual(self.ctrl.framework_id, "Qt")
        self.assertEqual(self.ctrl.auto_id, "")
        self.assertIsNone(self.ctrl.handle)
        self.assertTrue(self.ctrl.enabled)
        self.assertTrue(self.ctrl.visible)

    def test_synthetic_desktop_root_properties(self):
        """Test synthetic Qt desktop root properties."""
        desktop_root = Qt5ElementInfo()

        self.assertIsNone(desktop_root.control_id)
        self.assertIsNone(desktop_root.runtime_id)
        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(desktop_root.name, "--root--")
        self.assertEqual(desktop_root.class_name, "Qt5Desktop")
        self.assertEqual(desktop_root.control_type, "Desktop")
        self.assertEqual(desktop_root.framework_id, "Qt")
        self.assertEqual(desktop_root.auto_id, "Qt5Desktop")
        self.assertEqual(desktop_root.automation_id, "Qt5Desktop")
        self.assertIsNone(desktop_root.handle)
        self.assertIsNone(desktop_root.parent)
        self.assertEqual(desktop_root.value, "")
        self.assertEqual(desktop_root.rich_text, "--root--")

    def test_pid_not_found(self):
        """Test Qt element creation without a required target process id."""
        self.assertRaises(PIDNotFound, Qt5ElementInfo, 1)

    def test_children(self):
        """Test immediate children of the top-level Qt window."""
        children = self.ctrl.children()
        self.assertGreater(len(children), 5)
        self.assertEqual(children[0].name, "&Style:")
        self.assertEqual(children[0].class_name, "QLabel")
        self.assertEqual(children[0].control_type, "Text")

    def test_children_generator(self):
        """Test whether children generator iterates over correct elements."""
        children = [child for child in self.ctrl.iter_children()]
        self.assertSequenceEqual(self.ctrl.children(), children)

    def test_parent(self):
        """Test getting a parent of a Qt element."""
        pane = self.ctrl.children()[0]
        self.assertEqual(pane.parent, self.ctrl)
        self.assertIsNone(self.ctrl.parent)

    def test_default_depth_descendants(self):
        """Test descendants with default depth."""
        self.assertEqual(len(self.ctrl.descendants(depth=None)),
                         len(self.ctrl.descendants()))

    def test_depth_level_one_descendants(self):
        """Test descendants with depth=1 equal direct children."""
        self.assertSequenceEqual(self.ctrl.descendants(depth=1),
                                 self.ctrl.children())

    def test_depth_level_two_descendants(self):
        """Test descendants with a bounded depth."""
        descendants = self.ctrl.children()
        level_two_children = []
        for element in descendants:
            level_two_children.extend(element.children())
        descendants.extend(level_two_children)

        self.assertEqual(len(self.ctrl.descendants(depth=2)), len(descendants))

    def test_invalid_depth_descendants(self):
        """Test whether an invalid descendants depth raises exception."""
        self.assertRaises(Exception, self.ctrl.descendants, depth="qwerty")

    def test_descendants_generator(self):
        """Test whether descendant generator iterates over correct elements."""
        descendants = [desc for desc in self.ctrl.iter_descendants(depth=2)]
        self.assertSequenceEqual(self.ctrl.descendants(depth=2), descendants)

    def test_find_children_by_criteria(self):
        """Test Qt element criteria filtering."""
        combos = self.ctrl.children(control_type="ComboBox")
        self.assertEqual(len(combos), 1)
        self.assertEqual(combos[0].name, "NorwegianWood")

        panes = self.ctrl.children(control_type="GroupBox")
        self.assertEqual(len(panes), 3)
        self.assertEqual([pane.name for pane in panes],
                         ["Group 1", "Group 2", "Group 3"])
        self.assertEqual(panes[0].class_name, "QGroupBox")

        group = self.root.by(name="Group 1",
                             control_type="GroupBox").find(timeout=10)
        self.assertEqual(group.element_info.class_name, "QGroupBox")
        self.assertEqual(group.element_info.name, "Group 1")
        self.assertEqual(group.element_info.value, "Group 1")
        self.assertEqual(group.element_info.rich_text, "Group 1")

        edits = self.ctrl.descendants(control_type="Edit", class_name="QLineEdit")
        self.assertEqual(len(edits), 3)

    def test_desktop_finds_top_window(self):
        """Test Qt root finds window through win32 top-level search."""
        desktop_root = Qt5ElementInfo()

        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(desktop_root.control_type, "Desktop")
        self.assertEqual(desktop_root.children(), [])

        children = desktop_root.children(name="Styles")
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].process_id, self.app.process)
        self.assertEqual(children[0].name, "Styles")
        self.assertEqual(children[0].class_name, "WidgetGallery")
        self.assertEqual(children[0].control_type, "Window")
        self.assertIsNone(children[0].handle)

    def test_desktop_pid_for_children(self):
        """Test searching for desktop children with a specified process id."""
        desktop_root = Qt5ElementInfo()

        children = desktop_root.children(process=self.app.process)
        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].process_id, self.app.process)
        self.assertEqual(children[0].name, "Styles")
        self.assertEqual(children[0].class_name, "WidgetGallery")
        self.assertEqual(children[0].control_type, "Window")

    def test_native_property_missing(self):
        """Test missing native Qt property handling."""
        combo = self.root.by(control_type="ComboBox").find(timeout=10)

        self.assertIsNone(combo.element_info.get_native_property("__missing__"))
        self.assertRaises(InjectedNotFoundError,
                          combo.element_info.get_native_property,
                          "__missing__",
                          error_if_not_exists=True)

    def test_rich_text(self):
        """Test Qt element rich text fallback rules."""
        edit = self.root.by(control_type="Edit",
                            class_name="QLineEdit",
                            name="s3cRe7").find(timeout=10)
        combo = self.root.by(control_type="ComboBox").find(timeout=10)

        self.assertEqual(edit.element_info.rich_text, "s3cRe7")
        self.assertEqual(combo.element_info.rich_text, "NorwegianWood")
        self.assertEqual(self.ctrl.rich_text, "Styles")

    def test_active_element(self):
        """Test getting focused Qt element."""
        combo = self.root.by(control_type="ComboBox").find(timeout=10)
        combo.set_focus()

        active = self.ctrl.get_active(self.app.process)
        self.assertEqual(active, combo.element_info)

    def test_expanded_combo_popup_is_child_not_root(self):
        """Test expanded combo popup remains a child and not a top-level root."""
        combo = self.root.by(control_type="ComboBox").find(timeout=10)
        combo.expand()
        time.sleep(1)

        children = [
            child for child in combo.element_info.children()
            if child.class_name == "QComboBoxPrivateContainer"
        ]
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].parent, combo.element_info)

        desktop_root = Qt5ElementInfo()
        roots = desktop_root.children(process=self.app.process)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].name, "Styles")
        self.assertEqual(roots[0].class_name, "WidgetGallery")
        self.assertNotIn("QComboBoxPrivateContainer",
                         [root.class_name for root in roots])


class Qt5InterviewElementInfoTests(unittest.TestCase):

    """Unit tests for Qt5ElementInfo with the Qt interview sample."""

    def setUp(self):
        """Start the Qt interview sample application."""
        _set_timings()

        self.app = Application(backend="qt5")
        self.app = self.app.start(qt_interview_app)
        time.sleep(2)

        self.root = self.app.window().find(timeout=10)

    def tearDown(self):
        """Close the application after tests."""
        self.app.kill()

    def test_tree_expand_collapse_specific_item_path(self):
        """Test direct tree item path expand/collapse calls."""
        tree = self.root.by(control_type="Tree").find(timeout=10).element_info

        self.assertTrue(tree.is_collapsed((0,)))
        self.assertEqual(tree.item_text((0,)), "Item 0:0")
        self.assertEqual(tree.item_text(r"\Item 0:0"), "Item 0:0")
        tree.expand((0,))
        self.assertTrue(tree.is_expanded((0,)))
        tree.collapse((0,))
        self.assertTrue(tree.is_collapsed((0,)))

        tree.expand(r"\Item 0:0")
        self.assertTrue(tree.is_expanded(r"\Item 0:0"))
        tree.collapse(r"\Item 0:0")
        self.assertTrue(tree.is_collapsed(r"\Item 0:0"))
        self.assertRaises(InjectedBaseError, tree.expand, r"\__missing__")


if __name__ == "__main__":
    unittest.main()
