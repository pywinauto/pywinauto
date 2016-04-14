# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2010 Mark Mc Mahon
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

"""Provides functions for iterating and finding windows/elements

"""
from __future__ import unicode_literals

import re
import ctypes

from . import six
from . import win32functions
from . import win32structures
from . import findbestmatch
from . import controls
from .backend import registry


# TODO: we should filter out invalid elements before returning

#=========================================================================
class WindowNotFoundError(Exception):

    """No window could be found"""
    pass


#=========================================================================
class WindowAmbiguousError(Exception):

    """There was more then one window that matched"""
    pass

#=========================================================================
class ElementNotFoundError(Exception):

    """No element could be found"""
    pass

#=========================================================================
class ElementAmbiguousError(Exception):

    """There was more then one element that matched"""
    pass

#=========================================================================
def find_element(**kwargs):
    """
    Call find_elements and ensure that only one element is returned

    Calls find_elements with exactly the same arguments as it is called with
    so please see find_elements for a description of them.
    """
    elements = find_elements(**kwargs)

    if not elements:
        raise ElementNotFoundError(kwargs)

    if len(elements) > 1:
        exception =  ElementAmbiguousError(
            "There are %d elements that match the criteria %s"% (
            len(elements),
            six.text_type(kwargs),
            )
        )

        exception.elements = elements
        raise exception

    return elements[0]

#=========================================================================
def find_window(**kwargs):
    """
    Call find_elements and ensure that only handle of one element is returned

    Calls find_elements with exactly the same arguments as it is called with
    so please see find_elements for a description of them.
    """
    try:
        kwargs['backend'] = 'native'
        element = find_element(**kwargs)
        return element.handle
    except ElementNotFoundError:
        raise WindowNotFoundError
    except ElementAmbiguousError:
        raise WindowAmbiguousError

