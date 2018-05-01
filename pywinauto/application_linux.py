import sys
import os.path
import pickle
import time
import warnings
import multiprocessing
import locale
import subprocess

from .backend import registry

class AppStartError(Exception):

    """There was a problem starting the Application"""

    pass    # pragma: no cover


class ProcessNotFoundError(Exception):

    """Could not find that process"""

    pass    # pragma: no cover


class AppNotConnected(Exception):

    """Application has not been connected to a process yet"""

    pass    # pragma: no cover



class Application(object):

    def __init__(self, backend="atspi"):
        self.proces = None
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
        # if attr_name in ['__dict__', '__members__', '__methods__', '__class__']:
        #     return object.__getattribute__(self, attr_name)
        #
        # if attr_name in dir(self.__class__):
        #     return object.__getattribute__(self, attr_name)
        #
        # if attr_name in self.__dict__:
        #     return self.__dict__[attr_name]
        #
        # # delegate all functionality to item access
        # return self[attr_name]
        return None


if __name__ == "__main__":
    app = Application()