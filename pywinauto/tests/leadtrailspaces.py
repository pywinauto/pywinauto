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

"""Different Leading and Trailing Spaces Test

**What is checked**
Checks that the same space characters (<space>, <tab>, <enter>, <vertical tab>)
are before and after all non space characters in the title of the control when
compared to the reference control.

**How is it checked**
Find the 1st non-space character, and the characters of the title up to that
are the leading spaces.
Find the last non-space character, and the characters of the title after that
are the trailing spaces.
These are then compared to the lead and trail spaces from the reference
control and if they are not exactly the then a bug is reported.

**When is a bug reported**
When either the leading or trailing spaces of the control being tested does
not match the equivalent spaces of the reference control exactly.

**Bug Extra Information**
The bug contains the following extra information

  * **Lead-Trail**  Whether this bug report is for the leading or
    trailing spaces of the control, String

    This will be either:

      - "Leading"  bug relating to leading spaces
      - "Trailing"  bug relating to trailing spaces

  * **Ref**  The leading or trailings spaces of the reference string
    (depending on Lead-Trail value), String
  * **Loc**  The leading or trailings spaces of the local string (depending on
    Lead-Trail value), String

**Is Reference dialog needed**
This test will not run if the reference controls are not available.

**False positive bug reports**
This is usually not a very important test, so if it generates many false
positives then we should consider removing it.

**Test Identifier**
The identifier for this test/bug is "LeadTrailSpaces"
"""

testname = "LeadTrailSpaces"

def LeadTrailSpacesTest(windows):
    """Return the leading/trailing space bugs for the windows"""
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        locLeadSpaces = GetLeadSpaces(win.window_text())
        locTrailSpaces = GetTrailSpaces(win.window_text())

        refLeadSpaces = GetLeadSpaces(win.ref.window_text())
        refTrailSpaces = GetTrailSpaces(win.ref.window_text())

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
    """Return the leading spaces of the string"""
    spaces = ''

    for i in range(0, len(title)):
        if not title[i].isspace():
            break

        spaces += title[i]

    return spaces


def GetTrailSpaces(title):
    """Return the trailing spaces of the string"""
    rev = "".join(reversed(title))
    spaces = GetLeadSpaces(rev)
    return "".join(reversed(spaces))


LeadTrailSpacesTest.TestsMenus = True
