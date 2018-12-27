from abc import abstractmethod

from .recorder_defines import HOOK_MOUSE_RIGHT_BUTTON, HOOK_MOUSE_MIDDLE_BUTTON


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


class MouseClickHandler(EventHandler):
    def run(self):
        script = u""

        # Check if text has been typed
        for k, v in self.log_parser.text_sequence.items():
            item_name = k.names.get_preferred_name()
            script += u"app.{}.{}.type_keys(u'{}')\n".format(self.get_root_name(), item_name, v)
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
            coords = hook_event.mouse_x - min_rect_elem.rect.left, hook_event.mouse_y - min_rect_elem.rect.top
            script += u"app.{}.{}.click_input(button='{}', coords=({}, {}))\n".format(
                root_name, item_name, button, coords[0], coords[1])
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
