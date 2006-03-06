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

"Tests for application.py"

__revision__ = "$Revision: 234 $"

import os
import os.path
import unittest
import time
import pprint
import pdb

from pywinauto import application
from pywinauto.application import *
from pywinauto import findwindows


application.set_timing(1, .01, 1, .01, .05, 0, 0, .1, 0, .01)

class ApplicationTestCases(unittest.TestCase):
    "Unit tests for the application.Application class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        pass

    def tearDown(self):
        "Close the application after tests"
        # close the application
        #self.dlg.SendMessage(win32defines.WM_CLOSE)
        pass

    def testNotConnected(self):
        "Make sure the friendly class is set correctly"
        self.assertRaises (AppNotConnected, Application().__getattr__, 'Hiya')
        self.assertRaises (AppNotConnected, Application().__getitem__, 'Hiya')
        self.assertRaises (AppNotConnected, Application().window_, title = 'Hiya')
        self.assertRaises (AppNotConnected, Application().top_window_,)

    def testStartProblem(self):
        "Make sure the friendly class is set correctly"
        self.assertRaises (AppStartError, Application().start_, 'Hiya')


    def testStart(self):
        app = Application()
        self.assertEqual(app.process, None)
        app.start_("notepad.exe")
        self.assertNotEqual(app.process, None)

        self.assertEqual(app.UntitledNotepad.ProcessID(), app.process)

        notepadpath = os.path.join(os.environ['systemroot'], r"system32\notepad.exe")
        self.assertEqual(str(process_module(app.process)).lower(), str(notepadpath).lower())

        app.UntitledNotepad.MenuSelect("File->Exit")

    def testStart_bug01(self):
        "On SourceForge forum AppStartError forgot to include %s for application name"

        app = Application()
        self.assertEqual(app.process, None)
        application.app_start_timeout = 1
        app_name = r"I am not * and Application!/\.exe"
        try:
            app.start_(app_name)
        except AppStartError, e:
            self.assertEquals(app_name in str(e), True)


    def testset_timing(self):
        from pywinauto.controls import HwndWrapper
        prev_timing = (
            application.window_find_timeout,
            application.window_retry_interval,
            application.app_start_timeout,
            application.exists_timeout,
            application.exists_retry_interval,
            HwndWrapper.delay_after_click,
            HwndWrapper.delay_after_menuselect,
            HwndWrapper.delay_after_sendkeys_key,
            HwndWrapper.delay_after_button_click,
            HwndWrapper.delay_before_after_close_click,
        )
        set_timing(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        self.assertEquals(
            (
                application.window_find_timeout,
                application.window_retry_interval,
                application.app_start_timeout,
                application.exists_timeout,
                application.exists_retry_interval,
                HwndWrapper.delay_after_click,
                HwndWrapper.delay_after_menuselect,
                HwndWrapper.delay_after_sendkeys_key,
                HwndWrapper.delay_after_button_click,
                HwndWrapper.delay_before_after_close_click,
            ), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) )

        set_timing(*prev_timing)



    def testConnect_path(self):
        app1 = Application()
        app1.start_("notepad.exe")

        app_conn = Application()
        app_conn.connect_(path = r"system32\notepad.exe")
        self.assertEqual(app1.process, app_conn.process)

        app_conn = Application()
        app_conn.connect_(path = r"c:\windows\system32\notepad.exe")
        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')


    def testConnect_process(self):
        app1 = Application()
        app1.start_("notepad.exe")

        app_conn = Application()
        app_conn.connect_(process = app1.process)
        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')


    def testConnect_handle(self):
        app1 = Application()
        app1.start_("notepad.exe")
        handle = app1.UntitledNotepad.handle

        app_conn = Application()
        app_conn.connect_(handle = handle)
        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')


    def testConnect_windowspec(self):
        app1 = Application()
        app1.start_("notepad.exe")
        handle = app1.UntitledNotepad.handle

        app_conn = Application()
        try:
            app_conn.connect_(title = "Untitled - Notepad")
        except findwindows.WindowAmbiguousError:
            wins = findwindows.find_windows(title = "Untitled - Notepad")
            app_conn.connect_(handle = wins[0])

        self.assertEqual(app1.process, app_conn.process)

        app_conn.UntitledNotepad.MenuSelect('File->Exit')

    def testConnect_raises(self):
        # try an argument that does not exist
        self.assertRaises (
            TypeError,
            Application().connect_, **{'not_arg': 23})

        self.assertRaises (
            RuntimeError,
            Application().connect_)

        # try to pass an invalid process
        self.assertRaises (
            ProcessNotFoundError,
            Application().connect_, **{'process': 0})

        # try to pass an invalid handle
        self.assertRaises(
            RuntimeError,
            Application().connect_, **{'handle' : 0})

        # try to pass an invalid path
        self.assertRaises(
            ProcessNotFoundError,
            Application().connect_, **{'path': "no app here"})


    def testTopWindow(self):
        app = Application()
        app.start_('notepad.exe')

        self.assertEqual(app.UntitledNotepad.handle, app.top_window_().handle)

        app.UntitledNotepad.MenuSelect("File->Page Setup")

        self.assertEqual(app.PageSetup.handle, app.top_window_().handle)

        app.PageSetup.Cancel.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")


    def testWindows(self):
        app = Application()
        app.start_('notepad.exe')

        notepad_handle = app.UntitledNotepad.handle
        self.assertEquals(app.windows_(visible_only = True), [notepad_handle])

        app.UntitledNotepad.MenuSelect("File->Page Setup")

        pagesetup_handle = app.PageSetup.handle
        self.assertEquals(
            app.windows_(visible_only = True, enabled_only = False),
            [pagesetup_handle, notepad_handle])

        app.PageSetup.Cancel.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")

    def testWindow(self):
        app = Application()
        app.start_('notepad.exe')

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

    def testGetitem(self):
        app = Application()
        app.start_('notepad.exe')

        application.window_find_timeout = .5
        try:
            app['blahblah']
        except:
            pass


        self.assertRaises(
            findbestmatch.MatchError,
            app['blahblah'].__getattr__, 'handle')

        self.assertEqual(
            app[u'Unt\xeftledNotepad'].handle,
            app.window_(title = "Untitled - Notepad").handle)

        app.UntitledNotepad.MenuSelect("File->Page Setup")

        self.assertRaises(findbestmatch.MatchError,
            app[u'N\xeftepad'].__getattr__, 'handle')

        self.assertEqual(
            app['PageSetup'].handle,
            app.window_(title = "Page Setup").handle)

        app.PageSetup.Cancel.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")


    def testGetattr(self):
        app = Application()
        app.start_('notepad.exe')

        self.assertRaises(
            findbestmatch.MatchError,
            app.blahblah.__getattr__, 'handle')

        self.assertEqual(
            app.UntitledNotepad.handle,
            app.window_(title = "Untitled - Notepad").handle)

        app.UntitledNotepad.MenuSelect("File->Page Setup")

        self.assertRaises(findbestmatch.MatchError,
            app.Notepad.__getattr__, 'handle')

        self.assertEqual(
            app.PageSetup.handle,
            app.window_(title = "Page Setup").handle)

        app.PageSetup.Cancel.Click()
        app.UntitledNotepad.MenuSelect("File->Exit")




