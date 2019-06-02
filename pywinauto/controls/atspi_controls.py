# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Wrap various ATSPI windows controls"""

from . import atspiwrapper
from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from ..linux.atspi_element_info import AtspiElementInfo
from ..linux.atspi_objects import AtspiStateSet, AtspiAccessible, AtspiAction

from Xlib import Xatom
from Xlib.display import Display

# region PATTERNS


class ButtonWrapper(atspiwrapper.AtspiWrapper):
    """Wrap a UIA-compatible Button, CheckBox or RadioButton control"""
    _control_types = ['Button',
        'CheckBox',
        'RadioButton',
    ]

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ButtonWrapper, self).__init__(elem)
        self.action = self.element_info.get_action()

    def click(self):
        """Click the Button control"""
        self.action.do_action_by_name("click")
        return self


    # -----------------------------------------------------------
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
        pass