#=========================================================================
def find_elements(class_name = None,
                  class_name_re = None,
                  parent = None,
                  process = None,
                  title = None,
                  title_re = None,
                  top_level_only = True,
                  visible_only = True,
                  enabled_only = False,
                  best_match = None,
                  handle = None,
                  ctrl_index = None,
                  found_index = None,
                  predicate_func = None,
                  active_only = False,
                  control_id = None,
                  auto_id = None,
                  framework_id = None,
                  backend = None,
    ):
    """
    Find elements based on criteria passed in

    Possible values are:

    * **class_name**     Elements with this window class
    * **class_name_re**  Elements whose class match this regular expression
    * **parent**         Elements that are children of this
    * **process**        Elements running in this process
    * **title**          Elements with this text
    * **title_re**       Elements whose text match this regular expression
    * **top_level_only** Top level elements only (default=True)
    * **visible_only**   Visible elements only (default=True)
    * **enabled_only**   Enabled elements only (default=False)
    * **best_match**     Elements with a title similar to this
    * **handle**         The handle of the element to return
    * **ctrl_index**     The index of the child element to return
    * **found_index**    The index of the filtered out child element to return
    * **active_only**    Active elements only (default=False)
    * **control_id**     Elements with this control id
    * **auto_id**        Elements with this automation id (for UIAutomation elements)
    * **framework_id**   Elements with this framework id (for UIAutomation elements)
    * **backend**        Back-end name to use while searching (default=None means current active backend)
    """

    if backend is None:
        backend = registry.active_backend.name
    backend_obj = registry.backends[backend]

    # allow a handle to be passed in
    # if it is present - just return it
    if handle is not None:
        return [backend_obj.element_info_class(handle), ]

    # check if parent is a handle of element (in case of searching native controls)
    if parent and isinstance(parent, six.integer_types):
        parent = backend_obj.element_info_class(parent)

    if top_level_only:
        # find the top level elements
        element = backend_obj.element_info_class()
        elements = element.children(process = process, 
                                    class_name = class_name, 
                                    title = title) # root.children == enum_windows()

        # if we have been given a parent
        if parent:
            elements = [elem for elem in elements if elem.parent == parent]

    # looking for child elements
    else:
        # if not given a parent look for all children of the desktop
        if not parent:
            parent = backend_obj.element_info_class()

        # look for ALL children of that parent
        elements = parent.descendants(process = process, 
                                      class_name = class_name, 
                                      title = title) # root.children == enum_windows()

        # if the ctrl_index has been specified then just return
        # that control
        if ctrl_index is not None:
            return [elements[ctrl_index], ]

    if framework_id is not None and elements:
        elements = [elem for elem in elements if elem.framework_id == framework_id]

    if control_id is not None and elements:
        elements = [elem for elem in elements if elem.control_id == control_id]

    if auto_id is not None and elements:
        elements = [elem for elem in elements if elem.automation_id == auto_id]

    if active_only:
        # TODO: re-write to use ElementInfo interface
        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)

        # get all the active elements (not just the specified process)
        ret = win32functions.GetGUIThreadInfo(0, ctypes.byref(gui_info))

        if not ret:
            raise ctypes.WinError()

        found_active = False
        for elem in elements:
            if elem.handle == gui_info.hwndActive:
                found_active = True
                elements = [elem, ]
                break
        if not found_active:
            elements = []

    # early stop
    if not elements:
        return elements

    if class_name is not None:
        elements = [elem for elem in elements if elem.class_name == class_name]

    if class_name_re is not None:
        class_name_regex = re.compile(class_name_re)
        elements = [elem for elem in elements if class_name_regex.match(elem.class_name)]

    if process is not None:
        elements = [elem for elem in elements if elem.process_id == process]

    if title is not None:
        # TODO: some magic is happenning here
        if elements:
            elements[0].rich_text
        elements = [elem for elem in elements if elem.rich_text == title]
    elif title_re is not None:
        title_regex = re.compile(title_re)
        def _title_match(w):
            t = w.rich_text
            if t is not None:
                return title_regex.match(t)
            return False
        elements = [elem for elem in elements if _title_match(elem)]

    if visible_only:
        elements = [elem for elem in elements if elem.visible]

    if enabled_only:
        elements = [elem for elem in elements if elem.enabled]

    if best_match is not None:
        wrapped_elems = []
        for elem in elements:
            elem.set_cache_strategy(True)
            try:
                wrapped_elems.append(backend_obj.generic_wrapper_class(elem))
                #wrapped_elems.append(BaseWrapper(elem))
            except (controls.InvalidWindowHandle,
                    controls.InvalidElement):
                # skip invalid handles - they have dissapeared
                # since the list of elements was retrieved
                continue
        elements = findbestmatch.find_best_control_matches(best_match, wrapped_elems)

        # convert found elements back to ElementInfo
        backup_elements = elements[:]
        elements = []
        for elem in backup_elements:
            if hasattr(elem, "element_info"):
                elem.element_info.set_cache_strategy(False)
                elements.append(elem.element_info)
            else:
                elements.append(backend_obj.element_info_class(elem.handle))

    if predicate_func is not None:
        elements = [elem for elem in elements if predicate_func(elem)]

    # found_index is the last criterion to filter results
    if found_index is not None:
        if found_index < len(elements):
            elements = elements[found_index:found_index + 1]
        else:
            raise ElementNotFoundError("found_index is specified as {0}, but {1} window/s found".\
                format(found_index, len(elements)))

    return elements

#=========================================================================
def find_windows(**kwargs):
    """
    Find elements based on criteria passed in and return list of their handles

    Calls find_elements with exactly the same arguments as it is called with
    so please see find_elements for a description of them.
    """
    try:
        kwargs['backend'] = 'native'
        elements = find_elements(**kwargs)
        return [elem.handle for elem in elements]
    except ElementNotFoundError:
        raise WindowNotFoundError

#=========================================================================
def enum_windows():
    "Return a list of handles of all the top level windows"
    windows = []

    # The callback function that will be called for each HWND
    # all we do is append the wrapped handle
    def enum_window_proc(hwnd, lparam):
        "Called for each window - adds handles to a list"
        windows.append(hwnd)
        return True

    # define the type of the child procedure
    enum_win_proc_t = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_long, ctypes.c_long)

    # 'construct' the callback with our function
    proc = enum_win_proc_t(enum_window_proc)

    # loop over all the children (callback called for each)
    win32functions.EnumWindows(proc, 0)

    # return the collected wrapped windows
    return windows
