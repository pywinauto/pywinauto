from ctypes import *

import win32functions
from win32defines import *
import win32structures
import findwindows # for children

#=========================================================================
def text(handle):
	length = win32functions.GetWindowTextLength(handle,)

	text = ''
	if length:
		length += 1

		buffer = (c_wchar * length)()

		ret =  win32functions.GetWindowText(handle, byref(buffer), length)

		if ret:
			text = buffer.value

	return text

#=========================================================================
def classname(handle):
		className = (c_wchar * 257)()
		win32functions.GetClassName (handle, byref(className), 256)
		return className.value


#=========================================================================
def parent(handle):
		return win32functions.GetParent(handle)

#=========================================================================
def style(handle):
		return win32functions.GetWindowLong (handle, GWL_STYLE)
		
#=========================================================================
def exstyle(handle):
		return win32functions.GetWindowLong (handle, GWL_EXSTYLE)
		
#=========================================================================
def controlid(handle):
		return win32functions.GetWindowLong (handle, GWL_ID)
		
#=========================================================================
def userdata(handle):
		return win32functions.GetWindowLong (handle, GWL_USERDATA)	
		
#=========================================================================
def contexthelpid(handle):
		return win32functions.GetWindowContextHelpId (handle)	
		
#=========================================================================
def isvisible(handle):
		return win32functions.IsWindowVisible(handle)
		
#=========================================================================
def isunicode(handle):
		return win32functions.IsWindowUnicode(handle)
		
#=========================================================================
def isenabled(handle):
		return win32functions.IsWindowEnabled(handle)
		
#=========================================================================
def clientrect(handle):
		"Returns the client rectangle of the control"
		clientRect = win32structures.RECT()
		win32functions.GetClientRect(handle, byref(clientRect))
		return clientRect
		
#=========================================================================
def rectangle(handle):
		rect = win32structures.RECT()
		win32functions.GetWindowRect(handle, byref(rect))
		return rect

#=========================================================================
def font(handle):
		# set the font
		fontHandle = win32functions.SendMessage(handle,  WM_GETFONT, 0, 0)
	
		# if the fondUsed is 0 then the control is using the 
		# system font
		if not fontHandle:
			fontHandle = win32functions.GetStockObject(SYSTEM_FONT);
	
		# Get the Logfont structure of the font of the control
		font = win32structures.LOGFONTW()
		ret = win32functions.GetObject(fontHandle, sizeof(font), byref(font))
	
		# The function could not get the font - this is probably 
		# because the control does not have associated Font/Text
		# So we should make sure the elements of the font are zeroed.
		if not ret:
			font = win32structures.LOGFONTW()
	
		# if it is a main window
		if (has_style(handle, WS_OVERLAPPED) or \
			has_style(handle, WS_CAPTION)) and \
			not has_style(handle, WS_CHILD):

			if "MS Shell Dlg" in font.lfFaceName or font.lfFaceName == "System":
				# these are not usually the fonts actaully used in for 
				# title bars so we need to get the default title bar font

				# get the title font based on the system metrics rather 
				# than the font of the control itself
				ncms = win32structures.NONCLIENTMETRICSW()
				ncms.cbSize = sizeof(ncms)
				win32functions.SystemParametersInfo(
					SPI_GETNONCLIENTMETRICS, 
					sizeof(ncms), 
					byref(ncms),
					0)

				# with either of the following 2 flags set the font of the 
				# dialog isthe small one (but there is normally no difference!
				if has_style(handle, WS_EX_TOOLWINDOW) or \
				   has_style(handle, WS_EX_PALETTEWINDOW):

					font = ncms.lfSmCaptionFont
				else:
					font = ncms.lfCaptionFont
	
		return font
		
#=========================================================================
def processid(handle):
	"ID of process that controls this window"
	process_id = c_int()
	win32functions.GetWindowThreadProcessId(handle, byref(process_id))	

	return process_id.value

#=========================================================================
def children(handle):
	return findwindows.enum_child_windows(handle)


#=========================================================================
def has_style(handle, tocheck):
	hwnd_style = style(handle)
	return tocheck & hwnd_style == tocheck

#=========================================================================
def has_exstyle(handle, tocheck):
	hwnd_exstyle = exstyle(handle)
	return tocheck & hwnd_exstyle == tocheck

#=========================================================================
def dumpwindow(handle):
	props = {}
	
	for func in (
		text,
		classname,
		rectangle,
		clientrect,
		style,
		exstyle,
		contexthelpid,
		controlid,
		userdata,
		font,
		parent,
		processid,
		isenabled,
		isunicode,
		isvisible,
		children,
		):
	
		props[func.__name__] = func(handle)

	return props
	
#=========================================================================
def Main():
	handle = win32functions.GetDesktopWindow()
	
	for name, value in dumpwindow(handle).items():
		print "%15s\t%s" %(name, value)
	
if __name__ == "__main__":
	Main()
