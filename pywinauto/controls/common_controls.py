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

"Classes that wrap the Windows Common controls"

__revision__ = "$Revision$"

import time
import ctypes

from pywinauto import win32functions
from pywinauto import win32defines
from pywinauto import win32structures
from pywinauto import findbestmatch
import HwndWrapper

from pywinauto.timings import Timings

class AccessDenied(RuntimeError):
    "Raised when we cannot allocate memory in the control's process"
    pass



#====================================================================
class _RemoteMemoryBlock(object):
    "Class that enables reading and writing memory in a different process"
    #----------------------------------------------------------------
    def __init__(self, handle, size = 8192):
        "Allocatte the memory"
        self.memAddress = 0
        self.fileMap = 0

        self._as_parameter_ = self.memAddress

        process_id = ctypes.c_long()
        win32functions.GetWindowThreadProcessId(
            handle, ctypes.byref(process_id))

        self.process = win32functions.OpenProcess(
                win32defines.PROCESS_VM_OPERATION |
                win32defines.PROCESS_VM_READ |
                win32defines.PROCESS_VM_WRITE,
            0,
            process_id)

        if not self.process:
            raise AccessDenied(
                str(ctypes.WinError()) + "process: %d",
                process_id.value)

        if win32functions.GetVersion() < 2147483648L:
            self.memAddress = win32functions.VirtualAllocEx(
                self.process,	# remote process
                0,				# let Valloc decide where
                size,			# how much to allocate
                    win32defines.MEM_RESERVE |
                    win32defines.MEM_COMMIT,	# allocation type
                win32defines.PAGE_READWRITE	# protection
                )

            if not self.memAddress:
                raise ctypes.WinError()

        else:
            raise RuntimeError("Win9x allocation not supported")

        self._as_parameter_ = self.memAddress

    #----------------------------------------------------------------
    def __del__(self):
        "Ensure that the memory is Freed"
        # Free the memory in the remote process's address space

        if self.process:
            ret = win32functions.VirtualFreeEx(
                self.process, self.memAddress, 0, win32defines.MEM_RELEASE)

            if not ret:
                raise ctypes.WinError()

    #----------------------------------------------------------------
    def Address(self):
        "Return the address of the memory block"
        return self.memAddress

    #----------------------------------------------------------------
    def Write(self, data):
        "Write data into the memory block"
        # write the data from this process into the memory allocated
        # from the other process
        ret = win32functions.WriteProcessMemory(
            self.process,
            self.memAddress,
            ctypes.pointer(data),
            ctypes.sizeof(data),
            0);

        if not ret:
            raise ctypes.WinError()

    #----------------------------------------------------------------
    def Read(self, data, address = None):
        "Read data from the memory block"
        if not address:
            address = self.memAddress

        ret = win32functions.ReadProcessMemory(
            self.process, address, ctypes.byref(data), ctypes.sizeof(data), 0)

        # disabled as it often returns an error - but
        # seems to work fine anyway!!
        if not ret:
            raise ctypes.WinError()

        return data




