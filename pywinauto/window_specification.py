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

"""Provides a object for finding a window or control"""

from __future__ import print_function

import sys
import os.path
import locale
import codecs
import collections
import warnings

import six

from . import controls
from . import findbestmatch
from . import findwindows

from . import backend as backends

from .actionlogger import ActionLogger
from .timings import Timings, wait_until, TimeoutError, wait_until_passes, timestamp
from . import deprecated


class WindowSpecification(object):

    """
    A specification for finding a window or control

    Windows are resolved when used.
    You can also wait for existance or non existance of a window

    .. implicitly document some private functions
    .. automethod:: __getattribute__
    .. automethod:: __getitem__
    """
    WAIT_CRITERIA_MAP = {
        'visible': lambda ctrl, timeout, retry_interval: ctrl.wait_visible(timeout, retry_interval),
        'enabled': lambda ctrl, timeout, retry_interval: ctrl.wait_enabled(timeout, retry_interval),
        'active': lambda ctrl, timeout, retry_interval: ctrl.wait_active(timeout, retry_interval),
    }

    WAIT_NOT_CRITERIA_MAP = {
        'visible': lambda ctrl, timeout, retry_interval: ctrl.wait_not_visible(timeout, retry_interval),
        'enabled': lambda ctrl, timeout, retry_interval: ctrl.wait_not_enabled(timeout, retry_interval),
        'active': lambda ctrl, timeout, retry_interval: ctrl.wait_not_active(timeout, retry_interval),
    }

    def __init__(self, search_criteria, allow_magic_lookup=True):
        """
        Initialize the class

        :param search_criteria: the criteria to match a dialog
        :param allow_magic_lookup: whether attribute access must turn into child_window(best_match=...) search as fallback
        """
        # kwargs will contain however to find this window
        if 'backend' not in search_criteria:
            search_criteria['backend'] = backends.registry.active_backend.name
        if 'pid' in search_criteria and 'app' in search_criteria:
            raise KeyError(
                'Keywords "pid" and "app" cannot be combined (ambiguous). '
                'Use one option at a time: Application object with keyword "app" or '
                'integer process ID with keyword "process".'
            )
        self.app = search_criteria.get('app', None)
        self.criteria = [search_criteria, ]
        self.actions = ActionLogger()
        self.backend = backends.registry.backends[search_criteria['backend']]
        self.allow_magic_lookup = allow_magic_lookup

        # Non PEP-8 aliases for partial backward compatibility
        self.wrapper_object = deprecated(self.find, deprecated_name='wrapper_object')
        self.child_window = deprecated(self.by, deprecated_name="child_window")
        self.window = deprecated(self.by, deprecated_name='window')

    def __call__(self, *args, **kwargs):
        """No __call__ so return a useful error"""
        if "best_match" in self.criteria[-1]:
            raise AttributeError(
                "Neither GUI element (wrapper) "
                "nor wrapper method '{0}' were found (typo?)".
                format(self.criteria[-1]['best_match'])
            )

        message = (
            "You tried to execute a function call on a WindowSpecification "
            "instance. You probably have a typo for one of the methods of "
            "this class or of the targeted wrapper object.\n"
            "The criteria leading up to this are: " + str(self.criteria))

        raise AttributeError(message)

    def _get_updated_criteria(self, criteria_):
        # make a copy of the criteria
        criteria = [crit.copy() for crit in criteria_]
        # find the dialog
        if 'backend' not in criteria[0]:
            criteria[0]['backend'] = self.backend.name
        if self.app is not None:
            # find_elements(...) accepts only "process" argument
            criteria[0]['pid'] = self.app.process
            del criteria[0]['app']
        return criteria

    def __find_base(self, criteria_, timeout, retry_interval):
        time_left = timeout
        start = timestamp()
        criteria = self._get_updated_criteria(criteria_)
        dialog = self.backend.generic_wrapper_class(findwindows.find_element(**criteria[0]))
        if len(criteria) > 1:
            ctrls = []
            previous_parent = dialog.element_info
            for ctrl_criteria in criteria[1:]:
                ctrl_criteria["top_level_only"] = False
                if "parent" not in ctrl_criteria:
                    ctrl_criteria["parent"] = previous_parent

                if isinstance(ctrl_criteria["parent"], WindowSpecification):
                    time_left -= timestamp() - start
                    if time_left <= 0.0:
                        raise TimeoutError("Timed out: can not find parent {} for the control with the given"
                                           "criteria {}.".format(ctrl_criteria['parent'], ctrl_criteria))
                    ctrl_criteria["parent"] = ctrl_criteria["parent"].find(time_left, retry_interval)

                # resolve the control and return it
                if 'backend' not in ctrl_criteria:
                    ctrl_criteria['backend'] = self.backend.name

                ctrl = self.backend.generic_wrapper_class(findwindows.find_element(**ctrl_criteria))
                previous_parent = ctrl.element_info
                ctrls.append(ctrl)
            return ctrls[-1]
        else:
            return dialog

    def __find_all_base(self, criteria_, timeout, retry_interval):
        time_left = timeout
        start = timestamp()

        if len(criteria_) == 1:
            criteria = self._get_updated_criteria(criteria_)
            dialogs = findwindows.find_elements(**criteria[0])
            return [self.backend.generic_wrapper_class(dialog) for dialog in dialogs]

        else:
            previous_ctrl = self.__find_base(criteria_[:-1], time_left, retry_interval)
            previous_parent = previous_ctrl.element_info
            ctrl_criteria = criteria_[-1]
            ctrl_criteria["top_level_only"] = False
            if "parent" not in ctrl_criteria:
                ctrl_criteria["parent"] = previous_parent

            if isinstance(ctrl_criteria["parent"], WindowSpecification):
                time_left -= timestamp() - start
                if time_left <= 0.0:
                    raise TimeoutError("Timed out: can not find parent {} for the control with the given"
                                       "criteria {}.".format(ctrl_criteria['parent'], ctrl_criteria))
                ctrl_criteria["parent"] = ctrl_criteria["parent"].find(time_left, retry_interval)

            # resolve the controls and return it
            if 'backend' not in ctrl_criteria:
                ctrl_criteria['backend'] = self.backend.name

            all_ctrls = findwindows.find_elements(**ctrl_criteria)
            return [self.backend.generic_wrapper_class(ctrl) for ctrl in all_ctrls]

    def find(self, timeout=None, retry_interval=None):
        """
        Find a control using criteria. The returned control matches conditions from criteria[-1].

        * **criteria** - a list with dictionaries

             1st element is search criteria for the dialog

             other elements are search criteria for a control of the dialog

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
                self.__find_base,
                (
                    findwindows.ElementNotFoundError,
                    findbestmatch.MatchError,
                    controls.InvalidWindowHandle,
                    controls.InvalidElement,
                ),
                self.criteria,
                timeout,
                retry_interval,
            )
        except TimeoutError as e:
            raise e.original_exception

        return ctrl

    def find_all(self, timeout=None, retry_interval=None):
        """
        Find all controls using criteria. The returned controls match conditions from criteria[-1].
        Parent controls are assumed to exist in a single instance. Otherwise it will result in an ElementAmbiguousError.

        * **criteria** - a list with dictionaries

             1st element is search criteria for the dialog

             other elements are search criteria for a control of the dialog

        * **timeout** -  maximum length of time to try to find the controls (default 5)
        * **retry_interval** - how long to wait between each retry (default .09)
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            ctrls = wait_until_passes(
                timeout,
                retry_interval,
                self.__find_all_base,
                (
                    findwindows.ElementNotFoundError,
                    findbestmatch.MatchError,
                    controls.InvalidWindowHandle,
                    controls.InvalidElement
                ),
                self.criteria,
                timeout,
                retry_interval,
            )
        except TimeoutError as e:
            raise e.original_exception

        return ctrls

    def wait(self, wait_for, timeout=None, retry_interval=None):
        """
        (DEPRECATED) Wait for the window to be in a particular state/states.
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

        warnings.warn("Wait method is deprecated and will be removed. "
                      "Please, use find() instead of wait() or wait('exists'). "
                      "wait_visible(), wait_enabled() and wait_active() are methods of "
                      "HwndWrapper object, so you can use it like .find().wait_active(), "
                      ".find().wait_visible().wait_enabled(), etc.")

        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        time_left = timeout
        start = timestamp()
        try:
            ctrl = self.find(time_left, retry_interval)
        except (
            findwindows.ElementNotFoundError,
            findbestmatch.MatchError,
            controls.InvalidWindowHandle,
            controls.InvalidElement,
            TimeoutError
        ):
            raise TimeoutError('Timed out: can not find control with the given criteria {}'.format(self.criteria[-1]))

        correct_wait_for = wait_for.lower().split()
        if 'ready' in correct_wait_for:
            correct_wait_for.remove('ready')
            if 'visible' not in correct_wait_for:
                correct_wait_for.append('visible')
            if 'enabled' not in correct_wait_for:
                correct_wait_for.append('enabled')

        for condition in correct_wait_for:
            time_left -= timestamp() - start
            if time_left <= 0.0:
                raise TimeoutError("Timed out: not enough time to check the condition {}.".format(condition))
            if condition == 'exists':
                continue
            elif condition not in WindowSpecification.WAIT_CRITERIA_MAP.keys():
                raise SyntaxError("Invalid criteria: {}!".format(condition))
            else:
                WindowSpecification.WAIT_CRITERIA_MAP[condition](ctrl, time_left, retry_interval)

        return ctrl

    def wait_not(self, wait_for, timeout=None, retry_interval=None):
        """
        (DEPRECATED)Wait for the window to not be in a particular state/states.
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

        warnings.warn("Wait_not method is deprecated and will be removed. "
                      "You can use not_exists() instead of wait_not('exists'). "
                      "wait_not_visible(), wait_not_enabled() and wait_not_active() are methods of "
                      "HwndWrapper object, so you can use it like .find().wait_not_active(), "
                      ".find().wait_not_visible().wait_not_enabled(), etc.")

        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        correct_wait_for = wait_for.lower().split()

        if 'ready' in correct_wait_for:
            correct_wait_for.remove('ready')
            if 'visible' not in correct_wait_for:
                correct_wait_for.append('visible')
            if 'enabled' not in correct_wait_for:
                correct_wait_for.append('enabled')

        if 'exists' in correct_wait_for:
            if not self.not_exists(timeout, retry_interval):
                raise TimeoutError("Object with the given criteria {} still exists".format(self.criteria[-1]))
        else:
            time_left = timeout
            start = timestamp()
            try:
                ctrl = self.find(time_left, retry_interval)
            except (
                findwindows.ElementNotFoundError,
                findbestmatch.MatchError,
                controls.InvalidWindowHandle,
                controls.InvalidElement,
                TimeoutError,
            ):
                return
            for condition in correct_wait_for:
                time_left -= timestamp() - start
                if time_left <= 0.0:
                    raise TimeoutError('Timed out: not enough time to check the condition {}'.format(condition))
                if condition not in WindowSpecification.WAIT_NOT_CRITERIA_MAP.keys():
                    raise SyntaxError("Invalid criteria: {}!".format(condition))
                else:
                    WindowSpecification.WAIT_NOT_CRITERIA_MAP[condition](ctrl, time_left, retry_interval)

    def by(self, **criteria):
        """
        Add criteria for a control

        When this window specification is resolved it will be used
        to match against a control.
        """
        # default to non top level windows because we are usually
        # looking for a control
        if 'top_level_only' not in criteria:
            criteria['top_level_only'] = False

        new_item = WindowSpecification(self.criteria[0], allow_magic_lookup=self.allow_magic_lookup)
        new_item.criteria.extend(self.criteria[1:])
        new_item.criteria.append(criteria)

        return new_item

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
        if len(self.criteria) >= 2:  # FIXME - this is surprising

            ctrl = self.find()

            # try to return a good error message if the control does not
            # have a __getitem__() method)
            if hasattr(ctrl, '__getitem__'):
                return ctrl[key]
            else:
                message = (
                    "The control does not have a __getitem__ method "
                    "for item access (i.e. ctrl[key]) so maybe you have "
                    "requested this in error?"
                )

                raise AttributeError(message)

        # if we get here then we must have only had one criteria so far
        # so create a new :class:`WindowSpecification` for this control
        new_item = WindowSpecification(self.criteria[0], allow_magic_lookup=self.allow_magic_lookup)

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
        allow_magic_lookup = object.__getattribute__(self, "allow_magic_lookup")  # Beware of recursions here!
        if not allow_magic_lookup:
            try:
                return object.__getattribute__(self, attr_name)
            except AttributeError:
                wrapper_object = self.find()
                try:
                    return getattr(wrapper_object, attr_name)
                except AttributeError:
                    message = (
                        'Attribute "%s" exists neither on %s object nor on'
                        'targeted %s element wrapper (typo? or set allow_magic_lookup to True?)' %
                        (attr_name, self.__class__, wrapper_object.__class__))
                    raise AttributeError(message)

        if attr_name in ['__dict__', '__members__', '__methods__', '__class__', '__name__']:
            return object.__getattribute__(self, attr_name)

        if attr_name in dir(self.__class__):
            return object.__getattribute__(self, attr_name)

        if attr_name in self.__dict__:
            return self.__dict__[attr_name]

        # if we already have 2 levels of criteria (dlg, control)
        # this third must be an attribute so resolve and get the
        # attribute and return it
        if len(self.criteria) >= 2:  # FIXME - this is surprising

            ctrl = self.find()

            try:
                return getattr(ctrl, attr_name)
            except AttributeError:
                return self.by(best_match=attr_name)
        else:
            # FIXME - I don't get this part at all, why is it win32-specific and why not keep the same logic as above?
            # if we have been asked for an attribute of the dialog
            # then resolve the window and return the attribute
            desktop_wrapper = self.backend.generic_wrapper_class(self.backend.element_info_class())
            need_to_resolve = (len(self.criteria) == 1 and hasattr(desktop_wrapper, attr_name))
            if hasattr(self.backend, 'dialog_class'):
                need_to_resolve = need_to_resolve and hasattr(self.backend.dialog_class, attr_name)
            # Probably there is no DialogWrapper for another backend

            if need_to_resolve:
                ctrl = self.find()
                return getattr(ctrl, attr_name)

        # It is a dialog/control criterion so let getitem
        # deal with it
        return self[attr_name]

    def exists(self, timeout=None, retry_interval=None):
        """
        Wait for the window exists, return True if the control exists.

        :param timeout: how much time (in seconds) to try to find the control.
            Default: ``Timings.exists_timeout``.

        :param retry_interval: how long to wait between each retry.
            Default: ``Timings.exists_retry``.
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
            criterion['enabled'] = None
            criterion['visible'] = None

        try:
            self.find(timeout, retry_interval)

            return True
        except (
            findwindows.ElementNotFoundError,
            findbestmatch.MatchError,
            controls.InvalidWindowHandle,
            controls.InvalidElement,
            TimeoutError,
        ):
            return False

    def not_exists(self, timeout=None, retry_interval=None):
        """
        Wait for the window does not exist, return True if the control does not exist.

        :param timeout: how much time (in seconds) to wait until the control exists.
            Default: ``Timings.exists_timeout``.

        :param retry_interval: how long to wait between each retry.
            Default: ``Timings.exists_retry``.
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
            criterion['enabled'] = None
            criterion['visible'] = None

        try:
            wait_until(timeout, retry_interval, self.exists, False)

            return True
        except (
            findwindows.ElementNotFoundError,
            findbestmatch.MatchError,
            controls.InvalidWindowHandle,
            controls.InvalidElement,
            TimeoutError
        ):
            return False

    def dump_tree(self, depth=10, max_width=10, filename=None):
        """
        Dump the 'identifiers' to console or a file

        Dump identifiers for the control and for its descendants to
        a depth of **depth** (the whole subtree if **None**).

        :param depth: Max depth level of an element tree to dump (None: unlimited).

        :param max_width: Max number of children of each element to dump (None: unlimited).

        :param filename: Save tree to a specified file (None: print to stdout).

        .. note:: The identifiers dumped by this method have been made
               unique. So if you have 2 edit boxes, they won't both have "Edit"
               listed in their identifiers. In fact the first one can be
               referred to as "Edit", "Edit0", "Edit1" and the 2nd should be
               referred to as "Edit2".
        """
        if depth is None:
            depth = sys.maxsize
        if max_width is None:
            max_width = sys.maxsize
        # Wrap this control
        this_ctrl = self.find()

        ElementTreeNode = collections.namedtuple('ElementTreeNode', ['elem', 'id', 'children'])

        def create_element_tree(element_list):
            """Build elements tree and create list with pre-order tree traversal"""
            depth_limit_reached = False
            width_limit_reached = False
            current_id = 0
            elem_stack = collections.deque([(this_ctrl, None, 0)])
            root_node = ElementTreeNode(this_ctrl, current_id, [])
            while elem_stack:
                current_elem, current_elem_parent_children, current_node_depth = elem_stack.pop()
                if current_elem is None:
                    elem_node = ElementTreeNode(None, current_id, [])
                    current_elem_parent_children.append(elem_node)
                else:
                    if current_node_depth <= depth:
                        if current_elem_parent_children is not None:
                            current_id += 1
                            elem_node = ElementTreeNode(current_elem, current_id, [])
                            current_elem_parent_children.append(elem_node)
                            element_list.append(current_elem)
                        else:
                            elem_node = root_node
                        child_elements = current_elem.children()
                        if len(child_elements) > max_width and current_node_depth < depth:
                            elem_stack.append((None, elem_node.children, current_node_depth + 1))
                            width_limit_reached = True
                        for i in range(min(len(child_elements) - 1, max_width - 1), -1, -1):
                            elem_stack.append((child_elements[i], elem_node.children, current_node_depth + 1))
                    else:
                        depth_limit_reached = True
            return root_node, depth_limit_reached, width_limit_reached

        # Create a list of this control, all its descendants
        all_ctrls = [this_ctrl]

        # Build element tree
        elements_tree, depth_limit_reached, width_limit_reached = create_element_tree(all_ctrls)

        show_best_match_names = self.allow_magic_lookup and not (depth_limit_reached or width_limit_reached)
        if show_best_match_names:
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

        def print_identifiers(element_node, current_depth=0, log_func=print):
            """Recursively print ids for ctrls and their descendants in a tree-like format"""
            if current_depth == 0:
                if depth_limit_reached:
                    log_func('Warning: the whole hierarchy does not fit into depth={}. '
                             'Increase depth parameter value or set it to None (unlimited, '
                             'may freeze in case of very large number of elements).'.format(depth))
                if self.allow_magic_lookup and not show_best_match_names:
                    log_func('If the whole hierarchy fits into depth and max_width values, '
                             'best_match names are dumped.')
                log_func("Control Identifiers:")

            indent = current_depth * u"   | "
            output = indent + u'\n'

            ctrl = element_node.elem
            if ctrl is not None:
                ctrl_id = element_node.id
                ctrl_text = ctrl.window_text()
                if ctrl_text:
                    # transform multi-line text to one liner
                    ctrl_text = repr(ctrl_text)
                output += indent + u"{class_name} - {text}    {rect}".format(
                    class_name=ctrl.friendly_class_name(),
                    text=ctrl_text,
                    rect=ctrl.rectangle()
                )

                if show_best_match_names:
                    output += u'\n' + indent + u'{}'.format(ctrl_id_name_map[ctrl_id])

                class_name = ctrl.class_name()
                auto_id = None
                control_type = None
                if hasattr(ctrl.element_info, 'automation_id'):
                    auto_id = ctrl.element_info.automation_id
                if hasattr(ctrl.element_info, 'control_type'):
                    control_type = ctrl.element_info.control_type
                criteria_texts = []
                if ctrl_text:
                    criteria_texts.append(u'name={}'.format(ctrl_text))
                if class_name:
                    criteria_texts.append(u"class_name='{}'".format(class_name))
                if auto_id:
                    criteria_texts.append(u"auto_id='{}'".format(auto_id))
                if control_type:
                    criteria_texts.append(u"control_type='{}'".format(control_type))
                if ctrl_text or class_name or auto_id:
                    output += u'\n' + indent + u'.by(' + u', '.join(criteria_texts) + u')'
            else:
                output += indent + u'**********\n'
                output += indent + u'Max children output limit ({}) has been reached. ' \
                                   u'Set a larger max_width value or use max_width=None ' \
                                   u'to see all children.\n'.format(max_width)
                output += indent + u'**********'

            if six.PY3:
                log_func(output)
            else:
                log_func(output.encode(locale.getpreferredencoding(), errors='backslashreplace'))

            if current_depth <= depth:
                for child_elem in element_node.children:
                    print_identifiers(child_elem, current_depth + 1, log_func)

        if filename is None:
            if six.PY3:
                try:
                    encoding = sys.stdout.encoding
                except AttributeError:
                    encoding = sys.getdefaultencoding()
            else:
                encoding = locale.getpreferredencoding()
            print(u'# -*- coding: {} -*-'.format(encoding))
            print_identifiers(elements_tree)
        else:
            with codecs.open(filename, "w", locale.getpreferredencoding(), errors="backslashreplace") as log_file:
                def log_func(msg):
                    log_file.write(str(msg) + os.linesep)
                log_func(u'# -*- coding: {} -*-'.format(locale.getpreferredencoding()))
                print_identifiers(elements_tree, log_func=log_func)

    print_control_identifiers = deprecated(dump_tree, deprecated_name='print_control_identifiers')
    print_ctrl_ids = deprecated(dump_tree, deprecated_name='print_ctrl_ids')


#=========================================================================
