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

import time

import ctypes	 # write_debug_text action
import SendKeys  # typekeys action

from win32defines import *
import win32functions
import win32structures

import findbestmatch
import tests

# we need a delay after button click
delay_after_click = .05
		
class ControlNotEnabled(RuntimeError):
	pass

class ControlNotVisible(RuntimeError):
	pass



def verify_actionable(ctrl):
	verify_enabled(ctrl)
	verify_visible(ctrl)

def verify_enabled(ctrl):
	if not ctrl.FriendlyClassName == "Dialog":
		if not ctrl.Parent.IsEnabled:
			raise ControlNotEnabled()

	if not ctrl.IsEnabled:
		raise ControlNotEnabled()

def verify_visible(ctrl):
	if not ctrl.IsVisible or not ctrl.Parent.IsVisible:
		raise ControlNotVisible()



mouse_flags = {
	"left": MK_LBUTTON,
	"right": MK_RBUTTON,
	"middle": MK_MBUTTON,
	"shift": MK_SHIFT,
	"control": MK_CONTROL,
}


def calc_flags_and_coords(pressed, coords):
	flags = 0
	
	for key in pressed.split():	
		flags |= mouse_flags[key.lower()]
	
	click_point = coords[0] << 16 | coords[1]
	
	return flags, click_point

# TODO: Test simulating mouse clicks using SendInput of WM_* messages
def perform_click(ctrl, button = "left", pressed = "", coords = (0, 0), double = False, down = True, up = True):
	verify_enabled(ctrl)
	
	msgs  = []
	if not double:
		if button.lower() == "left":
			if down:
				msgs.append(WM_LBUTTONDOWN)
			if up:
				msgs.append(WM_LBUTTONUP)

		elif button.lower() == "middle":
			if down:
				msgs.append(WM_MBUTTONDOWN)
			if up:
				msgs.append(WM_MBUTTONUP)

		elif button.lower() == "right":
			if down:
				msgs.append(WM_RBUTTONDOWN)
			if up:
				msgs.append(WM_RBUTTONUP)

	else:
		if button.lower() == "left":
			msgs = (WM_LBUTTONDOWN, WM_LBUTTONUP, WM_LBUTTONDBLCLK, WM_LBUTTONUP)
		elif button.lower() == "middle":	
			msgs = (WM_MBUTTONDOWN, WM_MBUTTONUP, WM_MBUTTONDBLCLK, WM_MBUTTONUP)
		elif button.lower() == "right":
			msgs = (WM_RBUTTONDOWN, WM_RBUTTONUP, WM_RBUTTONDBLCLK, WM_RBUTTONUP)


	flags, click_point = calc_flags_and_coords(pressed, coords)
	
	for msg in msgs:
		ctrl.PostMessage(msg, flags, click_point)
	
	#ctrl.PostMessage(msg, 1, click_point)
	time.sleep(delay_after_click)
	

#====================================================================
def click_action(ctrl, button = "left", pressed = "", coords = (0, 0), double = False):
	#print ctrl.Text, ctrl.Class, ctrl.Rectangle, ctrl.Parent.Text
	perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def doubleclick_action(ctrl, button = "left", pressed = "", coords = (0, 0), double = True):
	perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def rightclick_action(ctrl, button = "right", pressed = "", coords = (0, 0), double = True):
	perform_click(ctrl, button, pressed, coords, double)

#====================================================================
def check_button_action(ctrl, select = True):
	ctrl.SendMessage(BM_SETCHECK, 1)

#====================================================================
def uncheck_button_action(ctrl, select = True):
	ctrl.SendMessage(BM_SETCHECK, 0)

#====================================================================
def press_mouse_action(ctrl, button = "left", pressed = "", coords = (0, 0)):
	flags, click_point = calc_flags_and_coords(pressed, coords)	

	perform_click(ctrl, button, pressed, coords, up = False)

#====================================================================
def release_mouse_action(ctrl, button = "left", pressed = "", coords = (0, 0)):
	flags, click_point = calc_flags_and_coords(pressed, coords)	
	perform_click(ctrl, button, pressed, coords, down = False)
	
#====================================================================
def move_mouse_action(ctrl, pressed = "left", coords = (0, 0)):
	flags, click_point = calc_flags_and_coords(pressed, coords)	
	ctrl.PostMessage(WM_MOUSEMOVE, flags, click_point)

#====================================================================
def settext_action(ctrl, text, append = False):
	if append:
		text = ctrl.Text + text
		
	text = c_wchar_p(unicode(text))
	ctrl.PostMessage(WM_SETTEXT, 0, text)

