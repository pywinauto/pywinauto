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

r"""Keyboard input emulation module

Automate typing keys or individual key actions (viz. press and hold, release) to
an active window by calling ``send_keys`` method.

You can use any Unicode characters (on Windows) and some special keys listed
below. The module is also available on Linux.

**Available key codes:** ::

    {SCROLLLOCK}, {VK_SPACE}, {VK_LSHIFT}, {VK_PAUSE}, {VK_MODECHANGE},
    {BACK}, {VK_HOME}, {F23}, {F22}, {F21}, {F20}, {VK_HANGEUL}, {VK_KANJI},
    {VK_RIGHT}, {BS}, {HOME}, {VK_F4}, {VK_ACCEPT}, {VK_F18}, {VK_SNAPSHOT},
    {VK_PA1}, {VK_NONAME}, {VK_LCONTROL}, {ZOOM}, {VK_ATTN}, {VK_F10}, {VK_F22},
    {VK_F23}, {VK_F20}, {VK_F21}, {VK_SCROLL}, {TAB}, {VK_F11}, {VK_END},
    {LEFT}, {VK_UP}, {NUMLOCK}, {VK_APPS}, {PGUP}, {VK_F8}, {VK_CONTROL},
    {VK_LEFT}, {PRTSC}, {VK_NUMPAD4}, {CAPSLOCK}, {VK_CONVERT}, {VK_PROCESSKEY},
    {ENTER}, {VK_SEPARATOR}, {VK_RWIN}, {VK_LMENU}, {VK_NEXT}, {F1}, {F2},
    {F3}, {F4}, {F5}, {F6}, {F7}, {F8}, {F9}, {VK_ADD}, {VK_RCONTROL},
    {VK_RETURN}, {BREAK}, {VK_NUMPAD9}, {VK_NUMPAD8}, {RWIN}, {VK_KANA},
    {PGDN}, {VK_NUMPAD3}, {DEL}, {VK_NUMPAD1}, {VK_NUMPAD0}, {VK_NUMPAD7},
    {VK_NUMPAD6}, {VK_NUMPAD5}, {DELETE}, {VK_PRIOR}, {VK_SUBTRACT}, {HELP},
    {VK_PRINT}, {VK_BACK}, {CAP}, {VK_RBUTTON}, {VK_RSHIFT}, {VK_LWIN}, {DOWN},
    {VK_HELP}, {VK_NONCONVERT}, {BACKSPACE}, {VK_SELECT}, {VK_TAB}, {VK_HANJA},
    {VK_NUMPAD2}, {INSERT}, {VK_F9}, {VK_DECIMAL}, {VK_FINAL}, {VK_EXSEL},
    {RMENU}, {VK_F3}, {VK_F2}, {VK_F1}, {VK_F7}, {VK_F6}, {VK_F5}, {VK_CRSEL},
    {VK_SHIFT}, {VK_EREOF}, {VK_CANCEL}, {VK_DELETE}, {VK_HANGUL}, {VK_MBUTTON},
    {VK_NUMLOCK}, {VK_CLEAR}, {END}, {VK_MENU}, {SPACE}, {BKSP}, {VK_INSERT},
    {F18}, {F19}, {ESC}, {VK_MULTIPLY}, {F12}, {F13}, {F10}, {F11}, {F16},
    {F17}, {F14}, {F15}, {F24}, {RIGHT}, {VK_F24}, {VK_CAPITAL}, {VK_LBUTTON},
    {VK_OEM_CLEAR}, {VK_ESCAPE}, {UP}, {VK_DIVIDE}, {INS}, {VK_JUNJA},
    {VK_F19}, {VK_EXECUTE}, {VK_PLAY}, {VK_RMENU}, {VK_F13}, {VK_F12}, {LWIN},
    {VK_DOWN}, {VK_F17}, {VK_F16}, {VK_F15}, {VK_F14}, {VK_MEDIA_NEXT_TRACK},
    {VK_MEDIA_PREV_TRACK}, {VK_MEDIA_STOP}, {VK_MEDIA_PLAY_PAUSE}

    ~ is a shorter alias for {ENTER}

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

Example which shows how to press and hold or release a key on the keyboard: ::

    send_keys("{VK_SHIFT down}"
              "pywinauto"
              "{VK_SHIFT up}") # to type PYWINAUTO

    send_keys("{h down}"
              "{e down}"
              "{h up}"
              "{e up}"
              "llo") # to type hello

Use curly brackers to escape modifiers and type reserved symbols as single keys: ::

    send_keys('{^}a{^}c{%}') # type string "^a^c%" (Ctrl will not be pressed)
    send_keys('{{}ENTER{}}') # type string "{ENTER}" without pressing Enter key

For Windows only, pywinauto defaults to sending a virtual key packet
(VK_PACKET) for textual input.  For applications that do not handle VK_PACKET
appropriately, the ``vk_packet`` option may be set to ``False``.  In this case
pywinauto will attempt to send the virtual key code of the requested key.  This
option only affects the behavior of keys matching [-=[]\;',./a-zA-Z0-9 ].  Note
that upper and lower case are included for a-z.  Both reference the same
virtual key for convenience.

"""
from __future__ import unicode_literals

import sys

if sys.platform == 'win32':
    from .windows.keyboard import KeySequenceError, KeyboardEvent, KeyboardHook, KeyAction, VirtualKeyAction, EscapedKeyAction, PauseAction
    from .windows.keyboard import handle_code, parse_keys, send_keys, LoByte, HiByte
    from .windows.keyboard import INPUT_KEYBOARD, KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_UNICODE, KEYEVENTF_SCANCODE
    from .windows.keyboard import VK_SHIFT, VK_CONTROL, VK_MENU, CODES, MODIFIERS
else:
    from .linux.keyboard import KeySequenceError, KeyAction, PauseAction
    from .linux.keyboard import handle_code, parse_keys, send_keys
    from .linux.keyboard import INPUT_KEYBOARD, KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_UNICODE, KEYEVENTF_SCANCODE
    from .linux.keyboard import VK_SHIFT, VK_CONTROL, VK_MENU, CODES, MODIFIERS
