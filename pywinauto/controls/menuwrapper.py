# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2009 Mark Mc Mahon
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

"""Wrapper around Menu's and Menu items

These wrappers allow you to work easily with menu items.
You can select or click on items and check if they are
checked or unchecked.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import ctypes
import ctypes.wintypes
import time
import win32gui
import win32gui_struct
import locale

from .. import win32structures
from .. import win32functions
from .. import win32defines
from .. import findbestmatch
from .. import six
from ..RemoteMemoryBlock import RemoteMemoryBlock
#from .. import SendKeysCtypes as SendKeys
from ..timings import Timings

class MenuItemInfo:
    def __init__(self):
        self.fType = 0
        self.fState = 0
        self.wID = 0
        self.hSubMenu = 0
        self.hbmpChecked = 0
        self.hbmpUnchecked = 0
        self.dwItemData = 0
        self.text = ""
        self.hbmpItem = 0


class MenuInfo:
    def __init__(self):
        self.dwStyle = 0
        self.cyMax = 0
        self.hbrBack = 0
        self.dwContextHelpID = 0
        self.dwMenuData = 0


class MenuItemNotEnabled(RuntimeError):
    "Raised when a menu item is not enabled"
    pass


class MenuInaccessible(RuntimeError):

    """Raised when a menu has handle but inaccessible."""
    pass


def ensure_accessible(method):
    """Decorator for Menu instance methods"""

    def check(instance, *args, **kwargs):
        """Check if the instance is accessible"""

        if not instance.accessible:
            raise MenuInaccessible
        else:
            return method(instance, *args, **kwargs)
    return check


class MenuItem(object):

    """Wrap a menu item"""

    def __init__(self, ctrl, menu, index, on_main_menu = False):
        """Initialize the menu item

        * **ctrl**	The dialog or control that owns this menu
        * **menu**	The menu that this item is on
        * **index**	The Index of this menu item on the menu
        * **on_main_menu**	True if the item is on the main menu

        """
        self.index = index
        self.menu = menu
        self.ctrl = ctrl
        self.on_main_menu = on_main_menu


    def _read_item(self):
        """Read the menu item info

        See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/winui/windowsuserinterface/resources/menus/menureference/menufunctions/getmenuiteminfo.asp
        for more information."""
        
        item_info = MenuItemInfo()
        buf, extras = win32gui_struct.EmptyMENUITEMINFO()
        win32gui.GetMenuItemInfo(self.menu.handle, self.index, True, buf)
        item_info.fType, item_info.fState, item_info.wID, item_info.hSubMenu, item_info.hbmpChecked, \
        item_info.hbmpUnchecked, item_info.dwItemData, item_info.text, item_info.hbmpItem = win32gui_struct.UnpackMENUITEMINFO(buf)
        if six.PY2:
            item_info.text = item_info.text.decode(locale.getpreferredencoding())

        # OWNERDRAW case try to get string from BCMenu
        if item_info.fType & 256 and not item_info.text:
            mem = RemoteMemoryBlock(self.ctrl)
            address = item_info.dwItemData
            s = win32structures.LPWSTR()
            mem.Read(s, address)
            address = s
            s = ctypes.create_unicode_buffer(100)
            mem.Read(s, address)
            item_info.text = s.value
            del mem

        return item_info

    def FriendlyClassName(self):
        return "MenuItem"

    def __print__(self, ctrl, menu, index):
        print('Menu ' + six.text_type(ctrl) + '; ' + six.text_type(menu) + '; ' + six.text_type(index))

    def Rectangle(self):
        "Get the rectangle of the menu item"
        rect = win32structures.RECT()

        if self.on_main_menu:
            ctrl = self.ctrl
        else:
            ctrl = 0

        # make it as HMENU type
        hMenu = ctypes.wintypes.HMENU(self.menu.handle)

        #(rect.left.value, rect.top.value, rect.right.value, rect.bottom.value) = win32gui.GetMenuItemRect(ctrl.handle, self.menu.handle, self.index)
        self.__print__(ctrl, hMenu, self.index)
        
        win32functions.GetMenuItemRect(
            ctrl,
            hMenu,
            self.index,
            ctypes.byref(rect))

        return rect

    def Index(self):
        "Return the index of this menu item"
        return self.index

    def State(self):
        "Return the state of this menu item"
        return self._read_item().fState

    def ID(self):
        "Return the ID of this menu item"
        return self._read_item().wID

    def Type(self):
        """Return the Type of this menu item

        Main types are MF_STRING, MF_BITMAP, MF_SEPARATOR.

        See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/winui/windowsuserinterface/resources/menus/menureference/menustructures/menuiteminfo.asp
        for further information."""
        return self._read_item().fType

    def Text(self):
        "Return the text of this menu item"
        return self._read_item().text

    def SubMenu(self):
        "Return the SubMenu or None if no submenu"
        submenu_handle = self._read_item().hSubMenu

        if submenu_handle:
            win32gui.SendMessageTimeout(self.ctrl.handle, win32defines.WM_INITMENUPOPUP,
                                        submenu_handle,
                                        self.index,
                                        win32defines.SMTO_NORMAL,
                                        0)

            return Menu(self.ctrl, submenu_handle, False, self)

        return None

    def IsEnabled(self):
        "Return True if the item is enabled."
        return not (
            self.State() & win32defines.MF_DISABLED or
            self.State() & win32defines.MF_GRAYED)

    def IsChecked(self):
        "Return True if the item is checked."
        return bool(self.State() & win32defines.MF_CHECKED)


    def Click(self):
        """Click on the menu item

        If the menu is open this it will click with the mouse on the item.
        If the menu is not open each of it's parent's will be opened
        until the item is visible.

        """

        self.ctrl.VerifyActionable()

        rect = self.Rectangle()

        if not self.IsEnabled():
            raise MenuItemNotEnabled(
                "MenuItem '%s' is disabled"% self.Text())

        # if the item is not visible - work up along it's parents
        # until we find an item we CAN click on
        if rect == (0, 0, 0, 0):
            if self.menu.owner_item:
                self.menu.owner_item.Click()

        rect = self.Rectangle()

        x_pt = int(float(rect.left + rect.right) / 2.)
        y_pt = int(float(rect.top + rect.bottom) / 2.)

        from .HwndWrapper import _perform_click_input #, delay_after_menuselect

        _perform_click_input(
            None,
            coords = (x_pt, y_pt),
            absolute = True)

        win32functions.WaitGuiThreadIdle(self.ctrl)


    def Select(self):
        """Select the menu item

        This will send a message to the parent window that the
        item was picked
        """

        if not self.IsEnabled():
            raise MenuItemNotEnabled(
                "MenuItem '%s' is disabled"% self.Text())

        #from .HwndWrapper import delay_after_menuselect

        #if self.State() & win32defines.MF_BYPOSITION:
        #    print self.Text(), "BYPOSITION"
        #    self.ctrl.NotifyMenuSelect(self.Index(), True)
        #else:

        # seems like SetFoucs might be messing with getting the
        # id for Popup menu items - so I calling it before SetFocus
        command_id = self.ID()

        # notify the control that a menu item was selected
        self.ctrl.SetFocus()
        self.ctrl.SendMessageTimeout(
            self.menu.COMMAND, command_id, timeout=1.0)
            #win32functions.MakeLong(0, command_id))

        #self.ctrl.NotifyMenuSelect(self.ID())
        win32functions.WaitGuiThreadIdle(self.ctrl)
        time.sleep(Timings.after_menu_wait)

    def GetProperties(self):
        """Return the properties for the item as a dict

        If this item opens a sub menu then call Menu.GetProperties()
        to return the list of items in the sub menu. This is avialable
        under the 'MenuItems' key
        """
        props = {}
        props['Index'] = self.Index()
        props['State'] = self.State()
        props['Type'] = self.Type()
        props['ID'] = self.ID()
        props['Text'] = self.Text()

        submenu = self.SubMenu()
        if submenu:
            if submenu.accessible:
                props['MenuItems'] = submenu.GetProperties()
            else:
                # Submenu is attached to the item but not accessible,
                # so just mark that it exists without any additional information.
                props['MenuItems'] = []

        return props

    def __repr__(self):
        "Return a representation of the object as a string"
        if six.PY3:
            return "<MenuItem " + self.Text() + ">"
        else:
            return "<MenuItem " + self.Text().encode(locale.getpreferredencoding()) + ">"



#    def Check(self):
#        item = self._read_item()
#        item.fMask = win32defines.MIIM_STATE
#        item.fState &= win32defines.MF_CHECKED
#
##        ret = win32functions.SetMenuItemInfo(
##            self.menuhandle,
##            self.ID(),
##            0, # by position
##            ctypes.byref(item))
##
##        if not ret:
##            raise ctypes.WinError()
#
#        print win32functions.CheckMenuItem(
#            self.menuhandle,
#            self.index,
#            win32defines.MF_BYPOSITION | win32defines.MF_CHECKED)
#
#        win32functions.DrawMenuBar(self.ctrl)
#
#    def UnCheck(self):
#        item = self._read_item()
#        item.fMask = win32defines.MIIM_STATE
#        item.fState &= win32defines.MF_UNCHECKED
#
#        ret = win32functions.SetMenuItemInfo(
#            self.menuhandle,
#            self.ID(),
#            0, # by position
#            ctypes.byref(item))
#
#        if not ret:
#            raise ctypes.WinError()
#
#        win32functions.DrawMenuBar(self.ctrl)
#
#

class Menu(object):
    """A simple wrapper around a menu handle

    A menu supports methods for querying the menu
    and getting it's menu items."""
    def __init__(
        self,
        owner_ctrl,
        menuhandle,
        is_main_menu = True,
        owner_item = None):
        """Initialize the class.

        * **owner_ctrl** is the Control that owns this menu
        * **menuhandle** is the menu handle of the menu
        * **is_main_menu** we have to track whether it is the main menu
          or a popup menu
        * **owner_item** The item that contains this menu - this will be
          None for the main menu, it will be a MenuItem instance for a
          submenu.

        """
        self.ctrl = owner_ctrl
        self.handle = menuhandle
        self.is_main_menu = is_main_menu
        self.owner_item = owner_item

        self._as_parameter_ = self.handle
        self.accessible = True

        if self.is_main_menu:
            self.ctrl.SendMessageTimeout(win32defines.WM_INITMENU, self.handle)
        
        menu_info = MenuInfo()
        buf = win32gui_struct.EmptyMENUINFO()
        try:
            win32gui.GetMenuInfo(self.handle, buf)
        except win32gui.error:
            self.accessible = False
        else:
            menu_info.dwStyle, menu_info.cyMax, menu_info.hbrBack, menu_info.dwContextHelpID,\
            menu_info.dwMenuData = win32gui_struct.UnpackMENUINFO(buf)

            if menu_info.dwStyle & win32defines.MNS_NOTIFYBYPOS:
                self.COMMAND = win32defines.WM_MENUCOMMAND
            else:
                self.COMMAND = win32defines.WM_COMMAND

    @ensure_accessible
    def ItemCount(self):
        "Return the count of items in this menu"
        return win32gui.GetMenuItemCount(self.handle)

    @ensure_accessible
    def Item(self, index):
        """Return a specific menu item

        * **index** is the 0 based index of the menu item you want
        """
        return MenuItem(self.ctrl, self, index, self.is_main_menu)

    @ensure_accessible
    def Items(self):
        "Return a list of all the items in this menu"
        items = []
        for i in range(0, self.ItemCount()):
            items.append(self.Item(i))

        return items

    @ensure_accessible
    def GetProperties(self):
        """Return the properties for the menu as a list of dictionaries

        This method is actually recursive. It calls GetProperties() for each
        of the items. If the item has a sub menu it will call this
        GetProperties to get the sub menu items.
        """
        item_props = []

        for item in self.Items():
            item_props.append(item.GetProperties())

        return {'MenuItems': item_props}

    @ensure_accessible
    def GetMenuPath(self, path, path_items = None, appdata = None, exact=False):
        """Walk the items in this menu to find the item specified by path
        
        The path is specified by a list of items separated by '->' each Item
        can be either a string (can include spaces) e.g. "Save As" or the zero
        based index of the item to return prefaced by # e.g. #1. 
        
        These can be mixed as necessary. For Example:
            "#0 -> Save As", 
            "$23453 -> Save As",
            "Tools -> #0 -> Configure"
        
        Text matching is done using a 'best match' fuzzy algorithm, so you don't
        have to add all puntuation, elipses, etc.
        """

        if path_items is None:
            path_items = []

        # get the first part (and remainder)
        parts = path.split("->", 1)
        current_part = parts[0]

        if current_part.startswith("#"):
            index = int(current_part[1:])
            best_item = self.Item(index)
        elif current_part.startswith("$"):
            # get the IDs from the menu items
            if appdata is None:
                item_IDs = [item.ID() for item in self.Items()]
            else:
                item_IDs = [item['ID'] for item in appdata]

            id = int(current_part[1:])
            # find the item that best matches the current part
            best_item = self.Item(item_IDs.index(id))
        else:
            # get the text names from the menu items
            if appdata is None:
                item_texts = [item.Text() for item in self.Items()]
            else:
                item_texts = [item['Text'] for item in appdata]

            if exact:
                if current_part not in item_texts:
                    raise IndexError('There are no menu item "' + str(current_part) + '" in ' + str(item_texts))
                best_item = self.Items()[item_texts.index(current_part)]
            else:
                # find the item that best matches the current part
                best_item = findbestmatch.find_best_match(
                    current_part,
                    item_texts,
                    self.Items())

        path_items.append(best_item)


        # if there are more parts - then get the next level
        if parts[1:]:
            if appdata:
                appdata = appdata[best_item.Index()]['MenuItems']
            if best_item.SubMenu() is not None:
                best_item.SubMenu().GetMenuPath(
                    "->".join(parts[1:]),
                    path_items,
                    appdata,
                    exact=exact)

        return path_items

    def __repr__(self):
        "Return a simple representation of the menu"
        return "<Menu %d>" % self.handle


