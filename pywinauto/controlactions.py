# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
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

"Actions for controls"

__revision__ = "$Revision$"


import time

import ctypes	 # write_debug_text action
import SendKeys  # typekeys action

import win32defines
import win32functions
import win32structures

import handleprops
import findbestmatch
import tests

# we need a slight delay after button click
# In most cases to allow the window to close
delay_after_click = .08
delay_after_menuselect = .08
delay_after_sendkeys_key = .001

class ControlNotEnabled(RuntimeError):
    "Raised when a control is not enabled"
    pass

class ControlNotVisible(RuntimeError):
    "Raised when a control is nto visible"
    pass



#====================================================================
def verify_actionable(ctrl):
    "Verify that the control is visible and enabled"

    verify_enabled(ctrl)
    verify_visible(ctrl)

#====================================================================
def verify_enabled(ctrl):
    "Verify that the control is enabled"
    # check is the parent enabled first
    if not handleprops.friendlyclassname(ctrl) == "Dialog":
        if not ctrl.Parent.IsEnabled:
            raise ControlNotEnabled()

    # then check if the control itself is enabled
    if not ctrl.IsEnabled:
        raise ControlNotEnabled()

#====================================================================
def verify_visible(ctrl):
    "Verify that the control is visible"
    if not ctrl.IsVisible or not ctrl.Parent.IsVisible:
        raise ControlNotVisible()


mouse_flags = {
    "left": win32defines.MK_LBUTTON,
    "right": win32defines.MK_RBUTTON,
    "middle": win32defines.MK_MBUTTON,
    "shift": win32defines.MK_SHIFT,
    "control": win32defines.MK_CONTROL,
}


#====================================================================
def calc_flags_and_coords(pressed, coords):
    "Calculate the flags to use and the coordinates"
    flags = 0

    for key in pressed.split():
        flags |= mouse_flags[key.lower()]

    click_point = win32functions.MakeLong(coords[1], coords[0])

    return flags, click_point


#====================================================================
# TODO: Test simulating mouse clicks using SendInput instead of WM_* messages
def perform_click(
        ctrl,
        button = "left",
        pressed = "",
        coords = (0, 0),
        double = False,
        down = True,
        up = True):
    "Low level method for performing click operations"

    verify_enabled(ctrl)

    msgs  = []
    if not double:
        if button.lower() == "left":
            if down:
                msgs.append(win32defines.WM_LBUTTONDOWN)
            if up:
                msgs.append(win32defines.WM_LBUTTONUP)

        elif button.lower() == "middle":
            if down:
                msgs.append(win32defines.WM_MBUTTONDOWN)
            if up:
                msgs.append(win32defines.WM_MBUTTONUP)

        elif button.lower() == "right":
            if down:
                msgs.append(win32defines.WM_RBUTTONDOWN)
            if up:
                msgs.append(win32defines.WM_RBUTTONUP)

    else:
        if button.lower() == "left":
            msgs = (
                win32defines.WM_LBUTTONDOWN,
                win32defines.WM_LBUTTONUP,
                win32defines.WM_LBUTTONDBLCLK,
                win32defines.WM_LBUTTONUP)
        elif button.lower() == "middle":
            msgs = (
                win32defines.WM_MBUTTONDOWN,
                win32defines.WM_MBUTTONUP,
                win32defines.WM_MBUTTONDBLCLK,
                win32defines.WM_MBUTTONUP)
        elif button.lower() == "right":
            msgs = (
                win32defines.WM_RBUTTONDOWN,
                win32defines.WM_RBUTTONUP,
                win32defines.WM_RBUTTONDBLCLK,
                win32defines.WM_RBUTTONUP)


    flags, click_point = calc_flags_and_coords(pressed, coords)

    for msg in msgs:
        ctrl.PostMessage(msg, flags, click_point)

    #ctrl.PostMessage(msg, 1, click_point)
    time.sleep(delay_after_click)


#====================================================================
def click_action(
    ctrl, button = "left", pressed = "", coords = (0, 0), double = False):
    "Peform a click action"
    #print ctrl.Text, ctrl.Class, ctrl.Rectangle, ctrl.Parent.Text
    perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def doubleclick_action(
    ctrl, button = "left", pressed = "", coords = (0, 0), double = True):
    "Perform a double click action"
    perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def rightclick_action(
    ctrl, button = "right", pressed = "", coords = (0, 0), double = True):
    "Perform a right click action"
    perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def check_button_action(ctrl):
    "Check a checkbox"
    ctrl.SendMessage(win32defines.BM_SETCHECK, win32defines.BST_CHECKED)

