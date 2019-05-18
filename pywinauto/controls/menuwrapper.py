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

"""Wrapper around Menu's and Menu items

These wrappers allow you to work easily with menu items.
You can select or click on items and check if they are
checked or unchecked.
"""
from __future__ import unicode_literals

import ctypes
import ctypes.wintypes
import time
import win32gui
import win32gui_struct
import locale
import six

from functools import wraps
from .. import win32structures
from .. import win32functions
from .. import win32defines
from .. import findbestmatch
from .. import mouse
from ..remote_memory_block import RemoteMemoryBlock
from ..timings import Timings
from .. import deprecated


class MenuItemInfo(object):

    """A holder for Menu Item Info"""

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


class MenuInfo(object):

    """A holder for Menu Info"""

    def __init__(self):
        self.dwStyle = 0
        self.cyMax = 0
        self.hbrBack = 0
        self.dwContextHelpID = 0
        self.dwMenuData = 0


class MenuItemNotEnabled(RuntimeError):

    """Raised when a menu item is not enabled"""

    pass


class MenuInaccessible(RuntimeError):

    """Raised when a menu has handle but inaccessible."""

    pass


def ensure_accessible(method):
    """Decorator for Menu instance methods"""
    @wraps(method)
    def check(instance, *args, **kwargs):
        """Check if the instance is accessible"""

        if not instance.accessible:
            raise MenuInaccessible
        else:
            return method(instance, *args, **kwargs)
    return check


