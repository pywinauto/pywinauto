	
#	#----------------------------------------------------------------
#	def GetContextMenu(self):
#		rect = self.Rectangle
#
#		# set the position of the context menu to be 2 pixels in from 
#		# the control edge
#		pos = c_long ((rect.top+ 2 << 16) | (rect.left + 2))
#
#		# get the top window before trying to bring up a context menu
#		oldTopWin = FindWindow(0, 0)
#		
#		# send the message but time-out after 10 mili seconds
#		res = DWORD()
#		SendMessageTimeout (
#			self.handle, 
#			WM_CONTEXTMENU, 
#			self.handle, 
#			pos, 
#			0, 		
#			100, 	# time out in miliseconds
#			byref(res)) # result
#		
#		# get the top window
#		popMenuWin = FindWindow(0, 0)
#		
#		# if no context menu has opened try right clicking the control
##		if oldTopWin == popMenuWin:
##			SendMessageTimeout (
##				self.handle, 
##				WM_RBUTTONDOWN, 
##				0,
##				pos,
##				0, 		
##				100, 	# time out in miliseconds
##				byref(res)) # result
##
##			SendMessageTimeout (
##				self.handle, 
##				WM_RBUTTONUP, 
##				2,
##				pos, 
##				0, 		
##				100, 	# time out in miliseconds
##				byref(res)) # result
##
##			# wait another .1 of a second to allow it to display
##			import time
##			time.sleep(.1)
##	
##			# get the top window
##			popMenuWin = FindWindow(0, 0)
#
#
#		# if we still haven't opened a popup menu
#		if oldTopWin == popMenuWin:
#			return
#
#
#		# get the MenuBar info from the PopupWindow which will
#		# give you the Menu Handle for the menu itself
#		mbi = MENUBARINFO()
#		mbi.cbSize = sizeof(MENUBARINFO)
#		ret = GetMenuBarInfo(popMenuWin, OBJID_CLIENT, 0, byref(mbi))
#		
#		if ret:
#			GetMenuItems(mbi.hMenu)
#			self.properties["ContextMenu"] = GetMenuItems(mbi.hMenu)
#			
#
#		# make sure the popup goes away!
#		self.handle.SendMessage (WM_CANCELMODE, 0, 0)
#		SendMessage (popMenuWin, WM_CANCELMODE, 0, 0)
#
#		# if it's still open - then close it.
#		if IsWindowVisible(popMenuWin):
#			SendMessage (popMenuWin, WM_CLOSE, 0, 0)
#			#SendMessage (popMenuWin, WM_DESTROY, 0, 0)
#			#SendMessage (popMenuWin, WM_NCDESTROY , 0, 0)
		






		
		
				
		


				

			


##====================================================================
#def RemoveNonCurrentTabControls(dialog, childWindows):
#	
#	# find out if there is a tab control and get it if there is one
#	tab = None
#	for child in childWindows:
#		if child.Class == "SysTabControl32":
#			tab = child
#			break
#	
#
#	# make a copy of childWindows
#	firstTabChildren = list(childWindows)
#	if tab:		
#		
#		firstTabHandle = 0
#		
#		# get the parent of the tab control
#		tabParent = GetParent(tab.handle)
#		
#		# find the control with that hwnd
#		tabParent = [c for c in childWindows if \
#			c.handle == tabParent][0]
#
#		# get the index of the parent
#		parentIdx = childWindows.index(tabParent) + 1
#		
#		passedFirstTab = False
#		for child in childWindows[parentIdx:]:
#			
#			# if the current control is a dialog
#			if child.Class == "#32770":
#			
#				# if this is the first tab
#				if not passedFirstTab:
#					# then just skip it
#					passedFirstTab = True
#					firstTabHandle = child.handle
#				else:
#					# Ok so this is NOT the first tab
#					# remove the dialog control itself
#					try:
#						firstTabChildren.remove(child)
#						print "Removing(a): ", child.IsVisible, IsWindowChildOf(firstTabHandle, child.handle)
#					except ValueError:
#						pass
#					
#					# then remove all the children of that dialog
#					for x in GetChildWindows(child.handle):
#						try:
#							firstTabChildren.remove(x)
#							print "Removing(b): ", child.IsVisible, IsWindowChildOf(firstTabHandle, x)
#						except ValueError:
#							pass
#	
#						
#	return firstTabChildren







