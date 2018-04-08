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

"""Implementation of the class to deal with an UI element (based on UI Automation API)"""

from comtypes import COMError
from six import integer_types, text_type

from .uia_defines import IUIA
from .uia_defines import get_elem_interface

from .handleprops import dumpwindow, controlid
from .element_info import ElementInfo
from .win32structures import RECT
from .actionlogger import ActionLogger


def elements_from_uia_array(ptrs, cache_enable=False):
    """Build a list of UIAElementInfo elements from IUIAutomationElementArray"""
    elements = []
    for n in range(ptrs.Length):
        try:
            elements.append(UIAElementInfo(ptrs.GetElement(n), cache_enable))
        except COMError:
            continue
    return elements


class UIAElementInfo(ElementInfo):
    """UI element wrapper for IUIAutomation API"""

    def __init__(self, handle_or_elem=None, cache_enable=False):
        """
        Create an instance of UIAElementInfo from a handle (int or long)
        or from an IUIAutomationElement.

        If handle_or_elem is None create an instance for UI root element.
        """
        if handle_or_elem is not None:
            if isinstance(handle_or_elem, integer_types):
                # Create instane of UIAElementInfo from a handle
                self._element = IUIA().iuia.ElementFromHandle(handle_or_elem)
            elif isinstance(handle_or_elem, IUIA().ui_automation_client.IUIAutomationElement):
                self._element = handle_or_elem
            else:
                raise TypeError("UIAElementInfo object can be initialized " + \
                                "with integer or IUIAutomationElement instance only!")
        else:
            self._element = IUIA().root

        self.set_cache_strategy(cached=cache_enable)

    def _get_current_class_name(self):
        """Return an actual class name of the element"""
        try:
            cn = self._element.CurrentClassName
            return text_type('') if cn is None else cn
        except COMError:
            return text_type('')  # probably element already doesn't exist

    def _get_cached_class_name(self):
        """Return a cached class name of the element"""
        if self._cached_class_name is None:
            self._cached_class_name = self._get_current_class_name()
        return self._cached_class_name

    def _get_current_handle(self):
        """Return an actual handle of the element"""
        try:
            return self._element.CurrentNativeWindowHandle
        except COMError:
            return None  # probably element already doesn't exist

    def _get_cached_handle(self):
        """Return a cached handle of the element"""
        if self._cached_handle is None:
            self._cached_handle = self._get_current_handle()
        return self._cached_handle

    def _get_current_control_type(self):
        """Return an actual control type of the element"""
        try:
            return IUIA().known_control_type_ids[self._element.CurrentControlType]
        except COMError:
            return None  # probably element already doesn't exist

    def _get_cached_control_type(self):
        """Return a cached control type of the element"""
        if self._cached_control_type is None:
            self._cached_control_type = self._get_current_control_type()
        return self._cached_control_type

    def _get_current_name(self):
        """Return an actual name of the element"""
        try:
            n = self._element.CurrentName
            return text_type('') if n is None else n
        except COMError:
            return text_type('')  # probably element already doesn't exist

    def _get_cached_name(self):
        """Return a cached name of the element"""
        if self._cached_name is None:
            self._cached_name = self._get_current_name()
        return self._cached_name

    def _get_current_visible(self):
        """Return an actual visible property of the element"""
        try:
            return bool(not self._element.CurrentIsOffscreen)
        except COMError:
            return False  # probably element already doesn't exist

    def _get_cached_visible(self):
        """Return a cached visible property of the element"""
        if self._cached_visible is None:
            self._cached_visible = self._get_current_visible()
        return self._cached_visible

    def _get_current_rich_text(self):
        """Return the actual rich_text of the element"""
        if not self.class_name:
            return self.name
        try:
            pattern = get_elem_interface(self._element, "Text")
            return pattern.DocumentRange.GetText(-1)
        except Exception:
            return self.name  # TODO: probably we should raise an exception here

    def _get_cached_rich_text(self):
        """Return the cached rich_text of the element"""
        if self._cached_rich_text is None:
            self._cached_rich_text = self._get_current_rich_text()
        return self._cached_rich_text

    def set_cache_strategy(self, cached=None):
        """Setup a cache strategy for frequently used attributes"""
        if cached is True:
            # Refresh cached attributes
            self._cached_class_name = None
            self._cached_handle = None
            self._cached_control_type = None
            self._cached_name = None
            self._cached_visible = None
            self._cached_rich_text = None

            # Switch to cached attributes
            self._get_class_name = self._get_cached_class_name
            self._get_handle = self._get_cached_handle
            self._get_control_type = self._get_cached_control_type
            self._get_name = self._get_cached_name
            self._get_visible = self._get_cached_visible
            self._get_rich_text = self._get_cached_rich_text
        else:
            # Switch to actual (non-cached) attributes
            self._get_class_name = self._get_current_class_name
            self._get_handle = self._get_current_handle
            self._get_control_type = self._get_current_control_type
            self._get_name = self._get_current_name
            self._get_visible = self._get_current_visible
            self._get_rich_text = self._get_current_rich_text

    @property
    def element(self):
        """Return AutomationElement's instance"""
        return self._element

    @property
    def automation_id(self):
        """Return AutomationId of the element"""
        try:
            return self._element.CurrentAutomationId
        except COMError:
            return None  # probably element already doesn't exist

    @property
    def control_id(self):
        """Return ControlId of the element if it has a handle"""
        if (self.handle):
            return controlid(self.handle)
        else:
            return None

    @property
    def process_id(self):
        """Return ProcessId of the element"""
        try:
            return self._element.CurrentProcessId
        except COMError:
            return None  # probably element already doesn't exist

    @property
    def framework_id(self):
        """Return FrameworkId of the element"""
        try:
            return self._element.CurrentFrameworkId
        except COMError:
            return None  # probably element already doesn't exist

    @property
    def runtime_id(self):
        """Return Runtime ID (hashable value but may be different from run to run)"""
        return self._element.GetRuntimeId()

    @property
    def name(self):
        """Return name of the element"""
        return self._get_name()

    @property
    def class_name(self):
        """Return class name of the element"""
        return self._get_class_name()

    @property
    def control_type(self):
        """Return control type of element"""
        return self._get_control_type()

    @property
    def handle(self):
        """Return handle of the element"""
        return self._get_handle()

    @property
    def parent(self):
        """Return parent of the element"""
        parent_elem = IUIA().iuia.ControlViewWalker.GetParentElement(self._element)
        if parent_elem:
            return UIAElementInfo(parent_elem)
        else:
            return None

    def _get_elements(self, tree_scope, cond=IUIA().true_condition, cache_enable=False):
        """Find all elements according to the given tree scope and conditions"""
        try:
            ptrs_array = self._element.FindAll(tree_scope, cond)
            return elements_from_uia_array(ptrs_array, cache_enable)
        except(COMError, ValueError):
            ActionLogger().log("COM error: can't get elements")
            return []

    def children(self, **kwargs):
        """Return a list of only immediate children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        cache_enable = kwargs.pop('cache_enable', False)
        cond = IUIA().build_condition(**kwargs)
        return self._get_elements(IUIA().tree_scope["children"], cond, cache_enable)

    def iter_children(self, **kwargs):
        """Return a generator of only immediate children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        cond = IUIA().build_condition(**kwargs)
        tree_walker = IUIA().iuia.CreateTreeWalker(cond)
        element = tree_walker.GetFirstChildElement(self._element)
        while element:
            yield UIAElementInfo(element)
            element = tree_walker.GetNextSiblingElement(element)

    def descendants(self, **kwargs):
        """Return a list of all descendant children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        cache_enable = kwargs.pop('cache_enable', False)
        depth = kwargs.pop('depth', None)
        cond = IUIA().build_condition(**kwargs)
        elements = self._get_elements(IUIA().tree_scope["descendants"], cond, cache_enable)

        elements = ElementInfo.filter_with_depth(elements, self, depth)

        return elements

    @property
    def visible(self):
        """Check if the element is visible"""
        return self._get_visible()

    @property
    def enabled(self):
        """Check if the element is enabled"""
        return bool(self._element.CurrentIsEnabled)

    @property
    def rectangle(self):
        """Return rectangle of the element"""
        bound_rect = self._element.CurrentBoundingRectangle
        rect = RECT()
        rect.left = bound_rect.left
        rect.top = bound_rect.top
        rect.right = bound_rect.right
        rect.bottom = bound_rect.bottom
        return rect

    def dump_window(self):
        """Dump window to a set of properties"""
        return dumpwindow(self.handle)

    @property
    def rich_text(self):
        """Return rich_text of the element"""
        return self._get_rich_text()

    def __eq__(self, other):
        """Check if 2 UIAElementInfo objects describe 1 actual element"""
        if not isinstance(other, UIAElementInfo):
            return False
        return bool(IUIA().iuia.CompareElements(self.element, other.element))
