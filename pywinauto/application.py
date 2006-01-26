# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"""The application module is the main one that users will user first.

When starting to automate and application you must initialize an instance
of the Application class. Then you must `start_()`_ that application or
`connect_()`_ to a running instance of that application.

Once you have an Application instance you can access dialogs in that
application either by using one of the methods below. ::

   dlg = app.YourDialogTitle
   dlg = app.window_(title = "your title", class = "your class", ...)
   dlg = app['Your Dialog Title']

Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways. ::

  ctrl = dlg.YourControlTitle
  ctrl = dlg.control_(title = "Your control", class = "Button", ...)
  ctrl = dlg["Your control"]

**Note:** For attribute access of controls and dialogs you do not have to
have the title of the control exactly, it does a best match of the
avialable dialogs or controls.

**See also:**
  `findwindows.find_windows()`_   for the keyword arguments that can be
  passed to both `Application.window_()`_ and `ActionDialog.control_()`_

.. _start_(): class-pywinauto.application.Application.html#start_
.. _connect_(): class-pywinauto.application.Application.html#connect_
.. _findwindows.find_windows():  module-pywinauto.findwindows.html#find_windows
.. _Application.window_(): class-pywinauto.application.Application.html#window_
.. _ActionDialog.control_(): class-pywinauto.application.ActionDialog.html#control_

