from ..recorder_defines import EVENT, PROPERTY, RecorderMouseEvent, RecorderKeyboardEvent, ApplicationEvent, \
    PropertyEvent, EventPattern, HOOK_MOUSE_LEFT_BUTTON, HOOK_MOUSE_RIGHT_BUTTON, HOOK_MOUSE_MIDDLE_BUTTON, \
    HOOK_KEY_DOWN, get_window_access_name_str, EventHandler


class MenuOpenedHandler(EventHandler):
    def run(self):
        menu_item_text = self.subtree[0].names.text_names[0]
        self.log_parser.menu_sequence = [menu_item_text, ]


class MenuClosedHandler(EventHandler):
    def run(self):
        menu_item_text = self.subtree[0].names.text_names[0]
        script = u"app{}.menu_select({})\n".format(
            self.get_root_name(), repr(" -> ".join(self.log_parser.menu_sequence + [menu_item_text, ])))
        self.log_parser.menu_sequence = []
        return script


class ExpandCollapseHandler(EventHandler):
    def run(self):
        exp_coll_state = self.subpattern.app_events[0]
        item_name = self.get_sender_name(0)
        script = u"app{}{}.{}\n".format(self.get_root_name(), item_name,
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
        return u"app{}{}.select('{}')\n".format(
            self.get_root_name(), get_window_access_name_str(parent.names.get_preferred_name(), self.key_only),
            selected.names.text_names[0])


class InvokeHandler(EventHandler):
    def run(self):
        return u"app{}{}.invoke()\n".format(self.get_root_name(), self.get_sender_name(0))


class ToggleHandler(EventHandler):
    def run(self):
        return u"app{}{}.toggle()\n".format(self.get_root_name(), self.get_sender_name(0))


class SelectHandler(EventHandler):
    def run(self):
        return u"app{}{}.select()\n".format(self.get_root_name(), self.get_sender_name(0))


class MouseClickHandler(EventHandler):
    def run(self):
        script = u""

        # Check if text has been typed
        for k, v in self.log_parser.text_sequence.items():
            item_name = get_window_access_name_str(k.names.get_preferred_name(), self.key_only)
            script += u"app{}{}.type_keys(u'{}')\n".format(self.get_root_name(), item_name, v)
        self.log_parser.text_sequence = {}

        # Process left click
        hook_event = self.subpattern.hook_event
        if hook_event.current_key == HOOK_MOUSE_RIGHT_BUTTON:
            button = "right"
        elif hook_event.current_key == HOOK_MOUSE_MIDDLE_BUTTON:
            button = "wheel"
        else:
            button = "left"
        if hook_event.control_tree_node:
            subtree = self.log_parser.recorder.control_tree.sub_tree_from_node(hook_event.control_tree_node)
            root_acc_name = get_window_access_name_str(subtree[-1].names.get_preferred_name(), self.key_only)

            min_rect_elem = None
            for elem in subtree:
                if (hook_event.mouse_x, hook_event.mouse_y) in elem.rect:
                    if min_rect_elem is None:
                        min_rect_elem = elem
                    elif elem.rect.width() < min_rect_elem.rect.width() and \
                            elem.rect.height() < min_rect_elem.rect.height():
                        min_rect_elem = elem
            item_name = min_rect_elem.names.get_preferred_name()
            item_acc_name = get_window_access_name_str(item_name, self.key_only)
            if self.log_parser.recorder.config.scale_click:
                scale_x = (hook_event.mouse_x - min_rect_elem.rect.left) / float(
                    min_rect_elem.rect.right - min_rect_elem.rect.left)
                scale_y = (hook_event.mouse_y - min_rect_elem.rect.top) / float(
                    min_rect_elem.rect.bottom - min_rect_elem.rect.top)

                script += u"# Clicking on object '{}' with scale ({}, {})\n".format(item_name, scale_x, scale_y)
                script += u"_elem = app{}{}.wrapper_object()\n".format(root_acc_name, item_acc_name)
                script += u"_rect = _elem.rectangle()\n"
                script += u"_x = int((_rect.right - _rect.left) * {})\n".format(scale_x)
                script += u"_y = int((_rect.bottom - _rect.top) * {})\n".format(scale_y)
                script += u"_elem.click_input(button='{}', coords=(_x, _y))\n".format(button)
            else:
                x, y = hook_event.mouse_x - min_rect_elem.rect.left, hook_event.mouse_y - min_rect_elem.rect.top
                script += u"app{}{}.click_input(button='{}', coords=({}, {}))\n".format(
                    root_acc_name, item_acc_name, button, x, y)
        else:
            script += u"pywinauto.mouse.click(button='{}', coords=({}, {}))\n".format(
                button, hook_event.mouse_x, hook_event.mouse_y)

        return script


class KeyboardHandler(EventHandler):
    def run(self):
        hook_event = self.subpattern.hook_event
        if hook_event.control_tree_node:
            uia_ctrl = hook_event.control_tree_node
        else:
            uia_ctrl = "hotkey"
        self.log_parser.text_sequence.setdefault(uia_ctrl, "")
        self.log_parser.text_sequence[uia_ctrl] += hook_event.current_key


UIA_EVENT_PATTERN_MAP = [
    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                              ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED))),
     SelectionChangedHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name=EVENT.INVOKED),)),
     InvokeHandler),

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
     ToggleHandler),
    (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),)),
     SelectHandler),

    (EventPattern(hook_event=RecorderMouseEvent(current_key=None, event_type=HOOK_KEY_DOWN)),
     MouseClickHandler),

    (EventPattern(hook_event=RecorderKeyboardEvent(current_key=None, event_type=HOOK_KEY_DOWN)),
     KeyboardHandler)
]
