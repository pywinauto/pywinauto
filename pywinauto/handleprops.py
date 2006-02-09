# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
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

"""Functions to retrieve properties from a window handle

These are implemented in a procedural way so as to to be
useful to other modules with the least conceptual overhead
"""

__revision__ = "$Revision$"

import ctypes

import win32functions
import win32defines
import win32structures

import findwindows # for children


#=========================================================================
def text(handle):
    "Return the text of the window"
    length = win32functions.GetWindowTextLength(handle,)

    textval = ''
    if length:
        length += 1

        buffer_ = (ctypes.c_wchar * length)()

        ret =  win32functions.GetWindowText(
            handle, ctypes.byref(buffer_), length)

        if ret:
            textval = buffer_.value

    return textval

#=========================================================================
def classname(handle):
    "Return the class name of the window"
    class_name = (ctypes.c_wchar * 257)()
    win32functions.GetClassName (handle, ctypes.byref(class_name), 256)
    return class_name.value


#=========================================================================
def parent(handle):
    "Return the handle of the parent of the window"
    return win32functions.GetParent(handle)

#=========================================================================
def style(handle):
    "Return the style of the window"
    return win32functions.GetWindowLong (handle, win32defines.GWL_STYLE)

#=========================================================================
def exstyle(handle):
    "Return the extended style of the window"
    return win32functions.GetWindowLong (handle, win32defines.GWL_EXSTYLE)

#=========================================================================
def controlid(handle):
    "Return the ID of the control"
    return win32functions.GetWindowLong (handle, win32defines.GWL_ID)

#=========================================================================
def userdata(handle):
    "Return the value of any userdata associated with the window"
    return win32functions.GetWindowLong (handle, win32defines.GWL_USERDATA)

#=========================================================================
def contexthelpid(handle):
    "Return the context help id of the window"
    return win32functions.GetWindowContextHelpId (handle)

#=========================================================================
def isvisible(handle):
    "Return True if the window is visible"
    return bool(win32functions.IsWindowVisible(handle))

#=========================================================================
def isunicode(handle):
    "Teturn True if the window is a unicode window"
    return bool(win32functions.IsWindowUnicode(handle))

#=========================================================================
def isenabled(handle):
    "Return True if the window is enabled"
    return bool(win32functions.IsWindowEnabled(handle))

#=========================================================================
def clientrect(handle):
    "Return the client rectangle of the control"
    client_rect = win32structures.RECT()
    win32functions.GetClientRect(handle, ctypes.byref(client_rect))
    return client_rect

#=========================================================================
def rectangle(handle):
    "Return the rectangle of the window"
    rect = win32structures.RECT()
    win32functions.GetWindowRect(handle, ctypes.byref(rect))
    return rect

#=========================================================================
def font(handle):
    "Return the font as a LOGFONTW of the window"

    # get the font handle
    font_handle = win32functions.SendMessage(
        handle, win32defines.WM_GETFONT, 0, 0)

    # if the fondUsed is 0 then the control is using the
    # system font
    if not font_handle:
        font_handle = win32functions.GetStockObject(win32defines.SYSTEM_FONT)

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
    if (has_style(handle, win32defines.WS_OVERLAPPED) or \
        has_style(handle, win32defines.WS_CAPTION)) and \
        not has_style(handle, win32defines.WS_CHILD):

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
    "Retrun the ID of process that controls this window"
    process_id = ctypes.c_int()
    win32functions.GetWindowThreadProcessId(handle, ctypes.byref(process_id))

    return process_id.value

#=========================================================================
def children(handle):
    "Return a list of handles to the children of this window"
    return findwindows.enum_child_windows(handle)


#=========================================================================
def has_style(handle, tocheck):
    "Return True if the control has style tocheck"
    hwnd_style = style(handle)
    return tocheck & hwnd_style == tocheck

#=========================================================================
def has_exstyle(handle, tocheck):
    "Return True if the control has extended style tocheck"
    hwnd_exstyle = exstyle(handle)
    return tocheck & hwnd_exstyle == tocheck


#=========================================================================
def is_toplevel_window(handle):
    "Return whether the window is a top level window or not"

    # I don't like this so I have commented it out
    #if classname(handle) in ['tooltips_class32']:
    #    return False

    if (has_style(handle, win32defines.WS_OVERLAPPED) or \
        has_style(handle, win32defines.WS_CAPTION)) and \
        not has_style(handle, win32defines.WS_CHILD):
        return True
    else:
        return False


def get_button_friendlyclassname(handle):
    "Return the friendly class name of a button control"

    # get the least significant bit
    style_lsb = style(handle) & 0xF

    # default to "Button"
    f_classname = "Button"

    if style_lsb == win32defines.BS_3STATE or \
        style_lsb == win32defines.BS_AUTO3STATE or \
        style_lsb == win32defines.BS_AUTOCHECKBOX or \
        style_lsb == win32defines.BS_CHECKBOX:
        f_classname = "CheckBox"

    elif style_lsb == win32defines.BS_RADIOBUTTON or \
        style_lsb == win32defines.BS_AUTORADIOBUTTON:
        f_classname = "RadioButton"

    elif style_lsb == win32defines.BS_GROUPBOX:
        f_classname = "GroupBox"

    if style(handle) & win32defines.BS_PUSHLIKE:
        f_classname = "Button"

    return f_classname


def friendlyclassname(handle):
    """Return the friendly class name of the window

    The friendly class name might be subjective, but it
    tries to be what a normal user would call a window
    rather then the windows class name for the window.
    """

    # if it's a dialog then return that
    if is_toplevel_window(handle):
        return "Dialog"

    class_name = classname(handle)

    from controls import wraphandle
    info = wraphandle._find_wrapper(class_name)

    if info:
        return info.friendlyclassname

    else:
        return class_name
#
#
#    # Check if the class name is in the known classes
#    for cls_name, f_cls_name in _class_names.items():
#
#        # OK we found it
#        if re.match(cls_name, classname(handle)):
#            # If it is a string then just return it
#            if isinstance(f_cls_name, basestring):
#                return f_cls_name
#            # otherwise it is a function so call it
#            else:
#                return f_cls_name(handle)
#
#    # unknown class - just return it's classname
#    return classname(handle)





#=========================================================================
def dumpwindow(handle):
    "Dump a window to a set of properties"
    props = {}

    for func in (
        text,
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

#=========================================================================
def _unittests():
    "Quick test of module"
    handle = win32functions.GetDesktopWindow()

    for name, value in dumpwindow(handle).items():
        print "%15s\t%s" % (name, value)

if __name__ == "__main__":
    _unittests()
