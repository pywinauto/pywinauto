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

"""Linux/Unix branch of the keyboard module

It allows to send keystrokes to the active display using python-xlib library.
"""
from __future__ import print_function

from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input
import Xlib.XK
import time
import six

_display = Display()

DEBUG = 0

spec_keysyms = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Return",  # for some reason this needs to be cr, not lf
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
}


def _to_keycode(key):
    """return python X11 keycode of symbol"""
    return _display.keysym_to_keycode(Xlib.XK.string_to_keysym(key))

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP       = 2
KEYEVENTF_UNICODE     = 4
KEYEVENTF_SCANCODE    = 8
VK_SHIFT        = _to_keycode('Shift_L')
VK_CONTROL      = _to_keycode('Control_L')
VK_MENU         = _to_keycode('Menu')

# 'codes' recognized as {CODE repeat)?}


CODES = {
    'BACK':     _to_keycode('BackSpace'),
    'BACKSPACE': _to_keycode('BackSpace'),
    'BKSP':     _to_keycode('BackSpace'),
    'BREAK':    _to_keycode('Break'),
    'BS':       _to_keycode('BackSpace'),
    'CAP':      _to_keycode('Caps_Lock'),
    'CAPSLOCK': _to_keycode('Caps_Lock'),
    'DEL':      _to_keycode('Delete'),
    'DELETE':   _to_keycode('Delete'),
    'DOWN':     _to_keycode('Down'),
    'END':      _to_keycode('End'),
    'ENTER':    _to_keycode('Return'),
    'ESC':      _to_keycode('Escape'),
    'F1':       _to_keycode('F1'),
    'F2':       _to_keycode('F2'),
    'F3':       _to_keycode('F3'),
    'F4':       _to_keycode('F4'),
    'F5':       _to_keycode('F5'),
    'F6':       _to_keycode('F6'),
    'F7':       _to_keycode('F7'),
    'F8':       _to_keycode('F8'),
    'F9':       _to_keycode('F9'),
    'F10':      _to_keycode('F10'),
    'F11':      _to_keycode('F11'),
    'F12':      _to_keycode('F12'),
    'F13':      _to_keycode('F13'),
    'F14':      _to_keycode('F14'),
    'F15':      _to_keycode('F15'),
    'F16':      _to_keycode('F16'),
    'F17':      _to_keycode('F17'),
    'F18':      _to_keycode('F18'),
    'F19':      _to_keycode('F19'),
    'F20':      _to_keycode('F20'),
    'F21':      _to_keycode('F21'),
    'F22':      _to_keycode('F22'),
    'F23':      _to_keycode('F23'),
    'F24':      _to_keycode('F24'),
    'HELP':     _to_keycode('Help'),
    'HOME':     _to_keycode('Home'),
    'INS':      _to_keycode('Insert'),
    'INSERT':   _to_keycode('Insert'),
    'LEFT':     _to_keycode('Left'),
    'LWIN':     _to_keycode('Super_L'),
    'NUMLOCK':  _to_keycode('Num_Lock'),
    'PGDN':     _to_keycode('Page_Down'),
    'PGUP':     _to_keycode('Page_Up'),
    'PRTSC':    _to_keycode('Print'),
    'RIGHT':    _to_keycode('Right'),
    'RMENU':    _to_keycode('Alt_R'),
    'RWIN':     _to_keycode('Super_R'),
    'SCROLLLOCK': _to_keycode('Scroll_Lock'),
    'SPACE':     _to_keycode('space'),
    'TAB':       _to_keycode('Tab'),
    'UP':        _to_keycode('Up'),

    'VK_ACCEPT': 30,
    'VK_ADD':    107,
    'VK_APPS':    93,
    'VK_ATTN':    246,
    'VK_BACK':    _to_keycode('BackSpace'),
    'VK_CANCEL':  _to_keycode('Break'),
    'VK_CAPITAL': _to_keycode('Caps_Lock'),
    'VK_CLEAR':   12,
    'VK_CONTROL': _to_keycode('Control_L'),
    'VK_CONVERT': 28,
    'VK_CRSEL':   247,
    'VK_DECIMAL': 110,
    'VK_DELETE':  _to_keycode('Delete'),
    'VK_DIVIDE':  111,
    'VK_DOWN':    _to_keycode('Down'),
    'VK_END':     _to_keycode('End'),
    'VK_EREOF':   249,
    'VK_ESCAPE':  _to_keycode('Escape'),
    'VK_EXECUTE': 43,
    'VK_EXSEL':   248,
    'VK_F1':       _to_keycode('F1'),
    'VK_F2':       _to_keycode('F2'),
    'VK_F3':       _to_keycode('F3'),
    'VK_F4':       _to_keycode('F4'),
    'VK_F5':       _to_keycode('F5'),
    'VK_F6':       _to_keycode('F6'),
    'VK_F7':       _to_keycode('F7'),
    'VK_F8':       _to_keycode('F8'),
    'VK_F9':       _to_keycode('F9'),
    'VK_F10':      _to_keycode('F10'),
    'VK_F11':      _to_keycode('F11'),
    'VK_F12':      _to_keycode('F12'),
    'VK_F13':      _to_keycode('F13'),
    'VK_F14':      _to_keycode('F14'),
    'VK_F15':      _to_keycode('F15'),
    'VK_F16':      _to_keycode('F16'),
    'VK_F17':      _to_keycode('F17'),
    'VK_F18':      _to_keycode('F18'),
    'VK_F19':      _to_keycode('F19'),
    'VK_F20':      _to_keycode('F20'),
    'VK_F21':      _to_keycode('F21'),
    'VK_F22':      _to_keycode('F22'),
    'VK_F23':      _to_keycode('F23'),
    'VK_F24':      _to_keycode('F24'),
    'VK_FINAL':   24,
    'VK_HANGEUL':  21,
    'VK_HANGUL':   21,
    'VK_HANJA':    25,
    'VK_HELP':     _to_keycode('Help'),
    'VK_HOME':     _to_keycode('Home'),
    'VK_INSERT':   _to_keycode('Insert'),
    'VK_JUNJA':    23,
    'VK_KANA':     21,
    'VK_KANJI':    25,
    'VK_LBUTTON':   1,
    'VK_LCONTROL': _to_keycode('Control_L'),
    'VK_LEFT':     _to_keycode('Left'),
    'VK_LMENU':   _to_keycode('Alt_L'),
    'VK_LSHIFT':  _to_keycode('Shift_L'),
    'VK_LWIN':     _to_keycode('Super_L'),
    'VK_MBUTTON':    4,
    'VK_MENU':        _to_keycode('Alt_L'),
    'VK_MODECHANGE':  31,
    'VK_MULTIPLY':   106,
    'VK_NEXT':        _to_keycode('Page_Down'),
    'VK_NONAME':     252,
    'VK_NONCONVERT':  29,
    'VK_NUMLOCK':    _to_keycode('Num_Lock'),
    'VK_NUMPAD0':     _to_keycode('KP_0'),
    'VK_NUMPAD1':     _to_keycode('KP_1'),
    'VK_NUMPAD2':     _to_keycode('KP_2'),
    'VK_NUMPAD3':     _to_keycode('KP_3'),
    'VK_NUMPAD4':    _to_keycode('KP_4'),
    'VK_NUMPAD5':    _to_keycode('KP_5'),
    'VK_NUMPAD6':    _to_keycode('KP_6'),
    'VK_NUMPAD7':    _to_keycode('KP_7'),
    'VK_NUMPAD8':    _to_keycode('KP_8'),
    'VK_NUMPAD9':    _to_keycode('KP_9'),
    'VK_OEM_CLEAR':  254,
    'VK_PA1':        253,
    'VK_PAUSE':       19,
    'VK_PLAY':       250,
    'VK_PRINT':       _to_keycode('Print'),
    'VK_PRIOR':       _to_keycode('Page_Up'),
    'VK_PROCESSKEY': 229,
    'VK_RBUTTON':      2,
    'VK_RCONTROL':   _to_keycode('Control_R'),
    'VK_RETURN':      _to_keycode('Return'),
    'VK_RIGHT':       _to_keycode('Right'),
    'VK_RMENU':      _to_keycode('Alt_R'),
    'VK_RSHIFT':     _to_keycode('Shift_R'),
    'VK_RWIN':        _to_keycode('Super_R'),
    'VK_SCROLL':     _to_keycode('Scroll_Lock'),
    'VK_SELECT':      41,
    'VK_SEPARATOR':  108,
    'VK_SHIFT':       _to_keycode('Shift_L'),
    'VK_SNAPSHOT':    _to_keycode('Print'),
    'VK_SPACE':       _to_keycode('Space'),
    'VK_SUBTRACT':   109,
    'VK_TAB':          _to_keycode('Tab'),
    'VK_UP':          _to_keycode('Up'),
    'ZOOM':          251, #no item in xlib
}

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

    """
    Class that represents a single 'keyboard' action

    It represents either a PAUSE action (not reallly keyboard) or a keyboard
    action (press or release or both) of a particular key.
    """

    def __init__(self, key, down = True, up = True):
        """Init a single key action params"""
        self.key = key
        self.down = down
        self.up = up
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.is_shifted = False

    @staticmethod
    def _key_modifiers(ctrl, shift, alt, action = X.KeyPress):
        """Apply key modifiers"""
        if ctrl:
            fake_input(_display, action, CODES['VK_CONTROL'])
        if shift:
            fake_input(_display, action, CODES['VK_SHIFT'])
        if alt:
            fake_input(_display, action, CODES['VK_MENU'])

    def run(self):
        """Do a single keyboard action using xlib"""
        if isinstance(self.key, six.string_types):
            key = self.key
            self.key = Xlib.XK.string_to_keysym(self.key)
            if self.key == 0:
                self.key = Xlib.XK.string_to_keysym(spec_keysyms[key])
            self.key = _display.keysym_to_keycode(self.key)
            if self.key == 0:
                raise RuntimeError('Key {} not found!'.format(self.key))
            self.is_shifted = key.isupper() or key in '~!@#$%^&*()_+{}|:"<>?'
        elif not isinstance(self.key, six.integer_types):
            raise TypeError('self.key = {} is not a string or integer'.format(self.key))

        self._key_modifiers(self.ctrl, (self.shift or self.is_shifted),
                            self.alt, action = X.KeyPress)
        if self.down:
            fake_input(_display, X.KeyPress, self.key)
            _display.sync()
        if self.up:
            fake_input(_display, X.KeyRelease, self.key)
            _display.sync()
        self._key_modifiers(self.ctrl, (self.shift or self.is_shifted),
                            self.alt, action = X.KeyRelease)
        _display.sync()

    def _get_down_up_string(self):
        """Return a string that will show whether the string is up or down

        return 'down' if the key is a press only
        return 'up' if the key is up only
        return '' if the key is up & down (as default)
        """
        if self.down and self.up:
            return ""
        if self.down:
            return "down"
        if self.up:
            return "up"
        return "" # TODO: raise RuntimeError('Nor "down" or "up" action specified!')

    def key_description(self):
        """Return a description of the key"""
        return "{}".format(self.key)

    def __str__(self):
        """Return key with modifiers as a string"""
        parts = []
        parts.append(self.key_description())
        up_down = self._get_down_up_string()
        if up_down:
            parts.append(up_down)

        return "<{}>".format(" ".join(parts))
    __repr__ = __str__


