import threading
import ctypes
import timeit
import time

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
from ..control_tree import ControlTree
from ..base_recorder import BaseRecorder
from ..recorder_defines import RecorderEvent, \
    RecorderKeyboardEvent, \
    RecorderMouseEvent, \
    ApplicationEvent, \
    PropertyEvent

from .injector import Injector
from .common_controls_handlers import resolve_handle_to_event

msg_id_to_key = {getattr(win32defines, attr_name): attr_name for attr_name in dir(win32defines) if attr_name.startswith('WM_') or attr_name.startswith('CB_')}

def print_winmsg(msg):
    pass
    #print(handleprops.classname(msg.hWnd))
    print("message:{}".format((msg_id_to_key[msg.message] if msg.message in msg_id_to_key else str(msg.message))))

class Win32Recorder(BaseRecorder):
    _APPROVED_MESSAGES_LIST = [
        win32defines.WM_CONTEXTMENU,
        win32defines.WM_ENTERMENULOOP,
        win32defines.WM_EXITMENULOOP,
        # win32defines.WM_GETTITLEBARINFOEX,
        win32defines.WM_MENUCOMMAND,
        # win32defines.WM_MENUDRAG,
        # win32defines.WM_MENUGETOBJECT,
        # win32defines.WM_MENURBUTTONUP,
        win32defines.WM_NEXTMENU,
        # win32defines.WM_UNINITMENUPOPUP,
        win32defines.WM_COMMAND,
        292,
        0x0126,
        0x0124,
        0x033F,
        0x011F,
        0x0120,
        win32defines.WM_QUIT,
        win32defines.WM_NOTIFY,
        win32defines.WM_KEYUP,
        win32defines.WM_SETFOCUS,
        win32defines.WM_COMPAREITEM,
        # win32defines.WM_DRAWITEM,
        win32defines.WM_MEASUREITEM,
    ]

    def __init__(self, app, config, record_props=True, record_focus=False, record_struct=False):
        super(Win32Recorder, self).__init__(app=app, config=config)
        if app.backend.name != "win32":
            raise TypeError("app must be a pywinauto.Application object of 'win32' backend")

        self.last_kbd_hwnd = None
        self.app = app
        self.dlg = app[config.cmd]
        self.listen = False
        self.hook = win32_hooks.Hook()
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

    def _setup(self):
        try:
            self.injector = Injector(self.dlg, approved_messages_list = self._APPROVED_MESSAGES_LIST)
            self.socket = self.injector.socket
            self.listen = True
            self.control_tree = ControlTree(self.wrapper, skip_rebuild=True)
            self._update(rebuild_tree=True, start_message_queue=True)
        except:
            self.stop()

    def _cleanup(self):
        self.listen = False
        self.hook.stop()
        self.message_thread.join(1)
        self.hook_thread.join(1)
        self.socket.close()
        self._parse_and_clear_log()
        self.script += u"app.kill()\n"

    def _pause_hook_thread(self):
        self.hook.stop()
        time.sleep(1)
        self.hook_thread.join(1)

    def _resume_hook_thread(self):
        self.hook_thread = threading.Thread(target=self.hook_target)
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
            self.message_thread = threading.Thread(target=self.message_queue)
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

    def _read_message(self):
        msg = ctypes.wintypes.MSG()
        buff = self.socket.recvfrom(1024)
        ctypes.memmove(ctypes.pointer(msg), buff[0], ctypes.sizeof(msg))
        return msg

    def message_queue(self):
        """infine listening socket while it's alive"""
        try:
            while self.listen:
                self.handle_message(self._read_message())
        except InvalidWindowHandle:
            print("WARNIN: message's window already closed")
        except Exception as e:
            print(e)
            self.stop()

    def hook_target(self):
        """Target function for hook thread"""
        self.hook.handler = self.handle_hook_event
        self.hook.hook(keyboard=True, mouse=True)

    def handle_hook_event(self, hook_event):
        """Callback for keyboard and mouse events"""
        if isinstance(hook_event, win32_hooks.KeyboardEvent):
            keyboard_event = RecorderKeyboardEvent.from_hook_keyboard_event(hook_event)
            self.add_to_log(keyboard_event)
        elif isinstance(hook_event, win32_hooks.MouseEvent):
            mouse_event = RecorderMouseEvent.from_hook_mouse_event(hook_event)
            mouse_event.control_tree_node = self._get_mouse_node(mouse_event)
            self.add_to_log(mouse_event)

    def hwnd_element_from_message(self, msg):
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

    def handle_message(self, msg):
        """Callback for keyboard and mouse events"""
        if msg.message == win32defines.WM_SETFOCUS or msg.message == win32defines.WM_KEYUP:
            self.last_kbd_hwnd = msg.hWnd
        elif msg.message == win32defines.WM_QUIT:
            time.sleep(0.1)
            if not self.app.is_process_running():
                self.stop()

        if msg.message == win32defines.WM_COMMAND:
            component = self.hwnd_element_from_message(msg)
            if component:
                event_name = resolve_handle_to_event(component, msg, True)
                if event_name:
                    print(event_name)

        if msg.message == win32defines.WM_NOTIFY:
            component = HwndElementInfo(msg.hWnd)
            if component:
                event_name = resolve_handle_to_event(component, msg, False)
                if event_name:
                    print(event_name)

