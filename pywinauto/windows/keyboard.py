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

"""Windows branch of the keyboard module

"""
import six

from ctypes import wintypes
from ctypes import windll
from ctypes import CFUNCTYPE
from ctypes import c_int
from ctypes import byref
from ctypes import pointer
from ctypes import sizeof
import atexit
import sys
import time
import string

import win32con
import win32api

from .win32defines import VK_PACKET
from ..actionlogger import ActionLogger
from . import win32functions
from . import win32structures
from .win32structures import KBDLLHOOKSTRUCT
from .win32structures import LRESULT
from .. import deprecated

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

__all__ = ['KeySequenceError', 'send_keys']

# pylint: disable-msg=R0903

DEBUG = 0

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP = 2
KEYEVENTF_UNICODE = 4
KEYEVENTF_SCANCODE = 8
VK_SHIFT = 16
VK_CONTROL = 17
VK_MENU = 18

# 'codes' recognized as {CODE( repeat)?}
CODES = {
    'BACK': 8,
    'BACKSPACE': 8,
    'BKSP': 8,
    'BREAK': 3,
    'BS': 8,
    'CAP': 20,
    'CAPSLOCK': 20,
    'DEL': 46,
    'DELETE': 46,
    'DOWN': 40,
    'END': 35,
    'ENTER': 13,
    'ESC': 27,
    'F1': 112,
    'F2': 113,
    'F3': 114,
    'F4': 115,
    'F5': 116,
    'F6': 117,
    'F7': 118,
    'F8': 119,
    'F9': 120,
    'F10': 121,
    'F11': 122,
    'F12': 123,
    'F13': 124,
    'F14': 125,
    'F15': 126,
    'F16': 127,
    'F17': 128,
    'F18': 129,
    'F19': 130,
    'F20': 131,
    'F21': 132,
    'F22': 133,
    'F23': 134,
    'F24': 135,
    'HELP': 47,
    'HOME': 36,
    'INS': 45,
    'INSERT': 45,
    'LEFT': 37,
    'LWIN': 91,
    'NUMLOCK': 144,
    'PGDN': 34,
    'PGUP': 33,
    'PRTSC': 44,
    'RIGHT': 39,
    'RMENU': 165,
    'RWIN': 92,
    'SCROLLLOCK': 145,
    'SPACE': 32,
    'TAB': 9,
    'UP': 38,

    'VK_ACCEPT': 30,
    'VK_ADD': 107,
    'VK_APPS': 93,
    'VK_ATTN': 246,
    'VK_BACK': 8,
    'VK_CANCEL': 3,
    'VK_CAPITAL': 20,
    'VK_CLEAR': 12,
    'VK_CONTROL': 17,
    'VK_CONVERT': 28,
    'VK_CRSEL': 247,
    'VK_DECIMAL': 110,
    'VK_DELETE': 46,
    'VK_DIVIDE': 111,
    'VK_DOWN': 40,
    'VK_END': 35,
    'VK_EREOF': 249,
    'VK_ESCAPE': 27,
    'VK_EXECUTE': 43,
    'VK_EXSEL': 248,
    'VK_F1': 112,
    'VK_F2': 113,
    'VK_F3': 114,
    'VK_F4': 115,
    'VK_F5': 116,
    'VK_F6': 117,
    'VK_F7': 118,
    'VK_F8': 119,
    'VK_F9': 120,
    'VK_F10': 121,
    'VK_F11': 122,
    'VK_F12': 123,
    'VK_F13': 124,
    'VK_F14': 125,
    'VK_F15': 126,
    'VK_F16': 127,
    'VK_F17': 128,
    'VK_F18': 129,
    'VK_F19': 130,
    'VK_F20': 131,
    'VK_F21': 132,
    'VK_F22': 133,
    'VK_F23': 134,
    'VK_F24': 135,
    'VK_FINAL': 24,
    'VK_HANGEUL': 21,
    'VK_HANGUL': 21,
    'VK_HANJA': 25,
    'VK_HELP': 47,
    'VK_HOME': 36,
    'VK_INSERT': 45,
    'VK_JUNJA': 23,
    'VK_KANA': 21,
    'VK_KANJI': 25,
    'VK_LBUTTON': 1,
    'VK_LCONTROL': 162,
    'VK_LEFT': 37,
    'VK_LMENU': 164,
    'VK_LSHIFT': 160,
    'VK_LWIN': 91,
    'VK_MBUTTON': 4,
    'VK_MENU': 18,
    'VK_MODECHANGE': 31,
    'VK_MULTIPLY': 106,
    'VK_NEXT': 34,
    'VK_NONAME': 252,
    'VK_NONCONVERT': 29,
    'VK_NUMLOCK': 144,
    'VK_NUMPAD0': 96,
    'VK_NUMPAD1': 97,
    'VK_NUMPAD2': 98,
    'VK_NUMPAD3': 99,
    'VK_NUMPAD4': 100,
    'VK_NUMPAD5': 101,
    'VK_NUMPAD6': 102,
    'VK_NUMPAD7': 103,
    'VK_NUMPAD8': 104,
    'VK_NUMPAD9': 105,
    'VK_OEM_CLEAR': 254,
    'VK_PA1': 253,
    'VK_PAUSE': 19,
    'VK_PLAY': 250,
    'VK_PRINT': 42,
    'VK_PRIOR': 33,
    'VK_PROCESSKEY': 229,
    'VK_RBUTTON': 2,
    'VK_RCONTROL': 163,
    'VK_RETURN': 13,
    'VK_RIGHT': 39,
    'VK_RMENU': 165,
    'VK_RSHIFT': 161,
    'VK_RWIN': 92,
    'VK_SCROLL': 145,
    'VK_SELECT': 41,
    'VK_SEPARATOR': 108,
    'VK_SHIFT': 16,
    'VK_SNAPSHOT': 44,
    'VK_SPACE': 32,
    'VK_SUBTRACT': 109,
    'VK_TAB': 9,
    'VK_UP': 38,
    'ZOOM': 251,
    'VK_MEDIA_NEXT_TRACK': 176,
    'VK_MEDIA_PREV_TRACK': 177,
    'VK_MEDIA_STOP': 178,
    'VK_MEDIA_PLAY_PAUSE': 179
}
# reverse the CODES dict to make it easy to look up a particular code name
CODE_NAMES = dict((entry[1], entry[0]) for entry in CODES.items())