##====================================================================
#class Window(object):
#	#----------------------------------------------------------------
#	def __init__(self, hwndOrProps):
#
#		self.ref = None
#		
#		# if the argument passed in is a Handle
#		if isinstance(hwndOrProps, HwndWrapper):
#		
#			# wrap the handle
#			self.handle = hwndOrProps
#			
#			# Get the properties from this handle
#			self.properties = self.handle.GetProperties()
#						
#		else:
#			self.properties = XMLHelpers.ControlFromXML(hwndOrProps)
#			
#				
#	#----------------------------------------------------------------
#	def __getattr__(self, name):
#		if name in self.properties:
#			return self.properties[name]
#		else:
#			raise AttributeError("'%s' has no attribute '%s'"% \
#				(self.__class__.__name__, name))		
#	
#	#----------------------------------------------------------------
#	def GetTitle(self):
#		return self.Titles[0]
#	Title = property(GetTitle) 
#	
#	#----------------------------------------------------------------
#	def GetRectangle(self):
#		return self.Rectangles[0]
#	Rectangle = property(GetRectangle) 
#
#	#----------------------------------------------------------------
#	def GetFont(self):
#		return self.Fonts[0]
#
#	#----------------------------------------------------------------
#	def SetFont(self, font):
#		self.Fonts[0] = font
#
#	Font = property(GetFont, SetFont) 
#
#	#----------------------------------------------------------------
#	def Parent(self):
#		# do a preliminary construction to a Window
#		parent = self.handle.Parent()
#		
#		# reconstruct it to the correct type
#		return  WindowClassRegistry().GetClass(parent.Class())(parent.handle)#.hwnd)
#		
#	#----------------------------------------------------------------
#	def Style(self, flag = None):
#		style = self.properties['Style']
#		if flag:
#			return style & flag == flag
#		else:
#			return style
#		
#	#----------------------------------------------------------------
#	def ExStyle(self, flag = None):
#		exstyle = self.properties['ExStyle']
#		if flag:
#			return exstyle & flag == flag
#		else:
#			return exstyle
#
#	#----------------------------------------------------------------
#	def __cmp__(self, other):
#		return cmp(self.handle, other.handle)
#		
#	#----------------------------------------------------------------
#	def __hash__(self):
#		return hash(self.handle)
#
#	#----------------------------------------------------------------
##	def __str__(self):
##		return "%8d %-15s\t'%s'" % (self.handle, 
##			"'%s'"% self.FriendlyClassName, 
##			self.Title)	


#
#
##====================================================================
#class DialogWindow(Window):
#	#----------------------------------------------------------------
#	def __init__(self, hwndOrXML):
#		
#		self.children = []	
#		
#		# if the argument passed in is a window hanle
#		if isinstance(hwndOrXML, (int, long)):
#			# read the properties for the dialog itself
#			# Get the dialog Rectangle first - to get the control offset
#			
#			if not IsWindow(hwndOrXML):
#				raise "The window handle passed is not valid"
#			
#			Window.__init__(self, hwndOrXML)
#			
#					
#		else:
#			dialogElemReached = False
#			for ctrlElem in hwndOrXML.findall("CONTROL"):
#			
#				# if this is the first time through the dialog
#				if not dialogElemReached:
#					# initialise the Dialog itself
#					Window.__init__(self, ctrlElem)
#					dialogElemReached = True
#				
#				# otherwise contruct each control normally
#				else:
#					# get the class for the control with that window class
#					Klass = WindowClassRegistry().GetClass(ctrlElem.attrib["Class"])
#					
#					# construct the object and append it
#					self.children.append(Klass(ctrlElem))
#					
#			self.children.insert(0, self)
#				
#
#	#----------------------------------------------------------------
#	def AllControls(self):
#		return self.children
#		
#
#
#	#----------------------------------------------------------------
#	def AddReference(self, ref):
#		
#		
#		#print "x"*20, ref.AllControls()
#		if len(self.AllControls()) != len(ref.AllControls()):
#			print len(self.AllControls()), len(ref.AllControls())
#			raise "Numbers of controls on ref. dialog does not match Loc. dialog"	
#			
#		
#		allIDsMatched = True
#		allClassesMatched = True
#		for idx, ctrl in enumerate(self.AllControls()):
#			refCtrl = ref.AllControls()[idx]
#			ctrl.ref = refCtrl
#			
#			if ctrl.ControlID != refCtrl.ControlID:
#				allIDsMatched = False
#
#			if ctrl.Class != refCtrl.Class:
#				allClassesMatched = False
#			
#		toRet = 1
#		
#		allIDsSameFlag = 2
#		allClassesSameFlag = 4
#		
#		if allIDsMatched:
#			toRet += allIDsSameFlag
#		
#		if allClassesMatched:
#			toRet += allClassesSameFlag
#		
#		return toRet
				


			
			
##====================================================================
#def DefaultWindowHwndReader(hwnd, dialogRect):
#	
#	ctrl = HwndWrapper(hwnd)
#	
#	return ctrl.GetProperties()
#	
#	if dialogRect:
#		# offset it's rect depending on it's parents
#		rect.left -= dialogRect.left
#		rect.top -= dialogRect.top
#		rect.right -= dialogRect.left
#		rect.bottom -= dialogRect.top


##====================================================================
#def GetClass(hwnd):
#	# get the className
#	className = (c_wchar * 257)()
#	GetClassName (hwnd, byref(className), 256)
#	return className.value
#
#
##====================================================================
#def GetTitle(hwnd):
#	# get the title
#	bufferSize = SendMessage (hwnd, WM_GETTEXTLENGTH, 0, 0)	
#	title = (c_wchar * bufferSize)()
#	
#	if bufferSize:
#		bufferSize += 1
#		SendMessage (hwnd, WM_GETTEXT, bufferSize, title)
#	
#
#	return title.value

#			
#
##====================================================================
#def GetChildWindows(dialog):
#
#	# this will be filled in the callback function
#	childWindows = []
#	
#	# callback function for EnumChildWindows
#	def enumChildProc(hWnd, LPARAM):
#		win = Window(hWnd)
#		
#		# construct an instance of the appropriate type
#		win = WindowClassRegistry().GetClass(win.Class)(hWnd)
#				
#		# append it to our list
#		childWindows.append(win)
#		
#		# return true to keep going
#		return True
#
#
#	# define the child proc type
#	EnumChildProc = WINFUNCTYPE(c_int, HWND, LPARAM)	
#	proc = EnumChildProc(enumChildProc)
#	
#	# loop over all the children (callback called for each)
#	EnumChildWindows(dialog.hwnd, proc, 0)
#	
#	return childWindows


