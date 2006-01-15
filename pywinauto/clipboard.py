import win32functions
import win32defines

import ctypes

# get all the formats names keyed on the value
all_formats = {}
for x in win32defines.__dict__.keys():
	if x.startswith("CF_"):
		all_formats[getattr(win32defines, x)] = x


#====================================================================
def GetClipboardFormats():
	if not win32functions.OpenClipboard(0):
		raise "Couldn't open clipboard"

	availableFormats = []
	format = 0
	while True:
		# retrieve the next format
		format = win32functions.EnumClipboardFormats(format)

		# stop enumerating because all formats have been
		# retrieved
		if not format:
			break

		availableFormats.append(format)

	win32functions.CloseClipboard()

	return availableFormats


#====================================================================
def GetFormatName(format):
	return all_formats[f]


#====================================================================
def GetData(format = win32defines.CF_UNICODETEXT):
	if not win32functions.OpenClipboard(0):
		raise "Couldn't open clipboard"

	handle = win32functions.GetClipboardData(win32defines.CF_UNICODETEXT)
	
	buffer = ctypes.c_wchar_p(win32functions.GlobalLock(handle))
	
	data = buffer.value
	
	win32functions.GlobalUnlock(handle)
	
	return data
	

#====================================================================
if __name__ == "__main__":
	formats = GetClipboardFormats()
	print formats
	
	print [GetFormatName(f) for f in formats]
	
	print repr(GetData())
