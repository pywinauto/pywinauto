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

testname = "Missalignment"

from pywinauto.win32structures import RECT

#====================================================================
def MissalignmentTest(windows):

	refAlignments = {}

	#find the controls alligned along each axis
	for win in windows:
		if not win.ref:
			continue
	

		for side in ("top", "left", "right", "bottom"):
			sideValue = getattr(win.ref.Rectangle, side)
			
			# make sure that the side dictionary has been created
			sideAlignments = refAlignments.setdefault(side, {})
			
			# make sure that the array of controls for this
			# alignment line has been created and add the current window
			sideAlignments.setdefault(sideValue, []).append(win)
			
	bugs = []
	for side in refAlignments:
		for alignment in refAlignments[side]:
			controls = refAlignments[side][alignment]
			sides = [getattr(c.Rectangle, side) for c in controls]
			sides = set(sides)			
			
			if len(sides) > 1:

				overAllRect = RECT()
				overAllRect.left = min([c.Rectangle.left for c in controls])
				overAllRect.top = min([c.Rectangle.top for c in controls])
				overAllRect.right = max([c.Rectangle.right for c in controls])
				overAllRect.bottom = max([c.Rectangle.bottom for c in controls])

			
				bugs.append((
					controls, 
					{
						"AlignmentType": side.upper(),
						"AlignmentRect": overAllRect
					}, 
					testname, 
					0)
				)
				
	return bugs

