# GUI Application automation and testing library
# Copyright (C) 2006-2016 Mark Mc Mahon and Contributors
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

"""
Windows global hooks in pure Python

The implementation uses foreign function interface (FFI) provided by
standard Python module **ctypes** and inspired by pyHook, pyhooked and other
similar modules (the code was re-written from scratch). It tends to be
a superset of pyHook but in pure Python only so it doesn't require compilation.

Current set of hooks implemented:
 * WH_MOUSE_LL
 * WH_KEYBOARD_LL

More detailed documentation about Windows hooks can be found in MSDN:
https://msdn.microsoft.com/en-us/library/windows/desktop/ms632589.aspx

This module can be used as a stand alone or along with pywinauto.
The fork of this code (at some moment) was used in
standalone library pyhooked 0.8 maintained by Ethan Smith.
"""

from ctypes import wintypes
from ctypes import windll
from ctypes import CFUNCTYPE
from ctypes import POINTER
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_void_p
from ctypes import byref
import atexit
import sys
import time

cmp_func = CFUNCTYPE(c_int, c_int, wintypes.HINSTANCE, POINTER(c_void_p))

windll.kernel32.GetModuleHandleA.restype = wintypes.HMODULE
windll.kernel32.GetModuleHandleA.argtypes = [wintypes.LPCWSTR]
windll.user32.SetWindowsHookExA.restype = c_int
windll.user32.SetWindowsHookExA.argtypes = [c_int, cmp_func, wintypes.HINSTANCE, wintypes.DWORD]
windll.user32.GetMessageW.argtypes = [POINTER(wintypes.MSG), wintypes.HWND, c_uint, c_uint]
windll.user32.TranslateMessage.argtypes = [POINTER(wintypes.MSG)]
windll.user32.DispatchMessageW.argtypes = [POINTER(wintypes.MSG)]

# BOOL WINAPI PeekMessage(
#  _Out_    LPMSG lpMsg,
#  _In_opt_ HWND  hWnd,
#  _In_     UINT  wMsgFilterMin,
#  _In_     UINT  wMsgFilterMax,
#  _In_     UINT  wRemoveMsg
#);
windll.user32.PeekMessageW.argtypes = [POINTER(wintypes.MSG), wintypes.HWND, c_uint, c_uint, c_uint]


def _callback_pointer(handler):
    """Create and return C-pointer"""
    return cmp_func(handler)


class KeyboardEvent(object):

    """Created when a keyboard event happened"""

    def __init__(self, current_key=None, event_type=None, pressed_key=None):
        self.current_key = current_key
        self.event_type = event_type
        self.pressed_key = pressed_key


class MouseEvent(object):

    """Created when a mouse event happened"""

    def __init__(self, current_key=None, event_type=None, mouse_x=0, mouse_y=0):
        self.current_key = current_key
        self.event_type = event_type
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y


