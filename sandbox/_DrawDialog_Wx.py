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

import PyDlgCheckerWrapper

import sys
if len(sys.argv) < 2 :
	print "Please specify the XML file to read"
	sys.exit()


## Create a new frame class, derived from the wxPython Frame.
class MyFrame(wxFrame):

	def __init__(self, parent, id, title):
		# First, call the base class' __init__ method to create the frame


		PyDlgCheckerWrapper.InitDialogFromFile(sys.argv[1])
		dlg = PyDlgCheckerWrapper.TestInfo['Dialog']

		wxFrame.__init__(self, 
			parent, 
			id, 
			dlg.Title,
			wxPoint(100, 100), 
			wxSize(dlg.Rectangle.right, dlg.Rectangle.bottom))

		# Add a panel and some controls to display the size and position
		panel = wxPanel(self, -1)


		classes = {
			"Static": wxStaticText,
			"Button": wxButton,
			"CheckBox": wxCheckBox,
			"RadioButton": wxRadioButton,
			"Dialog": None,
			"#32770": None,
			"SysTabControl32": None,

#			"GroupBox": None,
			"GroupBox": wxRadioBox,

#			"Static": wxStaticText,
#			"Static": wxStaticText,
#			"Static": wxStaticText,
			
			}
		for ctrl in dlg.AllControls()[1:]:
			wx_class_type = classes.get(ctrl.FriendlyClassName, wxStaticText)
			
			print ctrl.FriendlyClassName, wx_class_type
			
			if wx_class_type:
				width = ctrl.Rectangle.right - ctrl.Rectangle.left
				height = ctrl.Rectangle.bottom - ctrl.Rectangle.top

				if wx_class_type != wxRadioBox:
					wx_class_type (
						panel, 
						-1, 
						ctrl.Title,
						wxPoint(ctrl.Rectangle.left -3, ctrl.Rectangle.top - 23),
						wxSize(width, height)).Raise()
				else:
				
					wx_class_type (
						panel, 
						-1, 
						ctrl.Title,
						wxPoint(ctrl.Rectangle.left -3, ctrl.Rectangle.top - 23),
						wxSize(width, height),
						['']).Lower()
			


#		wxStaticText(panel, -1, "Size:",
#					 wxDLG_PNT(panel, wxPoint(4, 4)),  wxSize(30, 20))
#
#		wxStaticText(panel, -1, "Pos:",
#					 wxDLG_PNT(panel, wxPoint(4, 14)), wxDefaultSize)
#
#		self.sizeCtrl = wxTextCtrl(panel, -1, "",
#								   wxDLG_PNT(panel, wxPoint(24, 4)),
#								   wxDLG_SZE(panel, wxSize(36, -1)),
#								   wxTE_READONLY)
#		self.posCtrl = wxTextCtrl(panel, -1, "",
#								  wxDLG_PNT(panel, wxPoint(24, 14)),
#								  wxDLG_SZE(panel, wxSize(36, -1)),
#								  wxTE_READONLY)


	# This method is called automatically when the CLOSE event is
	# sent to this window
	def OnCloseWindow(self, event):
		# tell the window to kill itself
		self.Destroy()



# Every wxWindows application must have a class derived from wxApp
class MyApp(wxApp):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = MyFrame(NULL, -1, "This is a test")
        frame.Show(true)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return true


app = MyApp(0)     # Create an instance of the application class
app.MainLoop()     # Tell it to start processing events

