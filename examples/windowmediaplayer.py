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

#import os
import time

import application

import tests



def WindowsMedia():
	
	app = application.Application()

	app._connect(path = ur"C:\Program Files\Windows Media Player\wmplayer.exe")
	
	app.WindowsMediaPlayer.MenuSelect("View->Choose Columns")
	
	for ctrl in app.ChoolseColumns.Children:
		print ctrl.Class
	
	app.ChooseColumns.ListView.Check(1)
	time.sleep(.5)
	app.ChooseColumns.ListView.UnCheck(1)
	time.sleep(.5)
	app.ChooseColumns.ListView.Check(1)
	time.sleep(.5)
	
	app.ChooseColumsn.Cancel.Click()
	

def Mozilla_ListBox():
	app = application.Application()

	app._connect(title = ur"Select Components")
	
	lb = app.SelectComponents.ListBox
	#print "sdfds", app.SelectComponents.ListBox.IsChecked(0)
	#print "sdfds", app.SelectComponents.ListBox.IsChecked(1)
	
	import ctypes
	print 'xxx', ctypes.windll.user32.GetListBoxInfo(lb)
	#itemd = lb.SendMessage(win32defines.LB_GETITEMDATA, 1)
	#print itemd
	
	for i in range(lb.ItemCount()):
		print i
		time.sleep(.2)
		lb.SetFocus(i)
		lb.TypeKeys("{SPACE}") #{DOWN}
	
	
	#time.sleep(.5)
	#app.SelectComponents.ListBox.UnCheck(0)
	#time.sleep(.5)
	#app.SelectComponents.ListBox.UnCheck(1)
	#time.sleep(.5)

def Textpad_ListBox():
	app = application.Application()

	app._connect(title = ur"Preferences")
	
	
	lb = app.Preferences.ListBox0
	
	import ctypes
	print 'xxx', ctypes.windll.user32.GetListBoxInfo(lb)
	
	print lb.ItemCount()
	
	for i in range(lb.ItemCount()):
		time.sleep(.1)
		lb.SetFocus(i)



def Main():
	start = time.time()
	
	from findwindows import find_window
	win = find_window(title = "Tabs")
	
	dlg = application.ActionDialog(win)
	
	print dlg.ComboBox.Class
	print "count", dlg.ComboBox.ItemCount()
	print "idata", dlg.ComboBox.ItemData(0)
	print "selected", dlg.ComboBox.SelectedIndex()
	
	
	
	
	
	#WindowsMedia()
	
	#Mozilla_ListBox()
	#Textpad_ListBox()
	
	print "Total time taken:", time.time() - start

if __name__ == "__main__":
	Main()