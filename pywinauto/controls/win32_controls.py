# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2009 Mark Mc Mahon
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

"""Wraps various standard windows controls
"""
from __future__ import unicode_literals

import time
import ctypes
import win32gui
import locale

from . import HwndWrapper

from .. import sysinfo
from .. import six
from .. import win32functions
from .. import win32defines
from .. import win32structures
from .. import controlproperties

from ..timings import Timings

if sysinfo.UIA_support:
    from ..UIAElementInfo import _UIA_dll

#====================================================================
class ButtonWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Button control"

    friendlyclassname = "Button"
    windowclasses = [
        "Button",
        ".*Button",
        r"WindowsForms\d*\.BUTTON\..*",
        ".*CheckBox", ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_ButtonControlTypeId,
            _UIA_dll.UIA_CheckBoxControlTypeId,
            _UIA_dll.UIA_RadioButtonControlTypeId]
    can_be_label = True

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ButtonWrapper, self).__init__(hwnd)

        #self._set_if_needs_image()

    @property
    def _NeedsImageProp(self):

        """_NeedsImageProp=True if it is an image button"""

        # optimization call Style once and work with that rather than
        # calling HasStyle a number of times
        style = self.Style()

        if self.is_visible() and (style & win32defines.BS_BITMAP or
                                  style & win32defines.BS_ICON or
                                  style & win32defines.BS_OWNERDRAW):
            return True
        else:
            return False

    #-----------------------------------------------------------
    def friendly_class_name(self):
        """Return the friendly class name of the button

        Windows controls with the class "Button" can look like different
        controls based on their style. They can look like the following
        controls:

          - Buttons, this method returns "Button"
          - CheckBoxes, this method returns "CheckBox"
          - RadioButtons, this method returns "RadioButton"
          - GroupBoxes, this method returns "GroupBox"

        """
        # get the least significant BIT
        style_lsb = self.Style() & 0xF

        f_class_name = 'Button'


        vb_buttons = {
            "ThunderOptionButton": "RadioButton",
            "ThunderCheckBox": "CheckBox",
            "ThunderCommandButton": "Button"
        }

        if self.class_name() in vb_buttons:
            f_class_name = vb_buttons[self.class_name()]

        if style_lsb == win32defines.BS_3STATE or \
            style_lsb == win32defines.BS_AUTO3STATE or \
            style_lsb == win32defines.BS_AUTOCHECKBOX or \
            style_lsb == win32defines.BS_CHECKBOX:
            f_class_name = "CheckBox"
        elif style_lsb == win32defines.BS_RADIOBUTTON or \
            style_lsb == win32defines.BS_AUTORADIOBUTTON:
            f_class_name = "RadioButton"
        elif style_lsb ==  win32defines.BS_GROUPBOX:
            f_class_name = "GroupBox"

        if self.Style() & win32defines.BS_PUSHLIKE:
            f_class_name = "Button"

        return f_class_name


    #-----------------------------------------------------------
    def GetCheckState(self):
        """Return the check state of the checkbox

        The check state is represented by an integer
        0 - unchecked
        1 - checked
        2 - indeterminate

        The following constants are defined in the win32defines module
        BST_UNCHECKED = 0
        BST_CHECKED = 1
        BST_INDETERMINATE = 2
        """
        return self.SendMessage(win32defines.BM_GETCHECK)

    #-----------------------------------------------------------
    def Check(self):
        "Check a checkbox"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_CHECKED)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self


    #-----------------------------------------------------------
    def UnCheck(self):
        "Uncheck a checkbox"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_UNCHECKED)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    def SetCheckIndeterminate(self):
        "Set the checkbox to indeterminate"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_INDETERMINATE)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    def is_dialog(self):
        "Buttons are never dialogs so return False"
        return False

    #-----------------------------------------------------------
    def Click(self, *args, **kwargs):
        "Click the Button control"
    #    import win32functions
    #    win32functions.WaitGuiThreadIdle(self)
    #    self.NotifyParent(win32defines.BN_CLICKED)
        HwndWrapper.HwndWrapper.Click(self, *args, **kwargs)
    #    win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_button_click_wait)

    #-----------------------------------------------------------
    def CheckByClick(self):
        "Check the CheckBox control by Click() method"
        if self.GetCheckState() != win32defines.BST_CHECKED:
            self.Click()

    #-----------------------------------------------------------
    def UncheckByClick(self):
        "Uncheck the CheckBox control by Click() method"
        if self.GetCheckState() != win32defines.BST_UNCHECKED:
            self.Click()

    #-----------------------------------------------------------
    def CheckByClickInput(self):
        "Check the CheckBox control by click_input() method"
        if self.GetCheckState() != win32defines.BST_CHECKED:
            self.click_input()

    #-----------------------------------------------------------
    def UncheckByClickInput(self):
        "Uncheck the CheckBox control by click_input() method"
        if self.GetCheckState() != win32defines.BST_UNCHECKED:
            self.click_input()

