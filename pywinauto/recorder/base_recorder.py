import sys
import threading
from abc import abstractmethod

from .. import __version__ as recorded_version
from ..application import Application, get_process_command_line_wmi
from .log_parser import LogParser


def synchronized_method(method):
    """Decorator for a synchronized class method"""
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "_lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name):
                setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method


class BaseRecorder(object):
    """Record hook (keyboard, mouse) and back-end events"""

    def __init__(self, app, **kwargs):
        super(BaseRecorder, self).__init__()

        if not isinstance(app, Application):
            raise TypeError("app must be a pywinauto.Application object")

        if not app.is_process_running():
            raise TypeError("Application must be already running")

        self.wrapper = app.top_window().wrapper_object()

        self.verbose = kwargs.get("verbose", False)
        # Output events straight away (for debug purposes)
        self.hot_output = kwargs.get("hot_output", False)

        # Main recorder thread
        self.recorder_thread = threading.Thread(target=self.recorder_target)
        self.recorder_thread.daemon = True

        # Thread events to indicate recorder status (used as an alternative to an infinite loop)
        self.recorder_start_event = threading.Event()
        self.recorder_stop_event = threading.Event()

        # Hook event thread
        self.hook_thread = threading.Thread(target=self.hook_target)
        self.hook_thread.daemon = True

        # Log parser
        self.event_log = []
        self.control_tree = None
        self.log_parser = LogParser(self, self.verbose)

        # Generated script
        try:
            cmd = get_process_command_line_wmi(app.process)
        except Exception:
            cmd = "INSERT_CMD_HERE"

        # TODO: detect if pywinauto imported from custom location
        self.script = u"# encoding: {}\n".format(sys.getdefaultencoding())
        self.script += u"import os, sys\n"
        self.script += u"script_dir = os.path.dirname(__file__)\n"
        self.script += u"sys.path.append(script_dir)\n"
        self.script += u"import pywinauto\n"
        # TODO: check version: to int: if tuple(pywinauto.__version__.split('.')) > tuple(recorded_version.split('.')):
        self.script += u"recorded_version = {}\n".format(repr(recorded_version))
        self.script += u"print('Recorded with pywinauto-{}'.format(recorded_version))\n"
        self.script += u"print('Running with pywinauto-{}'.format(pywinauto.__version__))\n\n"
        self.script += u"app = pywinauto.Application(backend='{}').start('{}')\n".format(app.backend.name, cmd)
        if self.hot_output:
            print(self.script)

    @synchronized_method
    def add_to_log(self, item):
        """
        Add *item* to event log.
        This is a synchronized method.
        """
        self.event_log.append(item)
        if self.verbose:
            print(item)

    @synchronized_method
    def clear_log(self):
        """
        Clear event log.
        This is a synchronized method.
        """
        self.event_log = []

    def is_active(self):
        """Returns True if Recorder is active"""
        return self.recorder_thread.is_alive() or self.hook_thread.is_alive()

    def start(self):
        """Start Recorder"""
        self.recorder_thread.start()
        self.hook_thread.start()

    def stop(self):
        """Stop Recorder"""
        self.recorder_stop_event.set()

    def wait(self):
        """Wait for recorder to finish"""
        if self.is_active():
            self.recorder_thread.join()

    def _parse_and_clear_log(self):
        """Parse current event log and clear it afterwards"""
        new_script = self.log_parser.parse_current_log()
        if self.hot_output:
            print(new_script)
        self.script += new_script
        self.clear_log()

    @abstractmethod
    def _setup(self):
        """Setup Recorder (initialize hook, subscribe to events, etc.)"""
        pass

    @abstractmethod
    def _cleanup(self):
        pass

    """
    Target functions
    """

    def recorder_target(self):
        """Target function for recorder thread"""
        self._setup()
        self.recorder_start_event.set()

        # Wait Recorder is stopped
        self.recorder_stop_event.wait()

        self._cleanup()

    @abstractmethod
    def hook_target(self):
        """Target function for hook thread"""
        pass
