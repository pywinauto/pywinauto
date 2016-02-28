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
# and their appropriate comtypes classes
# https://msdn.microsoft.com/en-us/library/windows/desktop/ee671195(v=vs.85).aspx
# header: UIAutomationClient.h
pattern_ids = {
    # Dock control pattern.
    'Dock': [
        _UIA_dll.UIA_DockPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationDockPattern
        ],
    
    # ExpandCollapse control pattern.
    'ExpandCollapse': [
        _UIA_dll.UIA_ExpandCollapsePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationExpandCollapsePattern
        ],
    
    # GridItem control pattern.
    'GridItem': [
        _UIA_dll.UIA_GridItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationGridItemPattern 
        ],
    
    # Grid control pattern.
    'Grid': [
        _UIA_dll.UIA_GridPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationGridPattern
        ],
    
    # Invoke control pattern.
    'Invoke': [
        _UIA_dll.UIA_InvokePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern
        ],
    
    # ItemContainer control pattern.
    'ItemContainer': [
        _UIA_dll.UIA_ItemContainerPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationItemContainerPattern
        ],
    
    # LegacyIAccessible control pattern.
    'LegacyIAccessible': [
        _UIA_dll.UIA_LegacyIAccessiblePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationLegacyIAccessiblePattern
        ],
    
    # MultipleView control pattern.
    'MulipleView': [
        _UIA_dll.UIA_MultipleViewPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationMultipleViewPattern
        ],
    
    # RangeValue control pattern.
    'RangeValue': [
        _UIA_dll.UIA_RangeValuePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomation
        ],
    
    # ScrollItem control pattern.
    'ScrollItem': [
        _UIA_dll.UIA_ScrollItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationScrollItemPattern
        ],
    
    # Scroll control pattern.
    'Scroll': [
        _UIA_dll.UIA_ScrollPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationScrollPattern,
        ],
    
    # SelectionItem control pattern.
    'SelectionItem': [
        _UIA_dll.UIA_SelectionItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationSelectionItemPattern
        ],
    
    # Selection control pattern.
    'Selection': [
        _UIA_dll.UIA_SelectionPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationSelectionPattern
        ],
    
    # SynchronizedInput control pattern.
    'SynchronizedInput': [
        _UIA_dll.UIA_SynchronizedInputPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationSynchronizedInputPattern
        ],
    
    # TableItem control pattern.
    'TableItem': [
        _UIA_dll.UIA_TableItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTableItemPattern
        ],
    
    # Table control pattern.
    'Table': [
        _UIA_dll.UIA_TablePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTablePattern
        ],
    
    # Text control pattern.
    'Text': [
        _UIA_dll.UIA_TextPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTextPattern
        ],
    
    # Toggle control pattern.
    'Toggle': [
        _UIA_dll.UIA_TogglePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern
        ],
    
    # Transform control pattern.
    'Transform': [
        _UIA_dll.UIA_TransformPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTransformPattern
        ],
    
    # Value control pattern.
    'Value': [
        _UIA_dll.UIA_ValuePatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationValuePattern
        ],
    
    # VirtualizedItem control pattern.
    'VirtualizedItem': [
        _UIA_dll.UIA_VirtualizedItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationVirtualizedItemPattern
        ],
    
    # Window control pattern. 
    'Window': [
        _UIA_dll.UIA_WindowPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationWindowPattern
        ]
}

# We also try to add new patterns, supported by Win8 and later versions
try:
    ### Patterns supported starting with 
    ### Windows 8.
    # Annotation control pattern.
    pattern_ids['Annotation'] = [
        _UIA_dll.UIA_AnnotationPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationAnnotationPattern
        ],
    
    # Drag control pattern. 
    pattern_ids['Drag'] = [
        _UIA_dll.UIA_DragPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationDragPattern
        ],
    
    # DropTarget control pattern.
    pattern_ids['Drop'] = [
        _UIA_dll.UIA_DropTargetPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationDropTargetPattern
        ],
    
    # ObjectModel control pattern.
    pattern_ids['ObjectModel'] = [
        _UIA_dll.UIA_ObjectModelPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationObjectModelPattern
        ],
    
    # Spreadsheet control pattern.
    pattern_ids['Spreadsheet'] = [
        _UIA_dll.UIA_SpreadsheetPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationSpreadsheetPattern
        ],
    
    # SpreadsheetItem control pattern.
    pattern_ids['SpreadsheetItem'] = [
        _UIA_dll.UIA_SpreadsheetItemPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationSpreadsheetItemPattern
        ],
    
    # Styles control pattern.
    pattern_ids['Styles'] = [
        _UIA_dll.UIA_StylesPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationStylesPattern
        ],
    
    # TextChild control pattern.
    pattern_ids['TextChild'] = [
        _UIA_dll.UIA_TextChildPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTextChildPattern
        ],
    
    # A second version of the Text control pattern. 
    pattern_ids['TextV2'] = [
        _UIA_dll.UIA_TextPattern2Id,
        comtypes.gen.UIAutomationClient.IUIAutomationTextPattern
        ],
    
    # A second version of the Transform control pattern. 
    pattern_ids['TransformV2'] = [
        _UIA_dll.UIA_TransformPattern2Id,
        comtypes.gen.UIAutomationClient.IUIAutomationTransformPattern
        ],

    ### Patterns supported starting with 
    ### Windows 8.1.
    # TextEdit control pattern.
    pattern_ids['TextEdit'] = [
        _UIA_dll.UIA_TextEditPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationTextEditPattern
        ],

    ### Patterns supported starting with 
    ### Windows 10.
    # CustomNavigation control pattern.
    pattern_ids['CustomNavigation'] = [
        _UIA_dll.UIA_CustomNavigationPatternId,
        comtypes.gen.UIAutomationClient.IUIAutomationCustomNavigationPattern
        ],
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
    
    
