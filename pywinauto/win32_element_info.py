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

"""Implementation of the class to deal with a native element (window with a handle)"""

import ctypes

from . import win32functions
from . import handleprops
from .element_info import ElementInfo


class HwndElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        self._cache = {}
        if handle is None:  # root element
            self._handle = win32functions.GetDesktopWindow()
        else:
            self._handle = handle

    def set_cache_strategy(self, cached):
        """Set a cache strategy for frequently used attributes of the element"""
        pass  # TODO: implement a cache strategy for native elements

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def rich_text(self):
        """Return the text of the window"""
        return handleprops.text(self.handle)

    name = rich_text

    @property
    def control_id(self):
        """Return the ID of the window"""
        return handleprops.controlid(self.handle)

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return handleprops.processid(self.handle)

    @property
    def class_name(self):
        """Return the class name of the window"""
        return handleprops.classname(self.handle)

    @property
    def enabled(self):
        """Return True if the window is enabled"""
        return handleprops.isenabled(self.handle)

    @property
    def visible(self):
        """Return True if the window is visible"""
        return handleprops.isvisible(self.handle)

    @property
    def parent(self):
        """Return the parent of the window"""
        parent_hwnd = handleprops.parent(self.handle)
        if parent_hwnd:
            return HwndElementInfo(parent_hwnd)
        else:
            return None

    def children(self, **kwargs):
        """Return a list of immediate children of the window"""
        if self == HwndElementInfo():  # self == root
            child_handles = []

            # The callback function that will be called for each HWND
            # all we do is append the wrapped handle
            def enum_window_proc(hwnd, lparam):
                """Called for each window - adds handles to a list"""
                child_handles.append(hwnd)
                return True

            # define the type of the child procedure
            enum_win_proc_t = ctypes.WINFUNCTYPE(
                ctypes.c_int, ctypes.c_long, ctypes.c_long)

            # 'construct' the callback with our function
            proc = enum_win_proc_t(enum_window_proc)

            # loop over all the top level windows (callback called for each)
            win32functions.EnumWindows(proc, 0)
        else:
            # TODO: this code returns the whole sub-tree, we need to re-write it
            child_handles = handleprops.children(self._handle)
        return [HwndElementInfo(ch) for ch in child_handles]

    def descendants(self, **kwargs):
        """Return descendants of the window (all children from sub-tree)"""
        child_handles = handleprops.children(self.handle)
        child_handles = [HwndElementInfo(ch) for ch in child_handles]
        depth = kwargs.pop('depth', None)

        child_handles = ElementInfo.filter_with_depth(child_handles, self, depth)

        return child_handles

    @property
    def rectangle(self):
        """Return rectangle of the element"""
        return handleprops.rectangle(self.handle)

    def dump_window(self):
        """Dump a window as a set of properties"""
        return handleprops.dumpwindow(self.handle)

    def __eq__(self, other):
        """Check if 2 HwndElementInfo objects describe 1 actual element"""
        if not isinstance(other, HwndElementInfo):
            return self.handle == other
        return self.handle == other.handle
