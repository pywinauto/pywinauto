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

"""Provides functions for iterating and finding windows/elements"""
from __future__ import unicode_literals

import re
import sys
import six

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
class RenamedKeywordError(Exception):

    """Search keyword has been renamed"""
    pass


#=========================================================================
def find_element(**kwargs):
    """
    Call find_elements and ensure that only one element is returned

    Calls find_elements with exactly the same arguments as it is called with
    so please see :py:func:`find_elements` for the full parameters description.
    """
    elements = find_elements(**kwargs)

    if not elements:
        raise ElementNotFoundError(kwargs)

    if len(elements) > 1:
        exception = ElementAmbiguousError(
            "There are {0} elements that match the criteria {1}".format(
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
    so please see :py:func:`find_elements` for the full parameters description.
    """
    try:
        kwargs['backend'] = 'win32'
        element = find_element(**kwargs)
        return element.handle
    except ElementNotFoundError:
        raise WindowNotFoundError
    except ElementAmbiguousError:
        raise WindowAmbiguousError


def _raise_search_key_error(key, all_props):
    raise KeyError('Incorrect search keyword "{}". Availaible keywords: {}'.format(key, all_props))


#=========================================================================
def find_elements(**kwargs):
    backend = kwargs.pop('backend', None)
    parent = kwargs.pop('parent', None)
    handle = kwargs.pop('handle', None)
    ctrl_index = kwargs.pop('ctrl_index', None)
    top_level_only = kwargs.pop('top_level_only', True)
    # TODO: depth = 1, remove top_level_only?
    depth = kwargs.pop('depth', None)
    best_match = kwargs.pop('best_match', None)
    predicate_func = kwargs.pop('predicate_func', None)
    # TODO: eliminate found_index by find_all
    found_index = kwargs.pop('found_index', None)
    active_only = kwargs.pop('active_only', False)

    if backend is None:
        backend = registry.active_backend.name
    backend_obj = registry.backends[backend]

    if handle is not None:
        # TODO: uncomment later
        #if not kwargs:
        #    raise KeyError('Handle is already unique identifier, other keywords are redundant')
        # allow a handle to be passed in
        # if it is present - just return it
        return [backend_obj.element_info_class(handle), ]

    # tell user about new property name for every renamed one
    if hasattr(backend_obj.element_info_class, 'renamed_props'):
        renamed_erros = []
        for key, value in kwargs.items():
            renamed_prop = backend_obj.element_info_class.renamed_props.get(key, None)
            if renamed_prop is not None:
                new_key, values_map = renamed_prop
                if values_map and value in values_map.keys():
                    renamed_erros.append('"{}={}" -> "{}={}"'.format(key, value, new_key, values_map[value]))
                else:
                    renamed_erros.append('"{}" -> "{}"'.format(key, new_key))
        if renamed_erros:
            raise RenamedKeywordError('[pywinauto>=0.7.0] Some search keywords are renamed: ' + ', '.join(renamed_erros))

    re_props = backend_obj.element_info_class.re_props
    exact_only_props = backend_obj.element_info_class.exact_only_props
    all_props = re_props + exact_only_props
    for key, _ in kwargs.items():
        if key.endswith('_re') and key[:-3] not in re_props:
            _raise_search_key_error(key, all_props)
        if not key.endswith('_re') and key not in all_props:
            _raise_search_key_error(key, all_props)

    if isinstance(parent, backend_obj.generic_wrapper_class):
        parent = parent.element_info
    elif isinstance(parent, six.integer_types):
        # check if parent is a handle of element (in case of searching native controls)
        parent = backend_obj.element_info_class(parent)


    # create initial list of all elements
    if top_level_only:
        # find the top level elements
        element = backend_obj.element_info_class()
        # TODO: think about not passing **kwargs
        elements = element.children(class_name=kwargs.get('class_name'),
                                    name=kwargs.get('name'),
                                    control_type=kwargs.get('control_type'),
                                    process=kwargs.get('pid'),
                                    cache_enable=True)

        # if we have been given a parent
        if parent:
            elements = [elem for elem in elements if elem.parent == parent]

    # looking for child elements
    else:
        # if not given a parent look for all children of the desktop
        if not parent:
            parent = backend_obj.element_info_class()

        # look for ALL children of that parent
        # TODO: think about not passing **kwargs
        elements = parent.descendants(class_name=kwargs.get('class_name'),
                                      name=kwargs.get('name'),
                                      control_type=kwargs.get('control_type'),
                                      process=kwargs.get('pid'),
                                      cache_enable=True,
                                      depth=depth)

    # early stop
    if not elements:
        if found_index is not None:
            if found_index > 0:
                raise ElementNotFoundError("found_index is specified as {0}, but no windows found".format(
                    found_index))
        return elements

    # if the ctrl_index has been specified then just return
    # that control
    if ctrl_index is not None:
        return [elements[ctrl_index], ]


    for prop in backend_obj.element_info_class.search_order:
        exact_search_value = kwargs.get(prop)
        if prop in backend_obj.element_info_class.re_props:
            re_search_value = kwargs.get(prop + '_re')
            if exact_search_value is not None and \
                    re_search_value is not None:
                raise ValueError('Mutually exclusive keywords are used: "{}", "{}"'.format(prop, prop + '_re'))
            if re_search_value is not None:
                regex = re.compile(re_search_value)
                elements = [elem for elem in elements if regex.match(getattr(elem, prop))]
        if exact_search_value is not None:
            elements = [elem for elem in elements if exact_search_value == getattr(elem, prop)]

    if active_only:
        # TODO: re-write to use ElementInfo interface
        active_elem = backend_obj.element_info_class.get_active()

        elements = [elem for elem in elements if elem.handle == active_elem]

    if best_match is not None:
        # Build a list of wrapped controls.
        # Speed up the loop by setting up local pointers
        wrapped_elems = []
        add_to_wrp_elems = wrapped_elems.append
        wrp_cls = backend_obj.generic_wrapper_class
        for elem in elements:
            try:
                add_to_wrp_elems(wrp_cls(elem))
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
                elem.element_info.set_cache_strategy(cached=False)
                elements.append(elem.element_info)
            else:
                elements.append(backend_obj.element_info_class(elem.handle))
    else:
        for elem in elements:
            elem.set_cache_strategy(cached=False)

    if predicate_func is not None:
        elements = [elem for elem in elements if predicate_func(elem)]

    # TODO: add check for IndexError
    if found_index is not None:
        if found_index >= len(elements):
            return []
        elements = [elements[found_index]]

    return elements


#=========================================================================
'''
def find_elements(class_name=None,
                  class_name_re=None,
                  parent=None,
                  process=None,
                  name=None,
                  title_re=None,
                  top_level_only=True,
                  visible_only=True,
                  enabled_only=False,
                  best_match=None,
                  handle=None,
                  ctrl_index=None,
                  found_index=None,
                  predicate_func=None,
                  active_only=False,
                  control_id=None,
                  control_type=None,
                  auto_id=None,
                  framework_id=None,
                  backend=None,
                  depth=None
                  ):
    """
    Find elements based on criteria passed in

    WARNING! Direct usage of this function is not recommended! It's a very low level API.
    Better use Application and WindowSpecification objects described in the
    Getting Started Guide.

    Possible values are:

    * **class_name**     Elements with this window class
    * **class_name_re**  Elements whose class matches this regular expression
    * **parent**         Elements that are children of this
    * **process**        Elements running in this process
    * **title**          Elements with this text
    * **title_re**       Elements whose text matches this regular expression
    * **top_level_only** Top level elements only (default=**True**)
    * **visible_only**   Visible elements only (default=**True**)
    * **enabled_only**   Enabled elements only (default=False)
    * **best_match**     Elements with a title similar to this
    * **handle**         The handle of the element to return
    * **ctrl_index**     The index of the child element to return
    * **found_index**    The index of the filtered out child element to return
    * **predicate_func** A user provided hook for a custom element validation
    * **active_only**    Active elements only (default=False)
    * **control_id**     Elements with this control id
    * **control_type**   Elements with this control type (string; for UIAutomation elements)
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

    if isinstance(parent, backend_obj.generic_wrapper_class):
        parent = parent.element_info
    elif isinstance(parent, six.integer_types):
        # check if parent is a handle of element (in case of searching native controls)
        parent = backend_obj.element_info_class(parent)

    if top_level_only:
        # find the top level elements
        element = backend_obj.element_info_class()
        # vryabov: we don't use title=title below, because it fixes issue 779:
        # https://github.com/pywinauto/pywinauto/issues/779
        elements = element.children(process=process,
                                    class_name=class_name,
                                    name=title,
                                    control_type=control_type,
                                    cache_enable=True)

        # if we have been given a parent
        if parent:
            elements = [elem for elem in elements if elem.parent == parent]

    # looking for child elements
    else:
        # if not given a parent look for all children of the desktop
        if not parent:
            parent = backend_obj.element_info_class()

        # look for ALL children of that parent
        # vryabov: we don't use title=title below, because it fixes issue 779:
        # https://github.com/pywinauto/pywinauto/issues/779
        elements = parent.descendants(class_name=class_name,
                                      name=title,
                                      control_type=control_type,
                                      cache_enable=True,
                                      depth=depth)

        # if the ctrl_index has been specified then just return
        # that control
        if ctrl_index is not None:
            return [elements[ctrl_index], ]

    # early stop
    if not elements:
        if found_index is not None:
            if found_index > 0:
                raise ElementNotFoundError("found_index is specified as {0}, but no windows found".format(
                    found_index))
        return elements

    if framework_id is not None and elements:
        elements = [elem for elem in elements if elem.framework_id == framework_id]

    if control_id is not None and elements:
        elements = [elem for elem in elements if elem.control_id == control_id]

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

    if class_name is not None:
        elements = [elem for elem in elements if elem.class_name == class_name]

    if class_name_re is not None:
        class_name_regex = re.compile(class_name_re)
        elements = [elem for elem in elements if class_name_regex.match(elem.class_name)]

    if process is not None:
        elements = [elem for elem in elements if elem.process_id == process]

    if auto_id is not None and elements:
        elements = [elem for elem in elements if elem.automation_id == auto_id]

    if title is not None:
        # TODO: some magic is happenning here
        if elements:
            elements[0].rich_text
        elements = [elem for elem in elements if elem.rich_text == title]
    elif title_re is not None:
        title_regex = re.compile(title_re)

        def _title_match(w):
            """Match a window title to the regexp"""
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
        # Build a list of wrapped controls.
        # Speed up the loop by setting up local pointers
        wrapped_elems = []
        add_to_wrp_elems = wrapped_elems.append
        wrp_cls = backend_obj.generic_wrapper_class
        for elem in elements:
            try:
                add_to_wrp_elems(wrp_cls(elem))
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
                elem.element_info.set_cache_strategy(cached=False)
                elements.append(elem.element_info)
            else:
                elements.append(backend_obj.element_info_class(elem.handle))
    else:
        for elem in elements:
            elem.set_cache_strategy(cached=False)

    if predicate_func is not None:
        elements = [elem for elem in elements if predicate_func(elem)]

    # found_index is the last criterion to filter results
    if found_index is not None:
        if found_index < len(elements):
            elements = elements[found_index:found_index + 1]
        else:
            raise ElementNotFoundError("found_index is specified as {0}, but {1} window/s found".format(
                found_index, len(elements)))

    return elements
'''

#=========================================================================
def find_windows(**kwargs):
    """
    Find elements based on criteria passed in and return list of their handles

    Calls find_elements with exactly the same arguments as it is called with
    so please see :py:func:`find_elements` for the full parameters description.
    """
    try:
        kwargs['backend'] = 'win32'
        elements = find_elements(**kwargs)
        return [elem.handle for elem in elements]
    except ElementNotFoundError:
        raise WindowNotFoundError


#=========================================================================
def enum_windows():
    """(removed since 0.7.0) Return a list of handles of all the top level windows"""
    raise NotImplementedError("The function has been removed. " \
        "Use high level API instead or pin to version <=0.6.8.")
