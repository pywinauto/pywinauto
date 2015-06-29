pywinauto
(c) Mark Mc Mahon 2006-2015
Released under the LGPL v2.1 or later


What is it
----------
pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it's simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls.


Installation
------------
Install the following Python packages
(Required) pyWin32      http://sourceforge.net/projects/pywin32/files/pywin32/
(Optional) PIL          http://www.pythonware.com/products/pil/index.htm
Unzip the pywinauto zip file to a folder.
Run "python setup.py install"

To check you have it installed correctly
run Python
>>> from pywinauto.application import Application
>>> app = Application.start("notepad.exe")
>>> app.UntitledNotepad.TypeKeys("%FX")

Installation in silent mode (Python 2.7, 3.1-3.5)
------------
 Just run "pip install pywinauto"


Where to start
--------------
Look at the examples provided in test_application.py
There are examples in there to work with Notepad and MSPaint.

Note: These examples currently only work on English.


How does it work
----------------
A lot is done through attribute access (__getattr__) for each class. For example
when you get the attribute of an Application or Dialog object it looks for a 
dialog or control (respectively).

myapp.Notepad # looks for a Window/Dialog of your app that has a title 'similar'
              # to "Notepad"
              
myapp.PageSetup.OK # looks first for a dialog with a title like "PageSetup"
                   # then it looks for a control on that dialog with a title
                   # like "OK"
                   
This attribute resolution is delayed (currently a hard coded amount of time) until
it succeeds. So for example if you Select a menu option and then look for the
resulting dialog e.g.

app.Notepad.MenuSelect("File->SaveAs")
app.SaveAs.ComboBox5.Select("UTF-8")
app.SaveAs.edit1.SetText("Example-utf8.txt")
app.SaveAs.Save.Click()

At the 2nd line the SaveAs dialog might not be open by the time this line is
executed. So what happens is that we wait until we have a control to resolve 
before resolving the dialog. At that point if we can't find a SaveAs dialog with
a ComboBox5 control then we wait a very short period of time and try again, 
this is repeated up to a maximum time (currently 1 second!)

This avoid the user having to use time.sleep or a "WaitForDialog" function.

If your application performs long time operation, new dialog can appear or
disappear later. You can wait for its new state like so ::

  app.Open.Open.Click() # opening large file
  app.Open.WaitNot('visible') # make sure "Open" dialog became invisible
  # wait for up to 30 seconds until data.txt is loaded
  app.Window(title='data.txt - Notepad').Wait('ready', timeout=30)


Some similar tools for comparison
---------------------------------
* Python tools

  - PyAutoGui
  - AXUI
  - winGuiAuto

* Other scripting language tools

  - Perl Win32::GuiTest
  - Ruby Win32-Autogui

* Other free tools

  - AutoIt
  - See collection at: https://github.com/atinfo/awesome-test-automation

* Commercial tools

  - WinRunner
  - SilkTest
  - Many Others
