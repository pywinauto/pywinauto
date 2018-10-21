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

"""The application module is the main one that users will use first.

When starting to automate an application you must initialize an instance
of the Application class. Then you must :func:`Application.start` that
application or :func:`Application.connect()` to a running instance of that
application.

Once you have an Application instance you can access dialogs in that
application either by using one of the methods below. ::

   dlg = app.YourDialogTitle
   dlg = app.child_window(title="your title", classname="your class", ...)
   dlg = app['Your Dialog Title']

Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways. ::

  ctrl = dlg.YourControlTitle
  ctrl = dlg.child_window(title="Your control", classname="Button", ...)
  ctrl = dlg["Your control"]

.. note::

   For attribute access of controls and dialogs you do not have to
   have the title of the control exactly, it does a best match of the
   available dialogs or controls.

.. seealso::

   :func:`pywinauto.findwindows.find_elements` for the keyword arguments that
   can be passed to both: :func:`Application.window` and
   :func:`WindowSpecification.child_window`
"""
from __future__ import print_function

import sys
import os
import pickle
import time
import warnings
import multiprocessing
import locale

import win32process
import win32api
import win32gui
import win32con
import win32event
import six

from . import timings
from . import controls
from . import findbestmatch
from . import findwindows
from . import handleprops
from . import win32defines
from .backend import registry

from .actionlogger import ActionLogger
from .timings import Timings, wait_until, TimeoutError, wait_until_passes
from .sysinfo import is_x64_Python
from . import deprecated


class AppStartError(Exception):

    """There was a problem starting the Application"""

    pass    # pragma: no cover


class ProcessNotFoundError(Exception):

    """Could not find that process"""

    pass    # pragma: no cover


class AppNotConnected(Exception):

    """Application has not been connected to a process yet"""

    pass    # pragma: no cover


