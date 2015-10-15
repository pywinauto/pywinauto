# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
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
"""
Classes that wrap the Windows Common controls

.. implicitly document some private classes
.. autoclass:: _toolbar_button
   :members:
   :show-inheritance:

.. autoclass:: _treeview_element
   :members:
   :show-inheritance:

.. autoclass:: _listview_item
   :members:
   :show-inheritance:
"""


from __future__ import absolute_import
from __future__ import print_function

import time
import ctypes
import warnings
import locale

from .. import six
from .. import win32functions
from .. import win32defines
from .. import win32structures
from .. import findbestmatch
from ..RemoteMemoryBlock import RemoteMemoryBlock
from . import HwndWrapper

from ..timings import Timings


# Todo: I should return iterators from things like Items() and Texts()
#       to save building full lists all the time
# Todo: ListViews should be based off of GetItem, and then have actions
#       Applied to that e.g. ListView.Item(xxx).Select(), rather then
#       ListView.Select(xxx)
#       Or at least most of the functions should call GetItem to get the
#       Item they want to work with.

class _listview_item(object):
    "Wrapper around ListView items"
    #----------------------------------------------------------------
    def __init__(self, lv_ctrl, item_index, subitem_index = 0):
        "Initialize the item"
        self.listview_ctrl = lv_ctrl
        
        # ensure the item_index is an integer or
        # convert it to one
        self.item_index = self.listview_ctrl._as_item_index(item_index)
        self.subitem_index = subitem_index
        #self._as_parameter_ = self.item_index

    #----------------------------------------------------------------
    def _readitem(self):
        "Read the list view item"

        # set up a memory block in the remote application
        remote_mem = RemoteMemoryBlock(self.listview_ctrl)

        # set up the item structure to get the text
        item = self.listview_ctrl.LVITEM()
        item.mask = \
            win32defines.LVIF_TEXT | \
            win32defines.LVIF_IMAGE | \
            win32defines.LVIF_INDENT | \
            win32defines.LVIF_STATE

        item.iItem = self.item_index
        item.iSubItem = self.subitem_index
        item.stateMask = win32structures.UINT(-1)

        item.cchTextMax = 2000
        item.pszText = remote_mem.Address() + \
            ctypes.sizeof(item) + 1

        # Write the local LVITEM structure to the remote memory block
        remote_mem.Write(item)

        # Fill in the requested item
        retval = self.listview_ctrl.SendMessage(
            self.listview_ctrl.LVM_GETITEM,
            0, # MSDN: wParam for LVM_GETITEM must be zero
            remote_mem)

        text = ''
        # if it succeeded
        if retval:

            remote_mem.Read(item)

            # Read the remote text string
            char_data = self.listview_ctrl.create_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            text = self.listview_ctrl.text_decode(char_data.value)

        else:
            raise RuntimeError(
                "We should never get to this part of ListView.GetItem(), retval = " + str(retval) +
                ', GetLastError() = ' + str(ctypes.GetLastError()) +
                ', item_index = ' + str(self.item_index) + ', subitem_index = ' + str(self.subitem_index))

        del remote_mem

        return item, text

    #----------------------------------------------------------------
    def __getitem__(self, key):
        "Return property name"
        warnings.warn('ListView item properties "text", "state", "image" and "indent" are deprecated! ' +
                      'Use methods Text(), State(), Image() and Indent().', DeprecationWarning)
        
        item, text = self._readitem()
        if key == 'text':
            return text
        if key == 'state':
            return item.state
        if key == 'image':
            return item.iImage
        if key == 'indent':
            return item.iIndent
        
        raise KeyError('Incorrect property: "' + str(key) + '", can be "text", "state", "image" or "indent".')

    #----------------------------------------------------------------
    def Text(self):
        "Return the text of the item"
        return self._readitem()[1]

    #----------------------------------------------------------------
    def Item(self):
        "Return the item itself (LVITEM instance)"
        return self._readitem()[0]

    #----------------------------------------------------------------
    def ItemData(self):
        "Return the item data (dictionary)"
        item_data = {}
        
        item, text = self._readitem()
        # and add it to the titles
        item_data['text'] = text
        item_data['state'] = item.state
        item_data['image'] = item.iImage
        item_data['indent'] = item.iIndent
        
        return item_data

    #----------------------------------------------------------------
    def State(self):
        "Return the state of the item"
        return self.Item().state

    #----------------------------------------------------------------
    def Image(self):
        "Return the image index of the item"
        return self.Item().iImage

    #----------------------------------------------------------------
    def Indent(self):
        "Return the indent of the item"
        return self.Item().iIndent

    #----------------------------------------------------------------
    def Rectangle(self, area = "all"):
        """Return the rectangle of the item.

        Possible ``area`` values:

        * ``"all"``  Returns the bounding rectangle of the entire item, including the icon and label.
        * ``"icon"``  Returns the bounding rectangle of the icon or small icon.
        * ``"text"``  Returns the bounding rectangle of the item text.
        * ``"select"``  Returns the union of the "icon" and "text" rectangles, but excludes columns in report view.
        """
        # set up a memory block in the remote application
        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        rect = win32structures.RECT()

        if area.lower() == "all" or not area:
            rect.left = win32defines.LVIR_BOUNDS
        elif area.lower() == "icon":
            rect.left = win32defines.LVIR_ICON
        elif area.lower() == "text":
            rect.left = win32defines.LVIR_LABEL
        elif area.lower() == "select":
            rect.left = win32defines.LVIR_SELECTBOUNDS
        else:
            raise ValueError('Incorrect rectangle area of the list view item: "' + str(area) + '"')

        # Write the local RECT structure to the remote memory block
        remote_mem.Write(rect)

        # Fill in the requested item
        retval = self.listview_ctrl.SendMessage(
            win32defines.LVM_GETITEMRECT,
            self.item_index,
            remote_mem)

        # if it succeeded
        if not retval:
            del remote_mem
            raise RuntimeError("Did not succeed in getting rectangle")

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect

    #----------------------------------------------------------------
    def Click(self, button = "left", double = False, where = "text", pressed = ""):
        """Click on the list view item

        where can be any one of "all", "icon", "text", "select", "check"
        defaults to "text"
        """

        if where.lower() != "check":
            point_to_click = self.Rectangle(area=where.lower()).mid_point()
            self.listview_ctrl.Click(
                button,
                coords = (point_to_click.x, point_to_click.y),
                double = double,
                pressed = pressed)
        else:
            """
            Click on checkbox
            """
            point_to_click = self.Rectangle(area="icon").mid_point()
            point_to_click.y = self.Rectangle(area="icon").bottom - 3
            # Check ListView display mode
            # (to be able to process 'Full Row Details' mode separately
            remote_mem = RemoteMemoryBlock(self.listview_ctrl)
            hittest = win32structures.LVHITTESTINFO()
            hittest.pt = point_to_click
            # Actually, there is no need to set hittest.iItem, because
            # SendMessage followed by remote_mem.Read always refreshes it
            #hittest.iItem = self.item_index
            hittest.iSubItem = self.subitem_index
            remote_mem.Write(hittest)
            self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
            remote_mem.Read(hittest)

            # Hittest flag
            checkbox_found = False
            if hittest.flags == win32defines.LVHT_ONITEMICON:
                """
                Large Icons, Small Icons, List, Details
                """
                while not checkbox_found and point_to_click.x > 0:
                    point_to_click.x -= 1

                    hittest = win32structures.LVHITTESTINFO()
                    hittest.pt = point_to_click
                    #hittest.iItem = self.item_index
                    hittest.iSubItem = self.subitem_index
                    remote_mem.Write(hittest)
                    self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
                    remote_mem.Read(hittest)

                    if hittest.flags == win32defines.LVHT_ONITEMSTATEICON:
                        checkbox_found = True
                        break

            elif hittest.flags == win32defines.LVHT_ONITEM:
                """
                Full Row Details
                """
                warnings.warn("Full Row Details 'check' area is detected in experimental mode. Use carefully!")
                point_to_click.x = self.Rectangle(area="icon").left - 8
                # Check if point_to_click is still on item
                hittest = win32structures.LVHITTESTINFO()
                hittest.pt = point_to_click
                #hittest.iItem = self.item_index
                hittest.iSubItem = self.subitem_index
                remote_mem.Write(hittest)
                self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if hittest.flags == win32defines.LVHT_ONITEM:
                    checkbox_found = True
            else:
                raise RuntimeError("Unexpected hit test flags value " + str(hittest.flags) + " trying to find checkbox")

            # Click on the found checkbox
            if checkbox_found:
                self.listview_ctrl.Click(
                    button,
                    coords = (point_to_click.x, point_to_click.y),
                    double = double,
                    pressed = pressed)
            else:
                raise RuntimeError("Area ('check') not found for this list view item")

    #----------------------------------------------------------------
    def ClickInput(self, button = "left", double = False, wheel_dist = 0, where = "text", pressed = ""):
        """Click on the list view item

        where can be any one of "all", "icon", "text", "select", "check"
        defaults to "text"
        """

        if where.lower() != "check":
            point_to_click = self.Rectangle(area=where.lower()).mid_point()
            self.listview_ctrl.ClickInput(
                button,
                coords = (point_to_click.x, point_to_click.y),
                double = double,
                wheel_dist = wheel_dist,
                pressed = pressed)
        else:
            """
            Click on checkbox
            """
            point_to_click = self.Rectangle(area="icon").mid_point()
            point_to_click.y = self.Rectangle(area="icon").bottom - 3
            # Check ListView display mode
            # (to be able to process 'Full Row Details' mode separately
            remote_mem = RemoteMemoryBlock(self.listview_ctrl)
            hittest = win32structures.LVHITTESTINFO()
            hittest.pt = point_to_click
            # Actually, there is no need to set hittest.iItem, because
            # SendMessage followed by remote_mem.Read always refreshes it
            #hittest.iItem = self.item_index
            hittest.iSubItem = self.subitem_index
            remote_mem.Write(hittest)
            self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
            remote_mem.Read(hittest)

            # Hittest flag
            checkbox_found = False
            if hittest.flags == win32defines.LVHT_ONITEMICON:
                """
                Large Icons, Small Icons, List, Details
                """
                while not checkbox_found and point_to_click.x > 0:
                    point_to_click.x -= 1

                    hittest = win32structures.LVHITTESTINFO()
                    hittest.pt = point_to_click
                    #hittest.iItem = self.item_index
                    hittest.iSubItem = self.subitem_index
                    remote_mem.Write(hittest)
                    self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
                    remote_mem.Read(hittest)

                    if hittest.flags == win32defines.LVHT_ONITEMSTATEICON:
                        checkbox_found = True
                        break

            elif hittest.flags == win32defines.LVHT_ONITEM:
                """
                Full Row Details
                """
                warnings.warn("Full Row Details 'check' area is detected in experimental mode. Use carefully!")
                point_to_click.x = self.Rectangle(area="icon").left - 8
                # Check if point_to_click is still on item
                hittest = win32structures.LVHITTESTINFO()
                hittest.pt = point_to_click
                #hittest.iItem = self.item_index
                hittest.iSubItem = self.subitem_index
                remote_mem.Write(hittest)
                self.listview_ctrl.SendMessage(win32defines.LVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if hittest.flags == win32defines.LVHT_ONITEM:
                    checkbox_found = True
            else:
                raise RuntimeError("Unexpected hit test flags value " + str(hittest.flags) + " trying to find checkbox")

            # Click on the found checkbox
            if checkbox_found:
                self.listview_ctrl.ClickInput(
                    button,
                    coords = (point_to_click.x, point_to_click.y),
                    double = double,
                    wheel_dist = wheel_dist,
                    pressed = pressed)
            else:
                raise RuntimeError("Area ('check') not found for this list view item")

    #----------------------------------------------------------------
    def EnsureVisible(self):
        "Make sure that the ListView item is visible"
        if self.State() & win32defines.LVS_NOSCROLL:
            return False # scroll is disabled
        ret = self.listview_ctrl.SendMessage(
            win32defines.LVM_ENSUREVISIBLE,
            self.item_index,
            win32defines.FALSE)
        if ret != win32defines.TRUE:
            raise RuntimeError('Fail to make the list view item visible ' +
                               '(item_index = ' + str(self.item_index) + ')')

    #-----------------------------------------------------------
    def UnCheck(self):
        "Uncheck the ListView item"

        def INDEXTOSTATEIMAGEMASK(i):
            return i << 12

        self.listview_ctrl.VerifyActionable()

        lvitem = self.listview_ctrl.LVITEM()

        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)
        lvitem.state = win32structures.UINT(INDEXTOSTATEIMAGEMASK(1)) #win32structures.UINT(0x1000)
        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_STATEIMAGEMASK)

        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem)

        retval = self.listview_ctrl.SendMessage(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        del remote_mem

    #-----------------------------------------------------------
    def Check(self):
        "Check the ListView item"

        def INDEXTOSTATEIMAGEMASK(i):
            return i << 12

        self.listview_ctrl.VerifyActionable()

        lvitem = self.listview_ctrl.LVITEM()

        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)
        lvitem.state = win32structures.UINT(INDEXTOSTATEIMAGEMASK(2)) #win32structures.UINT(0x2000)
        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_STATEIMAGEMASK)

        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem)

        retval = self.listview_ctrl.SendMessage(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        del remote_mem

    #-----------------------------------------------------------
    def IsChecked(self):
        "Return whether the ListView item is checked or not"

        state = self.listview_ctrl.SendMessage(
            win32defines.LVM_GETITEMSTATE,
            self.item_index,
            win32defines.LVIS_STATEIMAGEMASK)

        return state & 0x2000 == 0x2000

    #-----------------------------------------------------------
    def IsSelected(self):
        "Return True if the item is selected"

        return win32defines.LVIS_SELECTED == self.listview_ctrl.SendMessage(
            win32defines.LVM_GETITEMSTATE, self.item_index, win32defines.LVIS_SELECTED)

    #-----------------------------------------------------------
    def IsFocused(self):
        "Return True if the item has the focus"

        return win32defines.LVIS_FOCUSED == self.listview_ctrl.SendMessage(
            win32defines.LVM_GETITEMSTATE, self.item_index, win32defines.LVIS_FOCUSED)

    #-----------------------------------------------------------
    def _modify_selection(self, to_select):
        """Change the selection of the item

        to_select should be True to select the item and false
        to deselect the item
        """

        self.listview_ctrl.VerifyActionable()

        if self.item_index >= self.listview_ctrl.ItemCount():
            raise IndexError("There are only %d items in the list view not %d"%
                (self.listview_ctrl.ItemCount(), self.item_index + 1))

        # first we need to change the state of the item
        lvitem = self.listview_ctrl.LVITEM()
        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)

        if to_select:
            lvitem.state = win32structures.UINT(win32defines.LVIS_FOCUSED | win32defines.LVIS_SELECTED)

        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_FOCUSED | win32defines.LVIS_SELECTED)
        
        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem, size=ctypes.sizeof(lvitem))

        retval = self.listview_ctrl.SendMessage(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)
        if retval != win32defines.TRUE:
            raise ctypes.WinError()#('retval = ' + str(retval))
        del remote_mem

        # now we need to notify the parent that the state has changed
        nmlv = win32structures.NMLISTVIEW()
        nmlv.hdr.hwndFrom = self.listview_ctrl.handle
        nmlv.hdr.idFrom = self.listview_ctrl.ControlID()
        nmlv.hdr.code = win32defines.LVN_ITEMCHANGING

        nmlv.iItem = self.item_index
        #nmlv.iSubItem = 0
        nmlv.uNewState = win32defines.LVIS_SELECTED
        #nmlv.uOldState = 0
        nmlv.uChanged = win32defines.LVIS_SELECTED
        nmlv.ptAction = win32structures.POINT()

        new_remote_mem = RemoteMemoryBlock(self.listview_ctrl, size=ctypes.sizeof(nmlv))
        new_remote_mem.Write(nmlv, size=ctypes.sizeof(nmlv))

        retval = self.listview_ctrl.Parent().SendMessage(
            win32defines.WM_NOTIFY,
            self.listview_ctrl.ControlID(),
            new_remote_mem)
        #if retval != win32defines.TRUE:
        #    print('retval = ' + str(retval))
        #    raise ctypes.WinError()
        del new_remote_mem

        win32functions.WaitGuiThreadIdle(self.listview_ctrl)
        time.sleep(Timings.after_listviewselect_wait)


    #-----------------------------------------------------------
    def Select(self):
        """Mark the item as selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        self._modify_selection(True)

    #-----------------------------------------------------------
    def Deselect(self):
        """Mark the item as not selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        self._modify_selection(False)



