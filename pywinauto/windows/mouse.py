# -*- coding: utf-8 -*-
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

"""Windows branch of the mouse module

"""

from ctypes import wintypes
from ctypes import windll
from ctypes import CFUNCTYPE
from ctypes import c_int
from ctypes import byref
from ctypes import pointer
import atexit
import sys
import time

import pywintypes
import win32con
import win32api
import win32gui

from math import ceil
from . import win32functions
from . import win32defines
from ..actionlogger import ActionLogger
from .win32structures import MSLLHOOKSTRUCT
from .win32structures import LRESULT
from ..timings import Timings
from .. import keyboard


HOOKCB = CFUNCTYPE(LRESULT, c_int, wintypes.WPARAM, wintypes.LPARAM)

windll.kernel32.GetModuleHandleA.restype = wintypes.HMODULE
windll.kernel32.GetModuleHandleA.argtypes = [wintypes.LPCSTR]
windll.user32.SetWindowsHookExA.restype = wintypes.HHOOK
windll.user32.SetWindowsHookExA.argtypes = [c_int, HOOKCB, wintypes.HINSTANCE, wintypes.DWORD]
windll.user32.SetWindowsHookExW.restype = wintypes.HHOOK
windll.user32.SetWindowsHookExW.argtypes = [c_int, HOOKCB, wintypes.HINSTANCE, wintypes.DWORD]

# LRESULT WINAPI CallNextHookEx(
#   _In_opt_ HHOOK  hhk,
#   _In_     int    nCode,
#   _In_     WPARAM wParam,
#   _In_     LPARAM lParam
# );
windll.user32.CallNextHookEx.argtypes = [wintypes.HHOOK, c_int, wintypes.WPARAM, wintypes.LPARAM]
windll.user32.CallNextHookEx.restypes = LRESULT


class MouseEvent(object):

    """Created when a mouse event happened"""

    def __init__(self, current_key=None, event_type=None, mouse_x=0, mouse_y=0):
        self.current_key = current_key
        self.event_type = event_type
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y


class MouseHook(object):

    """Hook for low level mouse events"""

    MOUSE_ID_TO_KEY = {win32con.WM_MOUSEMOVE: 'Move',
                       win32con.WM_LBUTTONDOWN: 'LButton',
                       win32con.WM_LBUTTONUP: 'LButton',
                       win32con.WM_RBUTTONDOWN: 'RButton',
                       win32con.WM_RBUTTONUP: 'RButton',
                       win32con.WM_MBUTTONDOWN: 'WheelButton',
                       win32con.WM_MBUTTONUP: 'WheelButton',
                       win32con.WM_MOUSEWHEEL: 'Wheel'}

    MOUSE_ID_TO_EVENT_TYPE = {win32con.WM_MOUSEMOVE: None,
                              win32con.WM_LBUTTONDOWN: 'key down',
                              win32con.WM_LBUTTONUP: 'key up',
                              win32con.WM_RBUTTONDOWN: 'key down',
                              win32con.WM_RBUTTONUP: 'key up',
                              win32con.WM_MBUTTONDOWN: 'key down',
                              win32con.WM_MBUTTONUP: 'key up',
                              win32con.WM_MOUSEWHEEL: None}

    event_types = {win32con.WM_KEYDOWN: 'key down',     # WM_KEYDOWN for normal keys
                   win32con.WM_KEYUP: 'key up',         # WM_KEYUP for normal keys
                   win32con.WM_SYSKEYDOWN: 'key down',  # WM_SYSKEYDOWN, is used for Alt key.
                   win32con.WM_SYSKEYUP: 'key up',      # WM_SYSKEYUP, is used for Alt key.
                   }

    def __init__(self):
        self.handler = None
        self.id = None
        self.is_hook = False

    def _ll_hdl(self, code, event_code, data_ptr):
        """Execute when a mouse low level event has been triggerred"""
        try:
            # The next hook in chain must be always called
            res = windll.user32.CallNextHookEx(self.id, code, event_code, data_ptr)
            if not self.handler:
                return res

            current_key = None
            event_code_word = 0xFFFFFFFF & event_code
            if event_code_word in self.MOUSE_ID_TO_KEY:
                current_key = self.MOUSE_ID_TO_KEY[event_code_word]

            event_type = None
            if current_key != 'Move':
                if event_code in self.MOUSE_ID_TO_EVENT_TYPE:
                    event_type = self.MOUSE_ID_TO_EVENT_TYPE[event_code]

                # Get the mouse position: x and y
                ms = MSLLHOOKSTRUCT.from_address(data_ptr)
                event = MouseEvent(current_key, event_type, ms.pt.x, ms.pt.y)
                self.handler(event)

        except Exception:
            al = ActionLogger()
            al.log("_ll_hdl, {0}".format(sys.exc_info()[0]))
            al.log("_ll_hdl, code {0}, event_code {1}".format(code, event_code))
            raise

        return res

    def hook(self, is_hook=True):
        """Hook mouse and/or keyboard events"""
        if not (is_hook):
            return

        self.is_hook = is_hook

        @HOOKCB
        def _ll_cb(code, event_code, data_ptr):
            """Forward the hook event to ourselves"""
            return self._ll_hdl(code, event_code, data_ptr)

        self.id = windll.user32.SetWindowsHookExA(
            win32con.WH_MOUSE_LL,
            _ll_cb,
            win32api.GetModuleHandle(None),
            0)

        self.listen()

    def unhook(self):
        """Unhook mouse events"""
        if self.is_hook:
            self.is_hook = False
            windll.user32.UnhookWindowsHookEx(self.id)

    def stop(self):
        """Stop the listening loop"""
        self.unhook()

    def is_hooked(self):
        """Verify if any of hooks are active"""
        return self.is_hook

    def _process_win_msgs(self):
        """Peek and process queued windows messages"""
        message = wintypes.MSG()
        while True:
            res = win32functions.PeekMessageW(pointer(message), 0, 0, 0, win32con.PM_REMOVE)
            if not res:
                break
            if message.message == win32con.WM_QUIT:
                self.stop()
                sys.exit(0)
            else:
                win32functions.TranslateMessage(byref(message))
                win32functions.DispatchMessageW(byref(message))

    def listen(self):
        """Listen for events"""
        atexit.register(windll.user32.UnhookWindowsHookEx, self.id)

        while self.is_hooked():
            self._process_win_msgs()
            time.sleep(0.02)


