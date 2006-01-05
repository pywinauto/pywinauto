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

import time
import os.path
import re

import ctypes

import win32structures
import win32functions
import win32defines
import controls
import findbestmatch
import controlproperties
import controlactions
import XMLHelpers


class AppStartError(Exception):
	pass

class ProcessNotFoundError(Exception):
	pass

class AppNotConnected(Exception):
	pass

class WindowIsDisabled(Exception):
	pass

class WindowNotFoundError(Exception):
	pass


#=========================================================================
def make_valid_filename(filename):
	for char in ('\/:*?"<>|'):
		filename = filename.replace(char, '#%d#'% ord(char))
	return filename

#=========================================================================
def WalkDialogControlAttribs(app, attr_path):

	# get items to select between
	# default options will filter hidden and disabled controls
	# and will default to top level windows only
	wins = FindWindows(process = app.process)

	# try to find the item
	dialogWin = findbestmatch.find_best_control_match(attr_path[0], wins)
	# get text for each item 
	#texts = [w.Text for w in wins]
	
	dlg = ActionDialog(dialogWin, app)
	
	attr_value = dlg
	for attr in attr_path[1:]:
		attr_value = getattr(attr_value, attr)

	return dlg, attr_value

#=========================================================================
class ActionControl(object):
	def __init__(self, wrapped_hwnd):
		if isinstance(wrapped_hwnd, ActionControl):
			self._ = wrapped_hwnd._
		else:
			self._ = wrapped_hwnd
		
		controlactions.add_actions(self)

#=========================================================================
class ActionDialog(ActionControl):
	def __init__(self, wrapped_hwnd, app = None, props = None):
		ActionControl.__init__(self, wrapped_hwnd)
		self.app = app
		
		dlg_controls = [self._, ]
		dlg_controls.extend(self._.Children)
		try:
			ret = controlproperties.SetReferenceControls(dlg_controls, props)
		
			if ret == 7:
				print "Dialog matched Great"
			elif ret == 5:
				print "Hmmm1: All classes were the same but not all ID's"
			elif ret == 3:
				print "Hmmm2: All Id's were the same but not all classes"
		except:
			pass
		
	def MenuSelect(self, path):
		item_id = FindMenu(self._.MenuItems, path)

		# TODO: and what does WM_MENUSELECT do?
		self._.PostMessage(win32defines.WM_COMMAND, item_id)
		
	def __getattr__(self, attr):
		# get text for each item
		#ctrl_texts = [
		#	ctrl.Text or ctrl.FriendlyClassName for ctrl in self._.Children]

		ctrl = findbestmatch.find_best_control_match(attr, self._.Children)

		# return the control
		return ActionControl(ctrl)
	
	def _write(self, filename):
		if self.app and self.app.xmlpath:
			filename = os.path.join(self.app.xmlpath, filename + ".xml")
		
		controls = [self._]
		controls.extend(self._.Children)
		props = [c.GetProperties() for c in controls]
		
		XMLHelpers.WriteDialogToFile(filename, props)

#=========================================================================
def wait_for_function_success(func, *args, **kwargs):
	
	if kwargs.has_key('time_interval'):
		time_interval = kwargs['time_interval']
	else:
		time_interval= .09 # seems to be a good time_interval
		
	if kwargs.has_key('timeout'):
		timeout = kwargs['timeout']
	else:
		timeout = 1
		
	# keep going until we either hit the return (success)
	# or an exception is raised (timeout)
	while 1:
		try:
			return func(*args, ** kwargs)
		except:
			if timeout > 0:
				time.sleep (time_interval)
				timeout -= time_interval
			else:
				raise

#=========================================================================
class DynamicAttributes(object):
	def __init__(self, app):
		self.app = app
		self.attr_path = []
		
	def __getattr__(self, attr):
		# do something with this one
		# and return a copy of ourselves with some
		# data related to that attribute
		
		if attr == "_":
			dlg, ctrl =  wait_for_function_success(self.__resolve_attributes, self)				
			
			return ctrl._
		
		else:			
			self.attr_path.append(attr)
			return self
	
	def __resolve_attributes(self):
		dlg, final = WalkDialogControlAttribs(self.app, self.attr_path)	
		return dlg, final
	
	def __do_call(self, *args, **kwargs):
		dlg, func = self.__resolve_attributes()

		return dlg, func(*args, **kwargs)
	
	def __call__(self, *args, **kwargs):
		dlg, return_val = wait_for_function_success(self.__do_call, *args, **kwargs)
		
		
		return return_val
	
#====================================================================
def FindMenu(menu_items, path_to_find):
	# get the cleaned names from teh menu items
	
	item_texts = [item['Text'] for item in menu_items]

	# get the first part (and remainder)
	parts = path_to_find.split("->", 1)
	current_part = parts[0]	

	# find the item that best matches the current part
	item = findbestmatch.find_best_match(current_part, item_texts, menu_items)
	
	# if there are more parts - then get the next level
	if parts[1:]:
		return FindMenu(item['MenuItems'], parts[1])

	else:
		return item['ID']
		