#====================================================================
def _get_multiple_text_items(wrapper, count_msg, item_len_msg, item_get_msg):
    "Helper function to get multiple text items from a control"

    texts = []

    # find out how many text items are in the combobox
    num_items = wrapper.SendMessage(count_msg)

    # get the text for each item in the combobox
    for i in range(0, num_items):
        text_len = wrapper.SendMessage (item_len_msg, i, 0)

        if six.PY3:
            text = ctypes.create_unicode_buffer(text_len + 1)
        else:
            text = ctypes.create_string_buffer(text_len + 1)

        wrapper.SendMessage(item_get_msg, i, ctypes.byref(text))

        if six.PY3:
            texts.append(text.value.replace('\u200e', ''))
        else:
            texts.append(text.value.decode(locale.getpreferredencoding(), 'ignore').replace('?', ''))

    return texts


#====================================================================
class ComboBoxWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows ComboBox control"

    friendlyclassname = "ComboBox"
    windowclasses = [
        "ComboBox",
        "WindowsForms\d*\.COMBOBOX\..*",
        ".*ComboBox", ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_ComboBoxControlTypeId]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ComboBoxWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            "SelectedIndex",
            "DroppedRect",
            ])

    #-----------------------------------------------------------
    def DroppedRect(self):
        "Get the dropped rectangle of the combobox"
        dropped_rect = win32structures.RECT()

        self.SendMessage(
            win32defines.CB_GETDROPPEDCONTROLRECT,
            0,
            ctypes.byref(dropped_rect))

        # we need to offset the dropped rect from the control
        dropped_rect -= self.rectangle()

        return dropped_rect

    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the combobox"
        return self.SendMessage(win32defines.CB_GETCOUNT)

    #-----------------------------------------------------------
    def SelectedIndex(self):
        "Return the selected index"
        return self.SendMessage(win32defines.CB_GETCURSEL)

    #-----------------------------------------------------------
    def SelectedText(self):
        "Return the selected text"
        return self.ItemTexts()[self.SelectedIndex()]

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        "Get the index for the item with this 'ident'"
        if isinstance(ident, six.integer_types):

            if ident >= self.ItemCount():
                raise IndexError(
                    "Combobox has %d items, you requested item %d (0 based)"%
                        (self.ItemCount(),
                        ident))

            # negative index
            if ident < 0:
                # convert it to a positive index
                ident = (self.ItemCount() + ident)

        elif isinstance(ident, six.string_types):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.ItemTexts().index(ident)

        return ident

    #-----------------------------------------------------------
    def ItemData(self, item):
        "Returns the item data associated with the item if any"
        index = self._get_item_index(item)
        return self.SendMessage(win32defines.CB_GETITEMDATA, index)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text of the items of the combobox"
        return _get_multiple_text_items(
            self,
            win32defines.CB_GETCOUNT,
            win32defines.CB_GETLBTEXTLEN,
            win32defines.CB_GETLBTEXT)

    #-----------------------------------------------------------
    def texts(self):
        "Return the text of the items in the combobox"
        texts = [self.window_text()]
        texts.extend(self.ItemTexts())
        return texts

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = HwndWrapper.HwndWrapper.GetProperties(self)

        #props['ItemData'] = []
        #for i in range(self.ItemCount()):
        #    props['ItemData'].append(self.ItemData(i))

        return props

    #-----------------------------------------------------------
    def Select(self, item):
        """Select the ComboBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        self.verify_actionable()

        index = self._get_item_index(item)

        # change the selected item
        self.SendMessageTimeout(win32defines.CB_SETCURSEL, index, timeout=0.05)

        # Notify the parent that we are finished selecting
        self.NotifyParent(win32defines.CBN_SELENDOK)

        # Notify the parent that we have changed
        self.NotifyParent(win32defines.CBN_SELCHANGE)

        # simple combo boxes don't have drop downs so they do not recieve
        # this notification
        if self.HasStyle(win32defines.CBS_DROPDOWN):
            # Notify the parent that the drop down has closed
            self.NotifyParent(win32defines.CBN_CLOSEUP)


        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_comboboxselect_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    #def Deselect(self, item):
    # Not implemented because it doesn't make sense for combo boxes.

    #TODO def EditControl(self): # return the edit control of the Combobox

    #TODO def ListControl(self): # return the list control of the combobox

    #TODO def ItemText(self, index):  # get the test of item XX?

    #TODO def EditText(self):  # or should this be self.EditControl.Text()?


#====================================================================
class ListBoxWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows ListBox control"

    friendlyclassname = "ListBox"
    windowclasses = [
        "ListBox",
        r"WindowsForms\d*\.LISTBOX\..*",
        ".*ListBox", ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_ListControlTypeId]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ListBoxWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            "SelectedIndices"])

    #-----------------------------------------------------------
    def IsSingleSelection(self):
        """Check whether the listbox has single selection mode."""
        num_selected = self.SendMessage(win32defines.LB_GETSELCOUNT)

        # if we got LB_ERR then it is a single selection list box
        return (num_selected == win32defines.LB_ERR)

    #-----------------------------------------------------------
    def SelectedIndices(self):
        "The currently selected indices of the listbox"
        num_selected = self.SendMessage(win32defines.LB_GETSELCOUNT)

        # if we got LB_ERR then it is a single selection list box
        if num_selected == win32defines.LB_ERR:
            items = tuple([self.SendMessage(win32defines.LB_GETCURSEL)])

        # otherwise it is a multiselection list box
        else:
            items = (ctypes.c_int * num_selected)()

            self.SendMessage(
                win32defines.LB_GETSELITEMS, num_selected, ctypes.byref(items))

            # Need to convert from Ctypes array to a python tuple
            items = tuple(items)

        return items

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        "Return the index of the item 'ident'"
        if isinstance(ident, six.integer_types):

            if ident >= self.ItemCount():
                raise IndexError(
                    "ListBox has %d items, you requested item %d (0 based)"%
                        (self.ItemCount(),
                        ident))

            # negative index
            if ident < 0:
                ident = (self.ItemCount() + ident)

        elif isinstance(ident, six.string_types):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.ItemTexts().index(ident) #-1

        return ident

    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the ListBox"
        return self.SendMessage(win32defines.LB_GETCOUNT)

    #-----------------------------------------------------------
    def ItemData(self, i):
        "Return the ItemData if any associted with the item"

        index = self._get_item_index(i)

        return self.SendMessage(win32defines.LB_GETITEMDATA, index)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text of the items of the listbox"
        return _get_multiple_text_items(
            self,
            win32defines.LB_GETCOUNT,
            win32defines.LB_GETTEXTLEN,
            win32defines.LB_GETTEXT)

    #-----------------------------------------------------------
    def ItemRect(self, item):
        "Return the rect of the item "
        index = self._get_item_index(item)
        rect = win32structures.RECT()
        res = self.SendMessage(win32defines.LB_GETITEMRECT, index, ctypes.byref(rect))
        if res == win32defines.LB_ERR:
            raise RuntimeError("LB_GETITEMRECT failed")
        return rect

    #-----------------------------------------------------------
    def texts(self):
        "Return the texts of the control"
        texts = [self.window_text()]
        texts.extend(self.ItemTexts())
        return texts

#    #-----------------------------------------------------------
#    def GetProperties(self):
#        "Return the properties as a dictionary for the control"
#        props = HwndWrapper.HwndWrapper.GetProperties(self)
#
#        props['ItemData'] = []
#        for i in range(self.ItemCount()):
#            props['ItemData'].append(self.ItemData(i))
#
#        return props

    #-----------------------------------------------------------
    def Select(self, item, select=True):
        """Select the ListBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """

        if self.IsSingleSelection() and isinstance(item, (list, tuple)) and len(item) > 1:
            raise Exception('Cannot set multiple selection for single-selection listbox!')

        if isinstance(item, (list, tuple)):
            for i in item:
                if i is not None:
                    self.Select(i, select)
            return self

        self.verify_actionable()

        # Make sure we have an index  so if passed in a
        # string then find which item it is
        index = self._get_item_index(item)

        if self.IsSingleSelection():
            # change the selected item
            self.SendMessageTimeout(win32defines.LB_SETCURSEL, index)
        else:
            if select:
                # add the item to selection
                self.SendMessageTimeout(win32defines.LB_SETSEL, win32defines.TRUE, index)
            else:
                # remove the item from selection
                self.SendMessageTimeout(win32defines.LB_SETSEL, win32defines.FALSE, index)

        # Notify the parent that we have changed
        self.NotifyParent(win32defines.LBN_SELCHANGE)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listboxselect_wait)

        return self

    #-----------------------------------------------------------
    def SetItemFocus(self, item):
        "Set the ListBox focus to the item at index"

        index = self._get_item_index(item)

        # if it is a multiple selection dialog
        if self.HasStyle(win32defines.LBS_EXTENDEDSEL) or \
            self.HasStyle(win32defines.LBS_MULTIPLESEL):
            self.SendMessageTimeout(win32defines.LB_SETCARETINDEX, index)
        else:
            self.SendMessageTimeout(win32defines.LB_SETCURSEL, index)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listboxfocuschange_wait)

        # return this control so that actions can be chained.
        return self


    #-----------------------------------------------------------
    def GetItemFocus(self):
        "Retrun the index of current selection in a ListBox"

        # if it is a multiple selection dialog
        if self.HasStyle(win32defines.LBS_EXTENDEDSEL) or \
            self.HasStyle(win32defines.LBS_MULTIPLESEL):
            return self.SendMessage(win32defines.LB_GETCARETINDEX)
        else:
            return self.SendMessage(win32defines.LB_GETCURSEL)


#====================================================================
class EditWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Edit control"

    friendlyclassname = "Edit"
    windowclasses = [
        "Edit",
        ".*Edit",
        "TMemo",
        r"WindowsForms\d*\.EDIT\..*",
        "ThunderTextBox",
        "ThunderRT6TextBox",
        ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_EditControlTypeId]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(EditWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            'SelectionIndices'])

    #-----------------------------------------------------------
    def LineCount(self):
        "Return how many lines there are in the Edit"
        return  self.SendMessage(win32defines.EM_GETLINECOUNT)

    #-----------------------------------------------------------
    def LineLength(self, line_index):
        "Return how many characters there are in the line"

        # need to first get a character index of that line
        char_index = self.SendMessage(win32defines.EM_LINEINDEX, line_index)

        # now get the length of text on that line
        return self.SendMessage (
            win32defines.EM_LINELENGTH, char_index, 0)


    #-----------------------------------------------------------
    def GetLine(self, line_index):
        "Return the line specified"

        text_len = self.LineLength(line_index)
        # create a buffer and set the length at the start of the buffer
        text = ctypes.create_unicode_buffer(text_len+3)
        text[0] = six.unichr(text_len)

        # retrieve the line itself
        win32functions.SendMessage(self, win32defines.EM_GETLINE, line_index, ctypes.byref(text))

        return text.value

    #-----------------------------------------------------------
    def texts(self):
        "Get the text of the edit control"

        texts = [self.window_text(), ]

        for i in range(self.LineCount()):
            texts.append(self.GetLine(i))

        return texts

    #-----------------------------------------------------------
    def TextBlock(self):
        "Get the text of the edit control"

        length = self.SendMessage(win32defines.WM_GETTEXTLENGTH)

        text = ctypes.create_unicode_buffer(length + 1)

        win32functions.SendMessage(self, win32defines.WM_GETTEXT, length + 1, ctypes.byref(text))

        return text.value

    #-----------------------------------------------------------
    def SelectionIndices(self):
        "The start and end indices of the current selection"
        start = ctypes.c_int()
        end = ctypes.c_int()
        self.SendMessage(
            win32defines.EM_GETSEL, ctypes.byref(start), ctypes.byref(end))

        return (start.value, end.value)

    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        """Override SetWindowText for edit controls because it should not be
        used for Edit controls.

        Edit Controls should either use SetEditText() or type_keys() to modify
        the contents of the edit control."""
        HwndWrapper.HwndWrapper.SetWindowText(self, text, append)
        raise UserWarning(
            "SetWindowText() should probably not be called for Edit Controls")

    #-----------------------------------------------------------
    def SetEditText(self, text, pos_start = None, pos_end = None):
        "Set the text of the edit control"
        self.verify_actionable()

        # allow one or both of pos_start and pos_end to be None
        if pos_start is not None or pos_end is not None:

            # if only one has been specified - then set the other
            # to the current selection start or end
            start, end = self.SelectionIndices()
            if pos_start is None:
                pos_start = start
            if pos_end is None and not isinstance(start, six.string_types):
                pos_end = end

            # set the selection if either start or end has
            # been specified
            self.Select(pos_start, pos_end)
        else:
            self.Select()

        if isinstance(text, six.text_type):
            if six.PY3:
                aligned_text = text
            else:
                aligned_text = text.encode(locale.getpreferredencoding())
        elif isinstance(text, six.binary_type):
            if six.PY3:
                aligned_text = text.decode(locale.getpreferredencoding())
            else:
                aligned_text = text
        else:
            # convert a non-string input
            if six.PY3:
                aligned_text = six.text_type(text)
            else:
                aligned_text = six.binary_type(text)
        
        if isinstance(aligned_text, six.text_type):
            buffer = ctypes.create_unicode_buffer(aligned_text, size=len(aligned_text) + 1)
        else:
            buffer = ctypes.create_string_buffer(aligned_text, size=len(aligned_text) + 1)

        # replace the selection with
        self.SendMessage(win32defines.EM_REPLACESEL, True, ctypes.byref(buffer))

        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_editsetedittext_wait)

        if isinstance(aligned_text, six.text_type):
            self.actions.log('Set text to the edit box: ' + aligned_text)
        else:
            self.actions.log(b'Set text to the edit box: ' + aligned_text)

        # return this control so that actions can be chained.
        return self

    # set SetText as an alias to SetEditText
    SetText = SetEditText

    #-----------------------------------------------------------
    def Select(self, start = 0, end = None):
        "Set the edit selection of the edit control"
        self.verify_actionable()
        win32functions.SetFocus(self)

        # if we have been asked to select a string
        if isinstance(start, six.text_type):
            string_to_select = start
            start = self.TextBlock().index(string_to_select)

            if end is None:
                end = start + len(string_to_select)
        elif isinstance(start, six.binary_type):
            string_to_select = start.decode(locale.getpreferredencoding())
            start = self.TextBlock().index(string_to_select)

            if end is None:
                end = start + len(string_to_select)

        if end is None:
            end = -1

        self.SendMessage(win32defines.EM_SETSEL, start, end)

        # give the control a chance to catch up before continuing
        win32functions.WaitGuiThreadIdle(self)

        time.sleep(Timings.after_editselect_wait)

        # return this control so that actions can be chained.
        return self


#====================================================================
class StaticWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Static control"

    friendlyclassname = "Static"
    windowclasses = [
        "Static",
        r"WindowsForms\d*\.STATIC\..*",
        "TPanel",
        ".*StaticText"]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_ImageControlTypeId,
            _UIA_dll.UIA_TextControlTypeId]
    can_be_label = True

    def __init__(self, hwnd):

        """Initialize the control"""

        super(StaticWrapper, self).__init__(hwnd)

    @property
    def _NeedsImageProp(self):

        """_NeedsImageProp=True if it is an image static"""

        # if the control is visible - and it shows an image
        if self.is_visible() and (self.HasStyle(win32defines.SS_ICON) or
                                  self.HasStyle(win32defines.SS_BITMAP) or
                                  self.HasStyle(win32defines.SS_CENTERIMAGE) or
                                  self.HasStyle(win32defines.SS_OWNERDRAW)):

            return True
        else:
            return False

#====================================================================
# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class DialogWrapper(HwndWrapper.HwndWrapper):
    "Wrap a dialog"

    friendlyclassname = "Dialog"
    #windowclasses = ["#32770", ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_WindowControlTypeId]
    can_be_label = True

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the DialogWrapper

        The only extra functionality here is to modify self.friendlyclassname
        to make it "Dialog" if the class is "#32770" otherwise to leave it
        the same as the window class.
        """
        HwndWrapper.HwndWrapper.__init__(self, hwnd)

        if self.class_name() == "#32770":
            self.friendlyclassname = "Dialog"
        else:
            self.friendlyclassname = self.class_name()

    #-----------------------------------------------------------
    def RunTests(self, tests_to_run = None, ref_controls = None):
        "Run the tests on dialog"

        # the tests package is imported only when running unittests
        from .. import tests

        # get all the controls
        controls = [self] + self.children()
        
        # add the reference controls
        if ref_controls is not None:
            matched_flags = controlproperties.SetReferenceControls(
                controls, ref_controls)
            
            # todo: allow some checking of how well the controls matched
            # matched_flags says how well they matched
            # 1 = same number of controls
            # 2 = ID's matched
            # 4 = control classes matched
            # i.e. 1 + 2 + 4 = perfect match
        
        return tests.run_tests(controls, tests_to_run)

    #-----------------------------------------------------------
    def WriteToXML(self, filename):
        "Write the dialog an XML file (requires elementtree)"
        
        controls = [self] + self.children()
        props = [ctrl.GetProperties() for ctrl in controls]

        from .. import XMLHelpers
        XMLHelpers.WriteDialogToFile(filename, props)

    #-----------------------------------------------------------
    def ClientAreaRect(self):
        """Return the client area rectangle

        From MSDN
        The client area of a control is the bounds of the control, minus the
        nonclient elements such as scroll bars, borders, title bars, and 
        menus."""
        rect = win32structures.RECT(self.rectangle())
        self.SendMessage(win32defines.WM_NCCALCSIZE, 0, ctypes.byref(rect))
        return rect

    #-----------------------------------------------------------
    def HideFromTaskbar(self):
        "Hide the dialog from the Windows taskbar"
        win32functions.ShowWindow(self, win32defines.SW_HIDE)
        win32functions.SetWindowLongPtr(self, win32defines.GWL_EXSTYLE, self.ExStyle() | win32defines.WS_EX_TOOLWINDOW)
        win32functions.ShowWindow(self, win32defines.SW_SHOW)

    #-----------------------------------------------------------
    def ShowInTaskbar(self):
        "Show the dialog in the Windows taskbar"
        win32functions.ShowWindow(self, win32defines.SW_HIDE)
        win32functions.SetWindowLongPtr(self, win32defines.GWL_EXSTYLE, self.ExStyle() | win32defines.WS_EX_APPWINDOW)
        win32functions.ShowWindow(self, win32defines.SW_SHOW)

    #-----------------------------------------------------------
    def IsInTaskbar(self):
        "Check whether the dialog is shown in the Windows taskbar"

        # Thanks to David Heffernan for the idea: 
        # http://stackoverflow.com/questions/30933219/hide-window-from-taskbar-without-using-ws-ex-toolwindow
        # A window is represented in the taskbar if:
        # It is not owned and does not have the WS_EX_TOOLWINDOW extended style, or
        # It has the WS_EX_APPWINDOW extended style.
        return self.HasExStyle(win32defines.WS_EX_APPWINDOW) or (self.Owner() is None and not self.HasExStyle(win32defines.WS_EX_TOOLWINDOW))

