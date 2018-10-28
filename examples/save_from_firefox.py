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

from pywinauto.controls.hwndwrapper import HwndWrapper

import sys
import time
import os.path

from pywinauto import WindowAmbiguousError

if len(sys.argv) < 2:
    print("please specify a web address to download")
    sys.exit()

web_address = sys.argv[1]

if len(sys.argv) > 2:
    outputfilename = sys.argv[2]
else:
    outputfilename = web_address
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
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe {}".format(web_address))

# some pages are slow to open - so wait some seconds
time.sleep(5)

# mozilla is one of thos applications that use existing windows
# if they exist (at least on my machine!)
# so if we cannot find any window for that process
#  - find the actual process
#  - connect to it
if app.windows():
    mozilla =  app.window(title_re=".*Mozilla Firefox")

else:
    app = application.Application().connect(title_re=".*Mozilla Firefox")
    mozilla = app.window(title_re=".*Mozilla Firefox")

# ie doesn't define it's menus as Menu's but actually as a toolbar!
print("No Menu's in FireFox:", mozilla.menu_items())

# File -> Save As
mozilla.type_keys("%FA")
#ie.Toolbar3.press_button("File")
app.SaveAs.Edit.set_edit_text(outputfilename)

app.SaveAs.Save.close_click()

try:
    # if asked to overwrite say yes
    if app.SaveAs.Yes.Exists():
        app.SaveAs.Yes.close_click()
except WindowAmbiguousError as e:
    for w in e.windows:
        w = HwndWrapper(w)
        print(w.window_text(), w.class_name())

print("saved:", outputfilename)

# File close tab or close
#(Firefox makes it easy for us having the same shortcut for both!
mozilla.type_keys("%FC")

