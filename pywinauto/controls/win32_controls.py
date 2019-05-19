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

"""Wraps various standard windows controls"""
from __future__ import unicode_literals

import time
import ctypes
import win32gui
import locale
import six

from . import hwndwrapper

from .. import win32functions
from .. import win32defines
from .. import win32structures

from ..timings import Timings
from .. import deprecated

#====================================================================
class ButtonWrapper(hwndwrapper.HwndWrapper):

    """Wrap a windows Button control"""

    friendlyclassname = "Button"
    windowclasses = [
        "Button",
        ".*Button",
        r"WindowsForms\d*\.BUTTON\..*",
        ".*CheckBox",
        ]
    can_be_label = True

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ButtonWrapper, self).__init__(hwnd)

        #self._set_if_needs_image()

    @property
    def _needs_image_prop(self):
        """_needs_image_prop=True if it is an image button"""
        # optimization call style once and work with that rather than
        # calling has_style a number of times
        style = self.style()

        if self.is_visible() and (style & win32defines.BS_BITMAP or
                                  style & win32defines.BS_ICON or
                                  style & win32defines.BS_OWNERDRAW):
            return True
        else:
            return False
    # Non PEP-8 alias
    _NeedsImageProp = deprecated(_needs_image_prop, deprecated_name='_NeedsImageProp')

    #-----------------------------------------------------------
    def friendly_class_name(self):
        """
        Return the friendly class name of the button

        Windows controls with the class "Button" can look like different
        controls based on their style. They can look like the following
        controls:

          - Buttons, this method returns "Button"
          - CheckBoxes, this method returns "CheckBox"
          - RadioButtons, this method returns "RadioButton"
          - GroupBoxes, this method returns "GroupBox"
        """
        # get the least significant BIT
        style_lsb = self.style() & 0xF

        f_class_name = 'Button'

        vb_buttons = {
            "ThunderOptionButton": "RadioButton",
            "ThunderCheckBox": "CheckBox",
            "ThunderCommandButton": "Button"
        }

        if self.class_name() in vb_buttons:
            f_class_name = vb_buttons[self.class_name()]

        if style_lsb in [win32defines.BS_3STATE,
                        win32defines.BS_AUTO3STATE,
                        win32defines.BS_AUTOCHECKBOX,
                        win32defines.BS_CHECKBOX, ]:
            f_class_name = "CheckBox"
        elif style_lsb in [win32defines.BS_RADIOBUTTON,
                        win32defines.BS_AUTORADIOBUTTON, ]:
            f_class_name = "RadioButton"
        elif style_lsb == win32defines.BS_GROUPBOX:
            f_class_name = "GroupBox"

        if self.style() & win32defines.BS_PUSHLIKE:
            f_class_name = "Button"

        return f_class_name

    #-----------------------------------------------------------
    def get_check_state(self):
        """
        Return the check state of the checkbox

        The check state is represented by an integer
        0 - unchecked
        1 - checked
        2 - indeterminate

        The following constants are defined in the win32defines module
        BST_UNCHECKED = 0
        BST_CHECKED = 1
        BST_INDETERMINATE = 2
        """
        self._ensure_enough_privileges('BM_GETCHECK')
        return self.send_message(win32defines.BM_GETCHECK)
    # Non PEP-8 alias
    GetCheckState = deprecated(get_check_state)

    __check_states = {
        win32defines.BST_UNCHECKED: False,
        win32defines.BST_CHECKED: True,
        win32defines.BST_INDETERMINATE: None,
        }
    #-----------------------------------------------------------
    def is_checked(self):
        """Return True if checked, False if not checked, None if indeterminate"""
        return self.__check_states[self.get_check_state()]

    #-----------------------------------------------------------
    def check(self):
        """Check a checkbox"""
        self._ensure_enough_privileges('BM_SETCHECK')
        self.send_message_timeout(win32defines.BM_SETCHECK,
                                  win32defines.BST_CHECKED)

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    Check = deprecated(check)

    #-----------------------------------------------------------
    def uncheck(self):
        """Uncheck a checkbox"""
        self._ensure_enough_privileges('BM_SETCHECK')
        self.send_message_timeout(win32defines.BM_SETCHECK,
                                  win32defines.BST_UNCHECKED)

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    UnCheck = deprecated(uncheck, deprecated_name='UnCheck')

    #-----------------------------------------------------------
    def set_check_indeterminate(self):
        """Set the checkbox to indeterminate"""
        self._ensure_enough_privileges('BM_SETCHECK')
        self.send_message_timeout(win32defines.BM_SETCHECK,
                                  win32defines.BST_INDETERMINATE)

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    SetCheckIndeterminate = deprecated(set_check_indeterminate)

    #-----------------------------------------------------------
    def is_dialog(self):
        """Buttons are never dialogs so return False"""
        return False

    #-----------------------------------------------------------
    def click(self, button="left", pressed="", coords=(0, 0),
              double=False, absolute=False):
        """Click the Button control"""
        #import win32functions
        #win32functions.WaitGuiThreadIdle(self)
        #self.notify_parent(win32defines.BN_CLICKED)
        hwndwrapper.HwndWrapper.click(self, button, pressed, coords, double, absolute)
        #win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_button_click_wait)

    #-----------------------------------------------------------
    def check_by_click(self):
        """Check the CheckBox control by click() method"""
        if self.get_check_state() != win32defines.BST_CHECKED:
            self.click()
    # Non PEP-8 alias
    CheckByClick = deprecated(check_by_click)

    #-----------------------------------------------------------
    def uncheck_by_click(self):
        """Uncheck the CheckBox control by click() method"""
        if self.get_check_state() != win32defines.BST_UNCHECKED:
            self.click()
    # Non PEP-8 alias
    UncheckByClick = deprecated(uncheck_by_click)

    #-----------------------------------------------------------
    def check_by_click_input(self):
        """Check the CheckBox control by click_input() method"""
        if self.get_check_state() != win32defines.BST_CHECKED:
            self.click_input()
    # Non PEP-8 alias
    CheckByClickInput = deprecated(check_by_click_input)

    #-----------------------------------------------------------
    def uncheck_by_click_input(self):
        """Uncheck the CheckBox control by click_input() method"""
        if self.get_check_state() != win32defines.BST_UNCHECKED:
            self.click_input()
    # Non PEP-8 alias
    UncheckByClickInput = deprecated(uncheck_by_click_input)

