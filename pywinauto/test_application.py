import os

import application


def TestNotepad():
	
	if 1:

		# ensure that the XML path exists
		example_path = r"examples\notepad_test"
		try:
			os.makedirs(example_path)
		except OSError:
			pass

		# test that trying to _connect to a non existent app fails
		try:
			app = application.Application()
			app._connect(path = ur"No process with this please")
			assert 0
		except application.ProcessNotFoundError:
			pass

		# test that trying to _connect to a non existent app fails
		try:
			app = application.Application()
			app._start(cmd_line = ur"No process with this please")
			assert 0
		except application.AppStartError:
			pass

		# try when it isn't connected
		try:
			app = application.Application()
			#app._start(ur"c:\windows\system32\notepad.exe")
			app.Notepad.Click()
			assert 0
		except application.AppNotConnected:
			pass


		app = application.Application()

		try:
			app._connect(path = ur"c:\windows\system32\notepad.exe")
		except application.ProcessNotFoundError:	
			app._start(ur"c:\windows\system32\notepad.exe")

		app.Notepad.MenuSelect("File->PageSetup")

		app.PageSetupDlg.ComboBox1.Select(4)
				
		app.PageSetupDlg.Printer.Click()		
		
		TestingCheckBox = 1
		if TestingCheckBox:
			# Open the Connect to printer dialog so we can 
			# try out checking/unchecking a checkbox
			app.PageSetupDlg.Network.Click()

			app.ConnectToPrinter.ExpandByDefault.Check()

			app.ConnectToPrinter.ExpandByDefault.UnCheck()


			# try doing the same by using click
			app.ConnectToPrinter.ExpandByDefault.Click()

			app.ConnectToPrinter.ExpandByDefault.Click()

			# close the dialog
			app.ConnectToPrinter.Cancel.Click()


		
		app.PageSetupDlg2.Properties.Click()

		docProps = app._window(title_re = ".*Document Properties")

		TestingTabSelect = 1
		if TestingTabSelect:
			docProps.TabCtrl.Select(0)

			docProps.TabCtrl.Select(1)

			docProps.TabCtrl.Select(2)


			docProps.TabCtrl.Select("PaperQuality")

			docProps.TabCtrl.Select("JobRetention")

			docProps.TabCtrl.Select("Layout")


		TestingRadioButton = 1
		if TestingRadioButton:
			docProps.RotatedLandscape.Click()

			docProps.BackToFront.Click()

			docProps.FlipOnShortEdge.Click()
			

			docProps.Portrait.Click()

			docProps._None.Click()

			docProps.FrontToBack.Click()

		

		#print docProps._ctrl
		advbutton = docProps.Advanced
		advbutton.Click()

		# close the 4 windows
		app._window(title_re = ".* Advanced Options").Ok.Click()

		docProps.Cancel.Click()

		app.PageSetupDlg2.OK.Click()

		app.PageSetupDlg.Ok.Click()
		
		# type some text
		app.Notepad.Edit.SetText("I am typing some text to Notepad\r\n\r\nAnd then I am going to quit")

		# exit notepad
		app.Notepad.MenuSelect("File->Exit")
		app.Notepad.No.Click()
	
	


def TestPaint():

		app = application.Application()

		try:
			app._connect(path = ur"c:\windows\system32\mspaint.exe")
		except application.ProcessNotFoundError:	
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
	TestNotepad()
	TestPaint()
