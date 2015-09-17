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
import sys
import time
import os
sys.path.append(".")
from PIL import ImageGrab
from pywinauto import taskbar, \
                      findwindows
from pywinauto.application import Application, \
                                  ProcessNotFoundError, \
                                  WindowSpecification
from pywinauto.sysinfo import is_x64_Python, \
                              is_x64_OS
from pywinauto import win32defines
from pywinauto.timings import WaitUntil
from pywinauto.actionlogger import ActionLogger

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')


def _notepad_exe():
    if is_x64_Python() or not is_x64_OS():
        return r"C:\Windows\System32\notepad.exe"
    else:
        return r"C:\Windows\SysWOW64\notepad.exe"


def _toggle_notification_area_icons(show_all=True, debug_img=None):
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
    class_name = 'CabinetWClass'

    def _cabinetwclass_exist():
        "Verify if at least one 'CabinetWClass' window is created"
        l = findwindows.find_windows(active_only=True, class_name=class_name)
        return (len(l) > 0)

    WaitUntil(30, 0.5, _cabinetwclass_exist)
    handle = findwindows.find_windows(active_only=True,
                                      class_name=class_name)[-1]
    NewWindow = WindowSpecification({'handle': handle, })
    explorer = Application().Connect(process=NewWindow.ProcessID())
    cur_state = None

    try:
        # Go to "Control Panel -> Notification Area Icons"
        NewWindow.AddressBandRoot.ClickInput()
        NewWindow.TypeKeys(
                    r'control /name Microsoft.NotificationAreaIcons{ENTER}',
                    with_spaces=True, set_foreground=False)
        explorer.WaitCPUUsageLower(threshold=5, timeout=40)

        # Get the new opened applet
        NotificationAreaIcons = explorer.Window_(
                                    title="Notification Area Icons",
                                    class_name=class_name)
        cur_state = NotificationAreaIcons.CheckBox.GetCheckState()

        # toggle the checkbox if it differs and close the applet
        if bool(cur_state) != show_all:
            NotificationAreaIcons.CheckBox.ClickInput()
        NotificationAreaIcons.Ok.ClickInput()
        explorer.WaitCPUUsageLower(threshold=5, timeout=40)

    except exceptions as e:
        if debug_img:
            ImageGrab.grab().save("%s.jpg" % (debug_img), "JPEG")
        ActionLogger().log("RuntimeError in _toggle_notification_area_icons")
        raise e

    finally:
        # close the explorer window
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
        self.dlg = app.TrayMenu  # top_window_()
        self.dlg.Wait('ready')

    def tearDown(self):
        "Close the application after tests"
        self.dlg.SendMessage(win32defines.WM_CLOSE)
        try:
            notepad = Application.connect(path=_notepad_exe())
            notepad.kill_()
        except ProcessNotFoundError:
            pass  # notepad already closed

    def testTaskbar(self):
        taskbar.TaskBar.Wait('visible')  # just make sure it's found

    '''
    def testStartButton(self): # TODO: fix it for AppVeyor
        taskbar.StartButton.ClickInput()

        start_menu = taskbar.explorer_app.Window_(class_name='DV2ControlHost')
        start_menu.SearchEditBoxWrapperClass.ClickInput()
        start_menu.SearchEditBoxWrapperClass.TypeKeys(
           _notepad_exe() + '{ENTER}', with_spaces=True, set_foreground=False)

        time.sleep(5)
        notepad = Application.connect(path=_notepad_exe())
        notepad.kill_()
    '''

    def testSystemTray(self):
        taskbar.SystemTray.Wait('visible')  # just make sure it's found

    '''
    def testClock(self): # TODO: make it stable on AppVeyor
        taskbar.Clock.ClickInput()
        ClockWindow = taskbar.explorer_app.Window_(
                               class_name='ClockFlyoutWindow')
        ClockWindow.Wait('visible')
        taskbar.Clock.ClickInput()
        ClockWindow.WaitNot('visible')
    '''

    def testClickVisibleIcon(self):
        """
        Test minimizing a sample app into the visible area of the tray
        and restoring the app back
        """

        # Make sure that the hidden icons area is disabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=True,
                debug_img="%s_01.jpg" % (self.id())
                )

        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # click in the visible area
        taskbar.SystemTrayIcons.Wait("ready", 30)
        taskbar.ClickSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('active')

        # Restore Notification Area settings
        _toggle_notification_area_icons(
                show_all=orig_hid_state,
                debug_img="%s_02.jpg" % (self.id())
                )

    def testClickHiddenIcon(self):
        """
        Test minimizing a sample app into the hidden area of the tray
        and restoring the app back
        """

        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=False,
                debug_img="%s_01.jpg" % (self.id())
                )

        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Run one more instance of the sample app
        # hopefully one of the icons moves into the hidden area
        app = Application()
        app.start_(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg = app.TrayMenu
        dlg.Wait('ready')
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Click in the hidden area
        taskbar.ClickHiddenSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('visible', timeout=30)

        # Restore Notification Area settings
        _toggle_notification_area_icons(
                show_all=orig_hid_state,
                debug_img="%s_02.jpg" % (self.id())
                )

        dlg.SendMessage(win32defines.WM_CLOSE)

    def testClickCustomizeButton(self):
        "Test click on show hidden icons button"

        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=False,
                debug_img="%s_01.jpg" % (self.id())
                )

        # Test click on "Show Hidden Icons" button
        taskbar.ShowHiddenIconsButton.ClickInput()
        dlg = taskbar.explorer_app.Window_(
                class_name='NotifyIconOverflowWindow')
        from pywinauto.timings import TimeoutError
        try:
            dlg.OverflowNotificationAreaToolbar.Wait('ready', timeout=30)
        except(TimeoutError):
            ImageGrab.grab().save("TimeoutError_%s.jpg" % (self.id()), "JPEG")
        dlg.SysLink.ClickInput()
        nai = taskbar.explorer_app.Window_(
                title="Notification Area Icons",
                class_name="CabinetWClass"
                )
        origAlwaysShow = nai.CheckBox.GetCheckState()
        if not origAlwaysShow:
            nai.CheckBox.ClickInput()
        nai.OK.Click()

        # Restore Notification Area settings
        _toggle_notification_area_icons(
                show_all=orig_hid_state,
                debug_img="%s_02.jpg" % (self.id())
                )


if __name__ == "__main__":
    unittest.main()
