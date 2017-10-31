import unittest
import os
import sys

sys.path.append(".")
from pywinauto.application import Application  # noqa: E402
from pywinauto.handleprops import processid  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.sysinfo import UIA_support  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402

if UIA_support:
    from pywinauto.uia_element_info import UIAElementInfo

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
wpf_app_1 = os.path.join(mfc_samples_folder, u"WpfApplication1.exe")

if UIA_support:
    class UIAElementInfoTests(unittest.TestCase):

        """Unit tests for the UIElementInfo class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            Timings.Slow()

            self.app = Application(backend="uia")
            self.app = self.app.start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.handle = self.dlg.handle
            self.ctrl = UIAElementInfo(self.handle)

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill_()

        def testProcessId(self):
            """Test process_id equals"""
            self.assertEqual(self.ctrl.process_id, processid(self.handle))

        def testName(self):
            """Test application name equals"""
            self.assertEqual(self.ctrl.name, "WPF Sample Application")

        def testHandle(self):
            """Test application handle equals"""
            self.assertEqual(self.ctrl.handle, self.handle)

        def testEnabled(self):
            """Test whether the element is enabled"""
            self.assertEqual(self.ctrl.enabled, True)

        def testVisible(self):
            """Test whether the element is visible"""
            self.assertEqual(self.ctrl.visible, True)

        def testChildren(self):
            """Test whether a list of only immediate children of the element is equal"""
            self.assertEqual(len(self.ctrl.children()), 5)

        def test_default_depth_descendants(self):
            """Test whether a list of descendants with default depth of the element is equal"""
            self.assertEqual(len(self.ctrl.descendants(depth=None)), len(self.ctrl.descendants()))

        def test_depth_level_one_descendants(self):
            """Test whether a list of descendants with depth=1 of the element is equal to children set"""
            self.assertEqual(len(self.ctrl.descendants(depth=1)), len(self.ctrl.children()))

        def test_depth_level_three_descendants(self):
            """Test whether a list of descendants with depth=3 of the element is equal"""
            descendants = self.ctrl.children()

            level_two_children = []
            for element in descendants:
                level_two_children.extend(element.children())
            descendants.extend(level_two_children)

            level_three_children = []
            for element in level_two_children:
                level_three_children.extend(element.children())
            descendants.extend(level_three_children)

            self.assertEqual(len(self.ctrl.descendants(depth=3)), len(descendants))

        def test_invalid_depth_descendants(self):
            """Test whether a list of descendants with invalid depth raises exception"""
            self.assertRaises(Exception, self.ctrl.descendants, depth='qwerty')

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
