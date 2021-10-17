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
import six

from . import findbestmatch
from . import WindowNotFoundError
from . import controls
from .backend import registry


# TODO: we should filter out invalid elements before returning


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
    elif parent and not isinstance(parent, backend_obj.element_info_class):
        raise TypeError('Parent must be {}, {}, integer or None'.format(backend_obj.generic_wrapper_class,
                                                                        backend_obj.element_info_class))

    # create initial list of all elements
    if top_level_only:
        # find the top level elements
        element = backend_obj.element_info_class()
        # TODO: think about not passing **kwargs
        elements = element.children(class_name=kwargs.get('class_name'),
                                    control_type=kwargs.get('control_type'),
                                    process=kwargs.get('pid'),
                                    cache_enable=False)

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
                                      control_type=kwargs.get('control_type'),
                                      process=kwargs.get('pid'),
                                      cache_enable=False,
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

    if found_index is not None:
        if found_index >= len(elements):
            return []
        elements = [elements[found_index]]

    return elements


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
