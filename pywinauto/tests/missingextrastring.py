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

"""Different number of special character sequences Test

**What is checked**
This test checks to make sure that certain special character sequences
appear the in the localised if they appear in the reference title strings.
These strings usually mean something to the user but the software internally
does not care if they exist or not. The list that is currently checked is:
">>", ">", "<<", "<", ":"(colon), "...", "&&", "&", ""

**How is it checked**
For each of the string to check for we make sure that if it appears in the
reference that it also appears in the localised title.

**When is a bug reported**
 - If the reference has one of the text strings but the localised does
   not a bug is reported.
 - If the localised has one of the text strings but the reference does
   not a bug is reported.

Bug Extra Information
The bug contains the following extra information

**MissingOrExtra**	Whether the characters are missing or extra from the
controls being check as compared to the reference, (String with
following possible values)

 - "MissingCharacters"	The characters are in the reference but not in
   the localised.
 - "ExtraCharacters"	The characters are not in the reference but are in
   the localised.

**MissingOrExtraText**	What character string is missing or added, String

**Is Reference dialog needed**
This test will not run if the reference controls are not available.

**False positive bug reports**
Currently this test is at a beta stage filtering of the results is probably
necessary at the moment.

**Test Identifier**
The identifier for this test/bug is "MissingExtraString"
"""

__revision__ = "$Revision$"



testname = "MissingExtraString"

CharsToCheck = (
    ">",
    ">>",
    "<",
    "<<",
    "&",
    "&&",
    "...",
    ":",
    "@",

)

#-----------------------------------------------------------------------------
def MissingExtraStringTest(windows):
    """Return the errors from running the test"""
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        for char in CharsToCheck:
            missing_extra = ''

            if win.window_text().count(char) > win.ref.window_text().count(char):
                missing_extra = u"ExtraCharacters"
            elif win.window_text().count(char) < win.ref.window_text().count(char):
                missing_extra = u"MissingCharacters"

            if missing_extra:
                bugs.append((
                    [win,],
                    {
                        "MissingOrExtra": missing_extra,
                        "MissingOrExtraText": char
                    },
                    testname,
                    0))

    return bugs


MissingExtraStringTest.TestsMenus = True

def _unittests():
    """Run the unit tests for this test"""
    # set up some mock controls - (only requires some 'text')
    test_strings = (
        ("Nospecial", "NietherHere", 0),

        ("Nob>ug", "Niet>herHere", 0),
        ("No>>bug", ">>NietherHere", 0),
        ("<Nobug", "NietherHere<", 0),
        ("Nobug<<", "NietherHere<<", 0),
        ("No&bu&g", "&NietherHere&", 0),
        ("No&&bug", "NietherHere&&", 0),
        ("Nobug...", "Nieth...erHere", 0),
        ("Nobug:", ":NietherHere", 0),
        ("No@bug", "Ni@etherHere", 0),
        (">Th&&>>is &str<<ing >>has ju<st about @everything :but ...no bug",
            "This s&tr...in<<g has jus<t abou&&t every>th:ing >>but no @bug",
            0),

        ("GreaterAdded >", "No Greater", 1),
        ("GreaterMissing", "Greater > here", 1),

        ("doubleGreater added >>", "No double greater", 1),
        ("doubleGreater added >>", "No double greater >", 1),
        ("doubleGreater Missing >", "No double greater >>", 1),
        )

    class Control(object):
        def Text(self):
            return self.text

    ctrls = []
    total_bug_count = 0
    for loc, ref, num_bugs in test_strings:
        ctrl = Control()
        ctrl.text = loc
        ctrl.ref = Control()
        ctrl.ref.text = ref

        total_bug_count += num_bugs
        num_found = len(MissingExtraStringTest([ctrl]))
        try:
            assert num_found == num_bugs
        except Exception:
            #print num_found, num_bugs, loc, ref
            pass


        ctrls.append(ctrl)

    assert len(MissingExtraStringTest(ctrls)) == total_bug_count



if __name__ == "__main__":
    _unittests()