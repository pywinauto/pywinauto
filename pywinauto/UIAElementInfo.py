# Copyright (C) 2016 Vasily Ryabov
# Copyright (C) 2016 Alexander Rumyantsev
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

"""Implementation of the class to deal with an UI element (based on UI Automation API)

"""

import comtypes
import comtypes.client

from .six import integer_types
from .handleprops import text, dumpwindow, controlid
from .ElementInfo import ElementInfo
from .win32structures import RECT

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
_iuia = comtypes.CoCreateInstance(
    comtypes.gen.UIAutomationClient.CUIAutomation().IPersist_GetClassID(),
    interface=comtypes.gen.UIAutomationClient.IUIAutomation,
    clsctx=comtypes.CLSCTX_INPROC_SERVER
)

_trueCondition = _iuia.CreateTrueCondition()

_treeScope = {
    'ancestors': _UIA_dll.TreeScope_Ancestors,
    'children': _UIA_dll.TreeScope_Children,
    'descendants': _UIA_dll.TreeScope_Descendants,
    'element': _UIA_dll.TreeScope_Element,
    'parent': _UIA_dll.TreeScope_Parent,
    'subtree': _UIA_dll.TreeScope_Subtree
}


# Named constants that identify Microsoft UI Automation control patterns
# https://msdn.microsoft.com/en-us/library/windows/desktop/ee671195(v=vs.85).aspx
# header: UIAutomationClient.h
_pattern_id = {
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
    _pattern_id['Annotation'] = _UIA_dll.UIA_AnnotationPatternId,
    
    # Drag control pattern. 
    _pattern_id['Drag'] = _UIA_dll.UIA_DragPatternId,
    
    # DropTarget control pattern.
    _pattern_id['Drop'] = _UIA_dll.UIA_DropTargetPatternId,
    
    # ObjectModel control pattern.
    _pattern_id['ObjectModel'] = _UIA_dll.UIA_ObjectModelPatternId,
    
    # Spreadsheet control pattern.
    _pattern_id['Spreadsheet'] = _UIA_dll.UIA_SpreadsheetPatternId,
    
    # SpreadsheetItem control pattern.
    _pattern_id['SpreadsheetItem'] = _UIA_dll.UIA_SpreadsheetItemPatternId,
    
    # Styles control pattern.
    _pattern_id['Styles'] = _UIA_dll.UIA_StylesPatternId,
    
    # TextChild control pattern.
    _pattern_id['TextChild'] = _UIA_dll.UIA_TextChildPatternId,
    
    # A second version of the Text control pattern. 
    _pattern_id['TextV2'] = _UIA_dll.UIA_TextPattern2Id,
    
    # A second version of the Transform control pattern. 
    _pattern_id['TransformV2'] = _UIA_dll.UIA_TransformPattern2Id,

    
    ### Patterns supported starting with 
    ### Windows 8.1.
    # TextEdit control pattern.
    _pattern_id['TextEdit'] = _UIA_dll.UIA_TextEditPatternId,


    ### Patterns supported starting with 
    ### Windows 10.
    # CustomNavigation control pattern.
    _pattern_id['CustomNavigation'] = _UIA_dll.UIA_CustomNavigationPatternId,
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
    

"""
Possible properties:

CurrentAcceleratorKey
CurrentAccessKey
CurrentAriaProperties
CurrentAriaRole
CurrentControllerFor
CurrentCulture
CurrentDescribedBy
CurrentFlowsTo
CurrentHelpText
CurrentIsContentElement
CurrentIsControlElement
CurrentIsDataValidForForm
CurrentIsPassword
CurrentIsRequiredForForm
CurrentItemStatus
CurrentItemType
CurrentLabeledBy
CurrentLocalizedControlType
CurrentOrientation
CurrentProviderDescription
"""

class UIAElementInfo(ElementInfo):
    "UI element wrapper for IUIAutomation API"

    def __init__(self, handle_or_elem = None):
        """
        Create an instance of UIAElementInfo from a handle (int or long)
        or from an IUIAutomationElement.
        If handle_or_elem is None create an instance for UI root element
        """
        if handle_or_elem is not None:
            if isinstance(handle_or_elem, integer_types):
                # Create instane of UIAElementInfo from a handle
                self._element = _iuia.ElementFromHandle(handle_or_elem)
            elif isinstance(handle_or_elem, comtypes.gen.UIAutomationClient.IUIAutomationElement):
                self._element = handle_or_elem
            else:
                raise TypeError("UIAElementInfo object can be initialized with integer or IUIAutomationElement \
                                instance only!")
        else:
            self._element = _iuia.GetRootElement()            

    @property
    def element(self):
        "Return AutomationElement's instance"
        return self._element

    @property
    def automationId(self):
        "Return AutomationId of the element"
        return self._element.CurrentAutomationId

    @property
    def controlId(self):
        "Return ControlId of the element if it has a handle"
        if (self.handle):
            return controlid(self.handle)
        else:
            return None

    @property
    def processId(self):
        "Return ProcessId of the element"
        return self._element.CurrentProcessId

    @property
    def frameworkId(self):
        "Return FrameworkId of the element"
        return self._element.CurrentFrameworkId

    @property
    def runtime_id(self):
        "Return Runtime ID (hashable value but may be different from run to run)"
        return self._element.GetRuntimeId()

    @property
    def name(self):
        "Return name of the element"
        return self._element.CurrentName

    @property
    def className(self):
        "Return class name of the element"
        return self._element.CurrentClassName

    @property
    def controlType(self):
        "Return control type of element"
        return self._element.CurrentControlType

    @property
    def handle(self):
        "Return handle of the element"
        return self._element.CurrentNativeWindowHandle

    @property
    def parent(self):
        "Return parent of the element"
        parent_elem = _iuia.ControlViewWalker.GetParentElement(self._element)
        if parent_elem:
            return UIAElementInfo(parent_elem)
        else:
            return None

    @property
    def children(self):
        "Return list of immediate children for the element"
        children = []
        
        childrenArray = self._element.FindAll(_treeScope['children'], _trueCondition)
        for childNumber in range(childrenArray.Length):
            childElement = childrenArray.GetElement(childNumber)
            children.append(UIAElementInfo(childElement))
            
        return children

    @property
    def descendants(self):
        "Return list of all children for the element"
        descendants = []

        descendantsArray = self._element.FindAll(_treeScope['descendants'], _trueCondition)
        for descendantNumber in range(descendantsArray.Length):
            descendantElement = descendantsArray.GetElement(descendantNumber)
            descendants.append(UIAElementInfo(descendantElement))

        return descendants

    @property
    def visible(self):
        "Check if the element is visible"
        return bool(not self._element.CurrentIsOffscreen)

    @property
    def enabled(self):
        "Check if the element is enabled"
        return bool(self._element.CurrentIsEnabled)

    @property
    def rectangle(self):
        "Return rectangle of the element"
        bound_rect = self._element.CurrentBoundingRectangle
        rect = RECT()
        rect.left = bound_rect.left
        rect.top = bound_rect.top
        rect.right = bound_rect.right
        rect.bottom = bound_rect.bottom
        return rect

    def dumpWindow(self):
        "Dump window to a set of properties"
        return dumpwindow(self.handle)

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
        """
        pattern = self._element.GetCurrentPattern(_pattern_id["Toggle"])
        interface = pattern.QueryInterface(
                comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern)
        interface.Toggle()
        
    @property
    def toggle_state(self):
        """
        An interface to ToggleState property of the Toggle control pattern.
        A control supporting the Toggle pattern cycles through its 
        toggle states in the following order: 
        ToggleState_On, ToggleState_Off and, 
        if supported, ToggleState_Indeterminate
        
        Usually applied for the check box control.
        
        The radio button control does not implement IToggleProvider, 
        because it is not capable of cycling through its valid states.
        """
        pattern = self._element.GetCurrentPattern(_pattern_id["Toggle"])
        interface = pattern.QueryInterface(
                comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern)
        return interface.CurrentToggleState

    def invoke(self):
        "An interface to the Invoke method of the Invoke control pattern"""
        pattern = self._element.GetCurrentPattern(_pattern_id["Invoke"])
        interface = pattern.QueryInterface(
                comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern)
        interface.Invoke()


    @property
    def richText(self):
        "Return richText of the element"
        if not self.className:
            return self.name
        try:
            pattern = self._element.GetCurrentPattern(_pattern_id["Text"]).QueryInterface(
                comtypes.gen.UIAutomationClient.IUIAutomationTextPattern)
            return pattern.DocumentRange.GetText(-1)
        except Exception:
            return self.name # TODO: probably we should raise an exception here

    def __eq__(self, other):
        "Check if 2 UIAElementInfo objects describe 1 actual element"
        if not isinstance(other, UIAElementInfo):
            return False;
        return self.handle == other.handle and self.className == other.className and self.name == other.name and \
               self.processId == other.processId and self.automationId == other.automationId and \
               self.frameworkId == other.frameworkId and self.controlType == other.controlType
