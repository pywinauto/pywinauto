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

r"""Converts XML files captured by DLGChecks to a close aproximation 
of the original dialog

Usage:
	DrawDialogFromXML.py (XML filepaths or directories containing XML files)

e.g.
	DrawDialogFromXML.py jpn c:\temp PropertiesDialog.xml
	

You can specify more then one file or more than one directory
Wildcard characters are not currently handled (?*).

Note that there will be differences between dialogs drawn this way 
and the original dialog:
 - Anything drawn directly to the dialog will not be drawn (usually
   something done in the OnPaint handler of the dialog.
 - OwnerDrawn controls will not be handled 100% correctly,
   but as close as possible
 - Images, Bitmaps and Icons are currently not drawn
"""

import pywin.mfc.dialog
import XMLHelpers
import win32defines
import win32functions
import sys
import os
import os.path

from pprint import pprint

# ignore the warning in the pywin/mfc/dialog module line number 32
import warnings
warnings.filterwarnings("ignore", module = ".*dialog", lineno  = 32)

# some constants for fixing Dialog units
rectSizerX = .675 #.675
rectSizerY = .62 #.62
titleBarHeight = 10



# ===========================================================================
def Main():

	# check that the parameters are correct
	if len(sys.argv) < 2:
		print __doc__
		print "*** Please specify the language and the " \
				"XML files or folders with XML files to read"
		sys.exit()
		
	xmlFiles = []

	# get the full list of XML files to try
	for arg in sys.argv[1:]:
		# if the current argument is a directory

		if os.path.isdir(arg):

			# for all the files in this directory
			for root, dirs, files in os.walk(arg):
				for f in files:
					
					# if it is an XML file
					if os.path.splitext(f)[1].lower() == ".xml":
						# add it to our list
						xmlFiles.append(os.path.join(root, f))
						
		# if the argument is a file then just append it
		elif os.path.isfile(arg):
			xmlFiles.append(arg)


	for xmlFile in xmlFiles:
		print xmlFile
	
		try:
			# try and parse the XML file
			# could easily fail if structure of XML is not exactly what 
			# we are expecting - for example if it is an XML file not
			# containing Dialog Information or from a later version of
			# XML dialog
			ctrls = ParseXML(xmlFile)
			
			# convert the XML information into a dialog template understood by
			# Win32ui
			template = MakeOLDDlgTemplate(ctrls)

			#try:
			# construct the dialog
			dlg = XmlDialog(template)
			#except DeprecationWarning, e:
			#	pass
			
			# give the dialog the original control information
			dlg.DlgControls = ctrls

			
			# show the dialog
			ret =  dlg.DoModal()
			if  ret == -1:
				pass
			
			
			
		except (AttributeError, XMLHelpers.XMLParsingError):
			print "**Ignored** %s"% xmlFile


# ===========================================================================
def ParseXML(filename):
	"Parse the Old style XML file to a dictionary"

	ctrls = XMLHelpers.ReadPropertiesFromFile(filename)
	return ctrls

	


# ===========================================================================
def ScaleToDialogUnitsAndConvert(rect, isDialogControl = False):
	bottomOffset = 0
	if isDialogControl:
		bottomOffset = titleBarHeight
		
	
	left = int(rect.left * rectSizerX) # x
	top = int(rect.top * rectSizerY)  -titleBarHeight	# y
	right =int((rect.right - rect.left)* rectSizerX)	# cx
	bottom = int(((rect.bottom - rect.top) * rectSizerY) - bottomOffset)	# cy
	
	return (left, top, right, bottom)
	



