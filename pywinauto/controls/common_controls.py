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

from pywinauto.win32functions import *
from pywinauto.win32defines import *
from pywinauto.win32structures import *

import HwndWrapper

class AccessDenied(RuntimeError):
	pass


#====================================================================
class RemoteMemoryBlock(object):
	#----------------------------------------------------------------
	def __init__(self, handle, size = 8192):
		self.memAddress = 0
		self.fileMap = 0
		
		# work with either a HwndWrapper or a real hwnd
		#try:
		#	handle = handle.hwnd
		#except:
		#	pass
		

		processID = c_long()
		GetWindowThreadProcessId(handle, byref(processID))

		self.process = OpenProcess(
			PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, 
			0, 
			processID)

		if not self.process:
			# TODO - work in a way that cannot be denied (or fail gracefully
			#raise WinError()
			#raise "could not communicate with process (%d)"% (processID.value)
			raise AccessDenied(str(WinError()) + "process: %d", processID.value)

		if GetVersion() < 0x80000000:
			self.memAddress = VirtualAllocEx(
				self.process,	# remote process 
				0,				# let Valloc decide where
				size,			# how much to allocate
				MEM_RESERVE | MEM_COMMIT,	# allocation type
				PAGE_READWRITE	# protection
				)
				
			if not self.memAddress:
				raise WinError()
				
			
		else:
			raise "Win9x allocation not supported"


	#----------------------------------------------------------------
	def __del__(self):
		# Free the memory in the remote process's address space
		address = ctypes.c_int(self.memAddress)
		VirtualFreeEx(self.process, byref(address), 0, MEM_RELEASE)

	#----------------------------------------------------------------
	def Address(self):
		return self.memAddress

	#----------------------------------------------------------------
	def Write(self, data):
		# write the data from this process into the memory allocated
		# from the other process
		ret = WriteProcessMemory(
			self.process, 
			self.memAddress, 
			pointer(data), 
			sizeof(data), 
			0);
			
		if not ret: 
			raise WinError()

	#----------------------------------------------------------------
	def Read(self, data, address = None):
		if not address:
			address = self.memAddress
		
		ret = ReadProcessMemory(self.process, address, byref(data), sizeof(data), 0)
		
		# disabled as it often returns an error - but seems to work fine anyway!!
		if not ret: 
			raise WinError()
		
		return data
		


