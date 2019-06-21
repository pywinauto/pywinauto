from macos_functions import launch_application
import os, sys
from os import path
import macos_functions
import subprocess
from subprocess import Popen, PIPE
from .. import backend
from ..backend import registry
from ..element_info import ElementInfo
from ..base_wrapper import BaseWrapper
from AppKit import *
from ApplicationServices import *


sys.path.append( path.dirname( path.dirname( path.abspath(__file__))))

from ..base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication

if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(parent_dir)
    os.path.join
    from ..timings import Timings, wait_until, TimeoutError


backend.register('ax', ElementInfo, BaseWrapper)


class Application(BaseApplication):

    def __init__(self, backend="ax"):
        self.connected = None
        self.ns_app = None
        self.process = None 

        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]


    def start(self, name=None, bundle_id=None, new_instance=True):
        
        if name is not None:
            result = macos_functions.launch_application(name)
            if (not result):
                message = ('Could not create the process "%s"\n') % (name)
                raise AppStartError(message)

            
            self.ns_app = macos_functions.get_instance_of_app(name)
            if (self.ns_app is None):
                message = ('Could not get instance of "%s" app\n') % (name)
                raise AppStartError(message)
            return self

        if bundle_id is not None:
            result = macos_functions.launch_application_by_bundle(bundle_id, new_instance)
            NsArray = macos_functions.get_app_instance_by_bundle(bundle_id)
            self.ns_app = NsArray[0]


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
                raise ProcessNotFoundError('pid = ' + str(self.process_id))

        # TODO : add bundle support
        elif 'name' in kwargs:
            # For os x you have to pass just app name
            app = macos_functions.get_instance_of_app(kwargs['name'])
            if (app):
                self.ns_app = app
                self.connected = True
            else:
                raise ProcessNotFoundError('name = ' + str(kwargs['name']))
        elif 'bundle' in kwargs:
            # For os x you have to pass just app name
            app = macos_functions.get_app_instance_by_bundle(kwargs['bundle'])
            if (app):
                pid = app[0].processIdentifier()
                self.ns_app = app[0]
                self.connected = None
                AXUIElementCreateApplication(pid)
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
            proc_info = subprocess.check_output(["ps", "-p", str(self.ns_app.processIdentifier()), "-o", "%cpu"], universal_newlines=True)
            proc_info = proc_info.split("\n")
            return float(proc_info[1])
        except subprocess.CalledProcessError:
            import traceback
            traceback.print_exc()
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
                result = self.ns_app.terminate()
            else:
                result = self.ns_app.forceTerminate()

            if not result:
                return result

            self.wait_for_process_exit()

            self.ns_app = None
            return True

        return False    


    def kill_process(self):
        #kill like sigkill
        Popen(["kill", "-9",str(self.process_id)], stdout=PIPE).communicate()[0]

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
            #print(pid)
            app_by_pid = macos_functions.get_app_instance_by_pid(pid)
            
            # print(app_by_pid)
            # if app_by_pid:
            #     print(app_by_pid.localizedName())
            # print(name)
            if (app_by_pid and (app_by_pid.localizedName() == name)):
                result = True
        return result

    @property
    def process_id(self):
        identifier = None
        if (self.ns_app):
            identifier = self.ns_app.processIdentifier()
        return identifier

    def wait_for_process_running(self, timeout=None, retry_interval=None):
        """
        Waits for process to run until timeout reaches

        Raises TimeoutError exception if timeout was reached
        """
        if timeout is None:
            timeout = Timings.app_start_timeout
        if retry_interval is None:
            retry_interval = Timings.app_start_retry

        wait_until(timeout, retry_interval, self.is_process_running, value=True)

    def wait_for_process_exit(self, timeout=None, retry_interval=None):
        """
        Waits for process to exit until timeout reaches

        Raises TimeoutError exception if timeout was reached
        """
        if timeout is None:
            timeout = Timings.app_exit_timeout
        if retry_interval is None:
            retry_interval = Timings.app_exit_retry

        wait_until(timeout, retry_interval, self.is_process_running, value=False)
    
if __name__ == "__main__":
    app = BaseApplication()
