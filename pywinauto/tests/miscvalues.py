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

"""Miscellaneous Control properties Test

**What is checked**
This checks various values related to a control in windows. The values tested
are
Class	The class type of the control
Style	The Style of the control (GetWindowLong)
ExStyle	The Extended Style of the control (GetWindowLong)
HelpID	The Help ID of the control (GetWindowLong)
ControlID	The Control ID of the control (GetWindowLong)
UserData	The User Data of the control (GetWindowLong)
Visibility	Whether the control is visible or not

**How is it checked**
After retrieving the information for the control we compare it to the same
information from the reference control.

**When is a bug reported**
If the information does not match then a bug is reported.

**Bug Extra Information**
The bug contains the following extra information
Name	Description
ValueType	What value is incorrect (see above), String
Ref	The reference value converted to a string, String
Loc	The localised value converted to a string, String

**Is Reference dialog needed**
This test will not run if the reference controls are not available.

**False positive bug reports**
Some values can change easily without any bug being caused, for example User
Data is actually meant for programmers to store information for the control
and this can change every time the software is run.

**Test Identifier**
The identifier for this test/bug is "MiscValues"
"""
__revision__ = "$Revision$"

testname = "MiscValues"

def MiscValuesTest(windows):
    "Return the bugs from checking miscelaneous values of a control"
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        diffs = {}

        if win.Class() != win.ref.Class():
            diffs["Class"] = (win.Class(), win.ref.Class())


        if win.Style() != win.ref.Style():
            diffs["Style"] = (win.Style(), win.ref.Style())

        if win.ExStyle() != win.ref.ExStyle():
            diffs["ExStyle"] = (win.ExStyle(), win.ref.ExStyle())

        if win.ContextHelpID() != win.ref.ContextHelpID():
            diffs["HelpID"] = (win.ContextHelpID(), win.ref.ContextHelpID())

        if win.ControlID() != win.ref.ControlID():
            diffs["ControlID()"] = (win.ControlID(), win.ref.ControlID())

        if win.IsVisible() != win.ref.IsVisible():
            diffs["Visibility"] = (win.IsVisible(), win.ref.IsVisible())

        if win.UserData() != win.ref.UserData():
            diffs["UserData()"] = (win.UserData(), win.ref.UserData())


        for diff, vals in diffs.items():
            bugs.append((
                [win, ],
                {
                    "ValueType": diff,
                    "Ref": unicode(vals[1]),
                    "Loc": unicode(vals[0]),
                },
                testname,
                0,)
            )
    return bugs

