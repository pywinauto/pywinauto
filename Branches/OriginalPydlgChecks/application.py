# Find Window 2

# Find a window based on:
#	Parent
#	Process
#	Class
#	Title
#	TopLevel = true/false
import time
import os.path
import sys
from pprint import pprint
import ctypes
import re

import win32structures
import win32functions
import win32defines
import controls
import findbestmatch
import controlproperties
import controlactions
import XMLHelpers

WRITE_DIALOGS_TO_XML = True
READ_DIALOGS_FROM_XML = False
# TODO: Create a class that makes it easy to deal with a single window
#       (e.g. no application)

# TODO: Allow apps to be started in a different thread so we don't lock up
#  - this is being done already - the problem is that some messages cannot
#    be sent across processes if they have pointers (so we need to send a 
#    synchronous message which waits for the other process to respond 
#    before returning)

# TODO: Message traps - how to handle unwanted message boxes popping up?
# a) Wait for an Exception then handle it there
# b) set a trap waiting for a specific dialog

# TODO: Implement an opional timing/config module so that all timing can 
#       be customized

# TODO: Handle adding reference controls

# TODO: Add referencing by closes static (or surrounding group box?)

# TODO: find the reference name of a variable .e.g so that in Dialog._write() we 
#       can know the variable name that called the _write on (this we don't have
#       to repeat the XML file name!)



# BringWindowToTop
# EnumThreadWindows
# GetGUIThreadInfo
# GetTopWindow
# 

# should be possible to get the modules used by a process


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



class config(object):
	pass
config.window_timout = 3 # 3 second wait for a dialog
config.retry_interval = .2 # 1/5 of a second wait between each retry
#config.delay_after_click = .05 # 1/5 of a second wait between each retry





# a) Dialogs returned from App (dialog)
#    should respond to _ctrl and their own actions
# b) Controls returned from Dialogs
#    should respond to _ctrl and their own actions
# c) Dialogs should be able to respond to calls of
#    FindControl
# d) Apps should be able to respond to calls of
#    FindDialog
# e) Dialogs need to be able to respond to MenuSelect

# app.dlgTitle
# app._Dialog(dlgSearchParams): raises WindowNotFound, WindowAmbiguous

# dlg.ControlTitle
# dlg._Control(ctrlSearchParams)

# dlg._Menu(menupath).Select()
# OR???
# dlg._Menu.File.Open.Select()

# dlg._.IsVisible
# dlg.Close()

# ctrl._.IsVisible
# ctrl.Click()



#App.Dialog.Control.Action()
#or App.Dialog.Action()



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

	dialogWin = findbestmatch.find_best_control_match(attr_path[0], wins)
	# get text for each item 
	#texts = [w.Text for w in wins]

	# try to find the item
	#dialogWin = findbestmatch.find_best_match(attr_path[0], texts, wins)

	if app.xmlpath and READ_DIALOGS_FROM_XML:
		dlgXML = os.path.join(app.xmlpath, attr_path[0] + ".xml")
		if os.path.exists(dlgXML):
			props = XMLHelpers.ReadPropertiesFromFile(dlgXML)
			
			for i, val in enumerate(props):
				props[i] = controlproperties.ControlProps(val)
				
	
			dlg = ActionDialog(dialogWin, app, props)
	
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
			
			self.app._write_dialog(self.attr_path[0], dlg)
			return ctrl._
		
		else:			
			self.attr_path.append(attr)
			return self
	
	def __resolve_attributes(self):
		dlg, final = WalkDialogControlAttribs(self.app, self.attr_path)	
		return dlg, final
	
	def __do_call(self, *args, **kwargs):
		dlg, func = self.__resolve_attributes()

		# the function may close the dialog! so 
		# write it out before we call the function
		print "writing %s" %self.attr_path[0]
		self.app._write_dialog(self.attr_path[0], dlg)

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
	

	def _write_dialog(self, name, dlg, force_rewrite = False):

		if force_rewrite or name not in self.window_cache:
			self.window_cache[name] = dlg

			# make sure that there are no invalid chars in 
			filename = os.path.join(self.xmlpath, name + ".xml")

			# get the properties for each control as a list
			controls = [dlg._]
			controls.extend(dlg._.Children)
			props = [c.GetProperties() for c in controls]

			# write those properties to the XML file
			XMLHelpers.WriteDialogToFile(filename, props)
			
			# write the request matches which XML
			import pickle
			mappingFile = os.path.join(self.xmlpath, "request_to_xml_map.txt")
			if not os.path.exists(mappingFile):
				print "blah"
				f = open(mappingFile, "w")
				pickle.dump({}, f)
				f.close()
					
			mapping = open(mappingFile, "r")
			xmltofile = pickle.load(mapping)
			mapping.close()

			print xmltofile

			if name not in xmltofile:
				xmltofile[name] = name + ".xml"
			
			f = open(mappingFile, "w")
			pickle.dump(xmltofile, f)
			f.close()

			
			
			
			

		
	
	def _window(self, *args, **kwargs):
		if not self.process:
			raise AppNotConnected("Please use _start or _connect before trying anything else")

		if args:
			raise RuntimeError("You must use keyword arguments")
			
		used_args = tuple(["%s_%s"%(k, kwargs[k]) for k in kwargs])
		used_args = make_valid_filename("-".join(used_args))
		
		
		
		if used_args not in self.window_cache or \
			not win32functions.IsWindow(self.window_cache[used_args]._):

			# add the restriction for this particular process
			kwargs['process'] = self.process._id

			# try and find the dialog (waiting for a max of 1 second
			win = wait_for_function_success (FindWindow, *args, **kwargs)
			win = ActionDialog(win, self)

			# wrap the Handle object (and store it in the cache
			#self.window_cache[used_args] = ActionDialog(win, self)
		else:
			win = self.window_cache[used_args]
			
		if WRITE_DIALOGS_TO_XML and self.xmlpath:
			self._write_dialog(used_args, win)
			
		return self.window_cache[used_args]
	
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




