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


import ctypes

from pywinauto import win32functions
from pywinauto import win32defines
from pywinauto import win32structures
from pywinauto import findbestmatch
import HwndWrapper

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
            # TODO - work in a way that cannot be denied (or fail gracefully)
            raise AccessDenied(
                str(ctypes.WinError()) + "process: %d",
                process_id.value)

        if win32functions.GetVersion() < 0x80000000:
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

    #----------------------------------------------------------------
    def __del__(self):
        "Ensure that the memory is Freed"
        # Free the memory in the remote process's address space
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

    #-----------------------------------------------------------
    def ColumnCount(self):
        """Return the number of columns"""
        return len(self.Columns())

    #-----------------------------------------------------------
    def ItemCount(self):
        "The number of items in the ListView"
        return self.SendMessage(win32defines.LVM_GETITEMCOUNT)

    #-----------------------------------------------------------
    def Columns(self):
        "Get the information on the columns of the ListView"
        cols = []

        remote_mem = _RemoteMemoryBlock(self)

        # Get each ListView columns text data
        index = 0
        while True:
            col = win32structures.LVCOLUMNW()
            col.mask = win32defines.LVCF_WIDTH | win32defines.LVCF_FMT
            #LVCF_TEXT, LVCF_SUBITEM, LVCF_IMAGE, LVCF_ORDER

            # put the information in the memory that the
            # other process can read/write
            remote_mem.Write(col)

            # ask the other process to update the information
            retval = self.SendMessage(
                win32defines.LVM_GETCOLUMNW,
                index,
                remote_mem.Address())

            col = remote_mem.Read(col)

            # if that succeeded then there was a column
            if retval:
                col = remote_mem.Read(col)

                cols.append(col)
            else:
                # OK - so it didn't work stop trying to get more columns
                break

            index += 1

        del (remote_mem)

        return cols


    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = HwndWrapper.HwndWrapper.GetProperties(self)

        # get selected item
        props['ColumnWidths'] = [col.cx for col in self.Columns()]

        props['ItemCount'] = self.ItemCount()

        props['ColumnCount'] = self.ColumnCount()
        if props['ColumnCount'] == 0:
            props['ColumnCount'] = 1
            props['ColumnWidths'] = [999, ] # never trunctated

        props['ItemData'] = []
        for item in self.Items():
            props['ItemData'].append(dict(
                state = item.state,
                image = item.iImage,
                indent = item.iIndent
            ))

        return props


    #-----------------------------------------------------------
    def GetItem(self, item_index, subitem_index = 0):
        "Return the item of the list view"

        # set up a memory block in the remote application
        remote_mem = _RemoteMemoryBlock(self)

        # set up the item structure to get the text
        item = win32structures.LVITEMW()
        item.iSubItem = subitem_index
        item.pszText = remote_mem.Address() + \
            ctypes.sizeof(item) + 1
        item.cchTextMax = 2000
        item.mask = win32defines.LVIF_TEXT

        # Write the local LVITEM structure to the remote memory block
        remote_mem.Write(item)

        # get the text for the requested item
        retval = self.SendMessage(
            win32defines.LVM_GETITEMTEXTW,
            item_index,
            remote_mem.Address())

        # if it succeeded
        if retval:

            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            # and add it to the titles
            item.Text = char_data.value
        else:
            item.Text  = ''

        del remote_mem

        return item

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
        texts = [self.Text()]
        texts.extend([item.Text for item in self.Items()])
        return texts


    #-----------------------------------------------------------
    # TODO: Make the RemoteMemoryBlock stuff more automatic!
    def UnCheck(self, item):
        "Uncheck the ListView item"

        self.VerifyActionable()

        lvitem = win32structures.LVITEMW()

        lvitem.mask = win32defines.LVIF_STATE
        lvitem.state = 0x1000
        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK

        remote_mem = _RemoteMemoryBlock(self)
        remote_mem.Write(lvitem)

        self.SendMessage(
            win32defines.LVM_SETITEMSTATE, item, remote_mem.Address())

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

        self.SendMessage(
            win32defines.LVM_SETITEMSTATE, item, remote_mem.Address())

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
    def Select(self, item):
        "Mark the item as selected"

        self.VerifyActionable()

        # first we need to change the state of the item
        lvitem = win32structures.LVITEMW()
        lvitem.mask = win32defines.LVIF_STATE
        lvitem.state = win32defines.LVIS_SELECTED
        lvitem.stateMask = win32defines.LVIS_SELECTED

        remote_mem = _RemoteMemoryBlock(self)
        remote_mem.Write(lvitem)

        self.SendMessage(
            win32defines.LVM_SETITEMSTATE, item, remote_mem.Address())


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

        self.Parent().SendMessage(
            win32defines.WM_NOTIFY,
            self.ControlID(),
            remote_mem.Write(lvitem))

        del remote_mem


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
            win32defines.TVM_GETITEMRECT, 0, remote_mem.Address())

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
            remote_mem.Address())

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
    def Count(self):
        "Return the number of items"
        return self.SendMessage(win32defines.TVM_GETCOUNT)

    #----------------------------------------------------------------
    def Texts(self):
        "Return all the text for the tree view"
        texts = [self.Text(), self.Root().Text()]

        elements = self.Root().SubElements()

        texts.extend(elem.Text() for elem in elements)

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
        props = HwndWrapper.HwndWrapper.GetProperties(self)

        props['Count'] = self.Count()

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
                    (self.Root().Text(), i + 1))

        self.SendMessage(
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
                    (current_elem.Text(), child_index + 1))


            self.SendMessage(
                win32defines.TVM_EXPAND,
                win32defines.TVE_EXPAND,
                current_elem)

        return  current_elem

    #----------------------------------------------------------------
    def Select(self, path):
        "Select the treeview item"
        elem = self.GetItem(path)
        self.SendMessage(
            win32defines.TVM_SELECTITEM, # message
            win32defines.TVGN_CARET,     # how to select
            elem)                 # item to select


    #-----------------------------------------------------------
    def IsSelected(self, path):
        "Return True if the item is selected"
        return win32defines.TVIS_SELECTED  == (win32defines.TVIS_SELECTED & \
            self.GetItem(path).State())

    #----------------------------------------------------------------
    def EnsureVisible(self, path):
        "Make sure that the TreeView item is visible"
        elem = self.GetItem(path)
        self.SendMessage(
            win32defines.TVM_ENSUREVISIBLE, # message
            win32defines.TVGN_CARET,     # how to select
            elem)                 # item to select