class WindowSpecificationTestCases(unittest.TestCase):
    "Unit tests for the application.Application class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start_("Notepad")
        self.dlgspec = self.app.UntitledNotepad
        self.ctrlspec = self.app.UntitledNotepad.Edit


    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.app.UntitledNotepad.MenuSelect("File->Exit")


    def test__init__(self):
        "Test creating a new spec by hand"

        wspec = WindowSpecification(
            dict(
                best_match = u"UntitledNotepad",
                process = self.app.process)
            )

        self.assertEquals(
            wspec.WindowText(),
            u"Untitled - Notepad")


    def test__call__(self):
        self.assertRaises(AttributeError, self.dlgspec)
        self.assertRaises(AttributeError, self.ctrlspec)

        # no best_match!
        wspec = WindowSpecification(
            dict(title = u"blah",) )

        self.assertRaises(AttributeError, wspec)



    def testCtrl(self):
        "Test that we can get a control "
        from pywinauto.controls import HwndWrapper
        self.assertEquals(True, isinstance(self.dlgspec, WindowSpecification))

        self.assertEquals(
            True,
            isinstance(self.dlgspec.ctrl_(), HwndWrapper.HwndWrapper)
            )

    def testWindow(self):
        "test specifying a sub window of an existing specification"
        sub_spec = self.dlgspec.window_(class_name = "Edit")

        self.assertEquals(True, isinstance(sub_spec, WindowSpecification))
        self.assertEquals(sub_spec.Class(), "Edit")



    def test__getitem__(self):
        "test item access of a windowspec"

        self.assertEquals(
            True,
            isinstance(self.dlgspec['Edit'], WindowSpecification)
            )

        self.assertEquals(self.dlgspec['Edit'].Class(), "Edit")

        self.assertRaises(AttributeError, self.ctrlspec.__getitem__, 'edit')



    def testGetAttr(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals(
            True,
            isinstance(self.dlgspec.Edit, WindowSpecification)
            )
        self.assertEquals(self.dlgspec.Edit.Class(), "Edit")



    def testExists(self):
        "Check that windows exist"

        self.assertEquals(True, self.dlgspec.Exists())
        self.assertEquals(True, self.dlgspec.Exists(0))
        self.assertEquals(True, self.ctrlspec.Exists())
        self.assertEquals(True, self.app.DefaultIME.Exists())

        self.assertEquals(False, self.app.BlahBlah.Exists(.1))


    def testExists_timing(self):

        # try ones that should be found immediately
        start = time.time()
        self.assertEquals(True, self.dlgspec.Exists())
        self.assertEquals(True, time.time() - start < .1)

        start = time.time()
        self.assertEquals(True, self.ctrlspec.Exists())
        self.assertEquals(True, time.time() - start < .1)

        # try one that should not be found
        start = time.time()
        self.assertEquals(True, self.dlgspec.Exists(.5))
        timedif =  time.time() - start
        self.assertEquals(True, .49 > timedif < .6)


    def testWait(self):

        allowable_error = .02

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait("enaBleD "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait("  ready"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait(" exiSTS"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait(" VISIBLE "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait(" ready enabled"))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait("visible exists "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)

        start = time.time()
        self.assertEqual(self.dlgspec.ctrl_(), self.dlgspec.Wait("exists "))
        self.assertEqual(True, 0 <= (time.time() - start) < 0 + allowable_error)



    def testWaitNot(self):
        """Test that wait not fails for all the following

        raises and error when criteria not met
        timing is close to the timeout value"""
        allowable_error = .02

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, "enaBleD ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, "  ready", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, " exiSTS", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, " VISIBLE ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, " ready enabled", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, "visible exists ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)

        start = time.time()
        self.assertRaises(RuntimeError, self.dlgspec.WaitNot, "exists ", .1, .05)
        self.assertEqual(True, .1 <= (time.time() - start) < .1 + allowable_error)


#    def testWaitReady(self):
#        "Make sure the friendly class is set correctly"
#        pass
#
#    def testWaitNotEnabled(self):
#        "Make sure the friendly class is set correctly"
#        pass
#
#    def testWaitNotVisible(self):
#        "Make sure the friendly class is set correctly"
#        pass
#
#    def testPrintControlIdentifiers(self):
#        "Make sure the friendly class is set correctly"
#        pass
#

if __name__ == "__main__":
    #_unittests()

    unittest.main()


