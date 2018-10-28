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

"""Translation Test

**What is checked**
This checks for controls which appear not to be translated.

**How is it checked**
It compares the text of the localised and reference controls.

If there are more than string in the control then each item is searched for in
the US list of titles (so checking is not order dependent).
The indices for the untranslated strings are returned in a comma separated
string.
Also the untranslated strings themselves are returned (all as one string).
These strings are not escaped and are delimited as
"string1","string2",..."stringN".

**When is a bug reported**

 If the text of the localised control is identical to the reference control
 (in case, spacing i.e.  a binary compare) then it will be flagged as
 untranslated. Otherwise the control is treated as translated.

Note: This is the method to return the least number of bugs. If there are
differences in any part of the string (e.g. a path or variable name) but the
rest of the string is untranslated then a bug will not be highlighted

**Bug Extra Information**
The bug contains the following extra information
Name	Description
Strings		The list of the untranslated strings as explained above
StringIndices		The list of indices (0 based) that are untranslated.
This will usually be 0 but if there are many strings in the control
untranslated it will report ALL the strings e.g. 0,2,5,19,23

**Is Reference dialog needed**
The reference dialog is always necessary.

**False positive bug reports**
False positive bugs will be reported in the following cases.
-	The title of the control stays the same as the US because the
translation is the same as the English text(e.g. Name: in German)
-	The title of the control is not displayed (and not translated).
This can sometimes happen if the programmer displays something else on the
control after the dialog is created.

**Test Identifier**
The identifier for this test/bug is "Translation" """

testname = "Translation"

import re
import six

#-----------------------------------------------------------------------------
def TranslationTest(windows):
    """Returns just one bug for each control"""
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        # get if any items are untranslated
        untranTitles, untranIndices = _GetUntranslations(win)

        if untranTitles:
            indicesAsString = ",".join([six.text_type(idx) for idx in untranIndices])

            bugs.append((
                [win,],
                {
                    "StringIndices": indicesAsString,
                    "Strings": ('"%s"' % '","'.join(untranTitles))
                },
                testname,
                0)
            )


    return bugs

def _GetUntranslations(win):
    """Find the text items that are not translated"""
    # remove ampersands and other non translatable bits from the string
    nonTransChars = re.compile(
        """(\&(?!\&)|	# ampersand not followed by an ampersand
            \.\.\.$|	# elipsis ...
            ^\s*|		# leading whitespace
            \s*$|		# trailing whitespace
            \s*:\s*$	# trailing colon (with/without whitespace)
            )*			# repeated as often as necessary
            """, re.X)


    # clean each of the loc titles for comparison
    cleanedLocTitles = []
    for title in win.texts():
        cleanedLocTitles.append(nonTransChars.sub("", title))

    # clean each of the ref titles for comparison
    cleanedRefTitles = []
    for title in win.ref.texts():
        cleanedRefTitles.append(nonTransChars.sub("", title))

    untranslatedTitles = []
    untranslatedIndices = []

    # loop over each of the cleaned loc title
    for index, title in enumerate(cleanedLocTitles):

        # if the title is empty just skip it
        if not title:
            continue

        # if that title is in the cleaned Ref Titles
        if title in cleanedRefTitles:
            # add this as one of the bugs
            untranslatedTitles.append(title)
            untranslatedIndices.append(index)

    # return all the untranslated titles and thier indices
    return untranslatedTitles, untranslatedIndices


TranslationTest.TestsMenus = True

