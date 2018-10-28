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
OverlappedRect  <What this info is>, rectangle

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

#====================================================================
def OverlappingTest(windows):
    """Return the repeated hotkey errors"""
    bugs = []

    for i, first in enumerate(windows[:-1]):
        first_rect = first.rectangle()

        if first.ref:
            first_ref_rect = first.ref.rectangle()

        for second in windows[i+1:]:
            second_rect = second.rectangle()


            # if the reference controls are available
            if first.ref and second.ref:
                second_ref_rect = second.ref.rectangle()

                if first_ref_rect == second_ref_rect and \
                    not first_rect == second_rect:

                    bugs.append(([first, second], {}, "NotExactOverlap", 0))

                elif _ContainedInOther(first_ref_rect,second_ref_rect) and \
                    not _ContainedInOther(first_rect, second_rect):

                    bugs.append(
                        ([first, second], {}, "NotContainedOverlap", 0))


            if _Overlapped(first_rect, second_rect) and \
                not _ContainedInOther(first_rect, second_rect) and \
                not first_rect == second_rect:

                ovlRect = _OverlapRect(first_rect, second_rect)

                isInRef = -1
                if first.ref and second.ref:
                    isInRef = 0
                    if _Overlapped(first_ref_rect, second_ref_rect):
                        isInRef = 1

                bugs.append((
                    [first, second],
                    {"OverlappedRect":ovlRect},
                    testname,
                    isInRef))

    return bugs



#====================================================================
def _ContainedInOther(rect1, rect2):
    """Return true if one rectangle completely contains the other"""
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
    """Return true if the two rectangles are overlapped"""
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

class OptRect(object): pass

def _OverlapRect (rect1, rect2):
    """check whether the 2 rectangles are actually overlapped"""
    ovlRect = OptRect()

    ovlRect.left   = max(rect1.left,   rect2.left)
    ovlRect.right  = min(rect1.right,  rect2.right)
    ovlRect.top    = max(rect1.top,    rect2.top)
    ovlRect.bottom = min(rect1.bottom, rect2.bottom)

    return ovlRect

