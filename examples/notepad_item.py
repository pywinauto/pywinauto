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

"""Run some automations to test things"""
from __future__ import unicode_literals
from __future__ import print_function

from pywinauto import application
#from pywinauto import tests
#from pywinauto.findbestmatch import MatchError


#application.set_timing(3, .5, 10, .5, .4, .2, .2, .1, .2, .5)

app = application.Application()
app.start(r"notepad.exe")

app['Notepad'].wait('ready')

app['Notepad'].menu_select("File->PageSetup")

# ----- Page Setup Dialog ----
# Select the 4th combobox item
app['PageSetupDlg']['ComboBox1'].select(4)

# Select the 'Letter' combobox item
app['PageSetupDlg']['ComboBox1'].select("Letter")

# ----- Next Page Setup Dialog ----
app['PageSetupDlg']['Printer'].click()

app['PageSetupDlg']['Network'].click()

# ----- Connect To Printer Dialog ----
# Select a checkbox
app['ConnectToPrinter']['ExpandByDef'].check()
# Uncheck it again - but use click this time!
app['ConnectToPrinter']['ExpandByDef'].click()

app['ConnectToPrinter']['OK'].close_click()

# ----- 2nd Page Setup Dialog again ----
app['PageSetupDlg2']['Properties'].click()

# ----- Document Properties Dialog ----
doc_props = app.window(title_re = ".*Document Properties")

# Two ways of selecting tabs
doc_props['TabCtrl'].select(2)
doc_props['TabCtrl'].select("Layout")

# click a Radio button
doc_props['RotatedLandscape'].click()
doc_props['Portrait'].click()

# open the Advanced options dialog in two steps
advbutton = doc_props['Advanced']
advbutton.click()

# ----- Advanced Options Dialog ----
# close the 4 windows
app.window(title_re = ".* Advanced Options")['Ok'].click()

# ----- Document Properties Dialog again ----
doc_props['Cancel'].close_click()
# ----- 2nd Page Setup Dialog again ----
app['PageSetup2']['OK'].close_click()
# ----- Page Setup Dialog ----
app['PageSetup']['Ok'].close_click()

# type some text
app['Notepad']['Edit'].set_edit_text("I am typing s\xe4me text to Notepad"
    "\r\n\r\nAnd then I am going to quit")

# exit notepad
app['NotepadDialog'].menu_select("File->Exit")
app['Notepad']['No'].close_click()

