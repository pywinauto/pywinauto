pywinauto 
(c) Mark Mc Mahon 2006 
Released under the LGPL licence


What is it
----------
pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it's simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls.


Installation
------------

Unzip the pywinauto zip file to a folder.
Install the following Python packages
ctypes       http://starship.python.net/crew/theller/ctypes/
Sendkeys     http://www.rutherfurd.net/python/sendkeys/index.html
(Optional) PIL          http://www.pythonware.com/products/pil/index.htm
(Optional) elementtree  http://effbot.org/downloads/

To check you have it installed correctly
run Python
>>> import application
>>> app = application.Application().start_("notepad")
>>> app.notepad.TypeKeys("%FX") 


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


Some similar tools for comparison
---------------------------------
 * Python tools
    - Watsup
    - winGuiAuto

 * Other scripting language tools
    - Perl Win32::GuiTest
    - Ruby GuiTest
    - others?

 * Other free tools
    - AutoIt
    - See collection at: 

 * Commercial tools
    - WinRunner
    - SilkTest
    - Visual Test
    - Many Others