# modifier keys
MODIFIERS = {
    '+': VK_SHIFT,
    '^': VK_CONTROL,
    '%': VK_MENU,
}

# Virtual keys that map to an ASCII character
# See https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
ascii_vk = {
    ' ': 0x20,
    '=': 0xbb,
    ',': 0xbc,
    '-': 0xbd,
    '.': 0xbe,
    # According to the above reference, the following characters vary per region.
    # This mapping applies to US keyboards
    ';': 0xba,
    '/': 0xbf,
    '`': 0xc0,
    '[': 0xdb,
    '\\': 0xdc,
    ']': 0xdd,
    '\'': 0xde,
}
# [0-9A-Z] map exactly to their ASCII counterparts
ascii_vk.update(dict((c, ord(c)) for c in string.ascii_uppercase + string.digits))
# map [a-z] to their uppercase ASCII counterparts
ascii_vk.update(dict((c, ord(c.upper())) for c in string.ascii_lowercase))


class KeySequenceError(Exception):

    """Exception raised when a key sequence string has a syntax error"""

    def __str__(self):
        return ' '.join(self.args)


class KeyboardEvent(object):

    """Created when a keyboard event happened"""

    def __init__(self, current_key=None, event_type=None, pressed_key=None):
        self.current_key = current_key
        self.event_type = event_type
        self.pressed_key = pressed_key