#====================================================================
class ListViewWrapper(HwndWrapper.HwndWrapper):
    """Class that wraps Windows ListView common control

    This class derives from HwndWrapper - so has all the methods o
    that class also

    **see** HwndWrapper.HwndWrapper_

    .. _HwndWrapper.HwndWrapper: class-pywinauto.controls.HwndWrapper.HwndWrapper.html

    """

    friendlyclassname = "ListView"
    windowclasses = [
        "SysListView32", 
        r"WindowsForms\d*\.SysListView32\..*", 
        "TSysListView",
        "ListView20WndClass"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ListViewWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            'ColumnCount',
            'ItemCount',
            'Columns',
            'Items'])
        
        if self.IsUnicode():
            self.create_buffer = ctypes.create_unicode_buffer
            self.LVCOLUMN       = win32structures.LVCOLUMNW
            self.LVITEM         = win32structures.LVITEMW
            self.LVM_GETITEM    = win32defines.LVM_GETITEMW
            self.LVM_GETCOLUMN  = win32defines.LVM_GETCOLUMNW
            self.text_decode    = lambda v: v
        else:
            self.create_buffer = ctypes.create_string_buffer
            self.LVCOLUMN       = win32structures.LVCOLUMNW
            self.LVITEM         = win32structures.LVITEMW
            self.LVM_GETCOLUMN  = win32defines.LVM_GETCOLUMNA
            self.LVM_GETITEM    = win32defines.LVM_GETITEMA            
            self.text_decode    = lambda v: v.decode(locale.getpreferredencoding())

    #-----------------------------------------------------------
    def ColumnCount(self):
        """Return the number of columns"""
        if self.GetHeaderControl() is not None:
            return self.GetHeaderControl().ItemCount()
        return 0

    #-----------------------------------------------------------
    def ItemCount(self):
        "The number of items in the ListView"
        return self.SendMessage(win32defines.LVM_GETITEMCOUNT)

    #-----------------------------------------------------------
    def GetHeaderControl(self):
        "Returns the Header control associated with the ListView"
        #from wraphandle import WrapHandle
        #from HwndWrapper import WrapHandle

        try:
            return HwndWrapper.HwndWrapper(
                self.SendMessage(win32defines.LVM_GETHEADER))
        except HwndWrapper.InvalidWindowHandle:
            return None

    #-----------------------------------------------------------
    def GetColumn(self, col_index):
        "Get the information for a column of the ListView"

        col_props = {}

        col = self.LVCOLUMN()
        col.mask = \
            win32defines.LVCF_FMT | \
            win32defines.LVCF_IMAGE | \
            win32defines.LVCF_ORDER | \
            win32defines.LVCF_SUBITEM | \
            win32defines.LVCF_TEXT | \
            win32defines.LVCF_WIDTH

        remote_mem = RemoteMemoryBlock(self)

        col.cchTextMax = 2000
        col.pszText = remote_mem.Address() + ctypes.sizeof(col) + 1

        # put the information in the memory that the
        # other process can read/write
        remote_mem.Write(col)

        # ask the other process to update the information
        retval = self.SendMessage(
            self.LVM_GETCOLUMN,
            col_index,
            remote_mem)

        col = remote_mem.Read(col)

        # if that succeeded then there was a column
        if retval:
            col = remote_mem.Read(col)

            text = self.create_buffer(2000)
            remote_mem.Read(text, col.pszText)

            col_props['order'] = col.iOrder
            col_props['text'] = self.text_decode(text.value)
            col_props['format'] = col.fmt
            col_props['width'] = col.cx
            col_props['image'] = col.iImage
            col_props['subitem'] = col.iSubItem

        del remote_mem

        return col_props

    #-----------------------------------------------------------
    def Columns(self):
        "Get the information on the columns of the ListView"
        cols = []

        for i in range(0,  self.ColumnCount()):
            cols.append(self.GetColumn(i))

        return cols

    #-----------------------------------------------------------
    def ColumnWidths(self):
        "Return a list of all the column widths"
        return [col['width'] for col in self.Columns()]

    #-----------------------------------------------------------
    def GetItemRect(self, item_index):
        "Return the bounding rectangle of the list view item"
        warnings.warn("Use GetItem(item).Rectangle() instead", DeprecationWarning)
        return self.GetItem(item_index).Rectangle()

    #-----------------------------------------------------------
    def _as_item_index(self, item):
        """Ensure that item is an item index

        If a string is passed in then it will be searched for in the
        list of item titles.
        """
        index = item
        if isinstance(item, six.string_types):
            index = int((self.Texts().index(item) - 1) / self.ColumnCount())

        return index

    #-----------------------------------------------------------
    def GetItem(self, item_index, subitem_index = 0):
        """Return the item of the list view"

        * **item_index** Can be either an index of the item or a string
          with the text of the item you want returned.
        * **subitem_index** A zero based index of the item you want returned.
          Defaults to 0.
        """

        return _listview_item(self, item_index, subitem_index)

    Item = GetItem # this is an alias to be consistent with other content elements

    #-----------------------------------------------------------
    def Items(self):
        "Get all the items in the list view"
        colcount = self.ColumnCount()

        if not colcount:
            colcount = 1

        items = []
        # now get the item values...
        # for each of the rows
        for item_index in range(0, self.ItemCount()):

            # and each of the columns for that row
            for subitem_index in range(0, colcount):

                # get the item
                #yield self.GetItem(item_index, subitem_index) # return iterator
                items.append(self.GetItem(item_index, subitem_index).ItemData())

        return items

    #-----------------------------------------------------------
    def Texts(self):
        "Get the texts for the ListView control"
        texts = [self.WindowText()]
        texts.extend([item['text'] for item in self.Items()])
        return texts

    #-----------------------------------------------------------
    def UnCheck(self, item):
        "Uncheck the ListView item"

        warnings.warn("Use GetItem(item).UnCheck() instead", DeprecationWarning)
        return self.GetItem(item).UnCheck()

    #-----------------------------------------------------------
    def Check(self, item):
        "Check the ListView item"

        warnings.warn("Use GetItem(item).Check() instead", DeprecationWarning)
        return self.GetItem(item).Check()

    #-----------------------------------------------------------
    def IsChecked(self, item):
        "Return whether the ListView item is checked or not"

        warnings.warn("Use GetItem(item).IsChecked() instead", DeprecationWarning)
        return self.GetItem(item).IsChecked()

    #-----------------------------------------------------------
    def IsSelected(self, item):
        "Return True if the item is selected"

        warnings.warn("Use GetItem(item).IsSelected() instead", DeprecationWarning)
        return self.GetItem(item).IsSelected()

    #-----------------------------------------------------------
    def IsFocused(self, item):
        "Return True if the item has the focus"

        warnings.warn("Use GetItem(item).IsFocused() instead", DeprecationWarning)
        return self.GetItem(item).IsFocused()

    #-----------------------------------------------------------
    def Select(self, item):
        """Mark the item as selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        warnings.warn("Use GetItem(item).Select() instead", DeprecationWarning)
        return self.GetItem(item).Select()

    #-----------------------------------------------------------
    def Deselect(self, item):
        """Mark the item as not selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        warnings.warn("Use GetItem(item).Deselect() instead", DeprecationWarning)
        return self.GetItem(item).Deselect()

    # Naming is not clear - so create an alias.
    #UnSelect = Deselect

    #-----------------------------------------------------------
    def GetSelectedCount(self):
        "Return the number of selected items"

        return self.SendMessage(win32defines.LVM_GETSELECTEDCOUNT)




