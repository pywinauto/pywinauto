def run_test():
    import os, time

    from .. import Application

    from .recorder import Recorder, hot_output
    from ..uia_defines import IUIA

    # app_path = os.path.join(os.path.dirname(__file__), r".\pywinauto_UIA\apps\WPF_samples\WpfApplication1.exe")
    app_path = 'notepad.exe'

    app = Application(backend="uia").start(app_path)
    time.sleep(0.3)

    rec = Recorder(app=app, record_props=True, record_focus=False, record_struct=False)
    rec.start()

    while not rec.recorder_stop_event.is_set():
        time.sleep(0.1)

    if not hot_output:
        time.sleep(1)
        print('\n===========================================\n')
        for event in rec.event_log:
            print(event)
