# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2009 Mark Mc Mahon
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

"""Wraps various WPF windows controls
"""
from . import UIAWrapper
from ..UIAElementInfo import _UIA_dll



#====================================================================
class ButtonWrapper(UIAWrapper.UIAWrapper):
    "Wrap a WPF Button control"

    friendlyclassname = "Button"
    windowclasses = [
        "Button",
        ".*Button",
        r"WindowsForms\d*\.BUTTON\..*",
        ".*CheckBox", ]
    controltypes = [
            _UIA_dll.UIA_ButtonControlTypeId,
            _UIA_dll.UIA_CheckBoxControlTypeId,
            _UIA_dll.UIA_RadioButtonControlTypeId
            ]
    can_be_label = True

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ButtonWrapper, self).__init__(hwnd)