class Hook(object):

    """Hook for low level keyboard and mouse events"""

    MOUSE_ID_TO_KEY = {512: 'Move',
                       513: 'LButton',
                       514: 'LButton',
                       516: 'RButton',
                       517: 'RButton',
                       519: 'WheelButton',
                       520: 'WheelButton',
                       522: 'Wheel'}

    MOUSE_ID_TO_EVENT_TYPE = {512: None,
                              513: 'key down',
                              514: 'key up',
                              516: 'key down',
                              517: 'key up',
                              519: 'key down',
                              520: 'key up',
                              522: None}

    ID_TO_KEY = {8: 'Back',
                 9: 'Tab',
                 13: 'Return',
                 20: 'Capital',
                 27: 'Escape',
                 32: 'Space',
                 33: 'Prior',
                 34: 'Next',
                 35: 'End',
                 36: 'Home',
                 37: 'Left',
                 38: 'Up',
                 39: 'Right',
                 40: 'Down',
                 44: 'Snapshot',
                 46: 'Delete',
                 48: '0',
                 49: '1',
                 50: '2',
                 51: '3',
                 52: '4',
                 53: '5',
                 54: '6',
                 55: '7',
                 56: '8',
                 57: '9',
                 65: 'A',
                 66: 'B',
                 67: 'C',
                 68: 'D',
                 69: 'E',
                 70: 'F',
                 71: 'G',
                 72: 'H',
                 73: 'I',
                 74: 'J',
                 75: 'K',
                 76: 'L',
                 77: 'M',
                 78: 'N',
                 79: 'O',
                 80: 'P',
                 81: 'Q',
                 82: 'R',
                 83: 'S',
                 84: 'T',
                 85: 'U',
                 86: 'V',
                 87: 'W',
                 88: 'X',
                 89: 'Y',
                 90: 'Z',
                 91: 'Lwin',
                 92: 'Rwin',
                 93: 'App',
                 95: 'Sleep',
                 96: 'Numpad0',
                 97: 'Numpad1',
                 98: 'Numpad2',
                 99: 'Numpad3',
                 100: 'Numpad4',
                 101: 'Numpad5',
                 102: 'Numpad6',
                 103: 'Numpad7',
                 104: 'Numpad8',
                 105: 'Numpad9',
                 106: 'Multiply',
                 107: 'Add',
                 109: 'Subtract',
                 110: 'Decimal',
                 111: 'Divide',
                 112: 'F1',
                 113: 'F2',
                 114: 'F3',
                 115: 'F4',
                 116: 'F5',
                 117: 'F6',
                 118: 'F7',
                 119: 'F8',
                 120: 'F9',
                 121: 'F10',
                 122: 'F11',
                 123: 'F12',
                 144: 'Numlock',
                 160: 'Lshift',
                 161: 'Rshift',
                 162: 'Lcontrol',
                 163: 'Rcontrol',
                 164: 'Lmenu',
                 165: 'Rmenu',
                 186: 'Oem_1',
                 187: 'Oem_Plus',
                 188: 'Oem_Comma',
                 189: 'Oem_Minus',
                 190: 'Oem_Period',
                 191: 'Oem_2',
                 192: 'Oem_3',
                 219: 'Oem_4',
                 220: 'Oem_5',
                 221: 'Oem_6',
                 222: 'Oem_7',
                 1001: 'mouse left',  # mouse hotkeys
                 1002: 'mouse right',
                 1003: 'mouse middle',
                 1000: 'mouse move',  # single event hotkeys
                 1004: 'mouse wheel up',
                 1005: 'mouse wheel down',
                 1010: 'Ctrl',  # merged hotkeys
                 1011: 'Alt',
                 1012: 'Shift',
                 1013: 'Win'}

    event_types = {0x100: 'key down',  # WM_KeyDown for normal keys
                   0x101: 'key up',  # WM_KeyUp for normal keys
                   0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
                   0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
                   }

    WH_KEYBOARD_LL = 0x00D
    WH_MOUSE_LL = 0x0E
    WM_QUIT = 0x0012

    def __init__(self):
        self.handler = 0
        self.pressed_keys = []
        self.keyboard_id = None
        self.mouse_id = None
        self.mouse_is_hook = False
        self.keyboard_is_hook = False

    def hook(self, keyboard=True, mouse=False):
        """Hook mouse and/or keyboard events"""
        self.mouse_is_hook = mouse
        self.keyboard_is_hook = keyboard

        if not self.mouse_is_hook and not self.keyboard_is_hook:
            return

        if self.keyboard_is_hook:
            def keyboard_low_level_handler(code, event_code, kb_data_ptr):
                """Execute when keyboard low level event was catched"""
                try:
                    key_code = 0xFFFFFFFF & kb_data_ptr[0]
                    current_key = self.ID_TO_KEY[key_code]
                    event_type = self.event_types[0xFFFFFFFF & event_code]

                    if event_type == 'key down':
                        self.pressed_keys.append(current_key)

                    if event_type == 'key up':
                        self.pressed_keys.remove(current_key)

                    event = KeyboardEvent(current_key, event_type, self.pressed_keys)

                    if self.handler != 0:
                        self.handler(event)

                finally:
                    # TODO: think how to resolve Landscape.io warning:
                    # "return statement in finally block may swallow exception"
                    return windll.user32.CallNextHookEx(self.keyboard_id, code, event_code, kb_data_ptr)

            keyboard_pointer = _callback_pointer(keyboard_low_level_handler)

            self.keyboard_id = windll.user32.SetWindowsHookExA(self.WH_KEYBOARD_LL, keyboard_pointer,
                                                               windll.kernel32.GetModuleHandleA(None),
                                                               0)

        if self.mouse_is_hook:
            def mouse_low_level_handler(code, event_code, kb_data_ptr):
                """Execute when mouse low level event was catched"""
                try:
                    current_key = self.MOUSE_ID_TO_KEY[event_code]
                    if current_key != 'Move':
                        event_type = self.MOUSE_ID_TO_EVENT_TYPE[event_code]
                        #the first two members of kb_data_ptr hold the mouse position, x and y
                        event = MouseEvent(current_key, event_type, kb_data_ptr[0], kb_data_ptr[1])

                        if self.handler != 0:
                            self.handler(event)

                finally:
                    # TODO: think how to resolve Landscape.io warning:
                    # "return statement in finally block may swallow exception"
                    return windll.user32.CallNextHookEx(self.mouse_id, code, event_code, kb_data_ptr)

            mouse_pointer = _callback_pointer(mouse_low_level_handler)
            self.mouse_id = windll.user32.SetWindowsHookExA(self.WH_MOUSE_LL, mouse_pointer,
                                                            windll.kernel32.GetModuleHandleA(None), 0)

        self.listen()

    def unhook_mouse(self):
        """Unhook mouse events"""
        if self.mouse_is_hook:
            self.mouse_is_hook = False
            windll.user32.UnhookWindowsHookEx(self.mouse_id)

    def unhook_keyboard(self):
        """Unhook keyboard events"""
        if self.keyboard_is_hook:
            self.keyboard_is_hook = False
            windll.user32.UnhookWindowsHookEx(self.keyboard_id)

    def listen(self):
        """Listen events"""
        atexit.register(windll.user32.UnhookWindowsHookEx, self.keyboard_id)
        atexit.register(windll.user32.UnhookWindowsHookEx, self.mouse_id)

        WM_QUIT = 0x12
        PM_REMOVE = 1
        message = wintypes.MSG()

        while self.mouse_is_hook or self.keyboard_is_hook:
            while True:
                res = windll.user32.PeekMessageW(byref(message), 0, 0, 0, PM_REMOVE)
                if not res:
                    break
                if message.message == WM_QUIT:
                    self.unhook_keyboard()
                    self.unhook_mouse()
                    sys.exit(0)
                else:
                    windll.user32.TranslateMessage(byref(message))
                    windll.user32.DispatchMessageW(byref(message))
            time.sleep(0.02)


if __name__ == "__main__":

    def on_event(args):
        """Callback for keyboard and mouse events"""
        if isinstance(args, KeyboardEvent):
            if args.current_key == 'A' and args.event_type == 'key down' and 'Lcontrol' in args.pressed_key:
                print("Ctrl + A was pressed")

            if args.current_key == 'K' and args.event_type == 'key down':
                print("K was pressed")

            if args.current_key == 'M' and args.event_type == 'key down' and 'U' in args.pressed_key:
                hk.unhook_mouse()
                print("Unhook mouse")

            if args.current_key == 'K' and args.event_type == 'key down' and 'U' in args.pressed_key:
                hk.unhook_keyboard()
                print("Unhook keyboard")

        if isinstance(args, MouseEvent):
            if args.current_key == 'RButton' and args.event_type == 'key down':
                print("Right button pressed at ({0}, {1})".format(args.mouse_x, args.mouse_y))

            if args.current_key == 'WheelButton' and args.event_type == 'key down':
                print("Wheel button pressed")

    hk = Hook()
    hk.handler = on_event
    hk.hook(keyboard=True, mouse=True)
