from .recorder_defines import *


class LogParser(object):
    def __init__(self, recorder, verbose=False):
        self.recorder = recorder
        self.verbose = verbose

        self.menu_sequence = []
        self.text_sequence = {}

    def parse_current_log(self):
        # TODO: General assumption: all hook events come before UIA events
        # TODO: click or keyboard button (hook) -> what happened (uia)

        # Break log to chunks (1 hook event, all uia events that come after it)
        action_log = []
        iter = 0
        for event in self.recorder.event_log:
            if isinstance(event, ApplicationEvent):
                # Only add events if hook event has been met
                if iter > 0:
                    action_log[iter - 1].append(event)
            elif isinstance(event, RecorderMouseEvent):
                # TODO: only add key down events, assume that user performs only clicks
                if event.event_type == "key down":
                    action_log.append([event, ])
                    iter += 1
            elif isinstance(event, RecorderKeyboardEvent):
                action_log.append([event, ])
                iter += 1
            else:
                pass

        # Parsed script
        script = ""

        # Main parser loop
        for action in action_log:
            hook_event = action[0]
            application_events = action[1:]
            if self.verbose:
                print("\n================================================================================\n"
                      "Hook event: {}\n    Application events: {}"
                      "".format(hook_event, application_events))

            if isinstance(hook_event, RecorderMouseEvent):
                # What happened after click (lbutton down-up)
                if hook_event.current_key == "LButton" and hook_event.event_type == "key down":
                    # Check if text has been typed
                    for k, v in self.text_sequence.items():
                        item_name = k.names.get_preferred_name()
                        script += u"app.{}.{}.type_keys('{}')\n".format(
                            self.recorder.control_tree.root_name, item_name, v)
                    self.text_sequence = {}

                    if hook_event.control_tree_node:
                        subtree = self.recorder.control_tree.sub_tree_from_node(hook_event.control_tree_node)
                        root_name = subtree[-1].names.get_preferred_name()
                        # print("Subtree: {}".format([node.wrapper for node in subtree]))

                        def get_node_sender(subtree, event_name):
                            for elem in subtree:
                                possible_handlers = getattr(elem.wrapper, "possible_handlers", {})
                                if event_name in possible_handlers:
                                    return elem, possible_handlers[event_name]
                            return None, None

                        event_handled = False

                        # Handle simple events
                        if any(e for e in application_events if e.name == EVENT.INVOKED):
                            node, handler = get_node_sender(subtree, EVENT.INVOKED)
                            if node:
                                item_name = node.names.get_preferred_name()
                                script += u"app.{}.{}.{}()\n".format(root_name, item_name,
                                                                    handler if handler else "invoke")
                                event_handled = True
                        elif any(e for e in application_events if e.name == EVENT.MENU_OPENED):
                            node, handler = get_node_sender(subtree, EVENT.MENU_OPENED)
                            if node:
                                menu_item_text = node.names.text_names[0]
                                self.menu_sequence = [menu_item_text, ]
                                event_handled = True
                        elif any(e for e in application_events if e.name == EVENT.MENU_CLOSED):
                            node, handler = get_node_sender(subtree, EVENT.MENU_CLOSED)
                            if node:
                                menu_item_text = node.names.text_names[0]
                                script += u"app.{}.menu_select({})\n".format(
                                    root_name, repr(" -> ".join(self.menu_sequence + [menu_item_text, ])))
                                self.menu_sequence = []
                                event_handled = True
                        # Handle PropertyEvent
                        elif any(e for e in application_events if isinstance(e, PropertyEvent)):
                            def prop_gen():
                                for e in application_events:
                                    if isinstance(e, PropertyEvent):
                                        yield e

                            prop1 = next(prop_gen())
                            if prop1.property_name == PROPERTY.EXPAND_COLLAPSE_STATE and hasattr(prop1.new_value,
                                                                                                 "value"):
                                node, handler = get_node_sender(subtree, PROPERTY.EXPAND_COLLAPSE_STATE)
                                if node:
                                    item_name = node.names.get_preferred_name()
                                    script += u"app.{}.{}.{}()\n".format(
                                        root_name, item_name, "expand" if prop1.new_value.value else "collapse")
                                    event_handled = True
                            elif prop1.property_name == PROPERTY.TOGGLE_STATE:
                                node, handler = get_node_sender(subtree, PROPERTY.TOGGLE_STATE)
                                if node:
                                    item_name = node.names.get_preferred_name()
                                    script += u"app.{}.{}.{}()\n".format(root_name, item_name,
                                                                        handler if handler else "toggle")
                                    event_handled = True

                        if not event_handled:
                            min_rect_elem = None
                            for elem in subtree:
                                if (hook_event.mouse_x, hook_event.mouse_y) in elem.rect:
                                    if min_rect_elem is None:
                                        min_rect_elem = elem
                                    elif elem.rect.width() < min_rect_elem.rect.width() and \
                                            elem.rect.height() < min_rect_elem.rect.height():
                                        min_rect_elem = elem
                            item_name = min_rect_elem.names.get_preferred_name()
                            script += u"app.{}.{}.click_input()\n".format(root_name, item_name)
                    else:
                        script += u"pywinauto.mouse.click(button='left', coords=({}, {}))\n" \
                            "".format(hook_event.mouse_x, hook_event.mouse_y)
                        # script += "app.{}.click_input(coords=({}, {}), absolute=True)".format(
                        #     root_name, hook_event.mouse_x, hook_event.mouse_y)
                elif hook_event.event_type == "key down":
                    if hook_event.current_key == "RButton":
                        button = "right"
                    elif hook_event.current_key == "Wheel":
                        button = "wheel"
                    else:
                        button = "left"
                    script += u"pywinauto.mouse.click(button='{}', coords=({}, {}))\n" \
                        "".format(button, hook_event.mouse_x, hook_event.mouse_y)
            elif isinstance(hook_event, RecorderKeyboardEvent):
                if hook_event.event_type == "key down":
                    if hook_event.control_tree_node:
                        uia_ctrl = hook_event.control_tree_node
                    else:
                        uia_ctrl = "hotkey"
                    self.text_sequence.setdefault(uia_ctrl, "")
                    self.text_sequence[uia_ctrl] += hook_event.current_key

            if self.verbose:
                print("================================================================================\n")

        return script
