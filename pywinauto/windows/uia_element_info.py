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
from ctypes.wintypes import tagPOINT
import warnings

from .uia_defines import IUIA, property_condition_flags, property_ids
from .uia_defines import get_elem_interface, NoPatternInterfaceError

from pywinauto.handleprops import dumpwindow, controlid
from pywinauto.element_info import ElementInfo
from .win32structures import RECT


class UIACondition(object):
    """Helper for filtering when searching for elements in the UI Automation tree"""
    def __init__(self, condition):
        if not isinstance(condition, IUIA().UIA_dll.IUIAutomationCondition):
            # IUIAutomation*Condition.GetChild(ren) could be returned (sequence of) IUnknown
            condition = condition.QueryInterface(IUIA().UIA_dll.IUIAutomationCondition)
        self._condition = condition

    @property
    def condition(self):
        """Return the pointer of IUIAutomationCondition"""
        return self._condition

    @property
    def condition_ex(self):
        """Return the pointer of IUIAutomationCondition inheritance"""
        cond = self._condition
        try:
            return cond.QueryInterface(IUIA().UIA_dll.IUIAutomationAndCondition)
        except COMError:
            pass
        try:
            return cond.QueryInterface(IUIA().UIA_dll.IUIAutomationOrCondition)
        except COMError:
            pass
        try:
            return cond.QueryInterface(IUIA().UIA_dll.IUIAutomationNotCondition)
        except COMError:
            pass
        try:
            return cond.QueryInterface(IUIA().UIA_dll.IUIAutomationPropertyCondition)
        except COMError:
            pass
        try:
            return cond.QueryInterface(IUIA().UIA_dll.IUIAutomationBoolCondition)
        except COMError:
            raise TypeError

    @classmethod
    def create_property(cls, propid, value, flags=None):
        """Create a condition filtering by property, value and optional flags"""
        if isinstance(propid, string_types):
            propid = property_ids[propid]
        elif not isinstance(propid, integer_types):
            raise TypeError('propid must be string or integer')
        if isinstance(flags, string_types):
            flags = property_condition_flags[flags]
        elif not isinstance(flags, (integer_types, type(None))):
            raise TypeError('flags must be string, integer or None')
        if flags is None:
            cond = IUIA().iuia.CreatePropertyCondition(propid, value)
        else:
            cond = IUIA().iuia.CreatePropertyConditionEx(propid, value, flags)
        return cls(cond)

    @classmethod
    def create_control_type(cls, value):
        """Create a condition filtering by control type"""
        if isinstance(value, string_types):
            value = IUIA().known_control_types[value]
        elif not isinstance(value, integer_types):
            raise TypeError('control_type must be string or integer')
        return cls.create_property('ControlType', value)

    @classmethod
    def create_bool(cls, value):
        """Create a condition filtering by boolean value"""
        if value:
            return cls(IUIA().true_condition)
        return cls(IUIA().false_condition)

    @classmethod
    def from_array(cls, operator_type, condition_array):
        """Create a condition from array"""
        if operator_type == "and":
            return cls(IUIA().iuia.CreateAndConditionFromArray([c.condition for c in condition_array]))
        elif operator_type == "or":
            return cls(IUIA().iuia.CreateOrConditionFromArray([c.condition for c in condition_array]))
        raise TypeError("operator_type must be 'and' or 'or'")

    def __and__(self, other):
        cond = IUIA().iuia.CreateAndCondition(self._condition, other.condition)
        return type(self)(cond)

    def __iand__(self, other):
        # type: (UIACondition) -> UIACondition
        return self & other

    def __or__(self, other):
        cond = IUIA().iuia.CreateOrCondition(self._condition, other.condition)
        return type(self)(cond)

    def __ior__(self, other):
        # type: (UIACondition) -> UIACondition
        return self | other

    def __invert__(self):
        cond = IUIA().iuia.CreateNotCondition(self._condition)
        return type(self)(cond)


def elements_from_uia_array(ptrs, cache_enable=False):
    """Build a list of UIAElementInfo elements from IUIAutomationElementArray"""
    elements = []
    for n in range(ptrs.Length):
        try:
            elements.append(UIAElementInfo(ptrs.GetElement(n), cache_enable))
        except COMError:
            continue
    return elements


