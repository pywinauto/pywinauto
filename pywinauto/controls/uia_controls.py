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

import pywinauto.uia_defines as uia_defs
from . import UIAWrapper
from ..uia_defines import _UIA_dll


#====================================================================
class ButtonWrapper(UIAWrapper.UIAWrapper):
    "Wrap a UIA-compatible Button, CheckBox or RadioButton control"

    control_types = [
        _UIA_dll.UIA_ButtonControlTypeId,
        _UIA_dll.UIA_CheckBoxControlTypeId,
        _UIA_dll.UIA_RadioButtonControlTypeId
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
        Toggle a state of a check box control.
        Notice, a radio button control isn't supported by UIA.
        https://msdn.microsoft.com/en-us/library/windows/desktop/ee671290(v=vs.85).aspx
        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Toggle")
        iface.Toggle()

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
        
