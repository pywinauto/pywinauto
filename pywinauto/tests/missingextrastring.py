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

testname = "MissingExtraString"

CharsToCheck = (
	">", 
	">>",
	"<", 
	"<<",
	"&",
	"&&",
	"...",
	":",
	"@",

)

#-----------------------------------------------------------------------------
def MissingExtraStringTest(windows):
	bugs = []
	for win in windows:
		if not win.ref:
			continue
	
		for char in CharsToCheck:
			missingExtra = ''
			
			if win.Text.count(char) > win.ref.Text.count(char):
				missingExtra = "ExtraCharacters"
			elif win.Text.count(char) < win.ref.Text.count(char):
				missingExtra = "MissingCharacters"
			
			if missingExtra:
				bugs.append((
					[win,],
					{
						"MissingOrExtra": missingExtra,
						"MissingOrExtraText": char 
					},
					testname,
					0))	
					
	return bugs


MissingExtraStringTest.TestsMenus = True
			
