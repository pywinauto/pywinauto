pywinauto
============
pywinauto (c) Mark Mc Mahon, 2006 - 2015

pywinauto is coming back! Newer version adds 64-bit support and works on Python 3.x.

This set of python modules to automate the Microsoft Windows GUI 
allows you to send mouse and keyboard actions to windows dialogs and controls, 
but it also supports more complex actions.

### Setup
* Install [pyWin32 extensions](http://sourceforge.net/projects/pywin32/files/pywin32/) (no need for Active Python)
* Download [latest pywinauto release](https://github.com/pywinauto/pywinauto/releases/download/0.5.0/pywinauto-0.5.0.zip)
* Just unpack and run `python setup.py install`

### Planning pywinauto 0.5.1 (2015 July, 14)
 - [x] Resolved pip issues
 - [x] Warnings about mismatched Python/application bitness
 - [x] Added "TCheckBox" class name to ButtonWrapper detection list

### pywinauto 0.5.0 release notes (2015 June, 30)
 - [x] 64-bit Python and 64-bit apps support (but 32-bit Python is recommended for 32-bit apps)
 - [x] Python 2.x/3.x compatibility
 - [!] Added pyWin32 dependency (silent install by pip for 2.7 and 3.1+)
 - [x] Improvements for Toolbar, TreeView, UpDown and DateTimePicker wrappers
 - [x] Improved `best_match` algorithm allows names like `ToolbarFile`
 - [x] Clicks can be performed with pressed Ctrl or Shift
 - [x] Drag-n-drop and scrolling methods (DragMouse, DragMouseInput, MouseWheelInput)
 - [x] Improved menu support: handling OWNERDRAW menu items; access by command_id (like `$23453`)
 - [x] Resolved issues with py2exe and cx_freeze
 - [x] `RemoteMemoryBlock` can now detect memory corruption by checking guard signature
 - [x] Upgraded `taskbar` module for Win7 and Win 8.1; added hidden icons support
 - [x] `sysinfo` module for checking 32-bit or 64-bit OS and Python
 - [x] `set_foreground` flag in `TypeKeys` method for typing into in-place controls
 - [x] flags `create_new_console` and `wait_for_idle` in `Application.start` method
 
### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)

### Dependencies
* pyWin32 package ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended). This is NOT required for ActivePython (except 3.4 64-bit).

### Testing status
* [Unit tests pass rate for master branch](https://github.com/pywinauto/pywinauto/wiki/Unit-testing-status)

### Continuous Integration
* [![Build status](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true)](https://ci.appveyor.com/project/vasily-v-ryabov/pywinauto/branch/master)
* [![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
* [![Code Issues](http://www.quantifiedcode.com/api/v1/project/6d66337b96ed4cb1b01574ec3d39f9e7/badge.svg)](http://www.quantifiedcode.com/app/project/6d66337b96ed4cb1b01574ec3d39f9e7)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)