#
##====================================================================
#def IsWindowChildOf(parent, child):
##	try:
##		parentHwnd = parent.handle
##	except:
##		parentHwnd = parent
#	
#	childHwnd = child
#	
#	while True:
#		curParentTest = GetParent(childHwnd)
#
#		
#		# the current parent matches 
#		if  curParentTest == parentHwnd:
#			return True
#		
#		# we reached the very top of the heirarchy so no more parents
#		if curParentTest == 0:
#			return False
#		
#		# the next child is the current parent
#		childHwnd = curParentTest
#		




# =====================================================
# DEAD XML STUFF CODE
# =====================================================
#	
#		props['ClientRect'] = ParseRect(ctrl.find("CLIENTRECT"))
#			
#		props['Rectangle'] = ParseRect(ctrl.find("RECTANGLE"))
#
#		props['Font'] = ParseLogFont(ctrl.find("FONT"))
#		
#		props['Titles'] = ParseTitles(ctrl.find("TITLES"))
#					
#		for key, item in ctrl.attrib.items():
#			props[key] = item
			




##-----------------------------------------------------------------------------
#def StructToXML(struct, structElem):
#	"Convert a ctypes Structure to an ElementTree"
#
#	for propName in struct._fields_:
#		propName = propName[0]
#		itemVal = getattr(struct, propName)
#
#		# convert number to string
#		if isinstance(itemVal, (int, long)):
#			propName += "_LONG"
#			itemVal = unicode(itemVal)
#
#		structElem.set(propName, EscapeSpecials(itemVal))
#
#
	
#
#
##====================================================================
#def XMLToMenuItems(element):
#	items = []
#	
#	for item in element:
#		itemProp = {}
#
#		itemProp["ID"] = int(item.attrib["ID_LONG"])
#		itemProp["State"] = int(item.attrib["State_LONG"])
#		itemProp["Type"] = int(item.attrib["Type_LONG"])
#		itemProp["Text"] = item.attrib["Text"]
#
#		#print itemProp
#		subMenu = item.find("MENUITEMS")
#		if subMenu:
#			itemProp["MenuItems"] = XMLToMenuItems(subMenu)
#	
#		items.append(itemProp)
#	return items	
#	
#
##====================================================================
#def ListToXML(listItems, itemName, element):
#	
#	for i, string in enumerate(listItems):
#
#		element.set("%s%05d"%(itemName, i), EscapeSpecials(string))
#
#
#
##====================================================================
#def XMLToList(element):
#	items = []
#	for subItem in element:
#		items.append(PropFromXML(subItem))
#		
##====================================================================
#def PropFromXML(element):
#
#	for propName in PropParsers:
#		if element.tag == propName.upper():
#			
#			ToXMLFunc, FromXMLFunc = PropParsers[element.tag.upper()]
#	
#			return FromXMLFunc(element)
#
#	raise "Unknown Element Type : %s"% element.tag
#
##====================================================================
#def PropToXML(parentElement, name, value, ):
#	print "=" *20, name, value
#
#	ToXMLFunc, FromXMLFunc = PropParsers[element.tag.upper()]
#	
#	return FromXMLFunc(element)
#	
#
#	
#
#PropParsers = {
#	"Font" : (StructToXML, XMLToFont),
#	"Rectangle" : (StructToXML, XMLToRect),
#	"ClientRects" : (ListToXML, XMLToRect),
#	"Titles" : (TitlesToXML, XMLToTitles),
#	"Fonts" : (ListToXML, XMLToList),
#	#"Rectangles" : (ListToXML, XMLToList),
#	#"" : XMLToMenuItems,
#	#"" : XMLToMenuItems,
#
#
#}
#

# USED TO BE NEEDED IN THE XML OUTPUT FUNCTION
#	# format the output xml a little
#	xml = open(fileName, "rb").read()
#
#	import re
#	tags = re.compile("""
#		(
#			<[^/>]+>    # An opening tag
#		)|
#		(
#			</[^>]+>    # A closing tag
#		)|
#		(
#			<[^>]+/>    # an empty element
#		)
#		
#		""", re.VERBOSE)
#
#	f = open(fileName, "wb")
#	indent = 0
#	indentText = "   "
#	for x in  tags.finditer(xml):
#
#		# closing tag
#		if x.group(2): 
#			indent -= 1
#			f.write(indentText*indent + x.group(2) + "\r\n")
#
#		# if the element may have attributes
#		else:
#			if x.group(1): 
#				text = x.group(1)
#			if x.group(3): 
#				text = x.group(3)
#
#			f.write(indentText*indent + text + "\r\n")
#
##
##			Trying to indent the attributes each on a single line
##			but it is more complicated then it first looks :-(
##
#			items = text.split()
#			
#			
#			f.write(indentText*indent + items[0] + "\r\n")
#			indent += 1
#			for i in items[1:]:
#				f.write(indentText*indent + i + "\r\n")
#
#			indent -= 1
#			
#			# opening tag
#			if x.group(1):
#				indent += 1
#		
#	f.close()


##====================================================================
## specializes XMLToStruct for Fonts
#def XMLToFont(element):
#	font = LOGFONTW()
#	#print element.attrib
#	XMLToStruct(element, font)
#	
#	return font
#
##====================================================================
## specializes XMLToStruct for Rects
#def XMLToRect(element):
#	rect = RECT()
#		
#	XMLToStruct(element, rect)
#	return rect
#
##====================================================================
#def TitlesToXML(titles, titleElem):
#	for i, string in enumerate(titles):
#
#		titleElem.set("s%05d"%i, EscapeSpecials(string))
#
#
##====================================================================




	
	
	
	
	
	
	




	
	
