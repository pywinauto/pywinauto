import json
import six

from . import injector
from ...backend import Singleton

# backend exit codes enum
OK=0
PARSE_ERROR=1
UNSUPPORTED_ACTION=2
MISSING_PARAM=3
RUNTIME_ERROR=4
NOT_FOUND=5
UNSUPPORTED_TYPE=6

class InjectedBackendError(Exception):
    """Base class for exceptions on the injected backend side"""
    pass

class UnsupportedActionError(InjectedBackendError):
    pass

class BackendRuntimeError(InjectedBackendError):
    pass

class NotFoundError(InjectedBackendError):
    pass

@six.add_metaclass(Singleton)
class ConnectionManager(object):
    def __init__(self):
        self._pipes = {}

    def _get_pipe(self, pid):
        if pid not in self._pipes:
            self._pipes[pid] = injector.create_pipe(pid)
        return self._pipes[pid]
    
    def call_action(self, action_name, pid, **params):
        command = json.dumps({'action': action_name, **params})
        reply = self._get_pipe(pid).transact(command)
        reply = json.loads(reply)

        if reply['status_code'] == UNSUPPORTED_ACTION:
            raise UnsupportedActionError(reply['message'])
        elif reply['status_code'] == RUNTIME_ERROR:
            raise BackendRuntimeError(reply['message'])
        elif reply['status_code'] == NOT_FOUND:
            raise NotFoundError(reply['message'])

        return reply
