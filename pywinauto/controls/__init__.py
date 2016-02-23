# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
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

"""Controls package"""

from ..sysinfo import UIA_support
if UIA_support:
    from . import UIAWrapper # register "uia" back-end (at the end of UIAWrapper module)

from .HwndWrapper import GetDialogPropsFromHandle
from .HwndWrapper import InvalidWindowHandle

# import the control classes - this will register the classes they
# contain
from . import common_controls
from . import win32_controls


from ..base_wrapper import InvalidElement