#	sys.exit()
#	
#	# SendText playing around!! - not required
#	SetForegroundWindow(handle)
#	SendText("here is some test text")
#
#	
#	# some SendText testing
#	text = sys.argv[2]
#	import os.path
#	if os.path.exists(text):
#		text = open(text, "rb").read().decode('utf-16')
#	
#	print `text`
#	
#	#SendText("--%s--"%text)
#	for c in dialog.AllChildren():
#		print "(%6d) %s - '%s'"% (c.handle,c.Class, c.Title)
#		if c.Class == "Edit":
#			#SetActiveWindow (c.handle)
#			SetForegroundWindow(c.handle)
#			#SetFocus(c.handle)
#			#EnableWindow(c.handle, True)
#			SendText("--%s--"%text)
#				
#		
#		
#		
		
		

	# get all the windows involved for this control	
	#windows.extend(windows[0].Children())
	
	
	
#	
#	
#	styles = 	{
#		"WS_DISABLED"	:	134217728, # Variable c_long
#		"WS_BORDER"	:	8388608, # Variable c_long
#		"WS_TABSTOP"	:	65536, # Variable c_long		<< adds min, max, buttons
#		"WS_MINIMIZE"	:	536870912, # Variable c_long
#		"WS_DLGFRAME"	:	4194304, # Variable c_long
#		"WS_VISIBLE"	:	268435456, # Variable c_long
#		"WS_OVERLAPPED"	:	0, # Variable c_long
#		"WS_CHILD"	:	1073741824, # Variable c_long
#		"WS_CAPTION"	:	12582912, # Variable c_long
#		"WS_POPUPWINDOW"	:	2156396544L, # Variable c_ulong
#		"WS_HSCROLL"	:	1048576, # Variable c_long
#		"WS_THICKFRAME"	:	262144, # Variable c_long			<< takes about 2 pixes off length
#		#"WS_SIZEBOX"	:	WS_THICKFRAME, # alias
#		"WS_OVERLAPPEDWINDOW"	:	13565952, # Variable c_long	<< turns off sysmenu!
#		#"WS_TILEDWINDOW"	:	WS_OVERLAPPEDWINDOW, # alias
#		"WS_GROUP"	:	131072, # Variable c_long			<< adds both minimize and maximize boxes
#		"WS_VSCROLL"	:	2097152, # Variable c_long
#		"WS_MAXIMIZEBOX"	:	65536, # Variable c_long	<< adds both minimize and maximize boxes
#		"WS_MAXIMIZE"	:	16777216, # Variable c_long
#		"WS_SYSMENU"	:	524288, # Variable c_long		<< adds/removes close box
#		"WS_POPUP"	:	2147483648L, # Variable c_ulong
#		"WS_MINIMIZEBOX"	:	131072, # Variable c_long	<< adds both minimize and maximize boxes
#		"WS_CLIPCHILDREN"	:	33554432, # Variable c_long
#		#"WS_ICONIC"	:	WS_MINIMIZE, # alias
#		"WS_CLIPSIBLINGS"	:	67108864, # Variable c_long
#		#"WS_TILED"	:	WS_OVERLAPPED, # alias
#		"WS_CHILDWINDOW"	:	1073741824, # Variable c_long
#	
#	}
#
#	exstyles = {
#		"WS_EX_TOOLWINDOW"	:	128, # Variable c_long		<< small font
#		"WS_EX_MDICHILD"	:	64, # Variable c_long
#		"WS_EX_WINDOWEDGE"	:	256, # Variable c_long
#		"WS_EX_RIGHT"	:	4096, # Variable c_long
#		"WS_EX_NOPARENTNOTIFY"	:	4, # Variable c_long
#		"WS_EX_ACCEPTFILES"	:	16, # Variable c_long
#		"WS_EX_LEFTSCROLLBAR"	:	16384, # Variable c_long
#		"WS_EX_OVERLAPPEDWINDOW"	:	768, # Variable c_long
#		"WS_EX_DLGMODALFRAME"	:	1, # Variable c_long	<< adds Icon
#		"WS_EX_TRANSPARENT"	:	32, # Variable c_long
#		"WS_EX_STATICEDGE"	:	131072, # Variable c_long
#		"WS_EX_TOPMOST"	:	8, # Variable c_long
#		"WS_EX_LTRREADING"	:	0, # Variable c_long
#		"WS_EX_RIGHTSCROLLBAR"	:	0, # Variable c_long
#		"WS_EX_APPWINDOW"	:	262144, # Variable c_long
#		"WS_EX_CONTROLPARENT"	:	65536, # Variable c_long
#		"WS_EX_LEFT"	:	0, # Variable c_long
#		"WS_EX_PALETTEWINDOW"	:	392, # Variable c_long	<< small font
#		"WS_EX_CONTEXTHELP"	:	1024, # Variable c_long		<< adds a CH button
#		"WS_EX_CLIENTEDGE"	:	512, # Variable c_long
#		"WS_EX_RTLREADING"	:	8192, # Variable c_long
#	}
#	
#	
#
#	for s in styles:
#		if dialog.Style(styles[s]):
#			print "%30s\t0x%-8x"% (s, styles[s])
#
#	print "-"*20
#	for s in exstyles:
#		if dialog.ExStyle(exstyles[s]):
#			print "%30s\t0x%-8x"% (s, exstyles[s])
			
#	print dialog.Font().lfHeight, dialog.Font().lfWidth, dialog.Font().lfFaceName
	
