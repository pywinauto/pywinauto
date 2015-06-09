pywinauto UI Automation API extensions branch
============

<<<<<<< HEAD
This branch is experimental for UI Automation API (UIA) as a back-end.
=======
pywinauto (c) Mark Mc Mahon, 2006 - 2015

pywinauto is coming back! Newer version adds 64-bit support and works on Python 3.x.

This set of python modules to automate the Microsoft Windows GUI 
allows you to send mouse and keyboard actions to windows dialogs and controls, 
but it also supports more complex actions.

### Setup
* Install [pyWin32 extensions](http://sourceforge.net/projects/pywin32/files/pywin32/) (no need for Active Python)
* Download [master branch as ZIP](https://github.com/pywinauto/pywinauto/archive/master.zip)
* Just unpack and run `python setup.py install`

### Roadmap
* pywinauto 0.5.0 is planned until end of June, 2015.
 - [x] 64-bit Python is supported
 - [x] Python 2.x/3.x compatibility
 - [!] Added pyWin32 dependency
 - [x] Improvements for Toolbar, TreeView, UpDown and DateTimePicker wrappers
 - [x] Improved `best_match` algorithm allows names like `ToolbarFile`
 - [x] Clicks can be performed with pressed Ctrl or Shift
 - [x] Drag-n-drop and scrolling methods (DragMouse, DragMouseInput, MouseWheelInput)
 - [x] Improved menu support: handling OWNERDRAW menu items; access by command_id (like `$23453`)
 - [x] `RemoteMemoryBlock` can now detect memory corruption by checking guard signature
 - [ ] Upgraded `taskbar` module
 - [x] `sysinfo` module for checking 32-bit or 64-bit OS and Python
 - [x] `set_foreground` flag in `TypeKeys` method for typing into in-place controls
 - [x] `create_new_console` flag in `Application.start_` method

### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)

### Dependencies
* pyWin32 package ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended). This is NOT required for ActivePython (except 3.4 64-bit).

### Testing status
* [Unit tests pass rate for master branch](https://github.com/pywinauto/pywinauto/wiki/Unit-testing-status)

### AppVeyor testing status
* [![Build status](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true)](https://ci.appveyor.com/project/vasily-v-ryabov/pywinauto/branch/master)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)
>>>>>>> master