#====================================================================
def uncheck_button_action(ctrl):
    "Uncheck a checkbox"
    ctrl.SendMessage(win32defines.BM_SETCHECK, win32defines.BST_UNCHECKED)

#====================================================================
def setcheck_indet_button_action(ctrl):
    "Set the checkbox to indeterminate"
    ctrl.SendMessage(win32defines.BM_SETCHECK, win32defines.BST_INDETERMINATE)


#====================================================================
def press_mouse_action(ctrl, button = "left", pressed = "", coords = (0, 0)):
    "Press the mouse button"
    flags, click_point = calc_flags_and_coords(pressed, coords)

    perform_click(ctrl, button, pressed, coords, up = False)

#====================================================================
def release_mouse_action(ctrl, button = "left", pressed = "", coords = (0, 0)):
    "Release the mouse button"
    flags, click_point = calc_flags_and_coords(pressed, coords)
    perform_click(ctrl, button, pressed, coords, down = False)

#====================================================================
def move_mouse_action(ctrl, pressed = "left", coords = (0, 0)):
    "Move the mouse"
    flags, click_point = calc_flags_and_coords(pressed, coords)
    ctrl.PostMessage(win32defines.WM_MOUSEMOVE, flags, click_point)

#====================================================================
def settext_action(ctrl, text, append = False):
    "Set the text of the window"

    if append:
        text = ctrl.Text + text

    text = ctypes.c_wchar_p(unicode(text))
    ctrl.PostMessage(win32defines.WM_SETTEXT, 0, text)

#====================================================================
def typekeys_action(
    ctrl,
    keys,
    pause = delay_after_sendkeys_key,
    with_spaces = False,
    with_tabs = False,
    with_newlines = False,
    turn_off_numlock = True):
    "Type keys to the window using SendKeys"

    verify_enabled(ctrl)

    win32functions.AttachThreadInput(
        win32functions.GetCurrentThreadId(), ctrl.ProcessID, 1)
    win32functions.SetForegroundWindow(ctrl)
    SendKeys.SendKeys(
        keys.encode('mbcs'),
        pause, with_spaces,
        with_tabs,
        with_newlines,
        turn_off_numlock)
    win32functions.AttachThreadInput(
        win32functions.GetCurrentThreadId(), ctrl.ProcessID, 0)




#====================================================================
def combobox_select(ctrl, item):
    """Select the ComboBox item

    item can be either a 0 based index of the item to select
    or it can be the string that you want to select
    """
    verify_enabled(ctrl)

    # Make sure we have an index  so if passed in a
    # string then find which item it is
    if isinstance(item, (int, long)):
        index = item
    else:
        index = ctrl.Texts.index(item) -1

    # change the selected item
    ctrl.SendMessage(win32defines.CB_SETCURSEL, index, 0)

    # Notify the parent that we have changed
    ctrl.NotifyParent(win32defines.CBN_SELCHANGE)

    return ctrl


#====================================================================
def listbox_select(ctrl, item):
    """Select the ListBox item

    item can be either a 0 based index of the item to select
    or it can be the string that you want to select
    """
    verify_enabled(ctrl)

    # Make sure we have an index  so if passed in a
    # string then find which item it is
    if isinstance(item, (int, long)):
        index = item
    else:
        index = ctrl.Texts.index(item)

    # change the selected item
    ctrl.PostMessage(win32defines.LB_SETCURSEL, index, 0)

    # Notify the parent that we have changed
    ctrl.NotifyParent(win32defines.LBN_SELCHANGE)

    return ctrl


#====================================================================
def set_edit_text(ctrl, text, pos_start = 0, pos_end = -1):
    "Set the text of the edit control"
    verify_enabled(ctrl)

    set_edit_selection(ctrl, pos_start, pos_end)

    text = ctypes.c_wchar_p(unicode(text))
    ctrl.SendMessage(win32defines.EM_REPLACESEL, True, text)



