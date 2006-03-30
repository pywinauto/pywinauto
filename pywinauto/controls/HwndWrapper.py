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

"Basic wrapping of Windows controls"

__revision__ = "$Revision$"

# pylint:  disable-msg=W0611

#from pprint import pprint

import time

import ctypes

# the wrappers may be used in an environment that does not need
# the actions - as such I don't want to require sendkeys - so
# the following makes the import optional.
try:
    import SendKeys
except ImportError:
    pass


# I leave this optional because PIL is a large dependency
try:
    import PIL.ImageGrab
except ImportError:
    pass

from pywinauto import win32defines
from pywinauto import win32functions
from pywinauto import win32structures
from pywinauto.timings import Timings

#from pywinauto import findbestmatch
from pywinauto import handleprops

# also import MenuItemNotEnabled so that it is
# accessible from HwndWrapper module
from menuwrapper import Menu, MenuItemNotEnabled

#delay_after_click = 0.0 #5
#delay_after_menuselect = 0#0.05
#delay_after_sendkeys_key = .01
#delay_after_button_click = 0#.1
#delay_before_after_close_click = .2


#====================================================================
class ControlNotEnabled(RuntimeError):
    "Raised when a control is not enabled"
    pass

#====================================================================
class ControlNotVisible(RuntimeError):
    "Raised when a control is nto visible"
    pass



#====================================================================
class InvalidWindowHandle(RuntimeError):
    "Raised when an invalid handle is passed to HwndWrapper "
    def __init__(self, hwnd):
        "Initialise the RuntimError parent with the mesage"
        RuntimeError.__init__(self,
            "Handle 0x%d is not a vaild window handle"% hwnd)


#====================================================================
# just wrap the importing of WrapHandle - because it imports us
# and we import it - it can't be at the global level
def WrapHandle(hwnd):
    """Wrap a window handle

    * **hwnd** the handle of the window to wrap

    This is a simple wrapper around wraphandle.WrapHandle
    that we need to have due to import cross dependencies."""
    import wraphandle
    return wraphandle.WrapHandle(hwnd)

#
#    # Optimization - check if the control name matches exactly
#    # before trying a re.match
#    if class_name in _HwndWrappers:
#        return _HwndWrappers[class_name][1](hwnd)
#
#    for wrapper_name, (regex, class_) in _HwndWrappers.items():
#        if regex.match(class_name):
#            #print wrapper_name
#            return class_(hwnd)
#
#    # so it is not one of the 'known' classes - just wrap it with
#    # hwnd wrapper
#    wrapped_hwnd = HwndWrapper(hwnd)
#
#    # if it's not a dialog -
#    #if not isDialog:
#    #	wrapped_hwnd._NeedsImageProp = True
#
#    return wrapped_hwnd


