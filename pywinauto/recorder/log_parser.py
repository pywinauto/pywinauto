from six import string_types

from .recorder_defines import EventPattern, RecorderMouseEvent, RecorderKeyboardEvent, ApplicationEvent, \
    PropertyEvent, EVENT, PROPERTY, HOOK_MOUSE_LEFT_BUTTON, HOOK_KEY_DOWN, get_window_access_name_str
from .event_handlers import EventHandler, SelectionChangedHandler, MenuOpenedHandler, MenuClosedHandler, \
    ExpandCollapseHandler, MouseClickHandler, KeyboardHandler

EVENT_PATTERN_MAP = [
    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED))),
     SelectionChangedHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.INVOKED),)),
     "invoke()"),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.MENU_OPENED),)),
     MenuOpenedHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.MENU_CLOSED),)),
     MenuClosedHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.EXPAND_COLLAPSE_STATE),
                              PropertyEvent(property_name=PROPERTY.TOGGLE_STATE))),
     ExpandCollapseHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.EXPAND_COLLAPSE_STATE),)),
     ExpandCollapseHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.TOGGLE_STATE),)),
     "toggle()"),
    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),)),
     "select()"),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=None, event_type=HOOK_KEY_DOWN)),
     MouseClickHandler),

    (EventPattern(hook_event=RecorderKeyboardEvent(current_key=None, event_type=HOOK_KEY_DOWN)),
     KeyboardHandler)
]


class LogParser(object):
    def __init__(self, recorder):
        self.recorder = recorder

        self.menu_sequence = []
        self.text_sequence = {}

    def _break_log_up(self):
        # TODO: General assumption: all hook events come before UIA events
        # TODO: click or keyboard button (hook) -> what happened (uia)
        action_log = []
        iter = 0
        for event in self.recorder.event_log:
            if isinstance(event, ApplicationEvent):
                # Only add events if hook event has been met
                if iter > 0:
                    action_log[iter - 1].app_events.append(event)
            elif isinstance(event, RecorderMouseEvent):
                # TODO: only add key down events, assume that user performs only clicks
                if event.event_type == HOOK_KEY_DOWN:
                    action_log.append(EventPattern(hook_event=event, app_events=[]))
                    iter += 1
            elif isinstance(event, RecorderKeyboardEvent):
                action_log.append(EventPattern(hook_event=event, app_events=[]))
                iter += 1
        return action_log

    def parse_current_log(self):
        # Break log to chunks (1 hook event, all uia events that come after it)
        action_log = self._break_log_up()

        # Parsed script
        script = ""

        # Main parser loop
        for action in action_log:
            hook_event = action.hook_event
            app_events = action.app_events
            if self.recorder.config.verbose:
                print("\n================================================================================\n"
                      "Hook event: {}\n    Application events: {}"
                      "".format(hook_event, app_events))

            # Scan action for known patterns
            for event_pattern, handler in EVENT_PATTERN_MAP:
                subpattern = action.get_subpattern(event_pattern)
                if subpattern:
                    if hook_event.control_tree_node:
                        subtree = self.recorder.control_tree.sub_tree_from_node(hook_event.control_tree_node)

                        if isinstance(handler, type) and issubclass(handler, EventHandler):
                            s = handler(subtree, self, subpattern).run()
                            if isinstance(s, string_types):
                                script += s
                        else:
                            root_name = subtree[-1].names.get_preferred_name()
                            item_name = subtree[0].names.get_preferred_name()
                            script += u"app{}{}.{}\n".format(
                                get_window_access_name_str(root_name, self.recorder.config.key_only),
                                get_window_access_name_str(item_name, self.recorder.config.key_only),
                                handler)
                    else:
                        print("WARNING: Event skipped")
                    break
            else:
                print("WARNING: Unrecognized pattern - {}".format(action))
            if self.recorder.config.verbose:
                print("================================================================================\n")

        return script
