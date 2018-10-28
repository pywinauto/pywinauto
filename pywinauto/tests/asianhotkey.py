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

testname = "AsianHotkeyFormat"

import re
from .repeatedhotkey import ImplementsHotkey, GetHotkey


#-----------------------------------------------------------------------------
def AsianHotkeyTest(windows):
    """Return the repeated hotkey errors"""
    bugs = []

    for win in windows:
        # skip it if it doesn't implement hotkey functionality
        if not ImplementsHotkey(win):
            continue

        if _IsAsianHotkeyFormatIncorrect(win.window_text()):

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
    """Check if the format of the hotkey is correct or not"""
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