#=========================================================================
class Application(object):
	def __init__(self):
		self.process = None
		self.xmlpath = ''
		self.window_cache = {}
	
	def _start(self, cmd_line, timeout = 2000):
		"Starts the application giving in cmd_line"
		
		si = win32structures.STARTUPINFOW()
		si.sb = ctypes.sizeof(si)

		pi = win32structures.PROCESS_INFORMATION()

		# we need to wrap the command line as it can be modified
		# by the function
		command_line = ctypes.c_wchar_p(unicode(cmd_line))

		# Actually create the process
		ret = win32functions.CreateProcess(
			0, 					# module name
			command_line,		# command line
			0, 					# Process handle not inheritable. 
			0, 					# Thread handle not inheritable. 
			0, 					# Set handle inheritance to FALSE. 
			0, 					# No creation flags. 
			0, 					# Use parent's environment block. 
			0,  				# Use parent's starting directory. 
			ctypes.byref(si),  	# Pointer to STARTUPINFO structure.
			ctypes.byref(pi)) 	# Pointer to PROCESS_INFORMATION structure

		# if it failed for some reason
		if not ret:
			raise AppStartError("CreateProcess: " + str(ctypes.WinError()))

		if win32functions.WaitForInputIdle(pi.hProcess, timeout):
			raise AppStartError("WaitForInputIdle: " + str(ctypes.WinError()))

		self.process = Process(pi.dwProcessId)
		
		return self
	
	
	def _connect(self, **kwargs):
		"Connects to an already running process"
		
		connected = False
		if 'process' in kwargs:
			self.process = Process(kwargs['process'])
			connected = True

		elif 'handle' in kwargs:
			self.process = kwargs['handle'].Process
			connected = True
		
		elif 'path' in kwargs:
			self.process = Process.process_from_module(kwargs['path'])
			connected = True

		else:
			handle = FindWindow(**kwargs)
			self.process = handle.Process
			connected = True
						
		if not connected:
			raise RuntimeError("You must specify one of process, handle or path")
		
		return self
	
	def _windows(self):
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")
		
		return self.process.windows()		
				
			
	def _window(self, *args, **kwargs):
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")

		if args:
			raise RuntimeError("You must use keyword arguments")
			
		# add the restriction for this particular process
		kwargs['process'] = self.process._id

		# try and find the dialog (waiting for a max of 1 second
		win = wait_for_function_success (FindWindow, *args, **kwargs)
		win = ActionDialog(win, self)

		# wrap the Handle object (and store it in the cache
		return ActionDialog(win, self)
	
	def __getattr__(self, key):
		"Find the dialog of the application"
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")		

		return getattr(DynamicAttributes(self), key)
					
#=========================================================================
class Process(object):
	"A running process"
	def __init__(self, ID, module = None):
		# allow any of these to be set
		
		self._id = ID
		
		if module:
			self._module = module
		else:
			self._module = None
							
	def id(self):
		return self.id_
		
	def windows(self):
		return FindWindows(process = self)
			
	def module(self):
		# Set instance variable _module if not already set
		if not self._module:
			hProcess = win32functions.OpenProcess(0x400 | 0x010, 0, self._id) # read and query info

			# get module name from process handle
			filename = (ctypes.c_wchar * 2000)()
			win32functions.GetModuleFileNameEx(hProcess, 0, ctypes.byref(filename), 2000)
	
			# set variable
			self._module = filename.value

		return self._module
	
	def __eq__(self, other):
		if isinstance(other, Process):
			return self._id == other._id
		else:
			return self._id == other
	
	@staticmethod
	def process_from_module(module):
		"Return the running process with path module"
		
		# set up the variable to pass to EnumProcesses
		processes = (ctypes.c_int * 2000)()
		bytes_returned = ctypes.c_int()
		# collect all the running processes
		ctypes.windll.psapi.EnumProcesses(
			ctypes.byref(processes), 
			ctypes.sizeof(processes), 
			ctypes.byref(bytes_returned))

		# check if the running process
		for i in range(0, bytes_returned.value / ctypes.sizeof(ctypes.c_int)):
			temp_process = Process(processes[i])
			if module.lower() in temp_process.module().lower():
				return temp_process

		raise ProcessNotFoundError("No running process - '%s' found"% module)

#=========================================================================
def FindWindow(**kwargs):

	windows = FindWindows(**kwargs)
	
	if not windows:
		raise WindowNotFoundError
	
	if len(windows) > 1:
		raise "ambiguous"
	
	return windows[0]

#=========================================================================
def FindWindows(class_name = None,
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
			windows = controls.WrapHandle(parent).Children
		else:
			parent = win32functions.GetDesktopWindow()
			windows = controls.WrapHandle(parent).Children
			windows = [win for win in windows if win.Parent == parent]
	
	if class_name and windows:
		windows = [win for win in windows if class_name == win.Class]

	if class_name_re and windows:
		windows = [win for win in windows if re.match(class_name_re, win.Class)]
		
	if process and windows:	
		windows = [win for win in windows if process == win.ProcessID]
	
	
	if title and windows:
		windows = [win for win in windows if title == win.Text]
	
	elif title_re and windows:
		windows = [win for win in windows if re.match(title_re, win.Text)]
	
	elif best_match_title and windows:
		windows = [findbestmatch.find_best_control_match(best_match_title, wins),]
		
	if visible_only and windows:
		windows = [win for win in windows if win.IsVisible]

	if enabled_only and windows:
		windows = [win for win in windows if win.IsEnabled]
	
	return windows

#=========================================================================
def enum_windows():
	windows = []
	
	# The callback function that will be called for each HWND
	# all we do is append the wrapped handle
	def enum_win_proc(hwnd, lparam):
		windows.append(controls.WrapHandle(hwnd))
		return True

	# define the type of the child procedure
	EnumWindowProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_long, ctypes.c_long)	
	
	# 'construct' the callback with our function
	proc = EnumWindowProc(enum_win_proc)

	# loop over all the children (callback called for each)
	win32functions.EnumWindows(proc, 0)
	
	# return the collected wrapped windows
	return windows


if __name__ == '__main__':
	import test_application
	test_application.Main()