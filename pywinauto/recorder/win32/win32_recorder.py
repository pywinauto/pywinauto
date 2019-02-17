import threading
import timeit

from comtypes import COMObject, COMError

from ... import win32_hooks
from ...win32structures import POINT
from ...uia_element_info import UIAElementInfo

from ..control_tree import ControlTree
from ..base_recorder import BaseRecorder

from pywin.mfc import dialog
import win32ui
import win32con
from ctypes import wintypes
import ctypes

from .injector import Injector

msg_id_to_key = {getattr(win32con, attr_name): attr_name for attr_name in dir(win32con) if attr_name.startswith('WM_')}

def print_winmsg(msg):
    print("hWnd:{}".format(str(msg.hWnd)))
    print("message:{}".format((msg_id_to_key[msg.message] if msg.message in msg_id_to_key else str(msg.message))))
    print("wParam:{}".format(str(msg.wParam)))
    print("lParam:{}".format(str(msg.lParam)))
    print("time:{}".format(str(msg.time)))
    print("pt:{}".format(str(msg.pt.x) + ',' + str(msg.pt.x)))

class Win32Recorder(BaseRecorder):

    def __init__(self, app, config, record_props=True, record_focus=False, record_struct=False):
        super(Win32Recorder, self).__init__(app=app, config=config)

        if app.backend.name != "win32":
            raise TypeError("app must be a pywinauto.Application object of 'win32' backend")

        self.app = app[config.cmd]
        self.injector = None
        self.socket = None
        self.listen = False
        self.record_props = record_props
        self.record_focus = record_focus
        self.record_struct = record_struct

    def _setup(self):
        try:
            # Add event handlers to all app's controls
            self.injector = Injector(self.app)
            print(self.injector)
            self.socket = self.injector.socket
            print(self.socket)
            self.listen = True
            self.control_tree = ControlTree(self.wrapper, skip_rebuild=True)
            self._update(rebuild_tree=True)
        except Exception as exc:
            print(exc)
            # TODO: Sometime we can't catch WindowClosed event in WPF applications
            self.listen = False
            self.stop()
            self.script += u"app.kill()\n"
            # Skip exceptions thrown by AddPropertyChangedEventHandler
            # print("Exception: {}".format(exc))

    def _cleanup(self):
        self.listen = False

    def _update(self, rebuild_tree=False, add_handlers_to=None):
        if rebuild_tree:
            self._rebuild_control_tree()
        self.hook_thread = threading.Thread(target=self.hook_target)
        self.hook_thread.start()

    def _rebuild_control_tree(self):
        if self.config.verbose:
            start_time = timeit.default_timer()
            print("[_rebuild_control_tree] Rebuilding control tree")
        self.control_tree.rebuild()
        if self.config.verbose:
            print("[_rebuild_control_tree] Finished rebuilding control tree. Time = {}".format(
                timeit.default_timer() - start_time))

    def hook_target(self):
        """Target function for hook thread"""
        while self.listen:
            print("SPAM")
            msg = wintypes.MSG()
            buff = self.socket.recvfrom(1024)
            print("SPAM1")
            ctypes.memmove(ctypes.pointer(msg), buff[0], ctypes.sizeof(msg))
            self.handle_message(msg)
            if msg.message == win32con.WM_QUIT:
                self.stop()

    def handle_message(self, message):
        """Callback for keyboard and mouse events"""
        print_winmsg(message)