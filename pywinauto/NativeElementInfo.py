# GUI Application automation and testing library
# Copyright (C) 2016 Vasily Ryabov
# Copyright (C) 2016 Alexander Rumyantsev
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

import ctypes

from . import win32functions
from . import handleprops
from .ElementInfo import ElementInfo

class NativeElementInfo(ElementInfo):
    "Wrapper for window handler"
    def __init__(self, handle = None):
        self._cache = {}
        if handle is None: # root element
            self._handle = win32functions.GetDesktopWindow()
        else:
            self._handle = handle

    @property
    def handle(self):
        "Return the handle of the window"
        return self._handle

    @property
    def richText(self):
        "Return the text of the window"
        return handleprops.text(self._handle)

    name = richText

    @property
    def controlId(self):
        "Return the ID of the window"
        return handleprops.controlid(self._handle)

    @property
    def processId(self):
        "Return the ID of process that controls this window"
        return handleprops.processid(self._handle)

    @property
    def className(self):
        "Return the class name of the window"
        return handleprops.classname(self._handle)

    @property
    def enabled(self):
        "Return True if the window is enabled"
        return handleprops.isenabled(self._handle)

    @property
    def visible(self):
        "Return True if the window is visible"
        return handleprops.isvisible(self._handle)

    @property
    def parent(self):
        "Return the parent of the window"
        return NativeElementInfo(handleprops.parent(self._handle))

    @property
    def children(self):
        "Return a list of immediate children of the window"
        if self == NativeElementInfo(): # self == root
            child_handles = []

            # The callback function that will be called for each HWND
            # all we do is append the wrapped handle
            def EnumWindowProc(hwnd, lparam):
                "Called for each window - adds handles to a list"
                child_handles.append(hwnd)
                return True

            # define the type of the child procedure
            enum_win_proc = ctypes.WINFUNCTYPE(
                ctypes.c_int, ctypes.c_long, ctypes.c_long)

            # 'construct' the callback with our function
            proc = enum_win_proc(EnumWindowProc)

            # loop over all the top level windows (callback called for each)
            win32functions.EnumWindows(proc, 0)
        else:
            # TODO: this code returns the whole sub-tree, we need to re-write it
            child_handles = handleprops.children(self._handle)
        return [NativeElementInfo(ch) for ch in child_handles]

    @property
    def descendants(self):
        "Return descendants of the window (all children from sub-tree)"
        child_handles = handleprops.children(self._handle)
        return [NativeElementInfo(ch) for ch in child_handles]

    @property
    def rectangle(self):
        "Return rectangle of element"
        return handleprops.rectangle(self._handle)

    def dumpWindow(self):
        "Dump a window to a set of properties"
        return handleprops.dumpwindow(self._handle)

    def __eq__(self, other):
        "Check if 2 NativeElementInfo objects describe 1 actual element"
        if not isinstance(other, NativeElementInfo):
            return False
        return self._handle == other._handle
