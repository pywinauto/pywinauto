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

"Wraps various standard windows controls"

__revision__ = "$Revision$"

from HwndWrapper import HwndWrapper, _HwndWrappers

import ctypes

from pywinauto import win32defines
from pywinauto import win32structures


#====================================================================
class ButtonWrapper(HwndWrapper):
    "Wrap a windows Button control"
    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ButtonWrapper, self).__init__(hwnd)

        # default to Button for FriendlyClassName
        # might be changed later
        #self.FriendlyClassName = "Button"
        #self._set_FriendlyClassName()

        self._set_if_needs_image()

    #-----------------------------------------------------------
    def _set_if_needs_image(self):
        "Set the _NeedsImageProp attribute if it is an image button"
        if self.IsVisible and (\
            self.HasStyle(win32defines.BS_BITMAP) or \
            self.HasStyle(win32defines.BS_ICON) or \
            self.HasStyle(win32defines.BS_OWNERDRAW)):

            self._NeedsImageProp = True

#	#-----------------------------------------------------------
#	def _set_FriendlyClassName(self):
#
#
#		# get the least significant bit
#		StyleLSB = self.Style & 0xF
#
#		if StyleLSB == BS_3STATE or StyleLSB == BS_AUTO3STATE or \
#			StyleLSB == BS_AUTOCHECKBOX or \
#			StyleLSB == BS_CHECKBOX:
#			self.FriendlyClassName = "CheckBox"
#
#		elif StyleLSB == BS_RADIOBUTTON or StyleLSB == BS_AUTORADIOBUTTON:
#			self.FriendlyClassName = "RadioButton"
#
#		elif StyleLSB ==  BS_GROUPBOX:
#			self.FriendlyClassName = "GroupBox"
#
#		if self.Style & BS_PUSHLIKE:
#			self.FriendlyClassName = "Button"


#====================================================================
def _get_multiple_text_items(wrapper, count_msg, item_len_msg, item_get_msg):
    "Helper function to get multiple text items from a control"

    texts = []

    # find out how many text items are in the combobox
    num_items = wrapper.SendMessage(count_msg)

    # get the text for each item in the combobox
    for i in range(0, num_items):
        text_len = wrapper.SendMessage (item_len_msg, i, 0)

        text = ctypes.create_unicode_buffer(text_len + 1)

        wrapper.SendMessage (item_get_msg, i, ctypes.byref(text))

        texts.append(text.value)

    return texts


#====================================================================
class ComboBoxWrapper(HwndWrapper):
    "Wrap a windows ComboBox control"
    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ComboBoxWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "ComboBox"

        self._extra_texts = self.ItemTexts()
        self._extra_props['DroppedRect'] = self._get_droppedrect()

    #-----------------------------------------------------------
    def SelectedIndex(self):
        "Return the selected index"
        return self.SendMessage(win32defines.CB_GETCURSEL)

    #-----------------------------------------------------------
    def _get_droppedrect(self):
        "Get the dropped rectangle of the combobox"
        droppedRect = win32structures.RECT()

        self.SendMessage(
            win32defines.CB_GETDROPPEDCONTROLRECT,
            0,
            ctypes.byref(droppedRect))

        # we need to offset the dropped rect from the control
        droppedRect -= self.Rectangle

        return droppedRect
    DroppedRect = property(_get_droppedrect, doc =
        "The dropped rectangle of the combobox")

    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the combobox"
        return self.SendMessage(win32defines.CB_GETCOUNT)

    #-----------------------------------------------------------
    def ItemData(self, i):
        "Returns the item data associated with the item if any"
        return self.SendMessage(win32defines.CB_GETITEMDATA, i)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text of the items of the combobox"
        return _get_multiple_text_items(
            self,
            win32defines.CB_GETCOUNT,
            win32defines.CB_GETLBTEXTLEN,
            win32defines.CB_GETLBTEXT)

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = HwndWrapper.GetProperties(self)

        # get selected item
        props['SelectedItem'] = self.SelectedIndex()

        props['DroppedRect'] = self.DroppedRect

        props['ItemData'] = []
        for i in range(self.ItemCount()):
            props['ItemData'].append(self.ItemData(i))

        return props



