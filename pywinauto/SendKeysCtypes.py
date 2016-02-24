# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2012 Michael Herrmann
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

"""
Check that SendInput can work the way we want it to

The tips and tricks at http://www.pinvoke.net/default.aspx/user32.sendinput
is useful!

"""
from __future__ import unicode_literals

import time
import ctypes
import win32api

from . import six
from . import win32structures

__all__ = ['KeySequenceError', 'SendKeys']

#pylint: disable-msg=R0903

DEBUG = 0

GetMessageExtraInfo = ctypes.windll.user32.GetMessageExtraInfo
MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
SendInput = ctypes.windll.user32.SendInput
UINT = ctypes.c_uint
SendInput.restype = UINT
SendInput.argtypes = [UINT, ctypes.c_void_p, ctypes.c_int]

VkKeyScan = ctypes.windll.user32.VkKeyScanW
VkKeyScan.restype = ctypes.c_short
VkKeyScan.argtypes = [ctypes.c_wchar]


INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP       = 2
KEYEVENTF_UNICODE     = 4
KEYEVENTF_SCANCODE    = 8
VK_SHIFT        = 16
VK_CONTROL      = 17
VK_MENU         = 18

# 'codes' recognized as {CODE( repeat)?}
CODES = {
    'BACK':     8,
    'BACKSPACE':8,
    'BKSP':     8,
    'BREAK':    3,
    'BS':       8,
    'CAP':      20,
    'CAPSLOCK': 20,
    'DEL':      46,
    'DELETE':   46,
    'DOWN':     40,
    'END':      35,
    'ENTER':    13,
    'ESC':      27,
    'F1':       112,
    'F2':       113,
    'F3':       114,
    'F4':       115,
    'F5':       116,
    'F6':       117,
    'F7':       118,
    'F8':       119,
    'F9':       120,
    'F10':      121,
    'F11':      122,
    'F12':      123,
    'F13':      124,
    'F14':      125,
    'F15':      126,
    'F16':      127,
    'F17':      128,
    'F18':      129,
    'F19':      130,
    'F20':      131,
    'F21':      132,
    'F22':      133,
    'F23':      134,
    'F24':      135,
    'HELP':     47,
    'HOME':     36,
    'INS':      45,
    'INSERT':   45,
    'LEFT':     37,
    'LWIN':     91,
    'NUMLOCK':  144,
    'PGDN':     34,
    'PGUP':     33,
    'PRTSC':    44,
    'RIGHT':    39,
    'RMENU':    165,
    'RWIN':     92,
    'SCROLLLOCK':145,
    'SPACE':     32,
    'TAB':       9,
    'UP':        38,

    'VK_ACCEPT': 30,
    'VK_ADD':    107,
    'VK_APPS':    93,
    'VK_ATTN':    246,
    'VK_BACK':    8,
    'VK_CANCEL':  3,
    'VK_CAPITAL': 20,
    'VK_CLEAR':   12,
    'VK_CONTROL': 17,
    'VK_CONVERT': 28,
    'VK_CRSEL':   247,
    'VK_DECIMAL': 110,
    'VK_DELETE':  46,
    'VK_DIVIDE':  111,
    'VK_DOWN':    40,
    'VK_END':     35,
    'VK_EREOF':   249,
    'VK_ESCAPE':  27,
    'VK_EXECUTE': 43,
    'VK_EXSEL':   248,
    'VK_F1':      112,
    'VK_F2':      113,
    'VK_F3':      114,
    'VK_F4':      115,
    'VK_F5':      116,
    'VK_F6':      117,
    'VK_F7':      118,
    'VK_F8':      119,
    'VK_F9':      120,
    'VK_F10':     121,
    'VK_F11':     122,
    'VK_F12':     123,
    'VK_F13':     124,
    'VK_F14':     125,
    'VK_F15':     126,
    'VK_F16':     127,
    'VK_F17':     128,
    'VK_F18':     129,
    'VK_F19':     130,
    'VK_F20':     131,
    'VK_F21':     132,
    'VK_F22':     133,
    'VK_F23':     134,
    'VK_F24':     135,
    'VK_FINAL':   24,
    'VK_HANGEUL':  21,
    'VK_HANGUL':   21,
    'VK_HANJA':    25,
    'VK_HELP':     47,
    'VK_HOME':     36,
    'VK_INSERT':   45,
    'VK_JUNJA':    23,
    'VK_KANA':     21,
    'VK_KANJI':    25,
    'VK_LBUTTON':   1,
    'VK_LCONTROL':162,
    'VK_LEFT':     37,
    'VK_LMENU':   164,
    'VK_LSHIFT':  160,
    'VK_LWIN':     91,
    'VK_MBUTTON':    4,
    'VK_MENU':        18,
    'VK_MODECHANGE':  31,
    'VK_MULTIPLY':   106,
    'VK_NEXT':        34,
    'VK_NONAME':     252,
    'VK_NONCONVERT':  29,
    'VK_NUMLOCK':    144,
    'VK_NUMPAD0':     96,
    'VK_NUMPAD1':     97,
    'VK_NUMPAD2':     98,
    'VK_NUMPAD3':     99,
    'VK_NUMPAD4':    100,
    'VK_NUMPAD5':    101,
    'VK_NUMPAD6':    102,
    'VK_NUMPAD7':    103,
    'VK_NUMPAD8':    104,
    'VK_NUMPAD9':    105,
    'VK_OEM_CLEAR':  254,
    'VK_PA1':        253,
    'VK_PAUSE':       19,
    'VK_PLAY':       250,
    'VK_PRINT':       42,
    'VK_PRIOR':       33,
    'VK_PROCESSKEY': 229,
    'VK_RBUTTON':      2,
    'VK_RCONTROL':   163,
    'VK_RETURN':      13,
    'VK_RIGHT':       39,
    'VK_RMENU':      165,
    'VK_RSHIFT':     161,
    'VK_RWIN':        92,
    'VK_SCROLL':     145,
    'VK_SELECT':      41,
    'VK_SEPARATOR':  108,
    'VK_SHIFT':       16,
    'VK_SNAPSHOT':    44,
    'VK_SPACE':       32,
    'VK_SUBTRACT':   109,
    'VK_TAB':          9,
    'VK_UP':          38,
    'ZOOM':          251,
}
# reverse the CODES dict to make it easy to look up a particular code name
CODE_NAMES = dict((entry[1], entry[0]) for entry in CODES.items())