"""

__revision__ = "$Revision$"

import time
import os.path

import ctypes

import win32structures
import win32functions
import controls
import findbestmatch
import findwindows
import handleprops

# Following only needed for writing out XML files
# and can be (also requires elementtree)
try:
    import XMLHelpers
except ImportError:
    pass

class AppStartError(Exception):
    "There was a problem starting the Application"
    pass

class ProcessNotFoundError(Exception):
    "Could not find that process"
    pass

class AppNotConnected(Exception):
    "Application has been connected to a process yet"
    pass


window_find_timeout = 3
window_retry_interval = .09
wait_after_app_start = 10


#=========================================================================
def _make_valid_filename(filename):
    r"""Return a valid file name for the string passed in.

    Replaces any character in ``:\/*?"<>|`` with ``'#%d#'% ord(char)``"""
    for char in ('\/:*?"<>|'):
        filename = filename.replace(char, '#%d#'% ord(char))
    return filename

#
##=========================================================================
#class ActionDialog(object):
#    """ActionDialog wraps the dialog you are interacting with
#
#    It provides support for finding controls using attribute access,
#    item access and the _control(...) method.
#
#    You can dump information from a dialgo to XML using the write_() method
#
#    A screenshot of the dialog can be taken using the underlying wrapped
#    HWND ie. my_action_dlg.wrapped_win.CaptureAsImage().save("dlg.png").
#    This is only available if you have PIL installed (fails silently
#    otherwise).
#    """
#    def __init__(self, hwnd, app = None, props = None):
#        """Initialises an ActionDialog object
#
#        ::
#           hwnd (required) The handle of the dialog
#           app An instance of an Application Object
#           props future use (when we have an XML file for reference)
#
#        """
#
#        #self.wrapped_win = controlactions.add_actions(
#        #    controls.WrapHandle(hwnd))
#        self.wrapped_win = controls.WrapHandle(hwnd)
#
#        self.app = app
#
#        dlg_controls = [self.wrapped_win, ]
#        dlg_controls.extend(self.wrapped_win.Children)
#
#    def __getattr__(self, key):
#        "Attribute access - defer to item access"
#        return self[key]
#
#    def __getitem__(self, attr):
#        "find the control that best matches attr"
#        # if it is an integer - just return the
#        # child control at that index
#        if isinstance(attr, (int, long)):
#            return self.wrapped_win.Children[attr]
#
#        # so it should be a string
#        # check if it is an attribute of the wrapped win first
#        try:
#            return getattr(self.wrapped_win, attr)
#        except (AttributeError, UnicodeEncodeError):
#            pass
#
#        # find the control that best matches our attribute
#        ctrl = findbestmatch.find_best_control_match(
#            attr, self.wrapped_win.Children)
#
#        # add actions to the control and return it
#        return ctrl
#
#    def write_(self, filename):
#        "Write the dialog an XML file (requires elementtree)"
#        if self.app and self.app.xmlpath:
#            filename = os.path.join(self.app.xmlpath, filename + ".xml")
#
#        controls = [self.wrapped_win]
#        controls.extend(self.wrapped_win.Children)
#        props = [ctrl.GetProperties() for ctrl in controls]
#
#        XMLHelpers.WriteDialogToFile(filename, props)
#
#    def control_(self, **kwargs):
#        "Find the control that matches the arguments and return it"
#
#        # add the restriction for this particular process
#        kwargs['parent'] = self.wrapped_win
#        kwargs['process'] = self.app.process
#        kwargs['top_level_only'] = False
#
#        # try and find the dialog (waiting for a max of 1 second
#        ctrl = findwindows.find_window(**kwargs)
#        #win = ActionDialog(win, self)
#
#        return controls.WrapHandle(ctrl)
#
#
#
#
##=========================================================================
#def _WalkDialogControlAttribs(app, attr_path):
#    "Try and resolve the dialog and 2nd attribute, return both"
#    if len(attr_path) != 2:
#        raise RuntimeError("Expecting only 2 items in the attribute path")
#
#    # get items to select between
#    # default options will filter hidden and disabled controls
#    # and will default to top level windows only
#    wins = findwindows.find_windows(process = app.process)
#
#    # wrap each so that find_best_control_match works well
#    wins = [controls.WrapHandle(win) for win in wins]
#
#    # if an integer has been specified
#    if isinstance(attr_path[0], (int, long)):
#        dialogWin  = wins[attr_path[0]]
#    else:
#        # try to find the item
#        dialogWin = findbestmatch.find_best_control_match(attr_path[0], wins)
#
#    # already wrapped
#    dlg = ActionDialog(dialogWin, app)
#
#    # for each of the other attributes ask the
#    attr_value = dlg
#    for attr in attr_path[1:]:
#        try:
#            attr_value = getattr(attr_value, attr)
#        except UnicodeEncodeError:
#            attr_value = attr_value[attr]
#
#    return dlg, attr_value
#
#
##=========================================================================
#class _DynamicAttributes(object):
#    "Class that builds attributes until they are ready to be resolved"
#
#    def __init__(self, app):
#        "Initialize the attributes"
#        self.app = app
#        self.attr_path = []
#
#    def __getattr__(self, attr):
#        "Attribute access - defer to item access"
#        return self[attr]
#
#    def __getitem__(self, attr):
#        "Item access[] for getting dialogs and controls from an application"
#
#        # do something with this one
#        # and return a copy of ourselves with some
#        # data related to that attribute
#
#        self.attr_path.append(attr)
#
#        # if we have a lenght of 2 then we have either
#        #   dialog.attribute
#        # or
#        #   dialog.control
#        # so go ahead and resolve
#        if len(self.attr_path) == 2:
#            dlg, final = _wait_for_function_success(
#                _WalkDialogControlAttribs, self.app, self.attr_path)
#
#            # seing as we may already have a reference to the dialog
#            # we need to strip off the control so that our dialog
#            # reference is not messed up
#            self.attr_path = self.attr_path[:-1]
#
#            return final
#
#        # we didn't hit the limit so continue collecting the
#        # next attribute in the chain
#        return self


#=========================================================================
def _wait_for_function_success(func, *args, **kwargs):
    """Retry the dialog up to timeout trying every time_interval seconds

    timeout defaults to 1 second
    time_interval defaults to .09 of a second """
    if kwargs.has_key('time_interval'):
        time_interval = kwargs['time_interval']
        del kwargs['time_interval']
    else:
        time_interval = window_retry_interval

    if kwargs.has_key('timeout'):
        timeout = kwargs['timeout']
        del kwargs['timeout']
    else:
        timeout = window_find_timeout


    # keep going until we either hit the return (success)
    # or an exception is raised (timeout)
    while 1:
        try:
            return func(*args, **kwargs)
        except:
            if timeout > 0:
                time.sleep (time_interval)
                timeout -= time_interval
            else:
                raise













#=========================================================================
class WindowSpecification(object):
    def __init__(self, search_criteria):
        # kwargs will contain however to find this window
        self.criteria = [search_criteria, ]

    def Exists(self):
        try:
            _wait_for_function_success(
                self.__resolve_control,
                timeout = .5,
                time_interval = .3)
            return True
        except (findwindows.WindowNotFoundError, findbestmatch.MatchError):
            return False

        return ctrl

    def WaitExists(self, timeout = 1, wait_interval = .3):
        # TODO should we return how long we waited or the window?
        ctrl = _wait_for_function_success(
            self.__resolve_control,
            timeout = timeout,
            time_interval = wait_interval)

        return ctrl

    def WaitEnabled(self):
        pass
    def WaitVisible(self):
        pass
    def WaitNotExists(self):
        pass
    def WaitNotEnabled(self, timeout = 2, wait_interval = .5):
        waited = 0
        while True:

            try:
                # stop trying if it is not enabled
                if not self.__resolve_control().IsEnabled:
                    break

            # stop trying if the window doesn't exist
            except (findwindows.WindowNotFoundError, findbestmatch.MatchError):
                break

            # stop trying if we have reached the timeout
            if waited >= timeout:
                break

            # other wise wait the interval, and try again
            time.sleep(wait_interval)
            waited += wait_interval


    def WaitNotVisible(self):
        self.__resolvewindow()
        pass

    def window_(self, **criteria):

        if len(self.criteria) < 2:
            self.criteria.append(criteria)
        else:
            self.criteria[1] = criteria

        print self.criteria

        return self

    def __getitem__(self, key):

        # FUTURE REQUIREMENT - NOT REQUIRED YET
        # if we already have 2 levels of criteria (dlg, control)
        # then resolve the control and do a getitem on it for the
        # key
        #if len(self.criteria) == 2:
        #    return self.__resolvewindow()[key]
        # END FUTURE REQUIREMENT - NOT REQUIRED YET

        new_item = WindowSpecification(self.criteria[0])
        new_item.criteria.append({"best_match" : key})

        # We don't really want this because it brings us back to
        # not being able to do app.Dlg.Control.WaitExists()
        #if len(self.criteria) == 2:
        #    return self.__resolve_control()

        return new_item

    # now there is a problem what if we do
    #app.Dlg.Click(), or app.Dlg.Font
    # one way would be to resolve on __call__
    # or maybe resolve - if window found and attribute found
    # then return it

    # - resolve on call - that will handle all actions
    # - We know the first one is a dialog so we an
    #   check if the attr is in the list of Dialog attributes!
    def __getattr__(self, attr):
        from pywinauto.controls.win32_controls import DialogWrapper

        # if we already have 2 levels of criteria (dlg, conrol)
        # this third must be an attribute so resolve and get the
        # attribute and return it
        if len(self.criteria) == 2:
            return getattr(
                _wait_for_function_success(self.__resolve_control),
                attr)
        else:
            # if we have been asked for an attribute of the dialog
            # then resolve the window and return the attribute
            if len(self.criteria) == 1 and hasattr(DialogWrapper, attr):
                return getattr(self.WaitExists(1, .3), attr)

        # It is a dialog/control criterion so let getitem
        # deal with it
        return self[attr]



    def __resolve_control(self):

        # hide this function in here - so it is clear that __resolve_control
        # is the method that needs to be called
        def __resolve_window(criteria):

            criteria['visible_only'] = True
            criteria['enabled_only'] = True
            return controls.WrapHandle(findwindows.find_window(**criteria))


        dialog = __resolve_window(self.criteria[0])

        # if there is only criteria for a dialog then return it
        if len(self.criteria) == 1:
            return dialog

        # so there was criteria for a control, add the extra criteria
        # that are required for child controls
        criteria = self.criteria[1]
        criteria["top_level_only"] = False
        criteria["parent"] = dialog

        # resolve the control and return it
        return __resolve_window(criteria)









#=========================================================================
class Application(object):
    "Represents an application"
    def __init__(self):
        "Set the attributes"
        self.process = None
        self.xmlpath = ''

    def start_(self, cmd_line, timeout = wait_after_app_start):
        "Starts the application giving in cmd_line"

        start_info = win32structures.STARTUPINFOW()
        start_info.sb = ctypes.sizeof(start_info)

        proc_info = win32structures.PROCESS_INFORMATION()

        # we need to wrap the command line as it can be modified
        # by the function
        command_line = ctypes.c_wchar_p(unicode(cmd_line))

        # Actually create the process
        ret = win32functions.CreateProcess(
            0, 					# module name
            command_line,		# command line
            0, 					# Process handle not inheritable.
            0, 					# Thread handle not inheritable.
            0, 					# Set handle inheritance to FALSE.
            0, 					# No creation flags.
            0, 					# Use parent's environment block.
            0,  				# Use parent's starting directory.
            ctypes.byref(start_info),# Pointer to STARTUPINFO structure.
            ctypes.byref(proc_info)) # Pointer to PROCESS_INFORMATION structure


        # if it failed for some reason
        if not ret:
            raise AppStartError("CreateProcess: " + str(ctypes.WinError()))

        self.process = _Process(proc_info.dwProcessId)

        if win32functions.WaitForInputIdle(proc_info.hProcess, timeout * 1000):
            raise AppStartError("WaitForInputIdle: " + str(ctypes.WinError()))

        while not self.process.windows():
            print "sleeping waiting for startup"
            time.sleep(.3)

        return self


    def connect_(self, **kwargs):
        "Connects to an already running process"

        connected = False
        if 'process' in kwargs:
            self.process = _Process(kwargs['process'])
            connected = True

        elif 'handle' in kwargs:
            self.process = kwargs['handle'].Process
            connected = True

        elif 'path' in kwargs:
            self.process = _Process.process_from_module(kwargs['path'])
            connected = True

        else:
            handle = findwindows.find_window(**kwargs)
            self.process = _Process(handleprops.processid(handle))
            connected = True

        if not connected:
            raise RuntimeError(
                "You must specify one of process, handle or path")

        return self

    def windows_(self):
        "hmm - seems wrong!!"
        if not self.process:
            raise AppNotConnected("Please use start_ or connect_ before "
                "trying anything else")

        return self.process.windows()


    def window_(self, *args, **kwargs):
        """Return a window of the application

        You can specify the same parameters as findwindows.find_windows.
        It will add the process parameter to ensure that the window is from
        the current process.
        """
        if not self.process:
            raise AppNotConnected("Please use start_ or connect_ before "
                "trying anything else")

        if args:
            raise RuntimeError("You must use keyword arguments")



        # add the restriction for this particular process
        kwargs['process'] = self.process._id

        return WindowSpecification(kwargs)
#
#
#        # try and find the dialog (waiting for a max of 1 second
#        win = _wait_for_function_success (
#            findwindows.find_window,
#            *args,
#            **kwargs)
#
#        # wrap the Handle object (and store it in the cache
#        return ActionDialog(win, self)

    def __getitem__(self, key):
        "Find the dialog of the application"
        if not self.process:
            raise AppNotConnected("Please use start_ or connect_ before "
                "trying anything else")

        return WindowSpecification(dict(
            process = self.process._id,
            best_match = key)
            )


#        return _DynamicAttributes(self)[key]

    def __getattr__(self, key):
        "Find the dialog of the application"
        if not self.process:
            raise AppNotConnected("Please use start_ or connect_ before "
                "trying anything else")

        return self[key]

#    def _wait_while_enabled(self, control, timeout = 1):
#
#        waited = 0
#        # go for dialog first
#        while True:
#            wins = findwindows.find_windows(process = self.process)
#            wins = [controls.WrapHandle(win) for win in wins]
#
#            try:
#                # check if it is a string
#                if isinstance(control, basestring):
#
#                    # get the dialog
#                    parts = control.split('.')
#                    to_check = findbestmatch.find_best_control_match(
#                        parts[0], wins)
#
#                    # if there are more parts then get teh control
#                    if parts[1:]:
#                        to_check = findbestmatch.find_best_control_match(
#                            parts[1], to_check.Children)
#
#                    # if it is enabled then we need to wait longer
#                    if to_check.IsEnabled:
#                        if waited >= timeout:
#                            raise RuntimeError("Timed Out")
#                        time.sleep(.5)
#                        waited += .5
#                    # OK so it is not enabled - we can break out
#                    else:
#                        break
#
#            except findbestmatch.MatchError, e:
#                break

#=========================================================================
class _Process(object):
    "A running process"
    def __init__(self, ID, module = None):
        "initialise the process instance"

        self._id = ID
        self._module = module

    def id(self):
        "Return the process iD"
        return self._id

    def windows(self):
        "Get the windows in this process"
        return findwindows.find_windows(process = self._id)

    def module(self):
        "Return the string module name of this process"
        # Set instance variable _module if not already set
        if not self._module:
            hProcess = win32functions.OpenProcess(
                0x400 | 0x010, 0, self._id) # read and query info

            # get module name from process handle
            filename = (ctypes.c_wchar * 2000)()
            win32functions.GetModuleFileNameEx(
                hProcess, 0, ctypes.byref(filename), 2000)

            # set variable
            self._module = filename.value

        return self._module

    def __eq__(self, other):
        "Check if this proces is the same as other"
        if isinstance(other, _Process):
            return self._id == other._id
        else:
            return self._id == other

    @staticmethod
    def process_from_module(module):
        "Return the running process with path module"

        # set up the variable to pass to EnumProcesses
        processes = (ctypes.c_int * 2000)()
        bytes_returned = ctypes.c_int()
        # collect all the running processes
        ctypes.windll.psapi.EnumProcesses(
            ctypes.byref(processes),
            ctypes.sizeof(processes),
            ctypes.byref(bytes_returned))

        # check if the running process
        for i in range(0, bytes_returned.value / ctypes.sizeof(ctypes.c_int)):
            temp_process = _Process(processes[i])
            if module.lower() in temp_process.module().lower():
                return temp_process

        raise ProcessNotFoundError("No running process - '%s' found"% module)



if __name__ == '__main__':
    import test_application
    test_application.Main()