#
#   #-----------------------------------------------------------
#    # TODO: Make the RemoteMemoryBlock stuff more automatic!
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
##            win32defines.LVM_SETITEMSTATE, item, remote_mem.Address())
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
#            win32defines.LVM_SETITEMSTATE, item, remote_mem.Address())
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
    def Count(self):
        "Return the number of columns in this header"
        # get the number of items in the header...
        return self.SendMessage(win32defines.HDM_GETITEMCOUNT)

    #----------------------------------------------------------------
    def ColumnRectangle(self, column_index):
        "Return the rectangle for the column specified by column_index"

        remote_mem = _RemoteMemoryBlock(self)
        # get the column rect
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        retval = self.SendMessage(
            win32defines.HDM_GETITEMRECT,
            column_index,
            remote_mem.Address())

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

        for col_index in range(0, self.Count()):

            rects.append(self.ColumnRectangle(col_index))

        return rects


    #----------------------------------------------------------------
    def ColumnText(self, column_index):
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
            remote_mem.Address())

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
        texts = [self.Text(), ]
        for i in range(0, self.Count()):
            texts.append(self.ColumnText(i))

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
#                remote_mem.Address())
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
            remote_mem.Address()
        )
        borders = remote_mem.Read(borders)
        borders_widths = {}
        borders_widths['Horizontal'] = borders[0]
        borders_widths['Vertical'] = borders[1]
        borders_widths['Inter'] = borders[2]

        del remote_mem

        return borders_widths

    #----------------------------------------------------------------
    def NumParts(self):
        "Return the number of parts"
        # get the number of parts for this status bar
        return self.SendMessage(
            win32defines.SB_GETPARTS,
            0,
            0 )

    #----------------------------------------------------------------
    def PartWidths(self):
        "Return the widths of the parts"
        remote_mem = _RemoteMemoryBlock(self)

        # get the number of parts for this status bar
        parts = (ctypes.c_int * self.NumParts())()
        remote_mem.Write(parts)
        self.SendMessage(
            win32defines.SB_GETPARTS,
            self.NumParts(),
            remote_mem.Address()
        )

        parts = remote_mem.Read(parts)

        del remote_mem

        return [int(part) for part in parts]

    #----------------------------------------------------------------
    def GetPartRect(self, part_index):
        "Return the rectangle of the part specified by part_index"
        remote_mem = _RemoteMemoryBlock(self)

        # get the rectangle for this item
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        self.SendMessage(
            win32defines.SB_GETRECT,
            part_index,
            remote_mem.Address())

        rect = remote_mem.Read(rect)
        del remote_mem
        return rect

    #----------------------------------------------------------------
    def ClientRects(self):
        "Return the client rectangles for the control"
        rects = [self.ClientRect()]

        for i in range(self.NumParts()):
            rects.append(self.GetPartRect(i))

        return rects

    #----------------------------------------------------------------
    def GetPartText(self, part_index):
        "Return the text of the part specified by part_index"

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
            remote_mem.Address()
        )

        text = remote_mem.Read(text)

        del remote_mem
        return text.value


    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts for the control"
        texts = [self.Text()]

        for i in range(self.NumParts()):
            texts.append(self.GetPartText(i))

        return texts

    #----------------------------------------------------------------
    def GetProperties(self):
        "Return the properties fo the StatusBar"
        props = HwndWrapper.GetProperties(self)

        props['BorderWidths'] = self.BorderWidths()




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

        self._extra_props = {}
        self._extra_clientrects = []
        self._extra_texts = []
        self._fill_tabcontrol_info()

    #----------------------------------------------------------------
    def _fill_tabcontrol_info(self):
        "Get the information from the Tab control"
        #tooltipHandle = self.SendMessage(win32defines.TCM_GETTOOLTIPS)

        remote_mem = _RemoteMemoryBlock(self)

        for i in range(0, self.TabCount()):

            item = win32structures.TCITEMW()
            item.mask = win32defines.TCIF_STATE | win32defines.TCIF_TEXT
            item.cchTextMax = 1999
            item.pszText = remote_mem.Address() + ctypes.sizeof(item)
            remote_mem.Write(item)

            self.SendMessage(
                win32defines.TCM_GETITEMW, i, remote_mem.Address())

            remote_mem.Read(item)

            self._extra_props.setdefault('TabState', []).append(item.dwState)

            text = ctypes.create_unicode_buffer(2000)
            text = remote_mem.Read(text, remote_mem.Address() + \
                ctypes.sizeof(item))
            self._extra_texts.append(text.value)

    #----------------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the TabControl as a Dictionary"
        props = HwndWrapper.HwndWrapper.GetProperties(self)

        props['TabCount'] = self.TabCount()

        props.update(self._extra_props)
        return props

    #----------------------------------------------------------------
    def TabCount(self):
        "Return the number of tabs"
        return self.SendMessage(win32defines.TCM_GETITEMCOUNT)

    #----------------------------------------------------------------
    def GetTabRect(self, tab_index):
        "Return the rectangle to the tab specified by tab_index"

        remote_mem = _RemoteMemoryBlock(self)

        rect = win32structures.RECT()
        remote_mem.Write(rect)

        self.SendMessage(
            win32defines.TCM_GETITEMRECT, tab_index, remote_mem.Address())

        remote_mem.Read(rect)

        del remote_mem

        return rect

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
        texts = [self.Text()]
        texts.extend(self._extra_texts)
        return texts

    #----------------------------------------------------------------
    def Select(self, tab):
        "Select the specified tab on the tab control"

        self.VerifyActionable()

        if isinstance(tab, basestring):
            # find the string in the tab control
            best_text = findbestmatch.find_best_match(
                tab, self.Texts(), self.Texts())
            tab = self.Texts().index(best_text) - 1

        self.SendMessage(win32defines.TCM_SETCURFOCUS, tab)


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

    #----------------------------------------------------------------
    def ButtonCount(self):
        "Return the number of buttons on the ToolBar"
        return self.SendMessage(win32defines.TB_BUTTONCOUNT)

    #----------------------------------------------------------------
    def GetButton(self, button_index):
        "Return information on the Toolbar button"

        remote_mem = _RemoteMemoryBlock(self)

        button = win32structures.TBBUTTON()

        remote_mem.Write(button)

        self.SendMessage(
            win32defines.TB_GETBUTTON, button_index, remote_mem.Address())

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
            remote_mem.Address())
        remote_mem.Read(button_info)

        # read the text
        button_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(button_info.text, remote_mem.Address() + \
            ctypes.sizeof(button_info))

        del remote_mem

        return button_info

    def Texts(self):
        "Return the texts of the Toolbar"
        texts = [self.Text()]
        for i in range(0, self.ButtonCount()):
            texts.append(self.GetButton(i).text)

        return texts


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
#                win32defines.TB_GETBUTTON, i, remote_mem.Address())
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
#                remote_mem.Address())
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

    #----------------------------------------------------------------
    def NumBands(self):
        "Return the number of bands in the control"
        return self.SendMessage(win32defines.RB_GETBANDCOUNT)

    #----------------------------------------------------------------
    def GetBand(self, band_index):
        "Get a band of the ReBar control"
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
        band_info.pszText = remote_mem.Address() + \
            ctypes.sizeof(band_info)
        band_info.cchText = 2000

        # write the structure
        remote_mem.Write(band_info)

        # Fill the structure
        self.SendMessage(
            win32defines.RB_GETBANDINFOW,
            band_index,
            remote_mem.Address())

        # read it back
        remote_mem.Read(band_info)

        # read the text
        band_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(band_info.pszText, remote_mem.Address() + \
            ctypes.sizeof(band_info))

        del remote_mem
        return band_info


    #----------------------------------------------------------------
    def Texts(self):
        "Return the texts of the Rebar"
        texts = [self.Text()]
        for i in range(0, self.NumBands()):
            band = self.GetBand(i)
            texts.append(band.text)

        return texts

    #----------------------------------------------------------------
    def GetProperties(self):
        "Return the properties for the ReBar"
        props = HwndWrapper.HwndWrapper.GetProperties(self)
        props['BandCount'] = self.NumBands()


