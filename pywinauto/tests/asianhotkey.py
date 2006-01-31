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

"""Asian Hotkey Format Test

**What is checked**

This test checks whether the format for shortcuts/hotkeys follows the
standards for localised Windows applications. This format is
{localised text}({uppercase hotkey})
so for example if the English control is
"&Help"
the localised control for Asian languages should be
"LocHelp(H)"

**How is it checked**

After checking whether this control displays hotkeys it examines the 1st
string of the control to make sure that the format is correct.
If the reference control is available then it also makes sure that the
hotkey character is the same as the reference.
Controls with a title of less than 4 characters are ignored. This has been
done to avoid false positive bug reports for strings like "&X:".

**When is a bug reported**

A bug is reported when a control has a hotkey and it is not in the correct
format.
Also if the reference control is available a bug will be reported if the
hotkey character is not the same as used in the reference

**Bug Extra Information**

This test produces 2 different types of bug:
BugType: "AsianHotkeyFormat"
There is no extra information associated with this bug type

**BugType: "AsianHotkeyDiffRef"**

There is no extra information associated with this bug type

**Is Reference dialog needed**

The reference dialog is not needed.
If it is unavailable then only bugs of type "AsianHotkeyFormat" will be
reported, bug of type "AsianHotkeyDiffRef" will not be found.

**False positive bug reports**

There should be very few false positive bug reports when testing Asian
software. If a string is very short (eg "&Y:") but is padded with spaces
then it will get reported.

**Test Identifier**

The identifier for this test/bug is "AsianHotkeyTests"
"""

__revision__ = "$Revision$"


testname = "AsianHotkeyFormat"


import re

from repeatedhotkey import ImplementsHotkey, GetHotkey


#-----------------------------------------------------------------------------
def AsianHotkeyTest(windows):
    "Return the repeated hotkey errors"

    bugs = []

    for win in windows:
        # skip it if it doesn't implement hotkey functionality
        if not ImplementsHotkey(win):
            continue

        if _IsAsianHotkeyFormatIncorrect(win.Text()):

            bugs.append((
                [win,],
                {},
                testname,
                0)
            )

    return bugs


_asianHotkeyRE = re.compile (r"""
    \(&.\)      # the hotkey
    (
        (\t.*)|     # tab, and then anything
        #(\\t.*)|   # escaped tab, and then anything
        (\(.*\)     # anything in brackets
    )|
    \s*|            # any whitespace
    :|              # colon
    (\.\.\.)|       # elipsis
    >|              # greater than sign
    <|              # less than sign
    (\n.*)          # newline, and then anything
    \s)*$""", re.VERBOSE)

#-----------------------------------------------------------------------------
def _IsAsianHotkeyFormatIncorrect(text):
    "Check if the format of the hotkey is correct or not"
    # get the hotkey
    pos, char = GetHotkey(text)

    # if it has a hotkey then check that it is correct Asian format
    if char:
        found = _asianHotkeyRE.search(text)
        if not found:
            return True


    return False


#	if (hotkeyPos - 2  >= 0 &&	// at least 4th character ".(&..."
#        // at most 2nd last character "...(&H)"
#		hotkeyPos + 1 <= title.length()-1 &&
#		title[hotkeyPos-2] == '(' &&
#		title[hotkeyPos+1] == ')' &&
#		hotkeyPos +1 == title.find_last_not_of("\n\t :")
#	   )
#	{
#		// OK So we know now that the format "..(&X).."
#       // is correct and that it is the
#		// last non space character in the title
#		; // SO NO BUG!


AsianHotkeyTest.TestsMenus = True