#====================================================================
def typekeys_action(
	ctrl, 
	keys, 
	pause = 0.05, 
	with_spaces = False,
    with_tabs = False, 
    with_newlines = False, 
    turn_off_numlock = True):

	verify_enabled(ctrl)
	
	win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), ctrl.ProcessID, 1)
	win32functions.SetForegroundWindow(ctrl)
	SendKeys.SendKeys(keys.encode('mbcs'), pause, with_spaces, with_tabs, with_newlines, turn_off_numlock)
	win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), ctrl.ProcessID, 0)
	


#====================================================================
def combobox_select(ctrl, item):
	verify_enabled(ctrl)

	if isinstance(item, (int, long)):
		index = item
	else:
		index = ctrl.Texts.index(item)
	
	ctrl.PostMessage(CB_SETCURSEL, index, 0)
	ctrl.PostMessage(CBN_SELCHANGE)
	


#====================================================================
def listbox_select(ctrl, item):
	verify_enabled(ctrl)

	if isinstance(item, (int, long)):
		index = item
	else:
		index = ctrl.Texts.index(item)
	
	ctrl.PostMessage(LB_SETCURSEL, index, 0)
	ctrl.PostMessage(LBN_SELCHANGE)



#====================================================================
def set_edit_text(ctrl, text, pos_start = 0, pos_end = -1):
	verify_enabled(ctrl)

	set_edit_selection(ctrl, pos_start, pos_end)
	
	text = c_wchar_p(unicode(text))
	ctrl.SendMessage(EM_REPLACESEL, True, text)
	
	

#====================================================================
def set_edit_selection(ctrl, start = 0, end = -1):
	verify_enabled(ctrl)

	# if we have been asked to select a string
	if isinstance(start, basestring):
		string_to_select = start
		# 
		start = ctrl.texts[1].index(string_to_select)
		end = start + len(string_to_select)

	ctrl.PostMessage(EM_SETSEL, start, end)



#====================================================================
def select_tab_action(ctrl, tab):
	verify_enabled(ctrl)
	
	if isinstance(tab, basestring):
		# find the string in the tab control
		bestText = findbestmatch.find_best_match(tab, ctrl.Texts, ctrl.Texts)
		tab = ctrl.Texts.index(bestText) - 1
	
	ctrl.SendMessage(TCM_SETCURFOCUS, tab)


#====================================================================
def select_menuitem_action(ctrl, path, items = None):
	verify_enabled(ctrl)
	
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
		ctrl.PostMessage(WM_COMMAND, item['ID'])
	

#====================================================================
def write_debug_text(ctrl, text):
	dc = win32functions.CreateDC(u"DISPLAY", None, None, None )
	
	if not dc:
		raise ctypes.WinError()
	
	rect = ctrl.Rectangle
	
	#ret = win32functions.TextOut(dc, rect.left, rect.top, unicode(text), len(text))
	ret = win32functions.DrawText(dc, unicode(text), len(text), ctypes.byref(rect), DT_SINGLELINE)
	
	if not ret:
		raise ctypes.WinError()


#====================================================================
def draw_outline(ctrl, colour = 'green', thickness = 2, fill = BS_NULL, rect = None):

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
	hPen = win32functions.CreatePen(PS_SOLID, 2, colour)
	
	# create the brush (inside)
	brush = win32structures.LOGBRUSH()
	brush.lbStyle = fill
	brush.lbHatch = HS_DIAGCROSS	
	hBrush = win32functions.CreateBrushIndirect(byref(brush))

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




def run_tests_action(ctrl, tests_to_run = None):
	# get all teh controls
	controls = [ctrl]
	controls.extend(ctrl.Children)
	
	return tests.run_tests(controls, tests_to_run)
	
	


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
		RunTests = run_tests_action,
	),

}	




#=========================================================================
def deferred_func(func):
	def func_wrapper(ctrl, *args, **kwargs):
		
		return func(ctrl._, *args, **kwargs)
		
	return func_wrapper

#=========================================================================
def identity(func):
	return func


#=========================================================================
def add_actions(to_obj, deferred = False):
	# add common actions:
	import application
	
	#if hasattr(to_obj, "_"):
	#	defer_action = deferred_func
	#	ctrl = to_obj._		
	#else:
	defer_action = identity
	ctrl = to_obj
		
	# for each of the standard actions
	for action_name in standard_action_funcs:
		# add it to the control class
		setattr (to_obj.__class__, action_name, defer_action(standard_action_funcs[action_name]))
	
	if class_specific_actions.has_key(ctrl.FriendlyClassName):
		actions = class_specific_actions[ctrl.FriendlyClassName]
	
		for action_name, action_func in actions.items():
			setattr (to_obj.__class__, action_name, defer_action(action_func))
	
	# add some specific ones
	if to_obj.MenuItems:
		setattr (to_obj.__class__, "MenuSelect", defer_action(select_menuitem_action))
	
	return to_obj
		



	return ctrl