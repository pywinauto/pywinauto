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
import SendKeys


# I leave this optional because PIL is a large dependency
try:
    import PIL.ImageGrab
except ImportError:
    pass

from pywinauto import win32defines
from pywinauto import win32functions
from pywinauto import win32structures

from pywinauto import findbestmatch
from pywinauto import handleprops

delay_after_click = 0.0 #5
delay_after_menuselect = 0#0.05
delay_after_sendkeys_key = .01
delay_after_button_click = 0#.1
delay_before_after_close_click = .2


#====================================================================
class MenuItemNotEnabled(RuntimeError):
    "Raised when a menuitem is not enabled"
    pass

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
    "Default wrapper for controls"

    friendlyclassname = ''
    handle = None

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
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


    #-----------------------------------------------------------
    def FriendlyClassName(self):
        "Return the friendly class name for the control"
        if not self.friendlyclassname:
            return handleprops.classname(self)
        else:
            return self.friendlyclassname

    #-----------------------------------------------------------
    def Class(self):
        "Class Name of the window"
        return handleprops.classname(self)

    #-----------------------------------------------------------
    def Text(self):
        "Main text of the control"
        return handleprops.text(self)

    #-----------------------------------------------------------
    def Style(self):
        "Style of window"
        return handleprops.style(self)

    #-----------------------------------------------------------
    def ExStyle(self):
        "Extended Style of window"
        return handleprops.exstyle(self)

    #-----------------------------------------------------------
    def ControlID(self):
        "The ID of the window"
        return handleprops.controlid(self)

    #-----------------------------------------------------------
    def UserData(self):
        "Extra data associted with the window"
        return handleprops.userdata(self)

    #-----------------------------------------------------------
    def ContextHelpID(self):
        "The Context Help ID of the window"
        return handleprops.contexthelpid(self)

    #-----------------------------------------------------------
    def IsVisible(self):
        "Whether the window is visible or not"
        return handleprops.isvisible(self)

    #-----------------------------------------------------------
    def IsUnicode(self):
        "Whether the window is unicode or not"
        return handleprops.isunicode(self)

    #-----------------------------------------------------------
    def IsEnabled(self):
        "Whether the window is enabled or not"
        return handleprops.isenabled(self)

    #-----------------------------------------------------------
    def Rectangle(self):
        "Rectangle of window"
        return handleprops.rectangle(self)

    #-----------------------------------------------------------
    def ClientRect(self):
        "Client rectangle of window"
        return handleprops.clientrect(self)

    #-----------------------------------------------------------
    def Font(self):
        "The font of the window"
        return handleprops.font(self)

    #-----------------------------------------------------------
    def ProcessID(self):
        "ID of process that controls this window"
        return handleprops.processid(self)

    #-----------------------------------------------------------
    def HasStyle(self, style):
        "Retrun true if the control has the specified sytle"
        return handleprops.has_style(self, style)

    #-----------------------------------------------------------
    def HasExStyle(self, exstyle):
        "Retrun true if the control has the specified extended sytle"
        return handleprops.has_exstyle(self, exstyle)

    #-----------------------------------------------------------
    def IsDialog(self):
        "Retrun true if the control is a top level window"
        return handleprops.is_toplevel_window(self)

    #-----------------------------------------------------------
    # define the Menu Property
    def MenuItems(self):
        "Return the menu items for the dialog"
        if self.IsDialog():
            menu_handle = win32functions.GetMenu(self)
            self.SendMessage(win32defines.WM_INITMENU, menu_handle)
            return _GetMenuItems(menu_handle, self)
        else:
            return []

    #-----------------------------------------------------------
    def Parent(self):
        "Return the parent of this control"
        parent_hwnd = handleprops.parent(self)

        if parent_hwnd:
            return WrapHandle(parent_hwnd)
        else:
            return None

    #-----------------------------------------------------------
    def Texts(self):
        "Return the text for each item of this control"
        texts = [self.Text(), ]
        return texts

    #-----------------------------------------------------------
    def ClientRects(self):
        "Return the client rect for each item in this control"

        return [self.ClientRect(), ]

    #-----------------------------------------------------------
    def Fonts(self):
        "Return the font for each item in this control"
        return [self.Font(), ]

    #-----------------------------------------------------------
    def Children(self):
        "Return the children of this control"

        # this will be filled in the callback function
        child_windows = handleprops.children(self)
        return [WrapHandle(hwnd) for hwnd in child_windows]


    #-----------------------------------------------------------
    def IsChild(self, parent):
        "Return whether the window is a child of parent."

        # Call the IsChild API funciton and convert the result
        # to True/False
        return win32functions.IsChild(self.handle, parent) != 0

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
        self, message, wparam = 0 , lparam = 0, timeout = .4):
        "Send a message to the control and wait for it to return or to timeout"

        result = ctypes.c_long()
        win32functions.SendMessageTimeout(self, message, wparam, lparam,
            win32defines.SMTO_NORMAL, int(timeout * 1000), ctypes.byref(result))

        return result.value


    #-----------------------------------------------------------
    def PostMessage(self, message, wparam = 0 , lparam = 0):
        "Post a message to the control messagem queue and return"
        return win32functions.PostMessage(self, message, wparam, lparam)

        #result = ctypes.c_long()
        #ret = win32functions.SendMessageTimeout(self, message, wparam, lparam,
        #    win32defines.SMTO_NORMAL, 400, ctypes.byref(result))

        #return result.value


    #-----------------------------------------------------------
    def NotifyMenuSelect(self, menu_id):
        "Notify the dialog that one of it's menu items was selected"
        return self.SendMessageTimeout(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(0, menu_id),
            0)


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

        # get the className
        props['Class'] = self.Class()

        # set up the friendlyclass defaulting
        # to the class Name
        props['FriendlyClassName'] = self.FriendlyClassName()

        props['Texts'] = self.Texts()
        props['Style'] = self.Style()
        props['ExStyle'] = self.ExStyle()
        props['ControlID'] = self.ControlID()
        props['UserData'] = self.UserData()
        props['ContextHelpID'] = self.ContextHelpID()

        props['Fonts'] = self.Fonts()
        props['ClientRects'] = self.ClientRects()

        props['Rectangle'] = self.Rectangle()

        props['IsVisible'] =  self.IsVisible()
        props['IsUnicode'] =  self.IsUnicode()
        props['IsEnabled'] =  self.IsEnabled()

        props['MenuItems'] = self.MenuItems()

        #if self.IsVisible and self._NeedsImageProp:
        #    print "\t", self.Class
        #    props['Image'] = self.CaptureAsImage()

        #return the properties
        return props

    #-----------------------------------------------------------
    def CaptureAsImage(self):
        "Return a PIL image of the dialog"
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
        "Return true if the control handles are the same"
        if isinstance(other, HwndWrapper):
            return self.handle == other.handle
        else:
            return self.handle == other

    #-----------------------------------------------------------
    def VerifyActionable(self):
        "Verify that the control is visible and enabled"
        win32functions.WaitGuiThreadIdle(self)
        self.VerifyVisible()
        self.VerifyEnabled()


    #-----------------------------------------------------------
    def VerifyEnabled(self):
        "Verify that the control is enabled"

        # check first if it's parent is enabled
        # (as long as it is not a dialog!)
        if not self.friendlyclassname == "Dialog":
            if not self.Parent().IsEnabled():
                raise ControlNotEnabled()

        # then check if the control itself is enabled
        if not self.IsEnabled():
            raise ControlNotEnabled()

    #-----------------------------------------------------------
    def VerifyVisible(self):
        "Verify that the control is visible"

        # check first if it's parent is visible
        # (as long as it is not a dialog!)
        if not self.friendlyclassname == "Dialog":
            if not self.Parent().IsVisible():
                raise ControlNotVisible()

        # then check if the control itself is Visible
        if not self.IsVisible():
            raise ControlNotVisible()


    #-----------------------------------------------------------
    def Click(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        "Peform a click action"

        _perform_click(self, button, pressed, coords, double)
        return self

    #-----------------------------------------------------------
    def CloseClick(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        "Peform a click action that should make the window go away"

        time.sleep(delay_before_after_close_click)

        _perform_click(self, button, pressed, coords, double)

        waited = 0
        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        while (win32functions.IsWindow(self) or \
            win32functions.IsWindow(self.Parent())) and \
            waited < 1.5:

            time.sleep(.1)
            waited += .1

        time.sleep(delay_before_after_close_click)

        return self


    #-----------------------------------------------------------
    def DoubleClick(
        self, button = "left", pressed = "", coords = (0, 0), double = True):
        "Perform a double click action"
        _perform_click(self, button, pressed, coords, double)
        return self

    #-----------------------------------------------------------
    def RightClick(
        self, button = "right", pressed = "", coords = (0, 0), double = True):
        "Perform a right click action"
        _perform_click(self, button, pressed, coords, double)
        return self


    #-----------------------------------------------------------
    def PressMouse(self, button = "left", pressed = "", coords = (0, 0)):
        "Press the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)

        _perform_click(self, button, pressed, coords, button_up = False)
        return self

    #-----------------------------------------------------------
    def ReleaseMouse(self, button = "left", pressed = "", coords = (0, 0)):
        "Release the mouse button"
        #flags, click_point = _calc_flags_and_coords(pressed, coords)
        _perform_click(self, button, pressed, coords, button_down = False)
        return self

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
    def SetText(self, text, append = False):
        "Set the text of the window"

        self.VerifyActionable()

        if append:
            text = self.Text() + text

        text = ctypes.c_wchar_p(unicode(text))
        self.PostMessage(win32defines.WM_SETTEXT, 0, text)
        win32functions.WaitGuiThreadIdle(self)

        return self

    #-----------------------------------------------------------
    def TypeKeys(
        self,
        keys,
        pause = delay_after_sendkeys_key,
        with_spaces = False,
        with_tabs = False,
        with_newlines = False,
        turn_off_numlock = True):
        "Type keys to the window using SendKeys"

        self.VerifyActionable()

        # attach the Python process with the process that self is in
        win32functions.AttachThreadInput(
            win32functions.GetCurrentThreadId(), self.ProcessID(), 1)

        # make sure that the control is in the foreground
        win32functions.SetForegroundWindow(self)

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
        "Draw an outline around the window"

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
    def MenuSelect(self, path, items = None):
        "Select the menuitem specifed in path"

        self.VerifyActionable()

        # if the menu items haven't been passed in then
        # get them from the window
        if not items:
            items = self.MenuItems()

        # get the text names from the menu items
        item_texts = [item['Text'] for item in items]

        # get the first part (and remainder)
        parts = path.split("->", 1)
        current_part = parts[0]

        # find the item that best matches the current part
        item = findbestmatch.find_best_match(current_part, item_texts, items)

        # if there are more parts - then get the next level
        if parts[1:]:
            self.MenuSelect("->".join(parts[1:]), item['MenuItems'])
        else:

            # unfortunately this is not always reliable :-(
            if \
                item['State'] & win32defines.MF_DISABLED or \
                item['State'] & win32defines.MF_GRAYED:

                raise MenuItemNotEnabled("MenuItem '%s' is disabled"% path)

            #self.PostMessage(WM_MENURBUTTONUP, win32functions.GetMenu(self))
            #self.PostMessage(WM_COMMAND, 0, item['ID'])
            self.NotifyMenuSelect(item['ID'])

            win32functions.WaitGuiThreadIdle(self)

        time.sleep(delay_after_menuselect)

        return self


    #-----------------------------------------------------------
    def MoveWindow(
        self,
        x = None,
        y = None,
        width = None,
        height = None,
        repaint = True):
        """Move the window to the new coordinates"""

        cur_rect = self.Rectangle()

        # if no X is specified - so use current coordinate
        if x is None:
            x = cur_rect.left

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




#====================================================================
# TODO: Test simulating mouse clicks using SendInput instead of WM_* messages
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

        # wait until the thread can accept another message
        win32functions.WaitGuiThreadIdle(ctrl)

    # wait a certain(short) time after the click
    time.sleep(delay_after_click)


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

    click_point = win32functions.MakeLong(coords[0], coords[1])

    return flags, click_point





# should really be in win32defines - I don't know why it isnt!
#====================================================================
def _GetMenuItems(menu_handle, ctrl):
    "Get the menu items as a list of dictionaries"
    # If it doesn't have a real menu just return
    if not win32functions.IsMenu(menu_handle):
        return []

    items = []

    item_count = win32functions.GetMenuItemCount(menu_handle)

    # for each menu item
    for i in range(0, item_count):

        item_prop = {}

        # get the information on the menu Item
        menu_info  = win32structures.MENUITEMINFOW()
        menu_info.cbSize = ctypes.sizeof (menu_info)
        menu_info.fMask = \
            win32defines.MIIM_CHECKMARKS | \
            win32defines.MIIM_ID | \
            win32defines.MIIM_STATE | \
            win32defines.MIIM_SUBMENU | \
            win32defines.MIIM_TYPE #| \
            #MIIM_FTYPE #| \
            #MIIM_STRING
            #MIIM_DATA | \


        ret = win32functions.GetMenuItemInfo (
            menu_handle, i, True, ctypes.byref(menu_info))
        if not ret:
            raise ctypes.WinError()

        item_prop['Index'] = i
        item_prop['State'] = menu_info.fState
        item_prop['Type'] = menu_info.fType
        item_prop['ID'] = menu_info.wID

        # if there is text
        if menu_info.cch:
            # allocate a buffer
            buffer_size = menu_info.cch+1
            text = ctypes.create_unicode_buffer(buffer_size)

            # update the structure and get the text info
            menu_info.dwTypeData = ctypes.addressof(text)
            menu_info.cch = buffer_size
            win32functions.GetMenuItemInfo (
                menu_handle, i, True, ctypes.byref(menu_info))
            item_prop['Text'] = text.value
        else:
            item_prop['Text'] = ""

        # if it's a sub menu then get it's items
        if menu_info.hSubMenu:
            # make sure that the app updates the menu if it need to
            ctrl.SendMessage(
                win32defines.WM_INITMENUPOPUP, menu_info.hSubMenu, i)

            # get the sub menu items
            sub_menu_items = _GetMenuItems(menu_info.hSubMenu, ctrl)#, indent)

            # append them
            item_prop['MenuItems'] = sub_menu_items

        items.append(item_prop)

    return items


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




import unittest

class HwndWrapperTests(unittest.TestCase):
    "Unit tests for the TreeViewWrapper class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        # start the application
        from pywinauto.application import Application
        app = Application()

        import os.path
        path = os.path.split(__file__)[0]

        test_file = os.path.join(path, "test.txt")

        self.test_data = open(test_file, "r").read()
        # remove the BOM if it exists
        self.test_data = self.test_data.replace("\xef\xbb\xbf", "")
        self.test_data = self.test_data.decode('utf-8')

        app.start_("Notepad.exe " + test_file)

        self.app = app
        self.dlg = app.UntitledNotepad
        #self.ctrl = self.dlg.Edit.ctrl_()

        #self.dlg.MenuSelect("Styles")

        # select show selection always, and show checkboxes
        #app.ControlStyles.ListBox1.TypeKeys(
        #    "{HOME}{SPACE}" + "{DOWN}"* 12 + "{SPACE}")
        #self.app.ControlStyles.ApplyStylesSetWindowLong.Click()
        #self.app.ControlStyles.SendMessage(win32defines.WM_CLOSE)

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.MenuSelect("File->Exit")

        if self.app.Notepad.No.Exists():
            self.app.Notepad.No.Click()

    #def testText(self):
    #    "Test getting the window Text of the dialog"
    #    self.assertEquals(self.dlg.Text(), "Untitled - Notepad")

    def testText(self):
        "Test getting the window Text of the dialog"
        self.assertEquals(self.dlg.Text(), "test.txt - Notepad")

    def testClass(self):
        "Test getting the classname of the dialog"
        self.assertEquals(self.dlg.Class(), "Notepad")

    def testFriendlyClassName(self):
        "Test getting the friendly classname of the dialog"
        self.assertEquals(self.dlg.FriendlyClassName(), "Dialog")

    def testRectangle(self):
        "Test getting the rectangle of the dialog"
        rect = self.dlg.Rectangle()
        self.assertNotEqual(rect.top, None)
        self.assertNotEqual(rect.left, None)
        self.assertNotEqual(rect.bottom, None)
        self.assertNotEqual(rect.right, None)

    def testMoveWindow_same(self):
        "Test calling movewindow without any parameters"
        prevRect = self.dlg.Rectangle()
        self.dlg.MoveWindow()
        self.assertEquals(prevRect, self.dlg.Rectangle())

    def testMoveWindow(self):
        "Test moving the window"
        #prevRect = self.dlg.Rectangle()
        self.dlg.MoveWindow(150, 100, 250, 200)
        self.assertEquals(
            self.dlg.Rectangle(),
            win32structures.RECT(150, 100, 150+250, 100+200))



##====================================================================
#def _unittests():
#    "do some basic testing"
#    from pywinauto.findwindows import find_windows
#    import sys
#
#    if len(sys.argv) < 2:
#        handle = win32functions.GetDesktopWindow()
#    else:
#        try:
#            handle = int(eval(sys.argv[1]))
#
#        except ValueError:
#
#            handle = find_windows(
#                title_re = "^" + sys.argv[1],
#                class_name = "#32770",
#                visible_only = False)
#
#            if not handle:
#                print "dialog not found"
#                sys.exit()
#
#    props = GetDialogPropsFromHandle(handle)
#    print len(props)
#    #pprint(GetDialogPropsFromHandle(handle))


if __name__ == "__main__":
    unittest.main()




