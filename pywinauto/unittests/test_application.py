# GUI Application automation and testing library
# Copyright (C) 2016 Vasily Ryabov
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

#pylint: disable-msg=C0301
#pylint: disable-msg=F0401
#pylint: disable-msg=W0142

"""Tests for application.py"""

import sys
import os
import unittest
import time
#import pprint
#import pdb
import warnings

sys.path.append(".")
from pywinauto import application
from pywinauto.controls import HwndWrapper
from pywinauto.application import Application
from pywinauto.application import WindowSpecification
from pywinauto.application import process_module
from pywinauto.application import process_get_modules
from pywinauto.application import ProcessNotFoundError
from pywinauto.application import AppStartError
from pywinauto.application import AppNotConnected
from pywinauto import findwindows
from pywinauto import findbestmatch
from pywinauto.timings import Timings
from pywinauto.timings import TimeoutError
from pywinauto.timings import WaitUntil
from pywinauto.timings import always_wait_until
from pywinauto.timings import always_wait_until_passes
from pywinauto.sysinfo import is_x64_Python
from pywinauto.sysinfo import is_x64_OS
from pywinauto import backend

#application.set_timing(1, .01, 1, .01, .05, 0, 0, .1, 0, .01)

# About dialog may take some time to load
# so make sure that we wait for it.
Timings.window_find_timeout = 5

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"

