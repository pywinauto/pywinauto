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
import pywinauto.uia_defines as uia_defs

from .six import integer_types
from .handleprops import dumpwindow, controlid
from .ElementInfo import ElementInfo
from .win32structures import RECT

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
from comtypes.gen import UIAutomationClient

_iuia = comtypes.CoCreateInstance(
    UIAutomationClient.CUIAutomation().IPersist_GetClassID(),
    interface=UIAutomationClient.IUIAutomation,
    clsctx=comtypes.CLSCTX_INPROC_SERVER
)

_true_condition = _iuia.CreateTrueCondition()

_tree_scope = {
    'ancestors': _UIA_dll.TreeScope_Ancestors,
    'children': _UIA_dll.TreeScope_Children,
    'descendants': _UIA_dll.TreeScope_Descendants,
    'element': _UIA_dll.TreeScope_Element,
    'parent': _UIA_dll.TreeScope_Parent,
    'subtree': _UIA_dll.TreeScope_Subtree
}

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
            elif isinstance(handle_or_elem, UIAutomationClient.IUIAutomationElement):
                self._element = handle_or_elem
            else:
                raise TypeError("UIAElementInfo object can be initialized ' + \
                    'with integer or IUIAutomationElement instance only!")
        else:
            self._element = _iuia.GetRootElement()            

    @property
    def element(self):
        "Return AutomationElement's instance"
        return self._element

    @property
    def automation_id(self):
        "Return AutomationId of the element"
        return self._element.CurrentAutomationId

    @property
    def control_id(self):
        "Return ControlId of the element if it has a handle"
        if (self.handle):
            return controlid(self.handle)
        else:
            return None

    @property
    def process_id(self):
        "Return ProcessId of the element"
        return self._element.CurrentProcessId

    @property
    def framework_id(self):
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
    def class_name(self):
        "Return class name of the element"
        return self._element.CurrentClassName

    @property
    def control_type(self):
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

    def _get_elements(self, scope, cond=_true_condition):
        "Find all elements according to the given scope and conditions"
        elements = []
        ptrs_array = self._element.FindAll(scope, cond)
        for num in range(ptrs_array.Length):
            child = ptrs_array.GetElement(num)
            elements.append(UIAElementInfo(child))

        return elements

    def _build_condition(self, process = None, class_name = None):
        "Build UIA filtering conditions"
        full_cond = _true_condition
        if process:
            new_cond = _iuia.CreatePropertyCondition(
                                    _UIA_dll.UIA_ProcessIdPropertyId, process)
            full_cond = _iuia.CreateAndCondition(new_cond, full_cond)
            
        if class_name:
            new_cond = _iuia.CreatePropertyCondition(
                                    _UIA_dll.UIA_ClassNamePropertyId, class_name)
            full_cond = _iuia.CreateAndCondition(new_cond, full_cond)

        return full_cond

    def children(self, **kwargs):
        "Return a list of only immediate children of the element according to the criterias"
        cond = self._build_condition(**kwargs)
        return self._get_elements(_tree_scope["children"], cond)

    def descendants(self, **kwargs):
        "Return a list of all descendant children of the element according to the criterias"
        cond = self._build_condition(**kwargs)
        return self._get_elements(_tree_scope["descendants"], cond)

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

    def dump_window(self):
        "Dump window to a set of properties"
        return dumpwindow(self.handle)

    @property
    def rich_text(self):
        "Return rich_text of the element"
        if not self.class_name:
            return self.name
        try:
            pattern = uia_defs.get_elem_interface(self._element, "Text")
            return pattern.DocumentRange.GetText(-1)
        except Exception:
            return self.name # TODO: probably we should raise an exception here

    def __eq__(self, other):
        "Check if 2 UIAElementInfo objects describe 1 actual element"
        if not isinstance(other, UIAElementInfo):
            return False;
        return self.handle == other.handle and self.class_name == other.class_name and self.name == other.name and \
               self.process_id == other.process_id and self.automation_id == other.automation_id and \
               self.framework_id == other.framework_id and self.control_type == other.control_type
