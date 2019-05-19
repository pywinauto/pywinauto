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

"""Common UIA definitions and helper functions"""

import comtypes
import comtypes.client
import six


class _Singleton(type):

    """
    Singleton metaclass implementation from StackOverflow

    http://stackoverflow.com/q/6760685/3648361
    """

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@six.add_metaclass(_Singleton)
class IUIA(object):

    """Singleton class to store global COM objects from UIAutomationCore.dll"""

    def __init__(self):
        self.UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
        self.ui_automation_client = comtypes.gen.UIAutomationClient
        self.iuia = comtypes.CoCreateInstance(
                self.ui_automation_client.CUIAutomation().IPersist_GetClassID(),
                interface=self.ui_automation_client.IUIAutomation,
                clsctx=comtypes.CLSCTX_INPROC_SERVER
                )
        self.true_condition = self.iuia.CreateTrueCondition()
        self.tree_scope = {
                'ancestors': self.UIA_dll.TreeScope_Ancestors,
                'children': self.UIA_dll.TreeScope_Children,
                'descendants': self.UIA_dll.TreeScope_Descendants,
                'element': self.UIA_dll.TreeScope_Element,
                'parent': self.UIA_dll.TreeScope_Parent,
                'subtree': self.UIA_dll.TreeScope_Subtree,
                }
        self.root = self.iuia.GetRootElement()

        self.get_focused_element = self.iuia.GetFocusedElement

        # collect all known control types
        start_len = len('UIA_')
        end_len = len('ControlTypeId')
        self._control_types = [attr[start_len:-end_len] for attr in dir(self.UIA_dll) if attr.endswith('ControlTypeId')]

        self.known_control_types = { 'InvalidControlType': 0 } # string id: numeric id
        self.known_control_type_ids = { 0: 'InvalidControlType' } # numeric id: string id

        for ctrl_type in self._control_types:
            type_id_name = 'UIA_' + ctrl_type + 'ControlTypeId'
            type_id = getattr(self.UIA_dll, type_id_name)
            self.known_control_types[ctrl_type] = type_id
            self.known_control_type_ids[type_id] = ctrl_type

    def build_condition(self, process=None, class_name=None, title=None, control_type=None,
                        content_only=None):
        """Build UIA filtering conditions"""
        conditions = []
        if process:
            conditions.append(self.iuia.CreatePropertyCondition(self.UIA_dll.UIA_ProcessIdPropertyId, process))

        if class_name:
            conditions.append(self.iuia.CreatePropertyCondition(self.UIA_dll.UIA_ClassNamePropertyId, class_name))

        if control_type:
            if isinstance(control_type, six.string_types):
                control_type = self.known_control_types[control_type]
            elif not isinstance(control_type, int):
                raise TypeError('control_type must be string or integer')
            conditions.append(self.iuia.CreatePropertyCondition(self.UIA_dll.UIA_ControlTypePropertyId, control_type))

        if title:
            # TODO: CreatePropertyConditionEx with PropertyConditionFlags_IgnoreCase
            conditions.append(self.iuia.CreatePropertyCondition(self.UIA_dll.UIA_NamePropertyId, title))

        if isinstance(content_only, bool):
            conditions.append(self.iuia.CreatePropertyCondition(self.UIA_dll.UIA_IsContentElementPropertyId,
                                                                content_only))

        if len(conditions) > 1:
            return self.iuia.CreateAndConditionFromArray(conditions)

        if len(conditions) == 1:
            return conditions[0]

        return self.true_condition

# Build a list of named constants that identify Microsoft UI Automation
# control patterns and their appropriate comtypes classes
# We'll try to add all patterns available for the given version of Windows OS
# Reference:
# https://msdn.microsoft.com/en-us/library/windows/desktop/ee671195(v=vs.85).aspx
# header: UIAutomationClient.h