#====================================================================
class HwndWrapper(object):
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

    friendlyclassname = ''
    handle = None

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control

        * **hwnd** is either a valid window handle or it can be an
          instance or subclass of HwndWrapper.

        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        # handle if hwnd is actually a HwndWrapper
        try:
            self.handle = hwnd.handle
        except AttributeError:
            self.handle = hwnd

        # verify that we have been passed in a valid windows handle
        if not win32functions.IsWindow(hwnd):
            raise InvalidWindowHandle(hwnd)

        # make it so that ctypes conversion happens correctly
        self._as_parameter_ = self.handle

        # specify whether we need to grab an image of ourselves
        # when asked for properties
        self._NeedsImageProp = False

        # default to not having a reference control added
        self.ref = None

        self.appdata = None

        # build the list of default properties to be written
        # Derived classes can either modify this list or override
        # GetProperties depending on how much control they need.
        self.writable_props = [
            'Class',
            'FriendlyClassName',
            'Texts',
            'Style',
            'ExStyle',
            'ControlID',
            'UserData',
            'ContextHelpID',
            'Fonts',
            'ClientRects',
            'Rectangle',
            'IsVisible',
            'IsUnicode',
            'IsEnabled',
            'MenuItems',
            'ControlCount',
            ]


    #-----------------------------------------------------------
    def FriendlyClassName(self):
        """Return the friendly class name for the control

        This differs from the class of the control in some cases.
        Class() is the actual 'Registered' window class of the control
        while FriendlyClassName() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if not self.friendlyclassname:
            return handleprops.classname(self)
        else:
            return self.friendlyclassname

    #-----------------------------------------------------------
    def Class(self):
        """Return the class name of the window"""
        return handleprops.classname(self)

    #-----------------------------------------------------------
    def WindowText(self):
        """Window text of the control

        Quite  a few contorls have other text that is visible, for example
        Edit controls usually have an empty string for WindowText but still
        have text displayed in the edit window.
        """
        return handleprops.text(self)

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
    def ControlID(self):
        """Return the ID of the window

        Only controls have a valid ID - dialogs usually have no ID assigned.

        The ID usually identified the control in the window - but there can
        be duplicate ID's for example lables in a dialog may have duplicate
        ID's.
        """
        return handleprops.controlid(self)

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
        "Return the Context Help ID of the window"
        return handleprops.contexthelpid(self)

    #-----------------------------------------------------------
    def IsUnicode(self):
        """Whether the window is unicode or not

        A window is Unicode if it was registered by the Wide char version
        of RegisterClass(Ex).
        """
        return handleprops.isunicode(self)


    #-----------------------------------------------------------
    def IsVisible(self):
        """Whether the window is visible or not

        Checks that both the Top Level Parent (probably dialog) that
        owns this window and the window itself are both visible.

        If you want to wait for a control to become visible (or wait
        for it to become hidden) use ``Application.Wait('visible')`` or
        ``Application.WaitNot('visible')``.

        If you want to raise an exception immediately if a window is
        not visible then you can use the HwndWrapper.VerifyVisible().
        HwndWrapper.VerifyActionable() raises if the window is not both
        visible and enabled.
        """

        return handleprops.isvisible(self.TopLevelParent()) and \
            handleprops.isvisible(self)

    #-----------------------------------------------------------
    def IsEnabled(self):
        """Whether the window is enabled or not

        Checks that both the Top Level Parent (probably dialog) that
        owns this window and the window itself are both enabled.

        If you want to wait for a control to become enabled (or wait
        for it to become disabled) use ``Application.Wait('visible')`` or
        ``Application.WaitNot('visible')``.

        If you want to raise an exception immediately if a window is
        not enabled then you can use the HwndWrapper.VerifyEnabled().
        HwndWrapper.VerifyReady() raises if the window is not both
        visible and enabled.
        """
        return handleprops.isenabled(self.TopLevelParent()) and \
            handleprops.isenabled(self)

    #-----------------------------------------------------------
    def Rectangle(self):
        """Return the rectangle of window

        The rectangle is the rectangle of the control on the screen,
        coordinates are given from the top left of the screen.

        This method returns a RECT structure, Which has attributes - top,
        left, right, bottom. and has methods width() and height().
        See win32structures.RECT for more information.
        """
        return handleprops.rectangle(self)

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
    def Font(self):
        """Return the font of the window

        The font of the window is used to draw the text of that window.
        It is a structure which has attributes for Font name, height, width
        etc.

        See win32structures.LOGFONTW for more information.
        """
        return handleprops.font(self)

    #-----------------------------------------------------------
    def ProcessID(self):
        """Return the ID of process that owns this window"""
        return handleprops.processid(self)

    #-----------------------------------------------------------
    def HasStyle(self, style):
        "Return True if the control has the specified sytle"
        return handleprops.has_style(self, style)

    #-----------------------------------------------------------
    def HasExStyle(self, exstyle):
        "Return True if the control has the specified extended sytle"
        return handleprops.has_exstyle(self, exstyle)

    #-----------------------------------------------------------
    def IsDialog(self):
        "Return true if the control is a top level window"
        return handleprops.is_toplevel_window(self)

    #-----------------------------------------------------------
    def Parent(self):
        """Return the parent of this control

        Note that the parent of a control is not necesarily a dialog or
        other main window. A group box may be the parent of some radio
        buttons for example.

        To get the main (or top level) window then use
        HwndWrapper.TopLevelParent().
        """
        parent_hwnd = handleprops.parent(self)

        if parent_hwnd:
            return WrapHandle(parent_hwnd)
        else:
            return None

    #-----------------------------------------------------------
    def TopLevelParent(self):
        """Return the top level window of this control

        The TopLevel parent is different from the parent in that the Parent
        is the window that owns this window - but it may not be a dialog/main
        window. For example most Comboboxes have an Edit. The ComboBox is the
        parent of the Edit control.

        This will always return a valid window handle (if the control has
        no top level parent then the control itself is returned - as it is
        a top level window already!)
        """
        if self.IsDialog():
            return self

        parent = self.Parent()

        if not parent:
            return self

        if not parent.IsDialog():
            return parent.TopLevelParent()
        else:
            return parent

    #-----------------------------------------------------------
    def Texts(self):
        """Return the text for each item of this control"

        It is a list of strings for the control. It is frequently over-ridden
        to extract all strings from a control with multiple items.

        It is always a list with one or more strings:

          * First elemtent is the window text of the control
          * Subsequent elements contain the text of any items of the
            control (e.g. items in a listbox/combobox, tabs in a tabcontrol)
        """
        texts = [self.WindowText(), ]
        return texts

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
    def Children(self):
        """Return the children of this control as a list

        It returns a list of HwndWrapper (or subclass) instances, it
        returns an empty list if there are no children.
        """

        child_windows = handleprops.children(self)
        return [WrapHandle(hwnd) for hwnd in child_windows]

    #-----------------------------------------------------------
    def ControlCount(self):
        "Return the number of children of this control"

        return len(handleprops.children(self))

    #-----------------------------------------------------------
    def IsChild(self, parent):
        """Return True if this window is a child of 'parent'.

        A window is a child of another window when it is a direct of the
        other window. A window is a direct descendant of a given
        window if the parent window is the the chain of parent windows
        for the child window.
        """

        # Call the IsChild API funciton and convert the result
        # to True/False
        return win32functions.IsChild(parent, self.handle) != 0

    #-----------------------------------------------------------
    def SendMessage(self, message, wparam = 0 , lparam = 0):
        "Send a message to the control and wait for it to return"
        return win32functions.SendMessage(self, message, wparam, lparam)

        #result = ctypes.c_long()
        #ret = win32functions.SendMessageTimeout(self, message, wparam, lparam,
        #    win32defines.SMTO_NORMAL, 400, ctypes.byref(result))

        #return result.value


    #-----------------------------------------------------------
    def SendMessageTimeout(
        self, message, wparam = 0 , lparam = 0, timeout = None):
        """Send a message to the control and wait for it to return or to timeout

        If no timeout is given then a default timeout of .4 of a second will
        be used.
        """

        if timeout is None:
            timeout = Timings.sendmessagetimeout_timeout

        result = ctypes.c_long()
        win32functions.SendMessageTimeout(self, message, wparam, lparam,
            win32defines.SMTO_NORMAL, int(timeout * 1000), ctypes.byref(result))

        return result.value


    #-----------------------------------------------------------
    def PostMessage(self, message, wparam = 0 , lparam = 0):
        "Post a message to the control message queue and return"
        return win32functions.PostMessage(self, message, wparam, lparam)

        #result = ctypes.c_long()
        #ret = win32functions.SendMessageTimeout(self, message, wparam, lparam,
        #    win32defines.SMTO_NORMAL, 400, ctypes.byref(result))

        #return result.value


    #-----------------------------------------------------------
    def NotifyMenuSelect(self, menu_id):
        """Notify the dialog that one of it's menu items was selected

        **This method is Deprecated**
        """

        import warnings
        warning_msg = "HwndWrapper.NotifyMenuSelect() is deprecated - " \
            "equivalent functionality is being moved to the MenuWrapper class."
        warnings.warn(warning_msg, DeprecationWarning)

        self.SetFocus()

        msg = win32defines.WM_COMMAND
        return self.SendMessageTimeout(
            msg,
            win32functions.MakeLong(0, menu_id), #wparam
            )


    #-----------------------------------------------------------
    def NotifyParent(self, message):
        "Send the notification message to parent of this control"

        return self.Parent().PostMessage(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(message, self.ControlID()),
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
    def CaptureAsImage(self):
        """Return a PIL image of the control

        See PIL documentation to know what you can do with the resulting
        image"""

        if not (self.Rectangle().width() and self.Rectangle().height()):
            return None

        # get the control rectangle in a way that PIL likes it
        box = (
            self.Rectangle().left,
            self.Rectangle().top,
            self.Rectangle().right,
            self.Rectangle().bottom)

        # grab the image and get raw data as a string
        # wrapped in try because PIL is optional
        try:
            return PIL.ImageGrab.grab(box)

        # if that fails due to a NameError - it is most likely because
        # PIL was not found - and the package not loaded
        except NameError:
            pass

    #-----------------------------------------------------------
    def __eq__(self, other):
        "Returns True if the handles of both controls are the same"
        if isinstance(other, HwndWrapper):
            return self.handle == other.handle
        else:
            return self.handle == other

    #-----------------------------------------------------------
    def VerifyActionable(self):
        """Verify that the control is both visible and enabled

        Raise either ControlNotEnalbed or ControlNotVisible if not
        enabled or visible respectively.
        """
        win32functions.WaitGuiThreadIdle(self)
        self.VerifyVisible()
        self.VerifyEnabled()


    #-----------------------------------------------------------
    def VerifyEnabled(self):
        """Verify that the control is enabled

        Check first if the control's parent is enabled (skip if no parent),
        then check if control itself is enabled.
        """

        # Check if the control and it's parent are enabled
        if not self.IsEnabled():
            raise ControlNotEnabled()

    #-----------------------------------------------------------
    def VerifyVisible(self):
        """Verify that the control is visible

        Check first if the control's parent is visible. (skip if no parent),
        then check if control itself is visible.
        """

        # check if the control and it's parent are visible
        if not self.IsVisible():
            raise ControlNotVisible()


    #-----------------------------------------------------------
    def Click(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        """Simulates a mouse click on the control

        This method sends WM_* messages to the control, to do a more
        'realistic' mouse click use ClickInput() which uses SendInput() API
        to perform the click.

        This method does not require that the control be visible on the screen
        (i.e. is can be hidden beneath another window and it will still work.)
        """

        _perform_click(self, button, pressed, coords, double)
        return self


    #-----------------------------------------------------------
    def ClickInput(
        self, button = "left", coords = (None, None), double = False ):
        """Click at the specified coordinates

        * **button** The mouse button to click. One of 'left', 'right',
          'middle' or 'x' (Default: 'left')
        * **coords** The coordinates to click at.(Default: center of control)
        * **double** Whether to perform a double click or not (Default: False)

        This is different from Click in that it requires the control to
        be visible on the screen but performs a more realistic 'click'
        simulation.

        This method is also vulnerable if the mouse if moved by the user
        as that could easily move the mouse off the control before the
        Click has finished.
        """
        _perform_click_input(self, button, coords, double)



    #-----------------------------------------------------------
    def CloseClick(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        """Peform a click action that should make the window go away

        The only difference from Click is that there are extra delays
        before and after the click action.
        """

        time.sleep(Timings.before_closeclick_wait)

        _perform_click(self, button, pressed, coords, double)

        start = time.time()
        timeout = Timings.closeclick_dialog_close_wait
        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        while (win32functions.IsWindow(self) or \
            win32functions.IsWindow(self.Parent())) and \
            time.time() - start < timeout:

            time.sleep(Timings.closeclick_retry)
            waited += Timings.closeclick_retry

        time.sleep(min(
            Timings.after_closeclick_wait,
            time.time() - start < timeout))

        return self


    #-----------------------------------------------------------
    def DoubleClick(
        self, button = "left", pressed = "", coords = (0, 0)):
        "Perform a double click action"
        _perform_click(self, button, pressed, coords, double = True)
        return self

    #-----------------------------------------------------------
    def DoubleClickInput(self, button = "left", coords = (None, None)):
        "Double click at the specified coordinates"
        _perform_click_input(self, button, coords, double = True)


    #-----------------------------------------------------------
    def RightClick(
        self, pressed = "", coords = (0, 0)):
        "Perform a right click action"

        _perform_click(
            self, "right", "right " + pressed, coords, button_up = False)
        _perform_click(self, "right", pressed, coords, button_down = False)
        return self

    #-----------------------------------------------------------
    def RightClickInput(self, coords = (None, None)):
        "Right click at the specified coords"
        _perform_click_input(self, 'right', coords)


    #-----------------------------------------------------------
    def PressMouse(self, button = "left", pressed = "", coords = (0, 0)):
        "Press the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)

        _perform_click(self, button, pressed, coords, button_up = False)
        return self

    #-----------------------------------------------------------
    def PressMouseInput(self, button = "left", coords = (None, None)):
        "Press a mouse button using SendInput"
        _perform_click_input(self, button, coords, button_up = False)


    #-----------------------------------------------------------
    def ReleaseMouse(self, button = "left", pressed = "", coords = (0, 0)):
        "Release the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)
        _perform_click(self, button, pressed, coords, button_down = False)
        return self

    #-----------------------------------------------------------
    def ReleaseMouseInput(self, button = "left", coords = (None, None)):
        "Release the mouse button"
        _perform_click_input(self, button, coords, button_down = False)

    #-----------------------------------------------------------
    def MoveMouse(self, pressed = "left", coords = (0, 0)):
        "Move the mouse"

        flags, click_point = _calc_flags_and_coords(pressed, coords)
        self.SendMessageTimeout(win32defines.WM_MOUSEMOVE, flags, click_point)
        win32functions.WaitGuiThreadIdle(self)

        return self

    #-----------------------------------------------------------
    def DragMouse(self,
        button = "left",
        pressed = "",
        press_coords = (0, 0),
        release_coords = (0, 0)):
        "Drag the mouse"

        self.PressMouse(button, pressed, press_coords)
        self.MoveMouse(pressed, press_coords)
        self.ReleaseMouse(button, pressed, release_coords)

        return self


    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        "Set the text of the window"

        self.VerifyActionable()

        if append:
            text = self.WindowText() + text

        text = ctypes.c_wchar_p(unicode(text))
        self.PostMessage(win32defines.WM_SETTEXT, 0, text)
        win32functions.WaitGuiThreadIdle(self)

        return self

    #-----------------------------------------------------------
    def TypeKeys(
        self,
        keys,
        pause = None,
        with_spaces = False,
        with_tabs = False,
        with_newlines = False,
        turn_off_numlock = True):
        """Type keys to the window using SendKeys

        This uses the SendKeys python module from
        http://www.rutherfurd.net/python/sendkeys/ .This is the best place
        to find documentation on what to use for the ``keys``
        """

        self.VerifyActionable()

        if pause is None:
            pause = Timings.after_sendkeys_key_wait

        self.SetFocus()

        # attach the Python process with the process that self is in
        win32functions.AttachThreadInput(
            win32functions.GetCurrentThreadId(), self.ProcessID(), 1)

        # make sure that the control is in the foreground
        win32functions.SetForegroundWindow(self)
        #win32functions.SetActiveWindow(self)


        # Play the keys to the active window
        SendKeys.SendKeys(
            keys.encode('mbcs'),
            pause, with_spaces,
            with_tabs,
            with_newlines,
            turn_off_numlock)

        # detach the python process from the window's process
        win32functions.AttachThreadInput(
            win32functions.GetCurrentThreadId(), self.ProcessID(), 0)

        win32functions.WaitGuiThreadIdle(self)
        return self

    #-----------------------------------------------------------
    def DebugMessage(self, text):
        "Write some debug text over the window"

        # don't draw if dialog is not visible

        dc = win32functions.CreateDC(u"DISPLAY", None, None, None )

        if not dc:
            raise ctypes.WinError()

        rect = self.Rectangle

        #ret = win32functions.TextOut(
        #    dc, rect.left, rect.top, unicode(text), len(text))
        ret = win32functions.DrawText(
            dc,
            unicode(text),
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
        if not self.IsVisible():
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
            rect = self.Rectangle()

        # create the pen(outline)
        pen_handle = win32functions.CreatePen(
            win32defines.PS_SOLID, thickness, colour)

        # create the brush (inside)
        brush = win32structures.LOGBRUSH()
        brush.lbStyle = fill
        brush.lbHatch = win32defines.HS_DIAGCROSS
        brush_handle = win32functions.CreateBrushIndirect(ctypes.byref(brush))

        # get the Device Context
        dc = win32functions.CreateDC(u"DISPLAY", None, None, None )

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
    def PopupWindow(self):
        """Return any owned Popups

        Please do not use in production code yet - not tested fully
        """
        popup = win32functions.GetWindow(self, win32defines.GW_HWNDNEXT)

        return popup


    #-----------------------------------------------------------
    def Owner(self):
        """Return the owner window for the window if it exists

        Returns None if there is no owner"""
        owner = win32functions.GetWindow(self, win32defines.GW_OWNER)
        if owner:
            return WrapHandle(owner)
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
        return win32functions.GetMenu(self)

    #-----------------------------------------------------------
    def Menu(self):
        "Return the menu of the control"
        return Menu(self, self._menu_handle())

    #-----------------------------------------------------------
    def MenuItem(self, path):
        """Return the menu item specifed by path

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

        return self.Menu().GetMenuPath(path, appdata = menu_appdata)[-1]


    #-----------------------------------------------------------
    def MenuItems(self):
        """Return the menu items for the dialog

        If there are no menu items then return an empty list
        """
        if self.IsDialog():
            #menu_handle = win32functions.GetMenu(self)
            #self.SendMessage(win32defines.WM_INITMENU, menu_handle)
            return self.Menu().GetProperties()

            #self.SendMessage(win32defines.WM_INITMENU, menu_handle)
            #return _GetMenuItems(menu_handle, self)
        else:
            return []



