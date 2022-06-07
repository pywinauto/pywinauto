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

"""Implementation of the class to deal with an UI element of WPF via injected managed DLL/assembly."""
from six import integer_types, string_types

from pywinauto.handleprops import dumpwindow
from pywinauto.element_info import ElementInfo
from .win32structures import RECT
from .injected.api import ConnectionManager, InjectedNotFoundError, InjectedUnsupportedActionError


def is_element_satisfying_criteria(element, process=None, class_name=None, name=None, control_type=None,
                                   **kwargs):
    """Check if element satisfies filter criteria."""
    is_appropriate_control_type = True
    if control_type:
        if isinstance(control_type, string_types):
            is_appropriate_control_type = element.control_type == control_type
        else:
            raise TypeError('control_type must be string')

    def is_none_or_equals(criteria, prop):
        return criteria is None or prop == criteria

    return is_none_or_equals(process, element.process_id) \
        and is_none_or_equals(class_name, element.class_name) \
        and is_none_or_equals(name, element.name) \
        and is_appropriate_control_type


class WPFElementInfo(ElementInfo):

    """Class to get information about WPF UI element in the specified process."""

    re_props = ["class_name", "name", "auto_id", "control_type", "full_control_type", "value"]
    exact_only_props = ["handle", "pid", "control_id", "enabled", "visible", "rectangle", "framework_id", "runtime_id"]
    search_order = ["handle", "control_type", "class_name", "pid", "control_id", "visible", "enabled", "name",
                    "auto_id", "full_control_type", "rectangle", "framework_id",
                    "runtime_id", "value"]
    assert set(re_props + exact_only_props) == set(search_order)

    def __init__(self, elem_id=None, cache_enable=False, pid=None):
        """Create an instance of WPFElementInfo from an ID of the element (int or long).

        If elem_id is None create an instance for UI root element.
        """
        self._pid = pid
        if elem_id is not None:
            if isinstance(elem_id, integer_types):
                # Create instance of WPFElementInfo from a handle
                self._element = elem_id
            else:
                raise TypeError("WPFElementInfo object can be initialized "
                                "with integer instance only!")
        else:
            self._element = 0

        self.set_cache_strategy(cached=cache_enable)

    def set_cache_strategy(self, cached):
        pass

    @property
    def handle(self):
        """Return handle of the element."""
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetHandle', self._pid, element_id=self._element)
        return reply['value']

    @property
    def auto_id(self):
        """Return AutomationId of the element."""
        if self._element == 0:
            return ''
        return self.get_native_property('Name') or ''

    @property
    def name(self):
        """Return name of the element."""
        if self._element == 0:
            return '--root--'
        reply = ConnectionManager().call_action('GetName', self._pid, element_id=self._element)
        return reply['value']

    @property
    def rich_text(self):
        """Return rich_text of the element."""
        if self.control_type == 'Edit':
            return self.get_native_property('Text') or ''
        return self.name

    @property
    def value(self):
        """Return value of the element (in order to search elements by this property).

        Only specified element types (like Edit) are supported.
        Use :py:meth:`get_native_property` to get value of the property with the specified name."""
        if self.control_type == 'Edit':
            return self.get_native_property('Text') or self.get_native_property('Password') or ''
        return ''

    @property
    def control_id(self):
        """Return element ID (may be different from run to run)."""
        return self._element

    @property
    def process_id(self):
        """Return process ID of the element."""
        return self._pid

    pid = process_id

    @property
    def framework_id(self):
        """Return framework ID of the element (always is 'WPF', for compatibility with UIA)."""
        return "WPF"

    @property
    def runtime_id(self):
        """Return element ID (may be different from run to run)."""
        return self._element

    @property
    def class_name(self):
        """Return class name of the element."""
        if self._element == 0:
            return ''
        reply = ConnectionManager().call_action('GetTypeName', self._pid, element_id=self._element)
        return reply['value']

    @property
    def enabled(self):
        """Check if the element is enabled."""
        if self._element == 0:
            return True
        return self.get_native_property('IsEnabled') or False

    @property
    def visible(self):
        """Check if the element is visible."""
        if self._element == 0:
            return True
        return self.get_native_property('IsVisible') or False

    @property
    def parent(self):
        """Return parent of the element."""
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetParent', self._pid, element_id=self._element)
        return WPFElementInfo(reply['value'], pid=self._pid)

    def children(self, **kwargs):
        """Return a list of only immediate children of the element.

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        return list(self.iter_children(**kwargs))

    @property
    def control_type(self):
        """Return control type of element."""
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetControlType', self._pid, element_id=self._element)
        return reply['value']

    def iter_children(self, **kwargs):
        """Return a generator of only immediate children of the element.

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        if 'process' in kwargs and self._pid is None:
            self._pid = kwargs['process']
        reply = ConnectionManager().call_action('GetChildren', self._pid, element_id=self._element)
        for elem_id in reply['elements']:
            element = WPFElementInfo(elem_id, pid=self._pid)
            if is_element_satisfying_criteria(element, **kwargs):
                yield element

    def descendants(self, **kwargs):
        """Return a list of all descendant children of the element.

         * **kwargs** is a criteria to reduce a list by process,
           class_name, control_type, content_only and/or title.
        """
        return list(self.iter_descendants(**kwargs))

    def iter_descendants(self, **kwargs):
        """Iterate over descendants of the element."""
        # TODO implement cache support
        # cache_enable = kwargs.pop('cache_enable', False)
        depth = kwargs.pop("depth", None)
        process = kwargs.pop("process", None)
        if not isinstance(depth, (integer_types, type(None))) or isinstance(depth, integer_types) and depth < 0:
            raise Exception("Depth must be an integer")

        if depth == 0:
            return
        for child in self.iter_children(process=process):
            if is_element_satisfying_criteria(child, **kwargs):
                yield child
            if depth is not None:
                kwargs["depth"] = depth - 1
            for c in child.iter_descendants(**kwargs):
                if is_element_satisfying_criteria(c, **kwargs):
                    yield c

    @property
    def rectangle(self):
        """Return rectangle of the element."""
        rect = RECT()
        if self._element != 0:
            reply = ConnectionManager().call_action('GetRectangle', self._pid, element_id=self._element)
            rect.left = reply['value']['left']
            rect.right = reply['value']['right']
            rect.top = reply['value']['top']
            rect.bottom = reply['value']['bottom']
        return rect

    def dump_window(self):
        """Dump window to a set of properties."""
        return dumpwindow(self.handle)

    def get_native_property(self, name, error_if_not_exists=False):
        """Return value of the specified property of the .NET object corresponding to the element."""
        try:
            reply = ConnectionManager().call_action('GetProperty', self._pid, element_id=self._element, name=name)
            return reply['value']
        except InjectedNotFoundError as e:
            if error_if_not_exists:
                raise e
        return None

    def get_native_properties(self):
        """Return a dict with names and types of available properties of
        the .NET object corresponding to the element."""
        reply = ConnectionManager().call_action('GetProperties', self._pid, element_id=self._element)
        return reply['value']

    def __hash__(self):
        """Return a unique hash value based on the element's ID."""
        return hash(self._element)

    def __eq__(self, other):
        """Check if 2 WPFElementInfo objects describe 1 actual element."""
        if not isinstance(other, WPFElementInfo):
            return False
        return self._element == other._element

    def __ne__(self, other):
        """Check if 2 WPFElementInfo objects describe 2 different elements."""
        return not (self == other)

    @classmethod
    def get_active(cls, app_or_pid):
        """Return current active element."""
        from .application import Application

        if isinstance(app_or_pid, integer_types):
            pid = app_or_pid
        elif isinstance(app_or_pid, Application):
            pid = app_or_pid.process
        else:
            raise TypeError("WPFElementInfo object can be initialized "
                            "with integer or Application instance only!")

        try:
            reply = ConnectionManager().call_action('GetFocusedElement', pid)
            if reply['value'] > 0:
                return cls(reply['value'], pid=pid)
            else:
                return None
        except InjectedUnsupportedActionError:
            return None
