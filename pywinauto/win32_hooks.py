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

import six
from ctypes import wintypes
from ctypes import windll
from ctypes import CFUNCTYPE
from ctypes import POINTER
from ctypes import c_int
from ctypes import c_uint
from ctypes import byref
from ctypes import pointer
import atexit
import sys
import time

import win32con
import win32api

from .win32defines import VK_PACKET
from .actionlogger import ActionLogger
from .win32structures import KBDLLHOOKSTRUCT
from .win32structures import MSLLHOOKSTRUCT
from .win32structures import LRESULT

HOOKCB = CFUNCTYPE(LRESULT, c_int, wintypes.WPARAM, wintypes.LPARAM)

windll.kernel32.GetModuleHandleA.restype = wintypes.HMODULE
windll.kernel32.GetModuleHandleA.argtypes = [wintypes.LPCSTR]
windll.user32.SetWindowsHookExA.restype = wintypes.HHOOK
windll.user32.SetWindowsHookExA.argtypes = [c_int, HOOKCB, wintypes.HINSTANCE, wintypes.DWORD]
windll.user32.SetWindowsHookExW.restype = wintypes.HHOOK
windll.user32.SetWindowsHookExW.argtypes = [c_int, HOOKCB, wintypes.HINSTANCE, wintypes.DWORD]
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
windll.user32.PeekMessageW.restypes = wintypes.BOOL