def is_element_satisfying_criteria(element, process=None, class_name=None, name=None, control_type=None,
                                   content_only=None, **kwargs):
    """Check if element satisfies filter criteria"""
    is_appropriate_control_type = True
    if control_type:
        if isinstance(control_type, str):
            is_appropriate_control_type = element.CurrentControlType == IUIA().known_control_types[control_type]
        elif not isinstance(control_type, int):
            raise TypeError('control_type must be string or integer')
        else:
            is_appropriate_control_type = element.CurrentControlType == control_type

    def is_none_or_equals(criteria, prop):
        return criteria is None or prop == criteria

    return is_none_or_equals(process, element.CurrentProcessId) \
        and is_none_or_equals(class_name, element.CurrentClassName) \
        and is_none_or_equals(name, element.CurrentName) \
        and is_appropriate_control_type \
        and (content_only is None or isinstance(content_only, bool) and element.CurrentIsContentElement == content_only)


class UIAElementInfo(ElementInfo):
    """UI element wrapper for IUIAutomation API"""

    re_props = ["class_name", "name", "auto_id", "control_type", "full_control_type", "access_key", "accelerator",
                "value", "legacy_action", "legacy_descr", "legacy_help", "legacy_name", "legacy_shortcut",
                "legacy_value"]
    exact_only_props = ["handle", "pid", "control_id", "enabled", "visible", "rectangle", "framework_id", "runtime_id"]
    search_order = ["handle", "control_type", "class_name", "pid", "control_id", "visible", "enabled", "name",
                    "access_key", "accelerator", "auto_id", "full_control_type", "rectangle", "framework_id",
                    "runtime_id", "value", "legacy_action", "legacy_descr", "legacy_help", "legacy_name",
                    "legacy_shortcut", "legacy_value"]
    assert set(re_props + exact_only_props) == set(search_order)

    renamed_props = {
        "title": ("name", None),
        "title_re": ("name_re", None),
        "process": ("pid", None),
        "visible_only": ("visible", {True: True, False: None}),
        "enabled_only": ("enabled", {True: True, False: None}),
        "top_level_only": ("depth", {True: 1, False: None}),
    }

    use_raw_view_walker = False
    """Enable/disable RawViewWalker-based implementation (can find more elements in some cases, but slow)"""

    def __init__(self, handle_or_elem=None, cache_enable=False):
        """
        Create an instance of UIAElementInfo from a handle (int or long)
        or from an IUIAutomationElement.

        If handle_or_elem is None create an instance for UI root element.
        """
        if handle_or_elem is not None:
            if isinstance(handle_or_elem, int):
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
            return "" if cn is None else cn
        except COMError:
            return ""  # probably element already doesn't exist

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
            return "" if n is None else n
        except COMError:
            return ""  # probably element already doesn't exist

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
    def auto_id(self):
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

    pid = process_id

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
        try:
            return self._element.GetRuntimeId()
        except COMError:
            return 0

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
    def access_key(self):
        """Return access key for the element. Most preferred way to get keyboard shortcut"""
        try:
            val = self._element.CurrentAccessKey
            return "" if val is None else val
        except COMError:
            # probably element already doesn't exist
            return ""

    @property
    def accelerator(self):
        """Return accelerator key for the element (try to use access_key property in case of empty value) """
        try:
            val = self._element.CurrentAcceleratorKey
            return "" if val is None else val
        except COMError:
            # probably element already doesn't exist
            return ""

    @property
    def value(self):
        """Return value of the element from ValuePattern (in order to search elements by this property)"""
        try:
            val = get_elem_interface(self._element, "Value").CurrentValue
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            # COMError also can be raised in case of attempt to get value of password EditBox
            return ""

    @property
    def legacy_action(self):
        """Return DefaultAction value of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentDefaultAction
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def legacy_descr(self):
        """Return description of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentDescription
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def legacy_help(self):
        """Return help string of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentHelp
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def legacy_name(self):
        """Return name of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentName
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def legacy_shortcut(self):
        """Return keyboard shortcut of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentKeyboardShortcut
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def legacy_value(self):
        """Return value of the element from LegacyIAccessible pattern"""
        try:
            val = get_elem_interface(self._element, "LegacyIAccessible").CurrentValue
            return "" if val is None else val
        except (NoPatternInterfaceError, COMError):
            return ""

    @property
    def parent(self):
        """Return parent of the element"""
        return UIATreeWalker("control").get_parent(self)

    def _get_elements(self, tree_scope, cond=IUIA().true_condition, cache_enable=False):
        """Find all elements according to the given tree scope and conditions"""
        try:
            ptrs_array = self._element.FindAll(tree_scope, cond)
            return elements_from_uia_array(ptrs_array, cache_enable)
        except(COMError, ValueError) as e:
            warnings.warn("Can't get elements due to COM error: {}. "
                          "Try to set pywinauto.windows.uia_element_info.UIAElementInfo.use_raw_view_walker = True".format(e), RuntimeWarning)
            return []

    def _iter_children_raw(self):
        """Return a generator of only immediate children of the element"""
        try:
            element = IUIA().raw_tree_walker.GetFirstChildElement(self._element)
            while element:
                yield element
                element = IUIA().raw_tree_walker.GetNextSiblingElement(element)
        except (COMError, ValueError) as e:
            warnings.warn("Can't get descendant elements due to error: {}".format(e), RuntimeWarning)

    def iter_children(self, **kwargs):
        """Return a generator of only immediate children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        cache_enable = kwargs.pop('cache_enable', False)
        if UIAElementInfo.use_raw_view_walker:
            for element in self._iter_children_raw():
                if is_element_satisfying_criteria(element, **kwargs):
                    yield UIAElementInfo(element, cache_enable)
        else:
            cond = IUIA().build_condition(**kwargs)
            tree_walker = IUIA().iuia.CreateTreeWalker(cond)
            element = tree_walker.GetFirstChildElement(self._element)
            while element:
                yield UIAElementInfo(element)
                element = tree_walker.GetNextSiblingElement(element)

    def iter_descendants(self, **kwargs):
        """Iterate over descendants of the element"""
        cache_enable = kwargs.pop('cache_enable', False)
        depth = kwargs.pop("depth", None)
        if not isinstance(depth, (int, type(None))) or isinstance(depth, int) and depth < 0:
            raise Exception("Depth must be an integer")

        if depth == 0:
            return
        if UIAElementInfo.use_raw_view_walker:
            for child in self._iter_children_raw():
                if is_element_satisfying_criteria(child, **kwargs):
                    yield UIAElementInfo(child, cache_enable)
                if depth is not None:
                    kwargs["depth"] = depth - 1
                for c in UIAElementInfo(child, cache_enable).iter_descendants(**kwargs):
                    if is_element_satisfying_criteria(c._element, **kwargs):
                        yield c
        else:
            for child in self.iter_children(**kwargs):
                yield child
                if depth is not None:
                    kwargs["depth"] = depth - 1
                for c in child.iter_descendants(**kwargs):
                    yield c

    def children(self, **kwargs):
        """Return a list of only immediate children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or name.
        """
        if UIAElementInfo.use_raw_view_walker:
            return list(self.iter_children(**kwargs))
        else:
            cache_enable = kwargs.pop('cache_enable', False)
            cond = IUIA().build_condition(**kwargs)
            return self._get_elements(IUIA().tree_scope["children"], cond, cache_enable)

    def descendants(self, **kwargs):
        """Return a list of all descendant children of the element

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or name.
        """
        if UIAElementInfo.use_raw_view_walker:
            return list(self.iter_descendants(**kwargs))
        else:
            cache_enable = kwargs.pop('cache_enable', False)
            depth = kwargs.pop('depth', None)
            if depth is None:
                cond = IUIA().build_condition(**kwargs)
                return self._get_elements(IUIA().tree_scope["descendants"], cond, cache_enable)
            if depth == 1:
                return self.children(cache_enable=cache_enable, **kwargs)
            else:
                if kwargs:
                    cond = IUIA().build_condition(**kwargs)
                    elements = self._get_elements(IUIA().tree_scope["descendants"], cond, cache_enable)
                    return ElementInfo.filter_with_depth(elements, self, depth)
                else:
                    descendants = []

                    def walk_the_tree(parent, depth_):
                        # type: (UIAElementInfo, int) -> None
                        if depth_ == 0:
                            return
                        for child in parent.children(cache_enable=cache_enable):
                            descendants.append(child)
                            walk_the_tree(child, depth_ - 1)

                    walk_the_tree(self, depth)
                    return descendants

    @property
    def visible(self):
        """Check if the element is visible"""
        return self._get_visible()

    @property
    def enabled(self):
        """Check if the element is enabled"""
        try:
            return bool(self._element.CurrentIsEnabled)
        except COMError:
            return False

    @property
    def rectangle(self):
        """Return rectangle of the element"""
        rect = RECT()
        try:
            bound_rect = self._element.CurrentBoundingRectangle
            rect.left = bound_rect.left
            rect.top = bound_rect.top
            rect.right = bound_rect.right
            rect.bottom = bound_rect.bottom
        except COMError:
            pass
        return rect

    def dump_window(self):
        """Dump window to a set of properties"""
        return dumpwindow(self.handle)

    @classmethod
    def from_point(cls, x, y):
        """Return child element at specified point coordinates"""
        return cls(IUIA().iuia.ElementFromPoint(tagPOINT(x, y)))

    @classmethod
    def top_from_point(cls, x, y):
        """Return top level element at specified point coordinates"""
        current_elem = cls.from_point(x, y)
        current_parent = current_elem.parent
        while current_parent is not None and current_parent != cls():
            current_elem = current_parent
            current_parent = current_elem.parent
        return current_elem

    @property
    def rich_text(self):
        """Return rich_text of the element"""
        return self._get_rich_text()

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value based on the element's Runtime ID"""
        return hash(self.runtime_id)

    def __eq__(self, other):
        """Check if 2 UIAElementInfo objects describe 1 actual element"""
        if not isinstance(other, UIAElementInfo):
            return False
        return bool(IUIA().iuia.CompareElements(self.element, other.element))

    def __ne__(self, other):
        """Check if 2 UIAElementInfo objects describe 2 different elements"""
        return not (self == other)

    @classmethod
    def get_active(cls):
        """Return current active element"""
        ae = IUIA().get_focused_element()
        return cls(ae)


