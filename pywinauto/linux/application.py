import sys
import os.path
import pickle
import time
import warnings
import multiprocessing
import locale
import subprocess
import shlex

from pywinauto.backend import registry
from ..base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication


class Application(BaseApplication):

    def __init__(self, backend="atspi"):
        self.process = None
        self.xmlpath = ''

        self.match_history = []
        self.use_history = False
        self.actions = None # TODO Action logger for linux
        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]

    def __getitem__(self, key):
        """Find the specified dialog of the application"""
        # delegate searching functionality to self.window()
        # return self.window(best_match=key)
        return None

    def __getattribute__(self, attr_name):
        """Find the specified dialog of the application"""
        if attr_name in ['__dict__', '__members__', '__methods__', '__class__']:
            return object.__getattribute__(self, attr_name)

        if attr_name in dir(self.__class__):
            return object.__getattribute__(self, attr_name)

        if attr_name in self.__dict__:
            return self.__dict__[attr_name]

        # delegate all functionality to item access
        return self[attr_name]

    def start(self, cmd_line, timeout=None, retry_interval=None,
              create_new_console=False, wait_for_idle=True, work_dir=None):
        command_line = shlex.split(cmd_line)
        try:
            process = subprocess.Popen(command_line, shell=create_new_console)
        except Exception as exc:
            # if it failed for some reason
            message = ('Could not create the process "%s"\n'
                       'Error returned by CreateProcess: %s') % (cmd_line, str(exc))
            raise AppStartError(message)
        self.process = process.pid
        return self


if __name__ == "__main__":
    app = BaseApplication()