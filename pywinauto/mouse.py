# Copyright (c) 2016 Ivan Magazinnik
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2010 Mark Mc Mahon
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
# * Neither the name of ttt nor the names of its
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

"Cross-platform module to emulate mouse events like a real user"

import sys
import time
if sys.platform == 'win32':
    from . import win32functions
    from . import win32defines
    from .timings import Timings
    from . import win32structures
    import win32api
else:
    from Xlib.display import Display
    from Xlib import X
    from Xlib.ext.xtest import fake_input


BUTTON_MAPPING = {'left': 1, 'middle': 2, 'right': 3, 'up_scroll': 4,
                  'down_scroll': 5, 'left_scroll': 6, 'right_scroll': 7}


if sys.platform == 'win32':
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
    ):
        """Perform a click action using SendInput

        All the *ClickInput() and *MouseInput() methods use this function.

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

        # set the cursor position
        win32api.SetCursorPos((coords[0], coords[1]))
        time.sleep(Timings.after_setcursorpos_wait)

        inp_struct = win32structures.INPUT()
        inp_struct.type = win32defines.INPUT_MOUSE

        keyboard_keys = pressed.lower().split()
        if ('control' in keyboard_keys) and key_down:
            SendKeys.VirtualKeyAction(SendKeys.VK_CONTROL, up=False).Run()
        if ('shift' in keyboard_keys) and key_down:
            SendKeys.VirtualKeyAction(SendKeys.VK_SHIFT, up=False).Run()
        if ('alt' in keyboard_keys) and key_down:
            SendKeys.VirtualKeyAction(SendKeys.VK_MENU, up=False).Run()

        inp_struct.mi.dwFlags = 0
        for event in events:
            inp_struct.mi.dwFlags |= event

        dwData = 0
        if button.lower() == 'wheel':
            wheel_dist = wheel_dist * 120
            dwData = wheel_dist
            inp_struct.mi.mouseData = wheel_dist
        else:
            inp_struct.mi.mouseData = 0

        if button.lower() == 'move':
            # win32functions.SendInput(     # vvryabov: SendInput() should be called sequentially in a loop [for event in events]
            #    win32structures.UINT(1),
            #    ctypes.pointer(inp_struct),
            #    ctypes.c_int(ctypes.sizeof(inp_struct)))
            X_res = win32functions.GetSystemMetrics(win32defines.SM_CXSCREEN)
            Y_res = win32functions.GetSystemMetrics(win32defines.SM_CYSCREEN)
            X_coord = int(float(coords[0]) * (65535. / float(X_res - 1)))
            Y_coord = int(float(coords[1]) * (65535. / float(Y_res - 1)))
            win32api.mouse_event(inp_struct.mi.dwFlags, X_coord, Y_coord, dwData)
        else:
            for event in events:
                inp_struct.mi.dwFlags = event
                win32api.mouse_event(inp_struct.mi.dwFlags, coords[0], coords[1], dwData)
                time.sleep(Timings.after_clickinput_wait)

        time.sleep(Timings.after_clickinput_wait)

        if ('control' in keyboard_keys) and key_up:
            SendKeys.VirtualKeyAction(SendKeys.VK_CONTROL, down=False).Run()
        if ('shift' in keyboard_keys) and key_up:
            SendKeys.VirtualKeyAction(SendKeys.VK_SHIFT, down=False).Run()
        if ('alt' in keyboard_keys) and key_up:
            SendKeys.VirtualKeyAction(SendKeys.VK_MENU, down=False).Run()


else:
    _display = Display()
    def _perform_click_input(button='left', coords=(0, 0),
                             button_down=True, button_up=True, double=False,
                             wheel_dist=0, pressed="", key_down=True, key_up=True):
        _move(coords)
        if button == 'wheel':
            if wheel_dist == 0:
                return
            if wheel_dist > 0:
                button = 'up_scroll'
            if wheel_dist < 0:
                button = 'down_scroll'
            for i in range(abs(wheel_dist)):
                _perform_click_input(button, coords)
        else:
            button = BUTTON_MAPPING[button]
            if button_down:
                fake_input(_display, X.ButtonPress, button)
                _display.sync()
            if button_up:
                fake_input(_display, X.ButtonRelease, button)
                _display.sync()


def click(button='left', coords=(0, 0)):
    "Click at the specified coordinates"
    _perform_click_input(button=button, coords=coords)


def double_click(button='left', coords=(0, 0)):
    "Double click at the specified coordinates"
    _perform_click_input(button=button, coords=coords)
    _perform_click_input(button=button, coords=coords)


def right_click(coords=(0, 0)):
    "Right click at the specified coords"
    _perform_click_input(button='right', coords=coords)


def move(coords=(0, 0)):
    "Move the mouse"
    _perform_click_input(button='move',coords=coords,button_down=False,button_up=False)


def press(button='left', coords=(0, 0)):
    "Press the mouse button"
    _perform_click_input(button='left', coords=coords, button_down=True, button_up=False)


def release(button='left', coords=(0, 0)):
    "Release the mouse button"
    _perform_click_input(button='left', coords=coords, button_down=False, button_up=True)


def scroll(coords=(0, 0), wheel_dist=1):
    "Do mouse wheel"
    if wheel_dist:
        _perform_click_input(button='wheel', wheel_dist=wheel_dist, coords=coords)


def wheel_click(coords=(0, 0)):
    "Middle mouse button click at the specified coords"
    _perform_click_input(button='middle', coords=coords)


def _move(coords=(0, 0)):
    x = int(coords[0])
    y = int(coords[1])
    fake_input(_display, X.MotionNotify, x=x, y=y)
    _display.sync()
