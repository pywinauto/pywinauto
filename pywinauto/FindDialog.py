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

# pylint:  disable-msg=W0611
"""Explanation of script"""
from pprint import pprint
import re

from ctypes import *
from ctypes.wintypes import *

from win32functions import *
from win32defines import *
from win32structures import *
import controls
from findwindows import find_windows

import handleprops

__revision__ = "0.0.1"		



# import all the necessary files that we want to end 
# up in the Py2exe zip.


import PyDlgCheckerWrapper

#
#def FindWindow(
#	start_window = None,
#	match_title = None,
#	match_class = None,
#	toplevel_only = False,
#	recurse_children = True,
#	this_thread_only = None,
#	)
#
#	if start_window == None:
#		start_window = GetDesktopWindow()
#	
#	if recurse_children:
#		# get the 1st child of the start window
#		win_to_test = GetWindow (start_window, GW_CHILD)
#		
#		wrapped = WrapHandle(win_to_test)
#		
#		if match_title:
#			if re.match(match_title, wrapped.Text)
#				
#		
		
		


#totalWindowCount = 0

##====================================================================
#def FindDialog(titleToFind, caseSensitive = False, testClass = None, startWin = None):
#	"""Find a dialog based on the title
#	
#	
#Returns the dialog that has a title that matches the regular
#expression in titleToFind.
#If caseSensitive == True then it performs a case sensitive match
#If startWin == None then it starts searching from the desktop window
#otherwise it searches the child windows of the specified window."""
#
#	if caseSensitive:
#
#		flags = re.IGNORECASE
#	else:
#		flags = 0
#	
#	titleRe = re.compile(titleToFind, flags)
#
#	# If the startWin is NULL then we are just starting and we
#	# should start with the Desktop window and look from there
#	if startWin == None:
#		startWin = GetDesktopWindow()
#
#	# get the 1st child of the start window
#	winToTest = GetWindow (startWin, GW_CHILD)
#
#	# Now Iterate through all the children of the startwindow
#	# (ie ALL windows, dialogs, controls ) then if the HWND is a dialog
#	# get the Title and compare it to what we are looking for
#	# it makes a check first to make sure that the window has at
#	# least 1 child window
#	while winToTest:
#		global totalWindowCount
#		totalWindowCount += 1
#
#		# get the Title of the Window and if the Title the same as
#		# what we want if So then return it
#		title = controls.WrapHandle(winToTest).Text
#		
#		# Check the title to see if it is the same as the title we
#		# are looking for - if it is then return the handle
#		found = titleRe.search(title)
#		if found:
#		
#			if testClass:
#				if testClass == controls.WrapHandle(winToTest).Class:
#					return winToTest
#			else:
#				return winToTest
#			
#
#		# Now Check through the children of the present window
#		# this is recursive through all the children of the window
#		# It calls FindDialog with the title and the new window
#		# this will keep going recursively until the window is found
#		# or we reach the end of the children
#		tempWin = FindDialog (titleToFind, caseSensitive, testClass, winToTest)
#
#		if tempWin != None:
#			return tempWin
#
#		# So the last one wasnt it just continue with the next
#		# which will be the next window at the present level
#		winToTest = GetWindow (winToTest, GW_HWNDNEXT)
#
#	# we have gotten to here so we didnt find the window
#	# in the current depth of the tree return NULL to say
#	# that we didnt get it and continue at the previous depth
#	return None
#
#
#




#====================================================================
def DrawOutline(rect, colour = None, fill = BS_NULL):
	# create the brush

	colours = {
		"green" : 0x00ff00,
		"blue" : 0xff0000,
		"red" : 0x0000ff,
	}
	
	if colour not in colours:
		colour = 'green'

	colour = colours[colour]

	brush = LOGBRUSH()
	brush.lbStyle = fill
	brush.lbHatch = HS_DIAGCROSS
	
	hBrush = CreateBrushIndirect(byref(brush))
	
	hPen = CreatePen(PS_SOLID, 2, colour)
	
	# get the Device Context
	dc = CreateDC(u"DISPLAY", None, None, None )
	
	SelectObject(dc, hBrush)
	SelectObject(dc, hPen)

	Rectangle(dc, rect.left, rect.top, rect.right, rect.bottom)

	# Delete the brush and pen we created
	DeleteObject(hBrush)
	DeleteObject(hPen)

	# delete the Display context that we created
	DeleteDC(dc)



#============================================================================
def PopulateCommandLineParser():
	from optparse import OptionParser
	
	parser = OptionParser()

	parser.add_option("-w", "--window", dest="windowTitle", metavar="WINDOW", #action = "store",
					  help="The window title to find and test")
	
	parser.add_option("-f", "--xml", dest="xmlFileName",# metavar="FILE",
					  help="save the window information to this XML file")



	parser.add_option("-r", "--refwin", dest="refWindow", #metavar="FILE",
					  action = "append",
					  help="save the domino report to file")
	

	parser.add_option("-x", "--refxml", dest="refXML", #metavar="USER",
					  help="username to access Domino DTS")
					  
					  
