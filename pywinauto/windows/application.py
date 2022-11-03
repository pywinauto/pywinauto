# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
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

"""Implementation of Application class for MS Windows platform."""

from __future__ import print_function

import os.path
import pickle
import time
import warnings
import multiprocessing

import win32process
import win32api
import win32gui
import win32con
import win32event

from .. import controls
from .. import findbestmatch
from .. import findwindows
from .. import handleprops
from . import win32defines
from ..backend import registry

from ..actionlogger import ActionLogger
from ..timings import Timings, wait_until, TimeoutError, wait_until_passes
from ..sysinfo import is_x64_Python
from ..base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication
from .. import deprecated

# Display User and Deprecation warnings every time
for warning in (UserWarning, PendingDeprecationWarning):
    warnings.simplefilter('always', warning)


#=========================================================================

cur_item = 0

def _resolve_from_appdata(
        criteria_, app, timeout=None, retry_interval=None):
    """Should not be used at the moment!"""
    # TODO: take a look into this functionality

    if timeout is None:
        timeout = Timings.window_find_timeout
    if retry_interval is None:
        retry_interval = Timings.window_find_retry

    global cur_item
    # get the stored item corresponding to this request
    matched_control = app.GetMatchHistoryItem(cur_item)

    cur_item += 1
    # remove parameters from the original search  that changes each time
    criteria = [crit.copy() for crit in criteria_]

    # Remove any attributes from the current search that are
    # completely language dependent
    for unloc_attrib in ['title_re', 'title', 'name', 'name_re', 'best_match']:
        for c in criteria:
            if unloc_attrib in c.keys():
                del c[unloc_attrib]

    #found_criteria = item[0]
    #for c in found_criteria:
    #    if c.has_key('process'):
    #        del c['process']
    #
    # They should match - so if they don't print it out.
    #if found_criteria != search_criteria:
    #    print "\t\t", matched[cur_index - 3][0]
    #    print "\t" ,matched[cur_index - 2][0]
    #    print search_criteria
    #    print "---"
    #    print found_criteria
    #    raise RuntimeError("Mismatch")

    # so let's use the ID from the matched control...
    #print item[1]

    # we need to try and get a good match for the dialog
    # this could be done by matching
    # - number/positoin of controls
    # - class
    # anything else?

    dialog_criterion = criteria[0]
    #print list(matched_control)
    dialog_criterion['class_name'] = matched_control[1]['class_name']

    # find all the windows in the process
    process_elems = findwindows.find_elements(**dialog_criterion)

    dialog = None
    ctrl = None
    if process_elems:
        #similar_child_count = [e for e in process_elems
        #    if matched_control[1]['control_count'] -2 <=
        #            len(e.children()) and
        #        matched_control[1]['control_count'] +2 >=
        #            len(e.children())]

        #if similar_child_count:
        #    process_hwnds = similar_child_count
        #else:
        #    print("None Similar child count!!???")
        #    print(matched_control[1]['control_count'], len(handleprops.children(h)))

        for e in process_elems:
            #print controls.WrapHandle(h).get_properties()
            #print "======", h, h, h

            dialog = registry.wrapper_class(e)

            # if a control was specified also
            if len(criteria_) > 1:
                # find it in the original data
                #print item[2]

                # remove those criteria which are langauge specific
                ctrl_criterion = criteria[1]

                #def has_same_id(other_ctrl):
                #    print "==="*20
                #    print "testing", item[2]['control_id'],
                #    print "against", other_ctrl
                #    return item[2]['control_id'] == \
                #    handleprops.controlid(other_ctrl)

                ctrl_criterion['class_name'] = matched_control[2]['class_name']
                ctrl_criterion['parent'] = dialog.handle
                ctrl_criterion['top_level_only'] = False
                #ctrl_criterion['predicate_func'] = has_same_id
                #print "CTRLCTRJL", ctrl_criterion
                ctrl_elems = findwindows.find_elements(**ctrl_criterion)

                if len(ctrl_elems) > 1:
                    same_ids = \
                        [elem for elem in ctrl_elems
                         if elem.control_id == matched_control[2]['control_id']]

                    if same_ids:
                        ctrl_elems = same_ids

                try:
                    ctrl = registry.wrapper_class(ctrl_elems[0])
                except IndexError:
                    print("-+-+=_" * 20)
                    #print(found_criteria)
                    raise

                break

    # it is possible that the dialog will not be found - so we
    # should raise an error
    if dialog is None:
        raise findwindows.ElementNotFoundError()

    if len(criteria_) == 2 and ctrl is None:
        raise findwindows.ElementNotFoundError()

    if ctrl:
        return dialog, ctrl
    else:
        return (dialog, )

    #print process_hwnds


