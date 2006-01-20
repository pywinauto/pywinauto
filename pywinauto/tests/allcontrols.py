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

"""Get All Controls Test
What is checked
This test does no actual testing  it just returns each control.

How is it checked
A loop over all the controls in the dialog is made and each control added to
the list of bugs

When is a bug reported
For each control.

Bug Extra Information
There is no extra information associated with this bug type

Is Reference dialog needed
No,but if available the reference control will be returned with the localised
control.

False positive bug reports
Not possible

Test Identifier
The identifier for this test/bug is "AllControls"
"""
__revision__ = "$Revision$"


testname = "AllControls"

#-----------------------------------------------------------------------------
def AllControlsTest(windows):
    "Returns just one bug for each control"

    bugs = []
    for win in windows:
        bugs.append((
            [win,],
            {},
            testname,
            0
        ))


    return bugs

