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
    "Return the errors from running the test"
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        for char in CharsToCheck:
            missing_extra = ''

            if win.Text.count(char) > win.ref.Text.count(char):
                missing_extra = "ExtraCharacters"
            elif win.Text.count(char) < win.ref.Text.count(char):
                missing_extra = "MissingCharacters"

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
    "Run the unit tests for this test"


    # set up some mock controls - (only requires some 'Text')
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
        pass

    ctrls = []
    total_bug_count = 0
    for loc, ref, num_bugs in test_strings:
        ctrl = Control()
        ctrl.Text = loc
        ctrl.ref = Control()
        ctrl.ref.Text = ref

        total_bug_count += num_bugs
        num_found = len(MissingExtraStringTest([ctrl]))
        try:
            assert num_found == num_bugs
        except:
            print num_found, num_bugs, loc, ref

        ctrls.append(ctrl)

    assert len(MissingExtraStringTest(ctrls)) == total_bug_count



if __name__ == "__main__":
    _unittests()