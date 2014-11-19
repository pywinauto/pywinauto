# -*- coding: UTF-8 -*-
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

from pywinauto import application

from pywinauto import tests


def SakuraTest():

	app = application.Application()
	app.start_(ur"\Program Files\sakura\sakura.exe")
	
	mainwin = app[u'無題sakura']

	# menu's from this application are not recovered well
	# but even with Japanese Regional settings they are not
	# rendered correctly by windows!
	# so using keys to select a menu item

	# open some dialog
	mainwin.TypeKeys("%OC")

	dlg = app[u'共通設定']

	app[u'共通設定'][u"フリーカーソル"].Click()

	dlg.MSDOS.Click()
	
	dlg.Cancel.Click()

	# quit the application
	mainwin.TypeKeys("%FX")
		

	
def Main():
	start = time.time()
	
	SakuraTest()	
	
	print "Total time taken:", time.time() - start

if __name__ == "__main__":
	Main()