def _build_pattern_ids_dic():
    """
    A helper procedure to build a registry of control patterns
    supported on the current system
    """
    base_names = [
        'Dock', 'ExpandCollapse', 'GridItem', 'Grid', 'Invoke', 'ItemContainer',
        'LegacyIAccessible', 'MulipleView', 'RangeValue', 'ScrollItem', 'Scroll',
        'SelectionItem', 'Selection', 'SynchronizedInput', 'TableItem', 'Table',
        'Text', 'Toggle', 'VirtualizedItem', 'Value', 'Window',
        'Transform',

        # Windows 8 and later
        'Annotation', 'Drag', 'Drop', 'ObjectModel', 'Spreadsheet',
        'SpreadsheetItem', 'Styles', 'TextChild', 'TextV2', 'TransformV2',

        # Windows 8.1 and later
        'TextEdit',

        # Windows 10 and later
        'CustomNavigation'
    ]

    ptrn_ids_dic = {}

    # Loop over the all base names and try to retrieve control patterns
    for ptrn_name in base_names:

        # Construct a class name and check if it is supported by comtypes
        v2 = ""
        name = ptrn_name
        if ptrn_name.endswith("V2"):
            name = ptrn_name[:-2]
            v2 = "2"
        cls_name = ''.join(['IUIAutomation', name, 'Pattern', v2])
        if hasattr(IUIA().ui_automation_client, cls_name):
            klass = getattr(IUIA().ui_automation_client, cls_name)

            # Contruct a pattern ID name and get the ID value
            ptrn_id_name = 'UIA_' + name + 'Pattern' + v2 + 'Id'
            ptrn_id = getattr(IUIA().UIA_dll, ptrn_id_name)

            # Update the registry of known patterns
            ptrn_ids_dic[ptrn_name] = (ptrn_id, klass)

    return ptrn_ids_dic

pattern_ids = _build_pattern_ids_dic()


# Return values for the toggle_state propery
#     enum ToggleState {
#       ToggleState_Off,
#       ToggleState_On,
#       ToggleState_Indeterminate
# };
# The definition can also be found in the comtypes package
# In a file automatically generated according to UIAutomation GUID:
# comtypes\gen\_944DE083_8FB8_45CF_BCB7_C477ACB2F897_*.py
toggle_state_off = IUIA().ui_automation_client.ToggleState_Off
toggle_state_on = IUIA().ui_automation_client.ToggleState_On
toggle_state_inderteminate = IUIA().ui_automation_client.ToggleState_Indeterminate


class NoPatternInterfaceError(Exception):

    """There is no such interface for the specified pattern"""
    pass

# values for enumeration 'ExpandCollapseState'
expand_state_collapsed = IUIA().ui_automation_client.ExpandCollapseState_Collapsed
expand_state_expanded = IUIA().ui_automation_client.ExpandCollapseState_Expanded
expand_state_partially = IUIA().ui_automation_client.ExpandCollapseState_PartiallyExpanded
expand_state_leaf_node = IUIA().ui_automation_client.ExpandCollapseState_LeafNode

# values for enumeration 'WindowVisualState'
window_visual_state_normal = IUIA().ui_automation_client.WindowVisualState_Normal
window_visual_state_maximized = IUIA().ui_automation_client.WindowVisualState_Maximized
window_visual_state_minimized = IUIA().ui_automation_client.WindowVisualState_Minimized

# values for enumeration 'ScrollAmount'
scroll_large_decrement = IUIA().ui_automation_client.ScrollAmount_LargeDecrement
scroll_small_decrement = IUIA().ui_automation_client.ScrollAmount_SmallDecrement
scroll_no_amount = IUIA().ui_automation_client.ScrollAmount_NoAmount
scroll_large_increment = IUIA().ui_automation_client.ScrollAmount_LargeIncrement
scroll_small_increment = IUIA().ui_automation_client.ScrollAmount_SmallIncrement

vt_empty = IUIA().ui_automation_client.VARIANT.empty.vt
vt_null = IUIA().ui_automation_client.VARIANT.null.vt

def get_elem_interface(element_info, pattern_name):
    """A helper to retrieve an element interface by the specified pattern name

    TODO: handle a wrong pattern name
    """
    # Resolve the pattern id and the class to query
    ptrn_id, cls_name = pattern_ids[pattern_name]
    # Get the interface
    try:
        cur_ptrn = element_info.GetCurrentPattern(ptrn_id)
        iface = cur_ptrn.QueryInterface(cls_name)
    except(ValueError):
        raise NoPatternInterfaceError()
    return iface