class _UIAChildrenTree(object):
    def __init__(self, walker, element, cache_enable):
        self._walker = walker
        self._element = element
        self._cache_enable = cache_enable

    def __iter__(self):
        try:
            elem = self._walker.GetFirstChildElement(self._element)
            while elem:
                yield UIAElementInfo(elem, self._cache_enable)
                elem = self._walker.GetNextSiblingElement(elem)
        except (COMError, ValueError) as e:
            warnings.warn("Can't get elements due to error: {}".format(e), RuntimeWarning)

    def __reversed__(self):
        try:
            elem = self._walker.GetLastChildElement(self._element)
            while elem:
                yield UIAElementInfo(elem, self._cache_enable)
                elem = self._walker.GetPreviousSiblingElement(elem)
        except (COMError, ValueError) as e:
            warnings.warn("Can't get elements due to error: {}".format(e), RuntimeWarning)


class UIATreeWalker(object):
    """UI tree walker wrapper for IUIAutomation API"""
    def __init__(self, condition, cache_enable=False):
        """
        Create an instance of UIATreeWalker.

        * **condition** is either a valid UIACondition or literal string('raw', 'content', 'control')
        * **cache_enable** is optional for caching of UIA elements attributes during walk.
        """
        if isinstance(condition, UIACondition):
            self._walker = IUIA().iuia.CreateTreeWalker(condition.condition)
        elif condition == "raw":
            self._walker = IUIA().raw_tree_walker
        elif condition == "content":
            self._walker = IUIA().content_tree_walker
        elif condition == "control":
            self._walker = IUIA().control_tree_walker
        else:
            raise TypeError
        self._cache_enable = cache_enable

    @property
    def walker(self):
        """Return TreeWalker's instance"""
        return self._walker

    @property
    def condition(self):
        """Return condition of walker"""
        return UIACondition(self._walker.condition)

    def walk(self, element):
        """Iterate over children of the element satisfying the condition"""
        return _UIAChildrenTree(self._walker, element.element, self._cache_enable)

    def get_parent(self, element):
        """Return parent of the element satisfying the condition"""
        elem = self._walker.GetParentElement(element.element)
        if elem:
            return UIAElementInfo(elem, self._cache_enable)
        return None
