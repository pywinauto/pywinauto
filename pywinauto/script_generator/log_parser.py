from .recorder_events import RecorderEvent, RecorderMouseEvent, RecorderKeyboardEvent, UIAEvent, PropertyEvent, \
    FocusEvent, StructureEvent


class LogParser(object):
    def __init__(self, recorder):
        self.recorder = recorder

        self.menu_sequence = []

    def parse_current_log(self):
        script = ""

        for event in self.recorder.event_log:
            if isinstance(event, RecorderEvent):
                if isinstance(event, RecorderMouseEvent):
                    if event.current_key == "LButton" and event.event_type == "key down":
                        if event.control_tree_node:
                            # Choose appropriate name
                            item_name = [name for name in event.control_tree_node.names
                                         if len(name) > 0 and not " " in name][-1]

                            joint_log = "\n".join([str(ev) for ev in self.recorder.event_log])
                            if "Invoke_Invoked" in joint_log:
                                script += "app.{}.{}.invoke()\n".format(self.recorder.control_tree.root_name, item_name)
                            elif "ToggleToggleState" in joint_log:
                                script += "app.{}.{}.toggle()\n".format(self.recorder.control_tree.root_name, item_name)
                            elif "MenuOpened" in joint_log:
                                self.menu_sequence = [event.control_tree_node.ctrl.window_text(), ]
                            elif "MenuClosed" in joint_log:
                                menu_item_text = event.control_tree_node.ctrl.window_text()
                                script += "app.{}.menu_select('{}')\n".format(
                                    self.recorder.control_tree.root_name,
                                    " -> ".join(self.menu_sequence + [menu_item_text, ]))
                                self.menu_sequence = [menu_item_text, ]
                            else:
                                script += "app.{}.{}.click_input()\n".format(self.recorder.control_tree.root_name,
                                                                             item_name)
                    elif event.event_type == "key down":
                        if event.current_key == "RButton":
                            button = "right"
                        elif event.current_key == "Wheel":
                            button = "wheel"
                        else:
                            button = "left"
                        script += "pywinauto.mouse.click(button='{}', coords=({}, {}))\n".format(button, event.mouse_x,
                                                                                                 event.mouse_y)
                elif isinstance(event, RecorderKeyboardEvent):
                    pass
            else:
                script += "print('{}')\n".format(event)

        return script