#def close_application(process_info):
#	win32functions.ExitProcess(process_info.hProcess, 0)
	


# Currently required to work with a single dialog
#
#  app = Application()
#  app._connect(some parameters)
#  app.dlg.something
# 
# or
# dlg = Application()._connect(some parameters)
# dlg.something
#
# and we would like something like
#
# dlg = Window(some parameters)
# dlg.something



def TestNotepad():
	
	
	sleeping = False
	def sleeper(delay):
		if sleeping:
			time.sleep(delay)

		return
	
	
	if 1:

		# ensure that the XML path exists
		example_path = r"examples\notepad_test"
		try:
			os.makedirs(example_path)
		except OSError:
			pass

		# test that trying to _connect to a non existent app fails
		try:
			app = Application()
			app._connect(path = ur"No process with this please")
			assert 0
		except ProcessNotFoundError:
			pass

		# test that trying to _connect to a non existent app fails
		try:
			app = Application()
			app._start(cmd_line = ur"No process with this please")
			assert 0
		except AppStartError:
			pass

		# try when it isn't connected
		try:
			app = Application()
			#app._start(ur"c:\windows\system32\notepad.exe")
			app.Notepad.Click()
			assert 0
		except AppNotConnected:
			pass


		app = Application()

		try:
			app._connect(path = ur"c:\windows\system32\notepad.exe")
		except ProcessNotFoundError:	
			app._start(ur"c:\windows\system32\notepad.exe")

		time_start = time.time()


		app.Notepad.MenuSelect("File->PageSetup")
		sleeper(.2)
		app.PageSetupDlg.ComboBox1.Select(4)
		sleeper(.2)
				
		app.PageSetupDlg.Printer.Click()
		sleeper(.2)
		
		
		TestingCheckBox = 1
		if TestingCheckBox:
			# Open the Connect to printer dialog so we can 
			# try out checking/unchecking a checkbox
			app.PageSetupDlg.Network.Click()
			sleeper(1)
			app.ConnectToPrinter.ExpandByDefault.Check()
			sleeper(1)
			app.ConnectToPrinter.ExpandByDefault.UnCheck()
			sleeper(1)

			# try doing the same by using click
			app.ConnectToPrinter.ExpandByDefault.Click()
			sleeper(1)
			app.ConnectToPrinter.ExpandByDefault.Click()
			sleeper(1)

			# close the dialog
			app.ConnectToPrinter.Cancel.Click()


		
		app.PageSetupDlg2.Properties.Click()
		sleeper(.2)
		docProps = app._window(title_re = ".*Document Properties")
		sleeper(.2)


		TestingTabSelect = 1
		if TestingTabSelect:
			docProps.TabCtrl.Select(0)
			sleeper(.5)
			docProps.TabCtrl.Select(1)
			sleeper(.5)
			docProps.TabCtrl.Select(2)
			sleeper(.5)


			docProps.TabCtrl.Select("PaperQuality")
			sleeper(.5)

			docProps.TabCtrl.Select("JobRetention")
			sleeper(.5)

			docProps.TabCtrl.Select("Layout")
			sleeper(.5)


		TestingRadioButton = 1
		if TestingRadioButton:
			docProps.RotatedLandscape.Click()
			sleeper(.2)
			docProps.BackToFront.Click()
			sleeper(.2)
			docProps.FlipOnShortEdge.Click()
			
			sleeper(.5)

			docProps.Portrait.Click()
			sleeper(.2)
			docProps._None.Click()
			sleeper(.2)
			docProps.FrontToBack.Click()
			sleeper(.5)
		

		#print docProps._ctrl
		advbutton = docProps.Advanced
		advbutton.Click()
		sleeper(.2)

		# close the 4 windows
		app._window(title_re = ".* Advanced Options").Ok.Click()
		sleeper(.2)
		docProps.Cancel.Click()
		sleeper(.2)
		app.PageSetupDlg2.OK.Click()
		sleeper(.2)
		app.PageSetupDlg.Ok.Click()
		sleeper(.2)
		
		# type some text
		app.Notepad.Edit.SetText("I am typing some text to Notepad\r\n\r\nAnd then I am going to quit")
		sleeper(1)


		# exit notepad
		app.Notepad.MenuSelect("File->Exit")
		app.Notepad.No.Click()
	
	
	print "Time:", time.time() - time_start

	if 0:
		app = Application()._connect(path = r"c:\program files\Textpad 4\Textpad.exe")
		
		print "Windows in this Process"
		for win in app._windows():
			print "%20s\t'%s'" %(win.Class, win.Text)



