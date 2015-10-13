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

import sys
import time
import os.path

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

outputfilename = os.path.abspath(outputfilename)


# start IE with a start URL of what was passed in
app = application.Application().start(
    r"c:\program files\internet explorer\iexplore.exe %s"% web_addresss)

# some pages are slow to open - so wait some seconds
time.sleep(10)

ie =  app.window_(title_re = ".*Windows Internet Explorer.*")

# ie doesn't define it's menus as Menu's but actually as a toolbar!
print("No Menu's in IE:", ie.MenuItems())
print("They are implemented as a toolbar:", ie.Toolbar3.Texts())

ie.TypeKeys("%FA")
#ie.Toolbar3.PressButton("File")
app.SaveWebPage.Edit.SetEditText(os.path.join(r"c:\.temp",outputfilename))


app.SaveWebPage.Save.CloseClick()

# if asked to overwrite say yes
if app.SaveWebPage.Yes.Exists():
    app.SaveWebPage.Yes.CloseClick()

print("saved:", outputfilename)

# quit IE
ie.TypeKeys("%FC")

