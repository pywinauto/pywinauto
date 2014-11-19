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

"Run some automations to test things"

__revision__ = "$Revision: 214 $"

import time

try:
    from pywinauto import application
except ImportError:
    import os.path
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    import sys
    sys.path.append(pywinauto_path)
    from pywinauto import application

from pywinauto import tests
from pywinauto.findbestmatch import MatchError
from pywinauto import findwindows
from pywinauto import WindowAmbiguousError
from pywinauto.controls import WrapHandle

from pywinauto.timings import Timings
Timings.Fast()

app = application.Application()

# for distribution we don't want to connect to anybodies application
# because we may mess up something they are working on!
#try:
#    app.connect_(path = ur"c:\windows\system32\mspaint.exe")
#except application.ProcessNotFoundError:
#    app.start_(ur"c:\windows\system32\mspaint.exe")

app.start_(ur"mspaint.exe")

pwin = app.window_(title_re = ".* - Paint")

# get the previous image size
pwin.MenuSelect("Image->Attributes")
prev_width = app.Attributes.Edit1.Texts()[1]
prev_height = app.Attributes.Edit2.Texts()[1]

# set our preferred area
app.Attributes.Edit1.TypeKeys("350")  # you can use TypeKeys or
app.Attributes.Edit2.SetEditText("350")   # SetText - they work differently!

app.Attributes.OK.CloseClick()

try:
    # get the reference to the Canvas window
    canvas = pwin.Afx100000008
    canvas.WrapperObject()
except WindowAmbiguousError, e:
    print e, e.windows
    for w in e.windows:
        w = WrapHandle(w)
        print w.WindowText(), w.Class()
    import sys
    sys.exit()

# make sure the pencil tool is selected
pwin.Tools2.Click(coords = (91, 16))

size = 15
num_slants = 20

# draw the axes
canvas.PressMouse(coords = (size, size * num_slants))
canvas.MoveMouse(coords = (size*num_slants, size*num_slants))
canvas.MoveMouse(coords = (size * num_slants, size))
canvas.ReleaseMouse()

# now draw the lines
print "*** if you move your mouse over Paint as it is drawing ***"
print "*** these lines then it will mess up the drawing!      ***\n"
for i in range(1, num_slants):

    endcoords = (size * (num_slants - i), size * num_slants)
    canvas.PressMouse(coords = (size * num_slants, i * size)) # start
    canvas.MoveMouse(coords = endcoords) # x and y axes
    canvas.ReleaseMouse(coords = endcoords)

# may fail if PIL is not installed
image = canvas.CaptureAsImage()
if image:
    image.save(r"Application_Paint_test.png")
    print "Saved image as: Application_Paint_test.png"

# set it back to  original width and height
pwin.MenuSelect("Image->Attributes")
# set our preferred area
app.Attributes.Edit1.TypeKeys(prev_width)
app.Attributes.Edit2.SetEditText(prev_height)
app.Attributes.OK.CloseClick()


# close Paint
pwin.MenuSelect("File->Exit")

if app.Paint.No.Exists():
    #print "It existed!"
    # Click the no button on the message box asking if we want to save
    app.Paint.No.CloseClick()