# LRESULT WINAPI CallNextHookEx(
#   _In_opt_ HHOOK  hhk,
#   _In_     int    nCode,
#   _In_     WPARAM wParam,
#   _In_     LPARAM lParam
# );
windll.user32.CallNextHookEx.argtypes = [wintypes.HHOOK, c_int, wintypes.WPARAM, wintypes.LPARAM]
windll.user32.CallNextHookEx.restypes = LRESULT


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

    # TODO: use constants from win32con: VK_BACK, VK_TAB, VK_RETURN ...
    ID_TO_KEY = {1: 'LButton',  # win32con.VK_LBUTTON
                 2: 'RButton',  # win32con.VK_RBUTTON
                 3: 'Cancel',  # win32con.VK_CANCEL
                 4: 'MButton',  # win32con.VK_MBUTTON
                 5: 'XButton1',   # win32con.VK_XBUTTON1
                 6: 'XButton2',  # win32con.VK_XBUTTON2
                 7: 'Undefined1',
                 8: 'Back',
                 9: 'Tab',
                 10: 'Reserved1',
                 11: 'Reserved2',
                 12: 'Clear',  # win32con.VK_CLEAR
                 13: 'Return',  # win32con.VK_RETURN
                 14: 'Undefined2',
                 15: 'Undefined3',
                 16: 'SHIFT',  # win32con.VK_SHIFT
                 17: 'CONTROL',  # win32con.VK_CONTROL
                 18: 'Menu',  # win32con.VK_MENU
                 19: 'Pause',  # win32con.VK_PAUSE
                 20: 'Capital',
                 21: 'Kana',  # win32con.VK_KANA and win32con.VK_HANGUL
                 22: 'Undefined4',
                 23: 'Junja',  # win32con.VK_JUNJA
                 24: 'Final',  # win32con.VK_FINAL
                 25: 'Kanji',  # win32con.VK_KANJI and win32con.VK_HANJA
                 26: 'Undefined5',
                 27: 'Escape',
                 28: 'Convert',  # win32con.VK_CONVERT
                 29: 'NonConvert',  # win32con.VK_NONCONVERT
                 30: 'Accept',  # win32con.VK_ACCEPT
                 31: 'ModeChange',  # win32con.VK_MODECHANGE
                 32: 'Space',
                 33: 'Prior',
                 34: 'Next',
                 35: 'End',
                 36: 'Home',
                 37: 'Left',
                 38: 'Up',
                 39: 'Right',
                 40: 'Down',
                 41: 'Select',  # win32con.VK_SELECT
                 42: 'Print',  # win32con.VK_PRINT
                 43: 'Execute',  # win32con.VK_EXECUTE
                 44: 'Snapshot',
                 45: 'Insert',  # win32con.VK_INSERT
                 46: 'Delete',
                 47: 'Help',  # win32con.VK_HELP
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
                 58: 'Undefined6',
                 59: 'Undefined7',
                 60: 'Undefined8',
                 61: 'Undefined9',
                 62: 'Undefined10',
                 63: 'Undefined11',
                 64: 'Undefined12',
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
                 94: 'Reserved3',
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
                 108: 'Separator',  # win32con.VK_SEPARATOR
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
                 124: 'F13',
                 125: 'F14',
                 126: 'F15',
                 127: 'F16',
                 128: 'F17',
                 129: 'F18',
                 130: 'F19',
                 131: 'F20',
                 132: 'F21',
                 133: 'F22',
                 134: 'F23',
                 135: 'F24',
                 136: 'Unassigned1',
                 137: 'Unassigned2',
                 138: 'Unassigned3',
                 139: 'Unassigned4',
                 140: 'Unassigned5',
                 141: 'Unassigned6',
                 142: 'Unassigned7',
                 143: 'Unassigned8',
                 144: 'Numlock',
                 145: 'Scroll',  # win32con.VK_SCROLL
                 146: 'OemSpecific1',
                 147: 'OemSpecific2',
                 148: 'OemSpecific3',
                 149: 'OemSpecific4',
                 150: 'OemSpecific5',
                 151: 'OemSpecific6',
                 152: 'OemSpecific7',
                 153: 'OemSpecific8',
                 154: 'OemSpecific9',
                 155: 'OemSpecific10',
                 156: 'OemSpecific11',
                 157: 'OemSpecific12',
                 158: 'OemSpecific13',
                 159: 'OemSpecific14',
                 160: 'Lshift',
                 161: 'Rshift',
                 162: 'Lcontrol',
                 163: 'Rcontrol',
                 164: 'Lmenu',
                 165: 'Rmenu',
                 166: 'BrowserBack',  # win32con.VK_BROWSER_BACK
                 167: 'BrowserForward',  # win32con.VK_BROWSER_FORWARD
                 168: 'BrowserRefresh',  # not defined in win32con
                 169: 'BrowserStop',  # not defined in win32con
                 170: 'BrowserSearch',  # not defined in win32con
                 171: 'BrowserFavourites',  # not defined in win32con
                 172: 'BrowserHome',  # not defined in win32con
                 173: 'Volume_mute',  # win32con.VK_VOLUME_MUTE
                 174: 'Volume_down',  # win32con.VK_VOLUME_DOWN
                 175: 'Volume_up',  # win32con.VK_VOLUME_UP
                 176: 'NextTrack',  # win32con.VK_MEDIA_NEXT_TRACK
                 177: 'PrevTrack',  # win32con.VK_MEDIA_PREV_TRACK
                 178: 'StopTrack',  # not defined in win32con
                 179: 'PlayPause',  # win32con.VK_MEDIA_PLAY_PAUSE
                 180: 'LaunchMail',  # not defined in win32con
                 181: 'MediaSelect',  # not defined in win32con
                 182: 'LaunchApp1',  # not defined in win32con
                 183: 'LaunchApp2',  # not defined in win32con
                 184: 'Reserved4',
                 185: 'Reserved5',
                 186: 'Oem_1',
                 187: 'Oem_Plus',
                 188: 'Oem_Comma',
                 189: 'Oem_Minus',
                 190: 'Oem_Period',
                 191: 'Oem_2',
                 192: 'Oem_3',
                 193: 'Reserved6',
                 194: 'Reserved7',
                 195: 'Reserved8',
                 196: 'Reserved9',
                 197: 'Reserved10',
                 198: 'Reserved11',
                 199: 'Reserved12',
                 200: 'Reserved13',
                 201: 'Reserved14',
                 202: 'Reserved15',
                 203: 'Reserved16',
                 204: 'Reserved17',
                 205: 'Reserved18',
                 206: 'Reserved19',
                 207: 'Reserved20',
                 208: 'Reserved21',
                 209: 'Reserved22',
                 210: 'Reserved23',
                 211: 'Reserved24',
                 212: 'Reserved25',
                 213: 'Reserved26',
                 214: 'Reserved27',
                 215: 'Reserved28',
                 216: 'Unassigned9',
                 217: 'Unassigned10',
                 218: 'Unassigned11',
                 219: 'Oem_4',
                 220: 'Oem_5',
                 221: 'Oem_6',
                 222: 'Oem_7',
                 223: 'Oem_8',  # not defined in win32cona
                 224: 'Reserved29',
                 225: 'OemSpecific15',
                 226: 'Oem_102',
                 227: 'OemSpecific16',
                 228: 'OemSpecific17',
                 229: 'ProcessKey',  # win32con.VK_PROCESSKEY
                 230: 'OemSpecific18',
                 231: 'VkPacket',  # win32con.VK_PACKET. It has a special processing in kbd_ll !
                 232: 'Unassigned12',
                 233: 'OemSpecific19',
                 234: 'OemSpecific20',
                 235: 'OemSpecific21',
                 236: 'OemSpecific22',
                 237: 'OemSpecific23',
                 238: 'OemSpecific24',
                 239: 'OemSpecific25',
                 240: 'OemSpecific26',
                 241: 'OemSpecific27',
                 242: 'OemSpecific28',
                 243: 'OemSpecific29',
                 244: 'OemSpecific30',
                 245: 'OemSpecific31',
                 246: 'Attn',  # win32con.VK_ATTN
                 247: 'CrSel',  # win32con.VK_CRSEL
                 248: 'ExSel',  # win32con.VK_EXSEL
                 249: 'ErEOF',  # win32con.VK_EREOF
                 250: 'Play',  # win32con.VK_PLAY
                 251: 'Zoom',  # win32con.VK_ZOOM
                 252: 'Noname',  # win32con.VK_NONAME
                 253: 'PA1',  # win32con.VK_PA1
                 254: 'OemClear',  # win32con.VK_OEM_CLEAR
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

    event_types = {win32con.WM_KEYDOWN: 'key down',     # WM_KEYDOWN for normal keys
                   win32con.WM_KEYUP: 'key up',         # WM_KEYUP for normal keys
                   win32con.WM_SYSKEYDOWN: 'key down',  # WM_SYSKEYDOWN, is used for Alt key.
                   win32con.WM_SYSKEYUP: 'key up',      # WM_SYSKEYUP, is used for Alt key.
                   }

    def __init__(self):
        self.handler = None
        self.pressed_keys = []
        self.keyboard_id = None
        self.mouse_id = None
        self.mouse_is_hook = False
        self.keyboard_is_hook = False

    def _process_kbd_data(self, kb_data_ptr):
        """Process KBDLLHOOKSTRUCT data received from low level keyboard hook calls"""
        kbd = KBDLLHOOKSTRUCT.from_address(kb_data_ptr)
        current_key = None
        key_code = kbd.vkCode
        if key_code == VK_PACKET:
            scan_code = kbd.scanCode
            current_key = six.unichr(scan_code)
        elif key_code in self.ID_TO_KEY:
            current_key = six.u(self.ID_TO_KEY[key_code])
        else:
            al = ActionLogger()
            al.log("_process_kbd_data, bad key_code: {0}".format(key_code))

        return current_key

    def _process_kbd_msg_type(self, event_code, current_key):
        """Process event codes from low level keyboard hook calls"""
        event_type = None
        event_code_word = 0xFFFFFFFF & event_code
        if event_code_word in self.event_types:
            event_type = self.event_types[event_code_word]
        else:
            al = ActionLogger()
            al.log("_process_kbd_msg_type, bad event_type: {0}".format(event_type))

        if event_type == 'key down':
            self.pressed_keys.append(current_key)
        elif event_type == 'key up':
            if current_key in self.pressed_keys:
                self.pressed_keys.remove(current_key)
            else:
                al = ActionLogger()
                al.log("_process_kbd_msg_type, can't remove a key: {0}".format(current_key))

        return event_type

    def _keyboard_ll_hdl(self, code, event_code, kb_data_ptr):
        """Execute when a keyboard low level event has been triggered"""
        try:
            # The next hook in chain must be always called
            res = windll.user32.CallNextHookEx(self.keyboard_id,
                                               code,
                                               event_code,
                                               kb_data_ptr)
            if not self.handler:
                return res

            current_key = self._process_kbd_data(kb_data_ptr)
            event_type = self._process_kbd_msg_type(event_code, current_key)
            event = KeyboardEvent(current_key, event_type, self.pressed_keys)
            self.handler(event)

        except Exception:
            al = ActionLogger()
            al.log("_keyboard_ll_hdl, {0}".format(sys.exc_info()[0]))
            al.log("_keyboard_ll_hdl, code {0}, event_code {1}".format(code, event_code))
            raise

        return res

    def _mouse_ll_hdl(self, code, event_code, mouse_data_ptr):
        """Execute when a mouse low level event has been triggerred"""
        try:
            # The next hook in chain must be always called
            res = windll.user32.CallNextHookEx(self.mouse_id, code, event_code, mouse_data_ptr)
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
                ms = MSLLHOOKSTRUCT.from_address(mouse_data_ptr)
                event = MouseEvent(current_key, event_type, ms.pt.x, ms.pt.y)
                self.handler(event)

        except Exception:
            al = ActionLogger()
            al.log("_mouse_ll_hdl, {0}".format(sys.exc_info()[0]))
            al.log("_mouse_ll_hdl, code {0}, event_code {1}".format(code, event_code))
            raise

        return res

    def hook(self, keyboard=True, mouse=False):
        """Hook mouse and/or keyboard events"""
        if not (mouse or keyboard):
            return

        self.mouse_is_hook = mouse
        self.keyboard_is_hook = keyboard

        if self.keyboard_is_hook:
            @HOOKCB
            def _kbd_ll_cb(ncode, wparam, lparam):
                """Forward the hook event to ourselves"""
                return self._keyboard_ll_hdl(ncode, wparam, lparam)

            self.keyboard_id = windll.user32.SetWindowsHookExW(
                win32con.WH_KEYBOARD_LL,
                _kbd_ll_cb,
                win32api.GetModuleHandle(None),
                0)

        if self.mouse_is_hook:
            @HOOKCB
            def _mouse_ll_cb(code, event_code, mouse_data_ptr):
                """Forward the hook event to ourselves"""
                return self._mouse_ll_hdl(code, event_code, mouse_data_ptr)

            self.mouse_id = windll.user32.SetWindowsHookExA(
                win32con.WH_MOUSE_LL,
                _mouse_ll_cb,
                win32api.GetModuleHandle(None),
                0)

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

    def stop(self):
        """Stop the listening loop"""
        self.unhook_keyboard()
        self.unhook_mouse()

    def is_hooked(self):
        """Verify if any of hooks are active"""
        return self.mouse_is_hook or self.keyboard_is_hook

    def _process_win_msgs(self):
        """Peek and process queued windows messages"""
        message = wintypes.MSG()
        while True:
            res = windll.user32.PeekMessageW(pointer(message), 0, 0, 0, win32con.PM_REMOVE)
            if not res:
                break
            if message.message == win32con.WM_QUIT:
                self.stop()
                sys.exit(0)
            else:
                windll.user32.TranslateMessage(byref(message))
                windll.user32.DispatchMessageW(byref(message))

    def listen(self):
        """Listen for events"""
        atexit.register(windll.user32.UnhookWindowsHookEx, self.keyboard_id)
        atexit.register(windll.user32.UnhookWindowsHookEx, self.mouse_id)

        while self.is_hooked():
            self._process_win_msgs()
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
