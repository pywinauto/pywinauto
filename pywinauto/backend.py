# GUI Application automation and testing library
# Copyright (C) 2016 Vasily Ryabov
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

"""Back-end components storage (links to platform-specific things)"""

from .ElementInfo import ElementInfo
from .base_wrapper import BaseWrapper


class BackEnd(object):
    "Minimal back-end description (name & 2 required base classes)"

    def __init__(self, name, element_info_class, generic_wrapper_class):
        "Init back-end description"
        self.name = name
        if not issubclass(element_info_class, ElementInfo):
            raise TypeError('element_info_class should be a class derived from ElementInfo')
        if not issubclass(generic_wrapper_class, BaseWrapper):
            raise TypeError('element_info_class should be a class derived from BaseWrapper')
        self.element_info_class = element_info_class
        self.generic_wrapper_class = generic_wrapper_class

class BackendsRegistry(object):
    "Registry pattern class for the list of available back-ends"

    def __init__(self):
        "Init back-ends list (it doesn't aware of concrete back-ends yet)"
        self.backends = {}
        self.active_backend = None

    @property
    def name(self):
        "Name of the active backend"
        return self.active_backend.name

    @property
    def element_class(self):
        "ElementInfo's subclass of the active backend"
        return self.active_backend.element_info_class

    @property
    def wrapper_class(self):
        "BaseWrapper's subclass of the active backend"
        return self.active_backend.generic_wrapper_class

registry = BackendsRegistry()

def name():
    "Return name of the active backend"
    return registry.name

def element_class():
    "Return ElementInfo's subclass of the active backend"
    return registry.element_class

def wrapper_class():
    "Return BaseWrapper's subclass of the active backend"
    return registry.element_class

def activate(name):
    """
    Set active back-end by name

    Possible values of **active_name** are "native", "uia" or
    other name registered by the **register** function.
    """
    if name not in registry.backends:
        raise ValueError('Back-end "{backend}" is not registered!'.format(backend=name))

    registry.active_backend = registry.backends[name]


def register(name, element_info_class, generic_wrapper_class):
    "Register new back-end"
    
    registry.backends[name] = BackEnd(name, element_info_class, generic_wrapper_class)