#	print "STyle 0x%08x EXStyle 0x%08x" % (dialog.Style(), dialog.ExStyle())
	
	
#	print "please type the style to set/unset"
#	typed = ""
#	while typed.lower() != "x":
#		typed = raw_input()
#		
#		if typed in exstyles:
#			old = dlg.ExStyle()
#			new = dlg.ExStyle() ^ exstyles[typed]
#			SetWindowLong(dlg.handle, GWL_EXSTYLE, c_long(new))
#			print "%0x %0x %0x"% (old, new, exstyles[typed])
#			SetWindowLong(dlg.handle, GWL_STYLE, dlg.Style() ^268435456)
#			SetWindowLong(dlg.handle, GWL_STYLE, dlg.Style() ^268435456)
#			SendMessage(dlg.handle, WM_PAINT, 0, 0)
#			SetForegroundWindow(dlg.handle)
#			
#
#		if typed in styles:
#			old = dlg.Style()
#			new = dlg.Style() ^ styles[typed]
#			SetWindowLong(dlg.handle, GWL_STYLE, c_long(new))
#			print "%0x %0x %0x"% (old, new, styles[typed])
#			SetWindowLong(dlg.handle, GWL_STYLE, dlg.Style() ^268435456)
#			SetWindowLong(dlg.handle, GWL_STYLE, dlg.Style() ^268435456)
#			SendMessage(dlg.handle, WM_PAINT, 0, 0)
#			SetForegroundWindow(dlg.handle)
	
	

	#dialog = ParentWindow(dlg.handle)


	
		
		





#
#
##====================================================================
#from SendInput import TypeKeys, PressKey, LiftKey, TypeKey, VK_MENU, \
#	VK_SHIFT, VK_BACK, VK_DOWN, VK_LEFT
#
#
#def SendText(text):
#	
#	# write the text passed in
#	TypeKeys(text)
#	
#	# press shift
#	PressKey(VK_SHIFT)
#	# lowercase 'a'
#	#import pm
#	#pm.set_trace()
#	toType = (VK_LEFT,) * 13
#	TypeKeys(toType)
#	
#	# unpress shift
#	LiftKey(VK_SHIFT)
#	
#
#	PressKey(VK_MENU)
#	TypeKey('F')
#	LiftKey(VK_MENU)
#
#
#	TypeKeys((VK_DOWN,)*4)
#	
#	
	
	
	
	
	
	
	


	
	

#====================================================================
#class Menuitem(object):
#	def __init__(self, item):
#		for attr in item.keys():
#			self.__dict__["_%s_"%attr] = item[attr]
#		
#		self.__dict__.setdefault("_MenuItems_", [])
#	
#	def __getattr__(self, key):
#		return getattr(MenuWrapper(self._MenuItems_), key)
#		
#			
#
##====================================================================
#class MenuWrapper(object):
#	def __init__(self, items):
#		# clean up the existing menuItem attributes
#		# and set them
#		self.__items = items
#		
#		self.__texts = [item['Text'] for item in self.__items]
#
#	
#	def __getattr__(self, key):
#		
#		item = find_best_match(key, self._texts_, self.__items)
#				
#		return item
#		
#
##====================================================================
#def MenuSelect(ctrl, menupath, menu_items):
#
#	id = FindMenu(menupath, menu_items)
#	
#	#print ctrl['MenuItems']
#	APIFuncs.PostMessage(ctrl.handle, win32defines.WM_COMMAND, id, 0)
#


#
#
#
##====================================================================
#class Dialog2(controls.HwndWrapper.HwndWrapper):
#	#----------------------------------------------------------------
#	def __init__(self, title = None, class_ = None, timeout = 1, handle = None):
#		
#		if not handle:
#
#			handle = FindDialog(title, testClass = class_)
#			waited = 0
#			while not handle and waited <= timeout:
#				time.sleep(.1)
#				handle = FindDialog(title, testClass = class_)
#				waited += .1
#
#			if not handle:
#				raise WindowNotFound("Window not found")
#
#		super(Dialog2, self).__init__(handle)
#	
#		self.controls = [self, ]
#		self.controls.extend(self.Children)
#		
#		controlactions.add_actions(self)
#		
#		#self._build_control_id_map()
#		
#		self.ctrl_texts = [ctrl.Text or ctrl.FriendlyClassName for ctrl in self.controls]
#		
#		# we need to handle controls where the default text is not that interesting e.g.
#		# edit boxes
#		
#	
#	#----------------------------------------------------------------
#	def __getattr__(self, to_find):
#	
#		waited = 0
#		while waited <= 1:
#			try:
#				#if "Dialog" in self.ctrl_texts:
#				#	print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
#				#	print self.ctrl_texts, self.Class, self.Children
#				ctrl = find_best_match(to_find, self.ctrl_texts, self.controls)
#				return controlactions.add_actions(ctrl)
#			except WindowNotFound:
#				waited += .1
#	
#		print self
#		print "failed to find %s in %s" % (to_find, self.ctrl_texts)
#
#		raise
#		
#		
#	#----------------------------------------------------------------
#	def MenuSelect(self, path):
#		
#		
#		item_id = FindMenu(self.MenuItems, path)
#		#menu_items = MenuWrapper(self.MenuItems)
#
#		#item_id = FindMenu(menu_items, path)		
#		
#		#print ctrl['MenuItems']
#		self.PostMessage(win32defines.WM_COMMAND, item_id)
#		
#	

