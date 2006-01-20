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

"""Different Leading and Trailing Spaces Test
What is checked
Checks that the same space characters (<space>, <tab>, <enter>, <vertical tab>)
are before and after all non space characters in the title of the control when
compared to the reference control.

How is it checked
Find the 1st non-space character, and the characters of the title up to that
are the leading spaces.
Find the last non-space character, and the characters of the title after that
are the trailing spaces.
These are then compared to the lead and trail spaces from the reference
control and if they are not exactly the then a bug is reported.

When is a bug reported
When either the leading or trailing spaces of the control being tested does
not match the equivalent spaces of the reference control exactly.

Bug Extra Information
The bug contains the following extra information
Name	Description
Lead-Trail	Whether this bug report is for the leading or trailing spaces of
the control, String
This will be either:
    "Leading"  bug relating to leading spaces
    "Trailing"  bug relating to trailing spaces
Ref	The reference leading or trailing (depending on Lead-Trail value) spaces,
String
Loc	The localised leading or trailing (depending on Lead-Trail value) spaces,
String

Is Reference dialog needed
This test will not run if the reference controls are not available.

False positive bug reports
This is usually not a very important test, so if it generates many false
positives then we should consider removing it.

Test Identifier
The identifier for this test/bug is "LeadTrailSpaces"
"""
__revision__ = "$Revision$"


testname = "LeadTrailSpaces"
def LeadTrailSpacesTest(windows):
    "Return the leading/trailing space bugs for the windows"
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        locLeadSpaces = GetLeadSpaces(win.Text)
        locTrailSpaces = GetTrailSpaces(win.Text)

        refLeadSpaces = GetLeadSpaces(win.ref.Text)
        refTrailSpaces = GetTrailSpaces(win.ref.Text)

        diffs = []
        if locLeadSpaces != refLeadSpaces:
            diffs.append(("Leading", locLeadSpaces, locTrailSpaces))

        if locTrailSpaces != refTrailSpaces:
            diffs.append(("Trailing", locTrailSpaces, refTrailSpaces))

        for diff, loc, ref in diffs:
            bugs.append((
                [win, ],
                {
                    "Lead-Trail": diff,
                    "Ref": ref,
                    "Loc": loc,
                },
                testname,
                0,)
            )
    return bugs


def GetLeadSpaces(title):
    "Return the leading spaces of the string"
    spaces = ''

    for i in range(0, len(title)):
        if not title[i].isspace():
            break

        spaces += title[i]

    return spaces


def GetTrailSpaces(title):
    "Return the trailing spaces of the string"
    rev = "".join(reversed(title))
    spaces = GetLeadSpaces(rev)
    return "".join(reversed(spaces))


LeadTrailSpacesTest.TestsMenus = True