#    def GetProperties(self):
#
#        for i in range(0, self.ItemCount()):
#            menu_info = self.Item(self, i)[0]
#
#            item_prop['Index'] = i
#            item_prop['State'] = menu_info.fState
#            item_prop['Type'] = menu_info.fType
#            item_prop['ID'] = menu_info.wID
#
#            else:
#                item_prop['Text'] = ""
#
#            if self.IsSubMenu(i):
#                item_prop['MenuItems'] = self.SubMenu(i).GetProperties()
#
#            return item_prop


##====================================================================
#def _GetMenuItems(menu_handle, ctrl):
#    "Get the menu items as a list of dictionaries"
#    # If it doesn't have a real menu just return
#    if not win32functions.IsMenu(menu_handle):
#        return []
#
#
#    menu = Menu(ctrl, menu_handle)
#
#    props = []
#    for item in menu.Items():
#        item_props = {}
#
#        item_prop['Index'] = item.Index()
#        item_prop['State'] = item.State()
#        item_prop['Type'] = item.Type()
#        item_prop['ID'] = item.ID()
#        item_prop['Text'] = item.Text()
#
#        props.append(item_props)
#
#
#
#
#
#
#
#    items = []
#
#
#    # for each menu item
#    for i in range(0, item_count):
#
#        item_prop = {}
#
#        # get the information on the menu Item
#        menu_info  = win32structures.MENUITEMINFOW()
#        menu_info.cbSize = ctypes.sizeof (menu_info)
#        menu_info.fMask = \
#            win32defines.MIIM_CHECKMARKS | \
#            win32defines.MIIM_ID | \
#            win32defines.MIIM_STATE | \
#            win32defines.MIIM_SUBMENU | \
#            win32defines.MIIM_TYPE #| \
#            #MIIM_FTYPE #| \
#            #MIIM_STRING
#            #MIIM_DATA | \
#
#
#        ret = win32functions.GetMenuItemInfo (
#            menu_handle, i, True, ctypes.byref(menu_info))
#        if not ret:
#            raise ctypes.WinError()
#
#        # if there is text
#        if menu_info.cch:
#            # allocate a buffer
#            buffer_size = menu_info.cch+1
#            text = ctypes.create_unicode_buffer(buffer_size)
#
#            # update the structure and get the text info
#            menu_info.dwTypeData = ctypes.addressof(text)
#            menu_info.cch = buffer_size
#            win32functions.GetMenuItemInfo (
#                menu_handle, i, True, ctypes.byref(menu_info))
#            item_prop['Text'] = text.value
#        else:
#            item_prop['Text'] = ""
#
#        # if it's a sub menu then get it's items
#        if menu_info.hSubMenu:
#            # make sure that the app updates the menu if it need to
#            ctrl.SendMessage(
#                win32defines.WM_INITMENUPOPUP, menu_info.hSubMenu, i)
#
#            #ctrl.SendMessage(
#            #    win32defines.WM_INITMENU, menu_info.hSubMenu, )
#
#            # get the sub menu items
#            sub_menu_items = _GetMenuItems(menu_info.hSubMenu, ctrl)
#
#            # append them
#            item_prop['MenuItems'] = sub_menu_items
#
#        items.append(item_prop)
#
#    return items
#


