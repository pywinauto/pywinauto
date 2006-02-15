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

"Collect the wrapping classes and respond to request to wrap handles"

import re

import win32_controls
import common_controls
from pywinauto import handleprops

__revision__ = "$Revision $"

#====================================================================
# get all the classes/functinos from win32_contols
_all_classes = win32_controls.__dict__.values()

# and add all the classes/functinos from common_controls
_all_classes.extend(common_controls.__dict__.values())

_wrapper_info = {}

for item in _all_classes:
    try:
        for classname_ in item.windowclasses:
            # set the info
            _wrapper_info[classname_] = (
                re.compile(classname_),
                item)

    except AttributeError, e:
        pass

def _find_wrapper(classname):
    """return the wrapper that handles this classname

    If there is no match found then return None.
    """

    # Optimization - check if the control name matches exactly
    # before trying a re.match
    if classname in _wrapper_info:
        return _wrapper_info[classname][1]

    for regex, wrapper in _wrapper_info.values():
        if regex.match(classname):
            #print wrapper_name
            return wrapper



#====================================================================
def WrapHandle(hwnd):
    """Return the hwnd wrapped with  the correct wraper

    Wrapper is chosen on the Class of the control
    """

    from HwndWrapper import HwndWrapper

    class_name = handleprops.classname(hwnd)
    wrapper = _find_wrapper(class_name)

    if wrapper is None:
        if handleprops.is_toplevel_window(hwnd):
            wrapped_hwnd = win32_controls.DialogWrapper(hwnd)
        else:
            wrapped_hwnd = HwndWrapper(hwnd)

        if not handleprops.is_toplevel_window(hwnd):
            wrapped_hwnd._NeedsImageProp = True

    else:
        wrapped_hwnd = wrapper(hwnd)

    return wrapped_hwnd