#    #-----------------------------------------------------------
#    def MenuClick(self, path):
#        "Select the menuitem specifed in path"
#
#        self.VerifyActionable()
#
#        self.SetFocus()
#
#        menu = Menu(self, self._menu_handle())
#
#        path_items = menu.GetMenuPath(path)
#
#        for menu_item in path_items:
#            if not menu_item.IsEnabled():
#                raise MenuItemNotEnabled(
#                    "MenuItem '%s' is disabled"% menu_item.Text())
#
#            menu_item.Click()
#
#        return self


    #-----------------------------------------------------------
    def MenuSelect(self, path, ):
        "Select the menuitem specifed in path"

        self.VerifyActionable()

        self.MenuItem(path).Select()


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

        cur_rect = self.Rectangle()

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

    #-----------------------------------------------------------
    #def Close(self):
    #    self.SendMessage(win32defines.WM_CLOSE)


    #-----------------------------------------------------------
    def GetFocus(self):
        """Return the control in the process of this window that has the Focus
        """

        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        ret = win32functions.GetGUIThreadInfo(
            win32functions.GetWindowThreadProcessId(self, 0),
            ctypes.byref(gui_info))

        if not ret:
            return None

        return WrapHandle(gui_info.hwndFocus)

    #-----------------------------------------------------------
    def SetFocus(self):
        """Set the focus to this control

        Bring the window to the foreground first if necessary."""

        # find the current foreground window
        cur_foreground = win32functions.GetForegroundWindow()

        # if it is already foreground then just return
        if self.handle != cur_foreground:

            # get the thread of the window that is in the foreground
            cur_fore_thread = win32functions.GetWindowThreadProcessId(
                cur_foreground, 0)

            # get the thread of the window that we want to be in the foreground
            control_thread = win32functions.GetWindowThreadProcessId(self, 0)

            # if a different thread owns the active window
            if cur_fore_thread != control_thread:
                # Attach the two threads and set the foreground window
                win32functions.AttachThreadInput(
                    cur_fore_thread, control_thread, True)

                win32functions.SetForegroundWindow(self)

                # detach the thread again
                win32functions.AttachThreadInput(
                    cur_fore_thread, control_thread, False)

            else:   # same threads - just set the foreground window
                win32functions.SetForegroundWindow(self)

            # make sure that we are idle before returning
            win32functions.WaitGuiThreadIdle(self)

            # only sleep if we had to change something!
            time.sleep(Timings.after_setfocus_wait)

        return self



    #-----------------------------------------------------------
    def SetApplicationData(self, appdata):
        """Application data is data from a previous run of the software

        It is essential for running scripts written for one spoke language
        on a different spoken langauge
        """
        self.appdata = appdata