#====================================================================
def set_edit_selection(ctrl, start = 0, end = -1):
    "Set the edit selection of the edit control"
    verify_enabled(ctrl)

    # if we have been asked to select a string
    if isinstance(start, basestring):
        string_to_select = start
        #
        start = ctrl.texts[1].index(string_to_select)
        end = start + len(string_to_select)

    ctrl.PostMessage(win32defines.EM_SETSEL, start, end)



#====================================================================
def select_tab_action(ctrl, tab):
    "Select the specified tab on teh tab control"

    verify_enabled(ctrl)

    if isinstance(tab, basestring):
        # find the string in the tab control
        bestText = findbestmatch.find_best_match(tab, ctrl.Texts, ctrl.Texts)
        tab = ctrl.Texts.index(bestText) - 1

    ctrl.SendMessage(win32defines.TCM_SETCURFOCUS, tab)


#====================================================================
def select_menuitem_action(ctrl, path, items = None):
    "Select the menuitem specifed in path"
    verify_enabled(ctrl)

    # if the menu items haven't been passed in then
    # get them from the window
    if not items:
        items = ctrl.MenuItems

    # get the text names from the menu items
    item_texts = [item['Text'] for item in items]

    # get the first part (and remainder)
    parts = path.split("->", 1)
    current_part = parts[0]

    # find the item that best matches the current part
    item = findbestmatch.find_best_match(current_part, item_texts, items)

    # if there are more parts - then get the next level
    if parts[1:]:
        select_menuitem_action(ctrl, "->".join(parts[1:]), item['MenuItems'])
    else:

        # unfortunately this is not always reliable :-(
        #if item['State'] & MF_DISABLED or item['State'] & MF_GRAYED:
        #	raise "TODO - replace with correct exception: " \
        #       "Menu item is not enabled"

        #ctrl.PostMessage(WM_MENURBUTTONUP, win32functions.GetMenu(ctrl))
        #ctrl.PostMessage(WM_COMMAND, 0, item['ID'])
        ctrl.NotifyMenuSelect(item['ID'])

    time.sleep(delay_after_menuselect)


#====================================================================
def write_debug_text(ctrl, text):
    "Write some debug text over the window"
    dc = win32functions.CreateDC(u"DISPLAY", None, None, None )

    if not dc:
        raise ctypes.WinError()

    rect = ctrl.Rectangle

    #ret = win32functions.TextOut(
    #    dc, rect.left, rect.top, unicode(text), len(text))
    ret = win32functions.DrawText(
        dc,
        unicode(text),
        len(text),
        ctypes.byref(rect),
        win32defines.DT_SINGLELINE)

    if not ret:
        raise ctypes.WinError()


#====================================================================
def draw_outline(
    ctrl,
    colour = 'green',
    thickness = 2,
    fill = win32defines.BS_NULL,
    rect = None):
    "Draw an outline around the window"
    colours = {
        "green" : 0x00ff00,
        "blue" : 0xff0000,
        "red" : 0x0000ff,
    }

    # if it's a known colour
    if colour in colours:
        colour = colours[colour]

    if not rect:
        rect = ctrl.Rectangle

    # create the pen(outline)
    hPen = win32functions.CreatePen(win32defines.PS_SOLID, thickness, colour)

    # create the brush (inside)
    brush = win32structures.LOGBRUSH()
    brush.lbStyle = fill
    brush.lbHatch = win32defines.HS_DIAGCROSS
    hBrush = win32functions.CreateBrushIndirect(ctypes.byref(brush))

    # get the Device Context
    dc = win32functions.CreateDC(u"DISPLAY", None, None, None )

    # push our objects into it
    win32functions.SelectObject(dc, hBrush)
    win32functions.SelectObject(dc, hPen)

    win32functions.Rectangle(dc, rect.left, rect.top, rect.right, rect.bottom)

    # Delete the brush and pen we created
    win32functions.DeleteObject(hBrush)
    win32functions.DeleteObject(hPen)

    # delete the Display context that we created
    win32functions.DeleteDC(dc)




def Dialog_RunTests(ctrl, tests_to_run = None):
    "Run the tests on dialog"

    # get all teh controls
    controls = [ctrl]
    controls.extend(ctrl.Children)

    return tests.run_tests(controls, tests_to_run)


