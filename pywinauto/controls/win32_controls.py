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

from HwndWrapper import HwndWrapper, HwndWrappers

from ctypes import * 

from pywinauto.win32defines import *
from pywinauto.win32functions import *
from pywinauto.win32structures import *


#====================================================================
class ButtonWrapper(HwndWrapper):
	#-----------------------------------------------------------
	def __init__(self, hwnd):
		super(ButtonWrapper, self).__init__(hwnd)

		# default to Button for FriendlyClassName				
		self.FriendlyClassName = "Button"
		self._set_FriendlyClassName()
		
		self._set_if_needs_image()
	
	#-----------------------------------------------------------
	def _set_if_needs_image(self):
		
		if self.IsVisible and (\
			self.HasStyle(BS_BITMAP) or \
			self.HasStyle(BS_ICON) or \
			self.HasStyle(BS_OWNERDRAW)):

			self._NeedsImageProp = True
						
	#-----------------------------------------------------------
	def _set_FriendlyClassName(self):

	
		# get the least significant bit
		StyleLSB = self.Style & 0xF

		if StyleLSB == BS_3STATE or StyleLSB == BS_AUTO3STATE or \
			StyleLSB == BS_AUTOCHECKBOX or \
			StyleLSB == BS_CHECKBOX:
			self.FriendlyClassName = "CheckBox"

		elif StyleLSB == BS_RADIOBUTTON or StyleLSB == BS_AUTORADIOBUTTON:
			self.FriendlyClassName = "RadioButton"

		elif StyleLSB ==  BS_GROUPBOX:
			self.FriendlyClassName = "GroupBox"

		if self.Style & BS_PUSHLIKE:
			self.FriendlyClassName = "Button"


#====================================================================
def get_multiple_text_items(wrapper, count_msg, item_len_msg, item_get_msg):
	texts = []

	# find out how many text items are in the combobox		
	numItems = wrapper.SendMessage(count_msg)

	# get the text for each item in the combobox
	for i in range(0, numItems):
		textLen = wrapper.SendMessage (item_len_msg, i, 0)

		text = create_unicode_buffer(textLen+1)

		wrapper.SendMessage (item_get_msg, i, byref(text))

		texts.append(text.value)

	return texts
	

#====================================================================
class ComboBoxWrapper(HwndWrapper):
	#-----------------------------------------------------------
	def __init__(self, hwnd):
		super(ComboBoxWrapper, self).__init__(hwnd)
		
		# default to ComboBox for FriendlyClassName				
		self.FriendlyClassName = "ComboBox"
		
		self._extra_texts = get_multiple_text_items(self, CB_GETCOUNT, CB_GETLBTEXTLEN, CB_GETLBTEXT)
		self._extra_props['DroppedRect'] = self.get_droppedrect()

		# get selected item
		self._extra_props['SelectedItem'] = self.get_selected_index()
	
	#-----------------------------------------------------------
	def get_selected_index(self):
		return self.SendMessage(CB_GETCURSEL)
	CurrentlySelected = property(get_selected_index, doc = "The currently selected index of the combobox")
		
	#-----------------------------------------------------------
	def get_droppedrect(self):

		droppedRect = RECT()

		self.SendMessage(
			CB_GETDROPPEDCONTROLRECT, 
			0, 
			byref(droppedRect))

		# we need to offset the dropped rect from the control
		droppedRect -= self.Rectangle
		
		return droppedRect
	DroppedRect = property(get_droppedrect, doc = "The dropped rectangle of the combobox")
	

#====================================================================
class ListBoxWrapper(HwndWrapper):
	#-----------------------------------------------------------
	def __init__(self, hwnd):
		super(ListBoxWrapper, self).__init__(hwnd)

		# default to LisBox for FriendlyClassName				
		self.FriendlyClassName = "ListBox"
		
		self._extra_texts = get_multiple_text_items(self, LB_GETCOUNT, LB_GETTEXTLEN, LB_GETTEXT)

		# get selected item
		self._extra_props['SelectedItem'] = self.get_selected_index()
	
	#-----------------------------------------------------------
	def get_selected_index(self):
		return self.SendMessage(LB_GETCURSEL)
	CurrentlySelected = property(get_selected_index, doc = "The currently selected index of the listbox")
		

#====================================================================
class EditWrapper(HwndWrapper):
	#-----------------------------------------------------------
	def __init__(self, hwnd):
		super(EditWrapper, self).__init__(hwnd)

		# default to Edit for FriendlyClassName				
		self.FriendlyClassName = "Edit"
		
		# find out how many text items are in the combobox		
		numItems = self.SendMessage(EM_GETLINECOUNT)

		# get the text for each item in the combobox
		for i in range(0, numItems):
			textLen = self.SendMessage (EM_LINELENGTH, i, 0)

			text = create_unicode_buffer(textLen+1)
			
			# set the length - which is required
			text[0] = unichr(textLen)

			self.SendMessage (EM_GETLINE, i, byref(text))

			self._extra_texts.append(text.value)
		
		self._extra_texts = ["\n".join(self._extra_texts), ]
		
		# get selected item
		self._extra_props['SelectionIndices'] = self.get_selectionindices()	
		
	#-----------------------------------------------------------
	def get_selectionindices(self):
		start = c_int()
		end = c_int()
		self.SendMessage(EM_GETSEL, byref(start), byref(end))
		
		return (start.value, end.value)
	SelectionIndices = property(get_selectionindices, doc = "The start and end indices of the current selection")



#====================================================================
class StaticWrapper(HwndWrapper):
	def __init__(self, hwnd):
		super(StaticWrapper, self).__init__(hwnd)

		# default to Edit for FriendlyClassName				
		self.FriendlyClassName = "Static"
		
		# if the control is visible - and it shows an image
		if self.IsVisible and (
			self.HasStyle(SS_ICON) or \
			self.HasStyle(SS_BITMAP) or \
			self.HasStyle(SS_CENTERIMAGE) or \
			self.HasStyle(SS_OWNERDRAW)):

			self._NeedsImageProp = True
							


# the main reason for this is just to make sure that 
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class DialogWrapper(HwndWrapper):
	pass


#====================================================================
HwndWrappers["ComboBox"] = ComboBoxWrapper
HwndWrappers[r"WindowsForms\d*\.COMBOBOX\..*"] =  ComboBoxWrapper
HwndWrappers["TComboBox"] = ComboBoxWrapper

HwndWrappers["ListBox"] =  ListBoxWrapper
HwndWrappers[r"WindowsForms\d*\.LISTBOX\..*"] =  ListBoxWrapper
HwndWrappers["TListBox"] =  ListBoxWrapper

HwndWrappers["Button"] =  ButtonWrapper
HwndWrappers[r"WindowsForms\d*\.BUTTON\..*"] =  ButtonWrapper
HwndWrappers["TButton"] =  ButtonWrapper
#HwndWrappers["TCheckBox"] =  ButtonWrapper
#HwndWrappers["TRadioButton"] =  ButtonWrapper

HwndWrappers["Static"] =  StaticWrapper
HwndWrappers["TPanel"] =  StaticWrapper

HwndWrappers["Edit"] =  EditWrapper
HwndWrappers["TEdit"] =  EditWrapper
HwndWrappers["TMemo"] =  EditWrapper


HwndWrappers["#32770"] =  DialogWrapper



#
#               'CheckBox': PCheckBox,
#               'TCheckBox': PCheckBox,
#               