#====================================================================
class ListBoxWrapper(HwndWrapper):
    "Wrap a windows ListBox control"
    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ListBoxWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "ListBox"

        self._extra_texts = self.ItemTexts()


    #-----------------------------------------------------------
    def SelectedIndices(self):
        "The currently selected indices of the listbox"
        num_selected = self.SendMessage(win32defines.LB_GETSELCOUNT)

        if num_selected != win32defines.LB_ERR:
            items = (ctypes.c_int * num_selected)()

            self.SendMessage(
                win32defines.LB_GETSELITEMS, num_selected, ctypes.byref(items))

        else:
            items = [self.SendMessage(win32defines.LB_GETCURSEL)]

        return items


    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the ListBox"
        return self.SendMessage(win32defines.LB_GETCOUNT)

    #-----------------------------------------------------------
    def ItemData(self, i):
        "Return the ItemData if any associted with the item"
        return self.SendMessage(win32defines.LB_GETITEMDATA, i)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text items of the control"
        return _get_multiple_text_items(
            self,
            win32defines.LB_GETCOUNT,
            win32defines.LB_GETTEXTLEN,
            win32defines.LB_GETTEXT)

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties as a dictionary for the control"
        props = HwndWrapper.GetProperties(self)

        # get selected item
        props['SelectedItems'] = self.SelectedIndices()

        props['ItemData'] = []
        for i in range(self.ItemCount()):
            props['ItemData'].append(self.ItemData(i))

        return props



#====================================================================
class EditWrapper(HwndWrapper):
    "Wrap a windows Edit control"
    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(EditWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "Edit"

        # find out how many text items are in the combobox
        numItems = self.SendMessage(win32defines.EM_GETLINECOUNT)


        # TODO: Move this to a method of EditWrapper!
        # get the text for each item in the combobox
        for i in range(0, numItems):
            textLen = self.SendMessage (win32defines.EM_LINELENGTH, i, 0)

            text = ctypes.create_unicode_buffer(textLen+1)

            # set the length - which is required
            text[0] = unichr(textLen)

            self.SendMessage (win32defines.EM_GETLINE, i, ctypes.byref(text))

            self._extra_texts.append(text.value)

        self._extra_texts = ["\n".join(self._extra_texts), ]

        # get selected item
        self._extra_props['SelectionIndices'] = self._get_selectionindices()

    #-----------------------------------------------------------
    def _get_selectionindices(self):
        "Return the indices of the selection"
        start = ctypes.c_int()
        end = ctypes.c_int()
        self.SendMessage(
            win32defines.EM_GETSEL, ctypes.byref(start), ctypes.byref(end))

        return (start.value, end.value)
    SelectionIndices = property(
        _get_selectionindices,
        doc = "The start and end indices of the current selection")




#====================================================================
class StaticWrapper(HwndWrapper):
    "Wrap a windows Static control"
    def __init__(self, hwnd):
        "Initialize the control"
        super(StaticWrapper, self).__init__(hwnd)

        # if the control is visible - and it shows an image
        if self.IsVisible and (
            self.HasStyle(win32defines.SS_ICON) or \
            self.HasStyle(win32defines.SS_BITMAP) or \
            self.HasStyle(win32defines.SS_CENTERIMAGE) or \
            self.HasStyle(win32defines.SS_OWNERDRAW)):

            self._NeedsImageProp = True



# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class DialogWrapper(HwndWrapper):
    "Wrap a dialog"
    pass


#====================================================================
_HwndWrappers["ComboBox"] = ComboBoxWrapper
_HwndWrappers[r"WindowsForms\d*\.COMBOBOX\..*"] =  ComboBoxWrapper
_HwndWrappers["TComboBox"] = ComboBoxWrapper

_HwndWrappers["ListBox"] =  ListBoxWrapper
_HwndWrappers[r"WindowsForms\d*\.LISTBOX\..*"] =  ListBoxWrapper
_HwndWrappers["TListBox"] =  ListBoxWrapper

_HwndWrappers["Button"] =  ButtonWrapper
_HwndWrappers[r"WindowsForms\d*\.BUTTON\..*"] =  ButtonWrapper
_HwndWrappers["TButton"] =  ButtonWrapper
#_HwndWrappers["TCheckBox"] =  ButtonWrapper
#_HwndWrappers["TRadioButton"] =  ButtonWrapper

_HwndWrappers["Static"] =  StaticWrapper
_HwndWrappers["TPanel"] =  StaticWrapper

_HwndWrappers["Edit"] =  EditWrapper
_HwndWrappers["TEdit"] =  EditWrapper
_HwndWrappers["TMemo"] =  EditWrapper


_HwndWrappers["#32770"] =  DialogWrapper



#
#               'CheckBox': PCheckBox,
#               'TCheckBox': PCheckBox,
#