# TODO: Make the RemoteMemoryBlock stuff more automatic!
def listview_checkbox_uncheck_action(ctrl, item):
    "Uncheck the ListView item"
    lvitem = win32structures.LVITEMW()

    lvitem.mask = win32defines.LVIF_STATE
    lvitem.state = 0x1000
    lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK

    from controls.common_controls import RemoteMemoryBlock

    remoteMem = RemoteMemoryBlock(ctrl)
    remoteMem.Write(lvitem)

    ctrl.SendMessage(win32defines.LVM_SETITEMSTATE, item, remoteMem.Address())

    del remoteMem


def listview_checkbox_check_action(ctrl, item):
    "Check the ListView item"
    lvitem = win32structures.LVITEMW()

    lvitem.mask = win32defines.LVIF_STATE
    lvitem.state = 0x2000
    lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK

    from controls.common_controls import RemoteMemoryBlock

    remoteMem = RemoteMemoryBlock(ctrl)
    remoteMem.Write(lvitem)

    ctrl.SendMessage(win32defines.LVM_SETITEMSTATE, item, remoteMem.Address())

    del remoteMem

def listview_isitemchecked_action(ctrl, item):
    "Return whether the ListView item is checked or not"
    state = ctrl.SendMessage(
        win32defines.LVM_GETITEMSTATE, item, win32defines.LVIS_STATEIMAGEMASK)

    return state & 0x2000


def listbox_setfocusitem_action(ctrl, item):
    "Set the ListBox focus to the item at index"

    # if it is a multiple selection dialog
    if ctrl.HasStyle(win32defines.LBS_EXTENDEDSEL) or \
        ctrl.HasStyle(win32defines.LBS_MULTIPLESEL):
        ctrl.SendMessage(win32defines.LB_SETCARETINDEX, item)
    else:
        ctrl.SendMessage(win32defines.LB_SETCURSEL, item)


def listbox_getcurrentselection_action(ctrl):
    "Retrun the index of current selection in a ListBox"
    return ctrl.SendMessage(win32defines.LB_GETCARETINDEX)





######ANYWIN
#CaptureBitmap
#GetAppId
#GetCaption
#GetChildren
#GetClass
#GetHandle
#GetNativeClass
#GetParent
#IsEnabled
#IsVisible
#TypeKeys
#Click
#DoubleClick

#GetHelpText


