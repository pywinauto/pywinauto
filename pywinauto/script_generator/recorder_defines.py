import time

from abc import ABCMeta

# TODO: pack this constants into Enum?
EVENT_ASYNC_CONTENT_LOADED = "AsyncContentLoaded"
EVENT_DRAG_CANCEL = "DragCancel"
EVENT_DRAG_COMPLETE = "DragComplete"
EVENT_DRAG_DROPPED = "DragDropped"
EVENT_DRAG_ENTER = "DragEnter"
EVENT_DRAG_LEAVE = "DragLeave"
EVENT_DRAG_START = "DragStart"
EVENT_EDIT_CONVERSION_TARGET_CHANGED = "EditConversionTargetChanged"
EVENT_EDIT_TEXT_CHANGED = "EditTextChanged"
EVENT_FOCUS_CHANGED = "FocusChanged"
EVENT_HOSTED_FRAGMENT_ROOTS_INVALIDATED = "HostedFragmentRootsInvalidated"
EVENT_INPUT_DISCARDED = "InputDiscarded"
EVENT_INPUT_REACHED_OTHER_ELEMENT = "InputReachedOtherElement"
EVENT_INPUT_REACHED_TARGET = "InputReachedTarget"
EVENT_INVOKED = "Invoked"
EVENT_LAYOUT_INVALIDATED = "LayoutInvalidated"
EVENT_LIVE_REGION_CHANGED = "LiveRegionChanged"
EVENT_MENU_CLOSED = "MenuClosed"
EVENT_MENU_END = "MenuEnd"
EVENT_MENU_OPENED = "MenuOpened"
EVENT_MENU_START = "MenuStart"
EVENT_PROPERTY_CHANGED = "PropertyChanged"
EVENT_SELECTION_ELEMENT_ADDED = "SelectionElementAdded"
EVENT_SELECTION_ELEMENT_REMOVED = "SelectionElementRemoved"
EVENT_SELECTION_ELEMENT_SELECTED = "SelectionElementSelected"
EVENT_SELECTION_INVALIDATED = "SelectionInvalidated"
EVENT_STRUCTURE_CHANGED = "StructureChanged"
EVENT_SYSTEM_ALERT = "SystemAlert"
EVENT_TEXT_CHANGED = "TextChanged"
EVENT_TEXT_SELECTION_CHANGED = "TextSelectionChanged"
EVENT_TOOLTIP_CLOSED = "ToolTipClosed"
EVENT_TOOLTIP_OPENED = "ToolTipOpened"
EVENT_WINDOW_CLOSED = "WindowClosed"
EVENT_WINDOW_OPENED = "WindowOpened"


# RecorderEvent
# -- HookEvent
# -- -- RecorderMouseEvent
# -- -- RecorderKeyboardEvent
# -- ApplicationEvent

class RecorderEvent(object):
    __metaclass__ = ABCMeta

    def __call__(self, *args, **kwargs):
        self.timestamp = time.time()
        self.control_tree_node = None  # event sender

    def __str__(self):
        return self.__repr__()


class HookEvent(RecorderEvent):
    pass


class RecorderMouseEvent(HookEvent):
    def __init__(self, current_key=None, event_type=None, mouse_x=0, mouse_y=0):
        super(RecorderMouseEvent, self).__init__()
        self.current_key = current_key
        self.event_type = event_type
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def __repr__(self):
        if self.control_tree_node:
            elem = " - {}".format(self.control_tree_node)
        else:
            elem = ""
        description = "<RecorderMouseEvent - '{}' - '{}' at ({}, {}){}>".format(self.current_key, self.event_type,
                                                                                self.mouse_x, self.mouse_y, elem)
        return description


class RecorderKeyboardEvent(HookEvent):
    def __init__(self, current_key=None, event_type=None, pressed_key=None):
        super(RecorderKeyboardEvent, self).__init__()
        self.current_key = current_key
        self.event_type = event_type
        self.pressed_key = pressed_key

    def __repr__(self):
        description = "<RecorderKeyboardEvent - '{}' - '{}', pressed = {}>".format(self.current_key, self.event_type,
                                                                                   self.pressed_key)
        return description


class ApplicationEvent(RecorderEvent):
    def __init__(self, name, sender):
        super(ApplicationEvent, self).__init__()
        self.name = name
        self.sender = sender

    def __repr__(self):
        description = "<ApplicationEvent - '{}' from '{}'>".format(self.name, self.sender)
        return description
