import unittest
import os
from pywinauto.application import Application
from pywinauto.handleprops import processid 
from pywinauto.sysinfo import is_x64_Python, is_x64_OS, UIA_support

if UIA_support:
    from pywinauto.UIAElementInfo import UIAElementInfo
    from pywinauto import backend

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
wpf_app_1 = os.path.join(mfc_samples_folder, u"WpfApplication1.exe")

if UIA_support:
    class UIAElementInfoTests(unittest.TestCase):
        "Unit tests for the UIElementInfo class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            self.app = Application(backend="native")
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.handle = self.dlg.handle
            self.ctrl = UIAElementInfo(self.dlg.handle)

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
            self.assertEqual(len(self.ctrl.children()), 18)

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
