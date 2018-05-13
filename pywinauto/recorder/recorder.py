import threading

from abc import ABCMeta, abstractmethod

from .. import Application

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


class Recorder(object):
    """Record hook (keyboard, mouse) and back-end events"""

    __metaclass__ = ABCMeta

    def __init__(self, app=None, hot_output=True):
        super(Recorder, self).__init__()

        if not isinstance(app, Application):
            raise TypeError("app must be a pywinauto.Application object")

        self.ctrl = app.top_window().wrapper_object()

        # Output events straight away (for debug purposes)
        self.hot_output = hot_output

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
        self.log_parser = LogParser(self)

        # Generated script
        self.script = "app = pywinauto.Application(backend='{}').start('INSERT_CMD_HERE')\n".format(app.backend.name)

    @synchronized_method
    def add_to_log(self, item):
        """
        Add *item* to event log.
        This is a synchronized method.
        """
        self.event_log.append(item)
        if self.hot_output:
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
        self.script += self.log_parser.parse_current_log()
        self.clear_log()

    @abstractmethod
    def _setup(self):
        """Setup Recorder (initialize hook, subscrive to events, etc.)"""
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
