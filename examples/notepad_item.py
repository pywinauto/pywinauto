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

from pywinauto import application
from pywinauto import tests
from pywinauto.findbestmatch import MatchError
from pywinauto import findwindows


#application.set_timing(3, .5, 10, .5, .4, .2, .2, .1, .2, .5)

"Run a quick test on Notepad"

app = application.Application()
app.start_(ur"notepad.exe")

app['Notepad'].Wait('ready')

app['Notepad'].MenuSelect("File->PageSetup")

# ----- Page Setup Dialog ----
# Select the 4th combobox item
app['PageSetupDlg']['ComboBox1'].Select(4)

# Select the 'Letter' combobox item
app['PageSetupDlg']['ComboBox1'].Select("Letter")

# ----- Next Page Setup Dialog ----
app['PageSetupDlg']['Printer'].Click()

app['PageSetupDlg']['Network'].Click()

# ----- Connect To Printer Dialog ----
# Select a checkbox
app['ConnectToPrinter']['ExpandByDef'].Check()
# Uncheck it again - but use Click this time!
app['ConnectToPrinter']['ExpandByDef'].Click()

app['ConnectToPrinter']['OK'].CloseClick()

# ----- 2nd Page Setup Dialog again ----
app['PageSetupDlg2']['Properties'].Click()

# ----- Document Properties Dialog ----
doc_props = app.window_(title_re = ".*Document Properties")

# Two ways of selecting tabs
doc_props['TabCtrl'].Select(2)
doc_props['TabCtrl'].Select("Layout")

# click a Radio button
doc_props['RotatedLandscape'].Click()
doc_props['Portrait'].Click()

# open the Advanced options dialog in two steps
advbutton = doc_props['Advanced']
advbutton.Click()

# ----- Advanced Options Dialog ----
# close the 4 windows
app.window_(title_re = ".* Advanced Options")['Ok'].Click()

# ----- Document Properties Dialog again ----
doc_props['Cancel'].CloseClick()
# ----- 2nd Page Setup Dialog again ----
app['PageSetup2']['OK'].CloseClick()
# ----- Page Setup Dialog ----
app['PageSetup']['Ok'].CloseClick()

# type some text
app['Notepad']['Edit'].SetEditText(u"I am typing s\xe4me text to Notepad"
    "\r\n\r\nAnd then I am going to quit")

# exit notepad
app['NotepadDialog'].MenuSelect("File->Exit")
app['Notepad']['No'].CloseClick()