class ApplicationWarningTestCases(unittest.TestCase):

    """Unit tests for warnings in the application.Application class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        # Force Display User and Deprecation warnings every time
        # Python 3.3+nose/unittest trys really hard to suppress them
        for warning in (UserWarning, PendingDeprecationWarning):
            warnings.simplefilter('always', warning)

        mfc_samples_folder = os.path.join(os.path.dirname(__file__),
                                          r"..\..\apps\MFC_samples")
        if is_x64_Python():
            self.sample_exe = os.path.join(mfc_samples_folder,
                                           "x64",
                                           "CmnCtrl1.exe")
            self.sample_exe_inverted_bitness = os.path.join(mfc_samples_folder,
                                                            "CmnCtrl1.exe")
        else:
            self.sample_exe = os.path.join(mfc_samples_folder, "CmnCtrl1.exe")
            self.sample_exe_inverted_bitness = os.path.join(mfc_samples_folder,
                                                            "x64",
                                                            "CmnCtrl1.exe")

    def testStartWarning3264(self):
        if not is_x64_OS():
            self.defaultTestResult()
            return
        
        warnings.filterwarnings('always', category=UserWarning, append=True)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            app = Application().start(self.sample_exe_inverted_bitness)
            app.kill_()
            assert len(w) >= 1
            assert issubclass(w[-1].category, UserWarning)
            assert "64-bit" in str(w[-1].message)

    def testConnectWarning3264(self):
        if not is_x64_OS():
            self.defaultTestResult()
            return
        
        app = Application().start(self.sample_exe_inverted_bitness)
        warnings.filterwarnings('always', category=UserWarning, append=True)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            app2 = Application().connect(path=self.sample_exe_inverted_bitness)
            app.kill_()
            assert len(w) >= 1
            assert issubclass(w[-1].category, UserWarning)
            assert "64-bit" in str(w[-1].message)

    def testDeprecatedConnectWarning(self):
        warn_text = "connect_()/Connect_() methods are deprecated,"
        deprecated_connect_methods = ('connect_', 'Connect_')
        # warnings.filterwarnings('always', category=PendingDeprecationWarning,
        #                         append=True)
        with warnings.catch_warnings(record=True) as warns:
            app = Application().start(self.sample_exe)
            for deprecated_method in deprecated_connect_methods:
                app2 = getattr(Application(),
                               deprecated_method)(path=self.sample_exe)
            app.kill_()

        self.assertEquals(len(deprecated_connect_methods), len(warns))
        self.assertEquals(warns[-1].category, PendingDeprecationWarning)
        self.assertEquals(warn_text in str(warns[-1].message), True)

    def testDeprecatedStartWarning(self):
        warn_text = "start_()/Start_() methods are deprecated,"
        deprecated_start_methods = ('start_', 'Start_')
        # warnings.filterwarnings('always', category=PendingDeprecationWarning,
        #                         append=True)
        with warnings.catch_warnings(record=True) as warns:
            for deprecated_method in deprecated_start_methods:
                app = getattr(Application(),
                              deprecated_method)(self.sample_exe)
                app.kill_()

        self.assertEquals(len(deprecated_start_methods), len(warns))
        self.assertEquals(warns[-1].category, PendingDeprecationWarning)
        self.assertEquals(warn_text in str(warns[-1].message), True)


class ApplicationTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        self.prev_warn = warnings.showwarning
        def no_warnings(*args, **kwargs): pass
        warnings.showwarning = no_warnings

        if is_x64_Python() or not is_x64_OS():
            self.notepad_subpath = r"system32\notepad.exe"
        else:
            self.notepad_subpath = r"SysWOW64\notepad.exe"

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        #self.dlg.SendMessage(win32defines.WM_CLOSE)
        warnings.showwarning = self.prev_warn

    def test__init__(self):
        """Verify that Application instance is initialized or not"""
        self.assertRaises(ValueError, Application, backend='unregistered')

    def test_not_connected(self):
        """Verify that it raises when the app is not connected"""
        self.assertRaises (AppNotConnected, Application().__getattribute__, 'Hiya')
        self.assertRaises (AppNotConnected, Application().__getitem__, 'Hiya')
        self.assertRaises (AppNotConnected, Application().window_, title = 'Hiya')
        self.assertRaises (AppNotConnected, Application().top_window_,)

    def test_start_problem(self):
        """Verify start_ raises on unknown command"""
        self.assertRaises (AppStartError, Application().start, 'Hiya')

    def test_start(self):
        """test start() works correctly"""
        app = Application()
        self.assertEqual(app.process, None)
        app.start(_notepad_exe())
        self.assertNotEqual(app.process, None)

        self.assertEqual(app.UntitledNotepad.process_id(), app.process)

        notepadpath = os.path.join(os.environ['systemroot'], self.notepad_subpath)
        self.assertEqual(str(process_module(app.process)).lower(), str(notepadpath).lower())

        app.UntitledNotepad.MenuSelect("File->Exit")

#    def test_start(self):
#        "test start() works correctly"
#        app = Application()
#        self.assertEqual(app.process, None)
#        app._start("notepad.exe")
#        self.assertNotEqual(app.process, None)
#
#        self.assertEqual(app.UntitledNotepad.process_id(), app.process)
#
#        notepadpath = os.path.join(os.environ['systemroot'], r"system32\notepad.exe")
#        self.assertEqual(str(process_module(app.process)).lower(), str(notepadpath).lower())
#
#        app.UntitledNotepad.MenuSelect("File->Exit")

    def testStart_bug01(self):
        """On SourceForge forum AppStartError forgot to include %s for application name"""
        app = Application()
        self.assertEqual(app.process, None)
        application.app_start_timeout = 1
        app_name = r"I am not * and Application!/\.exe"
        try:
            app.start(app_name)
        except AppStartError as e:
            self.assertEquals(app_name in str(e), True)

#    def testset_timing(self):
#        """Test that set_timing sets the timing correctly"""
#        prev_timing = (
#            application.window_find_timeout,
#            application.window_retry_interval,
#            application.app_start_timeout,
#            application.exists_timeout,
#            application.exists_retry_interval,
#            HwndWrapper.delay_after_click,
#            HwndWrapper.delay_after_menuselect,
#            HwndWrapper.delay_after_sendkeys_key,
#            HwndWrapper.delay_after_button_click,
#            HwndWrapper.delay_before_after_close_click,
#        )
#        set_timing(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
#
#        self.assertEquals(
#            (
#                application.window_find_timeout,
#                application.window_retry_interval,
#                application.app_start_timeout,
#                application.exists_timeout,
#                application.exists_retry_interval,
#                HwndWrapper.delay_after_click,
#                HwndWrapper.delay_after_menuselect,
#                HwndWrapper.delay_after_sendkeys_key,
#                HwndWrapper.delay_after_button_click,
#                HwndWrapper.delay_before_after_close_click,
#            ), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) )
#
#        set_timing(*prev_timing)

    def test_connect_path(self):
        """Test that connect_() works with a path"""
        app1 = Application()
        app1.start(_notepad_exe())

        app_conn = Application()
        app_conn.connect(path=self.notepad_subpath)
        self.assertEqual(app1.process, app_conn.process)

        app_conn = Application()
        if is_x64_Python() or not is_x64_OS():
            app_conn.connect(path=r"c:\windows\system32\notepad.exe")
        else:
            app_conn.connect(path=r"c:\windows\syswow64\notepad.exe")
        self.assertEqual(app1.process, app_conn.process)

        accessible_modules = process_get_modules()
        accessible_process_names = [os.path.basename(name.lower()) for process, name, cmdline in accessible_modules]
        self.assertEquals('notepad.exe' in accessible_process_names, True)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')

#    def test_Connect(self):
#        """Test that connect_() works with a path"""
#        app1 = Application()
#        app1.start_("notepad.exe")
#
#        app_conn = Application()
#        app_conn.connect_(path = r"system32\notepad.exe")
#        self.assertEqual(app1.process, app_conn.process)
#
#        app_conn = Application()
#        app_conn.connect_(path = r"c:\windows\system32\notepad.exe")
#        self.assertEqual(app1.process, app_conn.process)
#
#        app_conn.UntitledNotepad.MenuSelect('File->Exit')

    def test_connect_process(self):
        """Test that connect_() works with a process"""
        app1 = Application()
        app1.start(_notepad_exe())

        app_conn = Application()
        app_conn.connect(process=app1.process)
        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')


    def test_connect_handle(self):
        """Test that connect_() works with a handle"""
        app1 = Application()
        app1.start(_notepad_exe())
        handle = app1.UntitledNotepad.handle

        app_conn = Application()
        app_conn.connect(handle=handle)
        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')

    def test_connect_windowspec(self):
        """Test that connect_() works with a windowspec"""
        app1 = Application()
        app1.start(_notepad_exe())
        #unused var: handle = app1.UntitledNotepad.handle

        app_conn = Application()
        try:
            app_conn.connect(title = "Untitled - Notepad")
        except findwindows.WindowAmbiguousError:
            wins = findwindows.find_elements(active_only = True, title = "Untitled - Notepad")
            app_conn.connect(handle = wins[0].handle)
        except findwindows.ElementNotFoundError:
            WaitUntil(30, 0.5, lambda: len(findwindows.find_elements(active_only = True, title = "Untitled - Notepad")) > 0)
            wins = findwindows.find_elements(active_only = True, title = "Untitled - Notepad")
            app_conn.connect(handle = wins[0].handle)

        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')

    def test_connect_raises(self):
        """Test that connect_() raises with invalid input"""
        # try an argument that does not exist
        self.assertRaises (
            TypeError,
            Application().connect, **{'not_arg': 23})

        self.assertRaises (
            RuntimeError,
            Application().connect)

        # try to pass an invalid process
        self.assertRaises (
            ProcessNotFoundError,
            Application().connect, **{'process': 0})

        # try to pass an invalid handle
        self.assertRaises(
            RuntimeError,
            Application().connect, **{'handle' : 0})

        # try to pass an invalid path
        self.assertRaises(
            ProcessNotFoundError,
            Application().connect, **{'path': "no app here"})

    def test_top_window(self):
        """Test that top_window_() works correctly"""
        app = Application()
        self.assertRaises(AppNotConnected, app.top_window_)
        
        app.start(_notepad_exe())

        self.assertEqual(app.UntitledNotepad.handle, app.top_window_().handle)

        app.UntitledNotepad.MenuSelect("Help->About Notepad")

        self.assertEqual(app.AboutNotepad.handle, app.top_window_().handle)

        app.AboutNotepad.Ok.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")
        app.UntitledNotepad.WaitNot('exists')
        self.assertRaises(RuntimeError, app.top_window_)

    def test_active_window(self):
        """Test that active_() works correctly"""
        app = Application()
        self.assertRaises(AppNotConnected, app.active_)
        self.assertRaises(AppNotConnected, app.is64bit)
        app.start(_notepad_exe())
        app.UntitledNotepad.Wait('ready')
        self.assertEqual(app.active_().handle, app.UntitledNotepad.handle)
        app.UntitledNotepad.MenuSelect("File->Exit")
        app.UntitledNotepad.WaitNot('exists')
        self.assertRaises(RuntimeError, app.active_)

    def test_cpu_usage(self):
        """Verify that cpu_usage() works correctly"""
        app = Application()
        self.assertRaises(AppNotConnected, app.cpu_usage)
        app.start(_notepad_exe())
        self.assertEquals(0.0 <= app.cpu_usage() <= 100.0, True)
        app.UntitledNotepad.MenuSelect("File->Exit")
        app.UntitledNotepad.WaitNot('exists')

    def test_wait_cpu_usage_lower(self):
        """Test that wait_cpu_usage_lower() works correctly"""
        if is_x64_Python() != is_x64_OS():
            return None
        
        app = Application().Start(r'explorer.exe')
        
        def _cabinetwclass_exist():
            "Verify if at least one active 'CabinetWClass' window is created"
            l = findwindows.find_elements(active_only = True, class_name = 'CabinetWClass')
            return (len(l) > 0)

        WaitUntil(40, 0.5, _cabinetwclass_exist)
        handle = findwindows.find_elements(active_only = True, class_name = 'CabinetWClass')[-1].handle
        window = WindowSpecification({'handle': handle, 'backend': 'native', })
        explorer = Application().Connect(process = window.process_id())
        
        try:
            explorer.WaitCPUUsageLower(threshold = 1.5, timeout = 60, usage_interval = 2)
            window.AddressBandRoot.ClickInput()
            window.TypeKeys(r'Control Panel\Programs\Programs and Features', with_spaces=True, set_foreground=True)
            window.TypeKeys(r'{ENTER}', set_foreground = False)
            WaitUntil(40, 0.5, lambda: len(findwindows.find_elements(active_only = True,
                                                                     title = 'Programs and Features',
                                                                     class_name='CabinetWClass')) > 0)
            explorer.WaitCPUUsageLower(threshold = 1.5, timeout = 60, usage_interval = 2)
            installed_programs = window.FolderView.texts()[1:]
            programs_list = ','.join(installed_programs)
            if ('Microsoft' not in programs_list) and ('Python' not in programs_list):
                HwndWrapper.ImageGrab.grab().save(r'explorer_screenshot.jpg')
                HwndWrapper.ActionLogger().log('\ninstalled_programs:\n')
                for prog in installed_programs:
                    HwndWrapper.ActionLogger().log(prog)
            self.assertEqual(('Microsoft' in programs_list) or ('Python' in programs_list), True)
        finally:
            window.Close(2.0)

    def test_windows(self):
        """Test that windows_() works correctly"""
        app = Application()

        self.assertRaises(AppNotConnected, app.windows_, **{'title' : 'not connected'})

        app.start('notepad.exe')
        
        self.assertRaises(ValueError, app.windows_, **{'backend' : 'uia'})

        notepad_handle = app.UntitledNotepad.handle
        self.assertEquals(app.windows_(visible_only = True), [notepad_handle])

        app.UntitledNotepad.MenuSelect("Help->About Notepad")

        aboutnotepad_handle = app.AboutNotepad.handle
        self.assertEquals(
            app.windows_(visible_only = True, enabled_only = False),
            [aboutnotepad_handle, notepad_handle])

        app.AboutNotepad.OK.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")

    def test_window(self):
        """Test that window_() works correctly"""
        app = Application()

        self.assertRaises(AppNotConnected, app.window_, **{'title' : 'not connected'})

        app.start(_notepad_exe())

        self.assertRaises(ValueError, app.windows_, **{'backend' : 'uia'})

        title = app.window_(title = "Untitled - Notepad")
        title_re = app.window_(title_re = "Untitled[ -]+Notepad")
        classname = app.window_(class_name = "Notepad")
        classname_re = app.window_(class_name_re = "Not..ad")
        handle = app.window_(handle = title.handle)
        bestmatch = app.window_(best_match = "Untiotled Notepad")

        self.assertNotEqual(title.handle, None)
        self.assertNotEqual(title.handle, 0)

        self.assertEqual(title.handle, title_re.handle)
        self.assertEqual(title.handle, classname.handle)
        self.assertEqual(title.handle, classname_re.handle)
        self.assertEqual(title.handle, handle.handle)
        self.assertEqual(title.handle, bestmatch.handle)

        app.UntitledNotepad.MenuSelect("File->Exit")

    def test_getitem(self):
        """Test that __getitem__() works correctly"""
        app = Application()
        app.start(_notepad_exe())

        self.assertRaises(Exception, app['blahblah'])

        self.assertRaises(
            findbestmatch.MatchError,
            app['blahblah']['not here'].__getitem__, 'handle')

        self.assertEqual(
            app[u'Unt\xeftledNotepad'].handle,
            app.window_(title = "Untitled - Notepad").handle)

        app.UntitledNotepad.MenuSelect("Help->About Notepad")

        self.assertEqual(
            app['AboutNotepad'].handle,
            app.window_(title = "About Notepad").handle)

        app.AboutNotepad.Ok.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")

    def test_getattribute(self):
        """Test that __getattribute__() works correctly"""
        app = Application()
        app.start(_notepad_exe())

        self.assertRaises(
            findbestmatch.MatchError,
            app.blahblah.__getattribute__, 'handle')

        self.assertEqual(
            app.UntitledNotepad.handle,
            app.window_(title = "Untitled - Notepad").handle)

        app.UntitledNotepad.MenuSelect("Help->About Notepad")

        # I think it's OK that this no longer raises a matcherror
        # just because the window is not enabled - doesn't mean you
        # should not be able to access it at all!
        #self.assertRaises(findbestmatch.MatchError,
        #    app.Notepad.__getattribute__, 'handle')

        self.assertEqual(
            app.AboutNotepad.handle,
            app.window_(title = "About Notepad").handle)

        app.AboutNotepad.Ok.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")

    def test_kill_(self):
        """test killing the application"""
        app = Application()
        app.start(_notepad_exe())

        app.UntitledNotepad.Edit.type_keys("hello")

        app.UntitledNotepad.MenuSelect("File->Print...")

        #app.Print.FindPrinter.Click() # Vasily: (Win7 x64) "Find Printer" dialog is from splwow64.exe process
        #app.FindPrinters.Stop.Click()

        app.kill_()

        self.assertRaises(AttributeError, app.UntitledNotepad.Edit)


    def test_connect_timeout(self):
        """Test that connect_() works with a timeout"""

        app1 = Application()
        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
        app1.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        app_conn = Application()
        app_conn.connect(process=app1.process, timeout = 2)
        self.assertEqual(app1.process, app_conn.process)

    def test_connect_timeout_error(self):
        """Test that connect_() works with a timeout error"""

        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

        path = os.path.join(mfc_samples_folder, u"ttttt1.exe")

        app_conn = Application()
        self.assertRaises(TimeoutError, app_conn.connect, path=path, timeout=2)

    def test_connect_default_timeout(self):
        """Test that connect_() works with a default timeout"""

        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

        app1 = Application()
        app1.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        app_conn = Application()
        app_conn.connect(process=app1.process, timeout = 2)
        self.assertEqual(app1.process, app_conn.process)

    def test_connect_timeout_incorrect(self):
        """Test that connect_() works with a timeout incorrect"""

        app_conn = Application()
        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

        self.assertRaises(
            ValueError,
            app_conn.connect, **{'path' : os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"), 'timeout' :"1.0a"})


    def test_connect_with_App(self):

        mfc_samples_folder = os.path.join(
            os.path.dirname(__file__), r"..\..\apps\MFC_samples")
        if is_x64_Python():
            mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))
        self.app1 = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"))
        self.app.connect(path=os.path.join(mfc_samples_folder, u"CmnCtrl2.exe"), timeout=10)
        self.assertEqual(self.app.process, self.app1.process)


class WindowSpecificationTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        self.app = Application().start("Notepad")
        self.dlgspec = self.app.UntitledNotepad
        self.ctrlspec = self.app.UntitledNotepad.Edit


    def tearDown(self):
        """Close the application after tests"""
        # close the application
        #self.app.UntitledNotepad.MenuSelect("File->Exit")
        self.app.kill_()

    def test__init__(self):
        """Test creating a new spec by hand"""
        wspec = WindowSpecification(
            dict(
                best_match = u"UntitledNotepad",
                process = self.app.process)
            )

        self.assertEquals(
            wspec.window_text(),
            u"Untitled - Notepad")

    def test__call__(self):
        """Test that __call__() correctly raises an error"""
        self.assertRaises(AttributeError, self.dlgspec)
        self.assertRaises(AttributeError, self.ctrlspec)

        # no best_match!
        wspec = WindowSpecification(
            dict(title = u"blah", process = self.app.process) )

        self.assertRaises(AttributeError, wspec)

    def test_wrapper_object(self):
        """Test that we can get a control"""
        self.assertEquals(True, isinstance(self.dlgspec, WindowSpecification))

        self.assertEquals(
            True,
            isinstance(self.dlgspec.WrapperObject(), HwndWrapper.HwndWrapper)
            )

    def test_window(self):
        """test specifying a sub window of an existing specification"""
        sub_spec = self.dlgspec.ChildWindow(class_name = "Edit")
        sub_spec_legacy = self.dlgspec.Window_(class_name = "Edit")

        self.assertEquals(True, isinstance(sub_spec, WindowSpecification))
        self.assertEquals(sub_spec.class_name(), "Edit")
        self.assertEquals(sub_spec_legacy.class_name(), "Edit")

    def test__getitem__(self):
        """test item access of a windowspec"""
        self.assertEquals(
            True,
            isinstance(self.dlgspec['Edit'], WindowSpecification)
            )

        self.assertEquals(self.dlgspec['Edit'].class_name(), "Edit")

        self.assertRaises(AttributeError, self.ctrlspec.__getitem__, 'edit')

    def test_getattr(self):
        """Test getting attributes works correctly"""
        self.assertEquals(
            True,
            isinstance(self.dlgspec.Edit, WindowSpecification)
            )

        self.assertEquals(self.dlgspec.Edit.class_name(), "Edit")

        # check that getting a dialog attribute works correctly
        self.assertEquals(
            "Notepad",
            self.dlgspec.class_name())


    def test_exists(self):
        """Check that windows exist"""
        self.assertEquals(True, self.dlgspec.Exists())
        self.assertEquals(True, self.dlgspec.Exists(0))
        self.assertEquals(True, self.ctrlspec.Exists())
        # TODO: test a control that is not visible but exists
        #self.assertEquals(True, self.app.DefaultIME.Exists())

        self.assertEquals(False, self.app.BlahBlah.Exists(.1))

    def test_exists_timing(self):
        """test the timing of the exists method"""
        # try ones that should be found immediately
        start = time.time()
        self.assertEquals(True, self.dlgspec.Exists())
        self.assertEquals(True, time.time() - start < .3)

        start = time.time()
        self.assertEquals(True, self.ctrlspec.Exists())
        self.assertEquals(True, time.time() - start < .3)

        # try one that should not be found
        start = time.time()
        self.assertEquals(True, self.dlgspec.Exists(.5))
        timedif =  time.time() - start
        self.assertEquals(True, .49 > timedif < .6)

    def test_wait(self):
        """test the functionality and timing of the wait method"""
        allowable_error = .2

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait("enaBleD "))
        time_taken = (time.time() - start)
        if not 0 <= time_taken < (0 + 2 * allowable_error):
            self.assertEqual(.02,  time_taken)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait("  ready"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait(" exiSTS"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait(" VISIBLE "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait(" ready enabled"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait("visible exists "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.WrapperObject(), self.dlgspec.Wait("exists "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        self.assertRaises(SyntaxError, self.dlgspec.Wait, "Invalid_criteria")

    def test_wait_not(self):
        """
        Test that wait not fails for all the following

        * raises and error when criteria not met
        * timing is close to the timeout value
        """
        allowable_error = .16

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, "enaBleD ", .1, .05)
        taken = time.time() - start
        if .1 < (taken)  > .1 + allowable_error:
            self.assertEqual(.12, taken)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, "  ready", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, " exiSTS", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, " VISIBLE ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, " ready enabled", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, "visible exists ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(TimeoutError, self.dlgspec.WaitNot, "exists ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        self.assertRaises(SyntaxError, self.dlgspec.WaitNot, "Invalid_criteria")

#    def test_wait_ready(self):
#        """Make sure the friendly class is set correctly"""
#        allowable_error = .02
#
#        start = time.time()
#        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.WaitReady(.1, .05))
#
#        # it it didn't finish in the allocated time then raise an error
#        # we assertEqual to something that we know is not right - to get a
#        # better error report
#        if not 0 <= (time.time() - start) < 0 + allowable_error:
#            self.assertEqual(0, time.time() - start)
#        #self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)
#
#
#    def testWaitNotReady(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertRaises(RuntimeError, self.dlgspec.WaitNotReady, .1, .05)
#
#        if not .1 <= (time.time() - start) < .1 + allowable_error:
#            self.assertEqual(.1, time.time() - start)
#
#        #self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)
#
#
#    def testWaitEnabled(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.WaitEnabled(.1, .05))
#
#        if not 0 <= (time.time() - start) < 0 + allowable_error:
#            self.assertEqual(0, time.time() - start)
#
#        #self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)
#
#
#    def testWaitNotEnabled(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertRaises(RuntimeError, self.dlgspec.WaitNotEnabled, .1, .05)
#        if not .1 <= (time.time() - start) < .1 + allowable_error:
#            self.assertEqual(.1, time.time() - start)
#        #self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)
#
#    def testWaitVisible(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.WaitVisible(.1, .05))
#        if not 0 <= (time.time() - start) < 0 + allowable_error:
#            self.assertEqual(0, time.time() - start)
#        #self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)
#
#    def testWaitNotVisible(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertRaises(RuntimeError, self.dlgspec.WaitNotVisible, .1, .05)
#        # it it didn't finish in the allocated time then raise an error
#        # we assertEqual to something that we know is not right - to get a
#        # better error report
#        if not .1 <= (time.time() - start) < .1 + allowable_error:
#            self.assertEqual(.1, time.time() - start)
#
#    def testWaitExists(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.WaitExists(.1, .05))
#
#        # it it didn't finish in the allocated time then raise an error
#        # we assertEqual to something that we know is not right - to get a
#        # better error report
#        if not 0 <= (time.time() - start) < 0 + allowable_error:
#            self.assertEqual(.1, time.time() - start)
#
#    def testWaitNotExists(self):
#        "Make sure the friendly class is set correctly"
#
#        allowable_error = .02
#
#        start = time.time()
#        self.assertRaises(RuntimeError, self.dlgspec.WaitNotExists, .1, .05)
#        if not .1 <= (time.time() - start) < .1 + allowable_error:
#            self.assertEqual(.1, time.time() - start)
#        #self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)


    def testPrintControlIdentifiers(self):
        """Make sure PrintControlIdentifiers() doesn't crash"""
        self.dlgspec.print_control_identifiers()
        self.ctrlspec.print_control_identifiers()

    def test_find_elements_re(self):
        """Test for bug #90: A crash in 'find_elements' when called with 'title_re' argument"""
        self.dlgspec.Wait('visible')
        windows = findwindows.find_elements(title_re = "Untitled - Notepad")
        self.assertTrue(len(windows) >= 1)

class WaitUntilDecoratorTests(unittest.TestCase):
    """Unit tests for always_wait_until and always_wait_until_passes decorators"""
    
    def test_always_wait_until_decorator_success(self):
        """Test always_wait_until_decorator success"""
        
        @always_wait_until(4, 2)
        def foo():
            return True
        self.assertTrue(foo())
        
    def test_always_wait_until_decorator_failure(self):
        """Test wait_until_decorator failure"""
        
        @always_wait_until(4, 2)
        def foo():
            return False
        self.assertRaises(TimeoutError, foo)
        
    def test_always_wait_until_passes_decorator_success(self):
        """Test always_wait_until_passes_decorator success"""
        
        @always_wait_until_passes(4, 2)
        def foo():
            return True
        self.assertTrue(foo())
        
    def test_always_wait_until_passes_decorator_failure(self):
        """Test always_wait_until_passes_decorator failure"""
        
        @always_wait_until_passes(4, 2)
        def foo():
            raise Exception("Unexpected Error in foo")
        self.assertRaises(TimeoutError, foo)
        
if __name__ == "__main__":
    unittest.main()