class _treeview_element(object):
    "Wrapper around TreeView items"
    #----------------------------------------------------------------
    def __init__(self, elem, tv_handle):
        "Initialize the item"
        self.tree_ctrl = tv_handle
        self.elem = elem
        self._as_parameter_ = self.elem

    #----------------------------------------------------------------
    def Text(self):
        "Return the text of the item"
        return self._readitem()[1]

    #----------------------------------------------------------------
    def Item(self):
        "Return the item itself"
        return self._readitem()[0]

    #----------------------------------------------------------------
    def State(self):
        "Return the state of the item"
        return self.Item().state

    #-----------------------------------------------------------
    def IsChecked(self):
        "Return whether the TreeView item is checked or not"

        state = self.tree_ctrl.SendMessage(
            win32defines.TVM_GETITEMSTATE,
            self.elem,
            win32defines.TVIS_STATEIMAGEMASK)

        return state & 0x2000 == 0x2000

    #----------------------------------------------------------------
    def Rectangle(self, text_area_rect = True):
        """Return the rectangle of the item

        If text_area_rect is set to False then it will return
        the rectangle for the whole item (usually left is equal to 0).
        Defaults to True - which returns just the rectangle of the
        text of the item
        """
        remote_mem = RemoteMemoryBlock(self.tree_ctrl)

        # this is a bit weird
        # we have to write the element handle
        # but we read the Rectangle afterwards!
        remote_mem.Write(win32structures.LPARAM(self.elem))

        ret = self.tree_ctrl.SendMessage(
            win32defines.TVM_GETITEMRECT, text_area_rect, remote_mem)

        # the item is not visible
        if not ret:
            rect = None
        else:
            # OK - it's visible so read it
            rect = win32structures.RECT()
            remote_mem.Read(rect)

        del remote_mem
        return rect


    #----------------------------------------------------------------
    def Click(self, button = "left", double = False, where = "text", pressed = ""):
        """Click on the treeview item

        where can be any one of "text", "icon", "button", "check"
        defaults to "text"
        """

        # find the text rectangle for the item,
        point_to_click = self.Rectangle().mid_point()

        if where.lower() != "text":
            remote_mem = RemoteMemoryBlock(self.tree_ctrl)

            point_to_click.x = self.Rectangle().left

            found = False
            while not found and point_to_click.x >= 0:

                hittest = win32structures.TVHITTESTINFO()
                hittest.pt = point_to_click
                hittest.hItem = self.elem

                remote_mem.Write(hittest)

                self.tree_ctrl.SendMessage(win32defines.TVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if where.lower() == 'button' and \
                    hittest.flags == win32defines.TVHT_ONITEMBUTTON:
                    found = True
                    break

                if where.lower() == 'icon' and \
                    hittest.flags == win32defines.TVHT_ONITEMICON:
                    found = True
                    break

                if where.lower() == 'check' and \
                    hittest.flags == win32defines.TVHT_ONITEMSTATEICON:
                    found = True
                    break
                    
                point_to_click.x -= 1

            if not found:
                raise RuntimeError("Area ('%s') not found for this tree view item" % where)

        self.tree_ctrl.Click(
            button,
            coords = (point_to_click.x, point_to_click.y),
            double = double,
            pressed = pressed) #,
            #absolute = True) # XXX: somehow it works for 64-bit explorer.exe on Win8.1, but it doesn't work for 32-bit ControlSpyV6.exe

        # if we use click instead of clickInput - then we need to tell the
        # treeview to update itself
        #self.tree_ctrl.

    #----------------------------------------------------------------
    def ClickInput(self, button = "left", double = False, wheel_dist = 0, where = "text", pressed = ""):
        """Click on the treeview item

        where can be any one of "text", "icon", "button", "check"
        defaults to "text"
        """

        # find the text rectangle for the item,
        point_to_click = self.Rectangle().mid_point()

        if where.lower() != "text":
            remote_mem = RemoteMemoryBlock(self.tree_ctrl)

            point_to_click.x = self.Rectangle().left

            found = False
            while not found and point_to_click.x >= 0:

                hittest = win32structures.TVHITTESTINFO()
                hittest.pt = point_to_click
                hittest.hItem = self.elem

                remote_mem.Write(hittest)

                self.tree_ctrl.SendMessage(win32defines.TVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if where.lower() == 'button' and \
                    hittest.flags == win32defines.TVHT_ONITEMBUTTON:
                    found = True
                    break

                if where.lower() == 'icon' and \
                    hittest.flags == win32defines.TVHT_ONITEMICON:
                    found = True
                    break

                if where.lower() == 'check' and \
                    hittest.flags == win32defines.TVHT_ONITEMSTATEICON:
                    found = True
                    break
                    
                point_to_click.x -= 1

            if not found:
                raise RuntimeError("Area ('%s') not found for this tree view item" % where)

        self.tree_ctrl.ClickInput(
            button,
            coords = (point_to_click.x, point_to_click.y),
            double = double,
            wheel_dist = wheel_dist,
            pressed = pressed)

    #----------------------------------------------------------------
    def StartDragging(self, button='left', pressed=''):
        "Start dragging the item"
        
        #self.EnsureVisible()
        # find the text rectangle for the item
        rect = self.Rectangle()
        point_to_click = rect.mid_point()
        
        #self.tree_ctrl.SetFocus()
        self.tree_ctrl.PressMouseInput(button, coords = (point_to_click.x, point_to_click.y), pressed = pressed)
        for i in range(5):
            self.tree_ctrl.MoveMouseInput(coords = (rect.left + i, rect.top), pressed=pressed)

    #----------------------------------------------------------------
    def Drop(self, button='left', pressed=''):
        "Drop at the item"
        
        #self.EnsureVisible()
        # find the text rectangle for the item
        point_to_click = self.Rectangle().mid_point()
        
        self.tree_ctrl.MoveMouseInput(coords = (point_to_click.x, point_to_click.y), pressed=pressed)
        time.sleep(Timings.drag_n_drop_move_mouse_wait)
        
        self.tree_ctrl.ReleaseMouseInput(button, coords = (point_to_click.x, point_to_click.y), pressed = pressed)
        time.sleep(Timings.after_drag_n_drop_wait)

    #----------------------------------------------------------------
    def Collapse(self):
        "Collapse the children of this tree view item"
        self.tree_ctrl.SendMessage(
            win32defines.TVM_EXPAND,
            win32defines.TVE_COLLAPSE,
            self.elem)

    #----------------------------------------------------------------
    def Expand(self):
        "Expand the children of this tree view item"
        self.tree_ctrl.SendMessage(
            win32defines.TVM_EXPAND,
            win32defines.TVE_EXPAND,
            self.elem)


    #----------------------------------------------------------------
    def Children(self):
        "Return the direct children of this control"
        if self.Item().cChildren not in (0, 1):
            print("##### not dealing with that TVN_GETDISPINFO stuff yet")

        ## No children
        #if self.__item.cChildren == 0:
        #    pass

        children = []
        if self.Item().cChildren == 1:

            # Get the first child of this element
            child_elem = self.tree_ctrl.SendMessage(
                win32defines.TVM_GETNEXTITEM,
                win32defines.TVGN_CHILD,
                self.elem)

            if child_elem:
                children.append(_treeview_element(child_elem, self.tree_ctrl))

                # now get all the next children
                while True:
                    next_child = children[-1].Next()

                    if next_child is not None:
                        children.append(next_child)
                    else:
                        break

            else:
                return []
                #raise ctypes.WinError()

        return children

    #----------------------------------------------------------------
    def Next(self):
        "Return the next item"
        # get the next element
        next_elem = self.tree_ctrl.SendMessage(
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_NEXT,
            self.elem)

        if next_elem:
            return _treeview_element(next_elem, self.tree_ctrl)

        return None
        # don't raise - as it just meant that there was no
        # next
        #else:
        #    raise ctypes.WinError()

    #def Click(self):
    #    print self.Rectangle()
    #    self.t

    #----------------------------------------------------------------
    def SubElements(self):
        "Return the list of Children of this control"
        sub_elems = []

        for child in self.Children():
            sub_elems.append(child)

            sub_elems.extend(child.SubElements())

        return sub_elems

    #----------------------------------------------------------------
    def GetChild(self, child_spec, exact = False):
        """Return the child item of this item

        Accepts either a string or an index.
        If a string is passed then it returns the child item
        with the best match for the string."""

        #print child_spec


        if isinstance(child_spec, six.string_types):

            texts = [c.Text() for c in self.Children()]
            if exact:
                if child_spec in texts:
                    index = texts.index(child_spec)
                else:
                    raise IndexError('There is no child equal to "' + str(child_spec) + '" in ' + str(texts))
            else:
                indices = range(0, len(texts))
                index = findbestmatch.find_best_match(
                    child_spec, texts, indices, limit_ratio = .6)

            #if len(matching) > 1 :
            #    raise RuntimeError(
            #        "There are multiple children that match that spec '%s'"%
            #            child_spec)

        else:
            index = child_spec

        return self.Children()[index]

    #----------------------------------------------------------------
    def EnsureVisible(self):
        "Make sure that the TreeView item is visible"
        self.tree_ctrl.SendMessage(
            win32defines.TVM_ENSUREVISIBLE,
            win32defines.TVGN_CARET,
            self.elem)

    #----------------------------------------------------------------
    def Select(self):
        "Select the TreeView item"

        # http://stackoverflow.com/questions/14111333/treeview-set-default-select-item-and-highlight-blue-this-item
        # non-focused TreeView can ignore TVM_SELECTITEM
        self.tree_ctrl.SetFocus()

        retval = self.tree_ctrl.SendMessage(
            win32defines.TVM_SELECTITEM, # message
            win32defines.TVGN_CARET,     # how to select
            self.elem)                   # item to select

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

    #----------------------------------------------------------------
    def IsSelected(self):
        "Indicate that the TreeView item is selected or not"
        return win32defines.TVIS_SELECTED == (win32defines.TVIS_SELECTED & self.State())

    #----------------------------------------------------------------
    def IsExpanded(self):
        "Indicate that the TreeView item is selected or not"
        return win32defines.TVIS_EXPANDED == (win32defines.TVIS_EXPANDED & self.State())

    #----------------------------------------------------------------
    def _readitem(self):
        "Read the treeview item"
        remote_mem = RemoteMemoryBlock(self.tree_ctrl)

        item = win32structures.TVITEMW()
        item.mask =  win32defines.TVIF_TEXT | \
            win32defines.TVIF_HANDLE | \
            win32defines.TVIF_CHILDREN | \
            win32defines.TVIF_STATE

        # set the address for the text
        item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 16
        item.cchTextMax = 2000
        item.hItem = self.elem
        item.stateMask = win32structures.UINT(-1)

        # Write the local TVITEM structure to the remote memory block
        remote_mem.Write(item)

        # read the entry
        retval = win32functions.SendMessage(
            self.tree_ctrl,
            win32defines.TVM_GETITEMW,
            0,
            remote_mem)

        text = ''
        if retval:
            remote_mem.Read(item)

            #self.__item = item
            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            text = char_data.value
        else:
            # seems that this may not always be correct
            raise ctypes.WinError()

        return item, text



#====================================================================
class TreeViewWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows TreeView common control"

    friendlyclassname = "TreeView"
    windowclasses = [
        "SysTreeView32", r"WindowsForms\d*\.SysTreeView32\..*", "TTreeView", "TreeList.TreeListCtrl"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(TreeViewWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def ItemCount(self):
        "Return the count of the items in the treeview"
        return self.SendMessage(win32defines.TVM_GETCOUNT)

    #----------------------------------------------------------------
    def Texts(self):
        "Return all the text for the tree view"
        texts = [self.WindowText(), ]
        if self.ItemCount():
            texts.append(self.Root().Text())
            elements = self.Root().SubElements()

            texts.extend([elem.Text() for elem in elements])

        return texts

    #----------------------------------------------------------------
    def Root(self):
        "Return the root element of the tree view"
        # get the root item:
        root_elem = self.SendMessage(
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_ROOT)

        # Sometimes there is no root element
        if not root_elem:
            return None

        return _treeview_element(root_elem, self)

    #----------------------------------------------------------------
    def Roots(self):
        roots = []

        cur_elem = self.Root()
        while cur_elem:
            roots.append(cur_elem)

            cur_elem = cur_elem.Next()

        return roots

    #----------------------------------------------------------------
    def GetProperties(self):
        "Get the properties for the control as a dictionary"
        props = super(TreeViewWrapper, self).GetProperties()

        props['ItemCount'] = self.ItemCount()

        return props

    #----------------------------------------------------------------
    def GetItem(self, path, exact = False):
        """Read the TreeView item

        * **path** the path to the item to return. This can be one of
          the following:

          * A string separated by \\ characters. The first character must
            be \\. This string is split on the \\ characters and each of
            these is used to find the specific child at each level. The
            \\ represents the root item - so you don't need to specify the
            root itself.
          * A list/tuple of strings - The first item should be the root
            element.
          * A list/tuple of integers - The first item the index which root
            to select.
        """

        # work just based on integers for now

        if not self.ItemCount():
            return None

        # Ensure the path is absolute
        if isinstance(path, six.string_types):
            if not path.startswith("\\"):
                raise RuntimeError(
                    "Only absolute paths allowed - "
                    "please start the path with \\")

            path = path.split("\\")[1:]

        current_elem = None

        # find the correct root elem
        if isinstance(path[0], int):
            current_elem = self.Roots()[path[0]]

        else:
            roots = self.Roots()
            texts = [r.Text() for r in roots]
            #not used var: indices = range(0, len(texts))
            if exact:
                if path[0] in texts:
                    current_elem = roots[texts.index(path[0])]
                else:
                    raise IndexError("There is no root element equal to '%s'"% path[0])
            else:
                try:
                    current_elem = findbestmatch.find_best_match(
                        path[0], texts, roots, limit_ratio = .6)
                except IndexError:
                    raise IndexError("There is no root element similar to '%s'"% path[0])

        # get the correct lowest level item
#        current_elem.GetChild
#        for i in range(0, path[0]):
#            current_elem = current_elem.Next()
#
#            if current_elem is None:
#                raise IndexError("Root Item '%s' does not have %d sibling(s)"%
#                    (self.Root().WindowText(), i + 1))
#
        # remove the first (empty) item and the root element as we have
        # dealt with it (string or integer)
        path = path[1:]

        # now for each of the lower levels
        # just index into it's children
        for child_spec in path:

            # ensure that the item is expanded (as this is sometimes required
            # for loading the tree view branches
            current_elem.Expand()

            try:
                current_elem = current_elem.GetChild(child_spec, exact)
            except IndexError:
                if isinstance(child_spec, six.string_types):
                    raise IndexError("Item '%s' does not have a child '%s'"%
                        (current_elem.Text(), child_spec))
                else:
                    raise IndexError("Item '%s' does not have %d children"%
                        (current_elem.Text(), child_spec + 1))


            #self.SendMessageTimeout(
            #    win32defines.TVM_EXPAND,
            #    win32defines.TVE_EXPAND,
            #    current_elem)

        return  current_elem

    Item = GetItem # this is an alias to be consistent with other content elements

    #----------------------------------------------------------------
    def Select(self, path):
        "Select the treeview item"

        # http://stackoverflow.com/questions/14111333/treeview-set-default-select-item-and-highlight-blue-this-item
        # non-focused TreeView can ignore TVM_SELECTITEM
        self.SetFocus()

        elem = self.GetItem(path)
        #result = ctypes.c_long()
        retval = self.SendMessage(
            win32defines.TVM_SELECTITEM, # message
            win32defines.TVGN_CARET,     # how to select
            elem.elem)                   # item to select
            #win32defines.SMTO_NORMAL,
            #int(Timings.after_treeviewselect_wait * 1000),
            #ctypes.byref(result))

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_treeviewselect_wait)

    #-----------------------------------------------------------
    def IsSelected(self, path):
        "Return True if the item is selected"
        return win32defines.TVIS_SELECTED  == (win32defines.TVIS_SELECTED & \
            self.GetItem(path).State())

    #----------------------------------------------------------------
    def EnsureVisible(self, path):
        "Make sure that the TreeView item is visible"
        elem = self.GetItem(path)
        self.SendMessageTimeout(
            win32defines.TVM_ENSUREVISIBLE, # message
            win32defines.TVGN_CARET,     # how to select
            elem.elem)                 # item to select

        win32functions.WaitGuiThreadIdle(self)

    #----------------------------------------------------------------
    def PrintItems(self):
        "Print all items with line indents"
        
        self.text = self.WindowText() + "\n"

        def PrintOneLevel(item,ident):
            self.text += " " * ident + item.Text() + "\n"
            for child in item.Children():
                PrintOneLevel(child,ident+1)

        for root in self.Roots():
            PrintOneLevel(root,0)
            
        return self.text

#
#   #-----------------------------------------------------------
#    def UnCheck(self, path):
#        "Uncheck the ListView item"
#
#        self.VerifyActionable()
#
#        elem = self.GetItem(path)
#
##        lvitem = win32structures.LVITEMW()
##
##        lvitem.mask = win32defines.LVIF_STATE
##        lvitem.state = 0x1000
##        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK
##
##        remote_mem = RemoteMemoryBlock(self)
##        remote_mem.Write(lvitem)
##
##        self.SendMessage(
##            win32defines.LVM_SETITEMSTATE, item, remote_mem)
##
##        del remote_mem
#
#
#    #-----------------------------------------------------------
#    def Check(self, path):
#        "Check the ListView item"
#
#        self.VerifyActionable()
#
#        elem = self.GetItem(path)
#
#        #lvitem = win32structures.LVITEMW()
#
#        lvitem.mask = win32defines.LVIF_STATE
#        lvitem.state = 0x2000
#        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK
#
#        remote_mem = RemoteMemoryBlock(self)
#        remote_mem.Write(lvitem)
#
#        self.SendMessage(
#            win32defines.LVM_SETITEMSTATE, item, remote_mem)
#
#        del remote_mem
#
#    #-----------------------------------------------------------
#    def IsChecked(self, path):
#        "Return whether the ListView item is checked or not"
#
#        elem = self.GetItem(path)
#
#        elem.State
#
#        state = self.SendMessage(
#            win32defines.LVM_GETITEMSTATE,
#            item,
#            win32defines.LVIS_STATEIMAGEMASK)
#
#        return state & 0x2000
#




#====================================================================
class HeaderWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ListView Header common control "

    friendlyclassname = "Header"
    windowclasses = ["SysHeader32", "msvb_lib_header"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(HeaderWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def ItemCount(self):
        "Return the number of columns in this header"
        # get the number of items in the header...
        return self.SendMessage(win32defines.HDM_GETITEMCOUNT)

    #----------------------------------------------------------------
    def GetColumnRectangle(self, column_index):
        "Return the rectangle for the column specified by column_index"

        remote_mem = RemoteMemoryBlock(self)
        # get the column rect
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        retval = self.SendMessage(
            win32defines.HDM_GETITEMRECT,
            column_index,
            remote_mem)

        if retval:
            rect = remote_mem.Read(rect)
        else:
            raise ctypes.WinError()

        del remote_mem

        return rect

    #----------------------------------------------------------------
    def ClientRects(self):
        "Return all the client rectangles for the header control"
        rects = [self.ClientRect(), ]

        for col_index in range(0, self.ItemCount()):

            rects.append(self.GetColumnRectangle(col_index))

        return rects


    #----------------------------------------------------------------
    def GetColumnText(self, column_index):
        "Return the text for the column specified by column_index"

        remote_mem = RemoteMemoryBlock(self)

        item = win32structures.HDITEMW()
        item.mask = win32defines.HDI_FORMAT | \
            win32defines.HDI_WIDTH | \
            win32defines.HDI_TEXT #| HDI_ORDER
        item.cchTextMax = 2000

        # set up the pointer to the text
        # it should be at the
        item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1

        # put the information in the memory that the
        # other process can read/write
        remote_mem.Write(item)

        # ask the other process to update the information
        retval = self.SendMessage(
            win32defines.HDM_GETITEMW,
            column_index,
            remote_mem)

        if retval:
            item = remote_mem.Read(item)

            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)
            return char_data.value

        return None

    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts of the Header control"
        texts = [self.WindowText(), ]
        for i in range(0, self.ItemCount()):
            texts.append(self.GetColumnText(i))

        return texts

#    #----------------------------------------------------------------
#    def _fill_header_info(self):
#        "Get the information from the header control"
#        remote_mem = RemoteMemoryBlock(self)
#
#        for col_index in range(0, self.Count()):
#
#            item = win32structures.HDITEMW()
#            item.mask = win32defines.HDI_FORMAT | \
#                win32defines.HDI_WIDTH | \
#                win32defines.HDI_TEXT #| HDI_ORDER
#            item.cchTextMax = 2000
#
#            # set up the pointer to the text
#            # it should be at the
#            item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
#
#            # put the information in the memory that the
#            # other process can read/write
#            remote_mem.Write(item)
#
#            # ask the other process to update the information
#            retval = self.SendMessage(
#                win32defines.HDM_GETITEMW,
#                col_index,
#                remote_mem)
#
#            if retval:
#                item = remote_mem.Read(item)
#
#                # Read the remote text string
#                charData = ctypes.create_unicode_buffer(2000)
#                remote_mem.Read(charData, item.pszText)
#                self._extra_texts.append(charData.value)


#====================================================================
class StatusBarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Status Bar common control "

    friendlyclassname = "StatusBar"
    windowclasses = [
        "msctls_statusbar32",
        "HSStatusBar",
        "TStatusBar",
        r"WindowsForms\d*\.msctls_statusbar32\..*"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(StatusBarWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            'BorderWidths',
            'PartCount',
            'PartRightEdges',

        ])

    #----------------------------------------------------------------
    def BorderWidths(self):
        """Return the border widths of the StatusBar

        A dictionary of the 3 available widths is returned:
        Horizontal - the horizontal width
        Vertical - The width above and below the status bar parts
        Inter - The width between parts of the status bar
        """
        remote_mem = RemoteMemoryBlock(self)

        # get the borders for each of the areas there can be a border.
        borders = (ctypes.c_int*3)()
        remote_mem.Write(borders)
        self.SendMessage(
            win32defines.SB_GETBORDERS,
            0,
            remote_mem
        )
        borders = remote_mem.Read(borders)
        borders_widths = {}
        borders_widths['Horizontal'] = borders[0]
        borders_widths['Vertical'] = borders[1]
        borders_widths['Inter'] = borders[2]

        del remote_mem

        return borders_widths

    #----------------------------------------------------------------
    def PartCount(self):
        "Return the number of parts"
        # get the number of parts for this status bar
        return self.SendMessage(
            win32defines.SB_GETPARTS,
            0,
            0 )

    #----------------------------------------------------------------
    def PartRightEdges(self):
        "Return the widths of the parts"
        remote_mem = RemoteMemoryBlock(self)

        # get the number of parts for this status bar
        parts = (ctypes.c_int * self.PartCount())()
        remote_mem.Write(parts)
        self.SendMessage(
            win32defines.SB_GETPARTS,
            self.PartCount(),
            remote_mem
        )

        parts = remote_mem.Read(parts)

        del remote_mem

        return [int(part) for part in parts]

    #----------------------------------------------------------------
    def GetPartRect(self, part_index):
        "Return the rectangle of the part specified by part_index"

        if part_index >= self.PartCount():
            raise IndexError(
                "Only %d parts available you asked for part %d (zero based)" % (
                self.PartCount(),
                part_index))


        remote_mem = RemoteMemoryBlock(self)

        # get the rectangle for this item
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        self.SendMessage(
            win32defines.SB_GETRECT,
            part_index,
            remote_mem)

        rect = remote_mem.Read(rect)
        del remote_mem
        return rect

    #----------------------------------------------------------------
    def ClientRects(self):
        "Return the client rectangles for the control"
        rects = [self.ClientRect()]

        for i in range(self.PartCount()):
            rects.append(self.GetPartRect(i))

        return rects

    #----------------------------------------------------------------
    def GetPartText(self, part_index):
        "Return the text of the part specified by part_index"

        if part_index >= self.PartCount():
            raise IndexError(
                "Only %d parts available you asked for part %d (zero based)" % (
                self.PartCount(),
                part_index))

        remote_mem = RemoteMemoryBlock(self)

        textlen = self.SendMessage(
            win32defines.SB_GETTEXTLENGTHW,
            part_index,
            0
        )

        #draw_operation = win32functions.HiWord(textlen)
        textlen = win32functions.LoWord(textlen)

        # get the text for this item
        text = ctypes.create_unicode_buffer(textlen + ctypes.sizeof(ctypes.c_wchar))
        remote_mem.Write(text)
        self.SendMessage(
            win32defines.SB_GETTEXTW,
            part_index,
            remote_mem
        )

        text = remote_mem.Read(text)

        del remote_mem
        return text.value


    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts for the control"
        texts = [self.WindowText()]

        for i in range(self.PartCount()):
            texts.append(self.GetPartText(i))

        return texts




#====================================================================
class TabControlWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Tab common control "

    friendlyclassname = "TabControl"
    windowclasses = [
        "SysTabControl32",
        r"WindowsForms\d*\.SysTabControl32\..*"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(TabControlWrapper, self).__init__(hwnd)

        #self.writable_props.append("TabStates")

    #----------------------------------------------------------------
    def RowCount(self):
        "Return the number of rows of tabs"
        return self.SendMessage(win32defines.TCM_GETROWCOUNT)

    #----------------------------------------------------------------
    def GetSelectedTab(self):
        "Return the index of the selected tab"
        return self.SendMessage(win32defines.TCM_GETCURSEL)

    #----------------------------------------------------------------
    def TabCount(self):
        "Return the number of tabs"
        return self.SendMessage(win32defines.TCM_GETITEMCOUNT)

    #----------------------------------------------------------------
    def GetTabRect(self, tab_index):
        "Return the rectangle to the tab specified by tab_index"

        if tab_index >= self.TabCount():
            raise IndexError(
                "Only %d tabs available you asked for tab %d (zero based)" % (
                self.TabCount(),
                tab_index))

        remote_mem = RemoteMemoryBlock(self)

        rect = win32structures.RECT()
        remote_mem.Write(rect)

        self.SendMessage(
            win32defines.TCM_GETITEMRECT, tab_index, remote_mem)

        remote_mem.Read(rect)

        del remote_mem

        return rect

#    #----------------------------------------------------------------
#    def GetTabState(self, tab_index):
#        "Return the state of the tab"
#
#        if tab_index >= self.TabCount():
#            raise IndexError(
#                "Only %d tabs available you asked for tab %d (zero based)" % (
#                self.TabCount(),
#                tab_index))
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        item = win32structures.TCITEMW()
#        item.mask = win32defines.TCIF_STATE
#        remote_mem.Write(item)
#
#        ret = self.SendMessage(
#            win32defines.TCM_GETITEMW, tab_index, remote_mem)
#
#        remote_mem.Read(item)
#        del remote_mem
#
#        if not ret:
#            raise ctypes.WinError()
#
#        return item.dwState

    #----------------------------------------------------------------
    def GetTabText(self, tab_index):
        "Return the text of the tab"

        if tab_index >= self.TabCount():
            raise IndexError(
                "Only %d tabs available you asked for tab %d (zero based)" % (
                self.TabCount(),
                tab_index))

        remote_mem = RemoteMemoryBlock(self)

        item = win32structures.TCITEMW()
        item.mask = win32defines.TCIF_TEXT
        item.cchTextMax = 1999
        item.pszText = remote_mem.Address() + ctypes.sizeof(item)
        remote_mem.Write(item)

        self.SendMessage(
            win32defines.TCM_GETITEMW, tab_index, remote_mem)

        remote_mem.Read(item)

        # Read the text that has been written
        text = ctypes.create_unicode_buffer(2000)
        text = remote_mem.Read(text, remote_mem.Address() + \
            ctypes.sizeof(item))

        return text.value

    #----------------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the TabControl as a Dictionary"
        props = super(TabControlWrapper, self).GetProperties()

        props['TabCount'] = self.TabCount()


        return props

#    #----------------------------------------------------------------
#    def TabStates(self):
#        "Return the tab state for all the tabs"
#        states = []
#        for i in range(0, self.TabCount()):
#            states.append(self.GetTabState(i))
#        return states

    #----------------------------------------------------------------
    def ClientRects(self):
        "Return the client rectangles for the Tab Control"

        rects = [self.ClientRect()]
        for tab_index in range(0, self.TabCount()):
            rects.append(self.GetTabRect(tab_index))

        return rects

    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts of the Tab Control"
        texts = [self.WindowText()]

        for i in range(0, self.TabCount()):
            texts.append(self.GetTabText(i))

        return texts

    #----------------------------------------------------------------
    def Select(self, tab):
        "Select the specified tab on the tab control"

        self.VerifyActionable()
        logging_tab = tab

        # if it's a string then find the index of
        # the tab with that text
        if isinstance(tab, six.string_types):
            # find the string in the tab control
            best_text = findbestmatch.find_best_match(
                tab, self.Texts(), self.Texts())
            tab = self.Texts().index(best_text) - 1

        if tab >= self.TabCount():
            raise IndexError(
                "Only %d tabs available you asked for tab %d (zero based)" % (
                self.TabCount(),
                tab))

        if self.HasStyle(win32defines.TCS_BUTTONS):
            # workaround for TCS_BUTTONS case
            self.Click(coords=self.GetTabRect(tab))

            # TCM_SETCURFOCUS changes focus, but doesn't select the tab
            # TCM_SETCURSEL selects the tab, but tab content is not re-drawn
            # (TODO: need to find a solution without WM_CLICK)

            #self.Notify(win32defines.TCN_SELCHANGING)
            #self.SendMessage(win32defines.TCM_SETCURSEL, tab)
            #self.Notify(win32defines.TCN_SELCHANGE)
        else:
            self.SendMessage(win32defines.TCM_SETCURFOCUS, tab)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_tabselect_wait)
        self.actions.log('Selected tab "' + str(logging_tab) + '"')

        return self



#====================================================================
class _toolbar_button(object):
    """
    Wrapper around Toolbar button (TBBUTTONINFO) items
    """
    #----------------------------------------------------------------
    def __init__(self, index_, tb_handle):
        "Initialize the item"
        self.toolbar_ctrl = tb_handle
        self.index = index_
        self.info = self.toolbar_ctrl.GetButton(self.index)

    #----------------------------------------------------------------
    def Rectangle(self):
        "Get the rectangle of a button on the toolbar"

        remote_mem = RemoteMemoryBlock(self.toolbar_ctrl)

        rect = win32structures.RECT()

        remote_mem.Write(rect)

        self.toolbar_ctrl.SendMessage(
            win32defines.TB_GETRECT,
            self.info.idCommand,
            remote_mem)

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect

#    #----------------------------------------------------------------
#    def Press(self, press = True):
#        "Find where the button is and click it"
#
#        if press:
#            press_flag = win32functions.MakeLong(0, 1)
#        else:
#            press_flag = 0
#
#        ret = self.toolbar_ctrl.SendMessageTimeout(
#            win32defines.TB_PRESSBUTTON,
#            self.info.idCommand,
#            press_flag)
#
#        # Notify the parent that we are finished selecting
#        #self.toolbar_ctrl.NotifyParent(win32defines.TBN_TOOLBARCHANGE)
#
#        win32functions.WaitGuiThreadIdle(self.toolbar_ctrl)
#        time.sleep(Timings.after_toobarpressbutton_wait)
#
#    #----------------------------------------------------------------
#    def Press(self):
#        "Find where the button is and click it"
#        self.Press(press = False)
#
#    #----------------------------------------------------------------
#    def Check(self, check = True):
#        "Find where the button is and click it"
#
#        if check:
#            check_flag = win32functions.MakeLong(0, 1)
#        else:
#            check_flag = 0
#
#        ret = self.toolbar_ctrl.SendMessageTimeout(
#            win32defines.TB_CHECKBUTTON,
#            self.info.idCommand,
#            check_flag)
#
#        # Notify the parent that we are finished selecting
#        #self.toolbar_ctrl.NotifyParent(win32defines.TBN_TOOLBARCHANGE)
#
#        win32functions.WaitGuiThreadIdle(self.toolbar_ctrl)
#        time.sleep(Timings.after_toobarpressbutton_wait)
#
#    #----------------------------------------------------------------
#    def UnCheck(self):
#        self.Check(check = False)

    #----------------------------------------------------------------
    def Text(self):
        "Return the text of the button"
        return self.info.text

    #----------------------------------------------------------------
    def Style(self):
        "Return the style of the button"
        return self.toolbar_ctrl.SendMessage(
            win32defines.TB_GETSTYLE, self.info.idCommand)

    #----------------------------------------------------------------
    def HasStyle(self, style):
        "Return True if the button has the specified style"
        return self.Style() & style == style

    #----------------------------------------------------------------
    def State(self):
        "Return the state of the button"
        return self.toolbar_ctrl.SendMessage(
            win32defines.TB_GETSTATE, self.info.idCommand)

    #----------------------------------------------------------------
    def IsCheckable(self):
        "Return if the button can be checked"
        return self.HasStyle(win32defines.TBSTYLE_CHECK)

    #----------------------------------------------------------------
    def IsPressable(self):
        "Return if the button can be pressed"
        return self.HasStyle(win32defines.TBSTYLE_BUTTON)

    #----------------------------------------------------------------
    def IsChecked(self):
        "Return if the button is in the checked state"
        return self.State() & win32defines.TBSTATE_CHECKED == win32defines.TBSTATE_CHECKED

    #----------------------------------------------------------------
    def IsPressed(self):
        "Return if the button is in the pressed state"
        return self.State() & win32defines.TBSTATE_PRESSED == win32defines.TBSTATE_PRESSED

    #----------------------------------------------------------------
    def IsEnabled(self):
        "Return if the button is in the pressed state"

        # make sure it has an ID
        if not self.info.idCommand:
            return False

        return self.State() & win32defines.TBSTATE_ENABLED == win32defines.TBSTATE_ENABLED

    #----------------------------------------------------------------
    def Click(self, button = "left", pressed = ""):
        "Click on the Toolbar button"
        self.toolbar_ctrl.Click(button=button, coords = self.Rectangle(), pressed=pressed)
        time.sleep(Timings.after_toobarpressbutton_wait)

    #----------------------------------------------------------------
    def ClickInput(self, button = "left", double = False, wheel_dist = 0, pressed = ""):
        "Click on the Toolbar button"
        self.toolbar_ctrl.ClickInput(button=button, coords = self.Rectangle().mid_point(),
                                     double=double, wheel_dist=wheel_dist, pressed=pressed)
        time.sleep(Timings.after_toobarpressbutton_wait)

#====================================================================
class ToolbarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Toolbar common control "

    friendlyclassname = "Toolbar"
    windowclasses = [
        "ToolbarWindow32",
        r"WindowsForms\d*\.ToolbarWindow32\..*"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ToolbarWrapper, self).__init__(hwnd)

        self.writable_props.extend(['ButtonCount'])

    #----------------------------------------------------------------
    def ButtonCount(self):
        "Return the number of buttons on the ToolBar"
        return self.SendMessage(win32defines.TB_BUTTONCOUNT)

    #----------------------------------------------------------------
    def Button(self, button_identifier, exact = True, by_tooltip=False):
        "Return the button at index button_index"
        
        if isinstance(button_identifier, six.string_types):
            texts = self.Texts()[1:]
            self.actions.log('Toolbar buttons: ' + str(texts))
            # one of these will be returned for the matching text
            indices = [i for i in range(0, len(texts))]

            if by_tooltip:
                texts = self.TipTexts()
                self.actions.log('Toolbar tooltips: ' + str(texts))
            
            if exact:
                try:
                    button_index = texts.index(button_identifier)
                except ValueError:
                    raise findbestmatch.MatchError(items=texts, tofind=button_identifier)
            else:
                # find which index best matches that text
                button_index = findbestmatch.find_best_match(button_identifier, texts, indices)
        else:
            button_index = button_identifier
        
        return _toolbar_button(button_index, self)

    #----------------------------------------------------------------
    def GetButtonStruct(self, button_index):
        "Return TBBUTTON structure on the Toolbar button"
        
        if button_index >= self.ButtonCount():
            raise IndexError(
                "0 to %d are acceptiple for button_index"%
                self.ButtonCount())

        remote_mem = RemoteMemoryBlock(self)
        button = win32structures.TBBUTTON()
        remote_mem.Write(button)

        ret = self.SendMessage(
            win32defines.TB_GETBUTTON, button_index, remote_mem)

        if not ret:
            del remote_mem
            raise RuntimeError(
                "GetButton failed for button index %d"% button_index)

        remote_mem.Read(button)
        del remote_mem

        return button

    #----------------------------------------------------------------
    def GetButton(self, button_index):
        "Return information on the Toolbar button"

        button = self.GetButtonStruct(button_index)

        button_info = win32structures.TBBUTTONINFOW()
        button_info.cbSize = ctypes.sizeof(button_info)
        button_info.dwMask = \
            win32defines.TBIF_COMMAND | \
            win32defines.TBIF_SIZE | \
            win32defines.TBIF_STYLE | \
            win32defines.TBIF_IMAGE | \
            win32defines.TBIF_LPARAM | \
            win32defines.TBIF_STATE | \
            win32defines.TBIF_TEXT
            #win32defines.TBIF_IMAGELABEL | \

        button_info.cchText = 2000

        remote_mem = RemoteMemoryBlock(self)

        # set the text address to after the structures
        button_info.pszText = remote_mem.Address() + \
            ctypes.sizeof(button_info)

        # fill the button_info structure
        remote_mem.Write(button_info)
        ret = self.SendMessage(
            win32defines.TB_GETBUTTONINFOW,
            button.idCommand,
            remote_mem)
        remote_mem.Read(button_info)

        if ret == -1:
            del remote_mem
            raise RuntimeError(
                "GetButtonInfo failed for button with command id %d"%
                    button.idCommand)

        # read the text
        button_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(button_info.text, remote_mem.Address() + \
            ctypes.sizeof(button_info))

        button_info.text = button_info.text.value

        del remote_mem

        return button_info

    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts of the Toolbar"
        texts = [self.WindowText()]
        for i in range(0, self.ButtonCount()):
            btn_text = self.GetButton(i).text
            lines = btn_text.split('\n')
            if lines:
                texts.append(lines[0])
            else:
                texts.append(btn_text)

        return texts

    #----------------------------------------------------------------
    def TipTexts(self):
        "Return the tip texts of the Toolbar (without window text)"
        texts = []
        for i in range(0, self.ButtonCount()):
            
            # it works for MFC
            btn_tooltip_index = self.GetButtonStruct(i).iString
            # usually iString == -1 for separator
            
            # other cases if any
            if not (-1 <= btn_tooltip_index < self.GetToolTipsControl().ToolCount()):
                btn_tooltip_index = i
            
            btn_text = self.GetToolTipsControl().GetTipText(btn_tooltip_index + 1)
            texts.append(btn_text)

        return texts

    #----------------------------------------------------------------
    def GetButtonRect(self, button_index):
        "Get the rectangle of a button on the toolbar"

        button_struct = self.GetButton(button_index)

        remote_mem = RemoteMemoryBlock(self)

        rect = win32structures.RECT()

        remote_mem.Write(rect)

        self.SendMessage(
            win32defines.TB_GETRECT,
            button_struct.idCommand,
            remote_mem)

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect

    #----------------------------------------------------------------
    def GetToolTipsControl(self):
        "Return the tooltip control associated with this control"
        return ToolTipsWrapper(self.SendMessage(win32defines.TB_GETTOOLTIPS))



#    def Right_Click(self, button_index, **kwargs):
#        "Right click for Toolbar buttons"
#
#        win32functions.SetCapture(self)
#
#        button = self.GetButton(button_index)
#        #print button.text
#
#        rect = self.GetButtonRect(button_index)
#
#        x = (rect.left + rect.right) /2
#        y = (rect.top + rect.bottom) /2
#
#        #print x, y
#
#
#        self.MoveMouseInput(coords = (x, y))
#        self.SendMessage(
#            win32defines.WM_MOUSEACTIVATE,
#            self.Parent().Parent().Parent(),
#            win32functions.MakeLong(
#                win32defines.WM_RBUTTONDOWN,
#                win32defines.HTCLIENT)
#            )
#
#        self.PressMouse(pressed = "right", button = "right", coords = (x, y))
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        # now we need to notify the parent that the state has changed
#        nmlv = win32structures.NMMOUSE()
#        nmlv.hdr.hwndFrom = self.handle
#        nmlv.hdr.idFrom = self.ControlID()
#        nmlv.hdr.code = win32defines.NM_RCLICK
#
#
#        nmlv.dwItemSpec = button.idCommand
#        #nmlv.dwItemData
#
#        nmlv.pt = win32structures.POINT()
#
#        remote_mem.Write(nmlv)
#
#        self.SendMessage(
#            win32defines.WM_NOTIFY,
#            self.ControlID(),
#            remote_mem)
#
#        del remote_mem
#
#
#        self.ReleaseMouse(button = "right", coords = (x, y))
#
#        win32functions.ReleaseCapture()
#



    # TODO def Button(i or string).rect

    #----------------------------------------------------------------
    def PressButton(self, button_identifier, exact = True):
        "Find where the button is and click it"

        msg = 'Clicking "' + self.WindowText() + '" toolbar button "' + str(button_identifier) + '"'
        self.actions.logSectionStart(msg)
        self.actions.log(msg)
        button = self.Button(button_identifier, exact=exact)

        # transliterated from
        # http://source.winehq.org/source/dlls/comctl32/toolbar.c

        # if the button is enabled
        if button.IsEnabled():
            button.ClickInput()
        else:
            raise RuntimeError('Toolbar button "' + str(button_identifier) + '" is disabled! Cannot click it.')
        self.actions.logSectionEnd()

    #----------------------------------------------------------------
    def CheckButton(self, button_identifier, make_checked, exact = True):
        "Find where the button is and click it if it's unchecked and vice versa"

        self.actions.logSectionStart('Checking "' + self.WindowText() + '" toolbar button "' + str(button_identifier) + '"')
        button = self.Button(button_identifier, exact=exact)
        if make_checked:
            self.actions.log('Pressing down toolbar button "' + str(button_identifier) + '"')
        else:
            self.actions.log('Pressing up toolbar button "' + str(button_identifier) + '"')

        # TODO: add waiting for a button state
        if not button.IsEnabled():
            self.actions.log('Toolbar button is not enabled!')
            raise RuntimeError("Toolbar button is not enabled!")

        if button.IsChecked() != make_checked:
            button.ClickInput()

            # wait while button has changed check state
            #i = 0
            #while button.IsChecked() != make_checked:
            #    time.sleep(0.5)
            #    i += 1
            #    if i > 10:
            #        raise RuntimeError("Cannot wait button check state!")
        self.actions.logSectionEnd()


#    #----------------------------------------------------------------
#    def _fill_toolbar_info(self):
#        "Get the information from the toolbar"
#        buttonCount = self.SendMessage(win32defines.TB_BUTTONCOUNT)
#        self._extra_props['ButtonCount'] = buttonCount
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        for i in range(0, buttonCount):
#
#            button = win32structures.TBBUTTON()
#
#            remote_mem.Write(button)
#
#            self.SendMessage(
#                win32defines.TB_GETBUTTON, i, remote_mem)
#
#            remote_mem.Read(button)
#
#            buttonInfo = win32structures.TBBUTTONINFOW()
#            buttonInfo.cbSize = ctypes.sizeof(buttonInfo)
#            buttonInfo.dwMask = win32defines.TBIF_TEXT | \
#                win32defines.TBIF_COMMAND | \
#                win32defines.TBIF_SIZE | \
#                win32defines.TBIF_COMMAND | \
#                win32defines.TBIF_STYLE | \
#                win32defines.TBIF_STATE
#
#            buttonInfo.cchText = 2000
#
#            # set the text address to after the structures
#            buttonInfo.pszText = remote_mem.Address() + \
#                ctypes.sizeof(buttonInfo)
#
#            # fill the buttonInfo structure
#            remote_mem.Write(buttonInfo)
#            self.SendMessage(
#                win32defines.TB_GETBUTTONINFOW,
#                button.idCommand,
#                remote_mem)
#            remote_mem.Read(buttonInfo)
#
#            # read the text
#            text = ctypes.create_unicode_buffer(1999)
#            remote_mem.Read(text, remote_mem.Address() + \
#                ctypes.sizeof(buttonInfo))
#
#            extendedStyle = self.SendMessage(win32defines.TB_GETEXTENDEDSTYLE)
#
#            self._extra_props.setdefault('Buttons', []).append(
#                dict(
#                    iBitMap = button.iBitmap,
#                    idCommand = button.idCommand,
#                    fsState = button.fsState,
#                    fsStyle = button.fsStyle,
#                    cx = buttonInfo.cx,
#                    ExStyle = extendedStyle
#                )
#            )
#    #        if button.fsStyle & TBSTYLE_DROPDOWN == TBSTYLE_DROPDOWN and \
#    #            (extendedStyle & TBSTYLE_EX_DRAWDDARROWS) != \
#    #                TBSTYLE_EX_DRAWDDARROWS:
#    #            props['Buttons'][-1]["DROPDOWNMENU"] = 1
#    #
#    #            self.SendMessage(WM_COMMAND, button.idCommand)
#    #
#    #            print "Pressing", text.value
#    #            handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 1)
#    #            handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 0)
#
#            self._extra_texts.append(text.value)
#
#
# RB_GETBANDBORDERS

class BandWrapper(win32structures.REBARBANDINFOW):
    "Simple wrapper around REBARBANDINFOW to allow setting new attributes"
    pass

#====================================================================
class ReBarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ReBar common control "

    friendlyclassname = "ReBar"
    windowclasses = ["ReBarWindow32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ReBarWrapper, self).__init__(hwnd)

        self.writable_props.extend(['BandCount'])

    #----------------------------------------------------------------
    def BandCount(self):
        "Return the number of bands in the control"
        return self.SendMessage(win32defines.RB_GETBANDCOUNT)

    #----------------------------------------------------------------
    def GetBand(self, band_index):
        "Get a band of the ReBar control"

        if band_index >= self.BandCount():
            raise IndexError(
                "band_index %d greater then number of available bands: %d" %
                    (band_index, self.BandCount()))

        remote_mem = RemoteMemoryBlock(self)

        band_info = BandWrapper()

        band_info.cbSize = ctypes.sizeof(band_info)
        band_info.fMask = \
            win32defines.RBBIM_CHILD | \
            win32defines.RBBIM_CHILDSIZE | \
            win32defines.RBBIM_COLORS | \
            win32defines.RBBIM_HEADERSIZE | \
            win32defines.RBBIM_ID | \
            win32defines.RBBIM_IDEALSIZE | \
            win32defines.RBBIM_SIZE | \
            win32defines.RBBIM_STYLE | \
            win32defines.RBBIM_TEXT

        # set the pointer for the text
        band_info.lpText = win32structures.LPWSTR(
            remote_mem.Address() + ctypes.sizeof(band_info))
        band_info.cch = 2000

        # write the structure
        remote_mem.Write(band_info)

        # Fill the structure
        self.SendMessage(
            win32defines.RB_GETBANDINFOW,
            band_index,
            remote_mem)

        # read it back
        remote_mem.Read(band_info)

        # read the text
        band_info.text = ctypes.create_unicode_buffer(2000)
        remote_mem.Read(band_info.text, remote_mem.Address() + ctypes.sizeof(band_info))

        band_info.text = band_info.text.value

        del remote_mem
        return band_info


    #----------------------------------------------------------------
    def GetToolTipsControl(self):
        "Return the tooltip control associated with this control"
        tips_handle = self.SendMessage(win32defines.RB_GETTOOLTIPS)

        if tips_handle:
            return ToolTipsWrapper(tips_handle)

    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts of the Rebar"
        texts = [self.WindowText()]
        for i in range(0, self.BandCount()):
            band = self.GetBand(i)
            lines = band.text.split('\n')
            if lines:
                texts.append(lines[0])
            else:
                texts.append(band.text)

        return texts



class ToolTip(object):
    "Class that Wraps a single tip from a ToolTip control"
    def __init__(self, ctrl, tip_index):
        "Read the required information"
        self.ctrl = ctrl
        self.index = tip_index

        remote_mem = RemoteMemoryBlock(self.ctrl)
        tipinfo = win32structures.TOOLINFOW()
        tipinfo.cbSize = ctypes.sizeof(tipinfo)
        #tipinfo.uId = self.index
        tipinfo.lpszText = remote_mem.Address() + \
            ctypes.sizeof(tipinfo) + 1

        remote_mem.Write(tipinfo)

        self.ctrl.SendMessage(
            win32defines.TTM_ENUMTOOLSW,
            self.index,
            remote_mem)

        remote_mem.Read(tipinfo)

        self.info = tipinfo

        # now get the text
        self.info.lpszText = remote_mem.Address() + \
            ctypes.sizeof(self.info) + 1

        remote_mem.Write(self.info)

        self.ctrl.SendMessage(
            win32defines.TTM_GETTEXTW, 160, remote_mem)

        # There is no way to determine the required buffer size.
        # However, tool text, as returned at the lpszText member of the TOOLINFO structure,
        # has a maximum length of 80 TCHARs, including the terminating NULL.
        # If the text exceeds this length, it is truncated.
        # https://msdn.microsoft.com/en-us/library/windows/desktop/bb760375(v=vs.85).aspx
        text = ctypes.create_unicode_buffer(80)

        remote_mem.Read(text, self.info.lpszText)

        self.text = text.value

        del remote_mem




#====================================================================
class ToolTipsWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ToolTips common control (not fully implemented)"

    # mask this class as it is not ready for prime time yet!
    friendlyclassname = "ToolTips"
    windowclasses = ["tooltips_class32",
                     ".*ToolTip",
                     "#32774", "MS_WINNOTE", "VBBubble", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the instance"
        #HwndWrapper.HwndWrapper.__init__(self, hwnd)
        super(ToolTipsWrapper, self).__init__(hwnd)


    #----------------------------------------------------------------
    def GetTip(self, tip_index):
        "Return the particular tooltip"
        if tip_index >= self.ToolCount():
            raise IndexError(
                "tip_index %d greater then number of available tips: %d" %
                    (tip_index, self.ToolCount()))
        return ToolTip(self, tip_index)


    #----------------------------------------------------------------
    def ToolCount(self):
        "Return the number of tooltips"
        return self.SendMessage(win32defines.TTM_GETTOOLCOUNT)


    #----------------------------------------------------------------
    def GetTipText(self, tip_index):
        "Return the text of the tooltip"

        return ToolTip(self, tip_index).text

    #----------------------------------------------------------------
    def Texts(self):
        "Return the text of all the tooltips"
        texts = [self.WindowText(), ]
        for tip_index in range(0, self.ToolCount()):
            texts.append(self.GetTipText(tip_index))

        return texts


#====================================================================
class UpDownWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows UpDown common control "

    friendlyclassname = "UpDown"
    windowclasses = ["msctls_updown32", "msctls_updown", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        #HwndWrapper.HwndWrapper.__init__(self, hwnd)
        super(UpDownWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def GetValue(self):
        "Get the current value of the UpDown control"
        pos = win32functions.SendMessage(self, win32defines.UDM_GETPOS, win32structures.LPARAM(0), win32structures.WPARAM(0))
        return win32functions.LoWord(pos)

    #----------------------------------------------------------------
    def GetBase(self):
        "Get the base the UpDown control (either 10 or 16)"
        return self.SendMessage(win32defines.UDM_GETBASE)

    #----------------------------------------------------------------
    def SetBase(self, base_value):
        "Get the base the UpDown control (either 10 or 16)"
        return self.SendMessage(win32defines.UDM_SETBASE, base_value)

    #----------------------------------------------------------------
    def GetRange(self):
        "Return the lower, upper range of the up down control"
        updown_range = self.SendMessage(win32defines.UDM_GETRANGE)
        updown_range = (
            win32functions.HiWord(updown_range),
            win32functions.LoWord(updown_range)
            )
        return updown_range

    #----------------------------------------------------------------
    def GetBuddyControl(self):
        "Get the buddy control of the updown control"
        #from wraphandle import WrapHandle
        #from HwndWrapper import WrapHandle
        buddy_handle = self.SendMessage(win32defines.UDM_GETBUDDY)
        return HwndWrapper.HwndWrapper(buddy_handle)

    #----------------------------------------------------------------
    def SetValue(self, new_pos):
        "Set the value of the of the UpDown control to some integer value"
        for _ in range(3):
            result = ctypes.c_long()
            win32functions.SendMessageTimeout(self,
                win32defines.UDM_SETPOS, 0, win32functions.MakeLong(0, new_pos),
                win32defines.SMTO_NORMAL,
                int(Timings.after_updownchange_wait * 1000),
                ctypes.byref(result))
            win32functions.WaitGuiThreadIdle(self)
            time.sleep(Timings.after_updownchange_wait)
            if self.GetValue() == new_pos:
                break
            # make one more attempt elsewhere

    #----------------------------------------------------------------
    def Increment(self):
        "Increment the number in the UpDown control by one"
        # hmmm - VM_SCROLL and UDN_DELTAPOS don't seem to be working for me :-(
        # I will fake it for now either use Click, or GetValue() + 1
        rect = self.ClientRect()
        self.ClickInput(coords=(rect.left + 5, rect.top + 5))
        
        #self.SetValue(self.GetValue() + 1)
        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_updownchange_wait)

    #----------------------------------------------------------------
    def Decrement(self):
        "Decrement the number in the UpDown control by one"
        rect = self.ClientRect()
        self.ClickInput(coords=(rect.left + 5, rect.bottom - 5))
        
        #self.SetValue(self.GetValue() - 1)
        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_updownchange_wait)


#====================================================================
class TrackbarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Trackbar common control "

    friendlyclassname = "Trackbar"
    windowclasses = ["msctls_trackbar", ]

#
#    #----------------------------------------------------------------
#    def GetNumTicks(self):
#        return self.SendMessage(win32defines.TBM_GETNUMTICS)
#
#    #----------------------------------------------------------------
#    def GetPos(self):
#        return self.SendMessage(win32defines.TBM_GETPOS)
#
#    #----------------------------------------------------------------
#    def GetRangeMax(self):
#        return self.SendMessage(win32defines.TBM_GETRANGEMAX)
#
#    #----------------------------------------------------------------
#    def GetRangeMin(self):
#        return self.SendMessage(win32defines.TBM_GETRANGEMIN)
#
#    #----------------------------------------------------------------
#    def GetToolTipsControl(self):
#        "Return the tooltip control associated with this control"
#        return ToolTipsWrapper(self.SendMessage(win32defines.TBM_GETTOOLTIPS))


#====================================================================
class AnimationWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Animation common control "

    friendlyclassname = "Animation"
    windowclasses = ["SysAnimate32", ]


#====================================================================
class ComboBoxExWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ComboBoxEx common control "

    friendlyclassname = "ComboBoxEx"
    windowclasses = ["ComboBoxEx32", ]
    has_title = False


#====================================================================
class DateTimePickerWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows DateTimePicker common control "

    friendlyclassname = "DateTimePicker"
    windowclasses = ["SysDateTimePick32", ]
    has_title = False

    #----------------------------------------------------------------
    def GetTime(self):
        "Get the currently selected time"
        
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()
        remote_mem.Write(system_time)
        
        res = self.SendMessage(win32defines.DTM_GETSYSTEMTIME, 0, remote_mem)
        remote_mem.Read(system_time)
        del remote_mem
        
        if res != win32defines.GDT_VALID:
            raise RuntimeError('Failed to get time from Date Time Picker (result = ' + str(res) + ')')
        
        #year = system_time.wYear
        #month = system_time.wMonth
        #day_of_week = system_time.wDayOfWeek
        #day = system_time.wDay
        #hour = system_time.wHour
        #minute = system_time.wMinute
        #second = system_time.wSecond
        #milliseconds = system_time.wMilliseconds
        #return (year, month, day_of_week, day, hour, minute, second, milliseconds)
        return system_time 

    #----------------------------------------------------------------
    def SetTime(self, year, month, day_of_week, day, hour, minute, second, milliseconds):
        "Get the currently selected time"
        
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()
        
        system_time.wYear = year
        system_time.wMonth = month
        system_time.wDayOfWeek = day_of_week
        system_time.wDay = day
        system_time.wHour = hour
        system_time.wMinute = minute
        system_time.wSecond = second
        system_time.wMilliseconds = milliseconds
        
        remote_mem.Write(system_time)
        
        res = self.SendMessage(win32defines.DTM_SETSYSTEMTIME, win32defines.GDT_VALID, remote_mem)
        del remote_mem
        
        if res == 0:
            raise RuntimeError('Failed to set time in Date Time Picker')


#====================================================================
class HotkeyWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Hotkey common control "

    friendlyclassname = "Hotkey"
    windowclasses = ["msctls_hotkey32", ]
    has_title = False


#====================================================================
class IPAddressWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows IPAddress common control "

    friendlyclassname = "IPAddress"
    windowclasses = ["SysIPAddress32", ]
    has_title = False


#====================================================================
class CalendarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Calendar common control "

    friendlyclassname = "Calendar"
    windowclasses = ["SysMonthCal32", ]
    has_title = False


#====================================================================
class PagerWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Pager common control "

    friendlyclassname = "Pager"
    windowclasses = ["SysPager", ]

    def GetPosition(self):
        "Return the current position of the pager"
        return self.SendMessage(win32defines.PGM_GETPOS)

    def SetPosition(self, pos):
        "Set the current position of the pager"
        return self.SendMessage(win32defines.PGM_SETPOS, pos)


#====================================================================
class ProgressWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Progress common control "

    friendlyclassname = "Progress"
    windowclasses = ["msctls_progress", "msctls_progress32", ]
    has_title = False


    def GetPosition(self):
        "Return the current position of the progress bar"
        return self.SendMessage(win32defines.PBM_GETPOS)

    def SetPosition(self, pos):
        "Set the current position of the progress bar"
        return self.SendMessage(win32defines.PBM_SETPOS, pos)

    def GetState(self):
        """Get the state of the progress bar
        
        State will be one of the following constants:
         * PBST_NORMAL
         * PBST_ERROR
         * PBST_PAUSED
        """
        return self.SendMessage(win32defines.PBM_GETSTATE)

    def GetStep(self):
        "Get the step size of the progress bar"
        return self.SendMessage(win32defines.PBM_GETSTEP)

    def StepIt(self):
        "Move the progress bar one step size forward"
        return self.SendMessage(win32defines.PBM_STEPIT)

#
##
###HwndWrapper._HwndWrappers["ComboBoxEx32"] = ComboBoxEx
##




##
##
###====================================================================
##class ComboBoxEx(Controls_Standard.ComboBox):
##    #----------------------------------------------------------------
##    def __init__(self, hwndOrXML):
#        Window.__init__(self, hwndOrXML)
##
#        if isinstance(hwndOrXML, (int, long)):
##            comboCntrl = SendMessage(
##                hwndOrXML,
##                CBEM_GETCOMBOCONTROL,
##                0,
##                0)
##
##            print "--"*20, comboCntrl
##            Controls_Standard.ComboBox.__init__(self, comboCntrl)
##            print self.DroppedRect
##
##
##
##            droppedRect = win32structures.RECT()
##
##            SendMessage(
##                self,
##                CB_GETDROPPEDCONTROLRECT,
##                0,
##                ctypes.byref(droppedRect))
##
##            props['DroppedRect'] = droppedRect
#
#
#
#
#
#
#            # find out how many text items are in the combobox
#            numItems = SendMessage(
#                self,
#                CB_GETCOUNT,
#                0,
#                0)
#
#            print "*"*20, numItems
##            remote_mem = RemoteMemoryBlock(self)
##
##
##            # get the text for each item in the combobox
##            while True:
##                item = COMBOBOXEXITEMW()
##
##                item.mask = CBEIF_TEXT
##                item.cchTextMax = 4000
##                item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
##
##                remote_mem.Write(item)
##
##                retval = SendMessage (
##                    self,
##                    CBEM_GETITEMW,
##                    0,
##                    remote_mem
##                    )
##
##                if retval:
##                    item = remote_mem.Read(item)
##
##                    # Read the remote text string
##                  charData = ctypes.create_unicode_buffer(4000)
##                    remote_mem.Read(charData, item.pszText)
##                    self.Titles.append(charData.value)
##                else:
##                    break
##
#
#        else:
#
#            # get the dropped Rect form
#            droppedRect = XMLToRect(hwndOrXML.find("DROPPEDRECT"))
#            props['DroppedRect'] = droppedRect

