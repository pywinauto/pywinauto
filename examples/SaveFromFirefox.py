# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2009 Mark Mc Mahon
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

from __future__ import print_function

try:
    from pywinauto import application
except ImportError:
    import os.path
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    import sys
    sys.path.append(pywinauto_path)
    from pywinauto import application

from pywinauto.controls.HwndWrapper import HwndWrapper

import sys
import time
import os.path

from pywinauto import WindowAmbiguousError

if len(sys.argv) < 2:
    print("please specify a web address to download")
    sys.exit()

web_addresss = sys.argv[1]

if len(sys.argv) > 2:
    outputfilename = sys.argv[2]
else:
    outputfilename = web_addresss
    outputfilename = outputfilename.replace('/', '')
    outputfilename = outputfilename.replace('\\', '')
    outputfilename = outputfilename.replace(':', '')
    if not (outputfilename.lower().endswith("htm") or
       outputfilename.lower().endswith("html")):
       outputfilename += ".html"

# make sure that we have an absolute path - otherwise it is
# hard to know where firefox might save the file!
outputfilename = os.path.abspath(outputfilename)

# start IE with a start URL of what was passed in
app = application.Application().start(
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe %s"% web_addresss)

# some pages are slow to open - so wait some seconds
time.sleep(5)

# mozilla is one of thos applications that use existing windows
# if they exist (at least on my machine!)
# so if we cannot find any window for that process
#  - find the actual process
#  - connect to it
if app.windows_():
    mozilla =  app.window_(title_re=".*Mozilla Firefox")

else:
    app = application.Application().connect(title_re=".*Mozilla Firefox")
    mozilla = app.window_(title_re=".*Mozilla Firefox")

# ie doesn't define it's menus as Menu's but actually as a toolbar!
print("No Menu's in FireFox:", mozilla.MenuItems())

# File -> Save As
mozilla.type_keys("%FA")
#ie.Toolbar3.PressButton("File")
app.SaveAs.Edit.SetEditText(outputfilename)

app.SaveAs.Save.CloseClick()

try:
    # if asked to overwrite say yes
    if app.SaveAs.Yes.Exists():
        app.SaveAs.Yes.CloseClick()
except WindowAmbiguousError as e:
    for w in e.windows:
        w = HwndWrapper(w)
        print(w.window_text(), w.class_name())

print("saved:", outputfilename)

# File close tab or close
#(Firefox makes it easy for us having the same shortcut for both!
mozilla.type_keys("%FC")