#ClearTrap
#Exists
#GenerateDecl
#GetArrayProperty
#GetBitmapCRC
#GetContents
#GetEverything
#GetIDGetIndex
#GetInputLanguage
#GetManyProperties
#GetName
#GetProperty
#GetPropertyList
#GetRect
#GetTag
#InvokeMethods
#IsActive
#IsArrayProperty
#IsDefined
#IsOfClass
#InvokeJava
#MenuSelect
#MoveMouse
#MultiClick
#PopupSelect
#PressKeys
#PressMouse
#ReleaseKeys
#ReleaseMouse
#ScrollIntoView
#SetArrayProperty
#SetInputLanguage
#SetProperty
#SetTrap
#VerifyActive
#VerifyBitmap
#VerifyEnabled
#VerifyEverything
#VerifyText
#VerifyProperties
#WaitBitmap
#Properties
#
#bActive
#AppId
#sCaption
#lwChildren
#Class
#bEnabled
#bExists
#sID
#iIndex
#sName
#wParent
#Rect
#hWnd
#WndTag
#
#
######CONTROL
#GetPriorStatic
#HasFocus
#SetFocus
#VerifyFocus
#
######BUTTON
#Click
#IsIndeterminate
#IsPressed
#
#
#####CHECKBOX
#Check
#GetState
#IsChecked
#SetState
#Toggle
#Uncheck
#VerifyValue
#
#bChecked
#bValue
#
#
#####MENUITEM
#Check
#IsChecked
#Pick
#Uncheck
#VerifyChecked
#
#bChecked
#
#
#####COMBOBOX
#ClearText
#FindItem
#GetContents
#GetItemCount
#GetItemText
#GetSelIndex
#GetSelText
#GetText
#Select
#SetText
#VerifyContents
#VerifyText
#VerifyValue
#
#lsContents
#iItemCount
#iValue
#sValue
#
#####LISTBOX
#BeginDrag
#DoubleSelect
#EndDrag
#ExtendSelect
#FindItem
#GetContents
#GetItemCount
#GetItemText
#GetMultiSelIndex
#GetMultiSelText
#GetSelIndex
#GetSelText
#IsExtendSel
#IsMultiSel
#MultiSelect
#MultiUnselect
#Select
#SelectList
#SelectRange
#VerifyContents
#VerifyValue
#
#lsContents
#bIsExtend
#bIsMulti
#iItemCount
#iValue
#liValue
#lsValue
#sValue
#
#
#####EDIT
#ClearText
#GetContents
#GetFontName
#GetFontSize
#GetMultiSelText
#GetMultiText
#GetPosition
#GetSelRange
#GetSelText
#GetText
#IsBold
#IsItalic
#IsMultiText
#IsRichText
#IsUnderline
#SetMultiText
#SetPosition
#SetSelRange
#SetText
#VerifyPosition
#VerifySelRange
#VerifySelText
#VerifyValue
#
#bIsMulti
#lsValue
#sValue
#
#
#####LISTVIEW
#BeginDrag
#DoubleSelect
#EndDrag
#ExposeItem
#ExtendSelect
#FindItem
#GetColumnCount
#GetColumnName
#GetContents
#GetItemImageState
#GetItemImageIndex
#GetItemRect
#GetItemText
#GetMultiSelIndex
#GetMultiSelText
#GetSelIndex
#GetSelText
#GetView
#method
#(ListView)
#IsExtendSel
#IsMultiSel
#MultiSelect
#MultiUnselect
#PressItem
#ReleaseItem
#Select
#SelectList
#SelectRange
#VerifyContents
#VerifyValue
#
#
#####TREEVIEW
#BeginDrag
#Collapse
#DoubleSelect
#EndDrag
#Expand
#ExposeItem
#ExtendSelect
#FindItem
#GetContents
#GetItemCount
#GetItemImageIndex
#GetItemImageState
#GetItemLevel
#GetItemRect
#GetItemText
#GetSelIndex
#GetSelText
#GetSubItemCount
#GetSubItems
#IsItemEditable
#IsItemExpandable
#IsItemExpanded
#MultiSelect
#MultiUnselect
#PressItem
#ReleaseItem
#Select
#SelectList
#VerifyContents
#VerifyValue
#
#####Static
#GetText
#VerifyValue


standard_action_funcs = dict(
    Click = click_action,
    RightClick = rightclick_action,
    DoubleClick = doubleclick_action,

    TypeKeys = typekeys_action,
    SetText = settext_action,

    ReleaseMouse = release_mouse_action,
    MoveMouse = move_mouse_action,
    PressMouse = press_mouse_action,

    DebugMessage = write_debug_text,
    DrawOutline = draw_outline,
    )


class_specific_actions = {

    'ComboBox' : dict(
        Select = combobox_select,
    ),

    'ListBox' : dict(
        Select = listbox_select,
        FocusItem = listbox_getcurrentselection_action,
        SetFocus = listbox_setfocusitem_action,
    ),


    'ListView' : dict(
        Check = listview_checkbox_check_action,
        UnCheck = listview_checkbox_uncheck_action,
        IsChecked = listview_isitemchecked_action,
    ),

    'Edit' : dict(
        Select = set_edit_selection,
        SetText = set_edit_text,
    ),

    'CheckBox' : dict(
        Check = check_button_action,
        UnCheck = uncheck_button_action,
    ),

    'Button' : dict(
        Check = check_button_action,
        UnCheck = uncheck_button_action,
    ),
    "TabControl" : dict(
        Select = select_tab_action,
    ),
    "Dialog" : dict(
        RunTests = Dialog_RunTests,
    ),

}


#=========================================================================
def add_actions(to_obj):
    "Add the appropriate actions to the control"

    # for each of the standard actions
    for action_name in standard_action_funcs:
        # add it to the control class
        setattr (
            to_obj.__class__, action_name, standard_action_funcs[action_name])

    # check if there are actions specific to this type of control
    if class_specific_actions.has_key(to_obj.FriendlyClassName):

        # apply these actions to the class
        actions = class_specific_actions[to_obj.FriendlyClassName]
        for action_name, action_func in actions.items():
            setattr (to_obj.__class__, action_name, action_func)

    # If the object has menu items allow MenuSelect
    if to_obj.MenuItems:
        to_obj.__class__.MenuSelect =  select_menuitem_action

    return to_obj

