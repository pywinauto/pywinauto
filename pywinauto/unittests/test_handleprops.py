# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2010 Mark Mc Mahon
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

"Tests for handleprops.py"

__revision__ = "$Revision: 234 $"

import unittest

import os
import sys
sys.path.append(".")
from pywinauto.handleprops import children, classname, clientrect, contexthelpid, \
    controlid, dumpwindow, exstyle, font, has_exstyle, has_style, is64bitprocess, \
    is_toplevel_window, isenabled, isunicode, isvisible, iswindow, parent, processid, \
    rectangle, style, text, userdata
from pywinauto.application import Application
from pywinauto import six
from pywinauto.sysinfo import is_x64_OS, is_x64_Python
from pywinauto import backend


class HandlepropsTestCases(unittest.TestCase):
    "Unit tests for the handleprops module"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start("notepad")
        self.dlghandle = self.app.UntitledNotepad.handle
        self.edit_handle = self.app.UntitledNotepad.Edit.handle

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.SendMessage(win32defines.WM_CLOSE)
        #self.app.UntitledNotepad.MenuSelect("File->Exit")
        self.app.kill_()

    def test_text(self):
        "Make sure the text method returns correct result"
        self.assertEquals("Untitled - Notepad", text(self.dlghandle))
        self.assertEquals("", text(self.edit_handle))


    def test_classname(self):
        "Make sure the classname method returns correct result"
        self.assertEquals("Notepad", classname(self.dlghandle))
        self.assertEquals("Edit", classname(self.edit_handle))

    def test_parent(self):
        "Make sure the parent method returns correct result"
        self.assertEquals(0, parent(self.dlghandle))
        self.assertEquals(self.dlghandle, parent(self.edit_handle))

    def test_style(self):
        "Make sure the style method returns correct result"
        self.assertEquals(0x14cf0000, style(self.dlghandle))
        # will be 0x50300104 if wordwrap is on and 0x50200104 if off
        self.assertTrue(
            (0x50200104, 0x50300104).__contains__,
            style(self.edit_handle),)

    def test_exstyle(self):
        "Make sure the exstyle method returns correct result"
        self.assertEquals(0x110, exstyle(self.dlghandle))
        self.assertEquals(0x200, exstyle(self.edit_handle))

    def test_controlid(self):
        "Make sure the controlid method returns correct result"
        #self.assertEquals(0, controlid(self.dlghandle))
        self.assertEquals(15, controlid(self.edit_handle))

    def test_userdata(self):
        "Make sure the userdata method returns correct result"
        self.assertEquals(0, userdata(self.dlghandle))
        self.assertEquals(0, userdata(self.edit_handle))

    def test_contexthelpid(self):
        "Make sure the contexthelpid method returns correct result"
        self.assertEquals(0, contexthelpid(self.dlghandle))
        self.assertEquals(0, contexthelpid(self.edit_handle))

    def test_iswindow(self):
        "Make sure the iswindow method returns correct result"
        self.assertEquals(True, iswindow(self.dlghandle))
        self.assertEquals(True, iswindow(self.edit_handle))

        self.assertEquals(False, iswindow(1))

    def test_isvisible(self):
        "Make sure the isvisible method returns correct result"
        self.assertEquals(True, isvisible(self.dlghandle))
        self.assertEquals(True, isvisible(self.edit_handle))

        # need to check something invisible
        #self.assertEquals(False, isvisible(self.edit_handle))

    def test_isunicode(self):
        "Make sure the isunicode method returns correct result"
        self.assertEquals(True, isunicode(self.dlghandle))
        self.assertEquals(True, isunicode(self.edit_handle))

        # need to check something not unicode
        #self.assertEquals(False, isunicode(self.edit_handle))


    def test_isenabled(self):
        "Make sure the isenabled method returns correct result"
        self.assertEquals(True, isenabled(self.dlghandle))
        self.assertEquals(True, isenabled(self.edit_handle))

        self.app.UntitledNotepad.MenuSelect("Help->About Notepad")
        self.app.AboutNotepad.Wait('ready')
        self.assertEquals(False, isenabled(self.dlghandle))
        self.app.AboutNotepad.OK.CloseClick()

        self.app.UntitledNotepad.MenuSelect("Edit->Replace")
        self.assertEquals(
            False,
            isenabled(
                self.app.Replace.ChildWindow(
                    title_re = "Replace.*",
                    class_name = "Button",
                    enabled_only = False).handle))
        self.app.Replace.Cancel.Click()

    def test_clientrect(self):
        "Make sure clientrect() function works"
        self.assertEquals(0, clientrect(self.dlghandle).left)
        self.assertEquals(0, clientrect(self.edit_handle).left)

        self.assertEquals(0, clientrect(self.dlghandle).top)
        self.assertEquals(0, clientrect(self.edit_handle).top)

        self.assertEquals(True,
            rectangle(self.dlghandle).right > clientrect(self.dlghandle).right)
        self.assertEquals(True,
            rectangle(self.edit_handle).right > clientrect(self.edit_handle).right)

        self.assertEquals(True,
            rectangle(self.dlghandle).bottom > clientrect(self.dlghandle).bottom)
        self.assertEquals(True,
            rectangle(self.edit_handle).bottom > clientrect(self.edit_handle).bottom)



    def test_rectangle(self):
        "Make sure rectangle() function works"
        dlgrect = rectangle(self.dlghandle)
        self.assertEquals(True, dlgrect.left < dlgrect.right)
        self.assertEquals(True, dlgrect.top < dlgrect.bottom)

        editrect = rectangle(self.edit_handle)
        self.assertEquals(True, editrect.left < editrect.right)
        self.assertEquals(True, editrect.top < editrect.bottom)

    def test_font(self):
        "Make sure font() function works"
        dlgfont = font(self.dlghandle)
        self.assertEquals(True, isinstance(dlgfont.lfFaceName, six.string_types))

        editfont = font(self.edit_handle)
        self.assertEquals(True, isinstance(editfont.lfFaceName, six.string_types))


    def test_processid(self):
        "Make sure processid() function works"
        self.assertEquals(self.app.process, processid(self.dlghandle))
        self.assertEquals(self.app.process, processid(self.edit_handle))

    def test_children(self):
        "Make sure the children method returns correct result"
        self.assertEquals(2,  len(children(self.dlghandle)))
        self.assertEquals([], children(self.edit_handle))

    def test_has_style(self):
        "Make sure the has_style method returns correct result"
        self.assertEquals(True,  has_style(self.dlghandle, 0xf0000))
        self.assertEquals(True, has_style(self.edit_handle, 0x4))

        self.assertEquals(False,  has_style(self.dlghandle, 4))
        self.assertEquals(False, has_style(self.edit_handle, 1))


    def test_has_exstyle(self):
        "Make sure the has_exstyle method returns correct result"
        self.assertEquals(True,  has_exstyle(self.dlghandle, 0x10))
        self.assertEquals(True, has_exstyle(self.edit_handle, 0x200))

        self.assertEquals(False,  has_exstyle(self.dlghandle, 4))
        self.assertEquals(False, has_exstyle(self.edit_handle, 0x10))

    def test_is_toplevel_window(self):
        "Make sure is_toplevel_window() function works"

        self.assertEquals(True, is_toplevel_window(self.dlghandle))
        self.assertEquals(False, is_toplevel_window(self.edit_handle))

        self.app.UntitledNotepad.MenuSelect("Edit->Replace")
        self.assertEquals(True, is_toplevel_window(self.app.Replace.handle))
        self.assertEquals(False, is_toplevel_window(self.app.Replace.Cancel.handle))
        self.app.Replace.Cancel.Click()