#
#
##====================================================================
#def TestNotepad():
#	
#	try:
#		notepad = Dialog2(title = "^.*Notepad.*", class_ = "Notepad")
#	except WindowNotFound:
#		os.system("start notepad")
#		time.sleep(.1)
#		notepad = Dialog2(title = "^.*Notepad.*", class_ = "Notepad")
#
#
#	#print notepad.handle
#	
##	notepad.SendKeys("testing")
##	notepad.edit.SendKeys("Here is so\\nme tëÿext%H")
##	notepad.SendKeys("{DOWN}{ENTER}")
##	#notepad.SendKeys("a")
##	
##	# need to get active window!!
##	notepad.SendKeys("{ESC}")
##	notepad.SendKeys("%E")	
#	if "1" in sys.argv:
#		# Select that menu item
#		notepad.MenuSelect("File->Page Setup")
#
#		# find the dialog
#		page_setup = Dialog2(title = "Page Setup")
#
#		edit = page_setup.Edit1
#		edit.TypeKeys("{HOME}+{END}{BKSP}23")
#
#
#		page_setup.Combo1.Select(5)
#		time.sleep(1)
#
#		page_setup.Combo1.Select("Tabloid")
#		time.sleep(1)
#
#		# click the printer button
#		page_setup.Printer.Click()
#
#		dlg = Dialog2("^Page Setup").Properties.Click()
#
#		Dialog2(".*Document Properties").Advanced.Click()
#
#		Dialog2(".*Advanced Options").Cancel.Click()
#
#		Dialog2(".*Document Properties").cancel.Click()
#
#		Dialog2("^Page Setup").cancel.Click()
#
#		# dialog doesn't go away because 23 that we typed is 'wrong'
#		Dialog2(title = "^Page Setup").ok.Click()
#
#		# this is teh message box
#		Dialog2(title = "^Page Setup").ok.Click()
#
#		# dialog doesn't go away because 23 that we typed is 'wrong'
#		Dialog2(title = "^Page Setup").cancel.Click()
#
#	if "2" in sys.argv:
#		# Select that menu item
#		notepad.MenuSelect("Format->Font")
#
#		font_dlg = Dialog2(title = "^Font$")
#
#		font_dlg.combobox2.Select(3)
#		time.sleep(2)
#
#		Dialog2(title = "^Font$").OK.Click()
#	
#	if "3" in sys.argv:
#		notepad.Edit1.Select(1,4)
#		time.sleep(2)
#
#		print notepad.edit1.SelectionIndices
#		
#	if "4" in sys.argv:
#	
#		raise "NotWorkingYet"
#		edit = notepad.Edit1
#		print edit.Rectangle
#		
#		edit.PressMouse(coords = (0,0))
#		edit.MoveMouse(coords = (400, 400))
#		edit.ReleaseMouse(coords = (400,400))
#		
#	if "5" in sys.argv:
#		
#		edit = notepad.Edit1
#
#		edit.DoubleClick(coords = (1290,1290))
#
#		
#
##====================================================================
#def test():
#
#	# some some normal dailogs
#	if 1:
#		testStrings = ["Combo", "Combo2", "ComboBox", "blah blah", "test" ,"hex" ,"matchwhole" ,"regularExp" ,"wrapsearch" ,"wrap" ,"inalldocs" ,"extend_sel" ,"Find next" ,"markall" ,"up" ,"down" ,"direct" ,"conds"]
#	else:
#		testStrings = ["blah blah", "first", "from", "from0", "from001", "from2", "from0000003", "from3", "insensitive", "delduplicate", "charCodeOrder"]
#
#
#	item_texts = [ctrl.Text or ctrl.FriendlyClassName for ctrl in ctrls]
#
#	missedMatches = []
#	for test in testStrings:
#
#		try:
#			ctrl = find_best_match(test, item_texts, ctrls)
#			print "%15s %15s %-20s %s"% (test, ctrl.FriendlyClassName, `ctrl.Text[:20]`, str(ctrl.Rectangle))
#		except IndexError, e:
#			missedMatches.append(test)
#
#	if missedMatches:
#		print "\nNo Matches for: " +  ", ".join(missedMatches)
#
#
#
#if __name__ == "__main__":
#	TestNotepad()

#print "\n\nMenuTesting"
#missedMatches = []
#try:
#	print MenuWrapper(ctrls[0].MenuItems).File.PageSetup._Text_
#except IndexError, e:
#	missedMatches.append(test)
#
#if missedMatches:
#	print "\nNo Matches for: " +  ", ".join(missedMatches)
	


#
#
#for ctrl in ctrls:
#	print CtrlAccessName(ctrl)
#	
#	if ctrl.Class in ('ComboBox'):
#	
#	
#		candidates = []
#		# find controls that are to it's left
#		for ctrl2 in ctrls:
#			# if this ctrl has a top or bottom between
#			# other ctrl top and bottom
#			
#			if \
#				(((ctrl2.Rectangle.top >= ctrl.Rectangle.top and \
#			   	ctrl2.Rectangle.top < ctrl.Rectangle.bottom) or \
#			   	(ctrl2.Rectangle.bottom > ctrl.Rectangle.top and \
#			    ctrl2.Rectangle.bottom <= ctrl.Rectangle.bottom)) and\
#			    ctrl2.Rectangle.left < ctrl.Rectangle.left) \
#			    or \
#			   	(((ctrl2.Rectangle.right >= ctrl.Rectangle.left and \
#			   	ctrl2.Rectangle.right < ctrl.Rectangle.bottom) or \
#			   	(ctrl2.Rectangle.bottom > ctrl.Rectangle.top and \
#			    ctrl2.Rectangle.bottom <= ctrl.Rectangle.bottom)) and\
#			    ctrl2.Rectangle.left < ctrl.Rectangle.left) \
#			    :
#			    
#			    
#			    
#			    
#			    
#			    candidates.append(ctrl2)
#			    
#
#
#		#for candidate in cadidates:			    
#		#	print "%18s - 20%s" % (candidate.Class, "'%s'"%candidate.Title), CtrlAccessName(candidate)
#			
#			
#			
#			#if ctrl2.Rectangle.top >= ctrl.Rectangle.top  <= ctrl2.Rectangle.bottom or \
#			#   ctrl2.Rectangle.bottom >= ctrl.Rectangle.top
#			
#		
#			#if ctrl2.Rectangle.top 
#
#
#
##import pprint
##pprint.pprint(ctrls)
#

	
	
