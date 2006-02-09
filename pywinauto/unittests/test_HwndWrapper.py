# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"Tests for HwndWrapper"

__revision__ = "$Revision: 234 $"

try:
    from pywinauto.controls.HwndWrapper import *
except ImportError:
    # allow it to be imported in a dev environment
    import sys
    
    pywinauto_imp = "\\".join(__file__.split('\\')[:-3])    
    print "sdfdsf", pywinauto_imp
    sys.path.append(pywinauto_imp)
    from pywinauto.controls.HwndWrapper import *

import unittest

class HwndWrapperTests(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()

        import os.path
        path = os.path.split(__file__)[0]

        test_file = os.path.join(path, "test.txt")

        self.test_data = open(test_file, "r").read()
        # remove the BOM if it exists
        self.test_data = self.test_data.replace("\xef\xbb\xbf", "")
        self.test_data = self.test_data.decode('utf-8')

        app.start_("Notepad.exe " + test_file)

        self.app = app
        self.dlg = app.UntitledNotepad
        #self.ctrl = self.dlg.Edit.ctrl_()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.TypeKeys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.MenuSelect("File->Exit")

        if self.app.Notepad.No.Exists():
            self.app.Notepad.No.Click()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.Text(), "Untitled - Notepad")

    def testText(self):
        "Test getting the window Text of the dialog"
        self.assertEquals(self.dlg.Text(), "test.txt - Notepad")

    def testClass(self):
        "Test getting the classname of the dialog"
        self.assertEquals(self.dlg.Class(), "Notepad")

    def testFriendlyClassName(self):
        "Test getting the friendly classname of the dialog"
        self.assertEquals(self.dlg.FriendlyClassName(), "Notepad")

    def testRectangle(self):
        "Test getting the rectangle of the dialog"
        rect = self.dlg.Rectangle()
        self.assertNotEqual(rect.top, None)
        self.assertNotEqual(rect.left, None)
        self.assertNotEqual(rect.bottom, None)
        self.assertNotEqual(rect.right, None)

    def testMoveWindow_same(self):
        "Test calling movewindow without any parameters"
        prevRect = self.dlg.Rectangle()
        self.dlg.MoveWindow()
        self.assertEquals(prevRect, self.dlg.Rectangle())

    def testMoveWindow(self):
        "Test moving the window"
        #prevRect = self.dlg.Rectangle()
        self.dlg.MoveWindow(150, 100, 250, 200)
        self.assertEquals(
            self.dlg.Rectangle(),
            win32structures.RECT(150, 100, 150+250, 100+200))

    def testGetProperties(self):
        "Test getting the properties for the control"
        props  = self.dlg.GetProperties()
        
        self.assertEquals(
            self.dlg.FriendlyClassName(), props['FriendlyClassName'])
        
        self.assertEquals(
            self.dlg.Texts(), props['Texts'])
        
        for prop_name in props:
            self.assertEquals(getattr(self.dlg, prop_name)(), props[prop_name])



##====================================================================
#def _unittests():
#    "do some basic testing"
#    from pywinauto.findwindows import find_windows
#    import sys
#
#    if len(sys.argv) < 2:
#        handle = win32functions.GetDesktopWindow()
#    else:
#        try:
#            handle = int(eval(sys.argv[1]))
#
#        except ValueError:
#
#            handle = find_windows(
#                title_re = "^" + sys.argv[1],
#                class_name = "#32770",
#                visible_only = False)
#
#            if not handle:
#                print "dialog not found"
#                sys.exit()
#
#    props = GetDialogPropsFromHandle(handle)
#    print len(props)
#    #pprint(GetDialogPropsFromHandle(handle))


if __name__ == "__main__":
    unittest.main()