def WriteNotepadXMLs():	

	# set up the application
	app = Application()
	app.xmlpath = r"examples\notepad_xml"
	
	# ensure that the XML path exists
	try:
		os.makedirs(app.xmlpath)
	except OSError:
		pass

	# either connect to or start the application
	try:
		app._connect(path = ur"c:\windows\system32\notepad.exe")
	except ProcessNotFoundError:	
		app._start(ur"c:\windows\system32\notepad.exe")

	
	#Write the main dialog
	#app.notepad._write("Notepad")
	
	# bring up the next dialog
	app.Notepad.MenuSelect("File->PageSetup")
	
	# write it out
	#app.PageSetup._write("PageSetup")

	app.PageSetup.Printer.Click()
	#app.PageSetup2._write("PageSetup2")

	app.PageSetup2.Properties.Click()
	
	# TODO: This will cause a problem, here is yet another place that we
	# have to subvert the normal operation if we are working on the
	# localised software!
	docProps = app._window(title_re = ".*Document Properties")
	#docProps._write("docProps")

	# select each of the tabs
	docProps.TabCtrl.Select("PaperQuality")
	#docProps._write("docProps.PaperQuality")
	docProps.TabCtrl.Select("JobRetention")
	#docProps._write("docProps.JobRetention")
	docProps.TabCtrl.Select("Layout")
	#docProps._write("docProps.Layout")

	docProps.Advanced.Click()

	# close the 4 windows
	AdvancedOptions = app._window(title_re = ".* Advanced Options")
	#AdvancedOptions._write('AdvancedOptions')
	AdvancedOptions.Ok.Click()

	docProps.Cancel.Click()
	app.PageSetupDlg2.OK.Click()
	app.PageSetupDlg.Ok.Click()

	# type some text
	app.Notepad.Edit.SetText("I am typing some text to Notepad\r\n\r\nAnd then I am going to quit")

	# exit notepad
	app.Notepad.MenuSelect("File->Exit")
	app.Notepad2.No.Click()
		