# how should we read in the XML file 
# NOT USING MS Components (requirement on machine)
# maybe using built in XML
# maybe using elementtree
# others?

from elementtree.ElementTree import Element, SubElement, ElementTree
import ctypes

from APIStructures import RECT, LOGFONTW


charEncodings = {
	"\\n" : "\n",
	"\\x12" : "\x12",
	#"\\\\" : "\\",
}

#todo - make the dialog reading function not actually know about the 
# types of each element (so that we can read the control properties
# without having to know each and every element type)
# probably need to store info on what type things are.

#-----------------------------------------------------------------------------
def AddElement(element, name, value):

	# if it is a ctypes structure
	if isinstance(value, ctypes.Structure):
		
		# create an element for the structure
		structElem = SubElement(element, name)

		# iterate over the fields in the structure
		for propName in value._fields_:
			propName = propName[0]
			itemVal = getattr(value, propName)

			if isinstance(itemVal, (int, long)):
				propName += "_LONG"
				itemVal = unicode(itemVal)

			structElem.set(propName, EscapeSpecials(itemVal))#.encode('utf8'))

	elif isinstance(value, (list, tuple)):
		# add the element to hold the values
		#listElem = SubElement(element, name)

		# remove the s at the end (if there)
		name = name.rstrip('s')

		for i, attrVal in enumerate(value):
				AddElement(element, "%s_%05d"%(name, i), attrVal)

	elif isinstance(value, dict):
		dictElem = SubElement(element, name)

		for n, val in value.items():
			AddElement(dictElem, n, val)
			

	else:
		if isinstance(value, (int, long)):
			name += "_LONG"
		
		element.set(name, EscapeSpecials(value))#.encode('utf8', 'backslashreplace'))





#-----------------------------------------------------------------------------
def ConvertDialogToElement(dialog):
	

	# build a tree structure
	root = Element("DIALOG")
	for ctrl in dialog.AllControls():
		ctrlElem = SubElement(root, "CONTROL")
		for name, value in ctrl.properties.items():
			AddElement(ctrlElem, name, value)
	
	return root
	
#-----------------------------------------------------------------------------
def WriteElementToFile(element, fileName):
	
	# wrap it in an ElementTree instance, and save as XML
	tree = ElementTree(element)
	tree.write(fileName, encoding="utf-8")

#	# format the output xml a little
#	xml = open(fileName, "rb").read()
#
#	import re
#	tags = re.compile("""
#		(
#			<[^/>]+>    # An opening tag
#		)|
#		(
#			</[^>]+>    # A closing tag
#		)|
#		(
#			<[^>]+/>    # an empty element
#		)
#		
#		""", re.VERBOSE)
#
#	f = open(fileName, "wb")
#	indent = 0
#	indentText = "   "
#	for x in  tags.finditer(xml):
#
#		# closing tag
#		if x.group(2): 
#			indent -= 1
#			f.write(indentText*indent + x.group(2) + "\r\n")
#
#		# if the element may have attributes
#		else:
#			if x.group(1): 
#				text = x.group(1)
#			if x.group(3): 
#				text = x.group(3)
#
#			f.write(indentText*indent + text + "\r\n")
#
##
##			Trying to indent the attributes each on a single line
##			but it is more complicated then it first looks :-(
##
#			items = text.split()
#			
#			
#			f.write(indentText*indent + items[0] + "\r\n")
#			indent += 1
#			for i in items[1:]:
#				f.write(indentText*indent + i + "\r\n")
#
#			indent -= 1
#			
#			# opening tag
#			if x.group(1):
#				indent += 1
#		
#	f.close()




#-----------------------------------------------------------------------------
def EscapeSpecials(inStr):
	"Ensure that some characters are escaped before writing to XML"
	
	# make sure input is a unicode string or convert
	inStr = unicode(inStr)
	for (replacement, char) in charEncodings.items():
		inStr = inStr.replace(char, replacement)

	return inStr
		
	
#-----------------------------------------------------------------------------
def UnEscapeSpecials(inStr):
	"Replace escaped characters with real character"
	for (replacement, char) in charEncodings.items():
		inStr = inStr.replace(replacement, char)

	return unicode(inStr)


#-----------------------------------------------------------------------------
def StructToXML(struct, structElem):
	for propName in struct._fields_:
		propName = propName[0]
		itemVal = getattr(struct, propName)

		# convert number to string
		if isinstance(itemVal, (int, long)):
			propName += "_LONG"
			itemVal = unicode(itemVal)

		structElem.set(propName, EscapeSpecials(itemVal))#.encode('utf8'))



