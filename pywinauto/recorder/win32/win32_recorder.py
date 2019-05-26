import threading
import ctypes
import timeit
import time
import re

from ..recorder_defines import EVENT, PROPERTY

from ... import win32_hooks
from ... import win32defines
from ... import handleprops
from ...win32structures import POINT
from ...win32_element_info import HwndElementInfo
from ...controls.hwndwrapper import InvalidWindowHandle
from win32api import LOWORD, HIWORD
import win32gui

from ..uia.uia_recorder import ProgressBarDialog
from ..control_tree import ControlTree, ControlTreeNode
from ..base_recorder import BaseRecorder
from ..recorder_defines import RecorderEvent, RecorderKeyboardEvent, RecorderMouseEvent, \
    ApplicationEvent, PropertyEvent, EventPattern, EVENT, PROPERTY, HOOK_MOUSE_LEFT_BUTTON, HOOK_KEY_DOWN

from ..event_handlers import EventHandler, MouseClickHandler, KeyboardHandler, MenuOpenedHandler, MenuClosedHandler

from .injector import Injector
from .common_controls_handlers import resolve_handle_to_event

APP_CLOSE_MSG = 0xFFFFFFFF

class Win32MenuSelectHandler(EventHandler):

    def _cut_at_tab(self, text):
        return re.compile(r"\t.*", re.UNICODE).sub("", text)

    def run(self):
        menu_item_text    = self._cut_at_tab(self.subtree[0].metadata["menu_item_text"])
        submenu_item_text = self._cut_at_tab(self.subtree[0].metadata["submenu_item_text"])
        return u"app{}.menu_select(u'{} -> {}')\n".format(self.get_root_name(), menu_item_text, submenu_item_text)

