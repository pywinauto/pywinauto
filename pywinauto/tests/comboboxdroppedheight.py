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

testname = "ComboBoxDroppedHeight"

def ComboBoxDroppedHeightTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
	
		if win.Class != "ComboBox" or win.ref.Class != "ComboBox":
			continue

		if win.DroppedRect.height() != win.ref.DroppedRect.height():
		
			bugs.append((
				[win, ],
				{},
				testname,
				0,)
			)

	return bugs

