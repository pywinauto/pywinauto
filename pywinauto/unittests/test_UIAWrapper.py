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
    import pywinauto.uia_defines as uia_defs
    from pywinauto.controls.UIAWrapper import UIAWrapper
#from pywinauto.findwindows import ElementNotFoundError
#from pywinauto import clipboard
from pywinauto import backend
from pywinauto.timings import Timings, TimeoutError
Timings.Defaults()

import unittest

wpf_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    wpf_samples_folder = os.path.join(wpf_samples_folder, 'x64')
wpf_app_1 = os.path.join(wpf_samples_folder, u"WpfApplication1.exe")

if UIA_support:
    # Set backend to UIA

    class UIAWrapperTests(unittest.TestCase):
        "Unit tests for the UIAWrapper class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            # start the application
            self.app = Application(backend = 'uia')
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.Button.element_info)
            self.edit = UIAWrapper(self.dlg.Edit.element_info)
            self.label = UIAWrapper(self.dlg.TestLabel.element_info)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassName(self):
            "Test getting the friendly classname of the dialog"
            self.assertEqual(self.button.friendly_class_name(), "Button")

        def testClass(self):
            "Test getting the classname of the dialog"
            self.assertEqual(self.button.class_name(), "Button")

        def testWindowText(self):
            "Test getting the window Text of the dialog"
            self.assertEqual(self.label.window_text(), u"TestLable")

        def testControlID(self):
            self.assertEqual(self.button.control_id(), None)

        def testIsVisible(self):
            self.assertEqual(self.button.is_visible(), True)

        def testIsEnabled(self):
            self.assertEqual(self.button.is_enabled(), True)

        def testProcessID(self):
            self.assertEqual(self.button.process_id(), self.dlg.process_id())
            self.assertNotEqual(self.button.process_id(), 0)

        def testIsDialog(self):
            self.assertEqual(self.button.is_dialog(), False)

        def testParent(self):
            self.assertEqual(self.button.parent(), self.dlg.WrapperObject())

        def testTopLevelParent(self):
            self.assertEqual(self.button.top_level_parent(), self.dlg.WrapperObject())

        def testTexts(self):
            self.assertEqual(self.dlg.texts(), ['WPF Sample Application'])

        def testChildren(self):
            self.assertEqual(len(self.button.children()), 1)
            self.assertEqual(self.button.children()[0].class_name(), "TextBlock")

        def testIsChild(self):
            self.assertEqual(self.button.is_child(self.dlg.WrapperObject()), True)

        def testEquals(self):
            self.assertNotEqual(self.button, self.dlg.WrapperObject())
            self.assertEqual(self.button, self.button.element_info)
            self.assertEqual(self.button, self.button)

        #def testVerifyActionable(self):
        #    self.assertRaises()

        #def testVerifyEnabled(self):
        #    self.assertRaises()

        #def testVerifyVisible(self):
        #    self.assertRaises()

        def testIsKeyboardFocusable(self):
            self.assertEqual(self.button.is_keyboard_focusable(), True)
            self.assertEqual(self.edit.is_keyboard_focusable(), True)
            self.assertEqual(self.label.is_keyboard_focusable(), False)

        def testHasKeyboardFocus(self):
            self.edit.set_focus()
            self.assertEqual(self.edit.has_keyboard_focus(), True)

        def testSetFocus(self):
            self.edit.set_focus()
            self.assertEqual(self.edit.has_keyboard_focus(), True)

        def testTypeKeys(self):
            self.edit.type_keys("testTypeKeys")
            self.assertEqual(self.edit.window_text(), "testTypeKeys")

        def testGetProperties(self):
            uia_props = {'class_name',
                         'friendly_class_name',
                         'texts',
                         'control_id',
                         'rectangle',
                         'is_visible',
                         'is_enabled',
                         'control_count',
                         'is_keyboard_focusable',
                         'has_keyboard_focus',
                         }
            props = set(self.edit.get_properties().keys())
            self.assertEquals(props, uia_props)

    class UIAWrapperMouseTests(unittest.TestCase):
        "Unit tests for mouse actions of the UIAWrapper class"

        def setUp(self):
            """
            Start the application set some data and ensure the application
            is in the state we want it.
            """

            self.app = Application(backend = 'uia')
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.Button.element_info)
            self.label = self.dlg.TestLabel.WrapperObject()

        def tearDown(self):
            "Close the application after tests"

            self.app.kill_()

        #def testClick(self):
        #    pass

        def testClickInput(self):
            time.sleep(0.5)
            self.button.click_input()
            self.assertEqual(self.label.window_text(), "LeftClick")

        #def testDoubleClick(self):
        #    pass

        def testDoubleClickInput(self):
            self.button.double_click_input()
            self.assertEqual(self.label.window_text(), "DoubleClick")

        #def testRightClick(self):
        #    pass

        def testRightClickInput(self):
            time.sleep(0.5)
            self.button.right_click_input()
            self.assertEqual(self.label.window_text(), "RightClick")

        #def testPressMoveRelease(self):
        #    pass

    class ButtonWrapperTests(unittest.TestCase):
        "Unit tests for the ButtonWrapper class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            self.app = Application(backend = 'uia')
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = self.dlg.Button

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassName(self):
            """
            Test getting the friendly class name of a check box control 
            on the dialog
            """
            friendly_name = self.dlg.CheckBox.FriendlyClassName()
            self.assertEqual(friendly_name, "CheckBox")

        def testCheckBox(self):
            """"
            Test the toggle and the toggle_state methods 
            for the check box control
            """
            
            # Get a current state of the check box control
            cur_state = self.dlg.CheckBox.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_off)
            
            # Toggle the next state
            self.dlg.CheckBox.toggle()
            
            # Get a new state of the check box control
            cur_state = self.dlg.CheckBox.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_on)

        def testButtonClick(self):
            "Test the click method for the Button control"

            #TODO: verify click
            self.dlg.Button.click()

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