class Win32Recorder(BaseRecorder):

    _EVENT_PATTERN_MAP = [
        (EventPattern(hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
                  app_events=(ApplicationEvent(name="MENUSELECT"),)), Win32MenuSelectHandler),
        (EventPattern(hook_event=RecorderMouseEvent(current_key=None, event_type=HOOK_KEY_DOWN)), MouseClickHandler),
        (EventPattern(hook_event=RecorderKeyboardEvent(current_key=None, event_type=HOOK_KEY_DOWN)), KeyboardHandler)
    ]

    _APPROVED_MESSAGES_LIST = [
        win32defines.WM_COMMAND,
        win32defines.WM_NOTIFY,

        win32defines.WM_KEYUP,
        win32defines.WM_SETFOCUS,

        win32defines.WM_CONTEXTMENU,
        win32defines.WM_ENTERMENULOOP,
        win32defines.WM_EXITMENULOOP,
        win32defines.WM_MENUCOMMAND,
        win32defines.WM_NEXTMENU,
        win32defines.WM_COMPAREITEM,
        win32defines.WM_MEASUREITEM,

        win32defines.WM_MENUSELECT,
        win32defines.WM_SYSCOMMAND,
    ]

    def __init__(self, app, config, record_props=True, record_focus=False, record_struct=False):
        super(Win32Recorder, self).__init__(app=app, config=config)
        if app.backend.name != "win32":
            raise TypeError("app must be a pywinauto.Application object of 'win32' backend")

        self.last_kbd_hwnd = None
        self.app = app
        self.listen = False
        self.hook = win32_hooks.Hook()
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

        self.prev_hwnd = None
        self.prev_msg_id = None
        self.prev_time = None
        self.menu_data = {}

    def _setup(self):
        try:
            self.listen = True
            self.injector = Injector(self.wrapper, approved_messages_list = self._APPROVED_MESSAGES_LIST)
            self.control_tree = ControlTree(self.wrapper, skip_rebuild=True)
            self._update(rebuild_tree=True, start_message_queue=True)
        except:
            self.stop()

    def _cleanup(self):
        self.listen = False
        self.hook.stop()
        if hasattr(self, 'message_thread'):
            self.message_thread.join(1)
        self.hook_thread.join(1)
        if hasattr(self, 'injector'):
            self.injector.close_pipe()
        self._parse_and_clear_log()
        self.script += u"app.kill()\n"

    def _pause_hook_thread(self):
        self.hook.stop()
        time.sleep(1)
        self.hook_thread.join(1)

    def _resume_hook_thread(self):
        self.hook_thread = threading.Thread(target=self._hook_target)
        self.hook_thread.start()

    def _update(self, rebuild_tree=False, start_message_queue=False):
        if rebuild_tree:
            pbar_dlg = ProgressBarDialog(self.control_tree.root.rect if self.control_tree.root else None)
            pbar_dlg.show()

            self._pause_hook_thread()

            rebuild_tree_thr = threading.Thread(target=self._rebuild_control_tree)
            rebuild_tree_thr.start()
            pbar_dlg.pbar.SetPos(50)
            rebuild_tree_thr.join()
            pbar_dlg.pbar.SetPos(100)
            pbar_dlg.close()

            self._resume_hook_thread()

        if start_message_queue:
            self.message_thread = threading.Thread(target=self._message_queue)
            self.message_thread.start()

    def _rebuild_control_tree(self):
        if self.config.verbose:
            start_time = timeit.default_timer()
            print("[_rebuild_control_tree] Rebuilding control tree")
        self.control_tree.rebuild()
        if self.config.verbose:
            print("[_rebuild_control_tree] Finished rebuilding control tree. Time = {}".format(
                timeit.default_timer() - start_time))

    def _get_keyboard_node(self):
        node = None
        if not self.last_kbd_hwnd:
            time.sleep(0.1)
        if self.control_tree and self.last_kbd_hwnd:
            focused_element_info = HwndElementInfo(self.last_kbd_hwnd)
            node = self.control_tree.node_from_element_info(focused_element_info)
        return node

    def _get_mouse_node(self, mouse_event):
        node = None
        if self.control_tree:
            node = self.control_tree.node_from_point(POINT(mouse_event.mouse_x, mouse_event.mouse_y))
        return node

    def _message_queue(self):
        try:
            while self.listen:
                try:
                    self._handle_message(self.injector.read_massage())
                except InvalidWindowHandle:
                    #TODO: fix it by creating tree snapshots
                    print("WARNIN: message's window already closed")
        except Exception as e:
            print(e)
            self.stop()

    def _hook_target(self):
        self.hook.handler = self._handle_hook_event
        self.hook.hook(keyboard=True, mouse=True)

    def _handle_hook_event(self, hook_event):
        event = None
        if isinstance(hook_event, win32_hooks.KeyboardEvent):
            event = RecorderKeyboardEvent.from_hook_keyboard_event(hook_event)
            event.control_tree_node = self._get_keyboard_node()
        elif isinstance(hook_event, win32_hooks.MouseEvent):
            event = RecorderMouseEvent.from_hook_mouse_event(hook_event)
            event.control_tree_node = self._get_mouse_node(event)
        if event and event.control_tree_node:
            self.add_to_log(event)
        elif not event.control_tree_node:
            print("WARNING: can't find contol tree node, ensure you call _rebuild in right time")

    def _hwnd_element_from_message(self, msg):
        parent_handle = msg.hWnd
        child_handle = LOWORD(msg.wParam)
        if parent_handle == 0 or child_handle == 0:
            return None
        element_handle = 0
        try:
            element_handle = win32gui.GetDlgItem(parent_handle, child_handle)
        except:
            element_handle = parent_handle
        return HwndElementInfo(element_handle)

    def _resolve_component(self, msg):
        if msg.message == win32defines.WM_COMMAND:
            return self._hwnd_element_from_message(msg)
        elif msg.message == win32defines.WM_NOTIFY:
            return HwndElementInfo(msg.hWnd)
        return None

    def _should_skip_msg(self, msg):
        if msg.message == self.prev_msg_id and msg.hWnd == self.prev_hwnd and msg.time == self.prev_time:
            return True

        self.prev_msg_id = msg.message
        self.prev_hwnd = msg.hWnd
        self.prev_time = msg.time
        return False

    def _remove_menu_rect_clicks(self, menu_item_rect):
        def skip_this(event, item_rect):
            return isinstance(event, RecorderMouseEvent) and (event.mouse_x, event.mouse_y) in item_rect
        self.event_log = [event for event in self.event_log if not skip_this(event, menu_item_rect)]

    def _create_dummy_tree_node(self):
        root = self.control_tree.root
        return ControlTreeNode(root.wrapper, root.names, root.ctrl_type, root.rect)

    def _control_message_handler(self, msg):
        component = self._resolve_component(msg)
        if component:
            class_name, event_name = resolve_handle_to_event(component, msg, True)
            if class_name and event_name:
                print('{} - {}'.format(class_name, event_name))

    def _menu_open_handler(self, msg):
        if msg.message != win32defines.WM_MENUSELECT:
            return

        selected_index = msg.wParam & 0xFFFF
        menu_wrapper = self.app.window(handle = msg.hWnd).menu()
        if menu_wrapper.handle == msg.lParam:
            def submenu_items(item_index):
                current_parent = menu_wrapper.item(item_index)
                items = { item.item_id() : (item.text(), item.rectangle()) for item in current_parent.sub_menu().items() }
                items[-1] = current_parent.text()
                items[-2] = current_parent.rectangle()
                return items

            self.menu_data["submenus"] = []
            self.menu_data["submenus"].append(submenu_items(selected_index))
            if selected_index > 0:
                self.menu_data["submenus"].append(submenu_items(selected_index - 1))
            if selected_index < menu_wrapper.item_count() - 1:
                self.menu_data["submenus"].append(submenu_items(selected_index + 1))

    def _menu_choose_handler(self, msg):
        if msg.message != win32defines.WM_COMMAND or HIWORD(msg.wParam) != 0 or msg.lParam != 0:
            return

        menu_id = LOWORD(msg.wParam)
        for submenu_data in self.menu_data["submenus"]:
            if menu_id in submenu_data:
                selected_item, parent_text, parent_rect = submenu_data[menu_id], submenu_data[-1], submenu_data[-2]
                break

        if not selected_item:
            return

        self._remove_menu_rect_clicks(parent_rect)
        self._remove_menu_rect_clicks(selected_item[1])
        self.menu_event = RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN)
        self.menu_event.control_tree_node = self._create_dummy_tree_node()
        self.menu_event.control_tree_node.metadata["menu_item_text"] = parent_text
        self.menu_event.control_tree_node.metadata["submenu_item_text"] = selected_item[0]
        self.add_to_log(self.menu_event)
        self.add_to_log(ApplicationEvent(name="MENUSELECT", sender=None))

    def _type_keys_handle_handler(self, msg):
        if msg.message == win32defines.WM_SETFOCUS or msg.message == win32defines.WM_KEYUP:
            self.last_kbd_hwnd = msg.hWnd

    _message_handlers = [
        _type_keys_handle_handler,
        _control_message_handler,
        _menu_open_handler,
        _menu_choose_handler,
    ]

    def _handle_message(self, msg):
        if not msg or msg.message == APP_CLOSE_MSG:
            self.stop()
            return

        if self._should_skip_msg(msg):
            return

        for handle in self._message_handlers:
            handle(self, msg)

    @property
    def event_patterns(self):
        """Return backend-specific patterns dict"""
        return self._EVENT_PATTERN_MAP
