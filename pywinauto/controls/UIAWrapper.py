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

from ..UIAElementInfo import UIAElementInfo, elements_from_uia_array
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
_friendly_classes = {
    'Custom': None,
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
    """Metaclass for UiaWrapper objects"""
    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""

        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls.control_types:
            UiaMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this UIA element"""

        # Set a general wrapper by default
        wrapper_match = UIAWrapper

        # Check for a more specific wrapper in the registry
        if element.control_type in UiaMeta.control_type_to_cls:
            wrapper_match = UiaMeta.control_type_to_cls[element.control_type]

        return wrapper_match

#=========================================================================
@six.add_metaclass(UiaMeta)
class UIAWrapper(BaseWrapper):
    """Default wrapper for User Interface Automation (UIA) controls.

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
        """Return unique hash value based on element's Runtime ID"""
        return hash(self.element_info.runtime_id)

    #------------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(UIAWrapper, self).writable_props
        props.extend(['is_keyboard_focusable',
                      'has_keyboard_focus',
                      ])
        return props

    #------------------------------------------------------------
    def friendly_class_name(self):
        """Return the friendly class name for the control

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
                ctrl_type = _known_control_types[self.element_info.control_type]
                if (ctrl_type not in _friendly_classes) or (_friendly_classes[ctrl_type] is None):
                    self.friendlyclassname = ctrl_type
                else:
                    self.friendlyclassname = _friendly_classes[ctrl_type]
        return self.friendlyclassname

    #-----------------------------------------------------------
    def is_keyboard_focusable(self):
        """Return True if element can be focused with keyboard"""
        return self.element_info.element.CurrentIsKeyboardFocusable == 1

    #-----------------------------------------------------------
    def has_keyboard_focus(self):
        """Return True if element is focused with keyboard"""
        return self.element_info.element.CurrentHasKeyboardFocus == 1

    #-----------------------------------------------------------
    def set_focus(self):
        """Set the focus to this element"""
        if self.is_keyboard_focusable() and not self.has_keyboard_focus():
            try:
                self.element_info.element.SetFocus()
            except comtypes.COMError:
                pass # TODO: add RuntimeWarning here

        return self

    #-----------------------------------------------------------
    def invoke(self):
        """An interface to the Invoke method of the Invoke control pattern"""
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Invoke")
        iface.Invoke()
        
        # Return itself to allow action chaining
        return self

    #-----------------------------------------------------------
    def expand(self):
        """An interface to Expand method of the ExpandCollapse control pattern.

        Displays all child nodes, controls, or content of the control
        """

        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "ExpandCollapse")
        iface.Expand()

        # Return itself to allow action chaining
        return self

    #-----------------------------------------------------------
    def collapse(self):
        """
        An interface to Collapse method of the ExpandCollapse control pattern.

        Displays all child nodes, controls, or content of the control
        """

        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "ExpandCollapse")
        iface.Collapse()

        # Return itself to allow action chaining
        return self

    #-----------------------------------------------------------
    def get_expand_state(self):
        """An interface to CurrentExpandCollapseState property of 
        the ExpandCollapse control pattern.

        Indicates the state, expanded or collapsed, of the control.
        
        Values for enumeration as defined in uia_defines module:
        expand_state_collapsed = 0
        expand_state_expanded = 1
        expand_state_partially = 2
        expand_state_leaf_node = 3
        """

        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "ExpandCollapse")
        return iface.CurrentExpandCollapseState

    #-----------------------------------------------------------
    def is_expanded(self):
        """Test if the control is expanded"""
        state = self.get_expand_state()
        return state == uia_defs.expand_state_expanded

    #-----------------------------------------------------------
    def is_collapsed(self):
        """Test if the control is collapsed"""
        state = self.get_expand_state()
        return state == uia_defs.expand_state_collapsed

    def get_selection(self):
        """An interface to GetSelection of the SelectionProvider pattern

        Retrieves a UI Automation provider for each child element
        that is selected. Builds a list of UIAElementInfo elements 
        from all retrieved providers.
        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Selection")
        ptrs_array = iface.GetCurrentSelection()
        return elements_from_uia_array(ptrs_array)

    def can_select_multiple(self):
        """An interface to CanSelectMultiple of the SelectionProvider pattern

        Indicates whether the UI Automation provider allows more than one 
        child element to be selected concurrently.

        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Selection")
        return iface.CurrentCanSelectMultiple

    def is_selection_required(self):
        """
        An interface to IsSelectionRequired property of the 
        SelectionProvider pattern.

        This property can be dynamic. For example, the initial state of 
        a control might not have any items selected by default, 
        meaning that IsSelectionRequired is FALSE. However, 
        after an item is selected the control must always have 
        at least one item selected.
        """
        elem = self.element_info.element
        iface = uia_defs.get_elem_interface(elem, "Selection")
        return iface.CurrentIsSelectionRequired

    def select_by_name_or_by_idx(self, item_name = None, item_index = 0):
        """Find a child item by the name or index and select
        
        The action can be applied for dirrent controls with items:
        ComboBox, TreeView, ListView
        """

        list_ = self.element_info.children(title = item_name)
        if item_index < len(list_):
            elem = list_[item_index].element
            iface = uia_defs.get_elem_interface(elem, "SelectionItem")
            iface.Select()
        else:
            raise ValueError



backend.register('uia', UIAElementInfo, UIAWrapper)