#====================================================================
class ToolTipsWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ToolTips common control (not fully implemented)"

    # mask this class as it is not ready for prime time yet!
    # friendlyclassname = "ToolTips"
    # windowclasses = ["tooltips_class32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the instance"
        super(ToolTipsWrapper, self).__init__(hwnd)

        self._PlayWithToolTipControls()


    def _PlayWithToolTipControls(self):
        "Just playing for now!"
        # get the number of tooltips associated with the control
        count = self.SendMessage(win32defines.TTM_GETTOOLCOUNT, 0, 0)

        # find the owner window of the tooltip
        #parent = Window(GetWindow (winToTest, GW_OWNER))


        try:
            remote_mem = _RemoteMemoryBlock(self)
        except AccessDenied:
            return

        for i in range(0, count):

            for i2 in range(0, count):
                tipinfo = win32structures.TOOLINFOW()
                tipinfo.cbSize = ctypes.sizeof(tipinfo)
                tipinfo.lpszText  = remote_mem.Address() + \
                    ctypes.sizeof(tipinfo) +1
                tipinfo.uId = i2
                #tipInfo.uFlags = 0xff

                remote_mem.Write(tipinfo)

                ret = self.SendMessage(
                    win32defines.TTM_ENUMTOOLSW, i, remote_mem.Address())

                if not ret:
                    raise ctypes.WinError()
                else:
                    remote_mem.Read(tipinfo)


                    #print i, i2, tipInfo.lpszText
                    #print "-" * 10
                    #PrintCtypesStruct(tipInfo)


                    if tipinfo.lpszText in (
                        win32defines.LPSTR_TEXTCALLBACKW, 0, -1):
                        #print "CALLBACK CALLBACK CALLBACK"
                        pass

                    else:
                        try:
                            text = ctypes.create_unicode_buffer(2000)
                            remote_mem.Read(text, tipinfo.lpszText)

                            #print "TTT"* 10, `text.value`, i, i2
                        except RuntimeError:
                            pass




                #SendMessage(y.hwnd, WM_NOTIFY, )

                #n = ctypes.create_unicode_buffer(2000)
                #ret = ReadProcessMemory(process, y.lpszText, \
                #    ctypes.byref(n), ctypes.sizeof(n), 0)

                #print y.uFlags, Window(y.hwnd).Class, \
                #    Window(y.hwnd).Title, y.uId,  y.hinst, repr(n.value)
                #curTool += 1







#
## doesn't work :-(
###HwndWrapper._HwndWrappers["Afx:00400000:8:00010011:00000010:00000000"] = \
##    ToolbarWrapper
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
##					remote_mem.Address()
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
