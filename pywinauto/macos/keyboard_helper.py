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

'''
**Available key selected_keyboard.codes:** ::

    {'F1'},{'F2'},{'F3'},{'F4'},{'F5'},{'F6'},{'F7'},{'F8'},{'F9'},{'F10'},
    {'F11'},{'F12'},{'F13'},{'F14'},{'F15'},{'F16'},{'F17'},{'F18'},{'F19'},
    {'F20'},{'VK_F1'},{'VK_F2'},{'VK_F3'},{'VK_F4'},{'VK_F5'},{'VK_F6'},
    {'VK_F7'},{'VK_F8'},{'VK_F9'},{'VK_F10'},{'VK_F11'},{'VK_F12'},
    {'VK_F13'},{'VK_F14'},{'VK_F15'},{'VK_F16'},{'VK_F17'},{'VK_F18'},
    {'VK_F19'},{'VK_F20'},{'VK_SPACE'},{'SPACE'},{'VK_LEFT'},{'VK_RIGHT'},
    {'VK_UP'},{'VK_DOWN'},{'LEFT'},{'RIGHT'},{'UP'},{'DOWN'},{'VK_CONTROL'},
    {'VK_LCONTROL'},{'VK_RCONTROL'},{'VK_SHIFT'},{'VK_LSHIFT'},{'VK_RSHIFT'},
    {'VK_NUMPAD0'},{'VK_NUMPAD1'},{'VK_NUMPAD2'},{'VK_NUMPAD3'},{'VK_NUMPAD4'},
    {'VK_NUMPAD5'},{'VK_NUMPAD6'},{'VK_NUMPAD7'},{'VK_NUMPAD8'},{'VK_NUMPAD9'},
    {'TAB'},{'VK_TAB'},{'DEL'},{'DELETE'},{'VK_DELETE'},{'BKSP'},{'BACK'},{'VK_BACK'},
    {'BACKSPACE'},{'HOME'},{'VK_HOME'},{'END'},{'VK_END'},{'CAPSLOCK'},{'CAP'},
    {'VK_CAPITAL'},{'ENTER'},{'VK_RETURN'},{'VK_SEPARATOR'},{'PGDN'},
    {'PGUP'},{'VK_DECIMAL'},{'VK_CLEAR'},{'ESC'},{'VK_ESCAPE'},
    {'VK_ADD'},{'VK_SUBTRACT'},{'VK_MULTIPLY'},{'VK_DIVIDE'}

**Modifiers:**

- ``'+': {VK_SHIFT}``
- ``'^': {VK_CONTROL}``
- ``'%': {VK_MENU}`` a.k.a. Alt key

Example how to use modifiers: ::

    send_keys('^a^c') # select all (Ctrl+A) and copy to clipboard (Ctrl+C)
    send_keys('+{INS}') # insert from clipboard (Shift+Ins)
    send_keys('%{F4}') # close an active window with Alt+F4

Repetition count can be specified for special keys. ``{ENTER 2}`` says to
press Enter twice.
'''
import time

from Quartz.CoreGraphics import CGEventCreateKeyboardEvent
from Quartz.CoreGraphics import CGEventSourceCreate
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGHIDEventTap
from Quartz.CoreGraphics import kCGEventSourceStateHIDSystemState
from Quartz.CoreGraphics import CGEventSetFlags
from Quartz.CoreGraphics import kCGEventFlagMaskShift
from Quartz.CoreGraphics import kCGEventFlagMaskControl
from Quartz.CoreGraphics import kCGEventFlagMaskAlternate
from Quartz.CoreGraphics import kCGEventFlagMaskCommand
from Quartz.CoreGraphics import kCGEventFlagMaskSecondaryFn

VK_SHIFT = 0x38
VK_CONTROL = 0x3B
VK_MENU = 0x3A
VK_CMD = 0x37

DEBUG = 0