class PauseAction(KeyAction):

    """Represents a pause action"""

    def __init__(self, how_long):
        self.how_long = how_long

    def run(self):
        """Pause for the lenght of time specified"""
        time.sleep(self.how_long)

    def __str__(self):
        return "<PAUSE {}>".format(self.how_long)
    __repr__ = __str__


def handle_code(code):
    """Handle a key or sequence of keys in braces"""
    code_keys = []
    # it is a known code (e.g. {DOWN}, {ENTER}, etc)
    if code in CODES:
        code_keys.append(KeyAction(CODES[code]))

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
            if to_repeat in CODES:
                code_keys.extend(
                    [KeyAction(CODES[to_repeat])] * count)
            # otherwise parse the keys and we get back a KeyAction
            else:
                to_repeat = parse_keys(to_repeat)
                if isinstance(to_repeat, list):
                    keys = to_repeat * count
                else:
                    keys = [to_repeat] * count
                code_keys.extend(keys)
    else:
        raise RuntimeError("Unknown code: {}".format(code))

    return code_keys


def parse_keys(string,
                with_spaces = False,
                with_tabs = False,
                with_newlines = False,
                modifiers = None):
    """Return the parsed keys"""
    keys = []
    if not modifiers:
        modifiers = []
    index = 0
    while index < len(string):

        c = string[index]
        index += 1
        # check if one of CTRL, SHIFT, ALT has been pressed
        if c in MODIFIERS.keys():
            # remember that we are currently modified
            modifiers.append(c)
            # hold down the modifier key
            #keys.append(KeyAction(modifier, up = False))
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
                keys.append(KeyAction(CODES["ENTER"]))

            elif modifiers:
                keys.append(KeyAction(c))

            else:
                keys.append(KeyAction(c))

        # as we have handled the text - release the modifiers
        while modifiers:
            if DEBUG:
                print("MODS-", modifiers)
            mod = modifiers.pop()
            if mod == '+':
                keys[-1].shift = True
            elif mod == '^':
                keys[-1].ctrl = True
            elif mod == '%':
                keys[-1].alt = True

    # just in case there were any modifiers left pressed - release them
    while modifiers:
        keys.append(KeyAction(modifiers.pop(), down = False))
    return keys


def SendKeys(keys,
             pause=0.05,
             with_spaces=False,
             with_tabs=False,
             with_newlines=False,
             turn_off_numlock=True):
    """Parse the keys and type them"""
    keys = parse_keys(keys, with_spaces, with_tabs, with_newlines)
    for k in keys:
        k.run()
        time.sleep(pause)