#
#def MouseLeftClick():
#    pass
#def MouseRightClick():
#    pass
#def MouseDoubleClick():
#    pass
#def MouseDown():
#    pass
#def MouseUp():
#    pass
#def MoveMouse():
#    pass
#def DragMouse():
#    pass
#

#====================================================================
def _perform_click_input(
    ctrl = None,
    button = "left",
    coords = (None, None),
    double = False,
    button_down = True,
    button_up = True,
    absolute = False):
    """Peform a click action using SendInput

    All the *ClickInput() and *MouseInput() methods use this function.
    """

    events = []
    if button.lower() == 'left':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_LEFTDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_LEFTUP)
    elif button.lower() == 'right':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_RIGHTDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_RIGHTUP)
    elif button.lower() == 'middle':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_MIDDLEDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_MIDDLEUP)
    elif button.lower() == 'x':
        if button_down:
            events.append(win32defines.MOUSEEVENTF_XDOWN)
        if button_up:
            events.append(win32defines.MOUSEEVENTF_XUP)


    # if we were asked to double click (and we are doing a full click
    # not just up or down.
    if double and button_down and button_up:
        events *= 2


    if ctrl == None:
        ctrl = HwndWrapper(win32functions.GetDesktopWindow())


    coords = list(coords)
    # set the default coordinates
    if coords[0] is None:
        coords[0] = ctrl.Rectangle().width() / 2
    if coords[1] is None:
        coords[1] = ctrl.Rectangle().height() / 2

    if not absolute:
        coords[0] = coords[0] + ctrl.Rectangle().left
        coords[1] = coords[1] + ctrl.Rectangle().top

    # set the cursor position
    win32functions.SetCursorPos(coords[0], coords[1])
    time.sleep(Timings.after_setcursorpos_wait)

    inp_struct = win32structures.INPUT()
    inp_struct.type = win32defines.INPUT_MOUSE
    for event in events:
        inp_struct._.mi.dwFlags = event
        win32functions.SendInput(
            1,
            ctypes.pointer(inp_struct),
            ctypes.sizeof(inp_struct))

        time.sleep(Timings.after_clickinput_wait)





