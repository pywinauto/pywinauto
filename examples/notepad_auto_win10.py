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


#OS Supported : Windows 10 only
#Goal :: Automating few Notepad operations to test things
#For debug purpose I have put some print statements also
#NOTE : To make the things little slow I have given 1secs of sleep time. You can remove that if you don't want the delay.


from pywinauto import application
import time

app=application.Application()
app.start("Notepad.exe")
print("Notepad started")


app['Notepad'].wait('ready')
print("Waiting to be ready")

print("Starting jobs")
print("Opening Page Setup Dialog")
app['Notepad'].menu_select("File->PageSetup")

#Selecting Size of the paper
app["PageSetup"]["Combobox1"].select(2)
time.sleep(1)
app.PageSetup.Combobox1.select(1)
time.sleep(1)
app.PageSetup.Combobox1.select("Letter")
time.sleep(1)

print("OK upto this : Size Selection")

#Navigating the radio buttons to select Portrait/Landscape mode.
app["Page Setup"]["Radio Button1"].click()
time.sleep(1)
app["Page Setup"]["Radio Button2"].click()
time.sleep(1)
app.PageSetup.RadioButton1.click()
time.sleep(1)
print("OK upto this : Orientation Selection")


app.PageSetup.Cancel.click()
#app.PageSetup.OK.click()--> If you want to save the changes

print("OK upto this : Page Setup Dialog")


print("Opening Print Dialog")
app.Notepad.menu_select("File->Print")
#Selecting printer from the given printer list
app.print["list item"].select(1)
time.sleep(1)
#app.print["list item"].select("Name of the printer exactly as it is") --> You can give the name of the printer as well
print("OK upto this : Printer selection")


#Select preference button
app.Print.Preferences.click()
time.sleep(1)
app["Printing Preferences"].OK.click()

#app.Print["Find Printer..."].click()

app.Print.Cancel.click()
#app.Print.OK.click() --> If you want to start printing

print("Writing something to Notepad")
time.sleep(1)
app['Notepad']['Edit'].set_edit_text("I am typing s\xe4me text to Notepad"
    "\r\n\r\nAnd then I am going to quit")

print("Exiting Application")
app.UntitledNotepad.menu_select("File->Exit")
time.sleep(1)
app.Notepad.DontSave.click()
time.sleep(1)

print("Application Closed")
