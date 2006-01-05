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

import win32structures

def CompareToRefFontTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
		
		diffs = {}
		
		for f in win32structures.LOGFONTW._fields_:
			
			loc = getattr(win.Font, f[0])
			ref = getattr(win.ref.Font, f[0])
			if loc != ref:
				diffs.append(f[0], loc, ref)
			
		for diff, locVal, refVal in diffs.items():
			bugs.append((
				[win, ],
				{
					"ValueType": diff,
					"Ref": unicode(refVal),
					"Loc": unicode(locVal),
				},
				"CompareToRefFont",
				0,)
			)
	return bugs