class US_Keyboard():

    CODES = {
        'F1'     : 0x7A,
        'F2'     : 0x78,
        'F3'     : 0x63,
        'F4'     : 0x76,
        'F5'     : 0x60,
        'F6'     : 0x61,
        'F7'     : 0x62,
        'F8'     : 0x64,
        'F9'     : 0x65,
        'F10'    : 0x6D,
        'F11'    : 0x67,
        'F12'    : 0x6F,
        'F13'    : 0x69,
        'F14'    : 0x6B,
        'F15'    : 0x71,
        'F16'    : 0x6A,
        'F17'    : 0x40,
        'F18'    : 0x4F,
        'F19'    : 0x50,
        'F20'    : 0x5A,

        'VK_F1'  : 0x7A,
        'VK_F2'  : 0x78,
        'VK_F3'  : 0x63,
        'VK_F4'  : 0x76,
        'VK_F5'  : 0x60,
        'VK_F6'  : 0x61,
        'VK_F7'  : 0x62,
        'VK_F8'  : 0x64,
        'VK_F9'  : 0x65,
        'VK_F10' : 0x6D,
        'VK_F11' : 0x67,
        'VK_F12' : 0x6F,
        'VK_F13' : 0x69,
        'VK_F14' : 0x6B,
        'VK_F15' : 0x71,
        'VK_F16' : 0x6A,
        'VK_F17' : 0x40,
        'VK_F18' : 0x4F,
        'VK_F19' : 0x50,
        'VK_F20' : 0x5A,

        'VK_SPACE' : 0x31,
        'SPACE'    : 0x31,

        'VK_LEFT'  : 0x7B,
        'VK_RIGHT' : 0x7C,
        'VK_UP'    : 0x7D,
        'VK_DOWN'  : 0x7E,

        'LEFT'     : 0x7B,
        'RIGHT'    : 0x7C,
        'UP'       : 0x7D,
        'DOWN'     : 0x7E,

        'VK_NUMPAD0' : 0x52,
        'VK_NUMPAD1' : 0x53,
        'VK_NUMPAD2' : 0x54,
        'VK_NUMPAD3' : 0x55,
        'VK_NUMPAD4' : 0x56,
        'VK_NUMPAD5' : 0x57,
        'VK_NUMPAD6' : 0x58,
        'VK_NUMPAD7' : 0x59,
        'VK_NUMPAD8' : 0x5B,
        'VK_NUMPAD9' : 0x5C,

        'TAB'    : 0x30,
        'VK_TAB' : 0x30,

        'DEL'       : 0x33,
        'DELETE'    : 0x33,
        'VK_DELETE' : 0x33,

        'BKSP'      : 0x33,
        'BACK'      : 0x33,
        'VK_BACK'   : 0x33,
        'BACKSPACE' : 0x33,

        'HOME'      : 0x73,
        'VK_HOME'   : 0x73,

        'END'       : 0x77,
        'VK_END'    : 0x77,

        'CAPSLOCK'   : 0x39,
        'CAP'        : 0x39,
        'VK_CAPITAL' : 0x39,

        'ENTER'      : 0x24,
        'VK_RETURN'  : 0x24,

        'VK_SEPARATOR' : 0x4B,
        'PGDN'         : 0x79,
        'PGUP'         : 0x74,

        'VK_DECIMAL' : 0x2F,
        'VK_CLEAR'   : 0x47,
        'ESC'        : 0x35,
        'VK_ESCAPE'  : 0x35,

        'VK_ADD'      : 0x45,
        'VK_SUBTRACT' : 0x4E,
        'VK_MULTIPLY' : 0x43,
        'VK_DIVIDE'   : 0x4B,
        'VK_CMD' : 0x37,
        'CMD'    : 0x37,
        'cmd'    : 0x37,

        'VK_CONTROL'  : 0x3B,
        'VK_LCONTROL' : 0x3B,
        'VK_RCONTROL' : 0x3E,

        'VK_SHIFT'  : 0x3C,
        'VK_LSHIFT' : 0x3C,
        'VK_RSHIFT' : 0x3C,

        'VK_MENU' : 0x3A,
        'ALT'     : 0x3A,
        'alt'     : 0x3A,
        'option'  : 0x3A,

        'fun'     : 0x3F,
        'function': 0x3F,
    }

    hot_keys_components = {
        'VK_CMD' : 0x37,
        'CMD'    : 0x37,
        'cmd'    : 0x37,

        'VK_CONTROL'  : 0x3B,
        'VK_LCONTROL' : 0x3B,
        'VK_RCONTROL' : 0x3E,

        'VK_SHIFT'  : 0x3C,
        'VK_LSHIFT' : 0x3C,
        'VK_RSHIFT' : 0x3C,

        'VK_MENU' : 0x3A,
        'ALT'     : 0x3A,
        'alt'     : 0x3A,
        'option'  : 0x3A,

        'fun'     : 0x3F,
        'function': 0x3F,
    }

    shift_chars={
        '~': '`',
        '!': '1',
        '@': '2',
        '#': '3',
        '$': '4',
        '%': '5',
        '^': '6',
        '&': '7',
        '*': '8',
        '(': '9',
        ')': '0',
        '_': '-',
        '+': '=',
        '{': '[',
        '}': ']',
        '|': '\\',
        ':': ';',
        '"': '\'',
        '<': ',',
        '>': '.',
        '?': '/',
    }
    key_code_map={
        'a'              : 0x00,
        's'              : 0x01,
        'd'              : 0x02,
        'f'              : 0x03,
        'h'              : 0x04,
        'g'              : 0x05,
        'z'              : 0x06,
        'x'              : 0x07,
        'c'              : 0x08,
        'v'              : 0x09,
        'b'              : 0x0B,
        'q'              : 0x0C,
        'w'              : 0x0D,
        'e'              : 0x0E,
        'r'              : 0x0F,
        'y'              : 0x10,
        't'              : 0x11,
        '1'              : 0x12,
        '2'              : 0x13,
        '3'              : 0x14,
        '4'              : 0x15,
        '6'              : 0x16,
        '5'              : 0x17,
        '='              : 0x18,
        '9'              : 0x19,
        '7'              : 0x1A,
        '-'              : 0x1B,
        '8'              : 0x1C,
        '0'              : 0x1D,
        ']'              : 0x1E,
        'o'              : 0x1F,
        'u'              : 0x20,
        '['              : 0x21,
        'i'              : 0x22,
        'p'              : 0x23,
        'l'              : 0x25,
        'j'              : 0x26,
        '\''             : 0x27,
        'k'              : 0x28,
        ';'              : 0x29,
        '\\'             : 0x2A,
        ','              : 0x2B,
        '/'              : 0x2C,
        'n'              : 0x2D,
        'm'              : 0x2E,
        '.'              : 0x2F,
        '`'              : 0x32,
        'k.'             : 0x41,
        'k*'             : 0x43,
        'k+'             : 0x45,
        'kclear'         : 0x47,
        'k/'             : 0x4B,
        'k\n'            : 0x4C,
        'k-'             : 0x4E,
        'k='             : 0x51,
        'k0'             : 0x52,
        'k1'             : 0x53,
        'k2'             : 0x54,
        'k3'             : 0x55,
        'k4'             : 0x56,
        'k5'             : 0x57,
        'k6'             : 0x58,
        'k7'             : 0x59,
        'k8'             : 0x5B,
        'k9'             : 0x5C,
        '\n'             : 0x24,
        '\t'             : 0x30,
        ' '              : 0x31,
        'del'            : 0x33,
        'delete'         : 0x33,
        'esc'            : 0x35,
        'escape'         : 0x35,
        'cmd'            : 0x37,
        'command'        : 0x37,
        'shift'          : 0x38,
        'caps lock'      : 0x39,
        'option'         : 0x3A,
        'ctrl'           : 0x3B,
        'control'        : 0x3B,
        'right shift'    : 0x3C,
        'rshift'         : 0x3C,
        'right option'   : 0x3D,
        'roption'        : 0x3D,
        'right control'  : 0x3E,
        'rcontrol'       : 0x3E,
        'fun'            : 0x3F,
        'function'       : 0x3F,
        'volume up'      : 0x48,
        'volume down'    : 0x49,
        'mute'           : 0x4A,
        'f1'             : 0x7A,
        'f2'             : 0x78,
        'f3'             : 0x63,
        'f4'             : 0x76,
        'f5'             : 0x60,
        'f6'             : 0x61,
        'f7'             : 0x62,
        'f8'             : 0x64,
        'f9'             : 0x65,
        'f10'            : 0x6D,
        'f11'            : 0x67,
        'f12'            : 0x6F,
        'f13'            : 0x69,
        'f14'            : 0x6B,
        'f15'            : 0x71,
        'f16'            : 0x6A,
        'f17'            : 0x40,
        'f18'            : 0x4F,
        'f19'            : 0x50,
        'f20'            : 0x5A,
        'help'           : 0x72,
        'home'           : 0x73,
        'pgup'           : 0x74,
        'page up'        : 0x74,
        'forward delete' : 0x75,
        'end'            : 0x77,
        'page down'      : 0x79,
        'pgdn'           : 0x79,
        'left'           : 0x7B,
        'right'          : 0x7C,
        'down'           : 0x7D,
        'up'             : 0x7E,
    }

