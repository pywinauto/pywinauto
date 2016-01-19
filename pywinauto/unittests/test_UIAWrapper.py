from __future__ import print_function
from __future__ import unicode_literals

"Tests for UIAWrapper"

import time
#import pprint
#import pdb
#import warnings

import ctypes
import locale
import re

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python, is_x64_OS, UIA_support
if UIA_support:
    from pywinauto.controls.UIAWrapper import UIAWrapper
#from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import Timings, TimeoutError
#from pywinauto import clipboard
from pywinauto import backend

import unittest

wpf_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    wpf_samples_folder = os.path.join(wpf_samples_folder, 'x64')

if UIA_support:
    # Set backend to UIA

    class UIAWrapperTests(unittest.TestCase):
        "Unit tests for the UIAWrapper class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""
            backend.activate("uia")

            # start the application
            self.app = Application().Start(os.path.join(wpf_samples_folder, u"WpfApplication1.exe"))

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.Button.elementInfo)
            self.edit = UIAWrapper(self.dlg.Edit.elementInfo)
            self.label = UIAWrapper(self.dlg.TestLabel.elementInfo)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassName(self):
            "Test getting the friendly classname of the dialog"
            self.assertEqual(self.button.FriendlyClassName(), "Button")

        def testClass(self):
            "Test getting the classname of the dialog"
            self.assertEqual(self.button.Class(), "Button")

        def testWindowText(self):
            "Test getting the window Text of the dialog"
            self.assertEqual(self.label.WindowText(), u"TestLable")

        def testControlID(self):
            self.assertEqual(self.button.ControlID(), None)

        def testIsVisible(self):
            self.assertEqual(self.button.IsVisible(), True)

        def testIsEnabled(self):
            self.assertEqual(self.button.IsEnabled(), True)

        def ProcessID(self):
            self.assertEqual(self.button.ProcessID(), self.dlg.ProcessID())
            self.assertNotEqual(self.button.ProcessID(), 0)

        def testIsDialog(self):
            self.assertEqual(self.button.IsDialog(), False)

        def testParent(self):
            self.assertEqual(self.button.Parent(), self.dlg.WrapperObject())

        def testTopLevelParent(self):
            self.assertEqual(self.button.TopLevelParent(), self.dlg.WrapperObject())

        def testTexts(self):
            self.assertEqual(self.dlg.Texts(), ['WPF Sample Application'])

        def testChildren(self):
            self.assertEqual(len(self.button.Children()), 1)
            self.assertEqual(self.button.Children()[0].Class(), "TextBlock")

        def testIsChild(self):
            self.assertEqual(self.button.IsChild(self.dlg.WrapperObject()), True)

        def testEquals(self):
            self.assertNotEqual(self.button, self.dlg.WrapperObject())
            self.assertEqual(self.button, self.button.elementInfo)
            self.assertEqual(self.button, self.button)

        #def testVerifyActionable(self):
        #    self.assertRaises()

        #def testVerifyEnabled(self):
        #    self.assertRaises()

        #def testVerifyVisible(self):
        #    self.assertRaises()

        def testIsKeyboardFocusable(self):
            self.assertEqual(self.button.IsKeyboardFocusable(), True)
            self.assertEqual(self.edit.IsKeyboardFocusable(), True)
            self.assertEqual(self.label.IsKeyboardFocusable(), False)

        def testHasKeyboardFocus(self):
            self.edit.SetFocus()
            self.assertEqual(self.edit.HasKeyboardFocus(), True)

        def testSetFocus(self):
            self.edit.SetFocus()
            self.assertEqual(self.edit.HasKeyboardFocus(), True)

        def testTypeKeys(self):
            self.edit.TypeKeys("testTypeKeys")
            self.assertEqual(self.edit.WindowText(), "testTypeKeys")

    class UIAWrapperMouseTests(unittest.TestCase):
        "Unit tests for mouse actions of the UIAWrapper class"

        def setUp(self):
            """
            Start the application set some data and ensure the application
            is in the state we want it.
            """
            backend.activate("uia")

            # start the application
            self.app = Application().Start(os.path.join(wpf_samples_folder, u"WpfApplication1.exe"))

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.Button.elementInfo)
            self.label = self.dlg.TestLabel.WrapperObject()

        def tearDown(self):
            "Close the application after tests"

            # close the application
            try:
                self.dlg.Close(0.5)
            except Exception: # TimeoutError:
                pass
            finally:
                self.app.kill_()

        #def testClick(self):
        #    pass

        def testClickInput(self):
            time.sleep(0.5)
            self.button.ClickInput()
            self.assertEqual(self.label.WindowText(), "LeftClick")

        #def testDoubleClick(self):
        #    pass

        def testDoubleClickInput(self):
            self.dlg.SetFocus()
            time.sleep(2.0)
            Timings.after_clickinput_wait = 0.001
            self.button.DoubleClickInput()
            time.sleep(0.5)
            self.assertEqual(self.label.WindowText(), "DoubleClick")

        #def testRightClick(self):
        #    pass

        def testRightClickInput(self):
            time.sleep(0.5)
            self.button.RightClickInput()
            self.assertEqual(self.label.WindowText(), "RightClick")

        #def testPressMoveRelease(self):
        #    pass

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
