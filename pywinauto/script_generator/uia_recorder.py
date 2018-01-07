import threading

from comtypes import COMObject, COMError

from .. import Application
from ..uia_defines import IUIA

from .. import win32_hooks
from ..win32structures import POINT

from .control_tree import ControlTree
from .recorder_events import RecorderEvent, RecorderMouseEvent, RecorderKeyboardEvent, UIAEvent, PropertyEvent, \
    FocusEvent, StructureEvent

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


def synchronized_method(method):
    """Decorator for a synchronized class method"""
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "_lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name):
                setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method


class UiaRecorder(COMObject):
    """Record UIA, keyboard and mouse events"""

    _com_interfaces_ = [IUIA().UIA_dll.IUIAutomationEventHandler,
                        IUIA().UIA_dll.IUIAutomationPropertyChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationFocusChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationStructureChangedEventHandler]

    def __init__(self, app=None, record_props=False, record_focus=False, record_struct=False, hot_output=True):
        super(UiaRecorder, self).__init__()

        if app is not None and isinstance(app, Application) and app.backend.name == "uia":
            self.ctrl = app.top_window().wrapper_object()
            self.element_info = self.ctrl.element_info
        else:
            raise TypeError("app must be a pywinauto.Application object of 'uia' backend")
        self.element = self.element_info.element

        # List of RecordEvent objects
        self.event_log = []

        # Menu history
        self.menu_sequence = []

        # Turn on or off capturing different kinds of properties
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

        # Output events straight away (for debug purposes)
        self.hot_output = hot_output

        # Main recorder thread
        self.recorder_thread = threading.Thread(target=self.recorder_run)
        self.recorder_thread.daemon = True

        # Thread events to indicate recorder status (used as an alternative to an infinite loop)
        self.recorder_start_event = threading.Event()
        self.recorder_stop_event = threading.Event()

        # Hook event thread
        self.hook_thread = threading.Thread(target=self.hook_run)
        self.hook_thread.daemon = True

        # Application controls tree
        self.control_tree = None

        # Generated script
        self.script = "app = pywinauto.Application(backend='uia').start('INSERT_CMD_HERE')\n"

    @synchronized_method
    def add_to_log(self, item):
        """
        Add *item* to event log.
        This is a synchronized method. 
        """
        self.event_log.append(item)
        if self.hot_output:
            print(item)

    @synchronized_method
    def clear_log(self):
        """
        Clear event log.
        This is a synchronized method. 
        """
        # Clear instead of new empty list initialization to keep the link alive
        self.event_log.clear()

    def is_active(self):
        """Returns True if UiaRecorder is active"""
        return self.recorder_thread.is_alive() or self.hook_thread.is_alive()

    def start(self):
        """Start UiaRecorder"""
        self.recorder_thread.start()
        self.hook_thread.start()

    def stop(self):
        """Stop UiaRecorder"""
        self.recorder_stop_event.set()
        self.hook.stop()

    def wait(self):
        """Wait for recorder to finish"""
        if self.is_active():
            self.recorder_thread.join()

    def _add_handlers(self, element):
        """Add UIA handlers to element and all its descendants"""
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
            self.control_tree = ControlTree(self.ctrl)
        except Exception as exc:
            # Skip exceptions thrown by AddPropertyChangedEventHandler
            print("Exception: {}".format(exc))
        finally:
            self.recorder_start_event.set()

        # Wait until app closes and then remove all handlers
        self.recorder_stop_event.wait()
        IUIA().iuia.RemoveAllEventHandlers()

    def hook_run(self):
        """Target function for hook thread"""
        self.hook = win32_hooks.Hook()
        self.hook.handler = self.handle_hook_event
        self.hook.hook(keyboard=True, mouse=True)

    def parse_and_clear_log(self):
        """Parse current event log and clear it afterwards"""
        for event in self.event_log:
            if isinstance(event, RecorderEvent):
                if isinstance(event, RecorderMouseEvent):
                    if event.control_tree_node:
                        # Choose appropriate name
                        item_name = [name for name in event.control_tree_node.names
                                     if len(name) > 0 and not " " in name][-1]

                        joint_log = "\n".join([str(ev) for ev in self.event_log])
                        if "Invoke_Invoked" in joint_log:
                            self.script += "app.{}.{}.invoke()\n".format(self.control_tree.root_name, item_name)
                        elif "ToggleToggleState" in joint_log:
                            self.script += "app.{}.{}.toggle()\n".format(self.control_tree.root_name, item_name)
                        elif "MenuOpened" in joint_log:
                            self.menu_sequence = [event.control_tree_node.ctrl.window_text(), ]
                        elif "MenuClosed" in joint_log:
                            self.script += "app.{}.menu_select('{}')\n".format(
                                self.control_tree.root_name,
                                " -> ".join(self.menu_sequence) + " -> " + event.control_tree_node.ctrl.window_text())
                            self.menu_sequence = [event.control_tree_node.ctrl.window_text(), ]
                        else:
                            self.script += "app.{}.{}.click_input()\n".format(self.control_tree.root_name, item_name)
                    else:
                        self.script += "pywinauto.mouse.click(coords=({}, {}))\n".format(event.mouse_x, event.mouse_y)
            else:
                self.script += "print('{}')\n".format(event)
        self.clear_log()

    def handle_hook_event(self, hook_event):
        """Callback for keyboard and mouse events"""
        if isinstance(hook_event, win32_hooks.KeyboardEvent):  # Handle keyboard hook events
            keyboard_event = RecorderKeyboardEvent(hook_event.current_key, hook_event.event_type,
                                                   hook_event.pressed_key)
            self.add_to_log(keyboard_event)
        elif isinstance(hook_event, win32_hooks.MouseEvent):  # Handle mouse hook events
            mouse_event = RecorderMouseEvent(hook_event.current_key, hook_event.event_type, hook_event.mouse_x,
                                             hook_event.mouse_y)
            # Left mouse button down
            if mouse_event.current_key == 'LButton' and mouse_event.event_type == 'key down':
                # Parse current event log and clear it
                self.parse_and_clear_log()

                # Add information about clicked item to event
                if self.control_tree:
                    node = self.control_tree.node_from_point(POINT(mouse_event.mouse_x, mouse_event.mouse_y))
                    if node:
                        mouse_event.control_tree_node = node

                # Add new event to log
                self.add_to_log(mouse_event)

    def IUIAutomationEventHandler_HandleAutomationEvent(self, sender, eventID):
        if not self.recorder_start_event.is_set():
            return

        event = UIAEvent(event_name=IUIA().known_events_ids[eventID], sender=sender)
        self.add_to_log(event)

        # TODO: remove hardcoded values
        if event.event_name == 'MenuModeStart':
            self.control_tree.rebuild()

        if event.event_name == 'MenuOpened':
            self._add_handlers(sender)

        if event.event_name == 'Window_WindowOpened':
            self._add_handlers(sender)
            self.control_tree.rebuild()

        if event.event_name == 'Window_WindowClosed':
            # Detect if top_window is already closed
            try:
                process_id = self.element_info.process_id
            except COMError:
                process_id = 0
            if not process_id:
                self.stop()
                self.parse_and_clear_log()
                self.script += "app.kill()\n"

    def IUIAutomationPropertyChangedEventHandler_HandlePropertyChangedEvent(self, sender, propertyId, newValue):
        if not self.recorder_start_event.is_set():
            return

        event = PropertyEvent(sender=sender, property_name=IUIA().known_properties_ids[propertyId], new_value=newValue)
        self.add_to_log(event)

    def IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(self, sender):
        if not self.recorder_start_event.is_set():
            return

        event = FocusEvent(sender=sender)
        self.add_to_log(event)

    def IUIAutomationStructureChangedEventHandler_HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        if not self.recorder_start_event.is_set():
            return

        event = StructureEvent(sender=sender, change_type=changeType, runtime_id=runtimeId)
        self.add_to_log(event)