#    #-----------------------------------------------------------
#    def ReadControlsFromXML(self, filename):
#        from pywinauto import XMLHelpers
#        [controlproperties.ControlProps(ctrl) for
#            ctrl in XMLHelpers.ReadPropertiesFromFile(handle)]  


#    #-----------------------------------------------------------
#    def AddReference(self, reference):
#
#        if len(self.children() != len(reference)):
#            raise "different number of reference controls"
#
#        for i, ctrl in enumerate(reference):
#        # loop over each of the controls
#        # and set the reference
#            if isinstance(ctrl, dict):
#                ctrl = CtrlProps(ctrl)
#
#            self.
#            if ctrl.class_name() != self.children()[i+1].class_name():
#                print "different classes"



#====================================================================
# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class PopupMenuWrapper(HwndWrapper.HwndWrapper):
    "Wrap a Popup Menu"

    friendlyclassname = "PopupMenu"
    windowclasses = ["#32768", ]
    if sysinfo.UIA_support:
        controltypes = [
            _UIA_dll.UIA_MenuControlTypeId]
    has_title = False

    #-----------------------------------------------------------
    def is_dialog(self):
        "Return whether it is a dialog"
        return True

    #-----------------------------------------------------------
    def _menu_handle(self):
        '''Get the menu handle for the popup menu'''
        hMenu = win32gui.SendMessage(self.handle, win32defines.MN_GETHMENU)

        if not hMenu:
            raise ctypes.WinError()

        return (hMenu, False) # (hMenu, is_main_menu)