def _get_cursor_pos():  # get global coordinates
    return win32api.GetCursorPos()


def _set_cursor_pos(coords):
    """Wrapped SetCursorPos that handles non-active desktop case (coords is a tuple)"""
    try:
        win32api.SetCursorPos(coords)
    except pywintypes.error as exc:
        if str(exc) == "(0, 'SetCursorPos', 'No error message is available')":
            raise RuntimeError("There is no active desktop required for moving mouse cursor!\n")
        else:
            raise exc


def _perform_click_input(
    button="left",
    coords=(None, None),
    double=False,
    button_down=True,
    button_up=True,
    wheel_dist=0,
    pressed="",
    key_down=True,
    key_up=True,
    fast_move=False
):
    """Perform a click action using SendInput

    All the *click_input() and *mouse_input() methods use this function.

    Thanks to a bug report from Tomas Walch (twalch) on sourceforge and code
    seen at http://msdn.microsoft.com/en-us/magazine/cc164126.aspx this
    function now always works the same way whether the mouse buttons are
    swapped or not.

    For example if you send a right click to Notepad.Edit - it will always
    bring up a popup menu rather than 'clicking' it.
    """

    # Handle if the mouse buttons are swapped
    if win32functions.GetSystemMetrics(win32defines.SM_SWAPBUTTON):
        if button.lower() == 'left':
            button = 'right'
        elif button.lower() == 'right':
            button = 'left'

    events = []
    if button.lower() == 'left':
        events.append(win32defines.MOUSEEVENTF_MOVE)
        if button_down:
            events.append(win32defines.MOUSEEVENTF_LEFTDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_LEFTUP)
    elif button.lower() == 'right':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_RIGHTDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_RIGHTUP)
    elif button.lower() == 'middle':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_MIDDLEDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_MIDDLEUP)
    elif button.lower() == 'move':
        events.append(win32defines.MOUSEEVENTF_MOVE)
        events.append(win32defines.MOUSEEVENTF_ABSOLUTE)
    elif button.lower() == 'x':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_XDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_XUP)

    if button.lower() == 'wheel':
        events.append(win32defines.MOUSEEVENTF_WHEEL)

    # if we were asked to double click (and we are doing a full click
    # not just up or down.
    if double and button_down and button_up:
        events *= 2

    if button_down and (button.lower() not in ['move', 'wheel']):
        # wait while previous click is not affecting our current click
        while 0 < win32api.GetTickCount() - win32api.GetLastInputInfo() < win32gui.GetDoubleClickTime():
            time.sleep(Timings.after_clickinput_wait)

    # set the cursor position
    _set_cursor_pos((coords[0], coords[1]))
    if not fast_move:
        time.sleep(Timings.after_setcursorpos_wait)
    if win32api.GetCursorPos() != (coords[0], coords[1]):
        _set_cursor_pos((coords[0], coords[1]))
        time.sleep(Timings.after_setcursorpos_wait)

    keyboard_keys = pressed.lower().split()
    if ('control' in keyboard_keys) and key_down:
        keyboard.VirtualKeyAction(keyboard.VK_CONTROL, up=False).run()
    if ('shift' in keyboard_keys) and key_down:
        keyboard.VirtualKeyAction(keyboard.VK_SHIFT, up=False).run()
    if ('alt' in keyboard_keys) and key_down:
        keyboard.VirtualKeyAction(keyboard.VK_MENU, up=False).run()

    dw_flags = 0
    for event in events:
        dw_flags |= event

    dw_data = 0
    if button.lower() == 'wheel':
        wheel_dist = wheel_dist * 120
        dw_data = wheel_dist

    if button.lower() == 'move':
        x_res = win32functions.GetSystemMetrics(win32defines.SM_CXSCREEN)
        y_res = win32functions.GetSystemMetrics(win32defines.SM_CYSCREEN)
        x_coord = int(ceil(coords[0] * 65535 / (x_res - 1.)))  # in Python 2.7 return float val
        y_coord = int(ceil(coords[1] * 65535 / (y_res - 1.)))  # in Python 2.7 return float val
        win32api.mouse_event(dw_flags, x_coord, y_coord, dw_data)
    else:
        for event in events:
            if event == win32defines.MOUSEEVENTF_MOVE:
                x_res = win32functions.GetSystemMetrics(win32defines.SM_CXSCREEN)
                y_res = win32functions.GetSystemMetrics(win32defines.SM_CYSCREEN)
                x_coord = int(ceil(coords[0] * 65535 / (x_res - 1.)))  # in Python 2.7 return float val
                y_coord = int(ceil(coords[1] * 65535 / (y_res - 1.)))  # in Python 2.7 return float val
                win32api.mouse_event(
                    win32defines.MOUSEEVENTF_MOVE | win32defines.MOUSEEVENTF_ABSOLUTE,
                    x_coord, y_coord, dw_data)
            else:
                win32api.mouse_event(
                    event | win32defines.MOUSEEVENTF_ABSOLUTE,
                    coords[0], coords[1], dw_data)

    if not fast_move:
        time.sleep(Timings.after_clickinput_wait)

    if ('control' in keyboard_keys) and key_up:
        keyboard.VirtualKeyAction(keyboard.VK_CONTROL, down=False).run()
    if ('shift' in keyboard_keys) and key_up:
        keyboard.VirtualKeyAction(keyboard.VK_SHIFT, down=False).run()
    if ('alt' in keyboard_keys) and key_up:
        keyboard.VirtualKeyAction(keyboard.VK_MENU, down=False).run()