class KeyboardHook(object):

    """Hook for low level keyboard events"""

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
                 223: 'Oem_8',  # not defined in win32con
                 224: 'Reserved29',
                 225: 'OemSpecific15',
                 226: 'Oem_102',
                 227: 'OemSpecific16',
                 228: 'OemSpecific17',
                 229: 'ProcessKey',  # win32con.VK_PROCESSKEY
                 230: 'OemSpecific18',
                 231: 'VkPacket',  # win32con.VK_PACKET. It has a special processing in KeyboardHook._process_data !
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
        self.id = None
        self.is_hook = False

    def _process_data(self, data_ptr):
        """Process KBDLLHOOKSTRUCT data received from low level keyboard hook calls"""
        kbd = KBDLLHOOKSTRUCT.from_address(data_ptr)
        current_key = None
        key_code = kbd.vkCode
        if key_code == VK_PACKET:
            scan_code = kbd.scanCode
            current_key = six.unichr(scan_code)
        elif key_code in self.ID_TO_KEY:
            current_key = six.u(self.ID_TO_KEY[key_code])
        else:
            al = ActionLogger()
            al.log("_process_data, bad key_code: {0}".format(key_code))

        return current_key

    def _process_msg_type(self, event_code, current_key):
        """Process event codes from low level keyboard hook calls"""
        event_type = None
        event_code_word = 0xFFFFFFFF & event_code
        if event_code_word in self.event_types:
            event_type = self.event_types[event_code_word]
        else:
            al = ActionLogger()
            al.log("_process_msg_type, bad event_type: {0}".format(event_type))

        if event_type == 'key down' and current_key not in self.pressed_keys:
            self.pressed_keys.append(current_key)
        elif event_type == 'key up':
            if current_key in self.pressed_keys:
                self.pressed_keys.remove(current_key)
            else:
                al = ActionLogger()
                al.log("_process_msg_type, can't remove a key: {0}".format(current_key))

        return event_type

    def _ll_hdl(self, code, event_code, data_ptr):
        """Execute when a keyboard low level event has been triggered"""
        try:
            # The next hook in chain must be always called
            res = windll.user32.CallNextHookEx(self.id,
                                               code,
                                               event_code,
                                               data_ptr)
            if not self.handler:
                return res

            current_key = self._process_data(data_ptr)
            event_type = self._process_msg_type(event_code, current_key)
            event = KeyboardEvent(current_key, event_type, self.pressed_keys)
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
        def _ll_cb(ncode, wparam, lparam):
            """Forward the hook event to ourselves"""
            return self._ll_hdl(ncode, wparam, lparam)

        self.id = windll.user32.SetWindowsHookExW(
            win32con.WH_KEYBOARD_LL,
            _ll_cb,
            win32api.GetModuleHandle(None),
            0)

        self.listen()

    def unhook(self):
        """Unhook keyboard events"""
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


class KeyAction(object):

    """Class that represents a single keyboard action

    It represents either a PAUSE action (not really keyboard) or a keyboard
    action (press or release or both) of a particular key.
    """

    def __init__(self, key, down=True, up=True):
        self.key = key
        if isinstance(self.key, six.string_types):
            self.key = six.text_type(key)
        self.down = down
        self.up = up

    def _get_key_info(self):
        """Return virtual_key, scan_code, and flags for the action

        This is one of the methods that will be overridden by sub classes.
        """
        return 0, ord(self.key), KEYEVENTF_UNICODE

    def get_key_info(self):
        """Return virtual_key, scan_code, and flags for the action

        This is one of the methods that will be overridden by sub classes.
        """
        return self._get_key_info()

    def GetInput(self):
        """Build the INPUT structure for the action"""
        actions = 1
        # if both up and down
        if self.up and self.down:
            actions = 2

        inputs = (win32structures.INPUT * actions)()

        vk, scan, flags = self._get_key_info()

        for inp in inputs:
            inp.type = INPUT_KEYBOARD

            inp.ki.wVk = vk
            inp.ki.wScan = scan
            inp.ki.dwFlags |= flags

            # it seems to return 0 every time but it's required by MSDN specification
            # so call it just in case
            inp.ki.dwExtraInfo = win32functions.GetMessageExtraInfo()

        # if we are releasing - then let it up
        if self.up:
            inputs[-1].ki.dwFlags |= KEYEVENTF_KEYUP

        return inputs

    def run(self):
        """Execute the action"""
        inputs = self.GetInput()

        # SendInput() supports all Unicode symbols
        num_inserted_events = win32functions.SendInput(len(inputs), byref(inputs),
                                        sizeof(win32structures.INPUT))
        if num_inserted_events != len(inputs):
            raise RuntimeError('SendInput() inserted only ' + str(num_inserted_events) +
                               ' out of ' + str(len(inputs)) + ' keyboard events')

    def _get_down_up_string(self):
        """Return a string that will show whether the string is up or down

        return 'down' if the key is a press only
        return 'up' if the key is up only
        return '' if the key is up & down (as default)
        """
        down_up = ""
        if not (self.down and self.up):
            if self.down:
                down_up = "down"
            elif self.up:
                down_up = "up"
        return down_up

    def key_description(self):
        """Return a description of the key"""
        vk, scan, flags = self._get_key_info()
        desc = ''
        if vk:
            if vk in CODE_NAMES:
                desc = CODE_NAMES[vk]
            else:
                desc = "VK {}".format(vk)
        else:
            desc = "{}".format(self.key)

        return desc

    def __str__(self):
        parts = []
        parts.append(self.key_description())
        up_down = self._get_down_up_string()
        if up_down:
            parts.append(up_down)

        return "<{}>".format(" ".join(parts))

    __repr__ = __str__


