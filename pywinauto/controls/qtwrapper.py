# -*- coding: utf-8 -*-
"""Basic wrapping of Qt elements."""

from __future__ import unicode_literals

from .. import backend
from ..base_wrapper import BaseMeta
from .win_base_wrapper import WinBaseWrapper


class QtMeta(BaseMeta):

    """Metaclass for Qt wrapper objects."""

    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types."""
        BaseMeta.__init__(cls, name, bases, attrs)

        for control_type in cls._control_types:
            QtMeta.control_type_to_cls[control_type] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the most specific wrapper for this Qt element."""
        return QtMeta.control_type_to_cls.get(element.control_type, QtWrapper)


class QtWrapper(WinBaseWrapper, metaclass=QtMeta):

    """Default wrapper for Qt controls."""

    _control_types = []

    def __new__(cls, element_info):
        """Construct a Qt control wrapper."""
        return super(QtWrapper, cls)._create_wrapper(cls, element_info, QtWrapper)

    def __init__(self, element_info):
        """Initialize the control."""
        WinBaseWrapper.__init__(self, element_info, backend.registry.backends['qt'])

    def friendly_class_name(self):
        """Return a pywinauto-friendly class name."""
        return self.element_info.control_type or self.element_info.class_name or 'Pane'

    def get_native_property(self, name, error_if_not_exists=False):
        """Return a native Qt property value."""
        return self.element_info.get_native_property(name, error_if_not_exists)

    def set_native_property(self, name, value):
        """Set a native Qt property value."""
        self.element_info.set_native_property(name, value)
        return self

    def invoke_method(self, name):
        """Invoke a no-argument Qt method."""
        self.element_info.invoke_method(name)
        return self

    def click(self):
        """Perform a semantic click."""
        self.verify_actionable()
        self.element_info.click()
        return self

    def set_focus(self):
        """Set keyboard focus to this element."""
        self.element_info.set_focus()
        return self

    def has_keyboard_focus(self):
        """Return whether this element has keyboard focus."""
        return bool(self.get_native_property('hasFocus'))

    def is_keyboard_focusable(self):
        """Return whether this element can accept keyboard focus."""
        return bool(self.get_native_property('focusPolicy'))

    def get_active(self):
        """Return wrapper object for current focused Qt element."""
        element_info = self.backend.element_info_class.get_active(self.element_info.pid)
        if element_info is None:
            return None
        return self.backend.generic_wrapper_class(element_info)

    def is_active(self):
        """Return whether this element is in the active top-level window."""
        focused_wrap = self.get_active()
        if focused_wrap is None:
            return False
        return focused_wrap.top_level_parent() == self.top_level_parent()

    def children_texts(self):
        """Return text of immediate children."""
        return [child.window_text() for child in self.children()]

    def get_value(self):
        """Return a value-like representation when the Qt object exposes one."""
        return self.element_info.value

    def set_value(self, value):
        """Set a value-like representation when the Qt object supports it."""
        self.element_info.set_value(value)
        return self

    def select(self):
        """Select this element if it supports selection."""
        self.element_info.select()
        return self

    def is_selected(self):
        """Return selected state when available."""
        return bool(self.get_native_property('selected'))