MODIFIERS = {
    '+': 'VK_SHIFT',
    '^': 'VK_CONTROL',
    '%': 'VK_MENU',
    '⌘': 'VK_CMD',
}

selected_keyboard=US_Keyboard;

class KeySequenceError(Exception):

    def __str__(self):
        return ' '.join(self.args)

class KeyAction(object):

    def __init__(self, key, down=True, up=True, flag=None):
        self.key = key
        self.down = down
        self.up = up
        self.flag = flag

    def run(self):
        """Execute the action"""
        src = CGEventSourceCreate(kCGEventSourceStateHIDSystemState);
        keyboard_event = CGEventCreateKeyboardEvent(src, self.key, self.down)
        if self.flag is not None:
            CGEventSetFlags(keyboard_event, self.flag)
        else:
            CGEventSetFlags(keyboard_event, 0)
        CGEventPost(kCGHIDEventTap, keyboard_event)

    def _get_down_up_string(self):

        down_up = ""
        if not (self.down and self.up):
            if self.down:
                down_up = "down"
            elif self.up:
                down_up = "up"
        return down_up

    def key_description(self):

        return "{}".format(self.key)

    def __str__(self):
        parts = []
        parts.append(self.key_description())
        up_down = self._get_down_up_string()
        if up_down:
            parts.append(up_down)

        return "<{}>".format(   " ".join(parts))
    __repr__ = __str__

