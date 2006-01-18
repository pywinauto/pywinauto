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

"""The application module is the main one that users will user first.

When starting to automate and application you must initialize an instance
of the Application class. Then you must _start that application or _connect 
to a running instance of that application.

Once you have an Application instance you can access dialogs in that 
application either by using one of the methods below.::

   dlg = app.YourDialogTitle
   dlg = app._window(title = "your title", class = "your class", ...) 
   dlg = app['Your Dialog Title']
   
Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways.::

  ctrl = dlg.YourControlTitle
  ctrl = dlg._control(title = "Your control", class = "Button", ...)
  ctrl = dlg["Your control"]
  
**Note:** For attribute access of controls and dialogs you do not have to 
have the title of the control exactly, it does a best match of the 
avialable dialogs or controls.

**See also:**
  findwindows.find_windows for the keyword arguments that can be
  passed to both Application._window and ActionDialog._control
  
"""

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
import findwindows 

# Following only needed for writing out XML files
# and can be (also requires elementtree)
try:
	import XMLHelpers
except ImportError:
    pass

class AppStartError(Exception):
	pass

class ProcessNotFoundError(Exception):
	pass

class AppNotConnected(Exception):
	pass

class WindowIsDisabled(Exception):
	pass



#=========================================================================
def make_valid_filename(filename):
	r"""Return a valid file name for the string passed in.
	
	Replaces any character in ``:\/*?"<>|`` with ``'#%d#'% ord(char)``"""
	for char in ('\/:*?"<>|'):
		filename = filename.replace(char, '#%d#'% ord(char))
	return filename


#=========================================================================
class ActionDialog(object):
	"""ActionDialog wraps the dialog you are interacting with
	
	It provides support for finding controls using attribute access,
	item access and the _control(...) method.
	
	You can dump information from a dialgo to XML using the _write() method
	
	A screenshot of the dialog can be taken using the underlying wrapped
	HWND ie. my_action_dlg.wrapped_win.CaptureAsImage().save("dlg.png").
	This is only available if you have PIL installed (fails silently 
	otherwise).
	"""
	def __init__(self, hwnd, app = None, props = None):
		"""Initialises an ActionDialog object::
		
		   hwnd (required) The handle of the dialog
		   app An instance of an Application Object
		   props future use (when we have an XML file for reference)
		  
		"""
		
		self.wrapped_win = controlactions.add_actions(
			controls.WrapHandle(hwnd, True))
		
		self.app = app
		
		dlg_controls = [self.wrapped_win, ]
		dlg_controls.extend(self.wrapped_win.Children)

	def __getattr__(self, key):
		return self[key]
		
	def __getitem__(self, attr):
	
		# if it is an integer - just return the
		# child control at that index
		if isinstance(attr, (int, long)):
			return self.wrapped_win.Children[attr]
	
		# so it should be a string
		# check if it is an attribute of the wrapped win first
		try:
			return getattr(self.wrapped_win, attr)
		except (AttributeError, UnicodeEncodeError):
			pass
			
		# find the control that best matches our attribute		
		ctrl = findbestmatch.find_best_control_match(
			attr, self.wrapped_win.Children)

		# add actions to the control and return it
		return controlactions.add_actions(ctrl)
	
	def _write(self, filename):
		if self.app and self.app.xmlpath:
			filename = os.path.join(self.app.xmlpath, filename + ".xml")
		
		controls = [self.wrapped_win]
		controls.extend(self.wrapped_win.Children)
		props = [c.GetProperties() for c in controls]
		
		XMLHelpers.WriteDialogToFile(filename, props)
	
	def _control(self, **kwargs):
		# add the restriction for this particular process
		kwargs['parent'] = self.wrapped_win
		kwargs['process'] = self.app.process
		kwargs['top_level_only'] = False

		# try and find the dialog (waiting for a max of 1 second
		ctrl = findwindows.find_window(**kwargs)
		#win = ActionDialog(win, self)
		
		return controlactions.add_actions(controls.WrapHandle(ctrl))

		
		
#=========================================================================
def WalkDialogControlAttribs(app, attr_path):
	
	if len(attr_path) != 2:
		raise "yo you yo"

	# get items to select between
	# default options will filter hidden and disabled controls
	# and will default to top level windows only
	wins = findwindows.find_windows(process = app.process)

	# wrap each so that find_best_control_match works well
	wins = [controls.WrapHandle(w, True) for w in wins]


	if isinstance(attr_path[0], (int, long)):
		dialogWin  = wins[attr_path[0]]
	else:
		# try to find the item
		dialogWin = findbestmatch.find_best_control_match(attr_path[0], wins)
		
	# already wrapped
	dlg = ActionDialog(dialogWin, app)
	
	# for each of the other attributes ask the 
	attr_value = dlg
	for attr in attr_path[1:]:
		try:
			attr_value = getattr(attr_value, attr)
		except UnicodeEncodeError:		
			attr_value = attr_value[attr]

	return dlg, attr_value


#=========================================================================
class DynamicAttributes(object):
	def __init__(self, app):
		self.app = app
		self.attr_path = []
		
	def __getattr__(self, attr):
		return self[attr]

	def __getitem__(self, attr):
		# do something with this one
		# and return a copy of ourselves with some
		# data related to that attribute
				
		self.attr_path.append(attr)
		
		# if we have a lenght of 2 then we have either 
		#   dialog.attribute
		# or
		#   dialog.control
		# so go ahead and resolve
		if len(self.attr_path) == 2:
			dlg, final = wait_for_function_success(
				WalkDialogControlAttribs, self.app, self.attr_path)
			
			# seing as we may already have a reference to the dialog
			# we need to strip off the control so that our dialog
			# reference is not messed up
			self.attr_path = self.attr_path[:-1]
			
			return final
		
		# we didn't hit the limit so continue collecting the 
		# next attribute in the chain
		return self
		
		
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
class Application(object):
	def __init__(self):
		self.process = None
		self.xmlpath = ''
	
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
			handle = findwindows.find_window(**kwargs)
			self.process = Process(controls.WrapHandle(handle, True).ProcessID)
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
		win = wait_for_function_success (findwindows.find_window, *args, **kwargs)
		#win = ActionDialog(win, self)

		# wrap the Handle object (and store it in the cache
		return ActionDialog(win, self)
	
	def __getitem__(self, key):
		"Find the dialog of the application"
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")		

		return DynamicAttributes(self)[key]

	def __getattr__(self, key):
		"Find the dialog of the application"
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")		

		return self[key]
		#return getattr(DynamicAttributes(self), key)
					
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
		return findwindows.find_windows(process = self._id)
			
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



if __name__ == '__main__':
	import test_application
	test_application.Main()
