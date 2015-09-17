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
from pywinauto import taskbar, findwindows
from pywinauto.application import Application, ProcessNotFoundError, WindowSpecification
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto import win32defines
from pywinauto.timings import WaitUntil

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"

def _toggle_notification_area_icons(show_all=True):
    """
    A helper function to change 'Show All Icons' settings.
    On a succesful execution the function returns an original
    state of 'Show All Icons' checkbox.

    The helper works only for an "English" version of Windows,
    on non-english versions of Windows the 'Notification Area Icons'
    window should be accessed with a localized title"
    """

    app = Application()
    starter = app.start_(r'explorer.exe')
    WaitUntil(30, 0.5, lambda: len(findwindows.find_windows(active_only=True, class_name='CabinetWClass')) > 0)
    handle = findwindows.find_windows(active_only=True, class_name='CabinetWClass')[-1]
    NewWindow = WindowSpecification({'handle': handle, })
    explorer = Application().Connect(process=NewWindow.ProcessID())
    cur_state = None
    
    # Go to "Control Panel -> Notification Area Icons"
    try:
        NewWindow.AddressBandRoot.ClickInput()
        NewWindow.TypeKeys(r'control /name Microsoft.NotificationAreaIcons{ENTER}', 
                with_spaces=True, set_foreground=False)
        explorer.WaitCPUUsageLower(threshold=4)
        NotificationAreaIcons = explorer.Window_(title="Notification Area Icons", 
                class_name="CabinetWClass")

        cur_state = NotificationAreaIcons.CheckBox.GetCheckState()

        # toggle the checkbox if it differs
        if bool(cur_state) != show_all:
            NotificationAreaIcons.CheckBox.ClickInput()
        NotificationAreaIcons.Ok.ClickInput()
    
        explorer.WaitCPUUsageLower(threshold=4)
    finally:
        NewWindow.Close()

    return cur_state

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

    def testClickVisibleIcon(self):
        """
        Test minimizing a sample app to the visible area of the tray 
        and restoring the app back
        """
        
        # Make sure that the hidden icons area is disabled
        orig_hid_state = _toggle_notification_area_icons(show_all=True)
        
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # click in the visible area
        taskbar.ClickSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('active')

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state)
    
    def testClickHiddenIcon(self):
        """
        Test minimizing a sample app into the hidden area of the tray
        and restoring the app back
        """
        
        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(show_all=False)
        
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Run one more sample app to make sure one of the icons moves into the hidden area
        app = Application()
        app.start_(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg = app.TrayMenu
        dlg.Wait('ready')
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Click in the hidden area
        taskbar.ClickHiddenSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('active')

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state)

        dlg.SendMessage(win32defines.WM_CLOSE)

    def testClickCustomizeButton(self):
        "Test click on show hidden icons button"
        
        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(show_all=False)

        # Test click on "Show Hidden Icons" button
        taskbar.ShowHiddenIconsButton.ClickInput()
        popup_dlg = taskbar.explorer_app.Window_(class_name='NotifyIconOverflowWindow')
        popup_toolbar = popup_dlg.OverflowNotificationAreaToolbar.Wait('visible')
        popup_dlg.SysLink.ClickInput()
        nai = taskbar.explorer_app.Window_(title="Notification Area Icons", class_name="CabinetWClass")
        origAlwaysShow = nai.CheckBox.GetCheckState()
        if not origAlwaysShow:
            nai.CheckBox.ClickInput()
        nai.OK.Click()

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state)


if __name__ == "__main__":
    unittest.main()