# modifier keys
MODIFIERS = {
    '+': VK_SHIFT,
    '^': VK_CONTROL,
    '%': VK_MENU,
}


class KeySequenceError(Exception):
    """Exception raised when a key sequence string has a syntax error"""

    def __str__(self):
        return ' '.join(self.args)


class KeyAction(object):
    """Class that represents a single 'keyboard' action

    It represents either a PAUSE action (not reallly keyboard) or a keyboard
    action (press or release or both) of a particular key.
    """

    def __init__(self, key, down = True, up = True):
        self.key = key
        if isinstance(self.key, six.string_types):
            self.key = six.text_type(key)
        self.down = down
        self.up = up

    def _get_key_info(self):
        """Return virtual_key, scan_code, and flags for the action
        
        This is one of the methods that will be overridden by sub classes"""
        #print(self.key)
        return 0, ord(self.key), KEYEVENTF_UNICODE

    def GetInput(self):
        "Build the INPUT structure for the action"
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
            inp.ki.dwExtraInfo = GetMessageExtraInfo()

        # if we are releasing - then let it up
        if self.up:
            inputs[-1].ki.dwFlags |= KEYEVENTF_KEYUP

        return inputs

    def Run(self):
        "Execute the action"
        inputs = self.GetInput()

        # SendInput() supports all Unicode symbols
        num_inserted_events = SendInput(len(inputs), ctypes.byref(inputs),
                                        ctypes.sizeof(win32structures.INPUT))
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
        "Return a description of the key"
        vk, scan, flags = self._get_key_info()
        desc = ''
        if vk:
            if vk in CODE_NAMES:
                desc = CODE_NAMES[vk]
            else:
                desc = "VK %d"% vk
        else:
            desc = "%s"% self.key
        
        return desc

    def __str__(self):
        parts = []
        parts.append(self.key_description())
        up_down = self._get_down_up_string()
        if up_down:
            parts.append(up_down)

        return "<%s>"% (" ".join(parts))
    __repr__ = __str__


