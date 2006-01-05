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


def MiscValuesTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
		
		diffs = {}

		if win.Class != win.ref.Class:
			diffs["Class"] = (win.Class, win.ref.Class)

		
		if win.Style != win.ref.Style:
			diffs["Style"] = (win.Style, win.ref.Style())
			
		if win.ExStyle != win.ref.ExStyle:
			diffs["ExStyle"] = (win.ExStyle, win.ref.ExStyle)
		
		if win.ContextHelpID != win.ref.ContextHelpID:
			diffs["HelpID"] = (win.ContextHelpID, win.ref.ContextHelpID)
		
		if win.ControlID != win.ref.ControlID:
			diffs["ControlID"] = (win.ControlID, win.ref.ControlID)
			
		if win.IsVisible != win.ref.IsVisible:
			diffs["Visibility"] = (win.IsVisible, win.ref.IsVisible)
			
		if win.UserData != win.ref.UserData:
			diffs["UserData"] = (win.UserData, win.ref.UserData)
			
			
		for diff, vals in diffs.items():
			bugs.append((
				[win, ],
				{
					"ValueType": diff,
					"Ref": unicode(vals[1]),
					"Loc": unicode(vals[0]),
				},
				"MiscValues",
				0,)
			)
	return bugs

