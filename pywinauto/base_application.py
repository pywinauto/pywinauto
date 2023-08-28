# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""pywinauto.base_application module
------------------------------------

The application module is the main one that users will use first.

When starting to automate an application you must initialize an instance
of the Application class. Then you have to start the program with
:meth:`Application.start<pywinauto.base_application.BaseApplication.start>`
or connect to a runing process of an application with:
:meth:`Application.connect<pywinauto.base_application.BaseApplication.connect>`

Once you have an Application instance you can access dialogs in that
application by using one of the methods below. ::

   dlg = app.YourDialogTitle
   dlg = app.window(name="your title", classname="your class", ...)
   dlg = app['Your Dialog Title']

Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways. ::

   ctrl = dlg.YourControlTitle
   ctrl = dlg.child_window(name="Your control", classname="Button", ...)
   ctrl = dlg["Your control"]

.. note::

   For attribute access of controls and dialogs you do not have to
   specify the exact name/title/text of the control. Pywinauto automatically
   performs a best match of the available dialogs or controls.

   With introducing the cross-platform support in pywinauto,
   the Application class is automatically created with the platform
   default backend. For MS Windows OS it is 'win32' and for Linux OS it is 'atspi'.

.. seealso::

   :func:`pywinauto.findwindows.find_elements` for the keyword arguments that
   can be passed to both:
   :meth:`WindowSpecification.child_window<pywinauto.base_application.WindowSpecification.child_window>` and
   :meth:`WindowSpecification.window<pywinauto.base_application.WindowSpecification.window>`

   :class:`pywinauto.windows.application.Application` for the 'win32' and 'uia' backends

   :class:`pywinauto.linux.application.Application` for the 'atspi' backend
"""
from __future__ import print_function

import time

from . import timings
from . import findwindows

from .window_specification import WindowSpecification
from .timings import Timings, wait_until


class AppStartError(Exception):

    """There was a problem starting the Application"""

    pass    # pragma: no cover


class ProcessNotFoundError(Exception):

    """Could not find that process"""

    pass    # pragma: no cover


class AppNotConnected(Exception):

    """Application has not been connected to a process yet"""

    pass    # pragma: no cover


# TODO problem with if active_only: in findwindows to use on linux
#=========================================================================
class BaseApplication(object):

    """
    Represents an application

    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """

    def connect(self, **kwargs):
        """Connect to an already running process

        The action is performed according to only one of parameters

        :param pid: a process ID of the target
        :param handle: a window handle of the target
        :param path: a path used to launch the target
        :param timeout: a timeout for process start (relevant if path is specified)

        .. seealso::

           :func:`pywinauto.findwindows.find_elements` - the keyword arguments that
           are also can be used instead of **pid**, **handle** or **path**
        """
        raise NotImplementedError()

    def start(self, cmd_line, timeout=None, retry_interval=None,
              create_new_console=False, wait_for_idle=True, work_dir=None):
        """Start the application as specified by **cmd_line**

        :param cmd_line: a string with a path to launch the target
        :param timeout: a timeout for process to start (optional)
        :param retry_interval: retry interval (optional)
        :param create_new_console: create a new console (optional)
        :param wait_for_idle: wait for idle (optional)
        :param work_dir: working directory (optional)
        """
        raise NotImplementedError()

    def cpu_usage(self, interval=None):
        """Return CPU usage percent during specified number of seconds"""
        raise NotImplementedError()

    def wait_cpu_usage_lower(self, threshold=2.5, timeout=None, usage_interval=None):
        """Wait until process CPU usage percentage is less than the specified threshold"""
        if usage_interval is None:
            usage_interval = Timings.cpu_usage_interval
        if timeout is None:
            timeout = Timings.cpu_usage_wait_timeout

        start_time = timings.timestamp()

        while self.cpu_usage(usage_interval) > threshold:
            if timings.timestamp() - start_time > timeout:
                raise RuntimeError('Waiting CPU load <= {}% timed out!'.format(threshold))

        return self

    def top_window(self):
        """Return WindowSpecification for a current top window of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        timeout = Timings.window_find_timeout
        while timeout >= 0:
            windows = findwindows.find_elements(pid=self.process,
                                                backend=self.backend.name)
            if windows:
                break
            time.sleep(Timings.window_find_retry)
            timeout -= Timings.window_find_retry
        else:
            raise RuntimeError("No windows for that process could be found")

        criteria = {}
        criteria['backend'] = self.backend.name
        if windows[0].handle:
            criteria['handle'] = windows[0].handle
        else:
            criteria['name'] = windows[0].name

        return WindowSpecification(criteria, allow_magic_lookup=self.allow_magic_lookup)

    def active(self):
        """Return WindowSpecification for an active window of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        time.sleep(Timings.window_find_timeout)
        # very simple
        windows = findwindows.find_elements(pid=self.process,
                                            active_only=True,
                                            backend=self.backend.name)

        if not windows:
            raise RuntimeError("No Windows of that application are active")

        criteria = {}
        criteria['backend'] = self.backend.name
        if windows[0].handle:
            criteria['handle'] = windows[0].handle
        else:
            criteria['name'] = windows[0].name

        return WindowSpecification(criteria, allow_magic_lookup=self.allow_magic_lookup)

    def windows(self, **kwargs):
        """Return a list of wrapped top level windows of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        if 'backend' in kwargs:
            raise ValueError('Using another backend for this Application '
                             'instance is not allowed! Create another app object.')

        if 'visible' not in kwargs:
            kwargs['visible'] = None

        if 'enabled' not in kwargs:
            kwargs['enabled'] = None

        kwargs['pid'] = self.process
        kwargs['backend'] = self.backend.name
        if kwargs.get('top_level_only') is None:
            kwargs['top_level_only'] = True

        windows = findwindows.find_elements(**kwargs)
        return [self.backend.generic_wrapper_class(win) for win in windows]

    def window(self, **kwargs):
        """Return a window of the application

        You can specify the same parameters as findwindows.find_windows.
        It will add the process parameter to ensure that the window is from
        the current process.

        See :py:func:`pywinauto.findwindows.find_elements` for the full parameters description.
        """
        if 'backend' in kwargs:
            raise ValueError('Using another backend than set in the app constructor is not allowed!')
        kwargs['backend'] = self.backend.name
        if kwargs.get('top_level_only') is None:
            kwargs['top_level_only'] = True
            # TODO: figure out how to eliminate this workaround
            if self.backend.name == 'win32':
                kwargs['visible'] = True

        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        else:
            # add the restriction for this particular application
            kwargs['app'] = self
            win_spec = WindowSpecification(kwargs, allow_magic_lookup=self.allow_magic_lookup)

        return win_spec
    Window_ = window_ = window

    def __getitem__(self, key):
        """Find the specified dialog of the application"""
        # delegate searching functionality to self.window()
        return self.window(best_match=key)

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

    def kill(self, soft=False):
        """
        Try to close and kill the application

        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        This should only be used when it is OK to kill the process like you
        would do in task manager.
        """
        raise NotImplementedError()

    def is_process_running(self):
        """
        Checks that process is running.

        Can be called before start/connect.

        Returns True if process is running otherwise - False
        """
        raise NotImplementedError()

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