#====================================================================
def _perform_click(
        ctrl,
        button = "left",
        pressed = "",
        coords = (0, 0),
        double = False,
        button_down = True,
        button_up = True):
    "Low level method for performing click operations"

    ctrl.VerifyActionable()

    # figure out the messages for click/press
    msgs  = []
    if not double:
        if button.lower() == "left":
            if button_down:
                msgs.append(win32defines.WM_LBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_LBUTTONUP)

        elif button.lower() == "middle":
            if button_down:
                msgs.append(win32defines.WM_MBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_MBUTTONUP)

        elif button.lower() == "right":
            if button_down:
                msgs.append(win32defines.WM_RBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_RBUTTONUP)

    # figure out the messages for double clicking
    else:
        if button.lower() == "left":
            msgs = (
                win32defines.WM_LBUTTONDOWN,
                win32defines.WM_LBUTTONUP,
                win32defines.WM_LBUTTONDBLCLK,
                win32defines.WM_LBUTTONUP)
        elif button.lower() == "middle":
            msgs = (
                win32defines.WM_MBUTTONDOWN,
                win32defines.WM_MBUTTONUP,
                win32defines.WM_MBUTTONDBLCLK,
                win32defines.WM_MBUTTONUP)
        elif button.lower() == "right":
            msgs = (
                win32defines.WM_RBUTTONDOWN,
                win32defines.WM_RBUTTONUP,
                win32defines.WM_RBUTTONDBLCLK,
                win32defines.WM_RBUTTONUP)

    # figure out the flags and pack coordinates
    flags, click_point = _calc_flags_and_coords(pressed, coords)


    # send each message
    for msg in msgs:
        ctrl.SendMessageTimeout(msg, flags, click_point)
        #ctrl.PostMessage(msg, flags, click_point)
        #flags = 0

        # wait until the thread can accept another message
        win32functions.WaitGuiThreadIdle(ctrl)

    # wait a certain(short) time after the click
    time.sleep(Timings.after_click_wait)


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
class _dummy_control(dict):
    "A subclass of dict so that we can assign attributes"
    pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
    "Get the properties of all the controls as a list of dictionaries"

    # wrap the dialog handle and start a new list for the
    # controls on the dialog
    try:
        controls = [hwnd, ]
        controls.extend(hwnd.Children())
    except AttributeError:
        controls = [WrapHandle(hwnd), ]

        # add all the children of the dialog
        controls.extend(controls[0].Children())

    props = []

    # Add each control to the properties for this dialog
    for ctrl in controls:
        # Get properties for each control and wrap them in
        # _dummy_control so that we can assign handle
        ctrl_props = _dummy_control(ctrl.GetProperties())

        # assign the handle
        ctrl_props.handle = ctrl.handle

        # offset the rectangle from the dialog rectangle
        ctrl_props['Rectangle'] -= controls[0].Rectangle()

        props.append(ctrl_props)

    return props







