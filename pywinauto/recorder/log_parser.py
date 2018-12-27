from abc import abstractmethod

from .recorder_defines import *


class EventHandler(object):
    def __init__(self, subtree, log_parser, subpattern):
        self.subtree = subtree
        self.log_parser = log_parser
        self.subpattern = subpattern

    def get_root_name(self):
        return self.subtree[-1].names.get_preferred_name()

    def get_item_name(self):
        return self.subtree[0].names.get_preferred_name()

    @abstractmethod
    def run(self):
        raise NotImplementedError()


class MenuOpenedHandler(EventHandler):
    def run(self):
        menu_item_text = self.subtree[0].names.text_names[0]
        self.log_parser.menu_sequence = [menu_item_text, ]


class MenuClosedHandler(EventHandler):
    def run(self):
        menu_item_text = self.subtree[0].names.text_names[0]
        script = u"app.{}.menu_select({})\n".format(
            self.get_root_name(), repr(" -> ".join(self.log_parser.menu_sequence + [menu_item_text, ])))
        self.log_parser.menu_sequence = []
        return script


class ExpandCollapseHandler(EventHandler):
    def run(self):
        exp_coll_state = self.subpattern.app_events[0]
        script = u"app.{}.{}.{}\n".format(self.get_root_name(), self.get_item_name(),
                                          "expand()" if exp_coll_state.new_value else "collapse()")
        return script


class SelectionChangedHandler(EventHandler):
    def run(self):
        selected_elem_info = self.subpattern.app_events[-1].sender
        for node in self.subtree:
            if node.wrapper.element_info == selected_elem_info:
                selected = node
                parent = node.parent
                break
        else:
            selected = self.subtree[0]
            parent = self.subtree[0].parent
        return u"app.{}.{}.select('{}')\n".format(self.get_root_name(), parent.names.get_preferred_name(),
                                                  selected.names.text_names[0])


EVENT_PATTERN_MAP = [
    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED))),
     SelectionChangedHandler),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.INVOKED),)),
     "invoke()"),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.MENU_OPENED),)),
     MenuOpenedHandler),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.MENU_CLOSED),)),
     MenuClosedHandler),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.EXPAND_COLLAPSE_STATE),
                              PropertyEvent(property_name=PROPERTY.TOGGLE_STATE))),
     ExpandCollapseHandler),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.EXPAND_COLLAPSE_STATE),)),
     ExpandCollapseHandler),

    (EventPattern(hook_event=HookEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.TOGGLE_STATE),)),
     "toggle()")
]


class LogParser(object):
    def __init__(self, recorder, verbose=False):
        self.recorder = recorder
        self.verbose = verbose

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

    def _process_left_click(self, hook_event):
        if hook_event.control_tree_node:
            subtree = self.recorder.control_tree.sub_tree_from_node(hook_event.control_tree_node)
            root_name = subtree[-1].names.get_preferred_name()

            min_rect_elem = None
            for elem in subtree:
                if (hook_event.mouse_x, hook_event.mouse_y) in elem.rect:
                    if min_rect_elem is None:
                        min_rect_elem = elem
                    elif elem.rect.width() < min_rect_elem.rect.width() and \
                            elem.rect.height() < min_rect_elem.rect.height():
                        min_rect_elem = elem
            item_name = min_rect_elem.names.get_preferred_name()
            return u"app.{}.{}.click_input()\n".format(root_name, item_name)
        else:
            return u"pywinauto.mouse.click(button='left', coords=({}, {}))\n".format(
                hook_event.mouse_x, hook_event.mouse_y)

    def parse_current_log(self):
        # Break log to chunks (1 hook event, all uia events that come after it)
        action_log = self._break_log_up()

        # Parsed script
        script = ""

        # Main parser loop
        for action in action_log:
            hook_event = action.hook_event
            app_events = action.app_events
            if self.verbose:
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
                            if isinstance(s, str):
                                script += s
                        else:
                            root_name = subtree[-1].names.get_preferred_name()
                            item_name = subtree[0].names.get_preferred_name()
                            script += u"app.{}.{}.{}\n".format(root_name, item_name, handler)
                    else:
                        # TODO: for now
                        print("WARNING: Event skipped")
                    break
            # Process action as simple click or type event
            else:
                if isinstance(hook_event, RecorderMouseEvent):
                    # What happened after click (lbutton down-up)
                    if hook_event.current_key == "LButton" and hook_event.event_type == "key down":
                        # Check if text has been typed
                        for k, v in self.text_sequence.items():
                            item_name = k.names.get_preferred_name()
                            script += u"app.{}.{}.type_keys(u'{}')\n".format(
                                self.recorder.control_tree.root_name, item_name, v)
                        self.text_sequence = {}

                        # Process left click
                        script += self._process_left_click(hook_event)
                    elif hook_event.event_type == HOOK_KEY_DOWN:
                        if hook_event.current_key == HOOK_MOUSE_RIGHT_BUTTON:
                            button = "right"
                        elif hook_event.current_key == HOOK_MOUSE_MIDDLE_BUTTON:
                            button = "wheel"
                        else:
                            button = "left"
                        script += u"pywinauto.mouse.click(button='{}', coords=({}, {}))\n" \
                                  "".format(button, hook_event.mouse_x, hook_event.mouse_y)
                elif isinstance(hook_event, RecorderKeyboardEvent):
                    if hook_event.event_type == HOOK_KEY_DOWN:
                        if hook_event.control_tree_node:
                            uia_ctrl = hook_event.control_tree_node
                        else:
                            uia_ctrl = "hotkey"
                        self.text_sequence.setdefault(uia_ctrl, "")
                        self.text_sequence[uia_ctrl] += hook_event.current_key

            if self.verbose:
                print("================================================================================\n")

        return script
