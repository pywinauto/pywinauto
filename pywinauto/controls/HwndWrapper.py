# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2013 Michael Herrmann
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

"""Basic wrapping of Windows controls"""
from __future__ import unicode_literals
from __future__ import print_function

# pylint:  disable-msg=W0611

#import sys
import time
import re
import ctypes
import win32api
import win32gui
import win32con
import win32process
import locale

# the wrappers may be used in an environment that does not need
# the actions - as such I don't want to require sendkeys - so
# the following makes the import optional.

from .. import SendKeysCtypes as SendKeys
from .. import win32functions
from ..actionlogger import ActionLogger

# I leave this optional because PIL is a large dependency
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

from .. import six
from .. import win32defines
from .. import win32structures
from ..timings import Timings
from .. import timings

#from .. import findbestmatch
from .. import handleprops
from ..NativeElementInfo import NativeElementInfo
from .. import backend

# also import MenuItemNotEnabled so that it is
# accessible from HwndWrapper module
from .menuwrapper import Menu #, MenuItemNotEnabled

from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta


#====================================================================
class ControlNotEnabled(RuntimeError):
    "Raised when a control is not enabled"
    pass

#====================================================================
class ControlNotVisible(RuntimeError):
    "Raised when a control is not visible"
    pass

#====================================================================
class InvalidWindowHandle(RuntimeError):
    "Raised when an invalid handle is passed to HwndWrapper "
    def __init__(self, hwnd):
        "Initialise the RuntimError parent with the mesage"
        RuntimeError.__init__(self,
            "Handle {0} is not a vaild window handle".format(hwnd))

#=========================================================================
class HwndMeta(BaseMeta):
    "Metaclass for HwndWrapper objects"
    re_wrappers = {}
    str_wrappers = {}

    def __init__(cls, name, bases, attrs):
        # register the class names, both the regular expression
        # or the classes directly

        #print("metaclass __init__", cls)
        BaseMeta.__init__(cls, name, bases, attrs)

        for win_class in cls.windowclasses:
            HwndMeta.re_wrappers[re.compile(win_class)] = cls
            HwndMeta.str_wrappers[win_class] = cls

    @staticmethod
    def find_wrapper(element):
        "Find the correct wrapper for this native element"
        if isinstance(element, six.integer_types):
            from ..NativeElementInfo import NativeElementInfo
            element = NativeElementInfo(element)
        class_name = element.className

        try:
            return HwndMeta.str_wrappers[class_name]
        except KeyError:
            wrapper_match = None

            for regex, wrapper in HwndMeta.re_wrappers.items():
                if regex.match(class_name):
                    wrapper_match = wrapper
                    HwndMeta.str_wrappers[class_name] = wrapper

                    return wrapper

        # if it is a dialog then override the wrapper we found
        # and make it a DialogWrapper
        if handleprops.is_toplevel_window(element.handle):
            from . import win32_controls
            wrapper_match = win32_controls.DialogWrapper

        if wrapper_match is None:
            from .HwndWrapper import HwndWrapper
            wrapper_match = HwndWrapper
        return wrapper_match