class PauseAction(KeyAction):

    def __init__(self, how_long):
        self.how_long = how_long

    def run(self):
        """Pause for the lenght of time specified"""
        time.sleep(self.how_long)

    def __str__(self):
        """Represents a str value"""
        return "<PAUSE {}>".format(self.how_long)
    __repr__ = __str__

def handle_flag_by_code(value):
    flag=None
    if len(value) == 1:
        if value in MODIFIERS.keys():
            code_key=MODIFIERS[value]
            if code_key and code_key in selected_keyboard.CODES.keys():
                flag_code=selected_keyboard.CODES[MODIFIERS[value]]
                if flag_code == selected_keyboard.hot_keys_components['VK_SHIFT']:
                    flag=kCGEventFlagMaskShift
                elif flag_code == selected_keyboard.hot_keys_components['VK_CONTROL']:
                    flag=kCGEventFlagMaskControl
                elif flag_code == selected_keyboard.hot_keys_components['VK_CMD']:
                    flag=kCGEventFlagMaskCommand
                elif flag_code == selected_keyboard.hot_keys_components['VK_MENU']:
                    flag=kCGEventFlagMaskAlternate
    elif value in selected_keyboard.hot_keys_components.keys():
        code = selected_keyboard.hot_keys_components[value]
        if code == selected_keyboard.hot_keys_components['VK_SHIFT']:
            flag=kCGEventFlagMaskShift
        elif code == selected_keyboard.hot_keys_components['VK_CONTROL']:
            flag=kCGEventFlagMaskControl
        elif code == selected_keyboard.hot_keys_components['VK_CMD']:
            flag=kCGEventFlagMaskCommand
        elif code == selected_keyboard.hot_keys_components['VK_MENU']:
            flag=kCGEventFlagMaskAlternate
        elif code == selected_keyboard.hot_keys_components['function']:
            flag=kCGEventFlagMaskSecondaryFn
    return flag

