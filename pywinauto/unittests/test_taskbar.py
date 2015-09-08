# unit tests for taskbar module
# Copyright (C) 2015 Intel Corporation
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

"Tests for taskbar.py"

__revision__ = "$Revision$"

import unittest

import sys, time, os
sys.path.append(".")
from pywinauto import taskbar
from pywinauto.application import Application, ProcessNotFoundError
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto import win32defines

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


class TaskbarTestCases(unittest.TestCase):
    "Unit tests for the taskbar"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        app = Application()
        app.start_(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        self.app = app
        self.dlg = app.TrayMenu #top_window_()
        self.dlg.Wait('ready')


    def tearDown(self):
        "Close the application after tests"
        self.dlg.SendMessage(win32defines.WM_CLOSE)
        try:
            notepad = Application.connect(path=_notepad_exe())
            notepad.kill_()
        except ProcessNotFoundError:
            pass # notepad already closed


    def testTaskbar(self):
        taskbar.TaskBar.Wait('visible') # just make sure it's found

    '''
    def testStartButton(self): # TODO: fix it for AppVeyor
        taskbar.StartButton.ClickInput()
        
        start_menu = taskbar.explorer_app.Window_(class_name='DV2ControlHost')
        start_menu.SearchEditBoxWrapperClass.ClickInput()
        start_menu.SearchEditBoxWrapperClass.TypeKeys(_notepad_exe() + '{ENTER}', with_spaces=True, set_foreground=False)

        time.sleep(5)
        notepad = Application.connect(path=_notepad_exe())
        notepad.kill_()
    '''

    def testSystemTray(self):
        taskbar.SystemTray.Wait('visible') # just make sure it's found

    '''
    def testClock(self): # TODO: make it stable on AppVeyor
        taskbar.Clock.ClickInput()
        ClockWindow = taskbar.explorer_app.Window_(class_name='ClockFlyoutWindow')
        ClockWindow.Wait('visible')
        taskbar.Clock.ClickInput()
        ClockWindow.WaitNot('visible')
    '''

    def testClickIcons(self):
        "Test minimizing a sample app to tray and restoring"
        apps_area = taskbar.RunningApplications.Rectangle()
        
        self.dlg.Minimize()
        self.dlg.WaitNot('active')
        taskbar.ClickHiddenSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('active')


    '''
        taskbar.RunningApplications.RightClickInput(coords=(apps_area.width()-100, apps_area.height()-5))
        taskbar.explorer_app.PopupMenu.Menu().GetMenuPath('Start Task Manager')[0].Click()
        task_mgr = Application.connect(path='taskmgr.exe')
        task_manager_window = task_mgr.Window_(title='Windows Task Manager')
        task_manager_window.Wait('ready')
        task_manager_window.Minimize()
        task_manager_window.WaitNot('visible')
        
        taskbar.ClickSystemTrayIcon('CPU Usage: %', double=True)
        task_manager_window.Wait('ready')
        task_manager_window.Minimize()
        task_manager_window.WaitNot('visible')
    '''


if __name__ == "__main__":
    unittest.main()
