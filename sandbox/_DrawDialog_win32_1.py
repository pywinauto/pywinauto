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

## import all of the wxPython GUI package
from wxPython.wx import *


from ctypes import *


import PyDlgCheckerWrapper


import sys
if len(sys.argv) < 2 :
	print "Please specify the XML file to read"
	sys.exit()

PyDlgCheckerWrapper.InitDialogFromFile(sys.argv[1])
dlg = PyDlgCheckerWrapper.TestInfo['Dialog']



BOOL = c_int
BYTE = c_ubyte
CHAR = c_char
DWORD = c_ulong
LONG = c_long
LPVOID = c_void_p
PVOID = c_void_p
UINT = c_uint
WCHAR = c_wchar
WORD = c_ushort

COLORREF = DWORD
HBITMAP = LONG
HINSTANCE = LONG
HMENU = LONG
HTREEITEM = LONG
HWND = LONG
LPARAM = LONG
LPCWSTR = c_wchar_p
LPWSTR = c_wchar_p #POINTER(WCHAR)



SW_ERASE = 4 # Variable c_int
SW_FORCEMINIMIZE = 11 # Variable c_int
SW_HIDE = 0 # Variable c_int
SW_INVALIDATE = 2 # Variable c_int
SW_MAX = 11 # Variable c_int
SW_MAXIMIZE = 3 # Variable c_int
SW_MINIMIZE = 6 # Variable c_int
SW_NORMAL = 1 # Variable c_int
SW_OTHERUNZOOM = 4 # Variable c_int
SW_OTHERZOOM = 2 # Variable c_int
SW_PARENTCLOSING = 1 # Variable c_int
SW_PARENTOPENING = 3 # Variable c_int
SW_RESTORE = 9 # Variable c_int
SW_SCROLLCHILDREN = 1 # Variable c_int
SW_SHOW = 5 # Variable c_int
SW_SHOWDEFAULT = 10 # Variable c_int
SW_SHOWMAXIMIZED = 3 # Variable c_int
SW_SHOWMINIMIZED = 2 # Variable c_int
SW_SHOWMINNOACTIVE = 7 # Variable c_int
SW_SHOWNA = 8 # Variable c_int
SW_SHOWNOACTIVATE = 4 # Variable c_int
SW_SHOWNORMAL = 1 # Variable c_int




# C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 2186
class CREATESTRUCTW(Structure):
	_fields_ = [
		# C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 2186
		('lpCreateParams', LPVOID),
		('hInstance', HINSTANCE),
		('hMenu', HMENU),
		('hwndParent', HWND),
		('cy', c_int),
		('cx', c_int),
		('y', c_int),
		('x', c_int),
		('style', LONG),
		('lpszName', LPCWSTR),
		('lpszClass', LPCWSTR),
		('dwExStyle', DWORD),
	]
assert sizeof(CREATESTRUCTW) == 48, sizeof(CREATESTRUCTW)
assert alignment(CREATESTRUCTW) == 4, alignment(CREATESTRUCTW)





# C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 3278
class DLGTEMPLATE(Structure):
	_pack_ = 2
	_fields_ = [
		# C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 3278
		('style', DWORD),
		('dwExtendedStyle', DWORD),
		('cdit', WORD),
		('x', c_short),
		('y', c_short),
		('cx', c_short),
		('cy', c_short),
	]
assert sizeof(DLGTEMPLATE) == 18, sizeof(DLGTEMPLATE)
assert alignment(DLGTEMPLATE) == 2, alignment(DLGTEMPLATE)


def Main():
	import ctypes
	CW = ctypes.windll.user32.CreateWindowExW
	