#====================================================================
class ListViewWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(ListViewWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "ListView"

		# set up a memory block in the remote application
		self.remoteMem = RemoteMemoryBlock(self)

		self._get_column_info()

		self._extra_texts = self.get_extra_texts()
		
			
	#-----------------------------------------------------------
	def get_extra_texts(self):
		
		colcount = len(self._get_column_info())
		
		if not colcount:
			colcount = 1
			
		itemCount = self.SendMessage(LVM_GETITEMCOUNT)
		
		texts = []
				
		# now get the item values...
		# for each of the rows
		for nRowIndex in range(0, itemCount):

			# and each of the columns for that row
			for nColIndex in range(0, colcount):

				# set up the item structure to get the text		
				item = LVITEMW()
				item.iSubItem = nColIndex
				item.pszText = self.remoteMem.Address() + sizeof(item) + 1
				item.cchTextMax = 2000
				item.mask = LVIF_TEXT

				# Write the local LVITEM structure to the remote memory block
				ret = self.remoteMem.Write(item)

				# get the text for the requested item
				retval = self.SendMessage(
					LVM_GETITEMTEXTW,
					nRowIndex,
					self.remoteMem.Address())

				# if it succeeded
				if retval:

					# Read the remote text string
					charData = (c_wchar*2000)()
					ret = self.remoteMem.Read(charData, item.pszText)

					# and add it to the titles
					texts.append(charData.value)
				else:
					texts.append('')

		return texts

	
	#----------------------------------------------------------------
	def _get_column_info(self):
		cols = []
	
		# Get each ListView columns text data
		nIndex = 0
		while True:
			col = LVCOLUMNW()
			col.mask = LVCF_WIDTH | LVCF_FMT

			# put the information in the memory that the 
			# other process can read/write
			self.remoteMem.Write(col)

			# ask the other process to update the information
			retval = self.SendMessage(
				LVM_GETCOLUMNW,
				nIndex,
				self.remoteMem.Address())

			if not retval:
				break
			else:
				col = self.remoteMem.Read(col)
				
				cols.append(col)

			nIndex += 1
		
		
		if cols:
			self._extra_props['ColumnWidths'] = [col.cx for col in cols] 
			self._extra_props['ColumnCount'] = len(cols)
		
		else:
			self._extra_props['ColumnWidths'] = [999, ]
			self._extra_props['ColumnCount'] = 1
		
		return cols
			
	

	# commented out as we can get these strings from the header
	#					col = remoteMem.Read(col)
	#	
	#					charData = (c_wchar* 2000)()
	#					
	#					ret = remoteMem.Read(charData, col.pszText)
	#					
	#					self.Titles.append(charData.value)
	#				else:
	#					break

	
			
#====================================================================
def GetTreeViewElements(curElem, handle, remoteMem, items = None):
	
	if items == None:
		items = []
		
	item = TVITEMW()
	item.mask =  TVIF_TEXT | TVIF_HANDLE | TVIF_CHILDREN #| TVIF_STATE |
	item.pszText = remoteMem.Address() + sizeof(item) + 1
	item.cchTextMax = 2000
	item.hItem = curElem
	
	# Write the local LVITEM structure to the remote memory block
	ret = remoteMem.Write(item)

	# get this entry
	retval = SendMessage(
		handle,
		TVM_GETITEMW,
		0,
		remoteMem.Address())
	

	retval = 1
	if retval:
		ret = remoteMem.Read(item)

		# Read the remote text string
		charData = (c_wchar*2000)()
		ret = remoteMem.Read(charData, item.pszText)

		items.append(charData.value)
		
		if item.cChildren not in (0,1):
			print "##### not dealing with that TVN_GETDISPINFO stuff yet"
			pass
		
		if item.cChildren == 1:
			# call this function again for each child handle
			childElem = SendMessage(
				handle,
				TVM_GETNEXTITEM,
				TVGN_CHILD,
				curElem)

			if childElem:
				GetTreeViewElements(childElem, handle, remoteMem, items)
		
		# get the next element
		nextElem = SendMessage(
			handle,
			TVM_GETNEXTITEM,
			TVGN_NEXT,
			curElem)
		if nextElem:
			GetTreeViewElements(nextElem, handle, remoteMem, items)
			
	return items

	

#====================================================================
class TreeViewWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(TreeViewWrapper, self).__init__(hwnd)
		
		self.FriendlyClassName = "TreeView"
		
		self._extra_text = []

		remoteMem = RemoteMemoryBlock(self)

		# get the root item:
		rootElem = self.SendMessage(
			TVM_GETNEXTITEM,
			TVGN_ROOT)

		self._extra_texts = GetTreeViewElements(rootElem, self, remoteMem)





#====================================================================
class HeaderWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(HeaderWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "Header"

		self._fill_header_info()
		

	#====================================================================
	def _fill_header_info(self):

		remoteMem = RemoteMemoryBlock(self)

		# get the number of items in the header...
		itemCount = self.SendMessage(HDM_GETITEMCOUNT)

		for nIndex in range(0, itemCount):

			# get the column rect
			r = RECT()
			remoteMem.Write(r)
			retval = self.SendMessage(
				HDM_GETITEMRECT,
				nIndex,
				remoteMem.Address())

			r = remoteMem.Read(r)
			self._extra_clientrects.append(r)


			item = HDITEMW()
			item.mask = HDI_FORMAT | HDI_WIDTH | HDI_TEXT #| HDI_ORDER
			item.cchTextMax = 2000

			# set up the pointer to the text
			# it should be at the 
			item.pszText = remoteMem.Address() + sizeof(HDITEMW) + 1 

			# put the information in the memory that the 
			# other process can read/write
			remoteMem.Write(item)

			# ask the other process to update the information
			retval = self.SendMessage(
				HDM_GETITEMW,
				nIndex,
				remoteMem.Address())

			if retval:
				item = remoteMem.Read(item)

				# Read the remote text string
				charData = (c_wchar*2000)()
				remoteMem.Read(charData, item.pszText)
				self._extra_texts.append(charData.value)



#====================================================================
class StatusBarWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(StatusBarWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "StatusBar"
		
		self._fill_statusbar_info()
	
	#----------------------------------------------------------------
	def _fill_statusbar_info(self):

		remoteMem = RemoteMemoryBlock(self)


		# get the borders for each of the areas there can be a border.
		borders = (c_int*3)()
		remoteMem.Write(borders)
		numParts = self.SendMessage(
			SB_GETBORDERS,
			0,
			remoteMem.Address()
		)
		borders = remoteMem.Read(borders)
		self._extra_props['HorizBorderWidth'] = borders[0]
		self._extra_props['VertBorderWidth'] = borders[1]
		self._extra_props['InterBorderWidth'] = borders[2]			

		# get the number of parts for this status bar
		parts = (c_int*99)()
		remoteMem.Write(parts)
		numParts = self.SendMessage(
			SB_GETPARTS,
			99,
			remoteMem.Address()
		)

		for p in range(0, numParts):

			# get the rectangle for this item
			r = RECT()
			remoteMem.Write(r)
			numParts = self.SendMessage(
				SB_GETRECT,
				p,
				remoteMem.Address()
			)

			r = remoteMem.Read(r)				
			self._extra_clientrects.append(r)


			# get the text for this item
			text = (c_wchar*2000)()
			remoteMem.Write(text)				
			numParts = self.SendMessage(
				SB_GETTEXTW,
				p,
				remoteMem.Address()
			)

			text = remoteMem.Read(text)
			self._extra_texts.append(text.value)

		# remove the first title if we got other titles and the 
		# 2nd is the same
		#if len (self._extra_texts) >= 1 and self.Text == self._extra_texts[0]:
		#	props["Titles"][0] = ""




#====================================================================
class TabControlWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(TabControlWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "TabControl"
		
		self._fill_tabcontrol_info()


	#----------------------------------------------------------------
	def _fill_tabcontrol_info(self):
		tooltipHandle = self.SendMessage(TCM_GETTOOLTIPS)

		itemCount = self.SendMessage(TCM_GETITEMCOUNT)
		self._extra_props['TabCount'] = itemCount

		remoteMem = RemoteMemoryBlock(self)

		for i in range(0, itemCount):

			rect = RECT()
			remoteMem.Write(rect)

			self.SendMessage(TCM_GETITEMRECT, i, remoteMem.Address())

			remoteMem.Read(rect)				

			self._extra_clientrects.append(rect)


			item = TCITEMW()
			item.mask = TCIF_STATE | TCIF_TEXT
			item.cchTextMax = 1999
			item.pszText = remoteMem.Address() + sizeof(TCITEMW)
			remoteMem.Write(item)

			self.SendMessage(TCM_GETITEMW, i, remoteMem.Address())

			remoteMem.Read(item)


			self._extra_props.setdefault('TabState', []).append(item.dwState)

			text = (c_wchar*2000)()
			text = remoteMem.Read(text, remoteMem.Address() + sizeof(TCITEMW))
			self._extra_texts.append(text.value)
	
		
		

#====================================================================
class ToolbarWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(ToolbarWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "Toolbar"
		
		self._fill_toolbar_info()

		
	#----------------------------------------------------------------
	def _fill_toolbar_info(self):

		buttonCount = self.SendMessage(TB_BUTTONCOUNT)
		self._extra_props['ButtonCount'] = buttonCount

		remoteMem = RemoteMemoryBlock(self)

		for i in range(0, buttonCount):

			button = TBBUTTON()

			remoteMem.Write(button)

			self.SendMessage(TB_GETBUTTON, i, remoteMem.Address())

			remoteMem.Read(button)

			buttonInfo = TBBUTTONINFOW()
			buttonInfo.cbSize = sizeof(TBBUTTONINFOW)
			buttonInfo.dwMask = TBIF_TEXT | TBIF_COMMAND | TBIF_SIZE | TBIF_COMMAND | TBIF_STYLE | TBIF_STATE 
			buttonInfo.pszText = remoteMem.Address() + sizeof(TBBUTTONINFOW)
			buttonInfo.cchText = 2000

			remoteMem.Write(buttonInfo)

			self.SendMessage(TB_GETBUTTONINFOW, button.idCommand, remoteMem.Address())

			remoteMem.Read(buttonInfo)

			text = (c_wchar * 1999)()
			remoteMem.Read(text, remoteMem.Address() + sizeof(TBBUTTONINFOW))

	#		PrintCtypesStruct(buttonInfo, ('pszText', 'cchText', 'cbSize', 'dwMask', 'lParam', 'iImage'))

			extendedStyle = self.SendMessage(TB_GETEXTENDEDSTYLE) 
			
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
	#			extendedStyle & TBSTYLE_EX_DRAWDDARROWS != TBSTYLE_EX_DRAWDDARROWS:
	#			props['Buttons'][-1]["DROPDOWNMENU"] = 1
	#			
	#			self.SendMessage(WM_COMMAND, button.idCommand)
	#			
	#			print "Pressing", text.value
	#			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 1) 
	#			handle.SendMessage(TB_PRESSBUTTON, button.idCommand, 0) 



			self._extra_texts.append(text.value)
			
#====================================================================
class RebarWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(RebarWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "ReBar"
		
		self._fill_rebar_info()

		
	
	#----------------------------------------------------------------
	def _fill_rebar_info(self):
		bandCount = self.SendMessage(RB_GETBANDCOUNT)

		#print bandCount
		self._extra_props['BandCount'] = bandCount

		remoteMem = RemoteMemoryBlock(self)

		for i in range(0, bandCount):

			bandInfo = REBARBANDINFOW()

			bandInfo.cbSize = sizeof(bandInfo)
			bandInfo.fMask = RBBIM_ID | RBBIM_TEXT | RBBIM_SIZE | RBBIM_IDEALSIZE | RBBIM_CHILDSIZE | RBBIM_COLORS | RBBIM_STYLE | RBBIM_HEADERSIZE | RBBIM_CHILD
			bandInfo.pszText = remoteMem.Address() + sizeof(bandInfo)
			bandInfo.cchText = 2000

			remoteMem.Write(bandInfo)

			self.SendMessage(RB_GETBANDINFOW, i, remoteMem.Address())

			remoteMem.Read(bandInfo)

			text = (c_wchar * 1999)()
			remoteMem.Read(text, remoteMem.Address() + sizeof(bandInfo))
			
			self._extra_texts.append(text.value)

			#child = HwndWrapper(bandInfo.hwndChild)





#====================================================================
class ToolTipsWrapper(HwndWrapper.HwndWrapper):
	#----------------------------------------------------------------
	def __init__(self, hwnd):
		super(ToolTipsWrapper, self).__init__(hwnd)

		self.FriendlyClassName = "ToolTips"

		self.PlayWithToolTipControls()


	def PlayWithToolTipControls(self):

		# get the number of tooltips associated with the control
		count = self.SendMessage(TTM_GETTOOLCOUNT, 0, 0)
		
		# find the owner window of the tooltip
		#parent = Window(GetWindow (winToTest, GW_OWNER))


		try:
			remoteMem = RemoteMemoryBlock(self)
		except AccessDenied:
			return

		for i in range(0, count):

			for i2 in range(0, count):
				tipInfo = TOOLINFOW()
				tipInfo.cbSize = sizeof(TOOLINFOW)
				tipInfo.lpszText  = remoteMem.Address() + sizeof(tipInfo) +1
				tipInfo.uId = i2
				#tipInfo.uFlags = 0xff

				remoteMem.Write(tipInfo)

				ret = self.SendMessage(TTM_ENUMTOOLSW, i, remoteMem.Address())

				if not ret:
					print WinError()
					sys.exit()
				else:
					remoteMem.Read(tipInfo)


					#print i, i2, tipInfo.lpszText
					#print "-" * 10
					#PrintCtypesStruct(tipInfo)


					if tipInfo.lpszText in (LPSTR_TEXTCALLBACKW, 0, -1):
						#print "CALLBACK CALLBACK CALLBACK"
						pass

					else:
						try:
							text = (c_wchar*2000)()
							remoteMem.Read(text, tipInfo.lpszText)

							#print "TTT"* 10, `text.value`, i, i2
						except:
							pass




				#SendMessage(y.hwnd, WM_NOTIFY, )


				#n = (c_wchar* 2000)()
				#ret = ReadProcessMemory(process, y.lpszText, byref(n), sizeof(n), 0)

				#print y.uFlags, Window(y.hwnd).Class, Window(y.hwnd).Title, y.uId,  y.hinst, repr(n.value)
				#curTool += 1

		
	
	
	
	
		
	
	
	
#====================================================================
def PrintCtypesStruct(struct, exceptList = []):
	for f in struct._fields_:
		name = f[0]
		if name in exceptList:
			continue
		print "%20s "% name, getattr(struct, name)





HwndWrapper.HwndWrappers["SysListView32"] = ListViewWrapper
HwndWrapper.HwndWrappers[r"WindowsForms\d*\.SysListView32\..*"] = ListViewWrapper

HwndWrapper.HwndWrappers["SysTreeView32"] = TreeViewWrapper
HwndWrapper.HwndWrappers[r"WindowsForms\d*\.SysTreeView32\..*"] = TreeViewWrapper

HwndWrapper.HwndWrappers["SysHeader32"] = HeaderWrapper

HwndWrapper.HwndWrappers["msctls_statusbar32"] = StatusBarWrapper
HwndWrapper.HwndWrappers["HSStatusBar"] = StatusBarWrapper
HwndWrapper.HwndWrappers[r"WindowsForms\d*\.msctls_statusbar32\..*"] = StatusBarWrapper

HwndWrapper.HwndWrappers["SysTabControl32"] = TabControlWrapper

HwndWrapper.HwndWrappers["ToolbarWindow32"] = ToolbarWrapper
##HwndWrapper.HwndWrappers["Afx:00400000:8:00010011:00000010:00000000"] = ToolbarWrapper

HwndWrapper.HwndWrappers["ReBarWindow32"] = RebarWrapper

#HwndWrapper.HwndWrappers["tooltips_class32"] = ToolTipsWrapper
#
##HwndWrapper.HwndWrappers["ComboBoxEx32"] = ComboBoxEx
#


			
		
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
##			droppedRect = RECT()
##
##			SendMessage(
##				self, 
##				CB_GETDROPPEDCONTROLRECT, 
##				0, 
##				byref(droppedRect))
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
##			remoteMem = RemoteMemoryBlock(self)
##
##
##			# get the text for each item in the combobox
##			while True:
##				item = COMBOBOXEXITEMW()
##				
##				item.mask = CBEIF_TEXT
##				item.cchTextMax = 4000
##				item.pszText = remoteMem.Address() + sizeof(item) + 1
##				
##				remoteMem.Write(item)
##				
##				retval = SendMessage (
##					self, 
##					CBEM_GETITEMW,
##					0, 
##					remoteMem.Address()
##					)
##					
##				if retval:
##					item = remoteMem.Read(item)
##
##					# Read the remote text string
##					charData = (c_wchar*4000)()
##					remoteMem.Read(charData, item.pszText)
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



