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

from application import FindWindows
win = FindWindows(title = "Replace", class_name = "#32770")[0]

from findbestmatch import find_best_match


visibleTextChildren = [w for w in win.Children if w.IsVisible and w.Text]

visibleNonTextChildren = [w for w in win.Children if w.IsVisible and not w.Text]

for w2 in visibleNonTextChildren:
	closest = 999
	newname = ''
	for text_child in visibleTextChildren:
	
		# skip controls where w is to the right of w2
		if text_child.Rectangle.left >= w2.Rectangle.right:
			continue
		
		# skip controls where w is below w2
		if text_child.Rectangle.top >= w2.Rectangle.bottom:
			continue
		
		wr = text_child.Rectangle
		w2r = w2.Rectangle
		distance = ((wr.left - w2r.left) ** 2.0 + (wr.top - w2r.top) ** 2.0) ** .5
		

		if distance < closest:
			closest = distance
			newname = text_child.Text.replace(' ', '').replace ('&', '') + w2.FriendlyClassName
	
	if closest != 999:
		print newname