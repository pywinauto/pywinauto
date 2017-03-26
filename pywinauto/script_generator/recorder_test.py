import os, time

from .. import Application

from .recorder import Recorder, ControlTree
from ..uia_defines import IUIA
from ..win32structures import POINT

def run_tree_test():
    app_path = 'notepad.exe'

    app = Application(backend="uia").start(app_path)
    time.sleep(0.3)

    top_window = app.top_window().wrapper_object()
    top_window.menu_select('Help->AboutNotepad')
    time.sleep(0.5)

    control_tree = ControlTree(top_window)
    control_tree.print_tree()

    print(app.Dialog.OKButton.element_info)


def run_test():
    # app_path = os.path.join(os.path.dirname(__file__), r".\pywinauto_UIA\apps\WPF_samples\WpfApplication1.exe")
    app_path = 'notepad.exe'

    app = Application(backend="uia").start(app_path)
    time.sleep(0.3)

    rec = Recorder(app=app, record_props=True, record_focus=False, record_struct=False)
    rec.start()

    # Wait for recorder to finish
    rec.recorder_thread.join()

    if not rec.hot_output:
        time.sleep(1)
        print('\n===========================================\n')
        for event in rec.event_log:
            print(event)