#-----------------------------------------------------------------------------
def XMLToStruct(element, struct):

	# get the attribute and set them upper case
	structAttribs = dict([(at.upper(), at) for at in dir(struct)])

	for propName in element.attrib:
		
		val = element.attrib[propName]
		
		if propName.endswith("_LONG"):
			val = long(val)
			propName = propName[:-5]
		else:
			val = unicode(val)
			
		# now we can have all upper case attribute name
		# but structure name will not be upper case
		
		if propName.upper() in structAttribs:
			propName = structAttribs[propName.upper()]
		
			setattr(struct, propName, val)


#====================================================================
# specializes XMLToStruct for Fonts
def XMLToFont(element):
	font = LOGFONTW()
	#print element.attrib
	XMLToStruct(element, font)
	
	return font

#====================================================================
# specializes XMLToStruct for Rects
def XMLToRect(element):
	rect = RECT()
		
	XMLToStruct(element, rect)
	return rect

#====================================================================
def TitlesToXML(titles, titleElem):
	for i, string in enumerate(titles):

		titleElem.set("s%05d"%i, EscapeSpecials(string))


#====================================================================
def XMLToTitles(element):

	# get all the attribute names
	titleNames = element.attrib.keys()

	# sort them to make sure we get them in the right order	
	titleNames.sort()
	
	# build up the array	
	titles = []
	for name in titleNames:
		val = element.attrib[name]
		val = val.replace('\\n', '\n')
		val = val.replace('\\x12', '\x12')
		val = val.replace('\\\\', '\\')
		
		titles.append(unicode(val))
		
	
	return titles
	


#====================================================================
def XMLToMenuItems(element):
	items = []
	
	for item in element:
		itemProp = {}

		itemProp["ID"] = int(item.attrib["ID_LONG"])
		itemProp["State"] = int(item.attrib["State_LONG"])
		itemProp["Type"] = int(item.attrib["Type_LONG"])
		itemProp["Text"] = item.attrib["Text"]

		#print itemProp
		subMenu = item.find("MENUITEMS")
		if subMenu:
			itemProp["MenuItems"] = XMLToMenuItems(subMenu)
	
		items.append(itemProp)
	return items	
	

#====================================================================
def ListToXML(listItems, itemName, element):
	
	for i, string in enumerate(listItems):

		element.set("%s%05d"%(itemName, i), EscapeSpecials(string))



#====================================================================
def XMLToList(element):
	items = []
	for subItem in element:
		items.append(PropFromXML(subItem))
		
#====================================================================
def PropFromXML(element):

	for propName in PropParsers:
		if element.tag == propName.upper():
			
			ToXMLFunc, FromXMLFunc = PropParsers[element.tag.upper()]
	
			return FromXMLFunc(element)

	raise "Unknown Element Type : %s"% element.tag

#====================================================================
def PropToXML(parentElement, name, value, ):
	#print "=" *20, name, value

	ToXMLFunc, FromXMLFunc = PropParsers[element.tag.upper()]
	
	return FromXMLFunc(element)
	

		
import re



def GetAttributes(element):

	# get all the attributes
	for attribName, val in element.attrib.items():

		# if it is 'Long' element convert it to an long
		if attribName.endswith("_LONG"):
			val = long(val)
			attribName = attribName[:-5]
		else:
			# otherwise it is a string - make sure we get it as a unicode string
			val = unicode(val)

		# if the attributes are a list of itmes
		if re.match(r".*_\d{5}", attribName)
			# set the property
			properties[attribName] = val
		else:
			properties[attribName] = val
		



#====================================================================
def ControlFromXML(controlElement):
	properties = {}



	


	# get all the attributes
	for attribName in controlElement.attrib:

		# get attribute value
		val = controlElement.attrib[attribName]
		#print "-" *20, attribName, val


		# if it is 'Long' element convert it to an long
		if attribName.endswith("_LONG"):
			val = long(val)
			attribName = attribName[:-5]
		else:
			# otherwise it is a string - make sure we get it as a unicode string
			val = unicode(val)

		# if the attributes are a list of itmes
		if re.match(r".*_\d{5}", attribName)
			# set the property
			properties[attribName] = val
		else:
			properties[attribName] = val
		


	for elem in controlElement:
		propValue = PropFromXML(elem)

		# if there was another element with this name
		if propName in properties:
			
			# Make sure it is a list
			properties[propName] = list(properties[propName])

			# add our element
			properties[propName].append(propValue)
			
			#print propName, properties[propName]
		else:
			# so we haven't already seen another prop with this name
			# just add it
			properties[propName] = propValue

	return properties

	

PropParsers = {
	"Font" : (StructToXML, XMLToFont),
	"Rectangle" : (StructToXML, XMLToRect),
	"ClientRects" : (ListToXML, XMLToRect),
	"Titles" : (TitlesToXML, XMLToTitles),
	"Fonts" : (ListToXML, XMLToList),
	#"Rectangles" : (ListToXML, XMLToList),
	#"" : XMLToMenuItems,
	#"" : XMLToMenuItems,


}



if __name__ == "__main__":

	import sys	
	from elementtree import ElementTree
	parsed = ElementTree.parse(sys.argv[1])	
	
	props = {}
	
	print dir(parsed)
	for ctrl in parsed.findall("CONTROL"):
		print ControlFromXML(ctrl)
		sys.exit()
	
		props['ClientRect'] = ParseRect(ctrl.find("CLIENTRECT"))
			
		props['Rectangle'] = ParseRect(ctrl.find("RECTANGLE"))

		props['Font'] = ParseLogFont(ctrl.find("FONT"))
		
		props['Titles'] = ParseTitles(ctrl.find("TITLES"))
					
		for key, item in ctrl.attrib.items():
			props[key] = item
			