class MenuItem(object):

    """Wrap a menu item"""

    def __init__(self, ctrl, menu, index, on_main_menu=False):
        """
        Initialize the menu item

        * **ctrl**	The dialog or control that owns this menu
        * **menu**	The menu that this item is on
        * **index**	The Index of this menu item on the menu
        * **on_main_menu**	True if the item is on the main menu
        """
        self._index = index
        self.menu = menu
        self.ctrl = ctrl
        self.on_main_menu = on_main_menu

    def _read_item(self):
        """Read the menu item info

        See https://msdn.microsoft.com/en-us/library/windows/desktop/ms647980.aspx
        for more information.
        """
        item_info = MenuItemInfo()
        buf, extras = win32gui_struct.EmptyMENUITEMINFO()
        win32gui.GetMenuItemInfo(self.menu.handle, self._index, True, buf)
        item_info.fType, item_info.fState, item_info.wID, item_info.hSubMenu, \
            item_info.hbmpChecked, item_info.hbmpUnchecked, item_info.dwItemData, \
            item_info.text, item_info.hbmpItem = win32gui_struct.UnpackMENUITEMINFO(buf)

        return item_info

    def friendly_class_name(self):
        """Return friendly class name"""
        return "MenuItem"
    # Non PEP-8 alias
    FriendlyClassName = deprecated(friendly_class_name)

    #def __print__(self, ctrl, menu, index):
    #    print('Menu ' + six.text_type(ctrl) + '; ' + six.text_type(menu) + '; ' + six.text_type(index))

    def rectangle(self):
        """Get the rectangle of the menu item"""
        rect = win32structures.RECT()

        if self.on_main_menu:
            ctrl = self.ctrl
        else:
            ctrl = 0

        # make it as HMENU type
        hMenu = ctypes.wintypes.HMENU(self.menu.handle)

        #(rect.left.value, rect.top.value, rect.right.value, rect.bottom.value) = \
        #    win32gui.GetMenuItemRect(ctrl.handle, self.menu.handle, self.index)
        #self.__print__(ctrl, hMenu, self.index)

        win32functions.GetMenuItemRect(
            ctrl,
            hMenu,
            self._index,
            ctypes.byref(rect))

        return rect
    # Non PEP-8 alias
    Rectangle = deprecated(rectangle)

    def index(self):
        """Return the index of this menu item"""
        return self._index
    # Non PEP-8 alias
    Index = deprecated(index)

    def state(self):
        """Return the state of this menu item"""
        return self._read_item().fState
    # Non PEP-8 alias
    State = deprecated(state)

    def item_id(self):
        """Return the ID of this menu item"""
        return self._read_item().wID
    # Non PEP-8 alias
    ID = deprecated(item_id, deprecated_name='ID')

    def item_type(self):
        """
        Return the Type of this menu item

        Main types are MF_STRING, MF_BITMAP, MF_SEPARATOR.

        See https://msdn.microsoft.com/en-us/library/windows/desktop/ms647980.aspx
        for further information.
        """
        return self._read_item().fType
    # Non PEP-8 alias
    Type = deprecated(item_type, deprecated_name='Type')

    def text(self):
        """Return the text of this menu item"""
        item_info = self._read_item()
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
            try:
                mem.Read(s, address)
                item_info.text = s.value
            except Exception:
                item_info.text = '!! non-supported owner drawn item !!'  # TODO: look into Tkinter case
            del mem
        return item_info.text
    # Non PEP-8 alias
    Text = deprecated(text)

    def sub_menu(self):
        """Return the SubMenu or None if no submenu"""
        submenu_handle = self._read_item().hSubMenu

        if submenu_handle:
            win32gui.SendMessageTimeout(self.ctrl.handle, win32defines.WM_INITMENUPOPUP,
                                        submenu_handle,
                                        self._index,
                                        win32defines.SMTO_NORMAL,
                                        0)

            return Menu(self.ctrl, submenu_handle, False, self)

        return None
    # Non PEP-8 alias
    SubMenu = deprecated(sub_menu)

    def is_enabled(self):
        """Return True if the item is enabled."""
        return not (
            self.state() & win32defines.MF_DISABLED or
            self.state() & win32defines.MF_GRAYED)
    # Non PEP-8 alias
    IsEnabled = deprecated(is_enabled)

    def is_checked(self):
        "Return True if the item is checked."
        return bool(self.state() & win32defines.MF_CHECKED)
    # Non PEP-8 alias
    IsChecked = deprecated(is_checked)

    def click_input(self):
        """
        Click on the menu item in a more realistic way

        If the menu is open it will click with the mouse event on the item.
        If the menu is not open each of it's parent's will be opened
        until the item is visible.
        """
        self.ctrl.verify_actionable()

        rect = self.rectangle()

        if not self.is_enabled():
            raise MenuItemNotEnabled(
                "MenuItem {0} is disabled".format(self.text()))

        # if the item is not visible - work up along it's parents
        # until we find an item we CAN click on
        if rect == win32structures.RECT(0, 0, 0, 0) and self.menu.owner_item:
            self.menu.owner_item.click_input()

        rect = self.rectangle()

        x_pt = int(float(rect.left + rect.right) / 2.)
        y_pt = int(float(rect.top + rect.bottom) / 2.)

        mouse.click(coords=(x_pt, y_pt))

        win32functions.WaitGuiThreadIdle(self.ctrl.handle)
        time.sleep(Timings.after_menu_wait)
    # Non PEP-8 alias
    ClickInput = deprecated(click_input)

    def select(self):
        """
        Select the menu item

        This will send a message to the parent window that the
        item was picked.
        """

        if not self.is_enabled():
            raise MenuItemNotEnabled(
                "MenuItem {0} is disabled".format(self.text()))

        #if self.state() & win32defines.MF_BYPOSITION:
        #    print self.text(), "BYPOSITION"
        #    self.ctrl.NotifyMenuSelect(self.index(), True)
        #else:

        # seems like set_focus might be messing with getting the
        # id for Popup menu items - so I calling it before set_focus
        command_id = self.item_id()

        # notify the control that a menu item was selected
        self.ctrl.set_focus()
        self.ctrl.send_message_timeout(
            self.menu.COMMAND, command_id, timeout=1.0)

        win32functions.WaitGuiThreadIdle(self.ctrl.handle)
        time.sleep(Timings.after_menu_wait)

    # _perform_click() doesn't work for MenuItem, so let's call select() method
    click = select
    # Non PEP-8 alias
    Click = deprecated(click)
    # Non PEP-8 alias
    Select = deprecated(select)

    def get_properties(self):
        """
        Return the properties for the item as a dict

        If this item opens a sub menu then call Menu.get_properties()
        to return the list of items in the sub menu. This is avialable
        under the 'menu_items' key.
        """
        props = {}
        props['index'] = self.index()
        props['state'] = self.state()
        props['item_type'] = self.item_type()
        props['item_id'] = self.item_id()
        props['text'] = self.text()

        submenu = self.sub_menu()
        if submenu:
            if submenu.accessible:
                props['menu_items'] = submenu.get_properties()
            else:
                # Submenu is attached to the item but not accessible,
                # so just mark that it exists without any additional information.
                props['menu_items'] = []

        return props
    # Non PEP-8 alias
    GetProperties = deprecated(get_properties)

    def __repr__(self):
        """Return a representation of the object as a string"""
        if six.PY3:
            return "<MenuItem " + self.text() + ">"
        else:
            return b"<MenuItem {}>".format(self.text().encode(locale.getpreferredencoding(), errors='backslashreplace'))

