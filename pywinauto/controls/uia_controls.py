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

"""
Wrap various UIA windows controls
"""
import pywinauto.six as six
from .. import uia_defines as uia_defs
from . import UIAWrapper
from ..uia_defines import IUIA


#====================================================================
class ButtonWrapper(UIAWrapper.UIAWrapper):
    """Wrap a UIA-compatible Button, CheckBox or RadioButton control"""

    control_types = [
        IUIA().UIA_dll.UIA_ButtonControlTypeId,
        IUIA().UIA_dll.UIA_CheckBoxControlTypeId,
        IUIA().UIA_dll.UIA_RadioButtonControlTypeId
        ]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
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
        """
        Get a toggle state of a check box control.

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
        """Buttons are never dialogs so return False"""
        return False

    #-----------------------------------------------------------
    def click(self):
        """Click the Button control by using Invoke pattern"""
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
class ComboBoxWrapper(UIAWrapper.UIAWrapper):
    """Wrap a UIA CoboBox control"""

    control_types = [
        IUIA().UIA_dll.UIA_ComboBoxControlTypeId
        ]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(hwnd)

    #-----------------------------------------------------------
    def texts(self):
        """Return the text of the items in the combobox"""

        texts = []
        # ComboBox has to be expanded to populate a list of its children items
        try:
            self.expand()
            for c in self.children():
                texts.append(c.window_text())
        finally:
            # Make sure we collapse back in any case
            self.collapse()
        return texts

    def select(self, item):
        """
        Select the ComboBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """

        item_index = 0
        item_name = None
        if isinstance(item, six.integer_types):
            item_index = item
        elif isinstance(item, six.string_types):
            item_name = item
        else:
            err_msg = "unsupported {0} for item {1}".format(type(item), item)
            raise ValueError(err_msg)

        # ComboBox has to be expanded to populate a list of its children items
        self.expand()
        try:
            self.select_by_name_or_by_idx(item_name, item_index)
        # TODO: do we need to handle except ValueError for a wrong name/index ?
        #except ValueError:
        #    raise  # re-raise the last exception
        finally:
            # Make sure we collapse back in any case
            self.collapse()
        return self

    #-----------------------------------------------------------
    # TODO: add selected_texts for a combobox with a multi-select support
    def selected_text(self):
        """
        Return the selected text or None
        
        Notice, that in case of multi-select it will be only the text from 
        a first selected item
        """
        selection = self.get_selection()
        if selection:
            return selection[0].name
        else:
            return None

    #-----------------------------------------------------------
    # TODO: add selected_indices for a combobox with multi-select support
    def selected_index(self):
        """Return the selected index"""

        # Go through all children and look for an index 
        # of an item with the same text.
        # Maybe there is another and more efficient way to do it
        selection = self.get_selection()
        if selection:
            for i, c in enumerate(self.children()):
                if c.window_text() == selection[0].name:
                    return i
        return None

    #-----------------------------------------------------------
    def item_count(self):
        """
        Return the number of items in the combobox
        
        The interface is kept mostly for a backward compatibility with
        the native ComboBox interface
        """
        return self.control_count()
