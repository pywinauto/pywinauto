import os
import time
import sys
from os import path
import subprocess
from subprocess import Popen, PIPE

from AppKit import NSWorkspaceLaunchNewInstance, NSWorkspaceLaunchAllowingClassicStartup
from Foundation import NSAppleEventDescriptor
from ApplicationServices import AXUIElementCreateApplication

from . import macos_functions
from . import ax_element_info
from .. import backend
from ..backend import registry
from ..element_info import ElementInfo
from ..base_wrapper import BaseWrapper
from ..base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)
os.path.join
from ..timings import Timings, wait_until
backend.register('ax', ElementInfo, BaseWrapper)


class Pidmonitor():
    
    pid = None
    pid_before = []

    @staticmethod
    def pid_before():
        liste1 = []
        for apps in macos_functions.running_applications():
            liste1.append(apps.processIdentifier()) 
        return liste1

    @staticmethod        
    def pid_after():
        liste2 = [] 
        ax_element_info.cache_update()
        for apps in macos_functions.running_applications():
            liste2.append(apps.processIdentifier())
        return liste2


class Application(BaseApplication):

    Pidmonitor.pid_before = Pidmonitor.pid_before()

    def __init__(self, backend="ax"):
        self.connected = False
        self.ns_app = None
        self.process = None
        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]

    def start(self, name=None, bundle_id=None, new_instance=True):

        if name is not None and bundle_id is not None:
              raise ValueError('Parameters name and bundle_id are mutually exclusive. Use only one of them at the moment.')

        if name is not None:
            bundle = macos_functions.bundle_identifier_for_application_name(name)
            print(bundle)
            macos_functions.launch_application_by_bundle(bundle, new_instance)
            NsArray = macos_functions.get_app_instance_by_bundle(bundle)

            self.ns_app = NsArray[0]
            if (self.ns_app is None):
                message = ('Could not get instance of "%s" app\n') % (name)
                raise AppStartError(message)

        if bundle_id is not None: 
            if (new_instance):
                param = NSWorkspaceLaunchNewInstance
            else:
                param = NSWorkspaceLaunchAllowingClassicStartup

            r = macos_functions.get_ws_instance().launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(bundle_id,
                    param,
                    NSAppleEventDescriptor.nullDescriptor(),
                    None)
            if not r[0]:
                    raise AppStartError('Could not launch application by bundle id "{}". Error code: {}'.format(bundle_id, r))

            NsArray = macos_functions.get_app_instance_by_bundle(bundle_id)
            self.ns_app = NsArray[0]

        self.connected = True

        def app_launched(pid_before = Pidmonitor.pid_before):
            pid_after = Pidmonitor.pid_after()
            for element in pid_after:
                if element not in pid_before:
                    name_app = macos_functions.get_app_instance_by_pid(element)
                    print(name_app)
                    if name == name_app.localizedName() or bundle_id == name_app.bundleIdentifier():
                        Pidmonitor.pid = element
                        return True
            return False

        if new_instance:
            wait_until(Timings.app_start_timeout, Timings.app_start_retry, app_launched, value=True)
            self.ns_app = macos_functions.get_app_instance_by_pid(Pidmonitor.pid)

        def app_idle():
            ax_element_info.cache_update()
            nom = self.ns_app.localizedName()
            elem = ax_element_info.AxElementInfo()
            for app in elem.children():
                if app.name == nom:
                    return True
            return False

        wait_until(Timings.app_start_timeout, Timings.app_start_retry, app_idle, value=True)

        return self

    def connect(self, **kwargs):
        
        self.connected = False
        if 'process' in kwargs:
            app = macos_functions.get_app_instance_by_pid(kwargs['process'])
            if (app):
                self.ns_app = app
                self.connected = True
            else:
                raise ProcessNotFoundError('pid = ' + str(self.process_id))

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
        return self

    def cpu_usage(self, interval=None):
        """Return CPU usage percent during specified number of seconds"""
        if not self.ns_app and not self.connected:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        if interval:
            time.sleep(interval)
        try:
            proc_info = subprocess.check_output(["ps", "-p", str(self.ns_app.processIdentifier()),
                                                 "-o", "%cpu"], universal_newlines=True)
            proc_info = proc_info.split("\n")
            return float(proc_info[1])
        except subprocess.CalledProcessError:
            # import traceback
            # traceback.print_exc()
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
            ax_element_info.cache_update()
            self.ns_app = None
            return True
        return False

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
