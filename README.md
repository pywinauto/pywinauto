pywinauto-64
============

pywinauto (c) Mark Mc Mahon, 2006 - 2013
pywinauto-64 (c) 2014 - 2015

pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it's simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls.

### Supported Pythons
* Python 2.6, 2.7, 3.4
* 32-bit and 64-bit

### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)


### Dependencies
* pyWin32 package ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended). This is NOT required for ActivePython (except 3.4 64-bit).

### Setup

* Install pyWin32 extensions above (no need for Active Python)
* Download [master branch as ZIP](https://github.com/vasily-v-ryabov/pywinauto-64/archive/master.zip)
* Just unpack and run **python.exe setup.py install**

### Testing status

* [Unit tests pass rate for master branch](https://github.com/vasily-v-ryabov/pywinauto-64/wiki/Unit-testing-status)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)