class VirtualKeyAction(KeyAction):
    """Represents a virtual key action e.g. F9 DOWN, etc

    Overrides necessary methods of KeyAction"""

    def _get_key_info(self):
        "Virtual keys have extended flag set"

        # copied more or less verbatim from 
        # http://www.pinvoke.net/default.aspx/user32.sendinput
        if (
            (self.key >= 33 and self.key <= 46) or 
            (self.key >= 91 and self.key <= 93) ):
            flags = KEYEVENTF_EXTENDEDKEY;
        else:
            flags = 0
        # This works for %{F4} - ALT + F4
        #return self.key, 0, 0

        # this works for Tic Tac Toe i.e. +{RIGHT} SHIFT + RIGHT
        return self.key, MapVirtualKey(self.key, 0), flags

    def Run(self):
        "Execute the action"

        # it works more stable for virtual keys than SendInput
        for inp in self.GetInput():
            win32api.keybd_event(inp.ki.wVk, inp.ki.wScan, inp.ki.dwFlags)


class EscapedKeyAction(KeyAction):
    """Represents an escaped key action e.g. F9 DOWN, etc

    Overrides necessary methods of KeyAction"""

    def _get_key_info(self):
        """EscapedKeyAction doesn't send it as Unicode and the vk and 
        scan code are generated differently"""
        vkey_scan = LoByte(VkKeyScan(self.key))

        return (vkey_scan, MapVirtualKey(vkey_scan, 0), 0)

    def key_description(self):
        "Return a description of the key"
        
        return "KEsc %s"% self.key

    def Run(self):
        "Execute the action"

        # it works more stable for virtual keys than SendInput
        for inp in self.GetInput():
            win32api.keybd_event(inp.ki.wVk, inp.ki.wScan, inp.ki.dwFlags)


class PauseAction(KeyAction):
    "Represents a pause action"

    def __init__(self, how_long):
        self.how_long = how_long

    def Run(self):
        "Pause for the lenght of time specified"
        time.sleep(self.how_long)

    def __str__(self):
        return "<PAUSE %1.2f>"% (self.how_long)
    __repr__ = __str__


def handle_code(code):
    "Handle a key or sequence of keys in braces"

    code_keys = []
    # it is a known code (e.g. {DOWN}, {ENTER}, etc)
    if code in CODES:
        code_keys.append(VirtualKeyAction(CODES[code]))

    # it is an escaped modifier e.g. {%}, {^}, {+}
    elif len(code) == 1:
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
                    'invalid repetition count %s'% count)

            # If the value in to_repeat is a VK e.g. DOWN
            # we need to add the code repeated
            if to_repeat in CODES:
                code_keys.extend(
                    [VirtualKeyAction(CODES[to_repeat])] * count)
            # otherwise parse the keys and we get back a KeyAction
            else:
                to_repeat = parse_keys(to_repeat)
                if isinstance(to_repeat, list):
                    keys = to_repeat * count
                else:
                    keys = [to_repeat] * count
                code_keys.extend(keys)
    else:
        raise RuntimeError("Unknown code: %s"% code)

    return code_keys