#
#        # if best match was specified for the dialog
#        # then we need to replace it with other values
#        # for now we will just use class_name
#        for crit in ['best_match', 'title', 'title_re']:
#            if crit in criteria[0]:
#                del(criteria[0][crit])
#                criteria[0]['class_name'] = app_data[0].class_name()#['class_name']
#
#            if len(criteria) > 1:
#                # find the best match of the application data
#                if criteria[1].has_key('best_match'):
#                    best_match = findbestmatch.find_best_control_matches(
#                        criteria[1]['best_match'], app_data)[0]
#
#                    #visible_controls = [ctrl in app_data if ctrl.is_visible()]
#
#                    #find the index of the best match item
#                    ctrl_index = app_data.index(best_match)
#                    #print best_match[0].window_text()
#                    ctrl_index, best_match.window_text()
#
#                    criteria[1]['ctrl_index'] = ctrl_index -1
#                    #criteria[1]['class_name'] = best_match.class_name()
#                    #del(criteria[1]['best_match'])
#
# One idea here would be to run the new criteria on the app_data dialog and
# if it returns more then one control then you figure out which one would be
# best - so that you have that info when running on the current dialog
#
#            #for criterion in criteria[1:]:
#                # this part is weird - we now have to go off and find the
#                # index, class, text of the control in the app_data
#                # and then find the best match for this control in the
#                # current dialog
#            #    pass
#
#

#    dialog = None

    #return _resolve_control(criteria_, timeout, retry_interval)


