# -*- coding: utf-8 -*-
"""Linux element info tests for the Qt5 backend."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest


if sys.platform == "win32":
    raise unittest.SkipTest("Linux Qt tests require Linux")

sys.path.append(".")
from pywinauto import Application, Desktop  # noqa: E402
from pywinauto.qt.qt5_element_info import PIDNotFound, Qt5ElementInfo  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from injectlib.api import InjectedNotFoundError  # noqa: E402


qt_samples_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "apps", "Qt5_samples_linux"))
qt_styles_app = os.path.join(qt_samples_folder, "styles")


def _set_timings():
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt5ElementInfoLinuxTests(unittest.TestCase):
    """Element info tests for the Qt5 styles example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt5").start(qt_styles_app)
        time.sleep(2)
        self.dlg = self.app.window()
        self.root = self.dlg.find(timeout=15)
        self.ctrl = self.root.element_info

    def tearDown(self):
        self.app.kill()

    def test_top_window_and_desktop_root(self):
        self.assertGreater(self.ctrl.control_id, 0)
        self.assertGreater(self.ctrl.runtime_id, 0)
        self.assertEqual(self.ctrl.process_id, self.app.process)
        self.assertEqual(self.ctrl.name, "Styles")
        self.assertEqual(self.ctrl.class_name, "WidgetGallery")
        self.assertEqual(self.ctrl.control_type, "Window")
        self.assertEqual(self.ctrl.framework_id, "Qt")
        self.assertIsNone(self.ctrl.handle)
        self.assertTrue(self.ctrl.enabled)
        self.assertTrue(self.ctrl.visible)

        desktop_root = Qt5ElementInfo()
        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(desktop_root.name, "--root--")
        self.assertEqual(desktop_root.class_name, "Qt5Desktop")
        self.assertEqual(desktop_root.control_type, "Desktop")
        self.assertEqual(desktop_root.auto_id, "Qt5Desktop")
        self.assertRaises(PIDNotFound, Qt5ElementInfo, 1)

    def test_children_descendants_parent_and_criteria(self):
        children = self.ctrl.children()
        self.assertGreater(len(children), 5)
        self.assertEqual(children[0].name, "&Style:")
        self.assertEqual(children[0].class_name, "QLabel")
        self.assertEqual(children[0].control_type, "Text")
        self.assertSequenceEqual(self.ctrl.children(), list(self.ctrl.iter_children()))
        self.assertEqual(children[0].parent, self.ctrl)
        self.assertIsNone(self.ctrl.parent)
        self.assertSequenceEqual(self.ctrl.descendants(depth=1), children)
        self.assertEqual(len(self.ctrl.descendants(depth=None)), len(self.ctrl.descendants()))
        self.assertRaises(Exception, self.ctrl.descendants, depth="bad")

        combos = self.ctrl.children(control_type="ComboBox")
        self.assertEqual(len(combos), 1)
        self.assertEqual(combos[0].class_name, "QComboBox")
        groups = self.ctrl.children(control_type="GroupBox")
        self.assertEqual([group.name for group in groups], ["Group 1", "Group 2", "Group 3"])
        self.assertEqual(len(self.ctrl.descendants(control_type="Edit", class_name="QLineEdit")), 3)

    def test_desktop_discovery_by_atspi_and_explicit_pid(self):
        desktop_root = Qt5ElementInfo()
        self.assertEqual(desktop_root.children(), [])

        by_pid = desktop_root.children(process=self.app.process)
        self.assertEqual(len(by_pid), 1)
        self.assertEqual(by_pid[0].process_id, self.app.process)
        self.assertEqual(by_pid[0].name, "Styles")

        window = Desktop(backend="qt5").window(name="Styles").find()
        self.assertEqual(window.element_info.process_id, self.app.process)
        self.assertEqual(window.window_text(), "Styles")

    def test_native_properties_rich_text_and_active(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        edit = self.dlg.by(control_type="Edit", class_name="QLineEdit", name="s3cRe7").find(timeout=10)

        self.assertIsNone(combo.element_info.get_native_property("__missing__"))
        self.assertRaises(InjectedNotFoundError, combo.element_info.get_native_property,
                          "__missing__", error_if_not_exists=True)
        self.assertEqual(edit.element_info.rich_text, "s3cRe7")
        self.assertEqual(self.ctrl.rich_text, "Styles")

        combo.set_focus()
        self.assertEqual(self.ctrl.get_active(self.app.process), combo.element_info)


if __name__ == "__main__":
    unittest.main()
