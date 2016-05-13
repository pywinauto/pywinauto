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

"""Common UIA definitions and helper functions"""

import comtypes
import comtypes.client
from . import six


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
    
    def build_condition(self, process = None, class_name = None, title = None):
        """Build UIA filtering conditions"""
        conditions = []
        if process:
            conditions.append(self.iuia.CreatePropertyCondition(
                                    self.UIA_dll.UIA_ProcessIdPropertyId, process))
        
        if class_name:
            conditions.append(self.iuia.CreatePropertyCondition(
                                    self.UIA_dll.UIA_ClassNamePropertyId, class_name))
        
        if title:
            # TODO: CreatePropertyConditionEx with PropertyConditionFlags_IgnoreCase
            conditions.append(self.iuia.CreatePropertyCondition(
                                    self.UIA_dll.UIA_NamePropertyId, title))
        
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
        cls_name = ''.join(['IUIAutomation', ptrn_name, 'Pattern'])
        if hasattr(IUIA().ui_automation_client, cls_name):
            klass = getattr(IUIA().ui_automation_client, cls_name)
            
            # Contruct a pattern ID name and get the ID value
            ptrn_id_name = 'UIA_' + ptrn_name + 'PatternId'
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
expand_state_collapsed =IUIA().ui_automation_client.ExpandCollapseState_Collapsed
expand_state_expanded = IUIA().ui_automation_client.ExpandCollapseState_Expanded
expand_state_partially = IUIA().ui_automation_client.ExpandCollapseState_PartiallyExpanded
expand_state_leaf_node = IUIA().ui_automation_client.ExpandCollapseState_LeafNode

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
    
    