#=========================================================================
class Application(BaseApplication):

    """
    Represents an application

    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """

    def __init__(self, backend="win32", datafilename=None, allow_magic_lookup=True):
        """
        Initialize the Application object

        * **backend** is a name of used back-end (values: "win32", "uia").
        * **datafilename** is a file name for reading matching history.
        * **allow_magic_lookup** whether attribute access must turn into
                child_window(best_match=...) search as fallback
        """
        self.process = None
        self.xmlpath = ''

        self.match_history = []
        self.use_history = False
        self.actions = ActionLogger()
        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]
        self.allow_magic_lookup = allow_magic_lookup
        if self.backend.name == 'win32':
            # Non PEP-8 aliases for partial backward compatibility
            self.Start = deprecated(self.start)
            self.Connect = deprecated(self.connect)
            self.CPUUsage = deprecated(self.cpu_usage)
            self.WaitCPUUsageLower = deprecated(self.wait_cpu_usage_lower, deprecated_name='WaitCPUUsageLower')
            self.top_window_ = deprecated(self.top_window, deprecated_name='top_window_')
            self.active_ = deprecated(self.active, deprecated_name='active_')
            self.Windows_ = deprecated(self.windows, deprecated_name='Windows_')
            self.windows_ = deprecated(self.windows, deprecated_name='windows_')
            self.Window_ = deprecated(self.window, deprecated_name='Window_')
            self.window_ = deprecated(self.window, deprecated_name='window_')

        # load the match history if a file was specifed
        # and it exists
        if datafilename and os.path.exists(datafilename):
            with open(datafilename, "rb") as datafile:
                self.match_history = pickle.load(datafile)
            self.use_history = True

    def __iter__(self):
        """Raise to avoid infinite loops"""
        raise NotImplementedError("Object is not iterable, try to use .windows()")

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
        timeout = Timings.app_connect_timeout
        retry_interval = Timings.app_connect_retry
        if 'timeout' in kwargs and kwargs['timeout'] is not None:
            timeout = kwargs['timeout']
        if 'retry_interval' in kwargs and kwargs['retry_interval'] is not None:
            retry_interval = kwargs['retry_interval']

        connected = False
        if 'pid' in kwargs:
            self.process = kwargs['pid']
            try:
                wait_until(timeout, retry_interval, self.is_process_running, value=True)
            except TimeoutError:
                raise ProcessNotFoundError('Process with PID={} not found!'.format(self.process))
            connected = True
        elif 'process' in kwargs:
            warnings.warn("'process' keyword is deprecated, use 'pid' instead", DeprecationWarning)
            kwargs['pid'] = self.process = kwargs['process']
            del kwargs['process']
            try:
                wait_until(timeout, retry_interval, self.is_process_running, value=True)
            except TimeoutError:
                raise ProcessNotFoundError('Process with PID={} not found!'.format(self.process))
            connected = True

        elif 'handle' in kwargs:

            if not handleprops.iswindow(kwargs['handle']):
                message = "Invalid handle 0x%x passed to connect()" % (
                    kwargs['handle'])
                raise RuntimeError(message)

            self.process = handleprops.processid(kwargs['handle'])

            connected = True

        elif 'path' in kwargs:
            try:
                self.process = wait_until_passes(
                        timeout, retry_interval, process_from_module,
                        ProcessNotFoundError, kwargs['path'],
                    )
            except TimeoutError:
                raise ProcessNotFoundError('Process "{}" not found!'.format(kwargs['path']))
            connected = True

        elif kwargs:
            kwargs['backend'] = self.backend.name
            # XXX: vryabov
            # if 'found_index' not in kwargs:
            #     kwargs['found_index'] = 0

            #if 'visible_only' not in kwargs:
            #    kwargs['visible_only'] = False
            if 'timeout' in kwargs:
                del kwargs['timeout']
                self.process = wait_until_passes(
                        timeout, retry_interval, findwindows.find_element,
                        exceptions=(findwindows.ElementNotFoundError, findbestmatch.MatchError,
                                    controls.InvalidWindowHandle, controls.InvalidElement),
                        *(), **kwargs
                    ).process_id
            else:
                self.process = findwindows.find_element(**kwargs).process_id
            connected = True

        if not connected:
            raise RuntimeError(
                "You must specify some of process, handle, path or window search criteria.")

        if self.backend.name == 'win32':
            self.__warn_incorrect_bitness()

            if not handleprops.has_enough_privileges(self.process):
                warning_text = "Python process has no rights to make changes " \
                    "in the target GUI (run the script as Administrator)"
                warnings.warn(warning_text, UserWarning)

        return self

    def start(self, cmd_line, timeout=None, retry_interval=None,
              create_new_console=False, wait_for_idle=True, work_dir=None):
        """Start the application as specified by cmd_line"""
        # try to parse executable name and check it has correct bitness
        if '.exe' in cmd_line and self.backend.name == 'win32':
            exe_name = cmd_line.split('.exe')[0] + '.exe'
            _warn_incorrect_binary_bitness(exe_name)

        if timeout is None:
            timeout = Timings.app_start_timeout
        if retry_interval is None:
            retry_interval = Timings.app_start_retry

        start_info = win32process.STARTUPINFO()

        # we need to wrap the command line as it can be modified
        # by the function
        command_line = cmd_line

        # Actually create the process
        dw_creation_flags = 0
        if create_new_console:
            dw_creation_flags = win32con.CREATE_NEW_CONSOLE
        try:
            (h_process, _, dw_process_id, _) = win32process.CreateProcess(
                None, 					# module name
                command_line,			# command line
                None, 					# Process handle not inheritable.
                None, 					# Thread handle not inheritable.
                0, 						# Set handle inheritance to FALSE.
                dw_creation_flags,		# Creation flags.
                None, 					# Use parent's environment block.
                work_dir,				# If None - use parent's starting directory.
                start_info)				# STARTUPINFO structure.
        except Exception as exc:
            # if it failed for some reason
            message = ('Could not create the process "%s"\n'
                       'Error returned by CreateProcess: %s') % (cmd_line, str(exc))
            raise AppStartError(message)

        self.process = dw_process_id

        if self.backend.name == 'win32':
            self.__warn_incorrect_bitness()

        def app_idle():
            """Return true when the application is ready to start"""
            result = win32event.WaitForInputIdle(
                h_process, int(timeout * 1000))

            # wait completed successfully
            if result == 0:
                return True

            # the wait returned because it timed out
            if result == win32con.WAIT_TIMEOUT:
                return False

            return bool(self.windows())

        # Wait until the application is ready after starting it
        if wait_for_idle and not app_idle():
            warnings.warn('Application is not loaded correctly (WaitForInputIdle failed)', RuntimeWarning)

        self.actions.log("Started " + cmd_line + " application.")

        return self

    def __warn_incorrect_bitness(self):
        if self.backend.name == 'win32' and self.is64bit() != is_x64_Python():
            if is_x64_Python():
                warnings.warn(
                    "32-bit application should be automated using 32-bit Python (you use 64-bit Python)",
                    UserWarning)
            else:
                warnings.warn(
                    "64-bit application should be automated using 64-bit Python (you use 32-bit Python)",
                    UserWarning)

    def is64bit(self):
        """Return True if running process is 64-bit"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        return handleprops.is64bitprocess(self.process)

    def cpu_usage(self, interval=None):
        """Return CPU usage percent during specified number of seconds"""
        WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7

        if interval is None:
            interval = Timings.cpu_usage_interval

        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        try:
            h_process = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, 0, self.process)
        except win32api.error as e:
            if e.winerror == win32defines.ERROR_INVALID_PARAMETER:
                raise ProcessNotFoundError('Process with PID {} does not exist'.format(self.process))
            raise e

        times_dict = win32process.GetProcessTimes(h_process)
        UserTime_start, KernelTime_start = times_dict['UserTime'], times_dict['KernelTime']

        time.sleep(interval)

        times_dict = win32process.GetProcessTimes(h_process)
        UserTime_end, KernelTime_end = times_dict['UserTime'], times_dict['KernelTime']

        total_time = (UserTime_end - UserTime_start) / WIN32_PROCESS_TIMES_TICKS_PER_SECOND + \
                     (KernelTime_end - KernelTime_start) / WIN32_PROCESS_TIMES_TICKS_PER_SECOND

        win32api.CloseHandle(h_process)
        return 100.0 * (total_time / (float(interval) * multiprocessing.cpu_count()))

    def __getitem__(self, key):
        """Find the specified dialog of the application"""
        # delegate searching functionality to self.window()
        return self.window(best_match=key)

    def __getattribute__(self, attr_name):
        """Find the specified dialog of the application"""
        allow_magic_lookup = object.__getattribute__(self, "allow_magic_lookup")  # Beware of recursions here!
        if not allow_magic_lookup:
            try:
                return object.__getattribute__(self, attr_name)
            except AttributeError:
                message = (
                    'Attribute "%s" doesn\'t exist on %s object'
                    ' (typo? or set allow_magic_lookup to True?)' %
                    (attr_name, self.__class__))
                raise AttributeError(message)

        if attr_name in ['__dict__', '__members__', '__methods__', '__class__']:
            return object.__getattribute__(self, attr_name)

        if attr_name in dir(self.__class__):
            return object.__getattribute__(self, attr_name)

        if attr_name in self.__dict__:
            return self.__dict__[attr_name]

        # delegate all functionality to item access
        return self[attr_name]

    def WriteAppData(self, filename):
        """Should not be used - part of application data implementation"""
        with open(filename, "wb") as f:
            pickle.dump(self.match_history, f)

    def GetMatchHistoryItem(self, index):
        """Should not be used - part of application data implementation"""
        return self.match_history[index]

    def kill(self, soft=False):
        """
        Try to close (optional) and kill the application

        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        This should only be used when it is OK to kill the process like you
        would do in task manager.
        """
        if soft:
            windows = self.windows(visible=True)

            for win in windows:
                try:
                    if hasattr(win, 'close'):
                        win.close()
                        continue
                except TimeoutError:
                    self.actions.log('Failed to close top level window')

                if hasattr(win, 'force_close'):
                    self.actions.log('Application.kill: call win.force_close()')
                    win.force_close()

        try:
            process_wait_handle = win32api.OpenProcess(
                win32con.SYNCHRONIZE | win32con.PROCESS_TERMINATE,
                0,
                self.process)
        except win32gui.error:
            return True  # already closed

        # so we have either closed the windows - or the app is hung
        killed = True
        try:
            if process_wait_handle:
                try:
                    win32api.TerminateProcess(process_wait_handle, 0)
                except win32gui.error:
                    self.actions.log('Process {0} seems already killed'.format(self.process))
        finally:
            win32api.CloseHandle(process_wait_handle)

        self.wait_for_process_exit()
        return killed

    # Non PEP-8 aliases
    kill_ = deprecated(kill, deprecated_name='kill_')
    Kill_ = deprecated(kill, deprecated_name='Kill_')

    def is_process_running(self):
        """
        Check that process is running.

        Can be called before start/connect.

        Return True if process is running otherwise - False.
        """
        is_running = False
        try:
            h_process = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION,
                0,
                self.process)
            is_running = win32process.GetExitCodeProcess(
                h_process) == win32defines.PROCESS_STILL_ACTIVE
        except (win32gui.error, TypeError):
            is_running = False
        return is_running


#=========================================================================
def assert_valid_process(process_id):
    """Raise ProcessNotFound error if process_id is not a valid process id"""
    try:
        process_handle = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, 0, process_id)
    except win32gui.error as exc:
        raise ProcessNotFoundError(str(exc) + ', pid = ' + str(process_id))

    if not process_handle:
        message = "Process with ID '%d' could not be opened" % process_id
        raise ProcessNotFoundError(message)

    # finished process can still exist and have exit code,
    # but it's not usable any more, so let's check it
    exit_code = win32process.GetExitCodeProcess(process_handle)
    is_running = (exit_code == win32defines.PROCESS_STILL_ACTIVE)
    if not is_running:
        raise ProcessNotFoundError('Process with pid = {} has been already ' \
            'finished with exit code = {}'.format(process_id, exit_code))

    return process_handle


#=========================================================================
def process_get_modules():
    """Return the list of processes as tuples (pid, exe_path)"""
    modules = []

    # collect all the running processes
    pids = win32process.EnumProcesses()
    for pid in pids:
        if pid != 0 and isinstance(pid, int):  # skip system process (0x00000000)
            try:
                modules.append((pid, process_module(pid), None))
            except (win32gui.error, ProcessNotFoundError):
                continue
    return modules


#=========================================================================
def _process_get_modules_wmi():
    """Return the list of processes as tuples (pid, exe_path)"""
    from win32com.client import GetObject
    _wmi = GetObject('winmgmts:')

    modules = []
    # collect all the running processes
    processes = _wmi.ExecQuery('Select * from win32_process')
    for p in processes:
        if isinstance(p.ProcessId, int):
            modules.append((p.ProcessId, p.ExecutablePath, p.CommandLine))  # p.Name
    return modules


#=========================================================================
def process_module(process_id):
    """Return the string module name of this process"""
    process_handle = assert_valid_process(process_id)

    return win32process.GetModuleFileNameEx(process_handle, 0)


#=========================================================================
def _warn_incorrect_binary_bitness(exe_name):
    """Warn if the executable is of incorrect bitness"""
    if os.path.isabs(exe_name) and os.path.isfile(exe_name) and \
            handleprops.is64bitbinary(exe_name) and not is_x64_Python():
        warnings.warn(
            "64-bit binary from 32-bit Python may work incorrectly "
            "(please use 64-bit Python instead)",
            UserWarning, stacklevel=2)


#=========================================================================
def process_from_module(module):
    """Return the running process with path module"""
    # normalize . or .. relative parts of absolute path
    module_path = os.path.normpath(module)

    _warn_incorrect_binary_bitness(module_path)

    try:
        modules = _process_get_modules_wmi()
    except Exception:
        modules = process_get_modules()

    # check for a module with a matching name in reverse order
    # as we are most likely to want to connect to the last
    # run instance
    modules.reverse()
    for process, name, _ in modules:
        if name is None:
            continue
        if module_path.lower() in name.lower():
            return process

    message = "Could not find any accessible process with a module of '{0}'".format(module)
    raise ProcessNotFoundError(message)
