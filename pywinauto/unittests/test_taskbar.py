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

"""Tests for taskbar.py"""

import unittest
import sys
import os

sys.path.append(".")
from pywinauto import taskbar  # noqa: E402
from pywinauto import findwindows  # noqa: E402
from pywinauto.application import Application  # noqa: E402
from pywinauto.application import ProcessNotFoundError  # noqa: E402
from pywinauto.application import WindowSpecification  # noqa: E402
from pywinauto.sysinfo import is_x64_Python, is_x64_OS  # noqa: E402
from pywinauto import win32defines  # noqa: E402
from pywinauto.timings import wait_until  # noqa: E402
import pywinauto.actionlogger  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402
from pywinauto.controls.common_controls import ToolbarWrapper  # noqa: E402
from pywinauto import mouse  # noqa: E402
from pywinauto import Desktop  # noqa: E402

#pywinauto.actionlogger.enable()
mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\MFC_samples"
)
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

_ready_timeout = 60
_retry_interval = 0.5


def _toggle_notification_area_icons(show_all=True, debug_img=None):
    """
    A helper function to change 'Show All Icons' settings.
    On a succesful execution the function returns an original
    state of 'Show All Icons' checkbox.

    The helper works only for an "English" version of Windows,
    on non-english versions of Windows the 'Notification Area Icons'
    window should be accessed with a localized title"
    """

    Application().start(r'explorer.exe')
    class_name = 'CabinetWClass'

    def _cabinetwclass_exist():
        "Verify if at least one active 'CabinetWClass' window is created"
        l = findwindows.find_elements(active_only=True, class_name=class_name)
        return (len(l) > 0)

    wait_until(_ready_timeout, _retry_interval, _cabinetwclass_exist)
    handle = findwindows.find_elements(active_only=True,
                                       class_name=class_name)[-1].handle
    window = WindowSpecification({'handle': handle, 'backend': 'win32', })
    explorer = Application().connect(process=window.process_id())
    cur_state = None

    try:
        # Go to "Control Panel -> Notification Area Icons"
        cmd_str = r'control /name Microsoft.NotificationAreaIcons'
        for _ in range(3):
            window.wait("ready", timeout=_ready_timeout)
            window.AddressBandRoot.click_input()
            explorer.wait_cpu_usage_lower(threshold=2, timeout=_ready_timeout)
            window.type_keys(cmd_str, with_spaces=True, set_foreground=True)
            # verfiy the text in the address combobox after type_keys finished
            cmbx_spec = window.AddressBandRoot.ComboBoxEx
            if cmbx_spec.exists(timeout=_ready_timeout, retry_interval=_retry_interval):
                texts = cmbx_spec.texts()
                if texts and texts[0] == cmd_str:
                    break
            # Send ESCs to remove the invalid text
            window.type_keys("{ESC}" * 3)

        # Send 'ENTER' separately, this is to make sure
        # the window focus hasn't accidentally been lost
        window.type_keys(
            '{ENTER}',
            with_spaces=True,
            set_foreground=True
        )
        explorer.wait_cpu_usage_lower(threshold=5, timeout=_ready_timeout)

        # Get the new opened applet
        notif_area = Desktop().window(title="Notification Area Icons",
                                      class_name=class_name)
        notif_area.wait("ready", timeout=_ready_timeout)
        cur_state = notif_area.CheckBox.get_check_state()

        # toggle the checkbox if it differs and close the applet
        if bool(cur_state) != show_all:
            notif_area.CheckBox.click_input()
        notif_area.Ok.click_input()
        explorer.wait_cpu_usage_lower(threshold=5, timeout=_ready_timeout)

    except Exception as e:
        if debug_img:
            from PIL import ImageGrab
            ImageGrab.grab().save("%s.jpg" % (debug_img), "JPEG")
        l = pywinauto.actionlogger.ActionLogger()
        l.log("RuntimeError in _toggle_notification_area_icons")
        raise e

    finally:
        # close the explorer window
        window.close()

    return cur_state


def _wait_minimized(dlg):
    """A helper function to verify that the specified dialog is minimized

    Basically, WaitNot('visible', timeout=30) would work too, just
    wanted to make sure the dlg is really got to the 'minimized' state
    because we test hiding the window to the tray.
    """
    wait_until(
        timeout=_ready_timeout,
        retry_interval=_retry_interval,
        func=lambda: (dlg.get_show_state() == win32defines.SW_SHOWMINIMIZED)
    )
    return True


