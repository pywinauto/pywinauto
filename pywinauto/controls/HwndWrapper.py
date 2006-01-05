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
import PIL.ImageGrab
from ctypes import * 

from win32defines import *
from win32functions import *
from win32structures import *


#====================================================================
def WrapHandle(hwnd, isDialog = False):

	default_wrapper = HwndWrapper(hwnd)
	
	for wrapper_name in HwndWrappers:
		if re.search(wrapper_name, default_wrapper.Class):
			return HwndWrappers[wrapper_name](hwnd)
	
	default_wrapper._NeedsImageProp = True

	return default_wrapper
	
	
#====================================================================
class HwndWrapper(object):
	def __init__(self, hwnd):

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
	def get_text(self):
		# Had to use GetWindowText and GetWindowTextLength rather than
		# using WM_GETTEXT as we want it to fail for controls that dont
		# have 'usable' first text e.g. Edit controls and Comboboxes.		
		
		length = GetWindowTextLength(self.handle,)

		text = ''
		if length:
			length += 1

			buffer = (c_wchar * length)()

			ret =  GetWindowText(self, byref(buffer), length)
			
			if ret:
				text = buffer.value
		
		return text
		
		
#		
#		
#		
#		# get the number of characters required
#		bufferSize = self.SendMessage (WM_GETTEXTLENGTH)
#		
#		text = ''
#		# allocate the buffer size
#		if bufferSize:
#			bufferSize += 1
#			# allocate the buffer
#			title = (c_wchar * bufferSize)()
#			
#			# retrieve the text
#			self.SendMessage (WM_GETTEXT, bufferSize, title)
#			
#			# get the unicode object from the ctypes instance
#			text = title.value
#		
#		return text
	Text = property (get_text, doc = "Main text of the control")

	#-----------------------------------------------------------
	def get_texts(self):
		texts = [self.Text, ]
		texts.extend(self._extra_texts)
		return texts
	Texts = property (get_texts, doc = "All text items of the control")
	
	#-----------------------------------------------------------
	def get_Class(self):
		# get the className
		className = (c_wchar * 257)()
		GetClassName (self, byref(className), 256)
		return className.value
	Class = property (get_Class, doc = "Class Name of the window")

	#-----------------------------------------------------------
	def get_parent(self):
		return HwndWrapper(GetParent(self))
	Parent = property (get_parent, doc = "Parent window of window")
		
	#-----------------------------------------------------------
	def get_Style(self):
		return GetWindowLong (self, GWL_STYLE)
	Style = property (get_Style, doc = "Style of window")
	
	#-----------------------------------------------------------
	def get_ExStyle(self):
		return GetWindowLong (self.handle, GWL_EXSTYLE)
	ExStyle = property (get_ExStyle, doc = "Extended Style of window")
	
	#-----------------------------------------------------------
	def get_ControlID(self):
		return GetWindowLong (self.handle, GWL_ID)
	ControlID = property (get_ControlID, doc = "The ID of the window")
	
	#-----------------------------------------------------------
	def get_userdata(self):
		return GetWindowLong (self.handle, GWL_USERDATA)	
	UserData = property (
		get_userdata, doc = "Extra data associted with the window")
	
	#-----------------------------------------------------------
	def get_ContextHelpID(self):
		return GetWindowContextHelpId (self.handle)	
	ContextHelpID = property (
		get_ContextHelpID, doc = "The Context Help ID of the window")
	
	#-----------------------------------------------------------
	def get_IsVisible(self):
		return IsWindowVisible(self.handle)
	IsVisible = property (get_IsVisible, doc = "Whether the window is visible or not")
	
	#-----------------------------------------------------------
	def get_IsUnicode(self):
		return IsWindowUnicode(self.handle)
	IsUnicode = property (get_IsUnicode, doc = "Whether the window is unicode or not")
	
	#-----------------------------------------------------------
	def get_isenabled(self):
		return IsWindowEnabled(self.handle)
	IsEnabled = property (get_isenabled, doc = "Whether the window is enabled or not")
	
	#-----------------------------------------------------------
	def get_clientrect(self):
		"Returns the client rectangle of the control"
		clientRect = RECT()
		GetClientRect(self.handle, byref(clientRect))
		return clientRect
	ClientRect = property (get_clientrect, doc = "ClientRect of window")

	#-----------------------------------------------------------
	def get_clientrects(self):
		clientrects = [self.ClientRect, ]
		clientrects.extend(self._extra_clientrects)
		return clientrects
	ClientRects = property (
		get_clientrects, doc = "All client rectanbgles of the control")
	
	#-----------------------------------------------------------
	def get_rectangle(self):
		# get the full rectangle		
		rect = RECT()
		GetWindowRect(self.handle, byref(rect))
		return rect
	Rectangle = property (get_rectangle, doc = "Rectangle of window")

	#-----------------------------------------------------------
	def get_children(self):
	
		# this will be filled in the callback function
		childWindows = []
		
		# callback function for EnumChildWindows
		def enumChildProc(hWnd, LPARAM):
			win = WrapHandle(hWnd)
			
			# append it to our list
			childWindows.append(win)
			
			# return true to keep going
			return True
	
		# define the child proc type
		EnumChildProc = WINFUNCTYPE(c_int, HWND, LPARAM)	
		proc = EnumChildProc(enumChildProc)
		
		# loop over all the children (callback called for each)
		EnumChildWindows(self.handle, proc, 0)
		
		return childWindows
	Children = property (get_children, doc = "The list of children")

	#-----------------------------------------------------------
	def get_Font(self):
		# set the font
		fontHandle = self.SendMessage (WM_GETFONT)
	
		# if the fondUsed is 0 then the control is using the 
		# system font
		if not fontHandle:
			fontHandle = GetStockObject(SYSTEM_FONT);
	
		# Get the Logfont structure of the font of the control
		font = LOGFONTW()
		ret = GetObject(fontHandle, sizeof(font), byref(font))
	
		# The function could not get the font - this is probably 
		# because the control does not have associated Font/Text
		# So we should make sure the elements of the font are zeroed.
		if not ret:
			font = LOGFONTW()
	
		# if it is a main window
		if (self.HasStyle(WS_OVERLAPPED) or self.HasStyle(WS_CAPTION)) and not self.HasStyle(WS_CHILD):

			if "MS Shell Dlg" in font.lfFaceName or font.lfFaceName == "System":
				# these are not usually the fonts actaully used in for 
				# title bars so we need to get the default title bar font

				# get the title font based on the system metrics rather 
				# than the font of the control itself
				SPI_GETNONCLIENTMETRICS = 41 # set the message number
				ncms = NONCLIENTMETRICSW()
				ncms.cbSize = sizeof(ncms)
				SystemParametersInfo(
					SPI_GETNONCLIENTMETRICS, 
					sizeof(ncms), 
					byref(ncms),
					0)

				# with either of the following 2 flags set the font of the 
				# dialog isthe small one (but there is normally no difference!
				if self.HasStyle(WS_EX_TOOLWINDOW) or \
				   self.HasStyle(WS_EX_PALETTEWINDOW):

					font = ncms.lfSmCaptionFont
				else:
					font = ncms.lfCaptionFont
	
		return font
	Font = property (get_Font, doc = "The font of the window")

	#-----------------------------------------------------------
	def get_Fonts(self):
		return [self.Font, ]
	Fonts = property (get_Fonts, doc = "All fonts of the control")
	
	#-----------------------------------------------------------
	def IsChild(self, parent):
		"Return whether the window is a child of parent."
			
		# Call the IsChild API funciton and convert the result
		# to True/False
		return IsChild(self.handle, parentHwnd) != 0

	#-----------------------------------------------------------
	def HasStyle(self, Style):
		if self.Style & Style == Style:
			return True
		else:
			return False
			
	#-----------------------------------------------------------
	def HasExStyle(self, Style):
		if self.ExStyle & Style == Style:
			return True
		else:
			return False
			
	#-----------------------------------------------------------
	def SendMessage(self, message, wparam = 0 , lparam = 0):
		return SendMessage(self.handle, message, wparam, lparam)

	#-----------------------------------------------------------
	def PostMessage(self, message, wparam = 0 , lparam = 0):
		return PostMessage(self.handle, message, wparam, lparam)
	
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
		image = PIL.ImageGrab.grab(box)
		
		return image

	#-----------------------------------------------------------
	def __eq__(self, other):
		if isinstance(other, HwndWrapper):
			return self.handle == other.handle
		else:
			return self.handle == other
		
	#-----------------------------------------------------------
	def get_process_id(self):
		"ID of process that controls this window"
		process_id = c_int()
		GetWindowThreadProcessId(self, byref(process_id))	
		
		return process_id.value
	ProcessID = property (get_process_id, doc = get_process_id.__doc__)




