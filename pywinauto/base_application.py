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

import sys
import os.path
import time
import locale
import codecs
import collections

import six

from . import timings
from . import controls
from . import findbestmatch
from . import findwindows

from .backend import registry

from .actionlogger import ActionLogger
from .timings import Timings, wait_until, TimeoutError, wait_until_passes
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


# TODO problem with if active_only: in findwindows to use on linux
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

    def __init__(self, search_criteria, allow_magic_lookup=True):
        """
        Initialize the class

        :param search_criteria: the criteria to match a dialog
        :param allow_magic_lookup: whether attribute access must turn into child_window(best_match=...) search as fallback
        """
        # kwargs will contain however to find this window
        if 'backend' not in search_criteria:
            search_criteria['backend'] = registry.active_backend.name
        if 'pid' in search_criteria and 'app' in search_criteria:
            raise KeyError('Keywords "pid" and "app" cannot be combined (ambiguous). ' \
                'Use one option at a time: Application object with keyword "app" or ' \
                'integer process ID with keyword "process".')
        self.app = search_criteria.get('app', None)
        self.criteria = [search_criteria, ]
        self.actions = ActionLogger()
        self.backend = registry.backends[search_criteria['backend']]
        self.allow_magic_lookup = allow_magic_lookup

        # Non PEP-8 aliases for partial backward compatibility
        self.wrapper_object = deprecated(self.find, deprecated_name='wrapper_object')
        self.child_window = deprecated(self.by, deprecated_name="child_window")
        self.window = deprecated(self.by, deprecated_name='window')

    def __call__(self, *args, **kwargs):
        """No __call__ so return a useful error"""
        if "best_match" in self.criteria[-1]:
            raise AttributeError("Neither GUI element (wrapper) " \
                "nor wrapper method '{0}' were found (typo?)".
                format(self.criteria[-1]['best_match']))

        message = (
            "You tried to execute a function call on a WindowSpecification "
            "instance. You probably have a typo for one of the methods of "
            "this class or of the targeted wrapper object.\n"
            "The criteria leading up to this are: " + str(self.criteria))

        raise AttributeError(message)

    def __get_ctrl(self, criteria_):
        """Get a control based on the various criteria"""
        # make a copy of the criteria
        criteria = [crit.copy() for crit in criteria_]
        # find the dialog
        if 'backend' not in criteria[0]:
            criteria[0]['backend'] = self.backend.name
        if self.app is not None:
            # find_elements(...) accepts only "process" argument
            criteria[0]['pid'] = self.app.process
            del criteria[0]['app']
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
                    ctrl_criteria["parent"] = ctrl_criteria["parent"].find()

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

    def find(self):
        """Allow the calling code to get the HwndWrapper object"""
        ctrls = self.__resolve_control(self.criteria)
        return ctrls[-1]

    def by(self, **criteria):
        """
        Add criteria for a control

        When this window specification is resolved it will be used
        to match against a control.
        """
        # default to non top level windows because we are usualy
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

            ctrls = self.__resolve_control(self.criteria)

            try:
                return getattr(ctrls[-1], attr_name)
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
            criterion['enabled'] = None
            criterion['visible'] = None

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
        return self.find()

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
        this_ctrl = self.__resolve_control(self.criteria)[-1]

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
                    ctrl_text = ctrl_text.replace('\n', r'\n').replace('\r', r'\r')
                output += indent + u"{class_name} - '{text}'    {rect}" \
                                   "".format(class_name=ctrl.friendly_class_name(),
                                             text=ctrl_text,
                                             rect=ctrl.rectangle())

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
                    criteria_texts.append(u'name="{}"'.format(ctrl_text))
                if class_name:
                    criteria_texts.append(u'class_name="{}"'.format(class_name))
                if auto_id:
                    criteria_texts.append(u'auto_id="{}"'.format(auto_id))
                if control_type:
                    criteria_texts.append(u'control_type="{}"'.format(control_type))
                if ctrl_text or class_name or auto_id:
                    output += u'\n' + indent + u'child_window(' + u', '.join(criteria_texts) + u')'
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
            print_identifiers(elements_tree)
        else:
            with codecs.open(filename, "w", locale.getpreferredencoding()) as log_file:
                def log_func(msg):
                    log_file.write(str(msg) + os.linesep)
                print_identifiers(elements_tree, log_func=log_func)

    print_control_identifiers = deprecated(dump_tree, deprecated_name='print_control_identifiers')
    print_ctrl_ids = deprecated(dump_tree, deprecated_name='print_ctrl_ids')


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
