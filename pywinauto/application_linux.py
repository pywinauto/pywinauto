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


if __name__ == "__main__":
    app = Application()