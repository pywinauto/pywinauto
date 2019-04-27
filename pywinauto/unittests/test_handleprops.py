# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests for handleprops.py"""

import unittest
import six
import os
import sys
import warnings
sys.path.append(".")

from pywinauto import win32structures
from pywinauto.handleprops import children, classname, clientrect, contexthelpid, \
    controlid, dumpwindow, exstyle, font, has_exstyle, has_style, is64bitprocess, \
    is_toplevel_window, isenabled, isunicode, isvisible, iswindow, parent, processid, \
    rectangle, style, text, userdata, is64bitbinary
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_OS
from pywinauto.sysinfo import is_x64_Python
from pywinauto.timings import Timings


class HandlepropsTestCases(unittest.TestCase):

    """Unit tests for the handleprops module"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.defaults()
        self.app = Application().start("notepad")
        self.dlghandle = self.app.UntitledNotepad.handle
        self.edit_handle = self.app.UntitledNotepad.Edit.handle

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        #self.dlg.SendMessage(win32defines.WM_CLOSE)
        #self.app.UntitledNotepad.menu_select("File->Exit")
        self.app.kill()

    def test_text(self):
        """Make sure the text method returns correct result"""
        self.assertEqual("Untitled - Notepad", text(self.dlghandle))
        self.assertEqual("", text(self.edit_handle))
        self.assertEqual(None, text(sys.maxsize))
        self.assertEqual(None, text(None))


    def test_classname(self):
        """Make sure the classname method returns correct result"""
        self.assertEqual("Notepad", classname(self.dlghandle))
        self.assertEqual("Edit", classname(self.edit_handle))
        self.assertEqual("", classname(sys.maxsize))
        self.assertEqual(None, classname(None))

    def test_parent(self):
        """Make sure the parent method returns correct result"""
        self.assertEqual(None, parent(self.dlghandle))
        self.assertEqual(self.dlghandle, parent(self.edit_handle))
        self.assertEqual(None, parent(sys.maxsize))
        self.assertEqual(None, parent(None))

    def test_style(self):
        """Make sure the style method returns correct result"""
        self.assertEqual(0x14cf0000, style(self.dlghandle))
        # will be 0x50300104 if wordwrap is on and 0x50200104 if off
        self.assertTrue(
            (0x50200104, 0x50300104).__contains__,
            style(self.edit_handle),)
        self.assertEqual(0, style(sys.maxsize))
        self.assertEqual(0, style(None))

    def test_exstyle(self):
        """Make sure the exstyle method returns correct result"""
        self.assertEqual(0x110, exstyle(self.dlghandle))
        self.assertEqual(0x200, exstyle(self.edit_handle))
        self.assertEqual(0, exstyle(sys.maxsize))
        self.assertEqual(0, exstyle(None))

    def test_controlid(self):
        """Make sure the controlid method returns correct result"""
        #self.assertEqual(0, controlid(self.dlghandle))
        self.assertEqual(15, controlid(self.edit_handle))
        self.assertEqual(0, controlid(sys.maxsize))
        self.assertEqual(0, controlid(None))

    def test_userdata(self):
        """Make sure the userdata method returns correct result"""
        self.assertEqual(0, userdata(self.dlghandle))
        self.assertEqual(0, userdata(self.edit_handle))
        self.assertEqual(0, userdata(sys.maxsize))
        self.assertEqual(0, userdata(None))

    def test_contexthelpid(self):
        """Make sure the contexthelpid method returns correct result"""
        self.assertEqual(0, contexthelpid(self.dlghandle))
        self.assertEqual(0, contexthelpid(self.edit_handle))
        self.assertEqual(0, contexthelpid(sys.maxsize))
        self.assertEqual(0, contexthelpid(None))

    def test_iswindow(self):
        """Make sure the iswindow method returns correct result"""
        self.assertEqual(True, iswindow(self.dlghandle))
        self.assertEqual(True, iswindow(self.edit_handle))

        self.assertEqual(False, iswindow(1))
        self.assertEqual(False, iswindow(sys.maxsize))
        self.assertEqual(False, iswindow(None))

    def test_isvisible(self):
        """Make sure the isvisible method returns correct result"""
        self.assertEqual(True, isvisible(self.dlghandle))
        self.assertEqual(True, isvisible(self.edit_handle))
        self.assertEqual(False, isvisible(sys.maxsize))
        self.assertEqual(False, isvisible(None))
        # need to check something invisible
        #self.assertEqual(False, isvisible(self.edit_handle))

    def test_isunicode(self):
        """Make sure the isunicode method returns correct result"""
        self.assertEqual(True, isunicode(self.dlghandle))
        self.assertEqual(True, isunicode(self.edit_handle))
        self.assertEqual(False, isunicode(sys.maxsize))
        self.assertEqual(False, isunicode(None))

        # need to check something not unicode
        #self.assertEqual(False, isunicode(self.edit_handle))

    def test_isenabled(self):
        """Make sure the isenabled method returns correct result"""
        self.assertEqual(False, isenabled(sys.maxsize))
        self.assertEqual(False, isenabled(None))
        self.assertEqual(True, isenabled(self.dlghandle))
        self.assertEqual(True, isenabled(self.edit_handle))

        self.app.UntitledNotepad.menu_select("Help->About Notepad")
        self.app.AboutNotepad.wait('ready')
        self.assertEqual(False, isenabled(self.dlghandle))
        self.app.AboutNotepad.OK.close_click()

        self.app.UntitledNotepad.menu_select("Edit->Replace")
        self.assertEqual(
            False,
            isenabled(
                self.app.Replace.child_window(
                    title_re = "Replace.*",
                    class_name = "Button",
                    enabled_only = False).handle))
        self.app.Replace.Cancel.click()

    def test_clientrect(self):
        """Make sure clientrect() function works"""
        self.assertEqual(0, clientrect(self.dlghandle).left)
        self.assertEqual(0, clientrect(self.edit_handle).left)

        self.assertEqual(0, clientrect(self.dlghandle).top)
        self.assertEqual(0, clientrect(self.edit_handle).top)

        self.assertEqual(True,
            rectangle(self.dlghandle).right > clientrect(self.dlghandle).right)
        self.assertEqual(True,
            rectangle(self.edit_handle).right > clientrect(self.edit_handle).right)

        self.assertEqual(True,
            rectangle(self.dlghandle).bottom > clientrect(self.dlghandle).bottom)
        self.assertEqual(True,
            rectangle(self.edit_handle).bottom > clientrect(self.edit_handle).bottom)

    def test_rectangle(self):
        """Make sure rectangle() function works"""
        dlgrect = rectangle(self.dlghandle)
        self.assertEqual(True, dlgrect.left < dlgrect.right)
        self.assertEqual(True, dlgrect.top < dlgrect.bottom)

        editrect = rectangle(self.edit_handle)
        self.assertEqual(True, editrect.left < editrect.right)
        self.assertEqual(True, editrect.top < editrect.bottom)

    def test_font(self):
        """Make sure font() function works"""
        dlgfont = font(self.dlghandle)
        self.assertEqual(True, isinstance(dlgfont.lfFaceName, six.string_types))

        editfont = font(self.edit_handle)
        self.assertEqual(True, isinstance(editfont.lfFaceName, six.string_types))

        # handle.props font should return DEFAULT font for an invalid handle
        # Check only for a returned type as the default font can vary
        expected = win32structures.LOGFONTW()
        self.assertEqual(type(expected), type(font(sys.maxsize)))
        self.assertEqual(type(expected), type(font(None)))

    def test_processid(self):
        """Make sure processid() function works"""
        self.assertEqual(self.app.process, processid(self.dlghandle))
        self.assertEqual(self.app.process, processid(self.edit_handle))
        self.assertEqual(0, processid(sys.maxsize))
        self.assertEqual(0, processid(None))

    def test_children(self):
        """Make sure the children method returns correct result"""
        self.assertEqual(2,  len(children(self.dlghandle)))
        self.assertEqual([], children(self.edit_handle))

    def test_has_style(self):
        """Make sure the has_style method returns correct result"""
        self.assertEqual(True, has_style(self.dlghandle, 0xf0000))
        self.assertEqual(True, has_style(self.edit_handle, 0x4))

        self.assertEqual(False, has_style(self.dlghandle, 4))
        self.assertEqual(False, has_style(self.edit_handle, 1))


    def test_has_exstyle(self):
        """Make sure the has_exstyle method returns correct result"""
        self.assertEqual(True, has_exstyle(self.dlghandle, 0x10))
        self.assertEqual(True, has_exstyle(self.edit_handle, 0x200))

        self.assertEqual(False, has_exstyle(self.dlghandle, 4))
        self.assertEqual(False, has_exstyle(self.edit_handle, 0x10))

    def test_is_toplevel_window(self):
        """Make sure is_toplevel_window() function works"""
        self.assertEqual(True, is_toplevel_window(self.dlghandle))
        self.assertEqual(False, is_toplevel_window(self.edit_handle))

        self.app.UntitledNotepad.menu_select("Edit->Replace")
        self.assertEqual(True, is_toplevel_window(self.app.Replace.handle))
        self.assertEqual(False, is_toplevel_window(self.app.Replace.Cancel.handle))
        self.app.Replace.Cancel.click()

    def test_is64bitprocess(self):
        """Make sure a 64-bit process detection returns correct results"""
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
                    self.assertEqual(expected_is64bit, res_is64bit)
                finally:
                    # make sure to close an additional app we have opened
                    app.kill()

                # setup expected for a 64-bit app on x64
                expected_is64bit = True
        else:
            # setup expected for a 32-bit app on x86
            expected_is64bit = False

        # test native Notepad app
        res_is64bit = is64bitprocess(self.app.UntitledNotepad.process_id())
        self.assertEqual(expected_is64bit, res_is64bit)

    def test_is64bitbinary(self):
        exe32bit = os.path.join(os.path.dirname(__file__),
            r"..\..\apps\MFC_samples\RowList.exe")
        dll32bit = os.path.join(os.path.dirname(__file__),
            r"..\..\apps\MFC_samples\mfc100u.dll")
        self.assertEqual(is64bitbinary(exe32bit), False)
        self.assertEqual(is64bitbinary(dll32bit), None)

        warnings.filterwarnings('always', category=RuntimeWarning, append=True)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            is64bitbinary(dll32bit)
            assert len(w) >= 1
            assert issubclass(w[-1].category, RuntimeWarning)
            assert "Cannot get binary type for file" in str(w[-1].message)


    def test_dumpwindow(self):
        """Make sure dumpwindow() function works"""
        dlgdump = dumpwindow(self.dlghandle)

        for key, item in dlgdump.items():
            self.assertEqual(item, globals()[key](self.dlghandle))

        editdump = dumpwindow(self.edit_handle)

        for key, item in editdump.items():
            self.assertEqual(item, globals()[key](self.edit_handle))


if __name__ == "__main__":
    unittest.main()