# ===========================================================================
#  For Old XML files - converts from Dictionary to template
# ===========================================================================
def MakeOLDDlgTemplate(controls):
	template = []
	
	#pprint(controls)		
	for i, ctrl in enumerate(controls):	

		title =  ctrl['Texts'][0].encode('mbcs')

		# if it is the Dialog control
		if i == 0:
			
			# remove WS CHILD style if it exists
			style = ctrl["Style"] 
			if style & win32defines.WS_CHILD == win32defines.WS_CHILD:
				style =  style ^ win32defines.WS_CHILD
					
			# Start off the template with the dilaog information	
			template = [[
				str(title),
				ScaleToDialogUnitsAndConvert(ctrl["Rectangle"], True),
				style,
				int(ctrl["ExStyle"]),
				(8, ctrl["Fonts"][0].lfFaceName, )
				#(ctrl["Font").lfHeight, ctrl["Font").lfFaceName, )

				], ]

		#For each of the other controls
		else:
			
			# do not create ComboLBoxes and Edit controls that are just part of 
			# ComboBox controls - they will be created automatically by the ComboBox
			# control itself
			if ctrl["Class"] == "ComboLBox" and int(ctrl["ControlID"]) == 1000 or \
				ctrl["Class"] == "Edit" and int(ctrl["ControlID"]) == 1001:
				continue
	
			
			if not ctrl['IsVisible']:
				continue

	
			# remove the OwnderDraw style from ComboBoxes
			style = int(ctrl["Style"])
			if ctrl["Class"] == "ComboBox" and style & 0x10:
				style = style ^ 0x10

			# change controls we don't know how to deal with by
			# converting them to a static and changing the title to contain
			# the old class name
			if ctrl["Class"] not in (
				"#32770", 
				"Button",
				"ComboBox", 
				"ComboLBox", 
				"Edit", 
				"ListBox", 
				"ScrollBar", 
				"Static", 

				"ComboBoxEx32",
				"msctls_statusbar32", 
				"msctls_updown32", 
				"SysHeader32", 
				"SysListView32", 
				"SysTabControl32", 
				"SysTreeView32", 
				"ToolbarWindow32", 
				#"SSDemoParent",
				#"GraphCtl", 		# test
				#"CHECKLIST_ACLUI",	# test
				#"rctrl_renwnd32", 
				#"RichEdit20W", 
				):
				
				title = u"Was previously: " + ctrl["Class"]
				ctrl["Class"] = "Static"
				#continue
			
			# don't  bother doing dialogs or Tab Controls
			if ctrl["Class"] in ("#32770", "SysTabControl32"):
				continue
			
			# ensure that for drop down combo boxes that the size of the drop down is enough to 
			# clearly see many items
			if ctrl["Class"] in ("ComboBox",) and \
				(ctrl['Style'] & win32defines.CBS_DROPDOWNLIST == win32defines.CBS_DROPDOWNLIST  or \
				ctrl['Style'] & win32defines.CBS_DROPDOWN == win32defines.CBS_DROPDOWN):
				#not ctrl['Style'] & win32defines.CBS_SIMPLE:#& win32defines.CBS_DROPDOWNLIST or ctrl['Style'] & win32defines.CBS_DROPDOWN):
				ctrl["Rectangle"].bottom += 200
			
			
			item = [
				str(ctrl["Class"]),
				str(title),
				int(ctrl["ControlID"]),
				ScaleToDialogUnitsAndConvert(ctrl["Rectangle"] - controls[0]['Rectangle']),
				style,
				int(ctrl["ExStyle"]),
			]
			
			# append the information needed for the template
			template.append(item)

	#pprint(template)

	return template







# ===========================================================================
class XmlDialog (pywin.mfc.dialog.Dialog):
	def OnInitDialog(self):

		# loop over all the controls in the original dialog
		for x in self.DlgControls:
		
			# if it is a combobox
			if x["Class"] == "ComboBox":
				
				try:
					# get the control
					ctrl = self.GetDlgItem(int(x['ControlID']))
				
					#ctrl.SetExtendedUI(1)
		
					# add each of the text items
					for subTitle in x["Texts"][1:]:
						ctrl.AddString(subTitle.encode('mbcs'))


#						win32functions.SendMessage(
#							ctrl.GetSafeHwnd(), 
#							win32defines.CB_ADDSTRING, 
#							0, 
#							subTitle )


				except:
					pass
				
			elif x["Class"] == "ListBox":
				try:
					ctrl = self.GetDlgItem(int(x['ControlID']))

					for subTitle in x["Texts"][1:]:
						win32functions.SendMessage(
							ctrl.GetSafeHwnd(), 
							win32defines.LB_ADDSTRING, 
							0, 
							subTitle.encode('mbcs') )
				except:
					pass
			
#			if x.has_key('Image'):
#				#print "hasImage"
#				ctrl = self.GetDlgItem(int(x['ControlID']))
#				bmp = x['Image']
#				
#				from PIL import ImageWin
#				dib = ImageWin.Dib(bmp)
#				
#				hDC = ctrl.GetDC()
#				#hDC.DrawText("Should have an image", (0, 0, 100, 199), 0)
#				#print dib
#				
#				dib.expose(hDC.GetHandleAttrib())
#				
#				#dib.draw(hDC.GetHandleOutput(), (0, 0, 990, 990))

	def OnPaint(self):
		# loop over all the controls in the original dialog
		for x in self.DlgControls:
			
			if x.has_key('Image'):
				
				try:
					ctrl = self.GetDlgItem(int(x['ControlID']))
				
					bmp = x['Image']

					from PIL import ImageWin
					dib = ImageWin.Dib(bmp)

					hdc, paint_struct = ctrl.BeginPaint()
					dib.expose(hdc.GetHandleAttrib())

					ctrl.EndPaint(paint_struct)
				except:
					pass
				
		#return True
			
			
#			dib = ImageWin.Dib (bmp)
#			scaled_size = tuple ([scale * i for i in bmp.size])
#			x = (printer_size[0] - scaled_size[0]) / 2
#			y = (printer_size[1] - scaled_size[1]) / 2
#			dib.draw (hDC.GetHandleOutput (), (x, y) + scaled_size)
					

# ===========================================================================
if __name__ == "__main__":
	Main()
	





	