#	cs = CREATESTRUCTW()
#	cs.hInstance = 0   # ????
#	cs.hMenu = 0
#	cs.hwndParent = 0
#	cs.cx = 100
#	cs.cy = 200
#	cs.x = 10
#	cs.y = 20
#	cs.style = 0 #0x80000
#	cs.lpszName = u"Hi There"
#	cs.lpszClass = "#32770"
#	cs.dwExStyle = 0


	parent = 0
	for i, ctrl in enumerate(dlg.AllControls()):
	
		if i == 0:
			print "FIRST"
			#klass = u"#32770"
			style = ctrl.Style()
		else:
			klass = ctrl.Class.upper()
			style = ctrl.Style()
			#print klass
			#style = 0
	
		klass = ctrl.Class.upper()
	
		if parent and ctrl.Class == "#32770":
			continue
	

		handle =  CW(
			ctrl.ExStyle(),	# dwExStyle
			klass,	# class
			ctrl.Title,# titles
			style  , #ctrl.Style(),	# style
			ctrl.Rectangle.left, # x
			ctrl.Rectangle.top,	# y
			ctrl.Rectangle.right - ctrl.Rectangle.left,	# cx
			ctrl.Rectangle.bottom - ctrl.Rectangle.top,	# cy
			parent,	# parent
			0,	# menu
			ctypes.windll.kernel32.GetModuleHandleW(u"user32.dll"),	# hInstance ???
			0,	# lparam		
			)
	

		import time
		time.sleep(.3)
		if not parent:
			parent = handle
		print handle,
		x = (c_wchar * 200)()
		ctypes.windll.user32.GetClassNameW(handle, byref(x) ,100)
		print x.value
		style = ctypes.windll.user32.GetWindowLongW(handle, -16)
		ctypes.windll.user32.EnableWindow(handle, 1)
		
		if style != ctrl.Style():
			print "FAILED"
		
		
		
		ctypes.windll.user32.ShowWindow(handle, SW_SHOW)
	

	
#	edit =  CW(
#		0,	# dwExStyle
#		u"BUTTON",	# class
#		u"YO There",# titles
#		0,	# style
#		30,	# x
#		40,	# y
#		40,	# cx
#		20,	# cy
#		handle,	# parent
#		0,	# menu
#		0,	# hInstance ???
#		0,	# lparam		
#		)
#	
#	print edit
#	
#	ctypes.windll.user32.ShowWindow(edit, SW_SHOW)
	
	



if __name__=='__main__':
	Main()
	import time
	time.sleep(3)

	sys.exit()



