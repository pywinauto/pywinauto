from macos_functions import launch_application
import os, sys
from os import path
import macos_functions
import subprocess
from .. import backend
from ..backend import registry
from ..element_info import ElementInfo
from ..base_wrapper import BaseWrapper

sys.path.append( path.dirname( path.dirname( path.abspath(__file__))))

from ..base_application import BaseApplication

backend.register('ax', ElementInfo, BaseWrapper)


class Application(BaseApplication):

    def __init__(self, backend="ax"):
        self.connected = None
        self.ns_app = None

        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]

    def start(self, cmd_line):

        result = macos_functions.launch_application(cmd_line)
        if (not result):
            message = ('Could not create the process "%s"\n') % (cmd_line)
            raise AppStartError(message)
        
        self.instance = macos_functions.get_instance_of_app(cmd_line)
        
        if (self.instance is None):
            message = ('Could not get instance of "%s" app\n') % (cmd_line)
            raise AppStartError(message)
        return self

    def connect(self, **kwargs):
        # TODO!
        """Connect to an already running process
        The action is performed according to only one of parameters
        :param process: a process ID of the target
        :param path: a path used to launch the target
        .. seealso::
           :func:`pywinauto.findwindows.find_elements` - the keyword arguments that
           are also can be used instead of **process**, **handle** or **path**
        """
        connected = False
        if 'process' in kwargs:
            # self.process = kwargs['process']
            app = macos_functions.get_app_instance_by_pid(kwargs['process'])
            if (app):
                self.ns_app = app
                self.connected = True
            else:
                raise ProcessNotFoundError('pid = ' + str(process_id))

        # TODO : add bundle support
        elif 'name' in kwargs:
            # For os x you have to pass just app name
            app = macos_functions.get_instance_of_app(kwargs['path'])
            if (app):
                self.ns_app = app
                self.connected = True
            else:
                raise ProcessNotFoundError('path = ' + str(kwargs['path']))
        elif 'bundle' in kwargs:
            # For os x you have to pass just app name
            app = macos_functions.get_app_instance_by_bundle(kwargs['bundle'])
            if (app):
                self.ns_app = app
                self.connected = True
            else:
                raise ProcessNotFoundError('bundle = ' + str(kwargs['bundle']))

    def cpu_usage(self, interval=None):
        """Return CPU usage percent during specified number of seconds"""
        if not self.ns_app and self.connected:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        if interval:
            time.sleep(interval)
        try:
            proc_info = subprocess.check_output(["ps", "-p", str(l.processIdentifier()), "-o", "%cpu"], universal_newlines=True)
            proc_info = proc_info.split("\n")
            return float(proc_info[1])
        except Exception:
            raise ProcessNotFoundError()

    def kill(self, soft=False):
        """
        Try to close and kill the application
        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        This should only be used when it is OK to kill the process like you
        would do in task manager.
        """

        if (self.ns_app):
            if (soft):
                return self.ns_app.terminate()
            else:
                return self.ns_app.forceTerminate()

    def is_process_running(self):
        """
        Checks that process is running.
        Can be called before start/connect.
        Returns True if process is running otherwise - False
        """
        result = False
        if (self.ns_app):
            name = self.ns_app.localizedName()
            pid = self.process_id
            app_by_pid = macos_functions.get_app_instance_by_pid(pid)
            if (app_by_pid and (app_by_pid.localizedName() == name)):
                result = True
        return result

    @property
    def process_id(self):
        identifier = None
        if (self.ns_app):
            identifier = self.ns_app.processIdentifier()
        return identifier
    
if __name__ == "__main__":
    app = BaseApplication()
