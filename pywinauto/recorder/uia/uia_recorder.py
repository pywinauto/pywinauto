from comtypes import COMObject, COMError

from ... import win32_hooks
from ...win32structures import POINT
from ...uia_element_info import UIAElementInfo

from ..control_tree import ControlTree
from ..recorder import Recorder
from .uia_recorder_defines import *

_ignored_events = [
    # Events which are handled by separate handlers
    IUIA().known_events_ids[IUIA().UIA_dll.UIA_AutomationPropertyChangedEventId],  # AutomationPropertyChanged
    IUIA().known_events_ids[IUIA().UIA_dll.UIA_AutomationFocusChangedEventId],  # AutomationFocusChanged
    IUIA().known_events_ids[IUIA().UIA_dll.UIA_StructureChangedEventId],  # StructureChanged

    # Events which produce a lot of noise in output

    # Other unwanted events
]

_ignored_properties_ids = [
    # Properties that create too much noise in output
    IUIA().UIA_dll.UIA_BoundingRectanglePropertyId,
    IUIA().UIA_dll.UIA_IsEnabledPropertyId,
    IUIA().UIA_dll.UIA_IsOffscreenPropertyId,
    IUIA().UIA_dll.UIA_ItemStatusPropertyId,
    IUIA().UIA_dll.UIA_NamePropertyId,
    IUIA().UIA_dll.UIA_WindowWindowInteractionStatePropertyId,

    # Other unwanted properties
]

_cached_properties = [
    IUIA().UIA_dll.UIA_FrameworkIdPropertyId,
    IUIA().UIA_dll.UIA_AutomationIdPropertyId,
    IUIA().UIA_dll.UIA_ClassNamePropertyId,
    IUIA().UIA_dll.UIA_ControlTypePropertyId,
    IUIA().UIA_dll.UIA_ProviderDescriptionPropertyId,
    IUIA().UIA_dll.UIA_ProcessIdPropertyId,
    IUIA().UIA_dll.UIA_LocalizedControlTypePropertyId,
    IUIA().UIA_dll.UIA_NamePropertyId,
]


class UiaRecorder(COMObject, Recorder):
    """Record UIA, keyboard and mouse events"""

    _com_interfaces_ = [IUIA().UIA_dll.IUIAutomationEventHandler,
                        IUIA().UIA_dll.IUIAutomationPropertyChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationFocusChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationStructureChangedEventHandler]

    def __init__(self, app=None, record_props=False, record_focus=False, record_struct=False, hot_output=True):
        super(UiaRecorder, self).__init__(app=app, hot_output=hot_output)

        if app.backend.name != "uia":
            raise TypeError("app must be a pywinauto.Application object of 'uia' backend")

        # Turn on or off capturing different kinds of properties
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

    def _add_handlers(self, element):
        """Add UIA handlers to element and all its descendants"""
        cache_request = IUIA().iuia.CreateCacheRequest()
        for prop_id in _cached_properties:
            cache_request.AddProperty(prop_id)

        for event_id, event in IUIA().known_events_ids.items():
            if event not in _ignored_events:
                IUIA().iuia.AddAutomationEventHandler(event_id, element, IUIA().tree_scope['subtree'], cache_request,
                                                      self)

        # TODO: output gets a lot of 'Exception ignored in:' after terminating thread if next method is used
        if self.record_props:
            properties_ids = [p for p in IUIA().known_properties_ids.keys() if p not in _ignored_properties_ids]
            IUIA().iuia.AddPropertyChangedEventHandler(element, IUIA().tree_scope['subtree'], cache_request, self,
                                                       properties_ids)

        if self.record_focus:
            IUIA().iuia.AddFocusChangedEventHandler(cache_request, self)

        if self.record_struct:
            IUIA().iuia.AddStructureChangedEventHandler(element, IUIA().tree_scope['subtree'], cache_request, self)

    def _setup(self):
        try:
            # Add event handlers to all app's controls
            self._add_handlers(self.ctrl.element_info.element)
            self.control_tree = ControlTree(self.ctrl)
        except Exception as exc:
            # TODO: Sometime we can't catch WindowClosed event in WPF applications
            self.stop()
            self.script += "app.kill()\n"
            # Skip exceptions thrown by AddPropertyChangedEventHandler
            # print("Exception: {}".format(exc))

    def _cleanup(self):
        IUIA().iuia.RemoveAllEventHandlers()
        # Stop Hook
        self.hook.stop()

    def hook_target(self):
        """Target function for hook thread"""
        self.hook = win32_hooks.Hook()
        self.hook.handler = self.handle_hook_event
        self.hook.hook(keyboard=True, mouse=True)

    def handle_hook_event(self, hook_event):
        """Callback for keyboard and mouse events"""
        if isinstance(hook_event, win32_hooks.KeyboardEvent):  # Handle keyboard hook events
            keyboard_event = RecorderKeyboardEvent(hook_event.current_key, hook_event.event_type,
                                                   hook_event.pressed_key)
            # Add information about focused element to event
            if self.control_tree:
                focused_element_info = UIAElementInfo(IUIA().get_focused_element())
                keyboard_event.control_tree_node = self.control_tree.node_from_element_info(focused_element_info)
            self.add_to_log(keyboard_event)
        elif isinstance(hook_event, win32_hooks.MouseEvent):  # Handle mouse hook events
            mouse_event = RecorderMouseEvent(hook_event.current_key, hook_event.event_type, hook_event.mouse_x,
                                             hook_event.mouse_y)
            # Add information about clicked item to event
            if self.control_tree:
                mouse_event.control_tree_node = self.control_tree.node_from_point(POINT(mouse_event.mouse_x,
                                                                                        mouse_event.mouse_y))

            # TODO: choose when to parse log
            if mouse_event.event_type == "key down":
                self._parse_and_clear_log()

            self.add_to_log(mouse_event)

    def IUIAutomationEventHandler_HandleAutomationEvent(self, sender, eventID):
        if not self.recorder_start_event.is_set():
            return

        event = ApplicationEvent(name=EVENT_ID_TO_NAME_MAP[eventID], sender=sender)
        self.add_to_log(event)

        if event.name == EVENT.MENU_START:
            self.control_tree.rebuild()
        elif event.name == EVENT.MENU_OPENED:
            self._add_handlers(sender)
        elif event.name == EVENT.WINDOW_OPENED:
            self._add_handlers(sender)
            self.control_tree.rebuild()
        elif event.name == EVENT.WINDOW_CLOSED:
            # Detect if top_window is already closed
            try:
                process_id = self.ctrl.element_info.process_id
            except COMError:
                process_id = 0
            if not process_id:
                self.stop()
                self._parse_and_clear_log()
                self.script += "app.kill()\n"

    def IUIAutomationPropertyChangedEventHandler_HandlePropertyChangedEvent(self, sender, propertyId, newValue):
        if not self.recorder_start_event.is_set():
            return

        event = PropertyEvent(sender=sender, property_name=PROPERTY_ID_TO_NAME_MAP[propertyId], new_value=newValue)
        self.add_to_log(event)

    def IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(self, sender):
        if not self.recorder_start_event.is_set():
            return

        event = ApplicationEvent(name=EVENT.FOCUS_CHANGED, sender=sender)
        self.add_to_log(event)

    def IUIAutomationStructureChangedEventHandler_HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        if not self.recorder_start_event.is_set():
            return

        event = StructureEvent(sender=sender, change_type=changeType, runtime_id=runtimeId)
        self.add_to_log(event)