#====================================================================
def GetMenuItems(menuHandle):#, indent = ""):
	
	# If it doesn't have a real menu just return
	if not IsMenu(menuHandle):
		return []

	items = []
		
	itemCount = GetMenuItemCount(menuHandle)

	# for each menu item 
	for i in range(0, itemCount):

		itemProp = {} #Controls_Standard.ControlProps()

		# get the information on the menu Item
		menuInfo  = MENUITEMINFOW()
		menuInfo.cbSize = sizeof (menuInfo)
		menuInfo.fMask = \
			MIIM_CHECKMARKS | \
			MIIM_ID | \
			MIIM_STATE | \
			MIIM_SUBMENU | \
			MIIM_TYPE
			#MIIM_FTYPE | \
			#MIIM_STRING
			#MIIM_DATA | \


		ret = GetMenuItemInfo (menuHandle, i, True, byref(menuInfo))
		if not ret:
			raise WinError()

		itemProp['State'] = menuInfo.fState
		itemProp['Type'] = menuInfo.fType
		itemProp['ID'] = menuInfo.wID
		#itemProp.handle = menuHandle



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
			#indent += "  "
			subMenuItems = GetMenuItems(menuInfo.hSubMenu)#, indent)
			itemProp['MenuItems'] = subMenuItems
			#indent = indent[1:-2]

		items.append(itemProp)
	

	return items


#====================================================================
class dummy_control(dict):
	pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
	# wrap the dialog handle and start a new list for the 
	# controls on the dialog
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

	
	
	