class TaskbarTestCases(unittest.TestCase):

    """Unit tests for the taskbar"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        Timings.defaults()

        self.tm = _ready_timeout
        app = Application(backend='win32')
        app.start(os.path.join(mfc_samples_folder, u"TrayMenu.exe"), wait_for_idle=False)
        self.app = app
        self.dlg = app.top_window()
        mouse.move((-500, 200))  # remove the mouse from the screen to avoid side effects
        self.dlg.wait('ready', timeout=self.tm)

    def tearDown(self):
        """Close the application after tests"""
        self.dlg.send_message(win32defines.WM_CLOSE)
        self.dlg.wait_not('ready')

        # cleanup additional unclosed sampleapps
        l = pywinauto.actionlogger.ActionLogger()
        try:
            for i in range(2):
                l.log("Look for unclosed sample apps")
                app = Application()
                app.connect(path="TrayMenu.exe")
                l.log("Forse closing a leftover app: {0}".format(app))
                app.kill()
        except(ProcessNotFoundError):
            l.log("No more leftovers. All good.")

    def testTaskbar(self):
        # just make sure it's found
        taskbar.TaskBar.wait('visible', timeout=self.tm)

    '''
    def testStartButton(self): # TODO: fix it for AppVeyor
        taskbar.StartButton.click_input()

        sample_app_exe = os.path.join(mfc_samples_folder, u"TrayMenu.exe")
        start_menu = taskbar.explorer_app.window(class_name='DV2ControlHost')
        start_menu.SearchEditBoxWrapperClass.click_input()
        start_menu.SearchEditBoxWrapperClass.type_keys(
           sample_app_exe() + '{ENTER}',
           with_spaces=True, set_foreground=False
           )

        time.sleep(5)
        app = Application.connect(path=sample_app_exe())
        dlg = app.top_window()
        Wait('ready', timeout=self.tm)
    '''

    def testSystemTray(self):
        taskbar.SystemTray.wait('visible', timeout=self.tm)  # just make sure it's found

    def testClock(self):
        "Test opening/closing of a system clock applet"

        # Just hide a sample app as we don't use it in this test
        self.dlg.minimize()
        _wait_minimized(self.dlg)

        # Launch Clock applet
        taskbar.Clock.click_input()
        ClockWindow = taskbar.explorer_app.window(class_name='ClockFlyoutWindow')
        ClockWindow.wait('visible', timeout=self.tm)

        # Close the applet with Esc, we don't click again on it because
        # the second click sometimes doesn't hide a clock but just relaunch it
        taskbar.Clock.type_keys("{ESC}", set_foreground=False)
        ClockWindow.wait_not('visible', timeout=self.tm)

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
            debug_img="%s_01" % (self.id())
        )

        self.dlg.minimize()
        _wait_minimized(self.dlg)

        menu_window = [None]

        # Click in the visible area and wait for a popup menu
        def _show_popup_menu():
            taskbar.explorer_app.wait_cpu_usage_lower(threshold=5, timeout=self.tm)
            taskbar.RightClickSystemTrayIcon('MFCTrayDemo')
            menu = self.app.top_window().children()[0]
            res = isinstance(menu, ToolbarWrapper) and menu.is_visible()
            menu_window[0] = menu
            return res

        wait_until(self.tm, _retry_interval, _show_popup_menu)
        menu_window[0].menu_bar_click_input("#2", self.app)
        popup_window = self.app.top_window()
        hdl = self.dlg.popup_window()
        self.assertEqual(popup_window.handle, hdl)

        taskbar.ClickSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.wait('active', timeout=self.tm)

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02" % (self.id()))

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
            debug_img="%s_01" % (self.id())
        )

        self.dlg.minimize()
        _wait_minimized(self.dlg)

        # Run one more instance of the sample app
        # hopefully one of the icons moves into the hidden area
        app2 = Application()
        app2.start(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg2 = app2.top_window()
        dlg2.wait('visible', timeout=self.tm)
        dlg2.minimize()
        _wait_minimized(dlg2)

        # Click in the hidden area
        taskbar.explorer_app.wait_cpu_usage_lower(threshold=5, timeout=40)
        taskbar.ClickHiddenSystemTrayIcon('MFCTrayDemo', double=True)
        self.dlg.wait('visible', timeout=self.tm)

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02" % (self.id()))

        dlg2.send_message(win32defines.WM_CLOSE)

    def testClickCustomizeButton(self):
        "Test click on the 'show hidden icons' button"

        # Minimize to tray
        self.dlg.minimize()
        _wait_minimized(self.dlg)

        # Make sure that the hidden icons area is enabled
        orig_hid_state = _toggle_notification_area_icons(
            show_all=False,
            debug_img="%s_01" % (self.id())
        )

        # Run one more instance of the sample app
        # hopefully one of the icons moves into the hidden area
        app2 = Application()
        app2.start(os.path.join(mfc_samples_folder, u"TrayMenu.exe"))
        dlg2 = app2.top_window()
        dlg2.wait('visible', timeout=self.tm)
        dlg2.minimize()
        _wait_minimized(dlg2)

        # Test click on "Show Hidden Icons" button
        taskbar.ShowHiddenIconsButton.click_input()
        niow_dlg = taskbar.explorer_app.window(class_name='NotifyIconOverflowWindow')
        niow_dlg.OverflowNotificationAreaToolbar.wait('ready', timeout=self.tm)
        niow_dlg.SysLink.click_input()

        nai = Desktop().window(
            title="Notification Area Icons",
            class_name="CabinetWClass"
        )
        nai.wait('ready')
        origAlwaysShow = nai.CheckBox.get_check_state()
        if not origAlwaysShow:
            nai.CheckBox.click_input()
        nai.OK.click()

        # Restore Notification Area settings
        _toggle_notification_area_icons(show_all=orig_hid_state,
                                        debug_img="%s_02" % (self.id()))

        # close the second sample app
        dlg2.send_message(win32defines.WM_CLOSE)

if __name__ == "__main__":
    unittest.main()
