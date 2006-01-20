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

"""ComboBox dropped height Test

**What is checked**
It is ensured that the height of the list displayed when the combobox is
dropped down is not less than the height of the reference.

**How is it checked**
The value for the dropped rectangle can be retrieved from windows. The height
of this rectangle is calculated and compared against the reference height.

**When is a bug reported**
If the height of the dropped rectangle for the combobox being checked is less
than the height of the reference one then a bug is reported.

**Bug Extra Information**
There is no extra information associated with this bug type

**Is Reference dialog needed**
The reference dialog is necessary for this test.

**False positive bug reports**
No false bugs should be reported. If the font of the localised control has a
smaller height than the reference then it is possible that the dropped
rectangle could be of a different size.

**Test Identifier**
The identifier for this test/bug is "ComboBoxDroppedHeight"
"""
__revision__ = "$Revision$"

testname = "ComboBoxDroppedHeight"

def ComboBoxDroppedHeightTest(windows):
    "Check if each combobox height is the same as the reference"
    bugs = []
    for win in windows:
        if not win.ref:
            continue

        if win.Class != "ComboBox" or win.ref.Class != "ComboBox":
            continue

        if win.DroppedRect.height() != win.ref.DroppedRect.height():

            bugs.append((
                [win, ],
                {},
                testname,
                0,)
            )

    return bugs

