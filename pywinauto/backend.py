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

"""Back-end components storage (links to platform-specific things)"""

from .element_info import ElementInfo
from .base_wrapper import BaseWrapper


class BackEnd(object):

    """Minimal back-end description (name & 2 required base classes)"""

    def __init__(self, name, element_info_class, generic_wrapper_class):
        """Init back-end description"""
        self.name = name
        if not issubclass(element_info_class, ElementInfo):
            raise TypeError('element_info_class should be a class derived from ElementInfo')
        if not issubclass(generic_wrapper_class, BaseWrapper):
            raise TypeError('element_info_class should be a class derived from BaseWrapper')
        self.element_info_class = element_info_class
        self.generic_wrapper_class = generic_wrapper_class


class BackendsRegistry(object):

    """Registry pattern class for the list of available back-ends"""

    def __init__(self):
        """Init back-ends list (it doesn't aware of concrete back-ends yet)"""
        self.backends = {}
        self.active_backend = None

    @property
    def name(self):
        """Name of the active backend"""
        return self.active_backend.name

    @property
    def element_class(self):
        """Return :py:class:`.element_info.ElementInfo`'s subclass of the active backend"""
        return self.active_backend.element_info_class

    @property
    def wrapper_class(self):
        """BaseWrapper's subclass of the active backend"""
        return self.active_backend.generic_wrapper_class

registry = BackendsRegistry()

def name():
    """Return name of the active backend"""
    return registry.name

def element_class():
    """Return :py:class:`.element_info.ElementInfo`'s subclass of the active backend"""
    return registry.element_class

def wrapper_class():
    """Return BaseWrapper's subclass of the active backend"""
    return registry.wrapper_class

def activate(name):
    """
    Set active backend by name

    Possible values of **name** are "win32", "uia" or
    other name registered by the :py:func:`register` function.
    """
    if name not in registry.backends:
        raise ValueError('Back-end "{backend}" is not registered!'.format(backend=name))

    registry.active_backend = registry.backends[name]

def register(name, element_info_class, generic_wrapper_class):
    """Register a new backend"""
    registry.backends[name] = BackEnd(name, element_info_class, generic_wrapper_class)
