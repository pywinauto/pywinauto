from .recorder_defines import *


class LogParser(object):
    def __init__(self, recorder):
        self.recorder = recorder

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
                # TODO: only add key down events, assume that user down only clicks
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
            print("================================================================================\n"
                  "Hook event: {}\n    Application events: {}\n"
                  "".format(hook_event, application_events))

            if isinstance(hook_event, RecorderMouseEvent):
                # What happened after click (lbutton down-up)
                if hook_event.current_key == "LButton" and hook_event.event_type == "key down":
                    # Check if text has been typed
                    for k, v in self.text_sequence.items():
                        item_name = next(name for name in k.names)

                        item_name = [name for name in k.names if len(name) > 0 and not " " in name][-1]
                        script += "app.{}.{}.DO_SOMETHING_WITH_TEXT('{}')\n".format(
                            self.recorder.control_tree.root_name, item_name, v)
                    self.text_sequence = {}

                    if hook_event.control_tree_node:
                        item_name = [name for name in hook_event.control_tree_node.names
                                     if len(name) > 0 and not " " in name][-1]

                        joint_log = "\n".join([str(ev) for ev in application_events])
                        if any(e for e in application_events if e.name == EVENT.INVOKED):
                            script += "app.{}.{}.invoke()\n".format(self.recorder.control_tree.root_name, item_name)
                        elif any(e for e in application_events if e.name == EVENT.MENU_OPENED):
                            self.menu_sequence = [hook_event.control_tree_node.ctrl.window_text(), ]
                        elif any(e for e in application_events if e.name == EVENT.MENU_CLOSED):
                            menu_item_text = hook_event.control_tree_node.ctrl.window_text()
                            script += "app.{}.menu_select('{}')\n".format(
                                self.recorder.control_tree.root_name,
                                " -> ".join(self.menu_sequence + [menu_item_text, ]))
                            self.menu_sequence = [menu_item_text, ]
                        else:
                            script += "app.{}.{}.click_input()\n".format(self.recorder.control_tree.root_name,
                                                                         item_name)
                elif hook_event.event_type == "key down":
                    if hook_event.current_key == "RButton":
                        button = "right"
                    elif hook_event.current_key == "Wheel":
                        button = "wheel"
                    else:
                        button = "left"
                    script += "pywinauto.mouse.click(button='{}', coords=({}, {}))\n".format(button, hook_event.mouse_x,
                                                                                             hook_event.mouse_y)
            elif isinstance(hook_event, RecorderKeyboardEvent):
                if hook_event.event_type == "key down":
                    if hook_event.control_tree_node:
                        uia_ctrl = hook_event.control_tree_node
                    else:
                        uia_ctrl = "hotkey"
                    self.text_sequence.setdefault(uia_ctrl, "")
                    self.text_sequence[uia_ctrl] += hook_event.current_key

            print("================================================================================\n")

        return script
