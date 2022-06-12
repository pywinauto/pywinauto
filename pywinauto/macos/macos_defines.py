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

# accessibility role description
known_roles = {
    'AXApplication': 'Application',
    'AXBrowser': 'Browser',
    'AXBusyIndicator': 'BusyIndicator',
    'AXButton': 'Button',
    'AXCell': 'Cell',
    'AXCheckBox': 'CheckBox',
    'AXColorWell': 'ColorWell',
    'AXColumn': 'Column',
    'AXComboBox': 'ComboBox',
    'AXDateField': 'DateField',
    'AXDisclosureTriangle': 'DisclosureTriangle',
    'AXDockItem': 'DockItem',
    'AXDrawer': 'Drawer',
    'AXGrid': 'Grid',
    'AXGroup': 'Group',
    'AXGrowArea': 'GrowArea',
    'AXHandle': 'Handle',
    'AXHelpTag': 'HelpTag',
    'AXImage': 'Image',
    'AXIncrementor': 'Incrementor',
    'AXLayoutArea': 'LayoutArea',
    'AXLayoutItem': 'LayoutItem',
    'AXLevelIndicator': 'LevelIndicator',
    'AXLink': 'Link',
    'AXList': 'List',
    'AXMatte': 'Matte',
    # AXRoleConstants.h but listed as 'AXMatte': 'Matte',
    'AXMatteRole': 'MatteRole',
    'AXMenu': 'Menu',
    'AXMenuBar': 'MenuBar',
    'AXMenuBarItem': 'MenuBarItem',
    'AXMenuButton': 'MenuButton',
    'AXMenuItem': 'MenuItem',
    'AXOutline': 'Outline',
    'AXPopover': 'Popover',
    'AXPopUpButton': 'PopUpButton',
    'AXProgressIndicator': 'ProgressIndicator',
    'AXRadioButton': 'RadioButton',
    'AXRadioGroup': 'RadioGroup',
    'AXRelevanceIndicator': 'RelevanceIndicator',
    'AXRow': 'Row',
    'AXRuler': 'Ruler',
    'AXRulerMarker': 'RulerMarker',
    'AXScrollArea': 'ScrollArea',
    'AXScrollBar': 'ScrollBar',
    'AXSecureTextField': 'SecureTextField',
    'AXSheet': 'Sheet',
    'AXSlider': 'Slider',
    'AXSortButton': 'SortButton',
    'AXSplitter': 'Splitter',
    'AXSplitGroup': 'SplitGroup',
    'AXStaticText': 'StaticText',
    'AXSystemWide': 'SystemWide',
    'AXTabGroup': 'TabGroup',
    'AXTable': 'Table',
    'AXTextArea': 'TextArea',
    'AXTextField': 'TextField',
    'AXTimeField': 'TimeField',
    'AXToolbar': 'Toolbar',
    'AXUnknown': 'Unknown',
    'AXValueIndicator': 'ValueIndicator',
    'AXWindow': 'Window',

    # Marked by Apple as possibly obsolete:,
    'AXCell': 'Cell',
    'AXPushButton': 'PushButton',
    'AXMatrix': 'Matrix',
    'AXTabView': 'TabView',
    'AXTextView': 'TextView',
    'AXScrollView': 'ScrollView',
    'AXTableHeaderView': 'TableHeaderView',
    'AXTableView': 'TableView',
    'AXView': 'View',
    'AXTablessTabView': 'TablessTabView',
    'AXControl': 'Control',
    'AXForm': 'Form',
    'AXRadioCluster': 'RadioCluster',
    'AXScroller': 'Scroller',
    'AXIndicator': 'Indicator',
    'AXText': 'Text',
    'AXUnknownButton': 'UnknownButton',
    'AXTitledTextField': 'TitledTextField',
    'AXMenuTitle': 'MenuTitle',
    'AXTableColumn': 'TableColumn',
    'AXToolbarIcon': 'ToolbarIcon',
    'AXToolbarOverflowPullDownButton': 'ToolbarOverflowPullDownButton',
    'AXToolbarItemPullDownButton': 'ToolbarItemPullDownButton',
    'AXToolbarItemButton': 'ToolbarItemButton',
    'AXToolbarItemTitle': 'ToolbarItemTitle',
    'AXToolbarItem': 'ToolbarItem',
    'AXBox': 'Box',
    'AXTab': 'Tab',
    'AXWindowTitle': 'WindowTitle',
    'AXCloseBox': 'CloseBox',
    'AXMinimizeBox': 'MinimizeBox',
    'AXZoomBox': 'ZoomBox',
    'AXGrowBox': 'GrowBox',
    'AXToolbarBox': 'ToolbarBox',
    'AXUnknownBox': 'UnknownBox',
    'AXOutlineHeader': 'OutlineHeader',
    'AXOutlineRow': 'OutlineRow',
    'AXStepperRole': 'StepperRole',
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

ax_attributes = {
    "AllowedValues" : "AXAllowedValues",
    "AMPMField" : "AXAMPMField",
    "CancelButton" : "AXCancelButton",
    "Children" : "AXChildren",
    "CloseButton" : "AXCloseButton",
    "ColumnTitle" : "AXColumnTitle",
    "Contents" : "AXContents",
    "DayField" : "AXDayField",
    "DefaultButton" : "AXDefaultButton",
    "Description" : "AXDescription",
    "Enabled" : "AXEnabled",
    "Expanded" : "AXExpanded",
    "Focused" : "AXFocused",
    "Frame"   : "AXFrame",
    "GrowArea" : "AXGrowArea",
    "Header" : "AXHeader",
    "Help" : "AXHelp",
    "Hidden": "AXHidden",
    "HourField" : "AXHourField",
    "Incrementor" : "AXIncrementor",
    "InsertionPointLineNumber" : "AXInsertionPointLineNumber",
    "Main" : "AXMain",
    "MaxValue" : "AXMaxValue",
    "MinimizeButton" : "AXMinimizeButton",
    "Minimized" : "AXMinimized",
    "MinuteField" : "AXMinuteField",
    "MinValue" : "AXMinValue",
    "Modal" : "AXModal",
    "MonthField" : "AXMonthField",
    "NumberOfCharacters" : "AXNumberOfCharacters",
    "Orientation" : "AXOrientation",
    "Parent" : "AXParent",
    "Placeholder" : "AXPlaceholderValue",
    "Position" : "AXPosition",
    "Proxy" : "AXProxy",
    "Role" : "AXRole",
    "RoleDescription" : "AXRoleDescription",
    "SecondField" : "AXSecondField",
    "Selected" : "AXSelected",
    "SelectedChildren" : "AXSelectedChildren",
    "SelectedText" : "AXSelectedText",
    "SelectedTextRange" : "AXSelectedTextRange",
    "SelectedTextRanges" : "AXSelectedTextRanges",
    "SharedCharacterRange" : "AXSharedCharacterRange",
    "SharedTextUIElements" : "AXSharedTextUIElements",
    "Size" : "AXSize",
    "Subrole" : "AXSubrole",
    "Title" : "AXTitle",
    "ToolbarButton" : "AXToolbarButton",
    "TopLevelUIElement" : "AXTopLevelUIElement",
    "URL" : "AXURL",
    "Value" : "AXValue",
    "ValueDescription" : "AXValueDescription",
    "ValueIncrement" : "AXValueIncrement",
    "VisibleCharacterRange" : "AXVisibleCharacterRange",
    "VisibleChildren" : "AXVisibleChildren",
    "VisibleColumns" : "AXVisibleColumns",
    "Window" : "AXWindow",
    "YearField" : "AXYearField",
    "ZoomButton" : "AXZoomButton"
}

# This constants are not availible in pyobjc < 6.2
kAXValueTypeIllegal = 0
kAXValueTypeCGPoint = 1
kAXValueTypeCGSize  = 2
kAXValueTypeCGRect  = 3
kAXValueTypeCFRange = 4
kAXValueTypeAXError = 5
