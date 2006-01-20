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

"""Missalignment Test
What is checked
This test checks that if a set of controls were aligned on a particular axis
in the reference dialog  that they are all aligned on the same axis.

How is it checked
A list of all the reference controls that are aligned is created (ie more than
one control with the same Top, Left, Bottom or Right coordinates). These
controls are then analysed in the localised dialog to make sure that they are
all aligned on the same axis.

When is a bug reported
A bug is reported when any of the controls that were aligned in the reference
dialog are no longer aligned in the localised control.

Bug Extra Information
The bug contains the following extra information
Name	Description
AlignmentType	This is either LEFT, TOP, RIGHT or BOTTOM. It tells you how
the controls were aligned in the reference dialog. String
AlignmentRect	Gives the smallest rectangle that surrounds ALL the controls
concerned in the bug, Rectangle

Is Reference dialog needed
This test cannot be performed without the reference control. It is required
to see which controls should be aligned.

False positive bug reports
It is quite possible that this test reports false positives:
1.	Where the controls only just happen to be aligned in the reference dialog
(by coincidence)
2.	Where the control does not have a clear boundary (for example static
labels or checkboxes)  they may be miss-aligned but it is not noticeable that
they are not.


Test Identifier
The identifier for this test/bug is "Missalignment" """

__revision__ = "$Revision$"

testname = "Missalignment"

from pywinauto.win32structures import RECT

#====================================================================
def MissalignmentTest(windows):
    "Run the test on the windows passed in"
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
            sides = [getattr(ctrl.Rectangle, side) for ctrl in controls]
            sides = set(sides)

            if len(sides) > 1:

                overAllRect = RECT()
                overAllRect.left = min(
                    [ctrl.Rectangle.left for ctrl in controls])
                overAllRect.top = min(
                    [ctrl.Rectangle.top for ctrl in controls])
                overAllRect.right = max(
                    [ctrl.Rectangle.right for ctrl in controls])
                overAllRect.bottom = max(
                    [ctrl.Rectangle.bottom for ctrl in controls])


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

