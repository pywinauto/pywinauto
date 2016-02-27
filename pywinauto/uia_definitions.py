# Copyright (C) 2016 airelil
# Copyright (C) 2015 Intel Corporation
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

# Named constants that identify Microsoft UI Automation control patterns
# https://msdn.microsoft.com/en-us/library/windows/desktop/ee671195(v=vs.85).aspx
# header: UIAutomationClient.h
pattern_ids = {
    # Dock control pattern.
    'Dock': _UIA_dll.UIA_DockPatternId,
    
    # ExpandCollapse control pattern.
    'ExpandCollapse': _UIA_dll.UIA_ExpandCollapsePatternId,
    
    # GridItem control pattern.
    'GridItem': _UIA_dll.UIA_GridItemPatternId,
    
    # Grid control pattern.
    'Grid': _UIA_dll.UIA_GridPatternId,
    
    # Invoke control pattern.
    'Invoke': _UIA_dll.UIA_InvokePatternId,
    
    # ItemContainer control pattern.
    'ItemContainer': _UIA_dll.UIA_ItemContainerPatternId,
    
    # LegacyIAccessible control pattern.
    'LegacyIAccessible': _UIA_dll.UIA_LegacyIAccessiblePatternId,
    
    # MultipleView control pattern.
    'MulipleView': _UIA_dll.UIA_MultipleViewPatternId,
    
    # RangeValue control pattern.
    'RangeValue': _UIA_dll.UIA_RangeValuePatternId,
    
    # ScrollItem control pattern.
    'ScrollItem': _UIA_dll.UIA_ScrollItemPatternId,
    
    # Scroll control pattern.
    'Scroll': _UIA_dll.UIA_ScrollPatternId,
    
    # SelectionItem control pattern.
    'SelectionItem': _UIA_dll.UIA_SelectionItemPatternId,
    
    # Selection control pattern.
    'Selection': _UIA_dll.UIA_SelectionPatternId,
    
    # SynchronizedInput control pattern.
    'SynchronizedInput': _UIA_dll.UIA_SynchronizedInputPatternId,
    
    # TableItem control pattern.
    'TableItem': _UIA_dll.UIA_TableItemPatternId,
    
    # Table control pattern.
    'Table': _UIA_dll.UIA_TablePatternId,
    
    # Text control pattern.
    'Text': _UIA_dll.UIA_TextPatternId,
    
    # Toggle control pattern.
    'Toggle': _UIA_dll.UIA_TogglePatternId,
    
    # Transform control pattern.
    'Transform': _UIA_dll.UIA_TransformPatternId,
    
    # Value control pattern.
    'Value': _UIA_dll.UIA_ValuePatternId,
    
    # VirtualizedItem control pattern.
    'VirtualizedItem': _UIA_dll.UIA_VirtualizedItemPatternId,
    
    # Window control pattern. 
    'Window': _UIA_dll.UIA_WindowPatternId
}

# We also try to add new patterns, supported by Win8 and later versions
try:
    ### Patterns supported starting with 
    ### Windows 8.
    # Annotation control pattern.
    pattern_ids['Annotation'] = _UIA_dll.UIA_AnnotationPatternId,
    
    # Drag control pattern. 
    pattern_ids['Drag'] = _UIA_dll.UIA_DragPatternId,
    
    # DropTarget control pattern.
    pattern_ids['Drop'] = _UIA_dll.UIA_DropTargetPatternId,
    
    # ObjectModel control pattern.
    pattern_ids['ObjectModel'] = _UIA_dll.UIA_ObjectModelPatternId,
    
    # Spreadsheet control pattern.
    pattern_ids['Spreadsheet'] = _UIA_dll.UIA_SpreadsheetPatternId,
    
    # SpreadsheetItem control pattern.
    pattern_ids['SpreadsheetItem'] = _UIA_dll.UIA_SpreadsheetItemPatternId,
    
    # Styles control pattern.
    pattern_ids['Styles'] = _UIA_dll.UIA_StylesPatternId,
    
    # TextChild control pattern.
    pattern_ids['TextChild'] = _UIA_dll.UIA_TextChildPatternId,
    
    # A second version of the Text control pattern. 
    pattern_ids['TextV2'] = _UIA_dll.UIA_TextPattern2Id,
    
    # A second version of the Transform control pattern. 
    pattern_ids['TransformV2'] = _UIA_dll.UIA_TransformPattern2Id,

    
    ### Patterns supported starting with 
    ### Windows 8.1.
    # TextEdit control pattern.
    pattern_ids['TextEdit'] = _UIA_dll.UIA_TextEditPatternId,


    ### Patterns supported starting with 
    ### Windows 10.
    # CustomNavigation control pattern.
    pattern_ids['CustomNavigation'] = _UIA_dll.UIA_CustomNavigationPatternId,
except(AttributeError): 
    pass

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
    
    
