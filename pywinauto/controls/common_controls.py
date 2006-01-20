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
                win32defines.MEM_RESERVE | \
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
    "Class that wraps Windows ListView common control "

    friendlyclassname = "ListView"
    windowclasses = ["SysListView32", r"WindowsForms\d*\.SysListView32\..*",]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ListViewWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "ListView"

        # set up a memory block in the remote application
        self.remote_mem = _RemoteMemoryBlock(self)

    #-----------------------------------------------------------
    def ColumnCount(self):
        """Return the number of columns"""
        return len(self.Columns())

    #-----------------------------------------------------------
    def ItemCount(self):
        "The number of items in teh ListView"
        return self.SendMessage(win32defines.LVM_GETITEMCOUNT)


    #-----------------------------------------------------------
    def Columns(self):
        "Get the information on the columns of the ListView"
        cols = []

        # Get each ListView columns text data
        nIndex = 0
        while True:
            col = win32structures.LVCOLUMNW()
            col.mask = win32defines.LVCF_WIDTH | win32defines.LVCF_FMT

            # put the information in the memory that the
            # other process can read/write
            self.remote_mem.Write(col)

            # ask the other process to update the information
            retval = self.SendMessage(
                win32defines.LVM_GETCOLUMNW,
                nIndex,
                self.remote_mem.Address())

            # if that succeeded then there was a column
            if retval:
                col = self.remote_mem.Read(col)

                cols.append(col)
            else:
                break

            nIndex += 1

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
            props['ColumnWidths'] = [999,] # never trunctated

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

        # set up the item structure to get the text
        item = win32structures.LVITEMW()
        item.iSubItem = subitem_index
        item.pszText = self.remote_mem.Address() + \
            ctypes.sizeof(item) + 1
        item.cchTextMax = 2000
        item.mask = win32defines.LVIF_TEXT

        # Write the local LVITEM structure to the remote memory block
        self.remote_mem.Write(item)

        # get the text for the requested item
        retval = self.SendMessage(
            win32defines.LVM_GETITEMTEXTW,
            item_index,
            self.remote_mem.Address())

        # if it succeeded
        if retval:

            # Read the remote text string
            charData = (ctypes.c_wchar*2000)()
            self.remote_mem.Read(charData, item.pszText)

            # and add it to the titles
            item.text = charData.value
        else:
            item.text  = ''

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
    def _get_texts(self):
        "Get the texts for the ListView control"
        texts = [self.Text]
        texts.extend([item.text for item in self.Items()])
        return texts
    Texts = property(_get_texts, doc = _get_texts.__doc__)







    # commented out as we can get these strings from the header
    #					col = remote_mem.Read(col)
    #
    #					charData = (ctypes.c_wchar* 2000)()
    #
    #					ret = remote_mem.Read(charData, col.pszText)
    #
    #					self.Titles.append(charData.value)
    #				else:
    #					break



#====================================================================
def _GetTreeViewElements(curElem, handle, remote_mem, items = None):
    "Get the elements of the tree view"
    if items == None:
        items = []

    item = win32structures.TVITEMW()
    item.mask =  win32defines.TVIF_TEXT | \
        win32defines.TVIF_HANDLE | \
        win32defines.TVIF_CHILDREN #| TVIF_STATE |

    item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
    item.cchTextMax = 2000
    item.hItem = curElem

    # Write the local LVITEM structure to the remote memory block
    remote_mem.Write(item)

    # get this entry
    retval = win32functions.SendMessage(
        handle,
        win32defines.TVM_GETITEMW,
        0,
        remote_mem.Address())

    retval = 1
    if retval:
        remote_mem.Read(item)

        # Read the remote text string
        charData = (ctypes.c_wchar*2000)()
        remote_mem.Read(charData, item.pszText)

        items.append(charData.value)

        if item.cChildren not in (0, 1):


#            print "trying",
#
#            blah = win32structures.NMTVDISPINFOW()
#            blah.hdr.hwndFrom = handle.handle
#            blah.hdr.idFrom = handle.ControlID
#            blah.hdr.code = win32defines.TVN_GETDISPINFOW
#
#            blah.item.mask = win32defines.TVIF_CHILDREN
#            remote_mem.Write(blah)
#            print handle.SendMessage(
#                win32defines.WM_NOTIFY, handle.ControlID, remote_mem.Address())
#
#            blah = remote_mem.Read(blah)
#
#            print blah.item.cChildren



            print "##### not dealing with that TVN_GETDISPINFO stuff yet"
            pass

        if item.cChildren == 1:
            # call this function again for each child handle
            childElem = win32functions.SendMessage(
                handle,
                win32defines.TVM_GETNEXTITEM,
                win32defines.TVGN_CHILD,
                curElem)

            if childElem:
                _GetTreeViewElements(childElem, handle, remote_mem, items)

        # get the next element
        nextElem = win32functions.SendMessage(
            handle,
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_NEXT,
            curElem)
        if nextElem:
            _GetTreeViewElements(nextElem, handle, remote_mem, items)

    return items


