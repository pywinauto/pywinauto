"""Implementation of the class to deal with an UI element of WPF via injected DLL"""
import json

from six import integer_types, text_type, string_types
from ctypes.wintypes import tagPOINT
import warnings

from pywinauto.handleprops import dumpwindow, controlid
from pywinauto.element_info import ElementInfo
from .application import Application
from .win32structures import RECT
from .injected.api import *

class WPFElementInfo(ElementInfo):
    re_props = ["class_name", "name", "auto_id", "control_type", "full_control_type", "value"]
    exact_only_props = ["handle", "pid", "control_id", "enabled", "visible", "rectangle", "framework_id", "runtime_id"]
    search_order = ["handle", "control_type", "class_name", "pid", "control_id", "visible", "enabled", "name",
                    "auto_id", "full_control_type", "rectangle", "framework_id",
                    "runtime_id", "value"]
    assert set(re_props + exact_only_props) == set(search_order)

    def __init__(self, elem_id=None, cache_enable=False, pid=None):
        """
        Create an instance of WPFElementInfo from an ID of the element (int or long).

        If elem_id is None create an instance for UI root element.
        """
        self._pid=pid
        if elem_id is not None:
            if isinstance(elem_id, integer_types):
                # Create instance of WPFElementInfo from a handle
                self._element = elem_id
            else:
                raise TypeError("WPFElementInfo object can be initialized " + \
                                "with integer instance only!")
        else:
            self._element = 0

        self.set_cache_strategy(cached=cache_enable)

    def set_cache_strategy(self, cached):
        pass

    @property
    def handle(self):
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetHandle', self._pid, element_id=self._element)
        return reply['value']

    @property
    def auto_id(self):
        """Return AutomationId of the element"""
        if self._element == 0:
            return ''
        return self.get_property('Name') or ''

    @property
    def name(self):
        if self._element == 0:
            return '--root--'
        reply = ConnectionManager().call_action('GetName', self._pid, element_id=self._element)
        return reply['value']

    @property
    def rich_text(self):
        if self.control_type=='Edit':
            return self.get_property('Text') or ''
        return self.name

    @property
    def control_id(self):
        return self._element

    @property
    def process_id(self):
        return self._pid

    pid = process_id

    @property
    def framework_id(self):
        return "WPF"

    @property
    def runtime_id(self):
        return self._element

    @property
    def class_name(self):
        if self._element == 0:
            return ''
        reply = ConnectionManager().call_action('GetTypeName', self._pid, element_id=self._element)
        return reply['value']

    @property
    def enabled(self):
        if self._element == 0:
            return True
        return self.get_property('IsEnabled') or False

    @property
    def visible(self):
        if self._element == 0:
            return True
        return self.get_property('IsVisible') or False

    @property
    def parent(self):
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetParent', self._pid, element_id=self._element)
        return WPFElementInfo(reply['value'], pid=self._pid)

    def children(self, **kwargs):
        return list(self.iter_children(**kwargs))

    @property
    def control_type(self):
        """Return control type of element"""
        if self._element == 0:
            return None
        reply = ConnectionManager().call_action('GetControlType', self._pid, element_id=self._element)
        return reply['value']

    def iter_children(self, **kwargs):
        if 'process' in kwargs:
            self._pid = kwargs['process']
        reply = ConnectionManager().call_action('GetChildren', self._pid, element_id=self._element)
        for elem in reply['elements']:
            yield WPFElementInfo(elem, pid=self._pid)

    def descendants(self, **kwargs):
        return list(self.iter_descendants(**kwargs))

    def iter_descendants(self, **kwargs):
        cache_enable = kwargs.pop('cache_enable', False)
        depth = kwargs.pop("depth", None)
        if not isinstance(depth, (integer_types, type(None))) or isinstance(depth, integer_types) and depth < 0:
            raise Exception("Depth must be an integer")

        if depth == 0:
            return
        for child in self.iter_children(**kwargs):
            yield child
            if depth is not None:
                kwargs["depth"] = depth - 1
            for c in child.iter_descendants(**kwargs):
                yield c

    @property
    def rectangle(self):
        rect = RECT()
        if self._element != 0:
            reply = ConnectionManager().call_action('GetRectangle', self._pid, element_id=self._element)
            rect.left = reply['value']['left']
            rect.right = reply['value']['right']
            rect.top = reply['value']['top']
            rect.bottom = reply['value']['bottom']
        return rect

    def dump_window(self):
        return dumpwindow(self.handle)

    def get_property(self, name, error_if_not_exists=False):
        try:
            reply = ConnectionManager().call_action('GetProperty', self._pid, element_id=self._element, name=name)
            return reply['value']
        except NotFoundError as e:
            if error_if_not_exists:
                raise e
        return None

    def __hash__(self):
        """Return a unique hash value based on the element's ID"""
        return hash(self._element)

    def __eq__(self, other):
        """Check if 2 WPFElementInfo objects describe 1 actual element"""
        if not isinstance(other, WPFElementInfo):
            return False
        return self._element == other._element

    def __ne__(self, other):
        """Check if 2 WPFElementInfo objects describe 2 different elements"""
        return not (self == other)

    @classmethod
    def get_active(cls, app_or_pid):
        """Return current active element"""
        if isinstance(app_or_pid, integer_types):
            pid = app_or_pid
        elif isinstance(handle_or_elem, Application):
            pid = app.process
        else:
            raise TypeError("UIAElementInfo object can be initialized " + \
                            "with integer or IUIAutomationElement instance only!")

        try:
            reply = ConnectionManager().call_action('GetFocusedElement', pid)
            if reply['value'] > 0:
                return cls(reply['value'], pid=pid)
            else:
                return None
        except UnsupportedActionError:
            return None