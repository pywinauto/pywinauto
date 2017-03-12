from .. import Application
from ..uia_defines import IUIA
from ..uia_element_info import UIAElementInfo

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


class Recorder(COMObject):
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

        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

        self.recorder_start_event = threading.Event()
        self.recorder_stop_event = threading.Event()

        self.recorder_thread = threading.Thread(target=self.run)
        self.recorder_thread.daemon = False

        self._opened_windows = []

    def start(self):
        self.recorder_thread.start()

    def stop(self):
        self.recorder_stop_event.set()

    def _add_handlers(self, element):
        cache_request = IUIA().iuia.CreateCacheRequest()
        for prop_id in _cached_properties:
            cache_request.AddProperty(prop_id)

        for event_id, event in IUIA().known_events_ids.items():
            if event in _ignored_events:
                continue
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

    def run(self):
        try:
            # Get application top window
            # root_element = IUIA().root
            # cond_calc = IUIA().iuia.CreatePropertyCondition(IUIA().UIA_dll.UIA_NamePropertyId, "WPF Sample Application")
            # top_window = root_element.FindFirst(IUIA().UIA_dll.TreeScope_Children, cond_calc)

            # Add event handlers to all app's controls
            self._add_handlers(self.element)
        except Exception as exc:
            print(exc)
        finally:
            self.recorder_start_event.set()

        # Wait until app closes and then remove all handlers
        self.recorder_stop_event.wait()
        IUIA().iuia.RemoveAllEventHandlers()

    def IUIAutomationEventHandler_HandleAutomationEvent(self, sender, eventID):
        if not self.recorder_start_event.is_set():
            return

        print('Event: {} - {}, {}: {}'.format(IUIA().known_events_ids[eventID], sender.CachedClassName, sender.CachedName, sender))

        if IUIA().known_events_ids[eventID] == 'MenuOpened':
            self._add_handlers(sender)

        if IUIA().known_events_ids[eventID] == 'MenuClosed':
            # Handle MenuClosed event (click on menu item)
            pass

        if IUIA().known_events_ids[eventID] == 'Window_WindowOpened':
            self._add_handlers(sender)

        if IUIA().known_events_ids[eventID] == 'Window_WindowClosed':
            # Detect if top_window is already closed
            try:
                self.element_info.process_id
            except COMError:
                self.stop()

    def IUIAutomationPropertyChangedEventHandler_HandlePropertyChangedEvent(self, sender, propertyId, newValue):
        if not self.recorder_start_event.is_set():
            return

        print('Property Changed: {} - {}, {}: {}'.format(IUIA().known_properties_ids[propertyId], sender.CachedClassName, sender.CachedName, sender))

    def IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(self, sender):
        if not self.recorder_start_event.is_set():
            return

        print('Focus Changed:', sender)

    def IUIAutomationStructureChangedEventHandler_HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        if not self.recorder_start_event.is_set():
            return

        print('Structure Changed: {} - {}, {}: {}'.format(changeType, sender.CachedClassName, sender.CachedName, sender))
