# -*- coding: utf-8 -*-
"""Linux element info tests for the Qt6 backend."""

from __future__ import unicode_literals

import os
import sys
import time
import unittest


if sys.platform == "win32":
    raise unittest.SkipTest("Linux Qt tests require Linux")

sys.path.append(".")
from pywinauto import Application, Desktop  # noqa: E402
from pywinauto.qt.qt6_element_info import PIDNotFound, Qt6ElementInfo  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from injectlib.api import InjectedNotFoundError  # noqa: E402


qt_samples_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "apps", "Qt6_samples_linux"))
qt_gallery_app = os.path.join(qt_samples_folder, "gallery")


def _set_timings():
    Timings.defaults()
    Timings.window_find_timeout = 20


class Qt6ElementInfoLinuxTests(unittest.TestCase):
    """Element info tests for the Qt6 gallery example."""

    def setUp(self):
        _set_timings()
        self.app = Application(backend="qt6").start(qt_gallery_app)
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
        self.assertTrue(self.ctrl.name.startswith("Widget Gallery Qt "))
        self.assertEqual(self.ctrl.class_name, "WidgetGallery")
        self.assertEqual(self.ctrl.control_type, "Window")
        self.assertEqual(self.ctrl.framework_id, "Qt")
        self.assertIsNone(self.ctrl.handle)
        self.assertTrue(self.ctrl.enabled)
        self.assertTrue(self.ctrl.visible)

        desktop_root = Qt6ElementInfo()
        self.assertIsNone(desktop_root.process_id)
        self.assertEqual(desktop_root.class_name, "Qt6Desktop")
        self.assertEqual(desktop_root.control_type, "Desktop")
        self.assertEqual(desktop_root.auto_id, "Qt6Desktop")
        self.assertRaises(PIDNotFound, Qt6ElementInfo, 1)

    def test_children_descendants_and_discovery(self):
        children = self.ctrl.children()
        self.assertGreater(len(children), 5)
        self.assertEqual(children[0].name, "&Style:")
        self.assertEqual(children[0].class_name, "QLabel")
        self.assertEqual(children[0].control_type, "Text")
        self.assertTrue(self.ctrl.children(control_type="ComboBox"))
        self.assertTrue(self.ctrl.children(control_type="GroupBox"))
        self.assertTrue(self.ctrl.descendants(control_type="Table", class_name="QTableWidget"))

        by_pid = Qt6ElementInfo().children(process=self.app.process)
        self.assertEqual(len(by_pid), 1)
        self.assertEqual(by_pid[0].process_id, self.app.process)

        windows = Desktop(backend="qt6").windows(name=self.ctrl.name)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0].element_info.process_id, self.app.process)

    def test_native_properties_and_focus(self):
        combo = self.dlg.by(control_type="ComboBox").find(timeout=10)
        self.assertIsNone(combo.element_info.get_native_property("__missing__"))
        self.assertRaises(InjectedNotFoundError, combo.element_info.get_native_property,
                          "__missing__", error_if_not_exists=True)
        combo.set_focus()
        self.assertEqual(self.ctrl.get_active(self.app.process), combo.element_info)


if __name__ == "__main__":
    unittest.main()
