import unittest
import os
from pywinauto.application import Application
from pywinauto.handleprops import processid 
from pywinauto.sysinfo import is_x64_Python, is_x64_OS, UIA_support

if UIA_support:
    from pywinauto.UIAElementInfo import UIAElementInfo
    from pywinauto import backend

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
mfc_app_1 = os.path.join(mfc_samples_folder, u"RowList.exe")

if UIA_support:
    class UIAElementInfoTests(unittest.TestCase):
        "Unit tests for the UIElementInfo class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            self.app = Application(backend="native")
            self.app = self.app.Start(mfc_app_1)

            self.dlg = self.app.RowListSampleApplication
            self.handle = self.dlg.handle
            self.dlg.MenuSelect('View->Large Icons')
            self.ctrl = UIAElementInfo(self.dlg.handle)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testProcessId(self):
            self.assertEqual(self.ctrl.process_id, processid(self.handle))

        def testName(self):
            self.assertEqual(self.ctrl.name, "RowList Sample Application")

        def testHandle(self):
            self.assertEqual(self.ctrl.handle, self.handle)

        def testEnabled(self):
            self.assertEqual(self.ctrl.enabled, True)

        def testVisible(self):
            self.assertEqual(self.ctrl.visible, True)

        def testChildren(self):
            self.assertEqual(len(self.ctrl.children()), 3)

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
