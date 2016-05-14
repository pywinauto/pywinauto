# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2011 Mark Mc Mahon
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

"""The application module is the main one that users will use first.

When starting to automate an application you must initialize an instance
of the Application class. Then you must :func:`Application.Start` that
application or :func:`Application.Connect()` to a running instance of that
application.

Once you have an Application instance you can access dialogs in that
application either by using one of the methods below. ::

   dlg = app.YourDialogTitle
   dlg = app.ChildWindow(title = "your title", classname = "your class", ...)
   dlg = app['Your Dialog Title']

Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways. ::

  ctrl = dlg.YourControlTitle
  ctrl = dlg.ChildWindow(title = "Your control", classname = "Button", ...)
  ctrl = dlg["Your control"]

.. note::

   For attribute access of controls and dialogs you do not have to
   have the title of the control exactly, it does a best match of the
   available dialogs or controls.

.. seealso::

  :func:`pywinauto.findwindows.find_windows` for the keyword arguments that
  can be passed to both: :func:`Application.Window_` and
  :func:`WindowSpecification.Window`
"""
from __future__ import print_function

import os.path
import pickle
import time
import warnings

import win32process
import win32api
import win32gui
import win32con
import win32event
import multiprocessing

from functools import partial

from . import controls
from . import findbestmatch
from . import findwindows
from . import handleprops
from .backend import registry

from .actionlogger import ActionLogger
from .timings import Timings, WaitUntil, TimeoutError, WaitUntilPasses, wait_until_passes
from .sysinfo import is_x64_Python


class AppStartError(Exception):

    """There was a problem starting the Application"""

    pass    #pragma: no cover

class ProcessNotFoundError(Exception):

    """Could not find that process"""

    pass    #pragma: no cover

class AppNotConnected(Exception):

    """Application has not been connected to a process yet"""

    pass    #pragma: no cover


# Display User and Deprecation warnings every time
for warning in (UserWarning, PendingDeprecationWarning):
    warnings.simplefilter('always', warning)


#wait_method_deprecation = "Wait* functions are just simple wrappers around " \
#    "Wait() or WaitNot(), so they may be removed in the future!"