def handle_code(code_name):
    """Handle a key or sequence of keys in braces"""
    code_keys = []
    # it is a known code (e.g. {DOWN}, {ENTER}, etc)
    flag = None
    if code_name in selected_keyboard.hot_keys_components:
        res = handle_flag_by_code(code_name)
        if res is not None:
            flag = res
    elif code_name in selected_keyboard.CODES:
        code_keys.append(KeyAction(selected_keyboard.CODES[code_name]))

    # it is an escaped modifier e.g. {%}, {^}, {+},
    elif code_name in MODIFIERS.keys():
        res = handle_flag_by_code(code_name)
        if res is not None:
            flag = res

    elif len(code_name) == 1:
        if code_name.isalpha() and code_name.isupper():
            flag = kCGEventFlagMaskShift
            code_name = code_name.lower()
        if code_name in selected_keyboard.shift_chars:
            key_code = selected_keyboard.shift_chars[code_name]
            if key_code in selected_keyboard.key_code_map:
                flag = kCGEventFlagMaskShift
                key_code = selected_keyboard.key_code_map[key_code]
                code_keys.append(KeyAction(key_code, flag=flag))
                flag = None
        elif code_name in selected_keyboard.key_code_map:
            key_code = selected_keyboard.key_code_map[code_name]
            code_keys.append(KeyAction(key_code, flag=flag))
            flag = None
    # it is a repetition or a pause  {DOWN 5}, {PAUSE 1.3}
    elif ' ' in code_name:
        to_repeat, count = code_name.rsplit(None, 1)
        if to_repeat == "PAUSE":
            try:
                pause_time = float(count)
            except ValueError:
                raise KeySequenceError('invalid pause time {}'.format(count))
            code_keys.append(PauseAction(pause_time))

        else:
            try:
                count = int(count)
            except ValueError:
                raise KeySequenceError(
                    'invalid repetition count {}'.format(count))

            # If the value in to_repeat is a VK e.g. DOWN
            # we need to add the code repeated
            if to_repeat in selected_keyboard.CODES:
                code_keys.extend(
                    [KeyAction(selected_keyboard.CODES[to_repeat])] * count)
            # otherwise parse the keys and we get back a KeyAction
            else:
                flag = None
                if to_repeat.isalpha() and to_repeat.isupper():
                    flag = kCGEventFlagMaskShift
                    to_repeat = to_repeat.lower()
                to_repeat = parse_keys(to_repeat,flag=flag)
                flag = None
                if isinstance(to_repeat, list):
                    keys = to_repeat * count
                else:
                    keys = [to_repeat] * count
                code_keys.extend(keys)
    else:
        raise RuntimeError("Unknown code: {}".format(code_name))
    return code_keys, flag

