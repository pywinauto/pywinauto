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

import ctypes

# I leave this optional because PIL is a large dependency
try:
    import PIL.ImageGrab
except ImportError:
    pass

from pywinauto import win32defines
from pywinauto import win32functions
from pywinauto import win32structures

from pywinauto import handleprops



#====================================================================
class InvalidWindowHandle(RuntimeError):
    "Raised when an invalid handle is passed to HwndWrapper "
    def __init__(self, hwnd):
        "Initialise the RuntimError parent with the mesage"
        RuntimeError.__init__(self,
            "Handle 0x%d is not a vaild window handle"% hwnd)




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

        # set the friendly class name to default to
        # the class name
        self._extra_texts = []
        self._extra_clientrects = []
        self._extra_props = {}

        self._extra_props['MenuItems'] = self.MenuItems

        # if it is a main window
        #if self.IsDialog:
        #	self.FriendlyClassName = "Dialog"

        # default to not having a reference control added
        self.ref = None


    FriendlyClassName = property(
        handleprops.friendlyclassname,
        doc = "FriendlyClassName of the window ")

    #-----------------------------------------------------------
    #def _get_classname(self):
    #    try:
    #        return self._class_name
    #    except AttributeError:
    #        return handleprops.classname(self)

    Class = property (handleprops.classname,
        doc = "Class Name of the window")

    Text = property (handleprops.text,
        doc = "Main text of the control")
    Style = property (handleprops.style,
        doc = "Style of window")
    ExStyle = property (handleprops.exstyle,
        doc = "Extended Style of window")
    ControlID = property (handleprops.controlid,
        doc = "The ID of the window")
    UserData = property (handleprops.userdata,
        doc = "Extra data associted with the window")
    ContextHelpID = property (handleprops.contexthelpid,
        doc = "The Context Help ID of the window")
    IsVisible = property (handleprops.isvisible,
        doc = "Whether the window is visible or not")
    IsUnicode = property (handleprops.isunicode,
        doc = "Whether the window is unicode or not")
    IsEnabled = property (handleprops.isenabled,
        doc = "Whether the window is enabled or not")

    Rectangle = property (handleprops.rectangle,
        doc = "Rectangle of window")
    ClientRect = property (handleprops.clientrect,
        doc = "Client rectangle of window")

    Font = property (handleprops.font, doc = "The font of the window")

    ProcessID = property (handleprops.processid,
        doc = "ID of process that controls this window")

    HasStyle = handleprops.has_style
    HasExStyle = handleprops.has_exstyle

    IsDialog = property(handleprops.is_toplevel_window,
        doc = handleprops.is_toplevel_window.__doc__)

    #-----------------------------------------------------------
    # define the Menu Property
    def _get_menuitems(self):
        "Return the menu items for the dialog"
        if self.IsDialog:
            return _GetMenuItems(win32functions.GetMenu(self))
        else:
            return []
    MenuItems = property (_get_menuitems,
        doc = "Return the menu items for the dialog")

    #-----------------------------------------------------------
    def _get_parent(self):
        "Return the parent of this control"
        parent_hwnd = handleprops.parent(self)
        if parent_hwnd:
            return HwndWrapper(parent_hwnd)
        else:
            return None
    Parent = property (_get_parent,
        doc = "Parent window of window")

    #-----------------------------------------------------------
    # TODO: Make _extra_texts a property/method of the class
    # rather then a property that is set at initialization
    def _get_texts(self):
        "Return the text for each item of this control"
        texts = [self.Text, ]
        texts.extend(self._extra_texts)
        return texts
    Texts = property (_get_texts, doc = "All text items of the control")

    #-----------------------------------------------------------
    # TODO: Make _extra_clientrects a property/method of the class
    # rather then a property that is set at initialization
    def _get_clientrects(self):
        "Return the client rect for each item in this control"

        clientrects = [self.ClientRect, ]
        clientrects.extend(self._extra_clientrects)
        return clientrects
    ClientRects = property (
        _get_clientrects, doc = "All client rectanbgles of the control")

    #-----------------------------------------------------------
    def _get_Fonts(self):
        "Return the font for each item in this control"
        return [self.Font, ]
    Fonts = property (_get_Fonts, doc = "All fonts of the control")

    #-----------------------------------------------------------
    def _get_children(self):
        "Return the children of this control"

        from wraphandle import WrapHandle
        # this will be filled in the callback function
        child_windows = handleprops.children(self)
        return [WrapHandle(hwnd) for hwnd in child_windows]

    Children = property (_get_children, doc = "The list of children")

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

    #-----------------------------------------------------------
    def PostMessage(self, message, wparam = 0 , lparam = 0):
        "Post a message to the control messagem queue and return"
        return win32functions.PostMessage(self, message, wparam, lparam)

    #-----------------------------------------------------------
    def NotifyMenuSelect(self, menu_id):
        "Notify the dialog that one of it's menu items was selected"
        return self.PostMessage(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(menu_id, 0),
            0)


    #-----------------------------------------------------------
    def NotifyParent(self, message):
        "Send the notification message to parent of this control"

        return self.Parent.PostMessage(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(self.ControlID, message),
            self)

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = self._extra_props

        # get the className
        props['Class'] = self.Class

        # set up the friendlyclass defaulting
        # to the class Name
        props['FriendlyClassName'] = self.FriendlyClassName

        props['Texts'] = self.Texts
        props['Style'] = self.Style
        props['ExStyle'] = self.ExStyle
        props['ControlID'] = self.ControlID
        props['UserData'] = self.UserData
        props['ContextHelpID'] = self.ContextHelpID

        props['Fonts'] = self.Fonts
        props['ClientRects'] = self.ClientRects

        props['Rectangle'] = self.Rectangle

        props['IsVisible'] =  self.IsVisible
        props['IsUnicode'] =  self.IsUnicode
        props['IsEnabled'] =  self.IsEnabled

        #props['MenuItems'] = []

        #if self.IsVisible and self._NeedsImageProp:
        #    print "\t", self.Class
        #    props['Image'] = self.CaptureAsImage()

        #return the properties
        return props

    #-----------------------------------------------------------
    def CaptureAsImage(self):
        "Return a PIL image of the dialog"
        if not (self.Rectangle.width() and self.Rectangle.height()):
            return None

        # get the control rectangle in a way that PIL likes it
        box = (
            self.Rectangle.left,
            self.Rectangle.top,
            self.Rectangle.right,
            self.Rectangle.bottom)

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