def parse_keys(string,
                with_spaces = False,
                with_tabs = False,
                with_newlines = False,
                modifiers = None):
    "Return the parsed keys"

    keys = []
    if not modifiers:
        modifiers = []
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
            keys.append(VirtualKeyAction(modifier, up = False))
            if DEBUG:
                print("MODS+", modifiers)
            continue

        # Apply modifiers over a bunch of characters (not just one!)
        elif c == "(":
            # find the end of the bracketed text
            end_pos = string.find(")", index)
            if end_pos == -1:
                raise KeySequenceError('`)` not found')
            keys.extend(
                parse_keys(string[index:end_pos], modifiers = modifiers))
            index = end_pos + 1

        # Escape or named key
        elif c == "{":
            # We start searching from index + 1 to account for the case {}}
            end_pos = string.find("}", index+1)
            if end_pos == -1:
                raise KeySequenceError('`}` not found')

            code = string[index:end_pos]
            index = end_pos + 1
            keys.extend(handle_code(code))

        # unmatched ")"
        elif c == ')':
            raise KeySequenceError('`)` should be preceeded by `(`')

        # unmatched "}"
        elif c == '}':
            raise KeySequenceError('`}` should be preceeded by `{`')

        # so it is a normal character
        else:
            # don't output white space unless flags to output have been set
            if (c == ' ' and not with_spaces or
                c == '\t' and not with_tabs or
                c == '\n' and not with_newlines):
                continue
            
            # output newline
            if c in ('~', '\n'):
                keys.append(VirtualKeyAction(CODES["ENTER"]))

            # safest are the virtual keys - so if our key is a virtual key
            # use a VirtualKeyAction
            #if ord(c) in CODE_NAMES:
            #    keys.append(VirtualKeyAction(ord(c)))
                
            elif modifiers:
                keys.append(EscapedKeyAction(c))
                
            else:
                keys.append(KeyAction(c))

        # as we have handled the text - release the modifiers
        while modifiers:
            if DEBUG:
                print("MODS-", modifiers)
            keys.append(VirtualKeyAction(modifiers.pop(), down = False))

    # just in case there were any modifiers left pressed - release them
    while modifiers:
        keys.append(VirtualKeyAction(modifiers.pop(), down = False))

    return keys

def LoByte(val):
    "Return the low byte of the value"
    return val & 0xff

def HiByte(val):
    "Return the high byte of the value"
    return (val & 0xff00) >> 8

def SendKeys(keys,
             pause=0.05,
             with_spaces=False,
             with_tabs=False,
             with_newlines=False,
             turn_off_numlock=True):
    "Parse the keys and type them"
    keys = parse_keys(keys, with_spaces, with_tabs, with_newlines)

    for k in keys:
        k.Run()
        time.sleep(pause)


def main(): #pragma: no cover
    "Send some test strings"

    actions = """
        {LWIN}
        {PAUSE .25}
        r
        {PAUSE .25}
        Notepad.exe{ENTER}
        {PAUSE 1}
        Hello{SPACE}World!
        {PAUSE 1}
        %{F4}
        {PAUSE .25}
        n
        """
    SendKeys(actions, pause = .1)
    
    keys = parse_keys(actions)
    for k in keys:
        print(k)
        k.Run()
        time.sleep(.1)

    test_strings = [
        "\n"
        "(aa)some text\n",
        "(a)some{ }text\n",
        "(b)some{{}text\n",
        "(c)some{+}text\n",
        "(d)so%me{ab 4}text",
        "(e)so%me{LEFT 4}text",
        "(f)so%me{ENTER 4}text",
        "(g)so%me{^aa 4}text",
        "(h)some +(asdf)text",
        "(i)some %^+(asdf)text",
        "(j)some %^+a text+",
        "(k)some %^+a tex+{&}",
        "(l)some %^+a tex+(dsf)",
        "",
        ]

    for s in test_strings:
        print(repr(s))
        keys = parse_keys(s, with_newlines = True)
        print(keys)

        for k in keys:
            k.Run()
            time.sleep(.1)
        print()

if __name__ == "__main__": #pragma: no cover

    main() #pragma: no cover
