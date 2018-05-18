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

"""Compare against reference font test

**What is checked**
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


**How is it checked**
Each property of the font for the control being tested is compared against the
equivalent property of the reference control font for equality.

**When is a bug reported**
For each property of the font that is not identical to the reference font a bug
is reported. So for example if the Font Face has changed and the text is bold
then (at least) 2 bugs will be reported.

**Bug Extra Information**
The bug contains the following extra information
Name	Description
ValueType	What value is incorrect (see above), String
Ref	The reference value converted to a string, String
Loc	The localised value converted to a string, String

**Is Reference dialog needed**
This test will not run if the reference controls are not available.

**False positive bug reports**
Running this test for Asian languages will result in LOTS and LOTS of false
positives, because the font HAS to change for the localised text to display
properly.

**Test Identifier**
The identifier for this test/bug is "CompareToRefFont"
"""

testname = "CompareToRefFont"

import six
from pywinauto import win32structures
_font_attribs = [field[0] for field in win32structures.LOGFONTW._fields_]

def CompareToRefFontTest(windows):
    """Compare the font to the font of the reference control"""
    bugs = []
    for win in windows:
        # if no reference then skip the control
        if not win.ref:
            continue

        # find each of the bugs
        for font_attrib in _font_attribs:

            loc_value = getattr(win.font(), font_attrib)
            # get the reference value
            ref_value = getattr(win.ref.font(), font_attrib)

            # If they are different
            if loc_value != ref_value:

                # Add the bug information
                bugs.append((
                    [win, ],
                    {
                        "ValueType": font_attrib,
                        "Ref": six.text_type(ref_value),
                        "Loc": six.text_type(loc_value),
                    },
                    testname,
                    0,)
                )
    return bugs




