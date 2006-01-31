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
"""Overlapping Test

**What is checked**
The overlapping test checks for controls that occupy the same space as some
other control in the dialog.

  + If the reference controls are available check for each pair of controls:

    - If controls are exactly the same size and position in reference then
      make sure that they are also in the localised.
    - If a reference control is wholly contained in another make sure that the
      same happens for the controls being tested.

  + If the reference controls are not available only the following check can
    be done

    - If controls are overlapped in localised report a bug (if reference is
      available it is used just to say if this overlapping happens in reference
      also)


**How is it checked**
Various tests are performed on each pair of controls to see if any of the
above conditions are met. The most specific tests that can be performed are
done 1st so that the bugs reported are as specific as possible. I.e. we report
that 2 controls are not exactly overlapped when they should be rather than jut
reporting that they are overlapped which contains less information.

**When is a bug reported**
A bug is reported when:

    - controls are overlapped (but not contained wholly, and not exactly
      overlapped)
    - reference controls are exactly overlapped but they are not in tested
      dialog
    - one reference control is wholly contained in another but not in
      tested dialog


**Bug Extra Information**
This test produces 3 different types of bug:
BugType: "Overlapping"
Name    Description
OverlappedRect  <What this info is>, Rectangle

**BugType -  "NotContainedOverlap"**
There is no extra information associated with this bug type

**BugType - "NotExactOverlap"**
There is no extra information associated with this bug type

**Is Reference dialog needed**
For checking whether controls should be exactly overlapped and whether they
should be wholly contained the reference controls are necessary. If the
reference controls are not available then only simple overlapping of controls
will be checked.

**False positive bug reports**
If there are controls in the dialog that are not visible or are moved
dynamically it may cause bugs to be reported that do not need to be logged.
If necessary filter out bugs with hidden controls.

**Test Identifier**
The identifier for this test is "Overlapping"
"""

testname = "Overlapping"
__revision__ = "$Revision$"

from pywinauto import win32structures

#====================================================================
def OverlappingTest(windows):
    "Return the repeated hotkey errors"

    bugs = []

    for i, first in enumerate(windows[:-1]):
        for second in windows[i+1:]:

            # if the reference controls are available
            if first.ref and second.ref:

                if first.ref.Rectangle() == second.ref.Rectangle() and \
                    not first.Rectangle() == second.Rectangle():

                    bugs.append(([first, second], {}, "NotExactOverlap", 0))

                elif _ContainedInOther(first.ref.Rectangle(),
                    second.ref.Rectangle()) and \
                    not _ContainedInOther(first.Rectangle(), second.Rectangle()):

                    bugs.append(
                        ([first, second], {}, "NotContainedOverlap", 0))


            if _Overlapped(first.Rectangle(), second.Rectangle()) and \
                not _ContainedInOther(first.Rectangle(), second.Rectangle()) and \
                not first.Rectangle() == second.Rectangle():

                ovlRect = _OverlapRect(first.Rectangle(), second.Rectangle())

                isInRef = -1
                if first.ref and second.ref:
                    isInRef = 0
                    if _Overlapped(first.ref.Rectangle(), second.ref.Rectangle()):
                        isInRef = 1

                bugs.append((
                    [first, second],
                    {"OverlappedRect":ovlRect},
                    testname,
                    isInRef))

    return bugs



#====================================================================
def _ContainedInOther(rect1, rect2):
    "Return true if one rectangle completely contains the other"
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


def _Overlapped(rect1, rect2):
    "Return true if the two rectangles are overlapped"
    ovlRect = _OverlapRect(rect1, rect2)

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
def _OverlapRect (rect1, rect2):
    "check whether the 2 rectangles are actually overlapped"

    ovlRect = win32structures.RECT()

    ovlRect.left   = max(rect1.left,   rect2.left)
    ovlRect.right  = min(rect1.right,  rect2.right)
    ovlRect.top    = max(rect1.top,    rect2.top)
    ovlRect.bottom = min(rect1.bottom, rect2.bottom)

    return ovlRect

