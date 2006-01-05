import re

import ctypes

import win32functions
import findbestmatch
import handleprops

#=========================================================================
class WindowNotFoundError(Exception):
	pass

#=========================================================================
class WindowAmbiguousError(Exception):
	pass



#=========================================================================
def find_window(**kwargs):
	"Return the "
	windows = find_windows(**kwargs)
	
	if not windows:
		raise WindowNotFoundError()
	
	if len(windows) > 1:
		raise WindowAmbiguousError(
			"There are %d windows that match the criteria %s"% (
			len(windows),
			str(kwargs),
			)
		)
	
	return windows[0]

#=========================================================================
def find_windows(class_name = None,
				class_name_re = None,
				parent = None,
				process = None,
				title = None,
				title_re = None,
				top_level_only = True,
				visible_only = True,
				enabled_only = True,
				best_match_title = None
	):
	"""Find windows based on criteria passed in
	
	Possible values are: 
		class_name		Windows with this window class
		class_name_re	Windows whose class match this regular expression
		parent			Windows that are children of this
		process			Windows running in this process
		title			Windows with this Text
		title_re		Windows whose Text match this regular expression
		top_level_only	Top level windows only (default=True)
		visible_only	Visible windows only (default=True)
		enabled_only	Enabled windows only (default=True)
	"""
	
	
	
	if top_level_only:
		windows = enum_windows()
		
		if parent:	
			windows = [win for win in windows if win.Parent == parent]
			
	else:
		if parent:
			windows = enum_child_windows(parent)
		else:
			# find all the children of the desktop
			parent = win32functions.GetDesktopWindow()
			windows = enum_child_windows(parent)
			
			windows = [win for win in windows if handleprops.parent(win) == parent]
	
	
	if class_name and windows:
		windows = [win for win in windows if class_name == handleprops.classname(win)]
		
	if class_name_re and windows:
		windows = [win for win in windows 
			if re.match(class_name_re, handleprops.classname(win))]
		
	if process and windows:
		try:
			process_id = win.ProcessID
		except AttributeError:
			process_id = process
			
		windows = [win for win in windows if process == process_id]
	
	
	if title and windows:
		windows = [win for win in windows 
			if title == handleprops.text(win)]
	
	elif title_re and windows:
		windows = [win for win in windows 
			if re.match(title_re, handleprops.text(win))]
	
	elif best_match_title and windows:
		windows = [findbestmatch.find_best_control_match(best_match_title, wins),]
		
	if visible_only and windows:
		windows = [win for win in windows if handleprops.isvisible(win)]

	if enabled_only and windows:
		windows = [win for win in windows if handleprops.isenabled(win)]
	
	return windows

#=========================================================================
def enum_windows():
	"Return a list of handles of all the top level windows"
	windows = []
	
	# The callback function that will be called for each HWND
	# all we do is append the wrapped handle
	def enum_win_proc(hwnd, lparam):
		windows.append(hwnd)
		return True

	# define the type of the child procedure
	EnumWindowProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_long, ctypes.c_long)	
	
	# 'construct' the callback with our function
	proc = EnumWindowProc(enum_win_proc)

	# loop over all the children (callback called for each)
	win32functions.EnumWindows(proc, 0)
	
	# return the collected wrapped windows
	return windows


#=========================================================================
def enum_child_windows(handle):
	"Return a list of handles of the child windows of this handle"

	# this will be filled in the callback function
	childWindows = []

	# callback function for EnumChildWindows
	def enumChildProc(hWnd, LPARAM):

		# append it to our list
		childWindows.append(hWnd)

		# return true to keep going
		return True

	# define the child proc type
	EnumChildProc = WINFUNCTYPE(c_int, HWND, LPARAM)	
	proc = EnumChildProc(enumChildProc)

	# loop over all the children (callback called for each)
	EnumChildWindows(handle, proc, 0)

	return childWindows


#=========================================================================
def Main():
	windows = find_windows(
		class_name_re = "#32770", 
		enabled_only = False, 
		visible_only = False)
	
	for win in windows: 
		print "==" * 20
		print handleprops.dumpwindow(win)
	


if __name__ == "__main__":
	Main()