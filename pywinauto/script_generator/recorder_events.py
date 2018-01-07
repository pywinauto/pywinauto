from abc import ABCMeta

from .. import win32_hooks

from .recorder_defines import PROPERTY_EVENT_NAME, FOCUS_EVENT_NAME, STRUCTURE_EVENT_NAME


# RecorderEvent
# -- RecorderMouseEvent (from module Hooks)
# -- RecorderKeyboardEvent (from module Hooks)
# -- UIAEvent
# -- -- PropertyEvent
# -- -- FocusEvent
# -- -- StructureEvent


class RecorderEvent(object):
    __metaclass__ = ABCMeta


class RecorderMouseEvent(RecorderEvent, win32_hooks.MouseEvent):
    def __init__(self, current_key=None, event_type=None, mouse_x=0, mouse_y=0):
        super(RecorderMouseEvent, self).__init__(current_key, event_type, mouse_x, mouse_y)
        self.control_tree_node = None

    def __str__(self):
        description = "<RecorderMouseEvent - '{}' - '{}' at ({}, {})>".format(self.current_key, self.event_type,
                                                                              self.mouse_x, self.mouse_y)
        return description


class RecorderKeyboardEvent(RecorderEvent, win32_hooks.KeyboardEvent):
    def __str__(self):
        description = "<RecorderKeyboardEvent - '{}' - '{}' to '{}'>".format(self.current_key, self.event_type,
                                                                             self.pressed_key)
        return description


class UIAEvent(RecorderEvent):
    def __init__(self, event_name, sender):
        self.event_name = event_name
        self.sender = sender

    def __str__(self):
        description = "<UIAEvent - {} from {} ({}, {})>".format(self.event_name, self.sender,
                                                                self.sender.CachedClassName, self.sender.CachedName)
        return description


class PropertyEvent(UIAEvent):
    def __init__(self, sender, property_name, new_value):
        super(PropertyEvent, self).__init__(PROPERTY_EVENT_NAME, sender)
        self.property_name = property_name
        self.new_value = new_value

    def __str__(self):
        description = "<PropertyEvent - Change '{}' to '{}' from {} ({}, {})>".format(self.property_name,
                                                                                      self.new_value, self.sender,
                                                                                      self.sender.CachedClassName,
                                                                                      self.sender.CachedName)
        return description


class FocusEvent(UIAEvent):
    def __init__(self, sender):
        super(FocusEvent, self).__init__(FOCUS_EVENT_NAME, sender)

    def __str__(self):
        description = "<FocusEvent - Change focus to {} ({}, {})>".format(self.sender, self.sender.CachedClassName,
                                                                          self.sender.CachedName)
        return description


class StructureEvent(UIAEvent):
    def __init__(self, sender, change_type, runtime_id):
        super(StructureEvent, self).__init__(STRUCTURE_EVENT_NAME, sender)
        self.change_type = change_type
        self.runtime_id = runtime_id

    def __str__(self):
        description = "<StructureEvent - '{}' from {} ({}, {})>".format(self.change_type, self.sender,
                                                                        self.sender.CachedClassName,
                                                                        self.sender.CachedName)
        return description
