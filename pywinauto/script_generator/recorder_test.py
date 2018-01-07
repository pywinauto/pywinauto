import os
import time

from .. import Application

from .uia_recorder import UiaRecorder, ControlTree
from ..uia_defines import IUIA
from ..win32structures import POINT

import ctypes


def run_tree_test():
    app_path = 'notepad.exe'

    app = Application(backend="uia").start(app_path)
    time.sleep(0.3)

    top_window = app.top_window().wrapper_object()
    # top_window.menu_select('Help->AboutNotepad')
    time.sleep(0.5)

    control_tree = ControlTree(top_window)
    control_tree.print_tree()

    print(app.Dialog.OKButton.element_info)

    # ctypes.wintypes.POINT for ElementFromPoint()
    element = IUIA().iuia.ElementFromPoint(ctypes.wintypes.POINT(10, 10))


def run_recorder_test():
    # app_path = os.path.join(os.path.dirname(__file__), r"..\..\apps\WPF_samples\WpfApplication1.exe")
    app_path = 'notepad.exe'

    app = Application(backend="uia").start(app_path)

    rec = UiaRecorder(app=app, record_props=True, record_focus=False, record_struct=False, hot_output=True)
    rec.start()

    rec.wait()

    if not rec.hot_output:
        print("\n===========================================\n")
        for event in rec.event_log:
            print(event)

    print("\n===========================================\n")
    print(rec.script)
