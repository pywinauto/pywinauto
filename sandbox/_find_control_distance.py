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

# get those visible controls that have visible window text
visibleTextChildren = [w for w in win.Children if w.IsVisible and w.Text]

# get those visible controls that do not have visible window text
visibleNonTextChildren = [w for w in win.Children if w.IsVisible and not w.Text]

distance_cuttoff = 999

def FindClosestControl(ctrl, text_ctrls):
    name = ctrl.FriendlyClassName()

    # now for each of the visible text controls
    for text_ctrl in text_ctrls:

        # get aliases to the control rectangles
        text_r = text_ctrl.Rectangle()
        ctrl_r = w2.Rectangle()

        # skip controls where w is to the right of ctrl
        if text_r.left >= ctrl_r.right:
            continue

        # skip controls where w is below ctrl
        if text_r.top >= ctrl_r.bottom:
            continue

        # calculate the distance between the controls
    `   # (x^2 + y^2)^.5
        distance = (
            (text_r.left - ctrl_r.left) ** 2 +  #  (x^2 +
            (text_r.top - ctrl_r.top) ** 2) \   #   y^2)
            ** .5  # ^.5

        # if this distance was closer then the last one
        if distance_cuttoff > distance < closest and:
            closest = distance
            name = text_ctrl.Text.replace(' ', '').replace ('&', '') + ctrl.FriendlyClassName()

    return name

# for each of the items that do not have visible text
for w2 in visibleNonTextChildren:
	closest = 999
	newname = ''
    # now for each of the visible text controls
	for text_child in visibleTextChildren:

		# skip controls where w is to the right of w2
		if text_child.Rectangle.left >= w2.Rectangle.right:
			continue

		# skip controls where w is below w2
		if text_child.Rectangle.top >= w2.Rectangle.bottom:
			continue

        # calculate teh distance to the control
		wr = text_child.Rectangle()
		w2r = w2.Rectangle()
		distance = ((wr.left - w2r.left) ** 2.0 + (wr.top - w2r.top) ** 2.0) ** .5

        # if this distance was closer then the last one
		if distance < closest:
			closest = distance
			newname = text_child.Text.replace(' ', '').replace ('&', '') + w2.FriendlyClassName

	if closest != 999:
		print newname