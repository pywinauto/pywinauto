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

"""Functions to retrieve properties from a window handle

These are implemented in a procedural way so as to to be
useful to other modules with the least conceptual overhead
"""

import ctypes
import warnings
import win32process
import win32api
import win32con
import win32gui

from . import win32functions
from . import win32defines
from . import win32structures
from .actionlogger import ActionLogger


#=========================================================================
def text(handle):
    """Return the text of the window"""
    class_name = classname(handle)
    if class_name == 'IME':
        return 'Default IME'
    if class_name == 'MSCTFIME UI':
        return 'M'
    #length = win32functions.SendMessage(handle, win32defines.WM_GETTEXTLENGTH, 0, 0)

    # XXX: there are some very rare cases when WM_GETTEXTLENGTH hangs!
    # WM_GETTEXTLENGTH may hang even for notepad.exe main window!
    c_length = win32structures.DWORD(0)
    result = win32functions.SendMessageTimeout(
        handle,
        win32defines.WM_GETTEXTLENGTH,
        0,
        0,
        win32defines.SMTO_ABORTIFHUNG,
        500,
        ctypes.byref(c_length)
    )
    if result == 0:
        ActionLogger().log('WARNING! Cannot retrieve text length for handle = ' + str(handle))
        return None
    else:
        length = c_length.value

    textval = ''
    # In some rare cases, the length returned by WM_GETTEXTLENGTH is <0.
    # Guard against this by checking it is >0 (==0 is not of interest):
    if length > 0:
        length += 1

        buffer_ = ctypes.create_unicode_buffer(length)

        ret = win32functions.SendMessage(
            handle, win32defines.WM_GETTEXT, length, ctypes.byref(buffer_))

        if ret:
            textval = buffer_.value

    return textval


#=========================================================================
def classname(handle):
    """Return the class name of the window"""
    class_name = (ctypes.c_wchar * 257)()
    win32functions.GetClassName(handle, ctypes.byref(class_name), 256)
    return class_name.value


#=========================================================================
def parent(handle):
    """Return the handle of the parent of the window"""
    return win32functions.GetParent(handle)


#=========================================================================
def style(handle):
    """Return the style of the window"""
    return win32functions.GetWindowLong(handle, win32defines.GWL_STYLE)


#=========================================================================
def exstyle(handle):
    """Return the extended style of the window"""
    return win32functions.GetWindowLong(handle, win32defines.GWL_EXSTYLE)


#=========================================================================
def controlid(handle):
    """Return the ID of the control"""
    return win32functions.GetWindowLong(handle, win32defines.GWL_ID)


#=========================================================================
def userdata(handle):
    """Return the value of any user data associated with the window"""
    return win32functions.GetWindowLong(handle, win32defines.GWL_USERDATA)


#=========================================================================
def contexthelpid(handle):
    """Return the context help id of the window"""
    return win32functions.GetWindowContextHelpId(handle)


#=========================================================================
def iswindow(handle):
    """Return True if the handle is a window"""
    return bool(win32functions.IsWindow(handle))


#=========================================================================
def isvisible(handle):
    """Return True if the window is visible"""
    return bool(win32functions.IsWindowVisible(handle))


#=========================================================================
def isunicode(handle):
    """Return True if the window is a Unicode window"""
    return bool(win32functions.IsWindowUnicode(handle))


#=========================================================================
def isenabled(handle):
    """Return True if the window is enabled"""
    return bool(win32functions.IsWindowEnabled(handle))


#=========================================================================
def is64bitprocess(process_id):
    """Return True if the specified process is a 64-bit process on x64

    Return False if it is only a 32-bit process running under Wow64.
    Always return False for x86.
    """
    from .sysinfo import is_x64_OS
    is32 = True
    if is_x64_OS():
        phndl = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, 0, process_id)
        if phndl:
            is32 = win32process.IsWow64Process(phndl)
            #print("is64bitprocess, is32: %d, procid: %d" % (is32, process_id))

    return (not is32)


#=========================================================================
def is64bitbinary(filename):
    """Check if the file is 64-bit binary"""
    import win32file
    try:
        binary_type = win32file.GetBinaryType(filename)
        return binary_type != win32file.SCS_32BIT_BINARY
    except Exception as exc:
        warnings.warn('Cannot get binary type for file "{}". Error: {}' \
            ''.format(filename, exc), RuntimeWarning, stacklevel=2)
        return None


#=========================================================================
def clientrect(handle):
    """Return the client rectangle of the control"""
    client_rect = win32structures.RECT()
    win32functions.GetClientRect(handle, ctypes.byref(client_rect))
    return client_rect


#=========================================================================
def rectangle(handle):
    """Return the rectangle of the window"""
    # GetWindowRect returns 4-tuple
    return win32structures.RECT(*win32gui.GetWindowRect(handle))


