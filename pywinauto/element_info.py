# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Interface for classes which should deal with different backend elements"""

class ElementInfo(object):

    """Abstract wrapper for an element"""

    def set_cache_strategy(self, cached):
        """Set a cache strategy for frequently used attributes of the element"""
        raise NotImplementedError()

    @property
    def handle(self):
        """Return the handle of the element"""
        raise NotImplementedError()

    @property
    def name(self):
        """Return the name of the element"""
        raise NotImplementedError()

    @property
    def rich_text(self):
        """Return the text of the element"""
        raise NotImplementedError()

    @property
    def control_id(self):
        """Return the ID of the control"""
        raise NotImplementedError()

    @property
    def process_id(self):
        """Return the ID of process that controls this element"""
        raise NotImplementedError()

    @property
    def framework_id(self):
        """Return the framework of the element"""
        raise NotImplementedError()

    @property
    def class_name(self):
        """Return the class name of the element"""
        raise NotImplementedError()

    @property
    def enabled(self):
        """Return True if the element is enabled"""
        raise NotImplementedError()

    @property
    def visible(self):
        """Return True if the element is visible"""
        raise NotImplementedError()

    @property
    def parent(self):
        """Return the parent of the element"""
        raise NotImplementedError()

    def children(self, **kwargs):
        """Return children of the element"""
        raise NotImplementedError()

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        raise NotImplementedError()

    @property
    def rectangle(self):
        """Return rectangle of element"""
        raise NotImplementedError()

    def dump_window(self):
        """Dump an element to a set of properties"""
        raise NotImplementedError()
