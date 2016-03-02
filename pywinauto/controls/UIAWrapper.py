# Copyright (C) 2016 Alexander Rumyantsev
# Copyright (C) 2015 Intel Corporation
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

"""Basic wrapping of UI Automation elements"""

from __future__ import unicode_literals
from __future__ import print_function

import time

from .. import six
from ..timings import Timings
from ..actionlogger import ActionLogger

import comtypes
import comtypes.client
import pywinauto.uia_defines as uia_defs

from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from ..UIAElementInfo import UIAElementInfo
from ..UIAElementInfo import _UIA_dll

#region PATTERNS
AutomationElement = comtypes.gen.UIAutomationClient.IUIAutomationElement

DockPattern = comtypes.gen.UIAutomationClient.IUIAutomationDockPattern
ExpandCollapsePattern = comtypes.gen.UIAutomationClient.IUIAutomationExpandCollapsePattern
GridItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationGridItemPattern
GridPattern = comtypes.gen.UIAutomationClient.IUIAutomationGridPattern
InvokePattern = comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern
ItemContainerPattern = comtypes.gen.UIAutomationClient.IUIAutomationItemContainerPattern
LegacyIAccessiblePattern = comtypes.gen.UIAutomationClient.IUIAutomationLegacyIAccessiblePattern
MultipleViewPattern = comtypes.gen.UIAutomationClient.IUIAutomationMultipleViewPattern
RangeValuePattern = comtypes.gen.UIAutomationClient.IUIAutomationRangeValuePattern
ScrollItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationScrollItemPattern
ScrollPattern = comtypes.gen.UIAutomationClient.IUIAutomationScrollPattern
SelectionItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationSelectionItemPattern
SelectionPattern = comtypes.gen.UIAutomationClient.IUIAutomationSelectionPattern
SynchronizedInputPattern = comtypes.gen.UIAutomationClient.IUIAutomationSynchronizedInputPattern
TableItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationTableItemPattern
TablePattern = comtypes.gen.UIAutomationClient.IUIAutomationTablePattern
TextPattern = comtypes.gen.UIAutomationClient.IUIAutomationTextPattern
TogglePattern = comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern
TransformPattern = comtypes.gen.UIAutomationClient.IUIAutomationTransformPattern
ValuePattern = comtypes.gen.UIAutomationClient.IUIAutomationValuePattern
VirtualizedItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationVirtualizedItemPattern
WindowPattern = comtypes.gen.UIAutomationClient.IUIAutomationWindowPattern
#endregion

#=========================================================================
_control_types = [attr[len('UIA_'):-len('ControlTypeId')] for attr in dir(_UIA_dll) if attr.endswith('ControlTypeId')]
_known_control_types = {}
for type_ in _control_types:
    _known_control_types[_UIA_dll.__getattribute__('UIA_' + type_ + 'ControlTypeId')] = type_

#=========================================================================
_pywinauto_control_types = {'Custom': None,
                            'DataGrid': None,
                            'Document': None,
                            'Group': 'GroupBox',
                            'Hyperlink': None,
                            'Image': None,
                            'List': 'ListBox',
                            'MenuBar': None,
                            'Menu': None,
                            'Pane': None,
                            'ProgressBar': 'Progress',
                            'ScrollBar': None,
                            'Separator': None,
                            'Slider': None,
                            'Spinner': 'UpDown',
                            'SplitButton': None,
                            'Tab': 'TabControl',
                            'Table': None,
                            'Text': 'Static',
                            'Thumb': None,
                            'TitleBar': None,
                            'ToolBar': 'Toolbar',
                            'ToolTip': 'ToolTips',
                            'Tree': None,
                            'Window': 'Dialog',
                            }

#=========================================================================
class UiaMeta(BaseMeta):
    "Metaclass for UiaWrapper objects"
    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        "Register the control types"

        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls.control_types:
            UiaMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        "Find the correct wrapper for this UIA element"

        # Set a general wrapper by default
        wrapper_match = UIAWrapper

        # Check for a more specific wrapper in the registry
        if element.control_type in UiaMeta.control_type_to_cls:
            wrapper_match = UiaMeta.control_type_to_cls[element.control_type]

        return wrapper_match

#=========================================================================
@six.add_metaclass(UiaMeta)
class UIAWrapper(BaseWrapper):
    """
    Default wrapper for User Interface Automation (UIA) controls.

    All other UIA wrappers are derived from this.

    This class wraps a lot of functionality of underlying UIA features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """
    
    control_types = []

    #------------------------------------------------------------
    # TODO: can't inherit __new__ function from BaseWrapper?
    def __new__(cls, element_info):
        # only use the meta class to find the wrapper for BaseWrapper
        # so allow users to force the wrapper if they want
        if cls != UIAWrapper:
            obj = object.__new__(cls)
            obj.__init__(element_info)
            return obj

        new_class = cls.find_wrapper(element_info)
        obj = object.__new__(new_class)

        obj.__init__(element_info)

        return obj

    #-----------------------------------------------------------
    def __init__(self, element_info):
        """Initialize the control
        * **element_info** is either a valid UIAElementInfo or it can be an
          instance or subclass of UIAWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['uia'])

    #------------------------------------------------------------
    def __hash__(self):
        "Return unique hash value based on element's Runtime ID"
        return hash(self.element_info.runtime_id)

    #------------------------------------------------------------
    def friendly_class_name(self):
        """
        Return the friendly class name for the control

        This differs from the class of the control in some cases.
        class_name() is the actual 'Registered' window class of the control
        while friendly_class_name() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if self.friendlyclassname is None:
            if self.element_info.control_type not in _known_control_types.keys():
                self.friendlyclassname = str(self.element_info.control_type)
            else:
                ControlType = _known_control_types[self.element_info.control_type]
                if (ControlType not in _pywinauto_control_types.keys()) or (_pywinauto_control_types[ControlType] is None):
                    self.friendlyclassname = ControlType
                else:
                    self.friendlyclassname = _pywinauto_control_types[ControlType]
        return self.friendlyclassname

    #-----------------------------------------------------------
    def is_keyboard_focusable(self):
        "Return True if element can be focused with keyboard"
        return self.element_info.element.CurrentIsKeyboardFocusable == 1

    #-----------------------------------------------------------
    def has_keyboard_focus(self):
        "Return True if element is focused with keyboard"
        return self.element_info.element.CurrentHasKeyboardFocus == 1

    #-----------------------------------------------------------
    def set_focus(self):
        "Set the focus to this element"
        if self.is_keyboard_focusable() and not self.has_keyboard_focus():
            try:
                self.element_info.element.SetFocus()
            except comtypes.COMError as exc:
                pass # TODO: add RuntimeWarning here

        return self

    #-----------------------------------------------------------
    def invoke(self):
        "An interface to the Invoke method of the Invoke control pattern"
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Invoke")
        iface.Invoke()


backend.register('uia', UIAElementInfo, UIAWrapper)