def click(button='left', coords=(0, 0)):
    """Click at the specified coordinates"""
    _perform_click_input(button=button, coords=coords)


def double_click(button='left', coords=(0, 0)):
    """Double click at the specified coordinates"""
    _perform_click_input(button=button, coords=coords, double=True)


def right_click(coords=(0, 0)):
    """Right click at the specified coords"""
    _perform_click_input(button='right', coords=coords)


def move(coords=(0, 0), duration=0.0):
    """Move the mouse"""
    if not isinstance(duration, float):
        raise TypeError("duration must be float (in seconds)")
    minimum_duration = 0.05
    if duration >= minimum_duration:
        x_start, y_start = _get_cursor_pos()
        delta_x = coords[0] - x_start
        delta_y = coords[1] - y_start
        max_delta = max(abs(delta_x), abs(delta_y))
        num_steps = max_delta
        sleep_amount = duration / max(num_steps, 1)
        if sleep_amount < minimum_duration:
            num_steps = int(num_steps * sleep_amount / minimum_duration)
            sleep_amount = minimum_duration
        delta_x /= max(num_steps, 1)
        delta_y /= max(num_steps, 1)
        for step in range(num_steps):
            _perform_click_input(button='move', coords=(x_start + int(delta_x*step), y_start + int(delta_y*step)),
                                 button_down=False, button_up=False, fast_move=True)
            time.sleep(sleep_amount)
    _perform_click_input(button='move', coords=coords, button_down=False, button_up=False)


def press(button='left', coords=(0, 0)):
    """Press the mouse button"""
    _perform_click_input(button=button, coords=coords, button_down=True, button_up=False)


def release(button='left', coords=(0, 0)):
    """Release the mouse button"""
    _perform_click_input(button=button, coords=coords, button_down=False, button_up=True)


def scroll(coords=(0, 0), wheel_dist=1):
    """Do mouse wheel"""
    if wheel_dist:
        _perform_click_input(button='wheel', wheel_dist=wheel_dist, coords=coords)


def wheel_click(coords=(0, 0)):
    """Middle mouse button click at the specified coords"""
    _perform_click_input(button='middle', coords=coords)