# should really be in win32defines - I don't know why it isnt!
_MIIM_STRING = 0x40
#====================================================================
def _GetMenuItems(menuHandle):
    "Get the menu items as a list of dictionaries"
    # If it doesn't have a real menu just return
    if not win32functions.IsMenu(menuHandle):
        return []

    items = []

    itemCount = win32functions.GetMenuItemCount(menuHandle)

    # for each menu item
    for i in range(0, itemCount):

        itemProp = {}

        # get the information on the menu Item
        menuInfo  = win32structures.MENUITEMINFOW()
        menuInfo.cbSize = ctypes.sizeof (menuInfo)
        menuInfo.fMask = \
            win32defines.MIIM_CHECKMARKS | \
            win32defines.MIIM_ID | \
            win32defines.MIIM_STATE | \
            win32defines.MIIM_SUBMENU | \
            win32defines.MIIM_TYPE #| \
            #MIIM_FTYPE #| \
            #MIIM_STRING
            #MIIM_DATA | \


        ret = win32functions.GetMenuItemInfo (
            menuHandle, i, True, ctypes.byref(menuInfo))
        if not ret:
            raise ctypes.WinError()

        itemProp['Index'] = i
        itemProp['State'] = menuInfo.fState
        itemProp['Type'] = menuInfo.fType
        itemProp['ID'] = menuInfo.wID

        # if there is text
        if menuInfo.cch:
            # allocate a buffer
            bufferSize = menuInfo.cch+1
            text = (ctypes.c_wchar * bufferSize)()

            # update the structure and get the text info
            menuInfo.dwTypeData = ctypes.addressof(text)
            menuInfo.cch = bufferSize
            win32functions.GetMenuItemInfo (
                menuHandle, i, True, ctypes.byref(menuInfo))
            itemProp['Text'] = text.value
        else:
            itemProp['Text'] = ""

        # if it's a sub menu then get it's items
        if menuInfo.hSubMenu:
            subMenuItems = _GetMenuItems(menuInfo.hSubMenu)#, indent)
            itemProp['MenuItems'] = subMenuItems

        items.append(itemProp)

    return items


#====================================================================
class _dummy_control(dict):
    "A subclass of dict so that we can assign attributes"
    pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
    "Get the properties of all the controls as a list of dictionaries"

    from wraphandle import WrapHandle
    # wrap the dialog handle and start a new list for the
    # controls on the dialog
    try:
        controls = [hwnd, ]
        controls.extend(hwnd.Children)
    except AttributeError:
        controls = [WrapHandle(hwnd, True), ]

        # add all the children of the dialog
        controls.extend(controls[0].Children)

    props = []

    # Add each control to the properties for this dialog
    for ctrl in controls:
        # Get properties for each control and wrap them in
        # _dummy_control so that we can assign handle
        ctrl_props = _dummy_control(ctrl.GetProperties())

        # assign the handle
        ctrl_props.handle = ctrl.handle

        # offset the rectangle from the dialog rectangle
        ctrl_props['Rectangle'] -= controls[0].Rectangle

        props.append(ctrl_props)

    return props



#====================================================================
def _unittests():
    "do some basic testing"
    from pywinauto.findwindows import find_windows
    import sys

    if len(sys.argv) < 2:
        handle = win32functions.GetDesktopWindow()
    else:
        try:
            handle = int(eval(sys.argv[1]))

        except ValueError:

            handle = find_windows(
                title_re = "^" + sys.argv[1],
                class_name = "#32770",
                visible_only = False)

            if not handle:
                print "dialog not found"
                sys.exit()

    props = GetDialogPropsFromHandle(handle)
    print len(props)
    #pprint(GetDialogPropsFromHandle(handle))


if __name__ == "__main__":
    _unittests()