#=========================================================================
class WindowSpecification(object):

    """
    A specification for finding a window or control

    Windows are resolved when used.
    You can also wait for existance or non existance of a window 
 
    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """

    WAIT_CRITERIA_MAP = {'exists': ('Exists',),
                         'visible': ('is_visible',),
                         'enabled': ('is_enabled',),
                         'ready': ('is_visible', 'is_enabled',),
                         'active': ('is_active',),
                         }

    def __init__(self, search_criteria):
        """
        Initialize the class

        :param search_criteria: the criteria to match a dialog
        """
        # kwargs will contain however to find this window
        if 'backend' not in search_criteria:
            search_criteria['backend'] = registry.active_backend.name
        self.criteria = [search_criteria, ]
        self.actions = ActionLogger()
        self.backend = registry.backends[search_criteria['backend']]

    def __call__(self, *args, **kwargs):
        """No __call__ so return a usefull error"""
        if "best_match" in self.criteria[-1]:
            raise AttributeError(
                "WindowSpecification class has no '{0}' method".\
                format(self.criteria[-1]['best_match']) )

        message = (
            "You tried to execute a function call on a WindowSpecification "
            "instance. You probably have a typo for one of the methods of "
            "this class.\n"
            "The criteria leading up to this is: " + str(self.criteria))

        raise AttributeError(message)


    def __get_ctrl(self, criteria_):
        """Get the control based on the various criteria"""
        # make a copy of the criteria
        criteria = [crit.copy() for crit in criteria_]
        # find the dialog
        if 'backend' not in criteria[0]:
            criteria[0]['backend'] = self.backend.name
        dialog = self.backend.generic_wrapper_class(findwindows.find_element(**criteria[0]))
        #dialog = BaseWrapper(findwindows.find_element(**criteria[0]))

        ctrl = None
        # if there is only criteria for a dialog then return it
        if len(criteria) > 1:
            # so there was criteria for a control, add the extra criteria
            # that are required for child controls
            ctrl_criteria = criteria[1]
            ctrl_criteria["top_level_only"] = False
            if "parent" not in ctrl_criteria:
                ctrl_criteria["parent"] = dialog.handle

            # resolve the control and return it
            if 'backend' not in ctrl_criteria:
                ctrl_criteria['backend'] = self.backend.name
            ctrl = self.backend.generic_wrapper_class(findwindows.find_element(**ctrl_criteria))
            #ctrl = BaseWrapper(findwindows.find_element(**ctrl_criteria))

        if ctrl:
            return (dialog, ctrl)
        else:
            return (dialog, )


    def __resolve_control(self, criteria, timeout = None, retry_interval = None):
        """
        Find a control using criteria

        * **criteria** - a list that contains 1 or 2 dictionaries

             1st element is search criteria for the dialog

             2nd element is the search criteria for a control of the dialog

        * **timeout** -  maximum length of time to try to find the controls (default 5)
        * **retry_interval** - how long to wait between each retry (default .2)
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            ctrl = WaitUntilPasses(
                timeout,
                retry_interval,
                self.__get_ctrl,
                (findwindows.ElementNotFoundError,
                findbestmatch.MatchError,
                controls.InvalidWindowHandle,
                controls.InvalidElement),
                criteria)

        except TimeoutError as e:
            raise e.original_exception

        return ctrl


    def wrapper_object(self):
        """Allow the calling code to get the HwndWrapper object"""
        ctrls = self.__resolve_control(self.criteria)
        return ctrls[-1]

    # Non PEP-8 alias
    WrapperObject = wrapper_object

    def child_window(self, **criteria):
        """
        Add criteria for a control

        When this window specification is resolved then this will be used
        to match against a control.
        """
        # default to non top level windows because we are usualy
        # looking for a control
        if 'top_level_only' not in criteria:
            criteria['top_level_only'] = False

        new_item = WindowSpecification(self.criteria[0])
        new_item.criteria.append(criteria)

        return new_item

    # Non PEP-8 alias
    ChildWindow = child_window

    def Window_(self, **criteria):
        """Deprecated alias of child_window()"""
        warnings.warn(
            "WindowSpecification.Window() WindowSpecification.Window_(), "
            "WindowSpecification.window() and WindowSpecification.window_() "
            "are deprecated, please switch to WindowSpecification.child_window()",
            DeprecationWarning)
        return self.child_window(**criteria)
    window_ = Window_
    Window = Window_

    def __getitem__(self, key):
        """
        Allow access to dialogs/controls through item access

        This allows::

            app['DialogTitle']['ControlTextClass']

        to be used to access dialogs and controls.

        Both this and :func:`__getattribute__` use the rules outlined in the
        HowTo document.
        """
        # if we already have 2 levels of criteria (dlg, control)
        # then resolve the control and do a getitem on it for the
        if len(self.criteria) == 2:

            ctrls = self.__resolve_control(self.criteria)

            # try to return a good error message if the control does not
            # have a __getitem__() method)
            if hasattr(ctrls[-1], '__getitem__'):
                return ctrls[-1][key]
            else:
                message = "The control does not have a __getitem__ method " \
                    "for item access (i.e. ctrl[key]) so maybe you have " \
                    "requested this in error?"

                raise AttributeError(message)

        # if we get here then we must have only had one criteria so far
        # so create a new :class:`WindowSpecification` for this control
        new_item = WindowSpecification(self.criteria[0])

        # add our new criteria
        new_item.criteria.append({"best_match" : key})

        return new_item


    def __getattribute__(self, attr_name):
        """
        Attribute access for this class

        If we already have criteria for both dialog and control then
        resolve the control and return the requested attribute.

        If we have only criteria for the dialog but the attribute
        requested is an attribute of DialogWrapper then resolve the
        dialog and return the requested attribute.

        Otherwise delegate functionality to :func:`__getitem__` - which
        sets the appropriate criteria for the control.
        """
        if attr_name in ['__dict__', '__members__', '__methods__', '__class__', '__name__']:
            return object.__getattribute__(self, attr_name)

        if attr_name in dir(self.__class__):
            return object.__getattribute__(self, attr_name)

        if attr_name in self.__dict__:
            return self.__dict__[attr_name]

        from .controls.win32_controls import DialogWrapper

        # if we already have 2 levels of criteria (dlg, conrol)
        # this third must be an attribute so resolve and get the
        # attribute and return it
        if len(self.criteria) == 2:

            ctrls = self.__resolve_control(self.criteria)

            return getattr(ctrls[-1], attr_name)

        else:
            # if we have been asked for an attribute of the dialog
            # then resolve the window and return the attribute
            if len(self.criteria) == 1 and hasattr(DialogWrapper, attr_name):

                ctrls = self.__resolve_control(self.criteria)

                return getattr(ctrls[-1], attr_name)

        # It is a dialog/control criterion so let getitem
        # deal with it
        return self[attr_name]


    def exists(self, timeout = None, retry_interval = None):
        """
        Check if the window exists, return True if the control exists

        :param timeout: the maximum amount of time to wait for the
                    control to exists. Defaults to ``Timings.exists_timeout``
        :param retry_interval: The control is checked for existance this number
                    of seconds. ``Defaults to Timings.exists_retry``
        """
        # set the current timings -couldn't set as defaults as they are
        # evaluated at import time - and timings may be changed at any time
        if timeout is None:
            timeout = Timings.exists_timeout
        if retry_interval is None:
            retry_interval = Timings.exists_retry


        # modify the criteria as exists should look for all
        # windows - including not visible and disabled
        exists_criteria = self.criteria[:]
        for criterion in exists_criteria:
            criterion['enabled_only'] = False
            criterion['visible_only'] = False

        try:
            self.__resolve_control(exists_criteria, timeout, retry_interval)

            return True
        except (
            findwindows.ElementNotFoundError,
            findbestmatch.MatchError,
            controls.InvalidWindowHandle,
            controls.InvalidElement):
            return False

    # Non PEP-8 alias
    Exists = exists

    @classmethod
    def __parse_wait_args(cls, wait_conditions, timeout, retry_interval):
        """Both methods wait & wait_not have the same args handling"""
        # set the current timings -couldn't set as defaults as they are
        # evaluated at import time - and timings may be changed at any time
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        # allow for case mixups - just to make it easier to use
        wait_for = wait_conditions.lower()

        # get checking methods from the map by wait_conditions string
        # To avoid needless checks - use a set to filter duplicates
        unique_check_names = set()
        wait_criteria_names = wait_for.split()
        for criteria_name in wait_criteria_names:
            try:
                check_methods = cls.WAIT_CRITERIA_MAP[criteria_name]
            except KeyError:
                # Invalid check name in the wait_for
                raise SyntaxError('Unexpected criteria - %s' % criteria_name)
            else:
                unique_check_names.update(check_methods)

        # unique_check_names = set(['is_enabled', 'is_active', 'is_visible', 'Exists'])
        return unique_check_names, timeout, retry_interval

    def __check_all_conditions(self, check_names):
        """
        Checks for all conditions

        If any check's result != True return False immediately, do not matter others check results.
        True will be returned when all checks passed and all of them equal True.
        """
        for check_name in check_names:
            try:
                # Hidden __resolve_control call, handle the exceptions.
                check = getattr(self, check_name)
            except (findwindows.ElementNotFoundError,
                    findbestmatch.MatchError,
                    controls.InvalidWindowHandle,
                    controls.InvalidElement):
                # The control does not exist
                return False
            else:
                if not check():
                    # At least one check not passed
                    return False

        # All the checks have been done
        return True

    def wait(self, wait_for, timeout=None, retry_interval=None):
        """
        Wait for the window to be in a particular state/states.

        :param wait_for: The state to wait for the window to be in. It can
            be any of the following states, also you may combine the states by space key.

             * 'exists' means that the window is a valid handle
             * 'visible' means that the window is not hidden
             * 'enabled' means that the window is not disabled
             * 'ready' means that the window is visible and enabled
             * 'active' means that the window is active

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is not in the appropriate state after this number of seconds.

        :param retry_interval: How long to sleep between each retry.
        Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.

        An example to wait until the dialog
        exists, is ready, enabled and visible::

            self.Dlg.wait("exists enabled visible ready")

        .. seealso::
           :func:`WindowSpecification.WaitNot()`

           :func:`pywinauto.timings.TimeoutError`
        """
        check_method_names, timeout, retry_interval = self.__parse_wait_args(wait_for, timeout, retry_interval)
        WaitUntil(timeout, retry_interval, lambda: self.__check_all_conditions(check_method_names))

        # Return the wrapped control
        return self.wrapper_object()

    # Non PEP-8 alias
    Wait = wait

    def wait_not(self, wait_for_not, timeout=None, retry_interval=None):
        """
        Wait for the window to not be in a particular state/states.

        :param wait_for_not: The state to wait for the window to not be in. It can be any
            of the following states, also you may combine the states by space key.

             * 'exists' means that the window is a valid handle
             * 'visible' means that the window is not hidden
             * 'enabled' means that the window is not disabled
             * 'ready' means that the window is visible and enabled
             * 'active' means that the window is active

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window is sill in the
            state after this number of seconds.

        :param retry_interval: How long to sleep between each retry.
        Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.

        An example to wait until the dialog is not ready, enabled or visible::

            self.Dlg.wait_not("enabled visible ready")

        .. seealso::
           :func:`WindowSpecification.Wait()`

           :func:`pywinauto.timings.TimeoutError`
        """
        check_method_names, timeout, retry_interval = \
            self.__parse_wait_args(wait_for_not, timeout, retry_interval)
        WaitUntil(timeout, retry_interval, lambda: not self.__check_all_conditions(check_method_names))
        # None return value, since we are waiting for a `negative` state of the control.
        # Expect that you will have nothing to do with the window closed, disabled, etc.

    # Non PEP-8 alias
    WaitNot = wait_not

    def _ctrl_identifiers(self):

        ctrls = self.__resolve_control(self.criteria)

        if ctrls[-1].is_dialog():
            # dialog controls are all the control on the dialog
            dialog_controls = ctrls[-1].children()

            ctrls_to_print = dialog_controls[:]
            # filter out hidden controls
            ctrls_to_print = [
                ctrl for ctrl in ctrls_to_print if ctrl.is_visible()]
        else:
            dialog_controls = ctrls[-1].top_level_parent().children()
            ctrls_to_print = [ctrls[-1]]

        # build the list of disambiguated list of control names
        name_control_map = findbestmatch.build_unique_dict(dialog_controls)

        # swap it around so that we are mapped off the controls
        control_name_map = {}
        for name, ctrl in name_control_map.items():
            control_name_map.setdefault(ctrl, []).append(name)

        return control_name_map

    def print_control_identifiers(self, depth = 2):
        """
        Prints the 'identifiers'

        Prints identifiers for the control and for its descendants to
        a depth of **depth**.

        .. note:: The identifiers printed by this method have been made
               unique. So if you have 2 edit boxes, they won't both have "Edit"
               listed in their identifiers. In fact the first one can be
               referred to as "Edit", "Edit0", "Edit1" and the 2nd should be
               referred to as "Edit2".
        """
        # Wrap this control
        this_ctrl = self.__resolve_control(self.criteria)[-1]

        # Create a list of this control and all its descendants
        all_ctrls = [this_ctrl, ] + this_ctrl.descendants()

        # build the list of disambiguated list of control names
        name_control_map = findbestmatch.build_unique_dict(all_ctrls)

        # swap it around so that we are mapped off the controls
        control_name_map = {}
        for name, control in name_control_map.items():
            control_name_map.setdefault(control, []).append(name)

        print("Control Identifiers:")

        def print_identifiers(ctrls, current_depth = 1):
            """
            Recursive function that prints identifiers for ctrls and
            theirs descendants in a tree-like format
            """
            if len(ctrls) == 0 or current_depth > depth:
                return

            for ctrl in ctrls:
                print((current_depth - 1) * "     | ")

                print((current_depth - 1) * "     | ", end='')
                print("{class_name} - '{text}'    {rect}\t".format(
                    class_name=ctrl.friendly_class_name(),
                    text=ctrl.window_text(),
                    rect=str(ctrl.rectangle())))
                print((current_depth - 1) * "     | ", end='')
                print(control_name_map[ctrl])

                print_identifiers(ctrl.children(), current_depth + 1)

        print_identifiers([this_ctrl, ])

    # Non PEP-8 alias
    PrintControlIdentifiers = print_control_identifiers


cur_item = 0

def _resolve_from_appdata(
    criteria_, app, timeout = None, retry_interval = None):
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
    for unloc_attrib in ['title_re', 'title', 'best_match']:
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
            #dialog = BaseWrapper(e)

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
                         if elem.control_id == \
                         matched_control[2]['control_id']]

                    if same_ids:
                        ctrl_elems = same_ids

                try:
                    ctrl = registry.wrapper_class(ctrl_elems[0])
                    #ctrl = BaseWrapper(ctrl_elems[0])
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


##
##        # if best match was specified for the dialog
##        # then we need to replace it with other values
##        # for now we will just use class_name
##        for crit in ['best_match', 'title', 'title_re']:
##            if crit in criteria[0]:
##                del(criteria[0][crit])
##                criteria[0]['class_name'] = app_data[0].class_name()#['class_name']
##
##            if len(criteria) > 1:
##                # find the best match of the application data
##                if criteria[1].has_key('best_match'):
##                    best_match = findbestmatch.find_best_control_matches(
##                        criteria[1]['best_match'], app_data)[0]
##
##                    #visible_controls = [ctrl in app_data if ctrl.is_visible()]
##
##                    #find the index of the best match item
##                    ctrl_index = app_data.index(best_match)
##                    #print best_match[0].window_text()
##                    ctrl_index, best_match.window_text()
##
##                    criteria[1]['ctrl_index'] = ctrl_index -1
##                    #criteria[1]['class_name'] = best_match.class_name()
##                    #del(criteria[1]['best_match'])
##
## One idea here would be to run the new criteria on the app_data dialog and
## if it returns more then one control then you figure out which one would be
## best - so that you have that info when running on the current dialog
##
##            #for criterion in criteria[1:]:
##                # this part is weird - we now have to go off and find the
##                # index, class, text of the control in the app_data
##                # and then find the best match for this control in the
##                # current dialog
##            #    pass
##
##

#    dialog = None

    #return _resolve_control(criteria_, timeout, retry_interval)




#=========================================================================
class Application(object):

    """
    Represents an application
 
    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """

    def __init__(self, backend = "native", datafilename = None):
        """
        Initialize the Appliction object
        
        * **backend** is a name of used back-end (values: "native", "uia").
        * **datafilename** is a file name for reading matching history.
        """
        self.process = None
        self.xmlpath = ''

        self.match_history = []
        self.use_history = False
        self.actions = ActionLogger()
        if backend not in registry.backends:
            raise ValueError('Backend "{0}" is not registered!'.format(backend))
        self.backend = registry.backends[backend]

        # load the match history if a file was specifed
        # and it exists
        if datafilename and os.path.exists(datafilename):
            with open(datafilename, "rb") as datafile:
                self.match_history = pickle.load(datafile)
            self.use_history = True

    def __connect(self, **kwargs):
        """
        Deprecated method. Performs PendingDeprecationWarning before calling
        the .connect().
        Should be also removed in 0.6.X.
        """
        warnings.warn(
            "connect_()/Connect_() methods are deprecated, "
            "please switch to instance method connect(). "
            "Connect() is an alias to the connect() method. "
            "Please note that both Connect() and connect() "
            "are instance methods.", PendingDeprecationWarning)
        return self.connect(**kwargs)

    connect_ = __connect  # A deprecated name. Should be removed in 0.6.X
    Connect_ = __connect  # A deprecated name. Should be removed in 0.6.X

    def connect(self, **kwargs):
        """Connects to an already running process"""

        def get_connected(self, **kwargs):

            if 'process' in kwargs:
                self.process = kwargs['process']
                assert_valid_process(self.process)
                connected = True

            elif 'handle' in kwargs:

                if not handleprops.iswindow(kwargs['handle']):
                    message = "Invalid handle 0x%x passed to connect()" % (kwargs['handle'])
                    raise RuntimeError(message)

                self.process = handleprops.processid(kwargs['handle'])

                connected = True

            elif 'path' in kwargs:
                self.process = process_from_module(kwargs['path'])
                connected = True

            elif kwargs:
                kwargs['backend'] = self.backend.name
                self.process = findwindows.find_element(**kwargs).process_id
                connected = True

            return connected

        timeout = Timings.app_start_timeout
        if 'timeout' in kwargs:
            timeout = float(kwargs['timeout'])
            del kwargs['timeout']

        connected = wait_until_passes(timeout, Timings.app_connect_retry, partial(get_connected, self = self, **kwargs), (ValueError, ProcessNotFoundError, RuntimeError))

        if not connected:
            raise RuntimeError(
                "You must specify one of process, handle or path")

        self.__warn_incorrect_bitness()

        return self

    Connect = connect




    def __start(self, *args, **kwargs):
        """
        Deprecated method. Performs PendingDeprecationWarning before
        calling the .start().
        Should be also removed in 0.6.X.
        """
        warnings.warn(
            "start_()/Start_() methods are deprecated, "
            "please switch to instance method start(). "
            "Start() is an alias to the start() method. "
            "Please note that both Start() and start() are instance methods.",
            PendingDeprecationWarning)
        return self.start(*args, **kwargs)

    start_ = __start  # A deprecated name. Should be removed in 0.6.X
    Start_ = __start  # A deprecated name. Should be removed in 0.6.X

    def start(self, cmd_line, timeout=None, retry_interval=None,
              create_new_console=False, wait_for_idle=True):
        """Starts the application giving in cmd_line"""
        # try to parse executable name and check it has correct bitness
        if '.exe' in cmd_line:
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
                None, 					# Use parent's starting directory.
                start_info)				# STARTUPINFO structure.
        except Exception as exc:
            # if it failed for some reason
            message = ('Could not create the process "%s"\n'
                'Error returned by CreateProcess: %s')% (
                    cmd_line, str(exc))
            raise AppStartError(message)

        self.process = dw_process_id

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

            return bool(self.windows_())

        # Wait until the application is ready after starting it
        if wait_for_idle and not app_idle():
            warnings.warn('Application is not loaded correctly (WaitForInputIdle failed)', RuntimeWarning)

        return self

    # Non PEP-8 alias
    Start = start

    def __warn_incorrect_bitness(self):
        if self.is64bit() != is_x64_Python():
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

    def cpu_usage(self, interval = None):
        """Return CPU usage percent during specified number of seconds"""
        WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7
        
        if interval is None:
            interval = Timings.cpu_usage_interval
        
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        h_process = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, 0, self.process)
        
        times_dict = win32process.GetProcessTimes(h_process)
        UserTime_start, KernelTime_start = times_dict['UserTime'], times_dict['KernelTime']
        
        time.sleep(interval)
        
        times_dict = win32process.GetProcessTimes(h_process)
        UserTime_end, KernelTime_end = times_dict['UserTime'], times_dict['KernelTime']
        
        total_time = (UserTime_end - UserTime_start) / WIN32_PROCESS_TIMES_TICKS_PER_SECOND + \
                     (KernelTime_end - KernelTime_start) / WIN32_PROCESS_TIMES_TICKS_PER_SECOND
        
        win32api.CloseHandle(h_process)
        return 100.0 * (total_time / (float(interval) * multiprocessing.cpu_count()))

    # Non PEP-8 alias
    CPUUsage = cpu_usage

    def wait_cpu_usage_lower(self, threshold = 2.5, timeout = None, usage_interval = None):
        """Wait until process CPU usage percentage is less than specified threshold"""
        if usage_interval is None:
            usage_interval = Timings.cpu_usage_interval
        if timeout is None:
            timeout = Timings.cpu_usage_wait_timeout
        
        start_time = time.time()
        
        while self.CPUUsage(usage_interval) > threshold:
            if time.time() - start_time > timeout:
                raise RuntimeError('Waiting CPU load <= ' + str(threshold) + '% timed out!')
        
        return self

    # Non PEP-8 alias
    WaitCPUUsageLower = wait_cpu_usage_lower

    def top_window_(self):
        """Return the current top window of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        timeout = Timings.window_find_timeout
        while timeout >= 0:
            windows = findwindows.find_elements(process = self.process, backend = self.backend.name)
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
            criteria['title'] = windows[0].name

        return WindowSpecification(criteria)

    def active_(self):
        """Return the active window of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        time.sleep(Timings.window_find_timeout)
        # very simple
        windows = findwindows.find_elements(process = self.process, active_only = True, backend = self.backend.name)

        if not windows:
            raise RuntimeError("No Windows of that application are active")

        criteria = {}
        criteria['backend'] = self.backend.name
        if windows[0].handle:
            criteria['handle'] = windows[0].handle
        else:
            criteria['title'] = windows[0].name

        return WindowSpecification(criteria)


    def windows_(self, **kwargs):
        """Return list of wrapped top level windows of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        if 'backend' in kwargs:
            raise ValueError('Using another backend for this Application '
                             'instance is not allowed! Create another app object.')

        if 'visible_only' not in kwargs:
            kwargs['visible_only'] = False

        if 'enabled_only' not in kwargs:
            kwargs['enabled_only'] = False

        kwargs['process'] = self.process
        kwargs['backend'] = self.backend.name

        windows = findwindows.find_elements(**kwargs)
        return [self.backend.generic_wrapper_class(win) for win in windows]
        #return [BaseWrapper(win) for win in windows]

    Windows_ = windows_


    def window_(self, **kwargs):
        """
        Return a window of the application

        You can specify the same parameters as findwindows.find_windows.
        It will add the process parameter to ensure that the window is from
        the current process.
        """
        if 'backend' in kwargs:
            raise ValueError('Using another backend than set in the app constructor is not allowed!')
        kwargs['backend'] = self.backend.name

        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        else:
            # add the restriction for this particular process
            kwargs['process'] = self.process
            win_spec = WindowSpecification(kwargs)

        return win_spec
    Window_ = window_

    def __getitem__(self, key):
        """Find the specified dialog of the application"""
        # delegate searching functionality to self.window_()
        return self.window_(best_match = key)

    def __getattribute__(self, attr_name):
        """Find the specified dialog of the application"""
        if attr_name in ['__dict__', '__members__', '__methods__', '__class__']:
            return object.__getattribute__(self, attr_name)

        if attr_name in dir(Application):
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


    def Kill_(self):
        """
        Try to close and kill the application

        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        this should only be used when it is OK to kill the process like you
        would in task manager.
        """
        windows = self.windows_(visible_only = True)

        for win in windows:

            if hasattr(win, 'force_close') and win.force_close():
                continue

            try:
                if hasattr(win, 'close'):
                    win.close()
            except TimeoutError:
                self.actions.log('Failed to close top level window')

        try:
            process_wait_handle = win32api.OpenProcess(
                win32con.SYNCHRONIZE | win32con.PROCESS_TERMINATE,
                0,
                self.process)
        except win32gui.error:
            return True # already closed
        
        # so we have either closed the windows - or the app is hung
        killed = True
        if process_wait_handle:
            try:
                win32api.TerminateProcess(process_wait_handle, 0)
            except win32gui.error:
                self.actions.log('Process {0} seems already killed'.format(self.process))

        win32api.CloseHandle(process_wait_handle)

        return killed

    kill_ = Kill_


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

    return process_handle

AssertValidProcess = assert_valid_process # just in case

#=========================================================================
def process_get_modules():
    """Return the list of processes as tuples (pid, exe_path)"""
    modules = []
    
    # collect all the running processes
    pids = win32process.EnumProcesses()
    for pid in pids:
        if pid != 0 and isinstance(pid, int): # skip system process (0x00000000)
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
            modules.append((p.ProcessId, p.ExecutablePath, p.CommandLine)) # p.Name
    return modules

#=========================================================================
def process_module(process_id):
    """Return the string module name of this process"""
    process_handle = assert_valid_process(process_id)

    return win32process.GetModuleFileNameEx(process_handle, 0)

#=========================================================================
def _warn_incorrect_binary_bitness(exe_name):
    """warn if executable is of incorrect bitness"""
    if os.path.isabs(exe_name) and os.path.isfile(exe_name) and \
            handleprops.is64bitbinary(exe_name) and not is_x64_Python():
        warnings.warn(
            "64-bit binary from 32-bit Python may work incorrectly " \
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
    for process, name, cmdline in modules:
        if name is None:
            continue
        if module_path.lower() in name.lower():
            return process

    message = "Could not find any accessible process with a module of '{0}'".format(module)
    raise ProcessNotFoundError(message)