#    def test_friendlyclassname(self):
#        "Make sure the friendly class is returned correctly"
#        self.assertEquals("Notepad", friendlyclassname(self.dlghandle))
#        self.assertEquals("Edit", friendlyclassname(self.edit_handle))
#
#        self.app.UntitledNotepad.MenuSelect("Edit->Replace")
#        self.assertEquals("Dialog", friendlyclassname(self.app.Replace.handle))
#        self.app.Replace.Cancel.Click()
    def test_is64bitprocess(self):
        "Make sure a 64-bit process detection returns correct results"
 
        if is_x64_OS():
            # Test a 32-bit app running on x64
            expected_is64bit = False
            if is_x64_Python():
                exe32bit = os.path.join(os.path.dirname(__file__),
                              r"..\..\apps\MFC_samples\RowList.exe")
                app = Application().start(exe32bit, timeout=20)
                pid = app.RowListSampleApplication.process_id()
                res_is64bit = is64bitprocess(pid)
                try:
                    self.assertEquals(expected_is64bit, res_is64bit)
                finally:
                    # make sure to close an additional app we have opened
                    app.kill_()

                # setup expected for a 64-bit app on x64
                expected_is64bit = True
        else:
            # setup expected for a 32-bit app on x86
            expected_is64bit = False

        # test native Notepad app
        res_is64bit = is64bitprocess(self.app.UntitledNotepad.process_id())
        self.assertEquals(expected_is64bit, res_is64bit)

    def test_dumpwindow(self):
        "Make sure dumpwindow() function works"
        dlgdump = dumpwindow(self.dlghandle)

        for key, item in dlgdump.items():
            self.assertEquals(item, globals()[key](self.dlghandle))

        editdump = dumpwindow(self.edit_handle)

        for key, item in editdump.items():
            self.assertEquals(item, globals()[key](self.edit_handle))




if __name__ == "__main__":
    #_unittests()

    unittest.main()