def UseNotepadXLMs():

	# set up the application
	app = Application()
	app.xmlpath = r"examples\notepad_xml"

	# ensure that the XML path exists
	try:
		os.makedirs(app.xmlpath)
	except OSError:
		pass

	app.requireXML = True	
	
	# we have X dialogs
	# Notepad			".* - Notepad", 'Notepad'
	# PageSetup			"Page Setup", '#32770'
	# PageSetup2		"Page Setup"
	# docProps			".*Document Properties"
	# AdvancedOptions	".* Advanced Options"
	# Notepad2			"Notepad"
	
	# so for English we can use the title, regular expression
	# but then there needs to be a mapping for the Localised software
	# so that when we specify the same code - but it looks at the 
	# appropriate XML file to figure out if the correct dialog is open
	
	# so in english
	app.Notepad # gets the notepad dialog
	
	# while in the localized product
	app.Notepad  #get's the appropriate XML file, finds the current dialogs
	             # and returns the dialog that matches the XML
	             
	# then that brings us to the difficult part.
	
	# in English
	docProps = app._window(title_re = ".*Document Properties")
	# this finds the window in app's process that has a title that
	# matches this regular expression

	# while in localised
	docProps = app._window(title_re = ".*Document Properties")
	# I guess this would have to look at each of the XML files to 
	# figure out which one of the XML files to figure out to use
	
	# a configuation could be kept on the __getattr__ method of the 
	# application it could
	
	
	
	

	# either connect to or start the application
	try:
		app._connect(path = ur"c:\windows\system32\notepad.exe")
	except ProcessNotFoundError:	
		app._start(ur"c:\windows\system32\notepad.exe")

	
	#Write the main dialog
	app.notepad._write("Notepad")
	
	# bring up the next dialog
	app.Notepad.MenuSelect("File->PageSetup")
	
	# write it out
	app.PageSetup._write("PageSetup")

	app.PageSetup.Printer.Click()
	app.PageSetup2._write("PageSetup2")

	app.PageSetup2.Properties.Click()
	
	# TODO: This will cause a problem, here is yet another place that we
	# have to subvert the normal operation if we are working on the
	# localised software!
	docProps = app._window(title_re = ".*Document Properties")
	docProps._write("docProps")

	# select each of the tabs
	docProps.TabCtrl.Select("PaperQuality")
	docProps._write("docProps.PaperQuality")
	docProps.TabCtrl.Select("JobRetention")
	docProps._write("docProps.JobRetention")
	docProps.TabCtrl.Select("Layout")
	docProps._write("docProps.Layout")

	docProps.Advanced.Click()

	# close the 4 windows
	AdvancedOptions = app._window(title_re = ".* Advanced Options")
	AdvancedOptions._write('AdvancedOptions')
	AdvancedOptions.Ok.Click()

	docProps.Cancel.Click()
	app.PageSetupDlg2.OK.Click()
	app.PageSetupDlg.Ok.Click()

	# type some text
	app.Notepad.Edit.SetText("I am typing some text to Notepad\r\n\r\nAnd then I am going to quit")

	# exit notepad
	app.Notepad.MenuSelect("File->Exit")
	app.Notepad2.No.Click()







def TestPaint():

		app = Application()

		try:
			app._connect(path = ur"c:\windows\system32\mspaint.exe")
		except ProcessNotFoundError:	
			app._start(ur"c:\windows\system32\mspaint.exe")


		pwin = app._window(title_re = ".* - Paint")
		
		canvas = pwin.Afx100000008
		
		# make sure the pencil tool is selected
		pwin.Tools2.Click(coords = (91, 16))
		
		size = 30
		num_slants = 8
		
		# draw the axes
		canvas.PressMouse(coords = (size, size * num_slants)) 
		canvas.MoveMouse(coords = (size*num_slants, size*num_slants)) # x and y axes
		canvas.MoveMouse(coords = (size * num_slants, size))
		canvas.ReleaseMouse()

		# now draw the lines
		for i in range(1, num_slants):
			canvas.PressMouse(coords = (size * num_slants, i * size)) # start

			canvas.MoveMouse(coords = (size * (num_slants - i), size * num_slants)) # x and y axes

			canvas.ReleaseMouse()
		
		
		canvas._.CaptureAsImage().save(r"c:\test.png")		
	
	
	
if __name__ == "__main__":
	#TestNotepad()

	WriteNotepadXMLs()
	#TestNotepadWriting()	
	
	
	
#	# Select that menu item
#	try:
#		x = app.notepad 
#		app.notepad.MenuSelect("File->Page Setup")
#	except findbestmatch.WindowIsDisabled:
#		for win in app._windows():
#			print "%20s '%s'" % (win.Class, win.Texts)
#		print "Hmmm - a function to close windows would be nice:-)"
#		
#	
#
#	#time.sleep(.5)
#	app.page_setup.Edit1.TypeKeys("{HOME}+{END}{BKSP}23")
#	#time.sleep(1)


#	
#	app.Notepad.Edit.Select(0,0)
#	app.Notepad.Edit.SetText(u"[Woweee\r\nthis text will dissappear", append=False)
#	#app.Notepad.Edit.
#	app.Notepad.Edit.Select(9,-1)
#	app.Notepad.Edit.SetText(u"and this is the end]")
#
#		