#=========================================================================
def font(handle):
    """Return the font as a LOGFONTW of the window"""
    # get the font handle
    font_handle = win32functions.SendMessage(
        handle, win32defines.WM_GETFONT, 0, 0)

    # if the fondUsed is 0 then the control is using the
    # system font (well probably not - even though that is what the docs say)
    # instead we switch to the default GUI font - which is more likely correct.
    if not font_handle:

        # So just get the default system font
        font_handle = win32functions.GetStockObject(win32defines.DEFAULT_GUI_FONT)

        # if we still don't have a font!
        # ----- ie, we're on an antiquated OS, like NT 3.51
        if not font_handle:

            # ----- On Asian platforms, ANSI font won't show.
            if win32functions.GetSystemMetrics(win32defines.SM_DBCSENABLED):
                # ----- was...(SYSTEM_FONT)
                font_handle = win32functions.GetStockObject(
                    win32defines.SYSTEM_FONT)
            else:
                # ----- was...(SYSTEM_FONT)
                font_handle = win32functions.GetStockObject(
                    win32defines.ANSI_VAR_FONT)

    else:
        fontval = win32structures.LOGFONTW()
        ret = win32functions.GetObject(
            font_handle, ctypes.sizeof(fontval), ctypes.byref(fontval))

    # Get the Logfont structure of the font of the control
    fontval = win32structures.LOGFONTW()
    ret = win32functions.GetObject(
        font_handle, ctypes.sizeof(fontval), ctypes.byref(fontval))

    # The function could not get the font - this is probably
    # because the control does not have associated Font/Text
    # So we should make sure the elements of the font are zeroed.
    if not ret:
        fontval = win32structures.LOGFONTW()

    # if it is a main window
    if is_toplevel_window(handle):

        if "MS Shell Dlg" in fontval.lfFaceName or \
           fontval.lfFaceName == "System":
            # these are not usually the fonts actaully used in for
            # title bars so we need to get the default title bar font

            # get the title font based on the system metrics rather
            # than the font of the control itself
            ncms = win32structures.NONCLIENTMETRICSW()
            ncms.cbSize = ctypes.sizeof(ncms)
            win32functions.SystemParametersInfo(
                win32defines.SPI_GETNONCLIENTMETRICS,
                ctypes.sizeof(ncms),
                ctypes.byref(ncms),
                0)

            # with either of the following 2 flags set the font of the
            # dialog isthe small one (but there is normally no difference!
            if has_style(handle, win32defines.WS_EX_TOOLWINDOW) or \
               has_style(handle, win32defines.WS_EX_PALETTEWINDOW):

                fontval = ncms.lfSmCaptionFont
            else:
                fontval = ncms.lfCaptionFont

    return fontval


#=========================================================================
def processid(handle):
    """Return the ID of process that controls this window"""
    _, process_id = win32process.GetWindowThreadProcessId(int(handle))
    return process_id


#=========================================================================
def has_enough_privileges(process_id):
    """Check if target process has enough rights to query GUI actions"""
    try:
        access_level = win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ
        process_handle = win32api.OpenProcess(access_level, 0, process_id)
        if process_handle:
            win32api.CloseHandle(process_handle)
            return True
        return False
    except win32gui.error:
        return False


#=========================================================================
def children(handle):
    """Return a list of handles to the children of this window"""
    # this will be filled in the callback function
    child_windows = []

    # callback function for EnumChildWindows
    def enum_child_proc(hwnd, lparam):
        """Called for each child - adds child hwnd to list"""
        # append it to our list
        child_windows.append(hwnd)

        # return true to keep going
        return True

    # define the child proc type
    enum_child_proc_t = ctypes.WINFUNCTYPE(
        ctypes.c_int,            # return type
        win32structures.HWND,    # the window handle
        win32structures.LPARAM)  # extra information

    # update the proc to the correct type
    proc = enum_child_proc_t(enum_child_proc)

    # loop over all the children (callback called for each)
    win32functions.EnumChildWindows(handle, proc, 0)

    return child_windows


#=========================================================================
def has_style(handle, tocheck):
    """Return True if the control has style tocheck"""
    hwnd_style = style(handle)
    return tocheck & hwnd_style == tocheck


#=========================================================================
def has_exstyle(handle, tocheck):
    """Return True if the control has extended style tocheck"""
    hwnd_exstyle = exstyle(handle)
    return tocheck & hwnd_exstyle == tocheck


#=========================================================================
def is_toplevel_window(handle):
    """Return whether the window is a top level window or not"""
    # only request the style once - this is an optimization over calling
    # (handle, style) for each style I wan to check!
    style_ = style(handle)

    if (style_ & win32defines.WS_OVERLAPPED == win32defines.WS_OVERLAPPED or
        style_ & win32defines.WS_CAPTION == win32defines.WS_CAPTION) and \
       not (style_ & win32defines.WS_CHILD == win32defines.WS_CHILD):
        return True
    else:
        return False


#=========================================================================
def dumpwindow(handle):
    """Dump a window to a set of properties"""
    props = {}

    for func in (text,
                 classname,
                 rectangle,
                 clientrect,
                 style,
                 exstyle,
                 contexthelpid,
                 controlid,
                 userdata,
                 font,
                 parent,
                 processid,
                 isenabled,
                 isunicode,
                 isvisible,
                 children,
                 ):

        props[func.__name__] = func(handle)

    return props