class VirtualKeyAction(KeyAction):

    """Represents a virtual key action e.g. F9 DOWN, etc

    Overrides necessary methods of KeyAction
    """

    def _get_key_info(self):
        """Virtual keys have extended flag set"""
        # copied more or less verbatim from
        # http://www.pinvoke.net/default.aspx/user32.sendinput
        if 33 <= self.key <= 46 or 91 <= self.key <= 93:
            flags = KEYEVENTF_EXTENDEDKEY
        else:
            flags = 0
        # This works for %{F4} - ALT + F4
        # return self.key, 0, 0

        # this works for Tic Tac Toe i.e. +{RIGHT} SHIFT + RIGHT
        return self.key, win32functions.MapVirtualKeyW(self.key, 0), flags

    def run(self):
        """Execute the action"""
        # it works more stable for virtual keys than SendInput
        for inp in self.GetInput():
            win32api.keybd_event(inp.ki.wVk, inp.ki.wScan, inp.ki.dwFlags)


class EscapedKeyAction(KeyAction):

    """Represents an escaped key action e.g. F9 DOWN, etc

    Overrides necessary methods of KeyAction
    """

    def _get_key_info(self):
        """EscapedKeyAction doesn't send it as Unicode

        The vk and scan code are generated differently.
        """
        vkey_scan = LoByte(win32functions.VkKeyScanW(self.key))

        return (vkey_scan, win32functions.MapVirtualKeyW(vkey_scan, 0), 0)

    def key_description(self):
        """Return a description of the key"""
        return "KEsc {}".format(self.key)

    def run(self):
        """Execute the action"""
        # it works more stable for virtual keys than SendInput
        for inp in self.GetInput():
            win32api.keybd_event(inp.ki.wVk, inp.ki.wScan, inp.ki.dwFlags)


class PauseAction(object):

    """Represents a pause action"""

    def __init__(self, how_long):
        self.how_long = how_long

    def run(self):
        """Pause for the lenght of time specified"""
        time.sleep(self.how_long)

    def __str__(self):
        return "<PAUSE %1.2f>" % (self.how_long)

    __repr__ = __str__


def handle_code(code, vk_packet):
    """Handle a key or sequence of keys in braces"""
    code_keys = []
    # it is a known code (e.g. {DOWN}, {ENTER}, etc)
    if code in CODES:
        code_keys.append(VirtualKeyAction(CODES[code]))

    # it is an escaped modifier e.g. {%}, {^}, {+}
    elif len(code) == 1:
        if not vk_packet and code in ascii_vk:
            code_keys.append(VirtualKeyAction(ascii_vk[code]))
        else:
            code_keys.append(KeyAction(code))

    # it is a repetition or a pause  {DOWN 5}, {PAUSE 1.3}
    elif ' ' in code:
        to_repeat, count = code.rsplit(None, 1)
        if to_repeat == "PAUSE":
            try:
                pause_time = float(count)
            except ValueError:
                raise KeySequenceError('invalid pause time %s'% count)
            code_keys.append(PauseAction(pause_time))

        else:
            try:
                count = int(count)
            except ValueError:
                raise KeySequenceError(
                    'invalid repetition count {}'.format(count))

            # If the value in to_repeat is a VK e.g. DOWN
            # we need to add the code repeated
            if to_repeat in CODES:
                code_keys.extend(
                    [VirtualKeyAction(CODES[to_repeat])] * count)
            # otherwise parse the keys and we get back a KeyAction
            else:
                to_repeat = parse_keys(to_repeat, vk_packet=vk_packet)
                if isinstance(to_repeat, list):
                    keys = to_repeat * count
                else:
                    keys = [to_repeat] * count
                code_keys.extend(keys)
    else:
        raise RuntimeError("Unknown code: {}".format(code))

    return code_keys


