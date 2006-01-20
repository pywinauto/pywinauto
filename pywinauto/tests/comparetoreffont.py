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

"""Compare against reference font test
What is checked
This test checks all the parameters of the font for the control against the
font for the reference control. If any value is different then this is reported
as a bug.
Here is a list of all the possible values that are tested:
lfFaceName	The name of the font
lfHeight	The height of the font
lfWidth		Average width of characters
lfEscapement	Angle of text
lfOrientation	Another angle for the text!
lfWeight	How bold the text is
lfItalic	If the font is italic
lfUnderline	If the font is underlined
lfStrikeOut	If the font is struck out
lfCharSet	The character set of the font
lfOutPrecision	The output precision
lfClipPrecision	The clipping precision
lfQuality	The output quality
lfPitchAndFamily	The pitch and family


How is it checked
Each property of the font for the control being tested is compared against the
equivalent property of the reference control font for equality.

When is a bug reported
For each property of the font that is not identical to the reference font a bug
is reported. So for example if the Font Face has changed and the text is bold
then (at least) 2 bugs will be reported.

Bug Extra Information
The bug contains the following extra information
Name	Description
ValueType	What value is incorrect (see above), String
Ref	The reference value converted to a string, String
Loc	The localised value converted to a string, String

Is Reference dialog needed
This test will not run if the reference controls are not available.

False positive bug reports
Running this test for Asian languages will result in LOTS and LOTS of false
positives, because the font HAS to change for the localised text to display
properly.

Test Identifier
The identifier for this test/bug is "CompareToRefFont"
"""

__revision__ = "$Revision$"

testname = "CompareToRefFont"

def CompareToRefFontTest(windows):
    "Compare the font to the font of the reference control"
    bugs = []
    for win in windows:
        # if no reference then skip the control
        if not win.ref:
            continue

        # find each of the bugs
        for fname, loc_value in win.Font._fields_:

            # get the reference value
            ref_value = getattr(win.ref.Font, fname)

            # If they are different
            if loc_value != ref_value:

                # Add the bug information
                bugs.append((
                    [win, ],
                    {
                        "ValueType": fname,
                        "Ref": unicode(ref_value),
                        "Loc": unicode(loc_value),
                    },
                    testname,
                    0,)
                )
    return bugs



