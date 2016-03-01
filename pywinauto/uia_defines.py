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

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')

# Build a list of named constants that identify Microsoft UI Automation 
# control patterns and their appropriate comtypes classes
# We'll try to add all patterns available for the given version of Windows OS
# Reference:
# https://msdn.microsoft.com/en-us/library/windows/desktop/ee671195(v=vs.85).aspx
# header: UIAutomationClient.h

def _build_pattern_ids_dic():
    """A helper procedure to build a registry of control patterns 
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
        if hasattr(comtypes.gen.UIAutomationClient, cls_name):
            klass = getattr(comtypes.gen.UIAutomationClient, cls_name)
            
            # Contruct a pattern ID name and get the ID value
            ptrn_id_name = 'UIA_' + ptrn_name + 'PatternId'
            ptrn_id = getattr(_UIA_dll, ptrn_id_name)
    
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
toggle_state_off = 0
toggle_state_on = 1
toggle_state_inderteminate = 2

def get_elem_interface(element_info, pattern_name):
    """A helper to retrieve an element interface by the specified pattern name

    TODO: handle a wrong pattern name
    TODO: handle possible query interface exceptions
    """
    # Resolve the pattern id and the class to query
    ptrn_id, cls_name = pattern_ids[pattern_name]
    # Get the interface
    cur_ptrn = element_info.GetCurrentPattern(ptrn_id)
    iface = cur_ptrn.QueryInterface(cls_name)
    return iface
    
    
