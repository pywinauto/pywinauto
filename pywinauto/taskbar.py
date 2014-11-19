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

"""Module showing how to work with the task bar

This module will likely change significantly in the future!"""

import warnings

from pywinauto import win32defines
from pywinauto import findwindows
from pywinauto import application

warnings.warn("The taskbar module is still very experimental", FutureWarning)

def TaskBarHandle():
    "Return the first window that has a class name 'Shell_TrayWnd'"
    return findwindows.find_windows(class_name = "Shell_TrayWnd")[0]


def _get_visible_button_index(reqd_button):
    "Get the nth visible icon"
    cur_button = -1
    for i in range(0, SystemTrayIcons.ButtonCount()):
        if not SystemTrayIcons.GetButton(i).fsState & \
            win32defines.TBSTATE_HIDDEN:

            cur_button += 1

        if cur_button == reqd_button:
            return i

def ClickSystemTrayIcon(button):
    "Click on a visible tray icon given by button"
    button = _get_visible_button_index(button)
    r = SystemTrayIcons.GetButtonRect(button)
    SystemTrayIcons.ClickInput(coords = (r.left+2, r.top+2))

def RightClickSystemTrayIcon(button):
    "Right click on a visible tray icon given by button"
    button = _get_visible_button_index(button)
    r = SystemTrayIcons.GetButtonRect(button)
    SystemTrayIcons.RightClickInput(coords = (r.left+2, r.top+2))



# windows explorer owns all these windows so get that app
explorer_app = application.Application().connect_(handle = TaskBarHandle())

# Get the taskbar
TaskBar = explorer_app.window_(handle = TaskBarHandle())

# The Start button
StartButton = TaskBar.Start

# the Quick Launch toolbar
QuickLaunch = TaskBar.QuickLaunch

# the system tray - contains various windows
SystemTray = TaskBar.TrayNotifyWnd

# the clock is in the system tray
Clock = TaskBar.TrayClockWClass

# these are the icons - what people normally think of
# as the system tray
SystemTrayIcons = TaskBar.NoficationArea

# the toolbar with the running applications
RunningApplications = TaskBar.RunningApplicationsToolbar