#====================================================================
class ListViewWrapper(HwndWrapper.HwndWrapper):
    """Class that wraps Windows ListView common control

    This class derives from HwndWrapper - so has all the methods o
    that class also

    **see** HwndWrapper.HwndWrapper_

    .. _HwndWrapper.HwndWrapper: class-pywinauto.controls.HwndWrapper.HwndWrapper.html

    """

    friendlyclassname = "ListView"
    windowclasses = ["SysListView32", r"WindowsForms\d*\.SysListView32\..*", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ListViewWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            'ColumnCount',
            'ItemCount',
            'Columns',
            'Items'])

    #-----------------------------------------------------------
    def ColumnCount(self):
        """Return the number of columns"""
        return self.GetHeaderControl().ItemCount()

    #-----------------------------------------------------------
    def ItemCount(self):
        "The number of items in the ListView"
        return self.SendMessage(win32defines.LVM_GETITEMCOUNT)

    #-----------------------------------------------------------
    def GetHeaderControl(self):
        "Returns the Header control associated with the ListView"
        #from wraphandle import WrapHandle
        #from HwndWrapper import WrapHandle
        return HwndWrapper.HwndWrapper(
            self.SendMessage(win32defines.LVM_GETHEADER))

    #-----------------------------------------------------------
    def GetColumn(self, col_index):
        "Get the information for a column of the ListView"

        col_props = {}

        col = win32structures.LVCOLUMNW()
        col.mask = \
            win32defines.LVCF_FMT | \
            win32defines.LVCF_IMAGE | \
            win32defines.LVCF_ORDER | \
            win32defines.LVCF_SUBITEM | \
            win32defines.LVCF_TEXT | \
            win32defines.LVCF_WIDTH

        remote_mem = _RemoteMemoryBlock(self)

        col.cchTextMax = 2000
        col.item = remote_mem.Address() + ctypes.sizeof(col) + 1


        # put the information in the memory that the
        # other process can read/write
        remote_mem.Write(col)

        # ask the other process to update the information
        retval = self.SendMessage(
            win32defines.LVM_GETCOLUMNW,
            col_index,
            remote_mem)

        col = remote_mem.Read(col)

        # if that succeeded then there was a column
        if retval:
            col = remote_mem.Read(col)

            text = ctypes.create_unicode_buffer(1999)
            remote_mem.Read(text, col.pszText)

            col_props['order'] = col.iOrder
            col_props['text'] = text.value
            col_props['format'] = col.fmt
            col_props['width'] = col.cx
            col_props['image'] = col.iImage
            col_props['subitem'] = col.iSubItem

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
        # set up a memory block in the remote application
        remote_mem = _RemoteMemoryBlock(self)
        rect = win32structures.RECT()

        rect.left = win32defines.LVIR_SELECTBOUNDS

        # Write the local RECT structure to the remote memory block
        remote_mem.Write(rect)

        # Fill in the requested item
        retval = self.SendMessage(
            win32defines.LVM_GETITEMRECT,
            item_index,
            remote_mem)

        # if it succeeded
        if not retval:
        	del remote_mem
        	raise RuntimeError("Did not succeed in getting rectable")

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect


    #-----------------------------------------------------------
    def GetItem(self, item_index, subitem_index = 0):
        "Return the item of the list view"

        item_data = {}

        # set up a memory block in the remote application
        remote_mem = _RemoteMemoryBlock(self)

        # set up the item structure to get the text
        item = win32structures.LVITEMW()
        item.mask = \
            win32defines.LVIF_TEXT | \
            win32defines.LVIF_IMAGE | \
            win32defines.LVIF_INDENT | \
            win32defines.LVIF_STATE

        item.iItem = item_index
        item.iSubItem = subitem_index
        item.stateMask = ctypes.c_uint(-1)

        item.cchTextMax = 2000
        item.pszText = remote_mem.Address() + \
            ctypes.sizeof(item) + 1

        # Write the local LVITEM structure to the remote memory block
        remote_mem.Write(item)

        # Fill in the requested item
        retval = self.SendMessage(
            win32defines.LVM_GETITEMW,
            item_index,
            remote_mem)

        # if it succeeded
        if retval:

            remote_mem.Read(item)

            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            # and add it to the titles
            item_data['text'] = char_data.value
            item_data['state'] = item.state
            item_data['image'] = item.iImage
            item_data['indent'] = item.iIndent

        else:
            raise RuntimeError(
                "We should never get to this part of ListView.GetItem()")

        del remote_mem

        return item_data

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
                items.append(self.GetItem(item_index, subitem_index))

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

        self.VerifyActionable()

        lvitem = win32structures.LVITEMW()

        lvitem.mask = win32defines.LVIF_STATE
        lvitem.state = 0x1000
        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK

        remote_mem = _RemoteMemoryBlock(self)
        remote_mem.Write(lvitem)

        self.SendMessageTimeout(
            win32defines.LVM_SETITEMSTATE, item, remote_mem)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listviewcheck_wait)

        del remote_mem

    #-----------------------------------------------------------
    def Check(self, item):
        "Check the ListView item"

        self.VerifyActionable()

        lvitem = win32structures.LVITEMW()

        lvitem.mask = win32defines.LVIF_STATE
        lvitem.state = 0x2000
        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK

        remote_mem = _RemoteMemoryBlock(self)
        remote_mem.Write(lvitem)

        self.SendMessageTimeout(
            win32defines.LVM_SETITEMSTATE, item, remote_mem)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listviewcheck_wait)

        del remote_mem

    #-----------------------------------------------------------
    def IsChecked(self, item):
        "Return whether the ListView item is checked or not"
        state = self.SendMessage(
            win32defines.LVM_GETITEMSTATE,
            item,
            win32defines.LVIS_STATEIMAGEMASK)

        return state & 0x2000 == 0x2000

    #-----------------------------------------------------------
    def IsSelected(self, item):
        "Return True if the item is selected"
        return win32defines.LVIS_SELECTED == self.SendMessage(
            win32defines.LVM_GETITEMSTATE, item, win32defines.LVIS_SELECTED)

    #-----------------------------------------------------------
    def IsFocused(self, item):
        "Return True if the item has the focus"
        return win32defines.LVIS_FOCUSED == self.SendMessage(
            win32defines.LVM_GETITEMSTATE, item, win32defines.LVIS_FOCUSED)

    #-----------------------------------------------------------
    def _modify_selection(self, item, to_select):
        """Change the selection of the item

        item is the item you want to chagne
        to_slect shoudl be tru to select the item and false
        to deselect the item
        """

        self.VerifyActionable()

        if item >= self.ItemCount():
            raise IndexError("There are only %d items in the list view not %d"%
                (self.ItemCount(), item + 1))

        # first we need to change the state of the item
        lvitem = win32structures.LVITEMW()
        lvitem.mask = win32defines.LVIF_STATE

        if to_select:
            lvitem.state = win32defines.LVIS_SELECTED

        lvitem.stateMask = win32defines.LVIS_SELECTED

        remote_mem = _RemoteMemoryBlock(self)
        remote_mem.Write(lvitem)

        self.SendMessageTimeout(
            win32defines.LVM_SETITEMSTATE, item, remote_mem)

        # now we need to notify the parent that the state has chnaged
        nmlv = win32structures.NMLISTVIEW()
        nmlv.hdr.hwndFrom = self.handle
        nmlv.hdr.idFrom = self.ControlID()
        nmlv.hdr.code = win32defines.LVN_ITEMCHANGING

        nmlv.iItem = item
        #nmlv.iSubItem = 0
        nmlv.uNewState = win32defines.LVIS_SELECTED
        #nmlv.uOldState = 0
        nmlv.uChanged = win32defines.LVIS_SELECTED
        nmlv.ptAction = win32structures.POINT()

        remote_mem.Write(nmlv)

        self.Parent().SendMessageTimeout(
            win32defines.WM_NOTIFY,
            self.ControlID(),
            remote_mem)

        del remote_mem

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listviewselect_wait)

    #-----------------------------------------------------------
    def Select(self, item):
        """Mark the item as selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        self._modify_selection(item, True)

    #-----------------------------------------------------------
    def Deselect(self, item):
        """Mark the item as not selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised"""
        self._modify_selection(item, False)

    # Naming is not clear - so create an alias.
    #UnSelect = Deselect

    #-----------------------------------------------------------
    def GetSelectedCount(self):
        "Return the number of selected items"

        return self.SendMessage(win32defines.LVM_GETSELECTEDCOUNT)



    # commented out as we can get these strings from the header
    #					col = remote_mem.Read(col)
    #
    #                   charData = ctypes.create_unicode_buffer(2000)
    #
    #					ret = remote_mem.Read(charData, col.pszText)
    #
    #					self.Titles.append(charData.value)
    #				else:
    #					break



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

    #----------------------------------------------------------------
    def Rectangle(self):
        "Return the rectangle of the item"
        remote_mem = _RemoteMemoryBlock(self.tree_ctrl)

        # this is a bit weird
        # we have to write the element handle
        # but we read the Rectangle afterwards!
        remote_mem.Write(ctypes.c_long(self.elem))

        ret = self.tree_ctrl.SendMessage(
            win32defines.TVM_GETITEMRECT, 0, remote_mem)

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
    def Children(self):
        "Return the direct children of this control"
        if self.Item().cChildren not in (0, 1):
            print "##### not dealing with that TVN_GETDISPINFO stuff yet"
            pass

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

            #else:
            #    raise ctypes.WinError()

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
    def _readitem(self):
        "Read the treeview item"
        remote_mem = _RemoteMemoryBlock(self.tree_ctrl)

        item = win32structures.TVITEMW()
        item.mask =  win32defines.TVIF_TEXT | \
            win32defines.TVIF_HANDLE | \
            win32defines.TVIF_CHILDREN | \
            win32defines.TVIF_STATE

        # set the address for the text
        item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
        item.cchTextMax = 2000
        item.hItem = self.elem
        item.stateMask = -1

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
            raise ctypes.WinError()

        return item, text



#====================================================================
class TreeViewWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows TreeView common control"

    friendlyclassname = "TreeView"
    windowclasses = ["SysTreeView32", r"WindowsForms\d*\.SysTreeView32\..*"]

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
        texts = [self.WindowText(), self.Root().Text()]

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

        return _treeview_element(root_elem, self)


    #----------------------------------------------------------------
    def GetProperties(self):
        "Get the properties for the control as a dictionary"
        props = super(TreeViewWrapper, self).GetProperties()

        props['ItemCount'] = self.ItemCount()

        return props


    #----------------------------------------------------------------
    def GetItem(self, path):
        "Read the TreeView item"

        # work just based on integers for now

        current_elem = self.Root()

        # get the correct lowest level item
        for i in range(0, path[0]):
            current_elem = current_elem.Next()

            if current_elem is None:
                raise IndexError("Root Item '%s' does not have %d sibling(s)"%
                    (self.Root().WindowText(), i + 1))

        self.SendMessageTimeout(
            win32defines.TVM_EXPAND,
            win32defines.TVE_EXPAND,
            current_elem)

        # now for each of the lower levels
        # just index into it's children
        for child_index in path[1:]:
            try:
                current_elem = current_elem.Children()[child_index]
            except IndexError:
                raise IndexError("Item '%s' does not have %d children"%
                    (current_elem.WindowText(), child_index + 1))


            self.SendMessageTimeout(
                win32defines.TVM_EXPAND,
                win32defines.TVE_EXPAND,
                current_elem)

        return  current_elem

    #----------------------------------------------------------------
    def Select(self, path):
        "Select the treeview item"
        elem = self.GetItem(path)
        self.SendMessageTimeout(
            win32defines.TVM_SELECTITEM, # message
            win32defines.TVGN_CARET,     # how to select
            elem)                 # item to select

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_treeviewselect_wait)

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
            elem)                 # item to select

        win32functions.WaitGuiThreadIdle(self)


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
##        remote_mem = _RemoteMemoryBlock(self)
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
#        remote_mem = _RemoteMemoryBlock(self)
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
    windowclasses = ["SysHeader32", ]

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

        remote_mem = _RemoteMemoryBlock(self)
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

        remote_mem = _RemoteMemoryBlock(self)

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
#        remote_mem = _RemoteMemoryBlock(self)
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
        remote_mem = _RemoteMemoryBlock(self)

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
        remote_mem = _RemoteMemoryBlock(self)

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


        remote_mem = _RemoteMemoryBlock(self)

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

        remote_mem = _RemoteMemoryBlock(self)

        textlen = self.SendMessage(
            win32defines.SB_GETTEXTLENGTHW,
            part_index,
            0
        )

        #draw_operation = win32functions.HiWord(textlen)
        textlen = win32functions.LoWord(textlen)

        # get the text for this item
        text = ctypes.create_unicode_buffer(textlen + 1)
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

        remote_mem = _RemoteMemoryBlock(self)

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
#        remote_mem = _RemoteMemoryBlock(self)
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

        remote_mem = _RemoteMemoryBlock(self)

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

        # if it's a string then find the index of
        # the tab with that text
        if isinstance(tab, basestring):
            # find the string in the tab control
            best_text = findbestmatch.find_best_match(
                tab, self.Texts(), self.Texts())
            tab = self.Texts().index(best_text) - 1

        if tab >= self.TabCount():
            raise IndexError(
                "Only %d tabs available you asked for tab %d (zero based)" % (
                self.TabCount(),
                tab))

        self.SendMessageTimeout(win32defines.TCM_SETCURFOCUS, tab)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_tabselect_wait)

        return self


#====================================================================
class TBButtonWrappper(win32structures.TBBUTTONINFOW):
    "Simple wrapper around TBBUTTONINFOW to allow setting new attributes"
    pass

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
    def GetButton(self, button_index):
        "Return information on the Toolbar button"

        if button_index >= self.ButtonCount():
            raise IndexError(
                "0 to %d are acceptiple for button_index",
                self.ButtonCount())

        remote_mem = _RemoteMemoryBlock(self)

        button = win32structures.TBBUTTON()

        remote_mem.Write(button)

        self.SendMessage(
            win32defines.TB_GETBUTTON, button_index, remote_mem)

        remote_mem.Read(button)

        button_info = TBButtonWrappper()
        button_info.cbSize = ctypes.sizeof(button_info)
        button_info.dwMask = win32defines.TBIF_TEXT | \
            win32defines.TBIF_COMMAND | \
            win32defines.TBIF_SIZE | \
            win32defines.TBIF_COMMAND | \
            win32defines.TBIF_STYLE | \
            win32defines.TBIF_STATE

        button_info.cchText = 2000

        # set the text address to after the structures
        button_info.pszText = remote_mem.Address() + \
            ctypes.sizeof(button_info)

        # fill the button_info structure
        remote_mem.Write(button_info)
        self.SendMessage(
            win32defines.TB_GETBUTTONINFOW,
            button.idCommand,
            remote_mem)
        remote_mem.Read(button_info)

        # read the text
        button_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(button_info.text, remote_mem.Address() + \
            ctypes.sizeof(button_info))

        button_info.text = button_info.text.value

        del remote_mem

        return button_info

    def Texts(self):
        "Return the texts of the Toolbar"
        texts = [self.WindowText()]
        for i in range(0, self.ButtonCount()):
            texts.append(self.GetButton(i).text)

        return texts

    def GetButtonRect(self, button_index):
        "Get the rectangle of a button on the toolbar"

        remote_mem = _RemoteMemoryBlock(self)

        rect = win32structures.RECT()

        remote_mem.Write(rect)

        self.SendMessage(
            win32defines.TB_GETRECT,
            button_index,
            remote_mem)

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect

    def GetToolTipsControl(self):
        "Return teh tooltip control associated with this control"
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
#        self.MoveMouse(coords = (x, y))
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
#        remote_mem = _RemoteMemoryBlock(self)
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

    def PressButton(self, button_identifier):
        "Find where the button is and click it"

        if isinstance(button_identifier, basestring):
            best_text = findbestmatch.find_best_match(
                button_identifier, self.Texts(), self.Texts())
            button_index = self.Texts().index(best_text) - 1

        else:
            button_index = button_identifier

        button = self.GetButton(button_index)

        self.SendMessageTimeout(
            win32defines.TB_PRESSBUTTON,
            button.idCommand,
            win32functions.MakeLong(1, 0))

        self.SendMessageTimeout(
            win32defines.TB_PRESSBUTTON,
            button.idCommand,
            win32functions.MakeLong(0, 0))

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_toobarpressbutton_wait)


#    #----------------------------------------------------------------
#    def _fill_toolbar_info(self):
#        "Get the information from the toolbar"
#        buttonCount = self.SendMessage(win32defines.TB_BUTTONCOUNT)
#        self._extra_props['ButtonCount'] = buttonCount
#
#        remote_mem = _RemoteMemoryBlock(self)
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
#    #		if button.fsStyle & TBSTYLE_DROPDOWN == TBSTYLE_DROPDOWN and \
#    #			(extendedStyle & TBSTYLE_EX_DRAWDDARROWS) != \
#    #                TBSTYLE_EX_DRAWDDARROWS:
#    #			props['Buttons'][-1]["DROPDOWNMENU"] = 1
#    #
#    #			self.SendMessage(WM_COMMAND, button.idCommand)
#    #
#    #			print "Pressing", text.value
#    #			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 1)
#    #			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 0)
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

        remote_mem = _RemoteMemoryBlock(self)

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
        band_info.pszText = ctypes.c_long(remote_mem.Address() + \
            ctypes.sizeof(band_info))
        band_info.cchText = 2000

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
        band_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(band_info.text, remote_mem.Address() + \
            ctypes.sizeof(band_info))

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
            texts.append(band.text)

        return texts



class ToolTip(object):
    "Class that Wraps a single tip from a ToolTip control"
    def __init__(self, ctrl, tip_index):
        "Read the required information"
        self.ctrl = ctrl
        self.index = tip_index

        remote_mem = _RemoteMemoryBlock(self.ctrl)
        tipinfo = win32structures.TOOLINFOW()
        tipinfo.cbSize = ctypes.sizeof(tipinfo)
        tipinfo.lpszText = remote_mem.Address() + \
            ctypes.sizeof(tipinfo) +1

        remote_mem.Write(tipinfo)

        ret = self.ctrl.SendMessage(
            win32defines.TTM_ENUMTOOLSW,
            self.index,
            remote_mem)

        if not ret:
            raise ctypes.WinError()

        remote_mem.Read(tipinfo)

        self.info = tipinfo

        # now get the text
        self.info.lpszText = remote_mem.Address() + \
            ctypes.sizeof(self.info) +1

        remote_mem.Write(self.info)

        self.ctrl.SendMessage(
            win32defines.TTM_GETTEXTW, 0, remote_mem)

        text = ctypes.create_unicode_buffer(2000)

        remote_mem.Read(text, self.info.lpszText)

        self.text = text.value

        del remote_mem




#====================================================================
class ToolTipsWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ToolTips common control (not fully implemented)"

    # mask this class as it is not ready for prime time yet!
    friendlyclassname = "ToolTips"
    windowclasses = ["tooltips_class32", ]

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
        pos = self.SendMessage(win32defines.UDM_GETPOS)
        return win32functions.LoWord(pos)

    #----------------------------------------------------------------
    def GetBase(self):
        "Get the base the UpDown control (either 10 or 16)"
        return self.SendMessage(win32defines.UDM_GETBASE)

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
        self.SendMessageTimeout(
            win32defines.UDM_SETPOS, 0, win32functions.MakeLong(0, new_pos))

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_updownchange_wait)

    #----------------------------------------------------------------
    def Increment(self):
        "Increment the number in the UpDown control by one"
        # hmmm - VM_SCROLL and UDN_DELTAPOS don't seem to be working for me :-(
        # I will fake it for now either use Click, or GetValue() + 1
        self.SetValue(self.GetValue() + 1)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_updownchange_wait)

    #----------------------------------------------------------------
    def Decrement(self):
        "Decrement the number in the UpDown control by one"
        self.SetValue(self.GetValue() - 1)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_updownchange_wait)


#====================================================================
class TrackbarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Trackbar common control "

    friendlyclassname = "Trackbar"
    windowclasses = ["msctls_trackbar", ]

#
#    #----------------------------------------------------------------
#	def GetNumTicks(self):
#		return self.SendMessage(win32defines.TBM_GETNUMTICS)
#
#    #----------------------------------------------------------------
#	def GetPos(self):
#		return self.SendMessage(win32defines.TBM_GETPOS)
#
#    #----------------------------------------------------------------
#	def GetRangeMax(self):
#		return self.SendMessage(win32defines.TBM_GETRANGEMAX)
#
#    #----------------------------------------------------------------
#	def GetRangeMin(self):
#		return self.SendMessage(win32defines.TBM_GETRANGEMIN)
#
#    #----------------------------------------------------------------
#    def GetToolTipsControl(self):
#        "Return teh tooltip control associated with this control"
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


#====================================================================
class DateTimePickerWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows DateTimePicker common control "

    friendlyclassname = "DateTimePicker"
    windowclasses = ["SysDateTimePick32", ]


#====================================================================
class HotkeyWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Hotkey common control "

    friendlyclassname = "Hotkey"
    windowclasses = ["msctls_hotkey32", ]


#====================================================================
class IPAddressWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows IPAddress common control "

    friendlyclassname = "IPAddress"
    windowclasses = ["SysIPAddress32", ]


#====================================================================
class CalendarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Calendar common control "

    friendlyclassname = "Calendar"
    windowclasses = ["SysMonthCal32", ]


#====================================================================
class PagerWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Pager common control "

    friendlyclassname = "Pager"
    windowclasses = ["SysPager", ]


#====================================================================
class ProgressWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Progress common control "

    friendlyclassname = "Progress"
    windowclasses = ["msctls_progress", ]





#
##
###HwndWrapper._HwndWrappers["ComboBoxEx32"] = ComboBoxEx
##




##
##
###====================================================================
##class ComboBoxEx(Controls_Standard.ComboBox):
##	#----------------------------------------------------------------
##	def __init__(self, hwndOrXML):
#		Window.__init__(self, hwndOrXML)
##
#		if isinstance(hwndOrXML, (int, long)):
##			comboCntrl = SendMessage(
##				hwndOrXML,
##				CBEM_GETCOMBOCONTROL,
##				0,
##				0)
##
##			print "--"*20, comboCntrl
##			Controls_Standard.ComboBox.__init__(self, comboCntrl)
##			print self.DroppedRect
##
##
##
##			droppedRect = win32structures.RECT()
##
##			SendMessage(
##				self,
##				CB_GETDROPPEDCONTROLRECT,
##				0,
##				ctypes.byref(droppedRect))
##
##			props['DroppedRect'] = droppedRect
#
#
#
#
#
#
#			# find out how many text items are in the combobox
#			numItems = SendMessage(
#				self,
#				CB_GETCOUNT,
#				0,
#				0)
#
#			print "*"*20, numItems
##			remote_mem = _RemoteMemoryBlock(self)
##
##
##			# get the text for each item in the combobox
##			while True:
##				item = COMBOBOXEXITEMW()
##
##				item.mask = CBEIF_TEXT
##				item.cchTextMax = 4000
##				item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
##
##				remote_mem.Write(item)
##
##				retval = SendMessage (
##					self,
##					CBEM_GETITEMW,
##					0,
##					remote_mem
##					)
##
##				if retval:
##					item = remote_mem.Read(item)
##
##					# Read the remote text string
##                  charData = ctypes.create_unicode_buffer(4000)
##					remote_mem.Read(charData, item.pszText)
##					self.Titles.append(charData.value)
##				else:
##					break
##
#
#		else:
#
#			# get the dropped Rect form
#			droppedRect = XMLToRect(hwndOrXML.find("DROPPEDRECT"))
#			props['DroppedRect'] = droppedRect
