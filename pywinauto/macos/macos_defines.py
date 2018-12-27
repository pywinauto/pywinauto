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


from Quartz.CoreGraphics import (kCGEventFlagMaskAlphaShift, kCGEventFlagMaskShift,
    kCGEventFlagMaskAlternate, kCGEventFlagMaskCommand, kCGEventFlagMaskHelp,
    kCGEventFlagMaskSecondaryFn, kCGMouseButtonCenter, kCGEventFlagMaskControl,
    kCGEventFlagMaskNumericPad, kCGEventFlagMaskNonCoalesced, kCGMouseButtonLeft,
    kCGMouseButtonRight, kCGEventTabletProximity, kCGEventOtherMouseDown,
    kCGEventNull, kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventRightMouseDown,
    kCGEventRightMouseUp, kCGEventKeyUp, kCGEventTapDisabledByUserInput,
    kCGEventMouseMoved, kCGEventLeftMouseDragged, kCGEventRightMouseDragged, kCGEventKeyDown,
    kCGEventFlagsChanged, kCGEventScrollWheel, kCGEventTabletPointer,
    kCGEventOtherMouseUp, kCGEventOtherMouseDragged, kCGEventTapDisabledByTimeout,
    kCGHIDEventTap, kCGSessionEventTap, kCGAnnotatedSessionEventTap)

known_roles = {
    'Application' : "AXApplication",
    'Button' : "AXButton",
    'Cell' : "AXCell",
    'Column' : "AXColumn",
    'Group' : "AXGroup",
    'Heading' : "AXHeading",
    'Link' : "AXLink",
    'Image' : "AXImage",
    'MenuBarItem' : "AXMenuBarItem",
    'RadioButton' : "AXRadioButton",
    'Row' : "AXRow",
    'SafariAddressAndSearchField' : "AXSafariAddressAndSearchField",
    'ScrollBar' : "AXScrollBar",
    'SplitGroup' : "AXSplitGroup",
    'StaticText' : "AXStaticText",
    'ScrollArea' : "AXScrollArea",
    'Splitter' : "AXSplitter",
    'TabGroup' : "AXTabGroup",
    'Table' : "AXTable",
    'Toolbar' : "AXToolbar",
    'TextArea' : "AXTextArea",
    'TextField' : "AXTextField",
    'MenuBar' : "AXMenuBar",
    'WebArea' : "AXWebArea",
    'Window' : "AXWindow",
}

keyboard_event_flags_map = {
    'alpha_shift' : kCGEventFlagMaskAlphaShift,
    'shift' : kCGEventFlagMaskShift,
    'control' : kCGEventFlagMaskControl,
    'alternate' : kCGEventFlagMaskAlternate,
    'command' : kCGEventFlagMaskCommand,
    'with_help' : kCGEventFlagMaskHelp,
    'secondary_fn' : kCGEventFlagMaskSecondaryFn,
    'numeric_pad' : kCGEventFlagMaskNumericPad,
    'non_coalesced' : kCGEventFlagMaskNonCoalesced,
}

mouse_buttons_map = {
    "left" : kCGMouseButtonLeft,
    "right" : kCGMouseButtonRight,
    "middle": kCGMouseButtonCenter,
}

mouse_event_type_map = {
    "null" : kCGEventNull,
    "left_mouse_down" : kCGEventLeftMouseDown,
    "left_mouse_up" : kCGEventLeftMouseUp,
    "right_mouse_down" : kCGEventRightMouseDown,
    "right_mouse_up" : kCGEventRightMouseUp,
    "mouse_moved" : kCGEventMouseMoved,
    "left_mouse_dragged" : kCGEventLeftMouseDragged,
    "right_mouse_dragged" : kCGEventRightMouseDragged,
    "key_down" : kCGEventKeyDown,
    "key_up" : kCGEventKeyUp,
    "flags_changed" : kCGEventFlagsChanged,
    "scroll_wheel" : kCGEventScrollWheel,
    "tablet_pointer" : kCGEventTabletPointer,
    "tablet_proximity" : kCGEventTabletProximity,
    "other_mouse_down" : kCGEventOtherMouseDown,
    "other_mouse_up" : kCGEventOtherMouseUp,
    "other_mouse_dragged" : kCGEventOtherMouseDragged,
    "tap_disabled_by_timeout" : kCGEventTapDisabledByTimeout,
    "tap_disabled_by_user_input" : kCGEventTapDisabledByUserInput,
}

event_tap_location = {
    # Specifies that an event tap is placed at the point where HID system events enter the window server.
    "hid_event_tap":kCGHIDEventTap,

    # Specifies that an event tap is placed at the point where HID system and remote control events
    # enter a login session.
    "session_event_tap":kCGSessionEventTap,

    # Specifies that an event tap is placed at the point where session events have been annotated to
    # flow to an application.
    "annotated_session_event_tap":kCGAnnotatedSessionEventTap,
}
