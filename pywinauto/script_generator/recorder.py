from .. import Application
from ..uia_defines import IUIA
from ..uia_element_info import UIAElementInfo

from ..win32_hooks import *

from comtypes import COMObject, COMError

import threading

_ignored_events = [
    # Event which are handled by separate handlers
    'AutomationFocusChanged', 'AutomationPropertyChanged', 'StructureChanged',

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

active_recorder = None
hot_output = True


def handle_hook_event(args):
    """Callback for keyboard and mouse events"""
    if isinstance(args, KeyboardEvent):
        if args.current_key == 'A' and args.event_type == 'key down' and 'Lcontrol' in args.pressed_key:
            print("Ctrl + A was pressed")

        if args.current_key == 'M' and args.event_type == 'key down' and 'U' in args.pressed_key:
            active_recorder.hook.unhook_mouse()
            print("Unhook mouse")

        if args.current_key == 'K' and args.event_type == 'key down' and 'U' in args.pressed_key:
            active_recorder.hook.unhook_keyboard()
            print("Unhook keyboard")

    if isinstance(args, MouseEvent):
        if args.current_key == 'LButton' and args.event_type == 'key down':
            if active_recorder:
                active_recorder.add_to_log("Left button pressed at ({}, {})".format(args.mouse_x, args.mouse_y))
            if hot_output:
                print('Left mouse button pressed at ({}, {})'.format(args.mouse_x, args.mouse_y))

        if args.current_key == 'RButton' and args.event_type == 'key down':
            if active_recorder:
                active_recorder.add_to_log("Left button pressed at ({}, {})".format(args.mouse_x, args.mouse_y))
            if hot_output:
                print('Right mouse button pressed at ({}, {})'.format(args.mouse_x, args.mouse_y))

        if args.current_key == 'WheelButton' and args.event_type == 'key down':
            if active_recorder:
                active_recorder.add_to_log("Left button pressed at ({}, {})".format(args.mouse_x, args.mouse_y))


def synchronized_method(method):
    """Decorator for a synchronized class method"""
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "_lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method


class UIAEvent(object):
    """Created when an UIA event happened"""

    def __init__(self, event_name=None, sender=None, property_name=None, struct_change_type=None):
        self.event_name = event_name
        self.sender = sender
        self.property_name = property_name
        self.struct_change_type = struct_change_type

    def __str__(self):
        """Representation of the event"""
        description = '{} - {} | {} | {}'.format(self.event_name, self.sender, self.sender.CachedClassName,
                                                 self.sender.CachedName)
        if self.event_name == 'AutomationPropertyChanged':
            description += '; Property: {}'.format(self.property_name)
        if self.event_name == 'StructureChanged':
            description += '; Structure change type: {}'.format(self.struct_change_type)

        return description


class Recorder(COMObject):
    """Record UIA, keyboard and mouse events"""

    _com_interfaces_ = [IUIA().UIA_dll.IUIAutomationEventHandler,
                        IUIA().UIA_dll.IUIAutomationPropertyChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationFocusChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationStructureChangedEventHandler]

    def __init__(self, app=None, record_props=False, record_focus=False, record_struct=False):
        super(Recorder, self).__init__()

        if app is not None:
            if not isinstance(app, Application):
                raise TypeError("app must be a pywinauto.Application object")
            self.element_info = app.top_window().element_info
        else:
            self.element_info = UIAElementInfo()
        self.element = self.element_info.element

        self.event_log = []

        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

        self.recorder_start_event = threading.Event()
        self.recorder_stop_event = threading.Event()

        self.recorder_thread = threading.Thread(target=self.recorder_run)
        self.recorder_thread.daemon = False

        self.hook_thread = threading.Thread(target=self.hook_run)
        self.hook_thread.daemon = False

        global active_recorder
        active_recorder = self

        self._opened_windows = []

    @synchronized_method
    def add_to_log(self, text):
        self.event_log.append(text)

    def start(self):
        self.recorder_thread.start()
        self.hook_thread.start()

    def stop(self):
        self.recorder_stop_event.set()
        self.hook.stop()

    def _add_handlers(self, element):
        cache_request = IUIA().iuia.CreateCacheRequest()
        for prop_id in _cached_properties:
            cache_request.AddProperty(prop_id)

        for event_id, event in IUIA().known_events_ids.items():
            if event not in _ignored_events:
                IUIA().iuia.AddAutomationEventHandler(event_id,
                                                      element,
                                                      IUIA().tree_scope['subtree'],
                                                      cache_request,
                                                      self)

        # TODO: output gets a lot of 'Exception ignored in:' after terminating thread if next method is used
        if self.record_props:
            properties_ids = [p for p in IUIA().known_properties_ids.keys() if p not in _ignored_properties_ids]
            IUIA().iuia.AddPropertyChangedEventHandler(element,
                                                       IUIA().tree_scope['subtree'],
                                                       cache_request,
                                                       self,
                                                       properties_ids)

        if self.record_focus:
            IUIA().iuia.AddFocusChangedEventHandler(cache_request,
                                                    self)

        if self.record_struct:
            IUIA().iuia.AddStructureChangedEventHandler(element,
                                                        IUIA().tree_scope['subtree'],
                                                        cache_request,
                                                        self)

    def recorder_run(self):
        """Target function for recorder thread"""
        try:
            # Add event handlers to all app's controls
            self._add_handlers(self.element)
        except Exception as exc:
            print(exc)
        finally:
            self.recorder_start_event.set()

        # Wait until app closes and then remove all handlers
        self.recorder_stop_event.wait()
        IUIA().iuia.RemoveAllEventHandlers()

    def hook_run(self):
        """Target function for hook thread"""
        self.hook = Hook()
        self.hook.handler = handle_hook_event
        self.hook.hook(keyboard=False, mouse=True)

    def IUIAutomationEventHandler_HandleAutomationEvent(self, sender, eventID):
        if not self.recorder_start_event.is_set():
            return

        event_name = IUIA().known_events_ids[eventID]

        self.add_to_log(UIAEvent(event_name=event_name, sender=sender))
        if hot_output:
            print('Event: {} - {}, {}: {}'.format(IUIA().known_events_ids[eventID], sender.CachedClassName,
                                                  sender.CachedName, sender))

        if event_name == 'MenuOpened':
            self._add_handlers(sender)

        if event_name == 'MenuClosed':
            # Handle MenuClosed event (click on menu item)
            pass

        if event_name == 'Window_WindowOpened':
            self._add_handlers(sender)

        if event_name == 'Window_WindowClosed':
            # Detect if top_window is already closed
            try:
                self.element_info.process_id
            except COMError:
                self.stop()

    def IUIAutomationPropertyChangedEventHandler_HandlePropertyChangedEvent(self, sender, propertyId, newValue):
        if not self.recorder_start_event.is_set():
            return

        self.add_to_log(UIAEvent(event_name='AutomationPropertyChanged',
                                 sender=sender, property_name=IUIA().known_properties_ids[propertyId]))
        if hot_output:
            print('Property Changed: {} - {}, {}: {}'.format(IUIA().known_properties_ids[propertyId],
                                                             sender.CachedClassName, sender.CachedName, sender))

    def IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(self, sender):
        if not self.recorder_start_event.is_set():
            return

        self.add_to_log(UIAEvent(event_name='AutomationFocusChanged', sender=sender))
        if hot_output:
            print('Focus Changed: {}'.format(sender))

    def IUIAutomationStructureChangedEventHandler_HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        if not self.recorder_start_event.is_set():
            return

        self.add_to_log(UIAEvent(event_name='StructureChanged', sender=sender, struct_change_type=changeType))
        if hot_output:
            print('Structure Changed: {} - {}, {}: {}'.format(changeType, sender.CachedClassName, sender.CachedName,
                                                              sender))