#====================================================================
class TreeViewWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows TreeView common control "

    friendlyclassname = "TreeView"
    windowclasses = ["SysTreeView32",r"WindowsForms\d*\.SysTreeView32\..*"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(TreeViewWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "TreeView"

        self._extra_text = []

        remote_mem = _RemoteMemoryBlock(self)

        # get the root item:
        rootElem = self.SendMessage(
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_ROOT)

        self._extra_texts = _GetTreeViewElements(rootElem, self, remote_mem)


#====================================================================
class HeaderWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ListView Header common control "

    friendlyclassname = "Header"
    windowclasses = ["SysHeader32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(HeaderWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "Header"

        self._fill_header_info()


    #====================================================================
    def _fill_header_info(self):
        "Get the information from the header control"
        remote_mem = _RemoteMemoryBlock(self)

        # get the number of items in the header...
        itemCount = self.SendMessage(win32defines.HDM_GETITEMCOUNT)

        for nIndex in range(0, itemCount):

            # get the column rect
            rect = win32structures.RECT()
            remote_mem.Write(rect)
            retval = self.SendMessage(
                win32defines.HDM_GETITEMRECT,
                nIndex,
                remote_mem.Address())

            r = remote_mem.Read(rect)
            self._extra_clientrects.append(rect)


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
                nIndex,
                remote_mem.Address())

            if retval:
                item = remote_mem.Read(item)

                # Read the remote text string
                charData = (ctypes.c_wchar*2000)()
                remote_mem.Read(charData, item.pszText)
                self._extra_texts.append(charData.value)

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

        #self.FriendlyClassName = "StatusBar"

        self._fill_statusbar_info()

    #----------------------------------------------------------------
    def _fill_statusbar_info(self):
        "Get the information from the status bar"
        remote_mem = _RemoteMemoryBlock(self)


        # get the borders for each of the areas there can be a border.
        borders = (ctypes.c_int*3)()
        remote_mem.Write(borders)
        numParts = self.SendMessage(
            win32defines.SB_GETBORDERS,
            0,
            remote_mem.Address()
        )
        borders = remote_mem.Read(borders)
        self._extra_props['HorizBorderWidth'] = borders[0]
        self._extra_props['VertBorderWidth'] = borders[1]
        self._extra_props['InterBorderWidth'] = borders[2]

        # get the number of parts for this status bar
        parts = (ctypes.c_int*99)()
        remote_mem.Write(parts)
        numParts = self.SendMessage(
            win32defines.SB_GETPARTS,
            99,
            remote_mem.Address()
        )

        for part in range(0, numParts):

            # get the rectangle for this item
            rect = win32structures.RECT()
            remote_mem.Write(rect)
            numParts = self.SendMessage(
                win32defines.SB_GETRECT,
                part,
                remote_mem.Address()
            )

            rect = remote_mem.Read(rect)
            self._extra_clientrects.append(rect)


            # get the text for this item
            text = (ctypes.c_wchar*2000)()
            remote_mem.Write(text)
            numParts = self.SendMessage(
                win32defines.SB_GETTEXTW,
                part,
                remote_mem.Address()
            )

            text = remote_mem.Read(text)
            self._extra_texts.append(text.value)

        # remove the first title if we got other titles and the
        # 2nd is the same
        #if len (self._extra_texts) >= 1 and \
        #    self.Text == self._extra_texts[0]:
        #	props["Titles"][0] = ""



#====================================================================
class TabControlWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Tab common control "

    friendlyclassname = "TabControl"
    windowclasses = ["SysTabControl32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(TabControlWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "TabControl"

        self._fill_tabcontrol_info()


    #----------------------------------------------------------------
    def _fill_tabcontrol_info(self):
        "Get the information from the Tab control"
        #tooltipHandle = self.SendMessage(win32defines.TCM_GETTOOLTIPS)

        itemCount = self.SendMessage(win32defines.TCM_GETITEMCOUNT)
        self._extra_props['TabCount'] = itemCount

        remote_mem = _RemoteMemoryBlock(self)

        for i in range(0, itemCount):

            rect = win32structures.RECT()
            remote_mem.Write(rect)

            self.SendMessage(
                win32defines.TCM_GETITEMRECT, i, remote_mem.Address())

            remote_mem.Read(rect)

            self._extra_clientrects.append(rect)


            item = win32structures.TCITEMW()
            item.mask = win32defines.TCIF_STATE | win32defines.TCIF_TEXT
            item.cchTextMax = 1999
            item.pszText = remote_mem.Address() + ctypes.sizeof(item)
            remote_mem.Write(item)

            self.SendMessage(
                win32defines.TCM_GETITEMW, i, remote_mem.Address())

            remote_mem.Read(item)


            self._extra_props.setdefault('TabState', []).append(item.dwState)

            text = (ctypes.c_wchar*2000)()
            text = remote_mem.Read(text, remote_mem.Address() + \
                ctypes.sizeof(item))
            self._extra_texts.append(text.value)




#====================================================================
class ToolbarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows Toolbar common control "

    friendlyclassname = "Toolbar"
    windowclasses = ["ToolbarWindow32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ToolbarWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "Toolbar"

        self._fill_toolbar_info()


    #----------------------------------------------------------------
    def _fill_toolbar_info(self):
        "Get the information from the toolbar"
        buttonCount = self.SendMessage(win32defines.TB_BUTTONCOUNT)
        self._extra_props['ButtonCount'] = buttonCount

        remote_mem = _RemoteMemoryBlock(self)

        for i in range(0, buttonCount):

            button = win32structures.TBBUTTON()

            remote_mem.Write(button)

            self.SendMessage(win32defines.TB_GETBUTTON, i, remote_mem.Address())

            remote_mem.Read(button)

            buttonInfo = win32structures.TBBUTTONINFOW()
            buttonInfo.cbSize = ctypes.sizeof(buttonInfo)
            buttonInfo.dwMask = win32defines.TBIF_TEXT | \
                win32defines.TBIF_COMMAND | \
                win32defines.TBIF_SIZE | \
                win32defines.TBIF_COMMAND | \
                win32defines.TBIF_STYLE | \
                win32defines.TBIF_STATE

            buttonInfo.cchText = 2000

            # set the text address to after the structures
            buttonInfo.pszText = remote_mem.Address() + \
                ctypes.sizeof(buttonInfo)

            # fill the buttonInfo structure
            remote_mem.Write(buttonInfo)
            self.SendMessage(
                win32defines.TB_GETBUTTONINFOW,
                button.idCommand,
                remote_mem.Address())
            remote_mem.Read(buttonInfo)

            # read the text
            text = (ctypes.c_wchar * 1999)()
            remote_mem.Read(text, remote_mem.Address() + \
                ctypes.sizeof(buttonInfo))

            extendedStyle = self.SendMessage(win32defines.TB_GETEXTENDEDSTYLE)

            self._extra_props.setdefault('Buttons', []).append(
                dict(
                    iBitMap = button.iBitmap,
                    idCommand = button.idCommand,
                    fsState = button.fsState,
                    fsStyle = button.fsStyle,
                    cx = buttonInfo.cx,
                    ExStyle = extendedStyle
                )
            )
    #		if button.fsStyle & TBSTYLE_DROPDOWN == TBSTYLE_DROPDOWN and \
    #			(extendedStyle & TBSTYLE_EX_DRAWDDARROWS) != \
    #                TBSTYLE_EX_DRAWDDARROWS:
    #			props['Buttons'][-1]["DROPDOWNMENU"] = 1
    #
    #			self.SendMessage(WM_COMMAND, button.idCommand)
    #
    #			print "Pressing", text.value
    #			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 1)
    #			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 0)

            self._extra_texts.append(text.value)

#====================================================================
class ReBarWrapper(HwndWrapper.HwndWrapper):
    "Class that wraps Windows ReBar common control "

    friendlyclassname = "ReBar"
    windowclasses = ["ReBarWindow32", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        "Initialise the instance"
        super(ReBarWrapper, self).__init__(hwnd)

        #self.FriendlyClassName = "ReBar"

        self._fill_rebar_info()



    #----------------------------------------------------------------
    def _fill_rebar_info(self):
        "Set the rebar inforamtion"
        bandCount = self.SendMessage(win32defines.RB_GETBANDCOUNT)

        #print bandCount
        self._extra_props['BandCount'] = bandCount

        remote_mem = _RemoteMemoryBlock(self)

        for i in range(0, bandCount):

            bandInfo = win32structures.REBARBANDINFOW()

            bandInfo.cbSize = ctypes.sizeof(bandInfo)
            bandInfo.fMask = win32defines.RBBIM_ID | \
                win32defines.RBBIM_TEXT | \
                win32defines.RBBIM_SIZE | \
                win32defines.RBBIM_IDEALSIZE | \
                win32defines.RBBIM_CHILDSIZE | \
                win32defines.RBBIM_COLORS | \
                win32defines.RBBIM_STYLE | \
                win32defines.RBBIM_HEADERSIZE | \
                win32defines.RBBIM_CHILD
            bandInfo.pszText = remote_mem.Address() + \
                ctypes.sizeof(bandInfo)
            bandInfo.cchText = 2000

            remote_mem.Write(bandInfo)

            self.SendMessage(
                win32defines.RB_GETBANDINFOW, i, remote_mem.Address())

            remote_mem.Read(bandInfo)

            text = (ctypes.c_wchar * 1999)()
            remote_mem.Read(text, remote_mem.Address() + \
                ctypes.sizeof(bandInfo))

            self._extra_texts.append(text.value)

            #child = HwndWrapper(bandInfo.hwndChild)





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

        #self.FriendlyClassName = "ToolTips"

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
                            text = (ctypes.c_wchar*2000)()
                            remote_mem.Read(text, tipinfo.lpszText)

                            #print "TTT"* 10, `text.value`, i, i2
                        except RuntimeError:
                            pass




                #SendMessage(y.hwnd, WM_NOTIFY, )


                #n = (ctypes.c_wchar* 2000)()
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
##					charData = (ctypes.c_wchar*4000)()
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
