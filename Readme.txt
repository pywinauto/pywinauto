pywinauto
(c) Mark Mc Mahon 2006-2010, Intel Corporation 2015-2016, Open Source community 2016-2019
Released under BSD 3-clause license


What is it
----------
pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At its simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls.


Manual Installation
------------
Install the following Python packages
(Required) pyWin32      http://sourceforge.net/projects/pywin32/files/pywin32/
(Required) comtypes     https://github.com/enthought/comtypes
(Optional) PIL          http://www.pythonware.com/products/pil/index.htm
Unzip the pywinauto zip file to a folder.
Run "python setup.py install"

To check you have it installed correctly
run in Python REPL:
>>> from pywinauto import Application
>>> app = Application(backend="uia").start("notepad.exe")
>>> app.UntitledNotepad.type_keys("%FX")

Installation in silent mode (Python 2.7, 3.3+)
------------
 Just run "pip install -U pywinauto"


Where to start
--------------
The Getting Started Guide: https://pywinauto.readthedocs.io/en/latest/getting_started.html
It explains the core concept, how to choose appropriate backend, spy tools and many other things.

We also have several examples installed along with the pywinauto demonstrating the work with
Notepad, MSPaint, WireShark, explorer.exe and etc.
https://github.com/pywinauto/pywinauto/tree/master/examples
All the examples designed to work only on a system with English as OS interface language.


How does it work
----------------
A lot is done through attribute access (__getattr__) for each class. For instance,
when you get the attribute of an Application or Dialog object it looks for a 
dialog or control (respectively).

myapp.Notepad # looks for a Window/Dialog of your app that has a title 'similar'
              # to "Notepad"
              
myapp.PageSetup.OK # looks first for a dialog with a title like "PageSetup"
                   # then it looks for a control on that dialog with a title
                   # like "OK"
                   
The attribute resolution is delayed (at the present with a hard coded time limit) until
it succeeds. So for example, if you select a menu option and then look for the
resulting dialog e.g. with the following code:

app.Notepad.menu_select("File->SaveAs")
app.SaveAs.ComboBox5.select("UTF-8")
app.SaveAs.edit1.set_text("Example-utf8.txt")
app.SaveAs.Save.click()

At the 2nd line the SaveAs dialog might not be open by the time this line is
executed. So what happens is that we wait until we have a control to resolve 
before resolving the dialog. At that point, if we can't find a SaveAs dialog with
a ComboBox5 control we wait a short period of time and try again. 
The procedure repeats up to a maximum time limit (currently 5 second!)

This internal waiting loop is to avoid the user having to use time.sleep or
implementing a custom "wait_for_dialog" function.

However, if your application performs particularly long-standing operations, it can
still take time for a new dialog to appear or disappear. In that case, you could
wait for the transition to a new state like so ::

  app.Open.Open.click() # opening large file
  app.Open.wait_not('visible') # make sure "Open" dialog became invisible
  # wait up to 30 seconds until data.txt is loaded
  app.window(title='data.txt - Notepad').wait('ready', timeout=30)


Several similar tools for comparison
------------------------------------
See rating of competitors in the open source field (updated every month):
https://github.com/pywinauto/pywinauto/wiki/UI-Automation-tools-ratings

* Other free tools

  - See a collection at: https://github.com/atinfo/awesome-test-automation

* Commercial tools

  - TestComplete
  - Squish
  - HP UFT (former QTP)
  - LeanFT
  - WinRunner
  - SilkTest
  - Many Others