#    def check(self):
#        item = self._read_item()
#        item.fMask = win32defines.MIIM_STATE
#        item.fState &= win32defines.MF_CHECKED
#
#        #ret = win32functions.SetMenuItemInfo(
#        #    self.menuhandle,
#        #    self.item_id(),
#        #    0, # by position
#        #    ctypes.byref(item))
#        #
#        #if not ret:
#        #    raise ctypes.WinError()
#
#        print win32functions.CheckMenuItem(
#            self.menuhandle,
#            self.index,
#            win32defines.MF_BYPOSITION | win32defines.MF_CHECKED)
#
#        win32functions.DrawMenuBar(self.ctrl)
#
#    def uncheck(self):
#        item = self._read_item()
#        item.fMask = win32defines.MIIM_STATE
#        item.fState &= win32defines.MF_UNCHECKED
#
#        ret = win32functions.SetMenuItemInfo(
#            self.menuhandle,
#            self.item_id(),
#            0, # by position
#            ctypes.byref(item))
#
#        if not ret:
#            raise ctypes.WinError()
#
#        win32functions.DrawMenuBar(self.ctrl)
#


class Menu(object):

    """A simple wrapper around a menu handle

    A menu supports methods for querying the menu
    and getting it's menu items.
    """

    def __init__(self,
                 owner_ctrl,
                 menuhandle,
                 is_main_menu=True,
                 owner_item=None):
        """Initialize the class

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
            self.ctrl.send_message_timeout(win32defines.WM_INITMENU, self.handle)

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
    def item_count(self):
        """Return the count of items in this menu"""
        return win32gui.GetMenuItemCount(self.handle)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    @ensure_accessible
    def item(self, index, exact=False):
        """
        Return a specific menu item

        * **index** is the 0 based index or text of the menu item you want.
        * **exact** is True means exact matching for item text,
                       False means best matching.
        """
        if isinstance(index, six.string_types):
            if self.ctrl.appdata is not None:
                menu_appdata = self.ctrl.appdata['menu_items']
            else:
                menu_appdata = None
            return self.get_menu_path(index, appdata=menu_appdata, exact=exact)[-1]
        return MenuItem(self.ctrl, self, index, self.is_main_menu)
    # Non PEP-8 alias
    Item = deprecated(item)

    @ensure_accessible
    def items(self):
        "Return a list of all the items in this menu"
        items = []
        for i in range(0, self.item_count()):
            items.append(self.item(i))

        return items
    # Non PEP-8 alias
    Items = deprecated(items)

    @ensure_accessible
    def get_properties(self):
        """
        Return the properties for the menu as a list of dictionaries

        This method is actually recursive. It calls get_properties() for each
        of the items. If the item has a sub menu it will call this
        get_properties to get the sub menu items.
        """
        item_props = []

        for item in self.items():
            item_props.append(item.get_properties())

        return {'menu_items': item_props}
    # Non PEP-8 alias
    GetProperties = deprecated(get_properties)

    @ensure_accessible
    def get_menu_path(self, path, path_items=None, appdata=None, exact=False):
        """
        Walk the items in this menu to find the item specified by a path

        The path is specified by a list of items separated by '->'. Each item
        can be either a string (can include spaces) e.g. "Save As" or a zero
        based index of the item to return prefaced by # e.g. #1 or an ID of
        the item prefaced by $ specifier.

        These can be mixed as necessary. For example:
            - "#0 -> Save As",
            - "$23453 -> Save As",
            - "Tools -> #0 -> Configure"

        Text matching is done using a 'best match' fuzzy algorithm, so you don't
        have to add all punctuation, ellipses, etc.
        ID matching is performed against wID field of MENUITEMINFO structure
        (https://msdn.microsoft.com/en-us/library/windows/desktop/ms647578(v=vs.85).aspx)
        """

        if path_items is None:
            path_items = []

        # get the first part (and remainder)
        parts = [p.strip() for p in path.split("->", 1)]
        current_part = parts[0]

        if current_part.startswith("#"):
            index = int(current_part[1:])
            best_item = self.item(index)
        elif current_part.startswith("$"):
            # get the IDs from the menu items
            if appdata is None:
                item_IDs = [item.item_id() for item in self.items()]
            else:
                item_IDs = [item['item_id'] for item in appdata]

            item_id = int(current_part[1:])
            # find the item that best matches the current part
            best_item = self.item(item_IDs.index(item_id))
        else:
            # get the text names from the menu items
            if appdata is None:
                item_texts = [item.text() for item in self.items()]
            else:
                item_texts = [item['text'] for item in appdata]

            if exact:
                if current_part not in item_texts:
                    raise IndexError('There are no menu item "' + str(current_part) + '" in ' + str(item_texts))
                best_item = self.items()[item_texts.index(current_part)]
            else:
                # find the item that best matches the current part
                best_item = findbestmatch.find_best_match(
                    current_part,
                    item_texts,
                    self.items())

        path_items.append(best_item)

        # if there are more parts - then get the next level
        if parts[1:]:
            if appdata:
                appdata = appdata[best_item.index()]['menu_items']
            if best_item.sub_menu() is not None:
                best_item.sub_menu().get_menu_path(
                    "->".join(parts[1:]),
                    path_items,
                    appdata,
                    exact=exact)

        return path_items
    # Non PEP-8 alias
    GetMenuPath = deprecated(get_menu_path)

    def __repr__(self):
        """Return a simple representation of the menu"""
        return "<Menu {0}>".format(self.handle)


#    def get_properties(self):
#
#        for i in range(0, self.item_count()):
#            menu_info = self.item(self, i)[0]
#
#            item_prop['index'] = i
#            item_prop['state'] = menu_info.fState
#            item_prop['item_type'] = menu_info.fType
#            item_prop['item_id'] = menu_info.wID
#
#            else:
#                item_prop['text'] = ""
#
#            if self.IsSubMenu(i):
#                item_prop['menu_items'] = self.sub_menu(i).get_properties()
#
#            return item_prop


##====================================================================
#def _get_menu_items(menu_handle, ctrl):
#    """Get the menu items as a list of dictionaries"""
#    # If it doesn't have a real menu just return
#    if not win32functions.IsMenu(menu_handle):
#        return []
#
#
#    menu = Menu(ctrl, menu_handle)
#
#    props = []
#    for item in menu.items():
#        item_props = {}
#
#        item_prop['index'] = item.index()
#        item_prop['state'] = item.state()
#        item_prop['item_type'] = item.item_type()
#        item_prop['item_id'] = item.item_id()
#        item_prop['text'] = item.text()
#
#        props.append(item_props)
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
#            item_prop['text'] = text.value
#        else:
#            item_prop['text'] = ""
#
#        # if it's a sub menu then get it's items
#        if menu_info.hSubMenu:
#            # make sure that the app updates the menu if it need to
#            ctrl.send_message(
#                win32defines.WM_INITMENUPOPUP, menu_info.hSubMenu, i)
#
#            #ctrl.send_message(
#            #    win32defines.WM_INITMENU, menu_info.hSubMenu, )
#
#            # get the sub menu items
#            sub_menu_items = _GetMenuItems(menu_info.hSubMenu, ctrl)
#
#            # append them
#            item_prop['menu_items'] = sub_menu_items
#
#        items.append(item_prop)
#
#    return items
#    # Non PEP-8 alias
#    _GetMenuItems = deprecated(_get_menu_items)
#