def decode_flag_to_key(flag):
    keys = []
    if flag == kCGEventFlagMaskShift:
        keys.append(KeyAction(selected_keyboard.key_code_map['k+']))
    elif flag == kCGEventFlagMaskControl:
        keys.append(KeyAction(selected_keyboard.key_code_map['6'], flag=kCGEventFlagMaskShift))
    elif flag == kCGEventFlagMaskCommand:
        keys.append(KeyAction(selected_keyboard.key_code_map['cmd']))
    elif flag == kCGEventFlagMaskAlternate:
        keys.append(KeyAction(selected_keyboard.key_code_map['5'], flag=kCGEventFlagMaskShift))
    elif flag == kCGEventFlagMaskSecondaryFn:
        keys.append(KeyAction(selected_keyboard.key_code_map['function']))
    return keys

def parse_keys(string,
               with_spaces=False,
               with_tabs=False,
               with_newlines=False,
               modifiers=None,
               flag=None):
    """Return the parsed keys"""
    keys = []
    next_flag = flag
    if not modifiers:
        modifiers = []
    index = 0
    while index < len(string):
        c = string[index]
        index += 1
        # check if one of CTRL, SHIFT, ALT, CMD has been pressed
        if c in MODIFIERS.keys():
            modifier = MODIFIERS[c]
            # remember that we are currently modified
            modifiers.append(modifier)
            # hold down the modifier key
            code_keys, flag_from_func = handle_code(c)
            if flag_from_func is not None:
                next_flag = flag_from_func
            # keys.append(KeyAction(modifier, up = False))
            if DEBUG:
                print("MODS+", modifiers)
            continue

        # Apply modifiers over a bunch of characters (not just one!)
        elif c == "(":
            # find the end of the bracketed text
            end_pos = string.find(")", index)
            if end_pos == -1:
                raise KeySequenceError('`)` not found')
            keys.extend(parse_keys(string[index:end_pos], modifiers = modifiers, flag=next_flag))
            index = end_pos + 1

        # Escape or named key
        elif c == "{":
            # We start searching from index + 1 to account for the case {}}
            end_pos = string.find("}", index+1)
            if end_pos == -1:
                raise KeySequenceError('`}` not found')

            code_name = string[index:end_pos]
            index = end_pos + 1
            code_keys, flag_from_func = handle_code(code_name)
            if next_flag is not None:
                keys.extend(decode_flag_to_key(next_flag))
            next_flag = flag_from_func
            if index == len(string) and next_flag is not None:
                keys.extend(decode_flag_to_key(next_flag))
            keys.extend(code_keys)
        # unmatched ")"
        elif c == ')':
            raise KeySequenceError('`)` should be preceeded by `(`')

        # unmatched "}"
        elif c == '}':
            raise KeySequenceError('`}` should be preceeded by `{`')
        # so it is a normal character
        else:
            # don't output white space unless flag to output have been set
            if (c == ' ' and not with_spaces or \
                    c == '\t' and not with_tabs or \
                    c == '\n' and not with_newlines):
                continue

            # output newline
            if c in ('~', '\n'):
                keys.append(KeyAction(selected_keyboard.CODES["ENTER"], flag=next_flag))
                next_flag = None
            else:
                if c.isalpha() and c.isupper():
                    next_flag = kCGEventFlagMaskShift
                    c = c.lower()
                if c in selected_keyboard.shift_chars:
                    key_code = selected_keyboard.shift_chars[c]
                    if key_code in selected_keyboard.key_code_map:
                        next_flag = kCGEventFlagMaskShift
                        key_code = selected_keyboard.key_code_map[key_code]
                        keys.append(KeyAction(key_code, flag=next_flag))
                    next_flag = None
                elif c in selected_keyboard.key_code_map:
                    key_code = selected_keyboard.key_code_map[c]
                    keys.append(KeyAction(key_code, flag=next_flag))
                    next_flag = None

    return keys


def send_keys(keys,
              pause=0.05,
              with_spaces=True,
              with_tabs=True,
              with_newlines=True,
              turn_off_numlock=True):
    """Parse the keys and type them"""
    keys = parse_keys(keys, with_spaces, with_tabs, with_newlines,flag=None)
    for k in keys:
        k.run()
        time.sleep(pause)
