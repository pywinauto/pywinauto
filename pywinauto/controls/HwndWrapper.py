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

# pylint:  disable-msg=W0611
import re
from pprint import pprint

from ctypes import * 

# I leave this optional because PIL is a large dependency
try:
	import PIL.ImageGrab
except ImportError:
    pass
    

from pywinauto.win32defines import *
from pywinauto.win32functions import *
from pywinauto.win32structures import *

import handleprops


#====================================================================
def WrapHandle(hwnd, isDialog = False):

	default_wrapper = HwndWrapper(hwnd)
		
	for wrapper_name in HwndWrappers:
		if re.match(wrapper_name, default_wrapper.Class):
			return HwndWrappers[wrapper_name](hwnd)
	
	if not isDialog:
		default_wrapper._NeedsImageProp = True

	return default_wrapper
	
	
#====================================================================
class HwndWrapper(object):
	def __init__(self, hwnd):

		# handle if hwnd is actually a HwndWrapper
		try:
			self.handle = hwnd.handle
		except AttributeError:
			self.handle = hwnd
		
		# make it so that ctypes conversion happens correctly
		self._as_parameter_ = self.handle

		# specify whether we need to grab an image of ourselves
		# when asked for properties
		self._NeedsImageProp = False
		
		# set the friendly class name to default to
		# the class name
		self.FriendlyClassName = self.Class
		self._extra_texts = []
		self._extra_clientrects = []
		self._extra_props = {}
				
		self._extra_props['MenuItems'] = self.MenuItems
		
		# if it is a main window
		if self.IsDialog:
			self.FriendlyClassName = "Dialog"
			
		# default to not having a reference control added
		self.ref = None

	Text = property (handleprops.text, doc = "Main text of the control")
	Class = property (handleprops.classname, doc = "Class Name of the window")
	Style = property (handleprops.style, doc = "Style of window")
	ExStyle = property (handleprops.exstyle, doc = "Extended Style of window")
	ControlID = property (handleprops.controlid, doc = "The ID of the window")
	UserData = property (
		handleprops.userdata, doc = "Extra data associted with the window")
	ContextHelpID = property (
		handleprops.contexthelpid, doc = "The Context Help ID of the window")
	IsVisible = property (handleprops.isvisible, doc = "Whether the window is visible or not")
	IsUnicode = property (handleprops.isunicode, doc = "Whether the window is unicode or not")
	IsEnabled = property (handleprops.isenabled, doc = "Whether the window is enabled or not")

	Rectangle = property (handleprops.rectangle, doc = "Rectangle of window")
	ClientRect = property (handleprops.clientrect, doc = "Client rectangle of window")

	Font = property (handleprops.font, doc = "The font of the window")

	ProcessID = property (handleprops.processid, doc = "ID of process that controls this window")

	HasStyle = handleprops.has_style
	HasExStyle = handleprops.has_exstyle

#	#-----------------------------------------------------------
#	def HasStyle(self, Style):
#		return self.Style & Style == Style:
#			
#	#-----------------------------------------------------------
#	def HasExStyle(self, Style):
#		return  self.ExStyle & Style == Style:


	
	#-----------------------------------------------------------
	def get_is_dialog(self):
		if (self.HasStyle(WS_OVERLAPPED) or self.HasStyle(WS_CAPTION)) and not self.HasStyle(WS_CHILD):	
			return True
		else:
			return False
	IsDialog = property (get_is_dialog, doc = "Whether the window is a dialog or not")
	
	#-----------------------------------------------------------
	# define the Menu Property
	def get_menuitems(self):
		if self.IsDialog:
			return GetMenuItems(GetMenu(self))
		else:
			return []
	MenuItems = property (get_menuitems, doc = "Return the menu items for the dialog")
		
	#-----------------------------------------------------------
	def get_parent(self):
		return HwndWrapper(handleprops.parent(self))
	Parent = property (get_parent, doc = "Parent window of window")

	#-----------------------------------------------------------
	def get_texts(self):
		texts = [self.Text, ]
		texts.extend(self._extra_texts)
		return texts
	Texts = property (get_texts, doc = "All text items of the control")

	#-----------------------------------------------------------
	def get_clientrects(self):
		clientrects = [self.ClientRect, ]
		clientrects.extend(self._extra_clientrects)
		return clientrects
	ClientRects = property (
		get_clientrects, doc = "All client rectanbgles of the control")

	#-----------------------------------------------------------
	def get_Fonts(self):
		return [self.Font, ]
	Fonts = property (get_Fonts, doc = "All fonts of the control")

	#-----------------------------------------------------------
	def get_children(self):
	
		# this will be filled in the callback function
		child_windows = handleprops.children(self)
		return [WrapHandle(hwnd) for hwnd in child_windows]
		
	Children = property (get_children, doc = "The list of children")
		
	#-----------------------------------------------------------
	def IsChild(self, parent):
		"Return whether the window is a child of parent."
			
		# Call the IsChild API funciton and convert the result
		# to True/False
		return IsChild(self.handle, parentHwnd) != 0

	#-----------------------------------------------------------
	def SendMessage(self, message, wparam = 0 , lparam = 0):
		return SendMessage(self, message, wparam, lparam)

	#-----------------------------------------------------------
	def PostMessage(self, message, wparam = 0 , lparam = 0):
		return PostMessage(self, message, wparam, lparam)

	#-----------------------------------------------------------
	def NotifyParent(self, message):
		"Send the notification message to parent of this control"
	
		return self.Parent.PostMessage(
			WM_COMMAND,
			MakeLong(self.ControlID, message),
			self)

	#-----------------------------------------------------------	
	def GetProperties(self):
		props = self._extra_props
		
		# get the className
		props['Class'] = self.Class

		# set up the friendlyclass defaulting
		# to the class Name
		props['FriendlyClassName'] = self.FriendlyClassName

		props['Texts'] = self.Texts
		props['Style'] = self.Style
		props['ExStyle'] = self.ExStyle
		props['ControlID'] = self.ControlID
		props['UserData'] = self.UserData
		props['ContextHelpID'] = self.ContextHelpID
		
		props['Fonts'] = self.Fonts
		props['ClientRects'] = self.ClientRects
		
		props['Rectangle'] = self.Rectangle

		props['IsVisible'] =  self.IsVisible
		props['IsUnicode'] =  self.IsUnicode
		props['IsEnabled'] =  self.IsEnabled
		
		#props['MenuItems'] = []

		if self._NeedsImageProp:
			props['Image'] = self.CaptureAsImage()
			
		#return the properties
		return props

	#-----------------------------------------------------------
	def CaptureAsImage(self):
		
		if not (self.Rectangle.width() and self.Rectangle.height()):
			return None

		# get the control rectangle in a way that PIL likes it
		box = (
			self.Rectangle.left, 
			self.Rectangle.top, 
			self.Rectangle.right, 
			self.Rectangle.bottom)

		# grab the image and get raw data as a string
		# wrapped in try because PIL is optional
		try:
			image = PIL.ImageGrab.grab(box)
			return image
		
		# if that fails due to a NameError - it is most likely because
		# PIL was not found - and the package not loaded
		except NameError:
			pass
		

	#-----------------------------------------------------------
	def __eq__(self, other):
		if isinstance(other, HwndWrapper):
			return self.handle == other.handle
		else:
			return self.handle == other




