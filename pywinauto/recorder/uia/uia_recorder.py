import threading
import timeit

from comtypes import COMObject, COMError

from ... import win32_hooks
from ...win32structures import POINT
from ...uia_defines import IUIA, window_visual_state_normal, expand_state_expanded
from ...uia_element_info import UIAElementInfo
from ...findbestmatch import ControlNames

from ..control_tree import ControlTree, ControlTreeNode
from ..base_recorder import BaseRecorder
from ..win32_progress_bar import ProgressBarDialog
from ..recorder_defines import RecorderMouseEvent, RecorderKeyboardEvent, ApplicationEvent, PropertyEvent, EVENT, \
    PROPERTY
from .uia_event_handlers import UIA_EVENT_PATTERN_MAP
from .uia_recorder_defines import EVENT_ID_TO_NAME_MAP, PROPERTY_ID_TO_NAME_MAP, STRUCTURE_CHANGE_TYPE_TO_NAME_MAP, \
    StructureEvent

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


class UiaRecorder(COMObject, BaseRecorder):

    """Record UIA, keyboard and mouse events"""

    _com_interfaces_ = [IUIA().UIA_dll.IUIAutomationEventHandler,
                        IUIA().UIA_dll.IUIAutomationPropertyChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationFocusChangedEventHandler,
                        IUIA().UIA_dll.IUIAutomationStructureChangedEventHandler]

    def __init__(self, app, config, record_props=True, record_focus=False, record_struct=False):
        super(UiaRecorder, self).__init__(app=app, config=config)

        if app.backend.name != "uia":
            raise TypeError("app must be a pywinauto.Application object of 'uia' backend")

        # Turn on or off capturing different kinds of properties
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

        if self.record_struct is True:
            _ignored_events.remove(IUIA().known_events_ids[IUIA().UIA_dll.UIA_StructureChangedEventId])

        # _update() method variables used for synchronization
        self.update_lock = threading.Lock()
        self.update_counter = 0
        self.rebuild_tree_thr = None

    def _add_handlers(self, element):
        """Add UIA handlers to element and all its descendants"""
        if self.config.verbose:
            start_time = timeit.default_timer()
            print("[_add_handlers] Subscribing to events")

        cache_request = IUIA().iuia.CreateCacheRequest()
        for prop_id in _cached_properties:
            cache_request.AddProperty(prop_id)

        for event_id, event in IUIA().known_events_ids.items():
            if event not in _ignored_events:
                IUIA().iuia.AddAutomationEventHandler(event_id, element, IUIA().tree_scope['subtree'], cache_request,
                                                      self)

        if self.record_props:
            properties_ids = [p for p in IUIA().known_properties_ids.keys() if p not in _ignored_properties_ids]
            IUIA().iuia.AddPropertyChangedEventHandler(element, IUIA().tree_scope['subtree'], cache_request, self,
                                                       properties_ids)

        if self.record_focus:
            IUIA().iuia.AddFocusChangedEventHandler(cache_request, self)

        if self.record_struct:
            IUIA().iuia.AddStructureChangedEventHandler(element, IUIA().tree_scope['subtree'], cache_request, self)

        if self.config.verbose:
            print("[_add_handlers] Finished subscribing to events. Time = {}".format(
                timeit.default_timer() - start_time))

    def _rebuild_control_tree(self):
        if self.config.verbose:
            update_counter = self.update_counter
            start_time = timeit.default_timer()
            print("[_rebuild_control_tree {}] Rebuilding control tree".format(update_counter))
        self.control_tree.rebuild()
        if self.config.verbose:
            print("[_rebuild_control_tree {}] Finished rebuilding control tree. Time = {}".format(
                update_counter, timeit.default_timer() - start_time))

    def _setup(self):
        try:
            # Add event handlers to all app's controls
            self.control_tree = ControlTree(self.wrapper, skip_rebuild=True)
            self._update(rebuild_tree=True, add_handlers_to=self.wrapper.element_info.element, log_msg="Setup")
        except Exception:
            self.stop()
            self.script += u"app.kill()\n"

    def _cleanup(self):
        IUIA().iuia.RemoveAllEventHandlers()
        # Stop Hook
        self.hook.stop()

    def _update(self, rebuild_tree=False, add_handlers_to=None, log_msg=None):
        if self.config.verbose:
            print("[_update] Updating recorder. Reason: {}".format(log_msg))

        pbar_dlg = ProgressBarDialog(self.wrapper.rectangle())
        pbar_dlg.show()

        with self.update_lock:
            # First thread to cause the update - Temporary disable mouse and keyboard event processing
            if self.update_counter == 0:
                self.hook.stop()
                self.hook_thread.join(1)

            self.update_counter += 1

        # Always subscribe to events for new control subtree
        if add_handlers_to:
            add_handlers_thr = threading.Thread(target=self._add_handlers, args=(add_handlers_to,))
            add_handlers_thr.start()

        # Kill existing rebuilding tree thread, create new one
        if rebuild_tree:
            # TODO: Mechanism for killing thread? Wait for now
            if self.rebuild_tree_thr:
                self.rebuild_tree_thr.join()

            self.rebuild_tree_thr = threading.Thread(target=self._rebuild_control_tree)
            self.rebuild_tree_thr.start()

        # Subscription takes far less time than rebuilding control tree, so wait for its completion first
        if add_handlers_to:
            add_handlers_thr.join()

        pbar_dlg.set_progress(50)

        if rebuild_tree:
            self.rebuild_tree_thr.join()

        with self.update_lock:
            self.update_counter -= 1

            # Last thread to cause the update - Enable mouse and keyboard event processing back
            if self.update_counter == 0:
                self.hook_thread = threading.Thread(target=self.hook_target)
                self.hook_thread.start()

        pbar_dlg.set_progress(100)
        pbar_dlg.close()

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

    @property
    def event_patterns(self):
        return UIA_EVENT_PATTERN_MAP

    def IUIAutomationEventHandler_HandleAutomationEvent(self, sender, eventID):
        if not self.recorder_start_event.is_set():
            return

        event = ApplicationEvent(name=EVENT_ID_TO_NAME_MAP[eventID], sender=UIAElementInfo(sender))
        self.add_to_log(event)

        if event.name == EVENT.MENU_OPENED:
            self._update(rebuild_tree=True, add_handlers_to=sender, log_msg="Menu Opened")
        elif event.name == EVENT.WINDOW_OPENED:
            self._update(rebuild_tree=True, add_handlers_to=sender, log_msg="Window Opened")
        elif event.name == EVENT.SELECTION_ELEMENT_SELECTED:
            node = self.control_tree.node_from_element_info(UIAElementInfo(sender))
            if node.ctrl_type == "TabItem":
                self._update(rebuild_tree=True, add_handlers_to=sender, log_msg="Tab Changed")
        elif event.name == EVENT.WINDOW_CLOSED:
            # Detect if top_window is already closed
            try:
                process_id = self.wrapper.element_info.process_id
            except COMError:
                process_id = 0
            if not process_id:
                self.stop()
                self._parse_and_clear_log()
                self.script += u"app.kill()\n"
            else:
                self._update(rebuild_tree=True, add_handlers_to=None, log_msg="Window Closed")

    def IUIAutomationPropertyChangedEventHandler_HandlePropertyChangedEvent(self, sender, propertyId, newValue):
        if not self.recorder_start_event.is_set():
            return

        event = PropertyEvent(property_name=PROPERTY_ID_TO_NAME_MAP[propertyId], sender=UIAElementInfo(sender),
                              new_value=newValue.value if hasattr(newValue, "value") else newValue)
        self.add_to_log(event)

        if (PROPERTY_ID_TO_NAME_MAP[propertyId] == PROPERTY.WINDOW_WINDOW_VISUAL_STATE and
                newValue.value == window_visual_state_normal):
            self._update(rebuild_tree=True, add_handlers_to=sender, log_msg="Window Visual State Changed to Normal")
        if (PROPERTY_ID_TO_NAME_MAP[propertyId] == PROPERTY.EXPAND_COLLAPSE_STATE and
                newValue.value == expand_state_expanded):
            node = self.control_tree.node_from_element_info(UIAElementInfo(sender))
            # Append children of combobox to control tree
            if node.ctrl_type == "ComboBox":
                for item in node.wrapper.children():
                    names = ControlNames()
                    names.text_names.extend(item.texts())
                    node.add_child(item, names, "ComboBoxItem", item.rectangle())

    def IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(self, sender):
        if not self.recorder_start_event.is_set():
            return

        event = ApplicationEvent(name=EVENT.FOCUS_CHANGED, sender=UIAElementInfo(sender))
        self.add_to_log(event)

    def IUIAutomationStructureChangedEventHandler_HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        if not self.recorder_start_event.is_set():
            return

        event = StructureEvent(sender=UIAElementInfo(sender), change_type=STRUCTURE_CHANGE_TYPE_TO_NAME_MAP[changeType],
                               runtime_id=runtimeId)
        self.add_to_log(event)