#	parser.add_option("-p", "--pwd", dest="password", metavar="PASSWORD",
#					  help="password for user to access Domino DTS")
#
#					  
#	parser.add_option("--opendays", dest="open_days_report", metavar="FILE",
#					  help="get number of days bug is open and"\
#					  						" write output to file")
#
#	parser.add_option("--clarify", dest="clarify_report", metavar="FILE",
#					  help="get number of days each bug has been" \
#					  			"open and write output to file")
#					  
#	parser.add_option("--opengraph", dest="opengraph_report", metavar="FILE",
#					  help="write a table that can be used to graph " \
#					  			"the historical open/closed bug graph")
	return parser

		
#====================================================================
if __name__ == '__main__':
	import sys
	import PyDlgCheckerWrapper
	
	PyDlgCheckerWrapper.InitializeModules(".")


	optParser = PopulateCommandLineParser()
	options, args = optParser.parse_args()
	
	for arg in sys.argv:
		if arg.lower().lstrip("/-") in ("?", "h", "help"):
			optParser.print_help()
			sys.exit()
	
	
	
	if not (options.windowTitle or options.xmlFileName):
		if args:
			arg = args[0]
			if arg.lower().endswith(".xml"):
				options.xmlFileName = arg
			else:
				options.windowTitle  = arg
		else:

			optParser.print_help()

			print 
			print "*ERROR* Please specify either Window title or XML FileName"
			sys.exit()

	if options.windowTitle and options.xmlFileName:
		optParser.print_help()
		
		print 
		print "*ERROR* Please specify only one of Window title or XML FileName"
		sys.exit()
		
	
	
	
	
	
	
	if options.windowTitle:
		# find the dialog
		handle =  find_windows(title_re = "^" + options.windowTitle.decode("mbcs"))[0]
		
		if not handle:
			print "Could not find dialog"
			sys.exit()
		
		
		PyDlgCheckerWrapper.InitDialogFromWindow(handle)
		
		outputXML = PyDlgCheckerWrapper.TestInfo['Controls'][0].Text
		outputXML = outputXML.replace("\\", '_')
		outputXML = outputXML.replace("*", '_')
		outputXML = outputXML.replace("?", '_')
		outputXML = outputXML.replace(">", '_')
		outputXML = outputXML.replace("<", '_')
		outputXML = outputXML.replace("/", '_')
		outputXML = outputXML.replace("|", '_')
		outputXML = outputXML.replace("\"", '_')
		outputXML = outputXML.replace(":", '_')
		

	
	elif options.xmlFileName:
	
	
		PyDlgCheckerWrapper.InitDialogFromFile(options.xmlFileName)
		
		outputXML = options.xmlFileName

	print outputXML

	# write out the XML file
	PyDlgCheckerWrapper.WriteDialogToFile (outputXML + ".xml")


	if options.refWindow:
		handle =  find_windows (title_re = "^" + options.refWindow)
		PyDlgCheckerWrapper.AddReferenceFromWindow(handle)
			
	elif options.refXML:
		PyDlgCheckerWrapper.AddReferenceFromFile(options.refXML)
		




	
	
	
	for i in range(0, PyDlgCheckerWrapper.GetRegisteredTestCount()):
		tst = PyDlgCheckerWrapper.GetRegisteredTestName(i)
		if tst not in ("AllControls", "AsianHotkey", "Overlapping"):
			print `tst`
			PyDlgCheckerWrapper.AddTest(tst)
			#print tst
		
	PyDlgCheckerWrapper.RunTests(True)

		
		
	for (ctrls, info, bType, inRef) in  PyDlgCheckerWrapper.TestInfo['Bugs']:
		print "BugType:", bType,

		for i in info:
			print i, info[i],
		print
		
		
		for i, ctrl in enumerate(ctrls):
			print '\t"%s" "%s" (%d %d %d %d) Vis: %d'% (
				ctrl.Text, 
				ctrl.FriendlyClassName,
				ctrl.Rectangle.left,
				ctrl.Rectangle.top,
				ctrl.Rectangle.right,
				ctrl.Rectangle.bottom,
				ctrl.IsVisible,)
				
			try:
				
				#print PyDlgCheckerWrapper
				#print PyDlgCheckerWrapper.TestInfo
				dlgRect = handleprops.rectangle(PyDlgCheckerWrapper.TestInfo['Controls'][0].handle)
				
			
				DrawOutline(ctrl.Rectangle + dlgRect, "red")
			except AttributeError, e:
				print e
				pass
				
		print
	

	



	
	




	