def parse_keys(string,
               with_spaces=False,
               with_tabs=False,
               with_newlines=False,
               modifiers=None,
               vk_packet=True):
    """Return the parsed keys"""
    keys = []
    if not modifiers:
        modifiers = []

    should_escape_next_keys = False
    index = 0
    while index < len(string):

        c = string[index]
        index += 1
        # check if one of CTRL, SHIFT, ALT has been pressed
        if c in MODIFIERS.keys():
            modifier = MODIFIERS[c]
            # remember that we are currently modified
            modifiers.append(modifier)
            # hold down the modifier key
            keys.append(VirtualKeyAction(modifier, up=False))
            if DEBUG:
                print("MODS+", modifiers)
            continue

        # Apply modifiers over a bunch of characters (not just one!)
        elif c == "(":
            # find the end of the bracketed text
            end_pos = string.find(")", index)
            if end_pos == -1:
                raise KeySequenceError('`)` not found')
            keys.extend(parse_keys(
                    string[index:end_pos],
                    modifiers=modifiers,
                    vk_packet=vk_packet))
            index = end_pos + 1

        # Escape or named key
        elif c == "{":
            # We start searching from index + 1 to account for the case {}}
            end_pos = string.find("}", index+1)
            if end_pos == -1:
                raise KeySequenceError('`}` not found')

            code = string[index:end_pos]
            index = end_pos + 1
            key_events = [' up', ' down']
            current_key_event = None
            if any(key_event in code.lower() for key_event in key_events):
                code, current_key_event = code.split(' ')
                should_escape_next_keys = True
            current_keys = handle_code(code, vk_packet)
            if current_key_event is not None:
                if isinstance(current_keys[0].key, six.string_types):
                    current_keys[0] = EscapedKeyAction(current_keys[0].key)

                if current_key_event.strip() == 'up':
                    current_keys[0].down = False
                else:
                    current_keys[0].up = False
            keys.extend(current_keys)

        # unmatched ")"
        elif c == ')':
            raise KeySequenceError('`)` should be preceeded by `(`')

        # unmatched "}"
        elif c == '}':
            raise KeySequenceError('`}` should be preceeded by `{`')

        # so it is a normal character
        else:
            # don't output white space unless flags to output have been set
            if (c == ' ' and not with_spaces or \
                    c == '\t' and not with_tabs or \
                    c == '\n' and not with_newlines):
                continue

            # output newline
            if c in ('~', '\n'):
                keys.append(VirtualKeyAction(CODES["ENTER"]))

            # safest are the virtual keys - so if our key is a virtual key
            # use a VirtualKeyAction
            # if ord(c) in CODE_NAMES:
            #    keys.append(VirtualKeyAction(ord(c)))

            elif modifiers or should_escape_next_keys:
                keys.append(EscapedKeyAction(c))

            # if user disables the vk_packet option, always try to send a
            # virtual key of the actual keystroke
            elif not vk_packet and c in ascii_vk:
                keys.append(VirtualKeyAction(ascii_vk[c]))

            else:
                keys.append(KeyAction(c))

        # as we have handled the text - release the modifiers
        while modifiers:
            if DEBUG:
                print("MODS-", modifiers)
            keys.append(VirtualKeyAction(modifiers.pop(), down=False))

    # just in case there were any modifiers left pressed - release them
    while modifiers:
        keys.append(VirtualKeyAction(modifiers.pop(), down=False))

    return keys


def send_keys(keys,
              pause=0.05,
              with_spaces=False,
              with_tabs=False,
              with_newlines=False,
              turn_off_numlock=True,
              vk_packet=True):
    """Parse the keys and type them"""
    keys = parse_keys(
            keys, with_spaces, with_tabs, with_newlines,
            vk_packet=vk_packet)

    for k in keys:
        k.run()
        time.sleep(pause)


def LoByte(val):
    """Return the low byte of the value"""
    return val & 0xff


def HiByte(val):
    """Return the high byte of the value"""
    return (val & 0xff00) >> 8

SendKeys = deprecated(send_keys)