#====================================================================
def _get_multiple_text_items(wrapper, count_msg, item_len_msg, item_get_msg):
    """Helper function to get multiple text items from a control"""
    texts = []

    # find out how many text items are in the combobox
    num_items = wrapper.send_message(count_msg)

    # get the text for each item in the combobox
    for i in range(0, num_items):
        text_len = wrapper.send_message (item_len_msg, i, 0)

        if six.PY3:
            text = ctypes.create_unicode_buffer(text_len + 1)
        else:
            text = ctypes.create_string_buffer(text_len + 1)

        wrapper.send_message(item_get_msg, i, ctypes.byref(text))

        if six.PY3:
            texts.append(text.value.replace('\u200e', ''))
        else:
            texts.append(text.value.decode(locale.getpreferredencoding(), 'ignore').replace('?', ''))

    return texts


#====================================================================
class ComboBoxWrapper(hwndwrapper.HwndWrapper):

    """Wrap a windows ComboBox control"""

    friendlyclassname = "ComboBox"
    windowclasses = [
        "ComboBox",
        r"WindowsForms\d*\.COMBOBOX\..*",
        ".*ComboBox", ]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ComboBoxWrapper, self).writable_props
        props.extend(["selected_index",
                      "dropped_rect",
                      ])
        return props

    #-----------------------------------------------------------
    def dropped_rect(self):
        """Get the dropped rectangle of the combobox"""
        dropped_rect = win32structures.RECT()

        self.send_message(
            win32defines.CB_GETDROPPEDCONTROLRECT,
            0,
            ctypes.byref(dropped_rect))

        # we need to offset the dropped rect from the control
        dropped_rect -= self.rectangle()

        return dropped_rect
    # Non PEP-8 alias
    DroppedRect = deprecated(dropped_rect)

    #-----------------------------------------------------------
    def item_count(self):
        """Return the number of items in the combobox"""
        self._ensure_enough_privileges('CB_GETCOUNT')
        return self.send_message(win32defines.CB_GETCOUNT)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    #-----------------------------------------------------------
    def selected_index(self):
        """Return the selected index"""
        self._ensure_enough_privileges('CB_GETCURSEL')
        return self.send_message(win32defines.CB_GETCURSEL)
    # Non PEP-8 alias
    SelectedIndex = deprecated(selected_index)

    #-----------------------------------------------------------
    def selected_text(self):
        """Return the selected text"""
        return self.item_texts()[self.selected_index()]
    # Non PEP-8 alias
    SelectedText = deprecated(selected_text)

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        """Get the index for the item with this 'ident'"""
        if isinstance(ident, six.integer_types):

            if ident >= self.item_count():
                raise IndexError(('Combobox has {0} items, you requested ' + \
                    'item {1} (0 based)').format(self.item_count(), ident))

            # negative index
            if ident < 0:
                # convert it to a positive index
                ident = (self.item_count() + ident)

        elif isinstance(ident, six.string_types):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.item_texts().index(ident)

        return ident

    #-----------------------------------------------------------
    def item_data(self, item):
        """Returns the item data associated with the item if any"""
        index = self._get_item_index(item)
        return self.send_message(win32defines.CB_GETITEMDATA, index)
    # Non PEP-8 alias
    ItemData = deprecated(item_data)

    #-----------------------------------------------------------
    def item_texts(self):
        """Return the text of the items of the combobox"""
        self._ensure_enough_privileges('CB_GETCOUNT')
        return _get_multiple_text_items(
            self,
            win32defines.CB_GETCOUNT,
            win32defines.CB_GETLBTEXTLEN,
            win32defines.CB_GETLBTEXT)
    # Non PEP-8 alias
    ItemTexts = deprecated(item_texts)

    #-----------------------------------------------------------
    def texts(self):
        """Return the text of the items in the combobox"""
        texts = [self.window_text()]
        texts.extend(self.item_texts())
        return texts

    #-----------------------------------------------------------
    def get_properties(self):
        """Return the properties of the control as a dictionary"""
        props = hwndwrapper.HwndWrapper.get_properties(self)

        #props['item_data'] = []
        #for i in range(self.item_count()):
        #    props['item_data'].append(self.item_data(i))

        return props

    #-----------------------------------------------------------
    def select(self, item):
        """Select the ComboBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        self.verify_actionable()

        index = self._get_item_index(item)

        # change the selected item
        self.send_message_timeout(win32defines.CB_SETCURSEL, index, timeout=0.05)

        # Notify the parent that we are finished selecting
        self.notify_parent(win32defines.CBN_SELENDOK)

        # Notify the parent that we have changed
        self.notify_parent(win32defines.CBN_SELCHANGE)

        # simple combo boxes don't have drop downs so they do not recieve
        # this notification
        if self.has_style(win32defines.CBS_DROPDOWN):
            # Notify the parent that the drop down has closed
            self.notify_parent(win32defines.CBN_CLOSEUP)


        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_comboboxselect_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    Select = deprecated(select)

    #-----------------------------------------------------------
    #def deselect(self, item):
    # Not implemented because it doesn't make sense for combo boxes.

    #TODO def edit_control(self): # return the edit control of the Combobox

    #TODO def list_control(self): # return the list control of the combobox

    #TODO def item_text(self, index):  # get the test of item XX?

    #TODO def edit_text(self):  # or should this be self.EditControl.text()?


#====================================================================
class ListBoxWrapper(hwndwrapper.HwndWrapper):

    """Wrap a windows ListBox control"""

    friendlyclassname = "ListBox"
    windowclasses = [
        "ListBox",
        r"WindowsForms\d*\.LISTBOX\..*",
        ".*ListBox", ]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ListBoxWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ListBoxWrapper, self).writable_props
        props.extend(["selected_indices"])
        return props

    #-----------------------------------------------------------
    def is_single_selection(self):
        """Check whether the listbox has single selection mode."""
        self._ensure_enough_privileges('LB_GETSELCOUNT')
        num_selected = self.send_message(win32defines.LB_GETSELCOUNT)

        # if we got LB_ERR then it is a single selection list box
        return (num_selected == win32defines.LB_ERR)
    # Non PEP-8 alias
    IsSingleSelection = deprecated(is_single_selection)

    #-----------------------------------------------------------
    def selected_indices(self):
        """The currently selected indices of the listbox"""
        self._ensure_enough_privileges('LB_GETSELCOUNT')
        num_selected = self.send_message(win32defines.LB_GETSELCOUNT)

        # if we got LB_ERR then it is a single selection list box
        if num_selected == win32defines.LB_ERR:
            items = tuple([self.send_message(win32defines.LB_GETCURSEL)])

        # otherwise it is a multiselection list box
        else:
            items = (ctypes.c_int * num_selected)()

            self.send_message(
                win32defines.LB_GETSELITEMS, num_selected, ctypes.byref(items))

            # Need to convert from Ctypes array to a python tuple
            items = tuple(items)

        return items
    # Non PEP-8 alias
    SelectedIndices = deprecated(selected_indices)

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        """Return the index of the item 'ident'"""
        if isinstance(ident, six.integer_types):

            if ident >= self.item_count():
                raise IndexError(('ListBox has {0} items, you requested ' + \
                    'item {1} (0 based)').format(self.item_count(), ident))

            # negative index
            if ident < 0:
                ident = (self.item_count() + ident)

        elif isinstance(ident, six.string_types):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.item_texts().index(ident) #-1

        return ident

    #-----------------------------------------------------------
    def item_count(self):
        """Return the number of items in the ListBox"""
        self._ensure_enough_privileges('LB_GETCOUNT')
        return self.send_message(win32defines.LB_GETCOUNT)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    #-----------------------------------------------------------
    def item_data(self, i):
        """Return the item_data if any associted with the item"""
        index = self._get_item_index(i)
        return self.send_message(win32defines.LB_GETITEMDATA, index)
    # Non PEP-8 alias
    ItemData = deprecated(item_data)

    #-----------------------------------------------------------
    def item_texts(self):
        """Return the text of the items of the listbox"""
        self._ensure_enough_privileges('LB_GETCOUNT')
        return _get_multiple_text_items(
            self,
            win32defines.LB_GETCOUNT,
            win32defines.LB_GETTEXTLEN,
            win32defines.LB_GETTEXT)
    # Non PEP-8 alias
    ItemTexts = deprecated(item_texts)

    #-----------------------------------------------------------
    def item_rect(self, item):
        """Return the rect of the item"""
        index = self._get_item_index(item)
        rect = win32structures.RECT()
        res = self.send_message(win32defines.LB_GETITEMRECT, index, ctypes.byref(rect))
        if res == win32defines.LB_ERR:
            raise RuntimeError("LB_GETITEMRECT failed")
        return rect
    # Non PEP-8 alias
    ItemRect = deprecated(item_rect)

    #-----------------------------------------------------------
    def texts(self):
        """Return the texts of the control"""
        texts = [self.window_text()]
        texts.extend(self.item_texts())
        return texts

#    #-----------------------------------------------------------
#    def get_properties(self):
#        "Return the properties as a dictionary for the control"
#        props = hwndwrapper.HwndWrapper.get_properties(self)
#
#        props['item_data'] = []
#        for i in range(self.item_count()):
#            props['item_data'].append(self.item_data(i))
#
#        return props

    #-----------------------------------------------------------
    def select(self, item, select=True):
        """Select the ListBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        if self.is_single_selection() and isinstance(item, (list, tuple)) and len(item) > 1:
            raise Exception('Cannot set multiple selection for single-selection listbox!')

        if isinstance(item, (list, tuple)):
            for i in item:
                if i is not None:
                    self.select(i, select)
            return self

        self.verify_actionable()

        # Make sure we have an index  so if passed in a
        # string then find which item it is
        index = self._get_item_index(item)

        if self.is_single_selection():
            # change the selected item
            self.send_message_timeout(win32defines.LB_SETCURSEL, index)
        else:
            if select:
                # add the item to selection
                self.send_message_timeout(win32defines.LB_SETSEL, win32defines.TRUE, index)
            else:
                # remove the item from selection
                self.send_message_timeout(win32defines.LB_SETSEL, win32defines.FALSE, index)

        # Notify the parent that we have changed
        self.notify_parent(win32defines.LBN_SELCHANGE)

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_listboxselect_wait)

        return self
    # Non PEP-8 alias
    Select = deprecated(select)

    #-----------------------------------------------------------
    def set_item_focus(self, item):
        """Set the ListBox focus to the item at index"""
        index = self._get_item_index(item)

        # if it is a multiple selection dialog
        if self.has_style(win32defines.LBS_EXTENDEDSEL) or \
            self.has_style(win32defines.LBS_MULTIPLESEL):
            self.send_message_timeout(win32defines.LB_SETCARETINDEX, index)
        else:
            self.send_message_timeout(win32defines.LB_SETCURSEL, index)

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_listboxfocuschange_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    SetItemFocus = deprecated(set_item_focus)

    #-----------------------------------------------------------
    def get_item_focus(self):
        """Retrun the index of current selection in a ListBox"""
        # if it is a multiple selection dialog
        if self.has_style(win32defines.LBS_EXTENDEDSEL) or \
            self.has_style(win32defines.LBS_MULTIPLESEL):
            return self.send_message(win32defines.LB_GETCARETINDEX)
        else:
            return self.send_message(win32defines.LB_GETCURSEL)
    # Non PEP-8 alias
    GetItemFocus = deprecated(get_item_focus)


