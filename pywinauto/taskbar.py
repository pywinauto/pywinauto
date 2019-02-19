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

"""Module showing how to work with the task bar

This module will likely change significantly in the future!
"""

import warnings

from . import findwindows
from . import application

warnings.warn("The taskbar module is still very experimental", FutureWarning)

def TaskBarHandle():
    """Return the first window that has a class name 'Shell_TrayWnd'"""
    return findwindows.find_elements(class_name = "Shell_TrayWnd")[0].handle

def _click_hidden_tray_icon(reqd_button, mouse_button='left', exact=False, by_tooltip=False, double=False):
    popup_dlg = explorer_app.window(class_name='NotifyIconOverflowWindow')
    try:
        popup_toolbar = popup_dlg.OverflowNotificationAreaToolbar.wait('visible')
        button_index = popup_toolbar.button(reqd_button, exact=exact, by_tooltip=by_tooltip).index
    except Exception:
        ShowHiddenIconsButton.click_input() # may fail from PythonWin when script takes long time
        popup_dlg = explorer_app.window(class_name='NotifyIconOverflowWindow')
        popup_toolbar = popup_dlg.OverflowNotificationAreaToolbar.wait('visible')
        button_index = popup_toolbar.button(reqd_button, exact=exact, by_tooltip=by_tooltip).index

    popup_toolbar.button(button_index).click_input(button=mouse_button, double=double)

def ClickSystemTrayIcon(button, exact=False, by_tooltip=False, double=False):
    """Click on a visible tray icon given by button"""
    SystemTrayIcons.button(button, exact=exact, by_tooltip=by_tooltip).click_input(double=double)

def RightClickSystemTrayIcon(button, exact=False, by_tooltip=False):
    """Right click on a visible tray icon given by button"""
    SystemTrayIcons.button(button, exact=exact, by_tooltip=by_tooltip).click_input(button='right')

def ClickHiddenSystemTrayIcon(button, exact=False, by_tooltip=False, double=False):
    """Click on a hidden tray icon given by button"""
    _click_hidden_tray_icon(button, exact=exact, by_tooltip=by_tooltip, double=double)

def RightClickHiddenSystemTrayIcon(button, exact=False, by_tooltip=False):
    """Right click on a hidden tray icon given by button"""
    _click_hidden_tray_icon(button, mouse_button='right', exact=exact, by_tooltip=by_tooltip)


# windows explorer owns all these windows so get that app
explorer_app = application.Application().connect(handle=TaskBarHandle())

# Get the taskbar
TaskBar = explorer_app.window(handle=TaskBarHandle())

# The Start button
try:
    StartButton = explorer_app.window(title='Start', class_name='Button').wait('exists', 0.1) # Win7
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
SystemTrayIcons = TaskBar.child_window(class_name="ToolbarWindow32", found_index=0)

# the toolbar with the running applications
RunningApplications = TaskBar.MSTaskListWClass

# the language bar
try:
    LangPanel = TaskBar.CiceroUIWndFrame.wait('exists', 0.1) # Win7
except Exception:
    LangPanel = TaskBar.TrayInputIndicatorWClass # Win8.1

# the hidden tray icons button (TODO: think how to optimize)
ShowHiddenIconsButton = \
    [ch for ch in TaskBar.children() if ch.friendly_class_name() == 'Button'][-1]
