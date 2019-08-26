# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Linux Application class"""

import os.path
import time
import subprocess
import shlex

from ..backend import registry
from ..base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication


class Application(BaseApplication):

    def __init__(self, backend="atspi"):
        self.process = None
        self.xmlpath = ''

        self._proc_descriptor = None
        self.match_history = []
        self.use_history = False
        self.actions = None # TODO Action logger for linux
        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]

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
        self._proc_descriptor = process
        self.process = process.pid
        return self

    def connect(self, **kwargs):
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
            self.process = kwargs['process']
            assert_valid_process(self.process)
            connected = True
        elif 'path' in kwargs:
            for proc_id in os.listdir('/proc'):
                if proc_id == 'curproc':
                    continue
                try:
                    with open('/proc/{}/cmdline'.format(proc_id), mode='rb') as fd:
                        content = fd.read().decode().split('\x00')
                except IOError:
                    continue

                if kwargs['path'] in " ".join(content):
                    self.process = int(proc_id)
                    connected = True
                    break

        if not connected:
            raise RuntimeError(
                "You must specify one of process, handle or path")

    def cpu_usage(self, interval=None):
        """Return CPU usage percent during specified number of seconds"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        if interval:
            time.sleep(interval)
        try:
            proc_info = subprocess.check_output(["ps", "-p", str(self.process), "-o", "%cpu"], universal_newlines=True)
            proc_info = proc_info.split("\n")
            return float(proc_info[1])
        except Exception:
            raise ProcessNotFoundError()

    def kill(self):
        """
        Try to close and kill the application

        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        This should only be used when it is OK to kill the process like you
        would do in task manager.
        """
        if self._proc_descriptor is not None:
            # Kill process created via Application with subprocess kill
            self._proc_descriptor.kill()
            # wait for child process to terminate
            self._proc_descriptor.communicate()
            self._proc_descriptor = None

        if not self.is_process_running():
            return True # already closed
        status = subprocess.check_output(["kill", "-9", str(self.process)], universal_newlines=True)
        if "Operation not permitted" in status:
            raise Exception("Cannot kill process: {}".format(status))
        else:
            return True

    def is_process_running(self):
        """
        Checks that process is running.

        Can be called before start/connect.

        Returns True if process is running otherwise - False
        """
        if not str(self.process) in os.listdir('/proc'):
            return False
        else:
            return True


def assert_valid_process(process_id):
    if str(process_id) not in os.listdir('/proc'):
        raise ProcessNotFoundError('pid = ' + str(process_id))