#====================================================================
@six.add_metaclass(HwndMeta)
class HwndWrapper(BaseWrapper):
    """Default wrapper for controls.

    All other wrappers are derived from this.

    This class wraps a lot of functionality of underlying windows API
    features for working with windows.

    Most of the methods apply to every single window type. For example
    you can Click() on any window.

    Most of the methods of this class are simple wrappers around
    API calls and as such they try do the simplest thing possible.

    A HwndWrapper object can be passed directly to a ctypes wrapped
    C function - and it will get converted to a Long with the value of
    it's handle (see ctypes, _as_parameter_)"""

    handle = None

    # specify whether we need to grab an image of ourselves
    # when asked for properties
    _NeedsImageProp = False

    #-----------------------------------------------------------
    # TODO: can't inherit __new__ function from BaseWrapper?
    def __new__(cls, element):
        # only use the meta class to find the wrapper for HwndWrapper
        # so allow users to force the wrapper if they want
        # thanks to Raghav for finding this.
        if cls != HwndWrapper:
            obj = object.__new__(cls)
            obj.__init__(element)
            return obj

        new_class = cls.find_wrapper(element)

        obj = object.__new__(new_class)
        obj.__init__(element)

        return obj

    #-----------------------------------------------------------
    def __init__(self, elementInfo):
        """Initialize the control
        * **element_info** is either a valid NativeElementInfo or it can be an
          instance or subclass of HwndWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        if isinstance(elementInfo, six.integer_types):
            elementInfo = NativeElementInfo(elementInfo)
        if hasattr(elementInfo, "_elementInfo"):
            elementInfo = elementInfo.elementInfo

        BaseWrapper.__init__(self, elementInfo, backend.registry.backends['native'])

        # verify that we have been passed in a valid windows handle
        if not win32functions.IsWindow(self.handle):
            raise InvalidWindowHandle(self.handle)

        # make it so that ctypes conversion happens correctly
        self._as_parameter_ = self.handle

        # build the list of default properties to be written
        # Derived classes can either modify this list or override
        # GetProperties depending on how much control they need.
        self.writable_props = [
            'class_name',
            'friendly_class_name',
            'texts',
            'Style',
            'ExStyle',
            'control_id',
            'UserData',
            'ContextHelpID',
            'Fonts',
            'ClientRects',
            'rectangle',
            'is_visible',
            'IsUnicode',
            'is_enabled',
            'MenuItems',
            'control_count',
            ];

    #-----------------------------------------------------------
    def Style(self):
        """Returns the style of window

        Return value is a long.

        Combination of WS_* and specific control specific styles.
        See HwndWrapper.HasStyle() to easily check if the window has a
        particular style.
        """
        return handleprops.style(self)

    #-----------------------------------------------------------
    def ExStyle(self):
        """Returns the Extended style of window

        Return value is a long.

        Combination of WS_* and specific control specific styles.
        See HwndWrapper.HasStyle() to easily check if the window has a
        particular style.
        """
        return handleprops.exstyle(self)

    #-----------------------------------------------------------
    def UserData(self):
        """Extra data associted with the window

        This value is a long value that has been associated with the window
        and rarely has useful data (or at least data that you know the use
        of).
        """
        return handleprops.userdata(self)

    #-----------------------------------------------------------
    def ContextHelpID(self):
        """
        Return the Context Help ID of the window
        """
        return handleprops.contexthelpid(self)

    #-----------------------------------------------------------
    def IsActive(self):
        """
        Whether the window is active or not
        """
        return self.top_level_parent() == self.GetActive()

    #-----------------------------------------------------------
    def IsUnicode(self):
        """Whether the window is unicode or not

        A window is Unicode if it was registered by the Wide char version
        of RegisterClass(Ex).
        """
        return handleprops.isunicode(self)

    #-----------------------------------------------------------
    def ClientRect(self):
        """Returns the client rectangle of window

        The client rectangle is the window rectangle minus any borders that
        are not available to the control for drawing.

        Both top and left are always 0 for this method.

        This method returns a RECT structure, Which has attributes - top,
        left, right, bottom. and has methods width() and height().
        See win32structures.RECT for more information.
        """
        return handleprops.clientrect(self)

    #-----------------------------------------------------------
    #def client_to_screen(self, client_point):
    #    """Maps point from client to screen coordinates"""
    #    point = win32structures.POINT()
    #    if isinstance(client_point, win32structures.POINT):
    #        point.x = client_point.x
    #        point.y = client_point.y
    #    else:
    #        point.x = client_point[0]
    #        point.y = client_point[1]
    #    win32functions.client_to_screen(self, ctypes.byref(point))
    #
    #    # return tuple in any case because
    #    # coords param is always expected to be tuple
    #    return point.x, point.y

    #-----------------------------------------------------------
    def Font(self):
        """Return the font of the window

        The font of the window is used to draw the text of that window.
        It is a structure which has attributes for Font name, height, width
        etc.

        See win32structures.LOGFONTW for more information.
        """
        return handleprops.font(self)

    #-----------------------------------------------------------
    def HasStyle(self, style):
        "Return True if the control has the specified style"
        return handleprops.has_style(self, style)

    #-----------------------------------------------------------
    def HasExStyle(self, exstyle):
        "Return True if the control has the specified extended style"
        return handleprops.has_exstyle(self, exstyle)

    #-----------------------------------------------------------
    def is_dialog(self):
        "Return true if the control is a top level window"

        if not ("isdialog" in self._cache.keys()):
            self._cache['isdialog'] = handleprops.is_toplevel_window(self)

        return self._cache['isdialog']

    #-----------------------------------------------------------
    def ClientRects(self):
        """Return the client rect for each item in this control

        It is a list of rectangles for the control. It is frequently over-ridden
        to extract all rectangles from a control with multiple items.

        It is always a list with one or more rectangles:

          * First elemtent is the client rectangle of the control
          * Subsequent elements contain the client rectangle of any items of
            the control (e.g. items in a listbox/combobox, tabs in a
            tabcontrol)
        """

        return [self.ClientRect(), ]

    #-----------------------------------------------------------
    def Fonts(self):
        """Return the font for each item in this control

        It is a list of fonts for the control. It is frequently over-ridden
        to extract all fonts from a control with multiple items.

        It is always a list with one or more fonts:

          * First elemtent is the control font
          * Subsequent elements contain the font of any items of
            the control (e.g. items in a listbox/combobox, tabs in a
            tabcontrol)
        """
        return [self.Font(), ]

    #-----------------------------------------------------------
    def SendCommand(self, commandID):
        return self.SendMessage(win32defines.WM_COMMAND, commandID)

    #-----------------------------------------------------------
    def PostCommand(self, commandID):
        return self.PostMessage(win32defines.WM_COMMAND, commandID)

    #-----------------------------------------------------------
    #def Notify(self, code):
    #    "Send a notification to the parent (not tested yet)"

    #    # now we need to notify the parent that the state has changed
    #    nmhdr = win32structures.NMHDR()
    #    nmhdr.hwndFrom = self.handle
    #    nmhdr.idFrom = self.control_id()
    #    nmhdr.code = code

    #    from ..RemoteMemoryBlock import RemoteMemoryBlock
    #    remote_mem = RemoteMemoryBlock(self, size=ctypes.sizeof(nmhdr))
    #    remote_mem.Write(nmhdr, size=ctypes.sizeof(nmhdr))

    #    retval = self.parent().SendMessage(
    #        win32defines.WM_NOTIFY,
    #        self.handle,
    #        remote_mem)
    #    #if retval != win32defines.TRUE:
    #    #    print('retval = ' + str(retval))
    #    #    raise ctypes.WinError()
    #    del remote_mem

    #    return retval


    #-----------------------------------------------------------
    def SendMessage(self, message, wparam = 0 , lparam = 0):
        "Send a message to the control and wait for it to return"
        #return win32functions.SendMessage(self, message, wparam, lparam)
        wParamAddress = wparam
        if hasattr(wparam, 'memAddress'):
            wParamAddress = wparam.memAddress
        lParamAddress = lparam
        if hasattr(lparam, 'memAddress'):
            lParamAddress = lparam.memAddress

        CArgObject = type(ctypes.byref(ctypes.c_int(0)))
        if isinstance(wparam, CArgObject):
            wParamAddress = ctypes.addressof(wparam._obj)
        if isinstance(lparam, CArgObject):
            lParamAddress = ctypes.addressof(lparam._obj)

        return win32gui.SendMessage(self.handle, message, wParamAddress, lParamAddress)

        #result = ctypes.c_long()
        #ret = win32functions.SendMessageTimeout(self, message, wparam, lparam,
        #    win32defines.SMTO_NORMAL, 400, ctypes.byref(result))

        #return result.value


    #-----------------------------------------------------------
    def SendMessageTimeout(
        self,
        message,
        wparam = 0 ,
        lparam = 0,
        timeout = None,
        timeoutflags = win32defines.SMTO_NORMAL):
        """Send a message to the control and wait for it to return or to timeout

        If no timeout is given then a default timeout of .4 of a second will
        be used.
        """

        if timeout is None:
            timeout = Timings.sendmessagetimeout_timeout

        #result = ctypes.c_long()
        #win32functions.SendMessageTimeout(self,
        #    message, wparam, lparam,
        #    timeoutflags, int(timeout * 1000),
        #    ctypes.byref(result))
        result = -1
        try:
            (ret, result) = win32gui.SendMessageTimeout(int(self.handle), message, wparam, lparam, timeoutflags, int(timeout * 1000))
            #print '(ret, result) = ', (ret, result)
        except Exception as exc:
            #import traceback, inspect
            #print('____________________________________________________________')
            #print('self.handle =', int(self.handle), ', message =', message,
            #      ', wparam =', wparam, ', lparam =', lparam, ', timeout =', timeout)
            #print('Exception: ', exc)
            #print(traceback.format_exc())
            #print('Caller stack:')
            #for frame in inspect.stack():
            #    print(frame[1:])
            result = str(exc)

        return result #result.value


    #-----------------------------------------------------------
    def PostMessage(self, message, wparam = 0 , lparam = 0):
        "Post a message to the control message queue and return"
        return win32functions.PostMessage(self, message, wparam, lparam)

        #result = ctypes.c_long()
        #ret = win32functions.SendMessageTimeout(self, message, wparam, lparam,
        #    win32defines.SMTO_NORMAL, 400, ctypes.byref(result))

        #return result.value


#    #-----------------------------------------------------------
#    def NotifyMenuSelect(self, menu_id):
#        """Notify the dialog that one of it's menu items was selected
#
#        **This method is Deprecated**
#        """
#
#        import warnings
#        warning_msg = "HwndWrapper.NotifyMenuSelect() is deprecated - " \
#            "equivalent functionality is being moved to the MenuWrapper class."
#        warnings.warn(warning_msg, DeprecationWarning)
#
#        self.set_focus()
#
#        msg = win32defines.WM_COMMAND
#        return self.SendMessageTimeout(
#            msg,
#            win32functions.MakeLong(0, menu_id), #wparam
#            )
#

    #-----------------------------------------------------------
    def NotifyParent(self, message, controlID = None):
        "Send the notification message to parent of this control"

        if controlID is None:
            controlID = self.control_id()

        return self.parent().PostMessage(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(message, controlID),
            self)

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = {}

        # for each of the properties that can be written out
        for propname in self.writable_props:
            # set the item in the props dictionary keyed on the propname
            props[propname] = getattr(self, propname)()

        if self._NeedsImageProp:
            props["Image"] = self.CaptureAsImage()

        return props

    #-----------------------------------------------------------
    def CaptureAsImage(self, rect = None):
        """Return a PIL image of the control

        See PIL documentation to know what you can do with the resulting
        image"""

        rectangle = self.rectangle()
        if not (rectangle.width() and rectangle.height()):
            return None

        # PIL is optional so check first
        if not ImageGrab:
            print("PIL does not seem to be installed. "
                "PIL is required for CaptureAsImage")
            self.actions.log("PIL does not seem to be installed. "
                "PIL is required for CaptureAsImage")
            return None

        # get the control rectangle in a way that PIL likes it
        if rect:
            box = (rect.left, rect.top, rect.right, rect.bottom)
        else:
            box = (
                rectangle.left,
                rectangle.top,
                rectangle.right,
                rectangle.bottom)

        # grab the image and get raw data as a string
        return ImageGrab.grab(box)

    #-----------------------------------------------------------
    def __hash__(self):
        "Returns the hash value of the handle"
        return hash(self.handle)

    #-----------------------------------------------------------
    def Click(
        self, button = "left", pressed = "", coords = (0, 0), double = False, absolute = False):
        """Simulates a mouse click on the control

        This method sends WM_* messages to the control, to do a more
        'realistic' mouse click use click_input() which uses mouse_event() API
        to perform the click.

        This method does not require that the control be visible on the screen
        (i.e. it can be hidden beneath another window and it will still work.)
        """
        self.verify_actionable()

        _perform_click(self, button, pressed, coords, double, absolute=absolute)
        return self

    #-----------------------------------------------------------
    def CloseClick(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        """Perform a click action that should make the window go away

        The only difference from Click is that there are extra delays
        before and after the click action.
        """

        time.sleep(Timings.before_closeclick_wait)

        _perform_click(self, button, pressed, coords, double)

        def has_closed():
            return not (
                win32functions.IsWindow(self) or
                win32functions.IsWindow(self.parent()))

        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        timings.WaitUntil(
            Timings.closeclick_dialog_close_wait,
            Timings.closeclick_retry,
            has_closed
        )

        time.sleep(Timings.after_closeclick_wait)

        return self

    #-----------------------------------------------------------
    def CloseAltF4(self):
        """Close the window by pressing Alt+F4 keys."""

        time.sleep(Timings.before_closeclick_wait)
        self.type_keys('%{F4}')
        time.sleep(Timings.after_closeclick_wait)

        return self

    #-----------------------------------------------------------
    def DoubleClick(
        self, button = "left", pressed = "", coords = (0, 0)):
        "Perform a double click action"
        _perform_click(self, button, pressed, coords, double = True)
        return self

    #-----------------------------------------------------------
    def RightClick(
        self, pressed = "", coords = (0, 0)):
        "Perform a right click action"

        _perform_click(
            self, "right", "right " + pressed, coords, button_up = False)
        _perform_click(self, "right", pressed, coords, button_down = False)
        return self

    #-----------------------------------------------------------
    def PressMouse(self, button = "left", coords = (0, 0), pressed = ""):
        "Press the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)

        _perform_click(self, button, pressed, coords, button_down=True, button_up=False)
        return self

    #-----------------------------------------------------------
    def ReleaseMouse(self, button = "left", coords = (0, 0), pressed = ""):
        "Release the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)
        _perform_click(self, button, pressed, coords, button_down=False, button_up=True)
        return self

    #-----------------------------------------------------------
    def MoveMouse(self, coords = (0, 0), pressed = "", absolute = False):
        "Move the mouse by WM_MOUSEMOVE"

        if not absolute:
            self.actions.log('Moving mouse to relative (client) coordinates ' + str(coords).replace('\n', ', '))

        _perform_click(self, button='move', coords=coords, absolute=absolute, pressed=pressed)

        win32functions.WaitGuiThreadIdle(self)
        return self

    #-----------------------------------------------------------
    def DragMouse(self, button = "left",
        press_coords = (0, 0),
        release_coords = (0, 0),
        pressed = ""):
        "Drag the mouse"

        if isinstance(press_coords, win32structures.POINT):
            press_coords = (press_coords.x, press_coords.y)

        if isinstance(release_coords, win32structures.POINT):
            release_coords = (release_coords.x, release_coords.y)

        _pressed = pressed
        if not _pressed:
            _pressed = "left"

        self.PressMouse(button, press_coords, pressed=pressed)
        for i in range(5):
            self.MoveMouse((press_coords[0]+i,press_coords[1]), pressed=_pressed)
            time.sleep(Timings.drag_n_drop_move_mouse_wait)
        self.MoveMouse(release_coords, pressed=_pressed)
        time.sleep(Timings.before_drop_wait)
        self.ReleaseMouse(button, release_coords, pressed=pressed)
        time.sleep(Timings.after_drag_n_drop_wait)
        return self

    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        "Set the text of the window"

        self.verify_actionable()

        if append:
            text = self.window_text() + text

        text = ctypes.c_wchar_p(six.text_type(text))
        self.PostMessage(win32defines.WM_SETTEXT, 0, text)
        win32functions.WaitGuiThreadIdle(self)

        self.actions.log('Set text to the ' + self.friendly_class_name() + ': ' + str(text))
        return self

    #-----------------------------------------------------------
    def DebugMessage(self, text):
        "Write some debug text over the window"

        # don't draw if dialog is not visible

        dc = win32functions.CreateDC("DISPLAY", None, None, None )

        if not dc:
            raise ctypes.WinError()

        rect = self.rectangle()

        #ret = win32functions.TextOut(
        #    dc, rect.left, rect.top, six.text_type(text), len(text))
        ret = win32functions.DrawText(
            dc,
            six.text_type(text),
            len(text),
            ctypes.byref(rect),
            win32defines.DT_SINGLELINE)

        # delete the Display context that we created
        win32functions.DeleteDC(dc)

        if not ret:
            raise ctypes.WinError()

        return self

    #-----------------------------------------------------------
    def DrawOutline(
        self,
        colour = 'green',
        thickness = 2,
        fill = win32defines.BS_NULL,
        rect = None):
        """Draw an outline around the window

        * **colour** can be either an integer or one of 'red', 'green', 'blue'
          (default 'green')
        * **thickness** thickness of rectangle (default 2)
        * **fill** how to fill in the rectangle (default BS_NULL)
        * **rect** the coordinates of the rectangle to draw (defaults to
          the rectangle of the control.
        """

        # don't draw if dialog is not visible
        if not self.is_visible():
            return

        colours = {
            "green" : 0x00ff00,
            "blue" : 0xff0000,
            "red" : 0x0000ff,
        }

        # if it's a known colour
        if colour in colours:
            colour = colours[colour]

        if not rect:
            rect = self.rectangle()

        # create the pen(outline)
        pen_handle = win32functions.CreatePen(
            win32defines.PS_SOLID, thickness, colour)

        # create the brush (inside)
        brush = win32structures.LOGBRUSH()
        brush.lbStyle = fill
        brush.lbHatch = win32defines.HS_DIAGCROSS
        brush_handle = win32functions.CreateBrushIndirect(ctypes.byref(brush))

        # get the Device Context
        dc = win32functions.CreateDC("DISPLAY", None, None, None )

        # push our objects into it
        win32functions.SelectObject(dc, brush_handle)
        win32functions.SelectObject(dc, pen_handle)

        # draw the rectangle to the DC
        win32functions.Rectangle(
            dc, rect.left, rect.top, rect.right, rect.bottom)

        # Delete the brush and pen we created
        win32functions.DeleteObject(brush_handle)
        win32functions.DeleteObject(pen_handle)

        # delete the Display context that we created
        win32functions.DeleteDC(dc)


    #-----------------------------------------------------------
    def SetTransparency(self, alpha = 120):
        "Set the window transparency from 0 to 255 by alpha attribute"
        if not (0 <= alpha <= 255):
            raise ValueError('alpha should be in [0, 255] interval!')
        # TODO: implement SetExStyle method
        win32gui.SetWindowLong(self.handle, win32defines.GWL_EXSTYLE, self.ExStyle() | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(self.handle, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)


    #-----------------------------------------------------------
    def PopupWindow(self):
        """Return owned enabled Popup window wrapper if shown.

        If there is no enabled popups at that time, it returns **self**.
        See MSDN reference:
        https://msdn.microsoft.com/en-us/library/windows/desktop/ms633515.aspx

        Please do not use in production code yet - not tested fully
        """
        popup = win32functions.GetWindow(self, win32defines.GW_ENABLEDPOPUP)

        return popup


    #-----------------------------------------------------------
    def Owner(self):
        """Return the owner window for the window if it exists

        Returns None if there is no owner"""
        owner = win32functions.GetWindow(self, win32defines.GW_OWNER)
        if owner:
            return HwndWrapper(owner)
        else:
            return None

    #-----------------------------------------------------------
#    def ContextMenuSelect(self, path, x = None, y = None):
#        "TODO ContextMenuSelect Not Implemented"
#        pass
#        #raise NotImplementedError(
#        #    "HwndWrapper.ContextMenuSelect not implemented yet")

    #-----------------------------------------------------------
    def _menu_handle(self):
        "Simple Overridable method to get the menu handle"
        #return win32functions.GetMenu(self) # vvryabov: it doesn't work in 64-bit Python for x64 applications
        hMenu = win32gui.GetMenu(self.handle)
        is_main_menu = True
        if not hMenu:
            hMenu = self.SendMessage(self.handle, win32defines.MN_GETHMENU);
            is_main_menu = False
        return (hMenu, is_main_menu) #win32gui.GetMenu(self.handle)

    #-----------------------------------------------------------
    def Menu(self):
        "Return the menu of the control"
        hMenu, is_main_menu = self._menu_handle()
        if hMenu: # and win32functions.IsMenu(menu_hwnd):
            return Menu(self, hMenu, is_main_menu=is_main_menu)
        return None

    #-----------------------------------------------------------
    def MenuItem(self, path, exact = False):
        """Return the menu item specified by path

        Path can be a string in the form "MenuItem->MenuItem->MenuItem..."
        where each MenuItem is the text of an item at that level of the menu.
        E.g. ::

          File->Export->ExportAsPNG

        spaces are not important so you could also have written... ::

          File -> Export -> Export As PNG

        """
        if self.appdata is not None:
            menu_appdata = self.appdata['MenuItems']
        else:
            menu_appdata = None

        menu = self.Menu()
        if menu:
            return self.Menu().GetMenuPath(path, appdata = menu_appdata, exact=exact)[-1]

        raise RuntimeError("There is no menu.")

    #-----------------------------------------------------------
    def MenuItems(self):
        """Return the menu items for the dialog

        If there are no menu items then return an empty list
        """
        if self.is_dialog() and self.Menu():
            #menu_handle = win32functions.GetMenu(self)
            #self.SendMessage(win32defines.WM_INITMENU, menu_handle)
            return self.Menu().GetProperties()['MenuItems']

            #self.SendMessage(win32defines.WM_INITMENU, menu_handle)
            #return _GetMenuItems(menu_handle, self)
        else:
            return []



#    #-----------------------------------------------------------
#    def MenuClick(self, path):
#        "Select the menuitem specifed in path"
#
#        self.verify_actionable()
#
#        self.set_focus()
#
#        menu = Menu(self, self._menu_handle())
#
#        path_items = menu.GetMenuPath(path)
#
#        for menu_item in path_items:
#            if not menu_item.is_enabled():
#                raise MenuItemNotEnabled(
#                    "MenuItem '%s' is disabled"% menu_item.Text())
#
#            menu_item.Click()
#
#        return self


    #-----------------------------------------------------------
    def MenuSelect(self, path, exact = False, ):
        "Select the menuitem specified in path"

        self.verify_actionable()

        self.MenuItem(path, exact=exact).Select()


    #-----------------------------------------------------------
    def MoveWindow(
        self,
        x = None,
        y = None,
        width = None,
        height = None,
        repaint = True):
        """Move the window to the new coordinates

        * **x** Specifies the new left position of the window.
          Defaults to the current left position of the window.
        * **y** Specifies the new top position of the window.
          Defaults to the current top position of the window.
        * **width** Specifies the new width of the window. Defaults to the
          current width of the window.
        * **height** Specifies the new height of the window. Default to the
          current height of the window.
        * **repaint** Whether the window should be repainted or not.
          Defaults to True

        """

        cur_rect = self.rectangle()

        # if no X is specified - so use current coordinate
        if x is None:
            x = cur_rect.left
        else:
            try:
                y = x.top
                width = x.width()
                height = x.height()
                x = x.left
            except AttributeError:
                pass

        # if no Y is specified - so use current coordinate
        if y is None:
            y = cur_rect.top

        # if no width is specified - so use current width
        if width is None:
            width = cur_rect.width()

        # if no height is specified - so use current height
        if height is None:
            height = cur_rect.height()

        # ask for the window to be moved
        ret = win32functions.MoveWindow(self, x, y, width, height, repaint)

        # check that it worked correctly
        if not ret:
            raise ctypes.WinError()

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_movewindow_wait)


    #-----------------------------------------------------------
    def Close(self, wait_time = 0):
        """Close the window

        Code modified from http://msdn.microsoft.com/msdnmag/issues/02/08/CQA/

        """
        window_text = self.window_text()

        # tell the window it must close
        self.PostMessage(win32defines.WM_CLOSE)

        #unused var: start = time.time()
        # Keeps trying while
        #    we have not timed out and
        #    window is still a valid handle and
        #    window is still visible
        # any one of these conditions evaluates to false means the window is
        # closed or we have timed out
        def has_closed():
            return not (win32functions.IsWindow(self) and self.is_visible())

        if not wait_time:
            wait_time = Timings.closeclick_dialog_close_wait

        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        timings.WaitUntil(
            wait_time,
            Timings.closeclick_retry,
            has_closed
        )

        self.actions.log('Closed window "{0}"'.format(window_text))

    #-----------------------------------------------------------
    def Maximize(self):
        """Maximize the window"""
        win32functions.ShowWindow(self, win32defines.SW_MAXIMIZE)
        self.actions.log('Maximized window "{0}"'.format(self.window_text()))

    #-----------------------------------------------------------
    def Minimize(self):
        """Minimize the window"""
        win32functions.ShowWindow(self, win32defines.SW_MINIMIZE)
        self.actions.log('Minimized window "{0}"'.format(self.window_text()))

    #-----------------------------------------------------------
    def Restore(self):
        """Restore the window"""

        # do it twice just in case the window was minimized from being
        # maximized - because then the window would come up maximized
        # after the first ShowWindow, and Restored after the 2nd
        win32functions.ShowWindow(self, win32defines.SW_RESTORE)
        win32functions.ShowWindow(self, win32defines.SW_RESTORE)
        self.actions.log('Restored window "{0}"'.format(self.window_text()))


    #-----------------------------------------------------------
    def GetShowState(self):
        """Get the show state and Maximized/minimzed/restored state

        Returns a value that is a union of the following

        * SW_HIDE the window is hidden.
        * SW_MAXIMIZE the window is maximized
        * SW_MINIMIZE the window is minimized
        * SW_RESTORE the window is in the 'restored'
          state (neither minimized or maximized)
        * SW_SHOW The window is not hidden
        """

        wp = win32structures.WINDOWPLACEMENT()
        wp.lenght = ctypes.sizeof(wp)

        ret = win32functions.GetWindowPlacement(self, ctypes.byref(wp))

        if not ret:
            raise ctypes.WinError()

        return wp.showCmd

    #-----------------------------------------------------------
    def GetActive(self):
        """
        Return a handle to the active window within the process
        """
        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        window_thread_id, pid = win32process.GetWindowThreadProcessId(int(self.handle))
        ret = win32functions.GetGUIThreadInfo(
            window_thread_id,
            ctypes.byref(gui_info))

        if not ret:
            raise ctypes.WinError()

        hwndActive = gui_info.hwndActive
        if hwndActive:
            return HwndWrapper(hwndActive)
        else:
            return None

    #-----------------------------------------------------------
    def GetFocus(self):
        """Return the control in the process of this window that has the Focus
        """

        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        window_thread_id, pid = win32process.GetWindowThreadProcessId(self.handle)
        ret = win32functions.GetGUIThreadInfo(
            window_thread_id,
            ctypes.byref(gui_info))

        if not ret:
            return None

        return HwndWrapper(gui_info.hwndFocus)

    #-----------------------------------------------------------
    def set_focus(self):
        """
        Set the focus to this control.

        Bring the window to the foreground first if necessary.
        """
        # find the current foreground window
        cur_foreground = win32gui.GetForegroundWindow()

        # if it is already foreground then just return
        if self.handle != cur_foreground:
            # set the foreground window

            # get the thread of the window that is in the foreground
            cur_fore_thread = win32process.GetWindowThreadProcessId(
                cur_foreground)[0]

            # get the thread of the window that we want to be in the foreground
            control_thread = win32process.GetWindowThreadProcessId(
                self.handle)[0]

            # if a different thread owns the active window
            if cur_fore_thread != control_thread:
                # Attach the two threads and set the foreground window
                win32process.AttachThreadInput(control_thread,
                                               cur_fore_thread,
                                               1)

                win32gui.SetForegroundWindow(self.handle)

                # ensure foreground window has changed to the target
                # or is 0(no foreground window) before the threads detaching
                timings.WaitUntil(
                    Timings.setfocus_timeout,
                    Timings.setfocus_retry,
                    lambda: win32gui.GetForegroundWindow()
                    in [self.top_level_parent().handle, 0])

                # get the threads again to check they are still valid.
                cur_fore_thread = win32process.GetWindowThreadProcessId(
                    cur_foreground)[0]
                control_thread = win32process.GetWindowThreadProcessId(
                    self.handle)[0]

                if cur_fore_thread and control_thread:  # both are valid
                    # Detach the threads
                    win32process.AttachThreadInput(control_thread,
                                                   cur_fore_thread,
                                                   0)
            else:
                # same threads - just set the foreground window
                win32gui.SetForegroundWindow(self.handle)

            # make sure that we are idle before returning
            win32functions.WaitGuiThreadIdle(self)

            # only sleep if we had to change something!
            time.sleep(Timings.after_setfocus_wait)

        return self

    #-----------------------------------------------------------
    def SetApplicationData(self, appdata):
        """Application data is data from a previous run of the software

        It is essential for running scripts written for one spoke language
        on a different spoken language
        """
        self.appdata = appdata


    _scroll_types = {"left": {
            "line" : win32defines.SB_LINELEFT,
            "page" : win32defines.SB_PAGELEFT,
            "end" :  win32defines.SB_LEFT,
            },
        "right": {
                "line" : win32defines.SB_LINERIGHT,
                "page" : win32defines.SB_PAGERIGHT,
                "end" :  win32defines.SB_RIGHT,
            },
        "up": {
                "line" : win32defines.SB_LINEUP,
                "page" : win32defines.SB_PAGEUP,
                "end" :  win32defines.SB_TOP,
            },
        "down": {
                "line" : win32defines.SB_LINEDOWN,
                "page" : win32defines.SB_PAGEDOWN,
                "end" :  win32defines.SB_BOTTOM,
            },
        }

    #-----------------------------------------------------------
    def Scroll(self, direction, amount, count = 1, retry_interval = None):
        """Ask the control to scroll itself

        **direction** can be any of "up", "down", "left", "right"
        **amount** can be one of "line", "page", "end"
        **count** (optional) the number of times to scroll
        """

        # check which message we want to send
        if direction.lower() in ("left", "right"):
            message = win32defines.WM_HSCROLL
        elif direction.lower() in ("up", "down"):
            message = win32defines.WM_VSCROLL

        # the constant that matches direction, and how much
        scroll_type = \
            self._scroll_types[direction.lower()][amount.lower()]

        # Scroll as often as we have been asked to
        if retry_interval is None:
            retry_interval = Timings.scroll_step_wait
        while count > 0:
            self.SendMessage(message, scroll_type)
            time.sleep(retry_interval)
            count -= 1

        return self

    #-----------------------------------------------------------
    def GetToolbar(self):
        """Get the first child toolbar if it exists"""

        for child in self.children():
            if child.__class__.__name__ == 'ToolbarWrapper':
                return child

        return None

#====================================================================
def _perform_click(
        ctrl,
        button = "left",
        pressed = "",
        coords = (0, 0),
        double = False,
        button_down = True,
        button_up = True,
        absolute = False,
        ):
    "Low level method for performing click operations"

    if ctrl is None:
        ctrl = HwndWrapper(win32functions.GetDesktopWindow())
    ctrl.verify_actionable()
    ctrl_text = ctrl.window_text()

    if isinstance(coords, win32structures.RECT):
        coords = [coords.left, coords.top]
    # allow points objects to be passed as the coords
    if isinstance(coords, win32structures.POINT):
        coords = [coords.x, coords.y]
    #else:
    coords = list(coords)

    if absolute:
        coords = ctrl.client_to_screen(coords)

    # figure out the messages for click/press
    msgs  = []
    if not double:
        if button.lower() == 'left':
            if button_down:
                msgs.append(win32defines.WM_LBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_LBUTTONUP)
        elif button.lower() == 'middle':
            if button_down:
                msgs.append(win32defines.WM_MBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_MBUTTONUP)
        elif button.lower() == 'right':
            if button_down:
                msgs.append(win32defines.WM_RBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_RBUTTONUP)
        elif button.lower() == 'move':
            msgs.append(win32defines.WM_MOUSEMOVE)

    # figure out the messages for double clicking
    else:
        if button.lower() == 'left':
            msgs = (
                win32defines.WM_LBUTTONDOWN,
                win32defines.WM_LBUTTONUP,
                win32defines.WM_LBUTTONDBLCLK,
                win32defines.WM_LBUTTONUP)
        elif button.lower() == 'middle':
            msgs = (
                win32defines.WM_MBUTTONDOWN,
                win32defines.WM_MBUTTONUP,
                win32defines.WM_MBUTTONDBLCLK,
                win32defines.WM_MBUTTONUP)
        elif button.lower() == 'right':
            msgs = (
                win32defines.WM_RBUTTONDOWN,
                win32defines.WM_RBUTTONUP,
                win32defines.WM_RBUTTONDBLCLK,
                win32defines.WM_RBUTTONUP)
        elif button.lower() == 'move':
            msgs.append(win32defines.WM_MOUSEMOVE)

    # figure out the flags and pack coordinates
    flags, click_point = _calc_flags_and_coords(pressed, coords)


    #control_thread = win32functions.GetWindowThreadProcessId(ctrl, 0)
    #win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), control_thread, win32defines.TRUE)
    # TODO: check return value of AttachThreadInput properly

    # send each message
    for msg in msgs:
        win32functions.PostMessage(ctrl, msg, win32structures.WPARAM(flags), win32structures.LPARAM(click_point))
        #ctrl.PostMessage(msg, flags, click_point)
        #flags = 0

        time.sleep(Timings.sendmessagetimeout_timeout)

        # wait until the thread can accept another message
        win32functions.WaitGuiThreadIdle(ctrl)

    # detach the Python process with the process that self is in
    #win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), control_thread, win32defines.FALSE)
    # TODO: check return value of AttachThreadInput properly

    # wait a certain(short) time after the click
    time.sleep(Timings.after_click_wait)

    message = 'Clicked ' + ctrl.friendly_class_name() + ' "' + ctrl_text + \
              '" by ' + str(button) + ' button event (x,y=' + ','.join([str(coord) for coord in coords]) + ')'
    if double:
        message = 'Double-c' + message[1:]
    if button.lower() == 'move':
        message = 'Moved mouse over ' + ctrl.friendly_class_name() + ' "' + ctrl_text + \
              '" to screen point (x,y=' + ','.join([str(coord) for coord in coords]) + ') by WM_MOUSEMOVE'
    ActionLogger().log(message)



_mouse_flags = {
    "left": win32defines.MK_LBUTTON,
    "right": win32defines.MK_RBUTTON,
    "middle": win32defines.MK_MBUTTON,
    "shift": win32defines.MK_SHIFT,
    "control": win32defines.MK_CONTROL,
}

#====================================================================
def _calc_flags_and_coords(pressed, coords):
    "Calculate the flags to use and the coordinates for mouse actions"
    flags = 0

    for key in pressed.split():
        flags |= _mouse_flags[key.lower()]

    click_point = win32functions.MakeLong(coords[1], coords[0])

    return flags, click_point



#====================================================================
class _DummyControl(dict):
    "A subclass of dict so that we can assign attributes"
    pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
    "Get the properties of all the controls as a list of dictionaries"

    # wrap the dialog handle and start a new list for the
    # controls on the dialog
    try:
        controls = [hwnd, ]
        controls.extend(hwnd.children())
    except AttributeError:
        controls = [HwndWrapper(hwnd), ]

        # add all the children of the dialog
        controls.extend(controls[0].children())

    props = []

    # Add each control to the properties for this dialog
    for ctrl in controls:
        # Get properties for each control and wrap them in
        # _DummyControl so that we can assign handle
        ctrl_props = _DummyControl(ctrl.GetProperties())

        # assign the handle
        ctrl_props.handle = ctrl.handle

        # offset the rectangle from the dialog rectangle
        ctrl_props['rectangle'] -= controls[0].rectangle()

        props.append(ctrl_props)

    return props


backend.register('native', NativeElementInfo, HwndWrapper)
backend.activate('native') # default