#====================================================================
class EditWrapper(hwndwrapper.HwndWrapper):

    """Wrap a windows Edit control"""

    friendlyclassname = "Edit"
    windowclasses = [
        "Edit",
        ".*Edit",
        "TMemo",
        r"WindowsForms\d*\.EDIT\..*",
        "ThunderTextBox",
        "ThunderRT6TextBox",
        ]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(EditWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(EditWrapper, self).writable_props
        props.extend(['selection_indices'])
        return props

    #-----------------------------------------------------------
    def line_count(self):
        """Return how many lines there are in the Edit"""
        self._ensure_enough_privileges('EM_GETLINECOUNT')
        return  self.send_message(win32defines.EM_GETLINECOUNT)
    # Non PEP-8 alias
    LineCount = deprecated(line_count)

    #-----------------------------------------------------------
    def line_length(self, line_index):
        """Return how many characters there are in the line"""
        self._ensure_enough_privileges('EM_LINEINDEX')
        # need to first get a character index of that line
        char_index = self.send_message(win32defines.EM_LINEINDEX, line_index)

        # now get the length of text on that line
        return self.send_message (
            win32defines.EM_LINELENGTH, char_index, 0)
    # Non PEP-8 alias
    LineLength = deprecated(line_length)

    #-----------------------------------------------------------
    def get_line(self, line_index):
        """Return the line specified"""
        text_len = self.line_length(line_index)
        # create a buffer and set the length at the start of the buffer
        text = ctypes.create_unicode_buffer(text_len+3)
        text[0] = six.unichr(text_len)

        # retrieve the line itself
        win32functions.SendMessage(self, win32defines.EM_GETLINE, line_index, ctypes.byref(text))

        return text.value
    # Non PEP-8 alias
    GetLine = deprecated(get_line)

    #-----------------------------------------------------------
    def texts(self):
        """Get the text of the edit control"""
        texts = [self.window_text(), ]

        for i in range(self.line_count()):
            texts.append(self.get_line(i))

        return texts

    #-----------------------------------------------------------
    def text_block(self):
        """Get the text of the edit control"""
        length = self.send_message(win32defines.WM_GETTEXTLENGTH)

        text = ctypes.create_unicode_buffer(length + 1)

        win32functions.SendMessage(self, win32defines.WM_GETTEXT, length + 1, ctypes.byref(text))

        return text.value
    # Non PEP-8 alias
    TextBlock = deprecated(text_block)

    #-----------------------------------------------------------
    def selection_indices(self):
        """The start and end indices of the current selection"""
        self._ensure_enough_privileges('EM_GETSEL')
        start = ctypes.c_int()
        end = ctypes.c_int()
        self.send_message(
            win32defines.EM_GETSEL, ctypes.byref(start), ctypes.byref(end))

        return (start.value, end.value)
    # Non PEP-8 alias
    SelectionIndices = deprecated(selection_indices)

    #-----------------------------------------------------------
    def set_window_text(self, text, append = False):
        """Override set_window_text for edit controls because it should not be
        used for Edit controls.

        Edit Controls should either use set_edit_text() or type_keys() to modify
        the contents of the edit control."""
        hwndwrapper.HwndWrapper.set_window_text(self, text, append)
        raise UserWarning(
            "set_window_text() should probably not be called for Edit Controls")

    #-----------------------------------------------------------
    def set_edit_text(self, text, pos_start = None, pos_end = None):
        """Set the text of the edit control"""
        self._ensure_enough_privileges('EM_REPLACESEL')
        self.verify_actionable()

        # allow one or both of pos_start and pos_end to be None
        if pos_start is not None or pos_end is not None:

            # if only one has been specified - then set the other
            # to the current selection start or end
            start, end = self.selection_indices()
            if pos_start is None:
                pos_start = start
            if pos_end is None and not isinstance(start, six.string_types):
                pos_end = end

            # set the selection if either start or end has
            # been specified
            self.select(pos_start, pos_end)
        else:
            self.select()

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
        self.send_message(win32defines.EM_REPLACESEL, True, ctypes.byref(buffer))

        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_editsetedittext_wait)

        if isinstance(aligned_text, six.text_type):
            self.actions.log('Set text to the edit box: ' + aligned_text)
        else:
            self.actions.log(b'Set text to the edit box: ' + aligned_text)

        # return this control so that actions can be chained.
        return self

    # set SetText as an alias to set_edit_text
    set_text = set_edit_text
    # Non PEP-8 alias
    SetText = deprecated(set_text)
    # Non PEP-8 alias
    SetEditText = deprecated(set_edit_text)

    #-----------------------------------------------------------
    def select(self, start = 0, end = None):
        """Set the edit selection of the edit control"""
        self._ensure_enough_privileges('EM_SETSEL')
        self.verify_actionable()
        win32functions.SetFocus(self)

        # if we have been asked to select a string
        if isinstance(start, six.text_type):
            string_to_select = start
            start = self.text_block().index(string_to_select)

            if end is None:
                end = start + len(string_to_select)
        elif isinstance(start, six.binary_type):
            string_to_select = start.decode(locale.getpreferredencoding())
            start = self.text_block().index(string_to_select)

            if end is None:
                end = start + len(string_to_select)

        if end is None:
            end = -1

        self.send_message(win32defines.EM_SETSEL, start, end)

        # give the control a chance to catch up before continuing
        win32functions.WaitGuiThreadIdle(self.handle)

        time.sleep(Timings.after_editselect_wait)

        # return this control so that actions can be chained.
        return self
    # Non PEP-8 alias
    Select = deprecated(select)


