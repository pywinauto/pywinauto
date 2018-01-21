# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Missalignment Test

**What is checked**
This test checks that if a set of controls were aligned on a particular axis
in the reference dialog  that they are all aligned on the same axis.

**How is it checked**
A list of all the reference controls that are aligned is created (ie more than
one control with the same Top, Left, Bottom or Right coordinates). These
controls are then analysed in the localised dialog to make sure that they are
all aligned on the same axis.

**When is a bug reported**
A bug is reported when any of the controls that were aligned in the reference
dialog are no longer aligned in the localised control.

**Bug Extra Information**
The bug contains the following extra information
Name	Description
AlignmentType	This is either LEFT, TOP, RIGHT or BOTTOM. It tells you how
the controls were aligned in the reference dialog. String
AlignmentRect	Gives the smallest rectangle that surrounds ALL the controls
concerned in the bug, rectangle

**Is Reference dialog needed**
This test cannot be performed without the reference control. It is required
to see which controls should be aligned.

**False positive bug reports**
It is quite possible that this test reports false positives:
1.	Where the controls only just happen to be aligned in the reference dialog
(by coincidence)
2.	Where the control does not have a clear boundary (for example static
labels or checkboxes)  they may be miss-aligned but it is not noticeable that
they are not.


**Test Identifier**
The identifier for this test/bug is "Missalignment" """

testname = "Missalignment"

from pywinauto import win32structures

#====================================================================
def MissalignmentTest(windows):
    """Run the test on the windows passed in"""
    refAlignments = {}

    #find the controls alligned along each axis
    for win in windows:
        if not win.ref:
            continue


        for side in ("top", "left", "right", "bottom"):
            sideValue = getattr(win.ref.rectangle(), side)

            # make sure that the side dictionary has been created
            sideAlignments = refAlignments.setdefault(side, {})

            # make sure that the array of controls for this
            # alignment line has been created and add the current window
            sideAlignments.setdefault(sideValue, []).append(win)

    bugs = []
    for side in refAlignments:
        for alignment in refAlignments[side]:
            controls = refAlignments[side][alignment]
            sides = [getattr(ctrl.rectangle(), side) for ctrl in controls]
            sides = set(sides)

            if len(sides) > 1:

                overAllRect = win32structures.RECT()
                overAllRect.left = min(
                    [ctrl.rectangle().left for ctrl in controls])
                overAllRect.top = min(
                    [ctrl.rectangle().top for ctrl in controls])
                overAllRect.right = max(
                    [ctrl.rectangle().right for ctrl in controls])
                overAllRect.bottom = max(
                    [ctrl.rectangle().bottom for ctrl in controls])


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