# Display User and Deprecation warnings every time
for warning in (UserWarning, PendingDeprecationWarning):
    warnings.simplefilter('always', warning)


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

    WAIT_CRITERIA_MAP = {'exists': ('exists',),
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

        if self.backend.name == 'win32':
            # Non PEP-8 aliases for partial backward compatibility
            self.WrapperObject = deprecated(self.wrapper_object)
            self.ChildWindow = deprecated(self.child_window)
            self.Exists = deprecated(self.exists)
            self.Wait = deprecated(self.wait)
            self.WaitNot = deprecated(self.wait_not)
            self.PrintControlIdentifiers = deprecated(self.print_control_identifiers)

            self.Window = deprecated(self.child_window, deprecated_name='Window')
            self.Window_ = deprecated(self.child_window, deprecated_name='Window_')
            self.window_ = deprecated(self.child_window, deprecated_name='window_')

    def __call__(self, *args, **kwargs):
        """No __call__ so return a usefull error"""
        if "best_match" in self.criteria[-1]:
            raise AttributeError("Neither GUI element (wrapper) " \
                "nor wrapper method '{0}' were found (typo?)".
                format(self.criteria[-1]['best_match']))

        message = (
            "You tried to execute a function call on a WindowSpecification "
            "instance. You probably have a typo for one of the methods of "
            "this class.\n"
            "The criteria leading up to this is: " + str(self.criteria))

        raise AttributeError(message)

    def __get_ctrl(self, criteria_):
        """Get a control based on the various criteria"""
        # make a copy of the criteria
        criteria = [crit.copy() for crit in criteria_]
        # find the dialog
        if 'backend' not in criteria[0]:
            criteria[0]['backend'] = self.backend.name
        dialog = self.backend.generic_wrapper_class(findwindows.find_element(**criteria[0]))

        ctrls = []
        # if there is only criteria for a dialog then return it
        if len(criteria) > 1:
            # so there was criteria for a control, add the extra criteria
            # that are required for child controls
            previous_parent = dialog.element_info
            for ctrl_criteria in criteria[1:]:
                ctrl_criteria["top_level_only"] = False
                if "parent" not in ctrl_criteria:
                    ctrl_criteria["parent"] = previous_parent

                if isinstance(ctrl_criteria["parent"], WindowSpecification):
                    ctrl_criteria["parent"] = ctrl_criteria["parent"].wrapper_object()

                # resolve the control and return it
                if 'backend' not in ctrl_criteria:
                    ctrl_criteria['backend'] = self.backend.name
                ctrl = self.backend.generic_wrapper_class(findwindows.find_element(**ctrl_criteria))
                previous_parent = ctrl.element_info
                ctrls.append(ctrl)

        if ctrls:
            return (dialog, ) + tuple(ctrls)
        else:
            return (dialog, )

    def __resolve_control(self, criteria, timeout=None, retry_interval=None):
        """
        Find a control using criteria

        * **criteria** - a list that contains 1 or 2 dictionaries

             1st element is search criteria for the dialog

             2nd element is search criteria for a control of the dialog

        * **timeout** -  maximum length of time to try to find the controls (default 5)
        * **retry_interval** - how long to wait between each retry (default .2)
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            ctrl = wait_until_passes(
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

    def child_window(self, **criteria):
        """
        Add criteria for a control

        When this window specification is resolved it will be used
        to match against a control.
        """
        # default to non top level windows because we are usualy
        # looking for a control
        if 'top_level_only' not in criteria:
            criteria['top_level_only'] = False

        new_item = WindowSpecification(self.criteria[0])
        new_item.criteria.extend(self.criteria[1:])
        new_item.criteria.append(criteria)

        return new_item

    def window(self, **criteria):
        """Deprecated alias of child_window()"""
        warnings.warn(
            "WindowSpecification.Window() WindowSpecification.Window_(), "
            "WindowSpecification.window() and WindowSpecification.window_() "
            "are deprecated, please switch to WindowSpecification.child_window()",
            DeprecationWarning)
        return self.child_window(**criteria)

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
        if len(self.criteria) >= 2:

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
        new_item.criteria.append({"best_match": key})

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

        # if we already have 2 levels of criteria (dlg, conrol)
        # this third must be an attribute so resolve and get the
        # attribute and return it
        if len(self.criteria) >= 2:

            ctrls = self.__resolve_control(self.criteria)

            try:
                return getattr(ctrls[-1], attr_name)
            except AttributeError:
                return self.child_window(best_match=attr_name)
        else:
            # if we have been asked for an attribute of the dialog
            # then resolve the window and return the attribute
            desktop_wrapper = self.backend.generic_wrapper_class(self.backend.element_info_class())
            need_to_resolve = (len(self.criteria) == 1 and hasattr(desktop_wrapper, attr_name))
            if hasattr(self.backend, 'dialog_class'):
                need_to_resolve = need_to_resolve and hasattr(self.backend.dialog_class, attr_name)
            # Probably there is no DialogWrapper for another backend

            if need_to_resolve:
                ctrls = self.__resolve_control(self.criteria)
                return getattr(ctrls[-1], attr_name)

        # It is a dialog/control criterion so let getitem
        # deal with it
        return self[attr_name]

    def exists(self, timeout=None, retry_interval=None):
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
        except (findwindows.ElementNotFoundError,
                findbestmatch.MatchError,
                controls.InvalidWindowHandle,
                controls.InvalidElement):
            return False

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

    def __check_all_conditions(self, check_names, retry_interval):
        """
        Checks for all conditions

        If any check's result != True return False immediately, do not matter others check results.
        True will be returned when all checks passed and all of them equal True.
        """
        for check_name in check_names:
            # timeout = retry_interval because the timeout is handled at higher level
            if check_name == 'exists':
                check = getattr(self, check_name)
                if not check(retry_interval, float(retry_interval) // 2):
                    return False
                else:
                    continue
            try:
                # resolve control explicitly to pass correct timing params
                ctrls = self.__resolve_control(self.criteria, retry_interval, float(retry_interval) // 2)
                check = getattr(ctrls[-1], check_name)
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
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.

        An example to wait until the dialog
        exists, is ready, enabled and visible: ::

            self.Dlg.wait("exists enabled visible ready")

        .. seealso::
            :func:`WindowSpecification.wait_not()`

            :func:`pywinauto.timings.TimeoutError`
        """
        check_method_names, timeout, retry_interval = self.__parse_wait_args(wait_for, timeout, retry_interval)
        wait_until(timeout, retry_interval,
                   lambda: self.__check_all_conditions(check_method_names, retry_interval))

        # Return the wrapped control
        return self.wrapper_object()

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
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.

        An example to wait until the dialog is not ready, enabled or visible: ::

            self.Dlg.wait_not("enabled visible ready")

        .. seealso::
            :func:`WindowSpecification.wait()`

            :func:`pywinauto.timings.TimeoutError`
        """
        check_method_names, timeout, retry_interval = \
            self.__parse_wait_args(wait_for_not, timeout, retry_interval)
        wait_until(timeout, retry_interval,
                   lambda: not self.__check_all_conditions(check_method_names, retry_interval))
        # None return value, since we are waiting for a `negative` state of the control.
        # Expect that you will have nothing to do with the window closed, disabled, etc.

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

    def print_control_identifiers(self, depth=None, filename=None):
        """
        Prints the 'identifiers'

        Prints identifiers for the control and for its descendants to
        a depth of **depth** (the whole subtree if **None**).

        .. note:: The identifiers printed by this method have been made
               unique. So if you have 2 edit boxes, they won't both have "Edit"
               listed in their identifiers. In fact the first one can be
               referred to as "Edit", "Edit0", "Edit1" and the 2nd should be
               referred to as "Edit2".
        """
        if depth is None:
            depth = sys.maxsize
        # Wrap this control
        this_ctrl = self.__resolve_control(self.criteria)[-1]

        # Create a list of this control and all its descendants
        all_ctrls = [this_ctrl, ] + this_ctrl.descendants()

        # Create a list of all visible text controls
        txt_ctrls = [ctrl for ctrl in all_ctrls if ctrl.can_be_label and ctrl.is_visible() and ctrl.window_text()]

        # Build a dictionary of disambiguated list of control names
        name_ctrl_id_map = findbestmatch.UniqueDict()
        for index, ctrl in enumerate(all_ctrls):
            ctrl_names = findbestmatch.get_control_names(ctrl, all_ctrls, txt_ctrls)
            for name in ctrl_names:
                name_ctrl_id_map[name] = index

        # Swap it around so that we are mapped off the control indices
        ctrl_id_name_map = {}
        for name, index in name_ctrl_id_map.items():
            ctrl_id_name_map.setdefault(index, []).append(name)

        def print_identifiers(ctrls, current_depth=1, log_func=print):
            """Recursively print ids for ctrls and their descendants in a tree-like format"""
            if len(ctrls) == 0 or current_depth > depth:
                return

            indent = (current_depth - 1) * u"   | "
            for ctrl in ctrls:
                try:
                    ctrl_id = all_ctrls.index(ctrl)
                except ValueError:
                    continue
                ctrl_text = ctrl.window_text()
                if ctrl_text:
                    # transform multi-line text to one liner
                    ctrl_text = ctrl_text.replace('\n', r'\n').replace('\r', r'\r')

                output = indent + u'\n'
                output += indent + u"{class_name} - '{text}'    {rect}\n"\
                    "".format(class_name=ctrl.friendly_class_name(),
                              text=ctrl_text,
                              rect=ctrl.rectangle())
                output += indent + u'{}'.format(ctrl_id_name_map[ctrl_id])

                title = ctrl_text
                class_name = ctrl.class_name()
                auto_id = None
                control_type = None
                if hasattr(ctrl.element_info, 'automation_id'):
                    auto_id = ctrl.element_info.automation_id
                if hasattr(ctrl.element_info, 'control_type'):
                    control_type = ctrl.element_info.control_type
                    if control_type:
                        class_name = None  # no need for class_name if control_type exists
                    else:
                        control_type = None # if control_type is empty, still use class_name instead
                criteria_texts = []
                if title:
                    criteria_texts.append(u'title="{}"'.format(title))
                if class_name:
                    criteria_texts.append(u'class_name="{}"'.format(class_name))
                if auto_id:
                    criteria_texts.append(u'auto_id="{}"'.format(auto_id))
                if control_type:
                    criteria_texts.append(u'control_type="{}"'.format(control_type))
                if title or class_name or auto_id:
                    output += u'\n' + indent + u'child_window(' + u', '.join(criteria_texts) + u')'

                if six.PY3:
                    log_func(output)
                else:
                    log_func(output.encode(locale.getpreferredencoding(), errors='backslashreplace'))

                print_identifiers(ctrl.children(), current_depth + 1, log_func)

        if filename is None:
            print("Control Identifiers:")
            print_identifiers([this_ctrl, ])
        else:
            log_file = open(filename, "w")

            def log_func(msg):
                log_file.write(str(msg) + os.linesep)
            log_func("Control Identifiers:")
            print_identifiers([this_ctrl, ], log_func=log_func)
            log_file.close()

    print_ctrl_ids = print_control_identifiers
    dump_tree = print_control_identifiers

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
class Application(object):

    """
    Represents an application

    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """

    def __init__(self, backend="win32", datafilename=None):
        """
        Initialize the Application object

        * **backend** is a name of used back-end (values: "win32", "uia").
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

    def connect(self, **kwargs):
        """Connect to an already running process

        The action is performed according to only one of parameters

        :param process: a process ID of the target
        :param handle: a window handle of the target
        :param path: a path used to launch the target
        :param timeout: a timeout for process start (relevant if path is specified)

        .. seealso::

           :func:`pywinauto.findwindows.find_elements` - the keyword arguments that
           are also can be used instead of **process**, **handle** or **path**
        """
        timeout = Timings.app_connect_timeout
        retry_interval = Timings.app_connect_retry
        if 'timeout' in kwargs and kwargs['timeout'] is not None:
            timeout = kwargs['timeout']
        if 'retry_interval' in kwargs and kwargs['retry_interval'] is not None:
            retry_interval = kwargs['retry_interval']

        connected = False
        if 'process' in kwargs:
            self.process = kwargs['process']
            try:
                timings.wait_until_passes(
                        timeout, retry_interval, assert_valid_process,
                        ProcessNotFoundError, self.process
                    )
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
                self.process = timings.wait_until_passes(
                        timeout, retry_interval, process_from_module,
                        ProcessNotFoundError, kwargs['path'],
                    )
            except TimeoutError:
                raise ProcessNotFoundError('Process "{}" not found!'.format(kwargs['path']))
            connected = True

        elif kwargs:
            kwargs['backend'] = self.backend.name
            if 'timeout' in kwargs:
                del kwargs['timeout']
                self.process = timings.wait_until_passes(
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
            windows = findwindows.find_elements(process=self.process,
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
            criteria['title'] = windows[0].name

        return WindowSpecification(criteria)

    def active(self):
        """Return WindowSpecification for an active window of the application"""
        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")

        time.sleep(Timings.window_find_timeout)
        # very simple
        windows = findwindows.find_elements(process=self.process,
                                            active_only=True,
                                            backend=self.backend.name)

        if not windows:
            raise RuntimeError("No Windows of that application are active")

        criteria = {}
        criteria['backend'] = self.backend.name
        if windows[0].handle:
            criteria['handle'] = windows[0].handle
        else:
            criteria['title'] = windows[0].name

        return WindowSpecification(criteria)

    def windows(self, **kwargs):
        """Return a list of wrapped top level windows of the application"""
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

        if not self.process:
            raise AppNotConnected("Please use start or connect before trying "
                                  "anything else")
        else:
            # add the restriction for this particular process
            kwargs['process'] = self.process
            win_spec = WindowSpecification(kwargs)

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

    def WriteAppData(self, filename):
        """Should not be used - part of application data implementation"""
        with open(filename, "wb") as f:
            pickle.dump(self.match_history, f)

    def GetMatchHistoryItem(self, index):
        """Should not be used - part of application data implementation"""
        return self.match_history[index]

    def kill(self):
        """
        Try to close and kill the application

        Dialogs may pop up asking to save data - but the application
        will be killed anyway - you will not be able to click the buttons.
        This should only be used when it is OK to kill the process like you
        would do in task manager.
        """
        windows = self.windows(visible_only=True)

        for win in windows:

            try:
                if hasattr(win, 'close'):
                    win.close()
                    continue
            except TimeoutError:
                self.actions.log('Failed to close top level window')

            if hasattr(win, 'force_close'):
                self.actions.log('application.kill: call win.force_close')
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
        if process_wait_handle:
            try:
                win32api.TerminateProcess(process_wait_handle, 0)
            except win32gui.error:
                self.actions.log('Process {0} seems already killed'.format(self.process))

        win32api.CloseHandle(process_wait_handle)

        return killed

    # Non PEP-8 aliases
    kill_ = deprecated(kill, deprecated_name='kill_')
    Kill_ = deprecated(kill, deprecated_name='Kill_')

    def is_process_running(self):
        """
        Checks that process is running.

        Can be called before start/connect.

        Returns True if process is running otherwise - False
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

AssertValidProcess = assert_valid_process  # just in case


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
    for process, name, cmdline in modules:
        if name is None:
            continue
        if module_path.lower() in name.lower():
            return process

    message = "Could not find any accessible process with a module of '{0}'".format(module)
    raise ProcessNotFoundError(message)