#====================================================================
class StaticWrapper(hwndwrapper.HwndWrapper):

    """Wrap a windows Static control"""

    friendlyclassname = "Static"
    windowclasses = [
        "Static",
        r"WindowsForms\d*\.STATIC\..*",
        "TPanel",
        ".*StaticText"]
    can_be_label = True

    def __init__(self, hwnd):
        """Initialize the control"""
        super(StaticWrapper, self).__init__(hwnd)

    @property
    def _needs_image_prop(self):
        """_needs_image_prop=True if it is an image static"""
        # if the control is visible - and it shows an image
        if self.is_visible() and (self.has_style(win32defines.SS_ICON) or
                                  self.has_style(win32defines.SS_BITMAP) or
                                  self.has_style(win32defines.SS_CENTERIMAGE) or
                                  self.has_style(win32defines.SS_OWNERDRAW)):

            return True
        else:
            return False
    # Non PEP-8 alias
    _NeedsImageProp = deprecated(_needs_image_prop, deprecated_name='_NeedsImageProp')


#====================================================================
class PopupMenuWrapper(hwndwrapper.HwndWrapper):

    """Wrap a Popup Menu"""

    friendlyclassname = "PopupMenu"
    windowclasses = ["#32768", ]
    has_title = False

    #-----------------------------------------------------------
    def is_dialog(self):
        """Return whether it is a dialog"""
        return True

    #-----------------------------------------------------------
    def _menu_handle(self):
        """Get the menu handle for the popup menu"""
        hMenu = win32gui.SendMessage(self.handle, win32defines.MN_GETHMENU)

        if not hMenu:
            raise ctypes.WinError()

        return (hMenu, False) # (hMenu, is_main_menu)

