# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 Zoya Maslova (Nizhny Novgorod State University)
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

"""Module showing how to work with the task bar

This module will likely change significantly in the future!"""

import warnings

from . import sysinfo
from pywinauto import findwindows
from pywinauto import application

warnings.warn("The taskbar module is still very experimental", FutureWarning)

def TaskBarHandle():
    "Return the first window that has a class name 'Shell_TrayWnd'"
    return findwindows.find_elements(class_name = "Shell_TrayWnd")[0].handle

def _click_hidden_tray_icon(reqd_button, mouse_button = 'left', exact = False, by_tooltip = False, double = False):
    popup_dlg = explorer_app.Window_(class_name='NotifyIconOverflowWindow')
    try:
        popup_toolbar = popup_dlg.OverflowNotificationAreaToolbar.Wait('visible')
        button_index = popup_toolbar.Button(reqd_button, exact=exact, by_tooltip=by_tooltip).index
    except Exception:
        ShowHiddenIconsButton.click_input() # may fail from PythonWin when script takes long time
        popup_dlg = explorer_app.Window_(class_name='NotifyIconOverflowWindow')
        popup_toolbar = popup_dlg.OverflowNotificationAreaToolbar.Wait('visible')
        button_index = popup_toolbar.Button(reqd_button, exact=exact, by_tooltip=by_tooltip).index

    popup_toolbar.Button(button_index).click_input(button=mouse_button, double=double)

def ClickSystemTrayIcon(button, exact = False, by_tooltip = False, double=False):
    "Click on a visible tray icon given by button"
    SystemTrayIcons.Button(button, exact=exact, by_tooltip=by_tooltip).click_input(double=double)

def RightClickSystemTrayIcon(button, exact = False, by_tooltip = False):
    "Right click on a visible tray icon given by button"
    SystemTrayIcons.Button(button, exact=exact, by_tooltip=by_tooltip).click_input(button='right')

def ClickHiddenSystemTrayIcon(button, exact = False, by_tooltip = False, double=False):
    "Click on a hidden tray icon given by button"
    _click_hidden_tray_icon(button, exact=exact, by_tooltip=by_tooltip, double=double)

def RightClickHiddenSystemTrayIcon(button, exact = False, by_tooltip=False):
    "Right click on a hidden tray icon given by button"
    _click_hidden_tray_icon(button, mouse_button='right', exact=exact, by_tooltip=by_tooltip)


# windows explorer owns all these windows so get that app
explorer_app = application.Application().connect(handle = TaskBarHandle())

# Get the taskbar
TaskBar = explorer_app.window_(handle = TaskBarHandle())

# The Start button
try:
    StartButton = explorer_app.Window_(title='Start', class_name='Button').Wait('exists', 0.1) # Win7
except Exception:
    StartButton = TaskBar.Start # Win8.1

# the system tray - contains various windows
SystemTray = TaskBar.TrayNotifyWnd

# the clock is in the system tray
Clock = TaskBar.TrayClockWClass

# the show desktop button
ShowDesktop = TaskBar.TrayShowDesktopButtonWClass

# these are the icons - what people normally think of
# as the system tray
SystemTrayIcons = TaskBar.NotificationAreaToolbar

# the toolbar with the running applications
RunningApplications = TaskBar.MSTaskListWClass

# the language bar
try:
    LangPanel = TaskBar.CiceroUIWndFrame.Wait('exists', 0.1) # Win7
except Exception:
    LangPanel = TaskBar.TrayInputIndicatorWClass # Win8.1

# the hidden tray icons button (TODO: think how to optimize)
ShowHiddenIconsButton = [ch for ch in TaskBar.children() if ch.friendly_class_name() == 'Button'][-1] #TaskBar.Button #added
