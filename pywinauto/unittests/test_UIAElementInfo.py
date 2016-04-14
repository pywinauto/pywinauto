import unittest
from pywinauto.application import Application
from pywinauto.handleprops import processid 
from pywinauto.sysinfo import is_x64_Python, is_x64_OS, UIA_support

if UIA_support:
    from pywinauto.UIAElementInfo import UIAElementInfo
    from pywinauto import backend


if UIA_support:
    class UIAElementInfoTests(unittest.TestCase):
        "Unit tests for the UIElementInfo class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            # TODO: re-write the whole test
            self.app = Application(backend="native")
            if is_x64_Python() or not is_x64_OS():
                self.app.start(r"C:\Windows\System32\calc.exe")
            else:
                self.app.start(r"C:\Windows\SysWOW64\calc.exe")
            
            self.dlg = self.app.Calculator
            self.handle = self.dlg.handle
            self.dlg.MenuSelect('View->Scientific\tAlt+2')
            self.ctrl = UIAElementInfo(self.dlg.handle)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testProcessId(self):
            self.assertEqual(self.ctrl.process_id, processid(self.handle))

        def testName(self):
            self.assertEqual(self.ctrl.name, "Calculator")

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