##class DLGTEMPLATEEX(Structure):
###	_pack_ = 1
##	_fields_ = [
##		('dlgVer', WORD),
##		('signature', WORD),
##		('helpID', DWORD),
##		('exStyle', DWORD),
##		('style', DWORD),
##		('cDlgItems', WORD), #LPWSTR),
##		('x', c_short),
##		('y', c_short),
##		('cx', c_short),
##		('cy', c_short),
##		('menu', c_void_p),
##		('windowClass', c_void_p), #LPWSTR),
##		('title', c_wchar_p),
##		('pointsize', WORD),
##		('weight', WORD),
##		('italic', BYTE),
##		('charset', BYTE),
##		('typeface', c_wchar_p),
##	]
##
##	def __init__(self, dlg):
##		self.dlgVer = 1
##		self.signature = 0xFFFF
##		
##		#self.helpID = dlg.helpID
##		#self.exStyle = dlg.helpID
##		#self.style = dlg.helpID
##		#self.cdlgItems = dlg.helpID
##		self.x = 10
##		self.y = 10
##		self.cx = 50
##		self.cy = 50
##		#self.menu = xx
##		self.windowClass = "#32770"
##		#self.title = xx
##		#self.pointsize = xx
##		#self.weight = xx
##		#self.italic = xx
##		#self.charset = xx
##		#self.typeface = xx
##		
##
##
##
##class DLGITEMTEMPLATEEX(Structure):
###	_pack_ = 1
##	_fields_ = [
##		('helpID', DWORD), 
##		('exStyle', DWORD), 
##		('style', DWORD), 
##		('x', c_short), 
##		('y', c_short), 
##		('cx', c_short), 
##		('cy', c_short), 
##		('id', WORD), 
##		('windowClass', c_void_p), 
##		('title', c_void_p), 
##		('extraCount', WORD), 
##	]
##
##	def __init__(self, ctrl):
##		self.helpID = 1
##		self.exStyle = 2
##		self.style = 3
##		self.x = 10
##		self.y = 20
##		self.cx = 6
##		self.cy = 8
##		self.id = ctrl.ControlID
##		self.windowClass = 2134
##		self.title =  u"1234567678"
##		self.extraCount = 0
##
##
##
##
##
##
##
#### Create a new frame class, derived from the wxPython Frame.
##class MyFrame(wxFrame):
##
##	def __init__(self, parent, id, title):
##		# First, call the base class' __init__ method to create the frame
##
##
##
##		wxFrame.__init__(self, 
##			parent, 
##			id, 
##			dlg.Title,
##			wxPoint(100, 100), 
##			wxSize(dlg.Rectangle.right, dlg.Rectangle.bottom))
##
##		# Add a panel and some controls to display the size and position
##		panel = wxPanel(self, -1)
##
##
##		classes = {
##			"Static": wxStaticText,
##			"Button": wxButton,
##			"CheckBox": wxCheckBox,
##			"RadioButton": wxRadioButton,
##			"Dialog": None,
##			"#32770": None,
##			"SysTabControl32": None,
##
###			"GroupBox": None,
##			"GroupBox": wxRadioBox,
##
###			"Static": wxStaticText,
###			"Static": wxStaticText,
###			"Static": wxStaticText,
##			
##			}
##		for ctrl in dlg.AllControls()[1:]:
##			wx_class_type = classes.get(ctrl.FriendlyClassName, wxStaticText)
##			
##			print ctrl.FriendlyClassName, wx_class_type
##			
##			if wx_class_type:
##				width = ctrl.Rectangle.right - ctrl.Rectangle.left
##				height = ctrl.Rectangle.bottom - ctrl.Rectangle.top
##
##				if wx_class_type != wxRadioBox:
##					wx_class_type (
##						panel, 
##						-1, 
##						ctrl.Title,
##						wxPoint(ctrl.Rectangle.left -3, ctrl.Rectangle.top - 23),
##						wxSize(width, height)).Raise()
##				else:
##				
##					wx_class_type (
##						panel, 
##						-1, 
##						ctrl.Title,
##						wxPoint(ctrl.Rectangle.left -3, ctrl.Rectangle.top - 23),
##						wxSize(width, height),
##						['']).Lower()
##			
##
##
###		wxStaticText(panel, -1, "Size:",
###					 wxDLG_PNT(panel, wxPoint(4, 4)),  wxSize(30, 20))
###
###		wxStaticText(panel, -1, "Pos:",
###					 wxDLG_PNT(panel, wxPoint(4, 14)), wxDefaultSize)
###
###		self.sizeCtrl = wxTextCtrl(panel, -1, "",
###								   wxDLG_PNT(panel, wxPoint(24, 4)),
###								   wxDLG_SZE(panel, wxSize(36, -1)),
###								   wxTE_READONLY)
###		self.posCtrl = wxTextCtrl(panel, -1, "",
###								  wxDLG_PNT(panel, wxPoint(24, 14)),
###								  wxDLG_SZE(panel, wxSize(36, -1)),
###								  wxTE_READONLY)
##
##
##	# This method is called automatically when the CLOSE event is
##	# sent to this window
##	def OnCloseWindow(self, event):
##		# tell the window to kill itself
##		self.Destroy()
##
##
##
### Every wxWindows application must have a class derived from wxApp
##class MyApp(wxApp):
##
##    # wxWindows calls this method to initialize the application
##    def OnInit(self):
##
##        # Create an instance of our customized Frame class
##        frame = MyFrame(NULL, -1, "This is a test")
##        frame.Show(true)
##
##        # Tell wxWindows that this is our main window
##        self.SetTopWindow(frame)
##
##        # Return a success flag
##        return true
##
##
##app = MyApp(0)     # Create an instance of the application class
##app.MainLoop()     # Tell it to start processing events

