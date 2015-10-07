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
from pywinauto import taskbar, \
                      findwindows
from pywinauto.application import Application, \
                                  ProcessNotFoundError, \
                                  WindowSpecification
from pywinauto.sysinfo import is_x64_Python, \
                              is_x64_OS
from pywinauto import win32defines
from pywinauto.timings import WaitUntil
import pywinauto.actionlogger

#pywinauto.actionlogger.enable()
mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')


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
        "Verify if at least one active 'CabinetWClass' window is created"
        l = findwindows.find_windows(active_only=True, class_name=class_name)
        return (len(l) > 0)

    WaitUntil(30, 0.5, _cabinetwclass_exist)
    handle = findwindows.find_windows(active_only=True,
                                      class_name=class_name)[-1]
    window = WindowSpecification({'handle': handle, })
    explorer = Application().Connect(process=window.ProcessID())
    cur_state = None

    try:
        # Go to "Control Panel -> Notification Area Icons"
        window.AddressBandRoot.ClickInput()
        window.TypeKeys(
                    r'control /name Microsoft.NotificationAreaIcons{ENTER}',
                    with_spaces=True,
                    set_foreground=False)
        explorer.WaitCPUUsageLower(threshold=5, timeout=40)

        # Get the new opened applet
        notif_area = explorer.Window_(title="Notification Area Icons",
                                      class_name=class_name)
        cur_state = notif_area.CheckBox.GetCheckState()

        # toggle the checkbox if it differs and close the applet
        if bool(cur_state) != show_all:
            notif_area.CheckBox.ClickInput()
        notif_area.Ok.ClickInput()
        explorer.WaitCPUUsageLower(threshold=5, timeout=40)

    except Exception as e:
        if debug_img:
            from PIL import ImageGrab
            ImageGrab.grab().save("%s.jpg" % (debug_img), "JPEG")
        l = pywinauto.actionlogger.ActionLogger()
        l.log("RuntimeError in _toggle_notification_area_icons")
        raise e

    finally:
        # close the explorer window
        window.Close()

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

        # cleanup additional unclosed sampleapps
        l = pywinauto.actionlogger.ActionLogger()
        hndls = findwindows.find_windows(title="TrayMenu")
        for h in hndls:
            l.log("Cleanup unclosed sample app, handle: 0x%x" % (h))
            Application().windows_(handle=h).Close()

    def testTaskbar(self):
        taskbar.TaskBar.Wait('visible')  # just make sure it's found

    '''
    def testStartButton(self): # TODO: fix it for AppVeyor
        taskbar.StartButton.ClickInput()

        sample_app_exe = os.path.join(mfc_samples_folder, u"TrayMenu.exe")
        start_menu = taskbar.explorer_app.Window_(class_name='DV2ControlHost')
        start_menu.SearchEditBoxWrapperClass.ClickInput()
        start_menu.SearchEditBoxWrapperClass.TypeKeys(
           sample_app_exe() + '{ENTER}',
           with_spaces=True, set_foreground=False
           )

        time.sleep(5)
        app = Application.connect(path=sample_app_exe())
        dlg = app.TrayMenu  # top_window_()
        Wait('ready')
    '''

    def testSystemTray(self):
        taskbar.SystemTray.Wait('visible')  # just make sure it's found

    def testClock(self):
        "Test opening/closing of a system clock applet"

        # Just hide a sample app, as we don't use it in this test
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Launch Clock applet
        taskbar.Clock.ClickInput()
        ClockWindow = taskbar.explorer_app.Window_(
                               class_name='ClockFlyoutWindow')
        ClockWindow.Wait('visible', timeout=40)

        # Close the applet with Esc, we don't click again on it because
        # the second click sometimes doesn't hide a clock but just relaunch it
        taskbar.Clock.TypeKeys("{ESC}")
        ClockWindow.WaitNot('visible', timeout=40)

    def testClickVisibleIcon(self):
        """
        Test minimizing a sample app into the visible area of the tray
        and restoring the app back
        """

        if is_x64_Python() != is_x64_OS():
            # We don't run this test for mixed cases:
            # a 32-bit Python process can't interact with
            # a 64-bit explorer process (taskbar) and vice versa
            return

        # Make sure that the hidden icons area is disabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=True,
                debug_img="%s_01.jpg" % (self.id())
                )

        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # click in the visible area
        taskbar.explorer_app.WaitCPUUsageLower(threshold=5, timeout=40)
        taskbar.ClickSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('active', timeout=40)

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02.jpg" % (self.id()))

    def testClickHiddenIcon(self):
        """
        Test minimizing a sample app into the hidden area of the tray
        and restoring the app back
        """

        if is_x64_Python() != is_x64_OS():
            # We don't run this test for mixed cases:
            # a 32-bit Python process can't interact with
            # a 64-bit explorer process (taskbar) and vice versa
            return

        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=False,
                debug_img="%s_01.jpg" % (self.id())
                )

        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Run one more instance of the sample app
        # hopefully one of the icons moves into the hidden area
        app2 = Application()
        app2.start_(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg2 = app2.TrayMenu
        dlg2.Wait('visible')
        dlg2.Minimize()
        dlg2.WaitNot('active')

        # Click in the hidden area
        taskbar.explorer_app.WaitCPUUsageLower(threshold=5, timeout=40)
        taskbar.ClickHiddenSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.Wait('visible', timeout=30)

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02.jpg" % (self.id()))

        dlg2.SendMessage(win32defines.WM_CLOSE)

    def testClickCustomizeButton(self):
        "Test click on the 'show hidden icons' button"

        # Minimize to tray
        self.dlg.Minimize()
        self.dlg.WaitNot('active')

        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(
                show_all=False,
                debug_img="%s_01.jpg" % (self.id())
                )

        # Run one more instance of the sample app
        # hopefully one of the icons moves into the hidden area
        app2 = Application()
        app2.start_(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg2 = app2.TrayMenu
        dlg2.Wait('visible')
        dlg2.Minimize()
        dlg2.WaitNot('active')

        # Test click on "Show Hidden Icons" button
        taskbar.ShowHiddenIconsButton.ClickInput()
        niow_dlg = taskbar.explorer_app.Window_(
                class_name='NotifyIconOverflowWindow')
        niow_dlg.OverflowNotificationAreaToolbar.Wait('ready', timeout=30)
        niow_dlg.SysLink.ClickInput()
        nai = taskbar.explorer_app.Window_(
                title="Notification Area Icons",
                class_name="CabinetWClass"
                )
        origAlwaysShow = nai.CheckBox.GetCheckState()
        if not origAlwaysShow:
            nai.CheckBox.ClickInput()
        nai.OK.Click()

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02.jpg" % (self.id()))

        # close the second sample app
        dlg2.SendMessage(win32defines.WM_CLOSE)

if __name__ == "__main__":
    unittest.main()

