# Copyright (C) 2016 Vasily Ryabov
# Copyright (C) 2016 airelil
# Copyright (C) 2010 Mark Mc Mahon
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

"""Wrap various UIA windows controls
"""

import time
import locale

from .. import six
from ..timings import Timings
from .. import win32functions

from .. import uia_defines as uia_defs
from . import UIAWrapper
from ..uia_defines import IUIA


#====================================================================
class ButtonWrapper(UIAWrapper.UIAWrapper):
    "Wrap a UIA-compatible Button, CheckBox or RadioButton control"

    control_types = [
        IUIA().UIA_dll.UIA_ButtonControlTypeId,
        IUIA().UIA_dll.UIA_CheckBoxControlTypeId,
        IUIA().UIA_dll.UIA_RadioButtonControlTypeId
        ]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ButtonWrapper, self).__init__(hwnd)

    #-----------------------------------------------------------
    def toggle(self):
        """
        An interface to Toggle method of the Toggle control pattern.
        Control supporting the Toggle pattern cycles through its 
        toggle states in the following order: 
        ToggleState_On, ToggleState_Off and, 
        if supported, ToggleState_Indeterminate
        
        Usually applied for the check box control.
        
        The radio button control does not implement IToggleProvider, 
        because it is not capable of cycling through its valid states.
        Toggle a state of a check box control. (Use 'select' method instead)
        Notice, a radio button control isn't supported by UIA.
        https://msdn.microsoft.com/en-us/library/windows/desktop/ee671290(v=vs.85).aspx
        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Toggle")
        iface.Toggle()

        # Return itself so that action can be chained
        return self

    #-----------------------------------------------------------
    def get_toggle_state(self):
        """Get a toggle state of a check box control.
        The toggle state is represented by an integer
        0 - unchecked
        1 - checked
        2 - indeterminate

        The following constants are defined in the uia_defines module
        toggle_state_off = 0
        toggle_state_on = 1
        toggle_state_inderteminate = 2
        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Toggle")
        return iface.CurrentToggleState

    #-----------------------------------------------------------
    def is_dialog(self):
        "Buttons are never dialogs so return False"
        return False

    #-----------------------------------------------------------
    def click(self):
        "Click the Button control by using Invoke pattern"
        self.invoke()

        # Return itself so that action can be chained
        return self

    #-----------------------------------------------------------
    def select(self):
        """
        An interface to Select method of the SelectionItem control pattern.

        Usually applied for a radio button control
        """

        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "SelectionItem")
        iface.Select()

        # Return itself so that action can be chained
        return self
        
    #-----------------------------------------------------------
    def is_selected(self):
        """
        An interface to CurrentIsSelected method of the SelectionItem control pattern.

        Usually applied for a radio button control
        """

        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "SelectionItem")
        return iface.CurrentIsSelected


#====================================================================
class EditWrapper(UIAWrapper.UIAWrapper):
    """Wrap an UIA-compatible Edit control"""

    controltypes = [
        IUIA().UIA_dll.UIA_EditControlTypeId,
        IUIA().UIA_dll.UIA_DocumentControlTypeId
    ]
    has_title = False

    #-----------------------------------------------------------
    def __init__(self, elem_or_handle):
        """Initialize the control"""
        super(EditWrapper, self).__init__(elem_or_handle)

    #-----------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(EditWrapper, self).writable_props
        props.extend(['selection_indices'])
        return props

    #-----------------------------------------------------------
    def line_count(self):
        """Return how many lines there are in the Edit"""
        return self.window_text().count("\n") + 1

    #-----------------------------------------------------------
    def line_length(self, line_index):
        """Return how many characters there are in the line"""
        # need to first get a character index of that line
        lines = self.window_text().splitlines()
        if line_index < len(lines):
            return len(lines[line_index])
        elif line_index == self.line_count() - 1:
            return 0
        else:
            raise IndexError("There are only {0} lines but given index is {1}".format(self.line_count(), line_index))

    #-----------------------------------------------------------
    def get_line(self, line_index):
        """Return the line specified"""
        lines = self.window_text().splitlines()
        if line_index < len(lines):
            return lines[line_index]
        elif line_index == self.line_count() - 1:
            return ""
        else:
            raise IndexError("There are only {0} lines but given index is {1}".format(self.line_count(), line_index))

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
        return self.window_text()

    #-----------------------------------------------------------
    def selection_indices(self):
        """The start and end indices of the current selection"""
        #TODO: some elements can support multiple, disjoint spans of selected text
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Text")

        selected_text = iface.GetSelection().GetElement(0).GetText(-1)
        start = self.window_text().find(selected_text)
        end = start + len(selected_text)

        return (start, end)

    #-----------------------------------------------------------
    def set_window_text(self, text, append = False):
        """Override set_window_text for edit controls because it should not be
        used for Edit controls.

        Edit Controls should either use set_edit_text() or type_keys() to modify
        the contents of the edit control.
        """
        super(EditWrapper, self).set_window_text(text, append)
        raise UserWarning(
            "set_window_text() should probably not be called for Edit Controls")

    #-----------------------------------------------------------
    def set_edit_text(self, text, pos_start = None, pos_end = None):
        """Set the text of the edit control"""
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
        else:
            pos_start = 0
            pos_end = len(self.window_text())

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

        try:
            # Try to set text using IUIAutomationValuePattern
            iface = uia_defs.get_elem_interface(self.element_info.element, "Value")
            # Calculate new text value
            current_text = self.window_text()
            new_text = current_text[:pos_start] + aligned_text + current_text[pos_end:]
            iface.SetValue(new_text)
        except uia_defs.NoPatternInterfaceError:
            # Element doesn't support ValuePattern (e.g. RichTextBox)
            # Replace selected text with type_keys()
            self.select(pos_start, pos_end)
            self.type_keys(aligned_text, with_spaces=True, with_newlines=True, with_tabs=True)

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

    #-----------------------------------------------------------
    def select(self, start = 0, end = None):
        """Set the edit selection of the edit control"""
        self.verify_actionable()
        self.set_focus()

        # if we have been asked to select a string
        if isinstance(start, six.text_type):
            string_to_select = start
        elif isinstance(start, six.binary_type):
            string_to_select = start.decode(locale.getpreferredencoding())
        elif isinstance(start, six.integer_types):
            if isinstance(end, six.integer_types) and start > end:
                start, end = end, start
            string_to_select = self.window_text()[start:end]

        if string_to_select:
            elem = self.element_info.element
            iface = uia_defs.get_elem_interface(elem, "Text")
            document_range = iface.DocumentRange
            search_range = document_range.FindText(string_to_select, False, False)

            try:
                search_range.Select()
            except ValueError:
                # No such string has been found
                pass

            # give the control a chance to catch up before continuing
            if self.element_info.handle:
                win32functions.WaitGuiThreadIdle(self)
            else:
                # TODO: get WaitGuiThreadIdle function for elements without handle
                pass

            time.sleep(Timings.after_editselect_wait)

        # return this control so that actions can be chained.
        return self