MIIM_STRING = 0x40
#====================================================================
def GetMenuItems(menuHandle):
	
	# If it doesn't have a real menu just return
	if not IsMenu(menuHandle):
		return []

	items = []
		
	itemCount = GetMenuItemCount(menuHandle)

	# for each menu item 
	for i in range(0, itemCount):

		itemProp = {}

		# get the information on the menu Item
		menuInfo  = MENUITEMINFOW()
		menuInfo.cbSize = sizeof (menuInfo)
		menuInfo.fMask = \
			MIIM_CHECKMARKS | \
			MIIM_ID | \
			MIIM_STATE | \
			MIIM_SUBMENU | \
			MIIM_TYPE #| \
			#MIIM_FTYPE #| \
			#MIIM_STRING
			#MIIM_DATA | \


		ret = GetMenuItemInfo (menuHandle, i, True, byref(menuInfo))
		if not ret:
			raise WinError()

		itemProp['State'] = menuInfo.fState
		itemProp['Type'] = menuInfo.fType
		itemProp['ID'] = menuInfo.wID

		# if there is text
		if menuInfo.cch:
			# allocate a buffer
			bufferSize = menuInfo.cch+1
			text = (c_wchar * bufferSize)()

			# update the structure and get the text info
			menuInfo.dwTypeData = addressof(text)
			menuInfo.cch = bufferSize
			GetMenuItemInfo (menuHandle, i, True, byref(menuInfo))
			itemProp['Text'] = text.value
		else:
			itemProp['Text'] = ""

		# if it's a sub menu then get it's items
		if menuInfo.hSubMenu:
			subMenuItems = GetMenuItems(menuInfo.hSubMenu)#, indent)
			itemProp['MenuItems'] = subMenuItems

		items.append(itemProp)
	
	return items


#====================================================================
class dummy_control(dict):
	pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
	# wrap the dialog handle and start a new list for the 
	# controls on the dialog
	try:
		controls = [hwnd, ]
		controls.extend(hwnd.Children)
	except AttributeError:
		
		controls = [WrapHandle(hwnd, True), ]
	
		# add all the children of the dialog
		controls.extend(controls[0].Children)
	
	props = []

	# Add each control to the properties for this dialog
	for ctrl in controls:
		# Get properties for each control and wrap them in 
		# dummy_control so that we can assign handle
		ctrlProps = dummy_control(ctrl.GetProperties())
		
		# assign the handle
		ctrlProps.handle = ctrl.handle
		
		# offset the rectangle from the dialog rectangle
		ctrlProps['Rectangle'] -= controls[0].Rectangle
		
		props.append(ctrlProps)
		
	return props
			

#====================================================================
HwndWrappers = {}


#====================================================================
def Main():

	from findwindows import find_windows

	if len(sys.argv) < 2:
		handle = GetDesktopWindow()
	else:
		try:
			handle = int(eval(sys.argv[1]))
			
		except:
			
			handle = find_windows(title_re = "^" + sys.argv[1], class_name = "#32770")
		
			if not handle:
				print "dialog not found"
				sys.exit()
			

	#pprint(GetDialogPropsFromHandle(handle))
	
	
if __name__ == "__main__":
	Main()

	
	
	