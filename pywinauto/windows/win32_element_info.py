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

"""Implementation of the class to deal with a native element (window with a handle)"""

import ctypes
import six
import win32gui

from . import win32functions
from . import win32structures
from .. import handleprops
from ..element_info import ElementInfo
from .remote_memory_block import RemoteMemoryBlock


def _register_win_msg(msg_name):
    msg_id = win32functions.RegisterWindowMessage(six.text_type(msg_name))
    if not isinstance(msg_id, six.integer_types):
        return -1 # return dummy value if win32functions is mocked (on ReadTheDocs)
    if msg_id > 0:
        return msg_id
    else:
        raise Exception("Cannot register {}".format(msg_name))


class HwndElementInfo(ElementInfo):

    """Wrapper for window handler"""

    wm_get_ctrl_name = _register_win_msg('WM_GETCONTROLNAME')
    wm_get_ctrl_type = _register_win_msg('WM_GETCONTROLTYPE')
    re_props = ["class_name", "name", "auto_id", "control_type", "full_control_type"]
    exact_only_props = ["handle", "pid", "control_id", "enabled", "visible", "rectangle"]
    search_order = ["handle", "class_name", "pid", "control_id", "visible", "enabled", "name",
        "auto_id", "control_type", "full_control_type", "rectangle"]
    assert set(re_props + exact_only_props) == set(search_order)

    renamed_props = {
        "title": ("name", None),
        "title_re": ("name_re", None),
        "process": ("pid", None),
        "visible_only": ("visible", {True: True, False: None}),
        "enabled_only": ("enabled", {True: True, False: None}),
        "top_level_only": ("depth", {True: 1, False: None}),
    }

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

    pid = process_id

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
        class_name = kwargs.get('class_name', None)
        name = kwargs.get('name', None)
        control_type = kwargs.get('control_type', None)
        process = kwargs.get('process', None)
        # TODO: 'cache_enable' and 'depth' are ignored so far

        # this will be filled in the callback function
        child_elements = []

        # The callback function that will be called for each HWND
        # all we do is append the wrapped handle
        def enum_window_proc(hwnd, lparam):
            """Called for each window - adds wrapped elements to a list"""
            element = HwndElementInfo(hwnd)
            if process is not None and process != element.pid:
                return True
            if class_name is not None and class_name != element.class_name:
                return True
            if name is not None and name != element.rich_text:
                return True
            if control_type is not None and control_type != element.control_type:
                return True
            child_elements.append(element)
            return True

        # define the type of the child procedure
        enum_win_proc_t = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                             ctypes.wintypes.HWND,
                                             ctypes.wintypes.LPARAM)

        # 'construct' the callback with our function
        proc = enum_win_proc_t(enum_window_proc)

        if self == HwndElementInfo():  # self == root
            # loop over all the top level windows (callback called for each)
            win32functions.EnumWindows(proc, 0)
        else:
            # loop over all the children (callback called for each)
            win32functions.EnumChildWindows(self.handle, proc, 0)

        return child_elements

    def iter_children(self, **kwargs):
        """Return a generator of immediate children of the window"""
        # TODO: Iterate over children using Win32 API
        for child in self.children(**kwargs):
            yield child

    def descendants(self, **kwargs):
        """Return descendants of the window (all children from sub-tree)"""
        if self == HwndElementInfo(): # root
            top_elements = self.children()
            child_elements = self.children(**kwargs)
            for child in top_elements:
                child_elements.extend(child.children(**kwargs))
        else:
            child_elements = self.children(**kwargs)
        depth = kwargs.pop('depth', None)

        child_elements = ElementInfo.filter_with_depth(child_elements, self, depth)
        return child_elements

    @property
    def rectangle(self):
        """Return rectangle of the element"""
        return handleprops.rectangle(self.handle)

    def dump_window(self):
        """Dump a window as a set of properties"""
        return handleprops.dumpwindow(self.handle)

    def __hash__(self):
        """Return a unique hash value based on the element's handle"""
        return hash(self.handle)

    def __eq__(self, other):
        """Check if 2 HwndElementInfo objects describe 1 actual element"""
        if not isinstance(other, HwndElementInfo):
            return self.handle == other
        return self.handle == other.handle

    def __ne__(self, other):
        """Check if two HwndElementInfo objects describe different elements"""
        return not (self == other)

    @property
    def auto_id(self):
        """Return AutomationId of the element"""
        textval = ''

        length = 1024
        remote_mem = RemoteMemoryBlock(self, size=length*2)

        ret = win32gui.SendMessage(self.handle, self.wm_get_ctrl_name, length, remote_mem.mem_address)

        if ret:
            text = ctypes.create_unicode_buffer(length)
            remote_mem.Read(text)
            textval = text.value

        del remote_mem
        return textval

    def __get_control_type(self, full=False):
        """Internal parameterized method to distinguish control_type and full_control_type properties"""
        textval = ''

        length = 1024
        remote_mem = RemoteMemoryBlock(self, size=length*2)

        ret = win32gui.SendMessage(self.handle, self.wm_get_ctrl_type, length, remote_mem.mem_address)

        if ret:
            text = ctypes.create_unicode_buffer(length)
            remote_mem.Read(text)
            textval = text.value

        del remote_mem

        # simplify control type for WinForms controls
        if (not full) and ("PublicKeyToken" in textval):
            textval = textval.split(", ")[0]
        return textval

    @property
    def control_type(self):
        """Return control type of the element"""
        return self.__get_control_type(full=False)

    @property
    def full_control_type(self):
        """Return full string of control type of the element"""
        return self.__get_control_type(full=True)

    @classmethod
    def from_point(cls, x, y):
        """Return child element at specified point coordinates"""
        current_handle = win32gui.WindowFromPoint((x, y))
        child_handle = win32gui.ChildWindowFromPoint(current_handle, (x, y))
        if child_handle:
            return cls(child_handle)
        else:
            return cls(current_handle)

    @classmethod
    def top_from_point(cls, x, y):
        """Return top level element at specified point coordinates"""
        current_elem = cls.from_point(x, y)
        current_parent = current_elem.parent
        while current_parent is not None and current_parent != cls():
            current_elem = current_parent
            current_parent = current_elem.parent
        return current_elem

    @classmethod
    def get_active(cls):
        """Return current active element"""
        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)

        # get all the active elements (not just the specified process)
        ret = win32functions.GetGUIThreadInfo(0, ctypes.byref(gui_info))

        if not ret:
            raise ctypes.WinError()

        hwndActive = gui_info.hwndActive

        return cls(hwndActive) if hwndActive is not None else None
