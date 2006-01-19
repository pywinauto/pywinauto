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
"test for overlapping controls"

testname = "Overlapping"
__revision__ = "$Revision$"

import pywinauto.win32structures

#====================================================================
def OverlappingTest(windows):
	"Return the repeated hotkey errors"

	bugs = []
	
	for i, first in enumerate(windows[:-1]):
		for second in windows[i+1:]:
		
			# if the reference controls are available
			if first.ref and second.ref:	
				
				if first.ref.Rectangle == second.ref.Rectangle and \
					not first.Rectangle == second.Rectangle:
					
					bugs.append(([first, second], {}, "NotExactOverlap", 0))

				elif ContainedInOther(first.ref.Rectangle, second.ref.Rectangle) and \
					not ContainedInOther(first.Rectangle, second.Rectangle):

					bugs.append(([first, second], {}, "NotContainedOverlap", 0))

				
			if Overlapped(first.Rectangle, second.Rectangle) and \
				not ContainedInOther(first.Rectangle, second.Rectangle) and \
				not first.Rectangle == second.Rectangle:

				ovlRect = OverlapRect(first.Rectangle, second.Rectangle)

				isInRef = -1
				if first.ref and second.ref:
					isInRef = 0
					if Overlapped(first.ref.Rectangle, second.ref.Rectangle):
						isInRef = 1

				bugs.append((
					[first, second], 
					{"OverlappedRect":ovlRect}, 
					testname, 
					isInRef))
			
	return bugs
				


#====================================================================
def ContainedInOther(rect1, rect2):
	# check if rect2 is inside rect1

	if rect1.left   >= rect2.left and \
		rect1.top    >= rect2.top and \
		rect1.right  <= rect2.right and \
		rect1.bottom <= rect2.bottom:
		return True
		
	# check if rect1 is inside rect2
	elif rect2.left  >= rect1.left and \
		rect2.top    >= rect1.top and \
		rect2.right  <= rect1.right and \
		rect2.bottom <= rect1.bottom:
		return True
	
	# no previous return - so must not be included
	return False


def Overlapped(rect1, rect2):
	ovlRect = OverlapRect(rect1, rect2)
	
	# if it is actually a bug
	if ovlRect.left < ovlRect.right and ovlRect.top < ovlRect.bottom:
		# make sure that the rectangle is the 'right way around :-)'
		return True
	return False
	
			
# Case 1: L2 between L1 and R1 -> max(L1, L2) < min(R1, R2)
#
# L1            R1
# ---------------
#        L2          R2
#        --------------
#
# Case 2: R2 outside L1 and R1 -> NOT max(L1, L2) < min(R1, R2)
#
#               L1          R1
#               -------------
# L2        R2
# ------------
#
def OverlapRect (rect1, rect2):
	"check whether the 2 rectangles are actually overlapped"	

	ovlRect = win32structures.RECT()

	ovlRect.left   = max(rect1.left,   rect2.left)
	ovlRect.right  = min(rect1.right,  rect2.right)	
	ovlRect.top    = max(rect1.top,    rect2.top)
	ovlRect.bottom = min(rect1.bottom, rect2.bottom)
	
	return ovlRect

