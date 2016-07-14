# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2012 Michael Herrmann
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

"""
Python package for automating GUI manipulation on Windows

"""

__version__ = "0.5.4"

from . import findwindows
WindowAmbiguousError = findwindows.WindowAmbiguousError
ElementNotFoundError = findwindows.ElementNotFoundError

from .sysinfo import UIA_support
if UIA_support:
    ElementNotFoundError = findwindows.ElementNotFoundError
    ElementAmbiguousError = findwindows.ElementAmbiguousError

from . import findbestmatch
from . import backend as backends
MatchError = findbestmatch.MatchError

from .application import Application, WindowSpecification


class Desktop(object):

    """Simple class to call something like ``Desktop().WindowName.ControlName.method()``"""

    def __init__(self, backend=None):
        """Create desktop element description"""
        if backend:
            self.backend = backend
        else:
            self.backend = backends.registry.name

    def window(self, **criterion):
        """Create WindowSpecification object for top-level window"""
        if 'top_level_only' not in criterion:
            criterion['top_level_only'] = True
        if 'backend' not in criterion:
            criterion['backend'] = self.backend
        return WindowSpecification(criterion)

    def __getitem__(self, key):
        """Allow describe top-level window as Desktop()['Window Caption']"""
        return self.window(best_match=key)

    def __getattribute__(self, attr_name):
        """Attribute access for this class"""
        try:
            return object.__getattribute__(self, attr_name)
        except AttributeError:
            return self[attr_name] # delegate it to __get_item__

