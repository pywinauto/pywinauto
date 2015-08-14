pywinauto
============
pywinauto (c) Mark Mc Mahon

pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it’s simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls, but It has support for more complex controls also.

Recommended usage: 64-bit Python is for 64-bit applications; 32-bit Python is for 32-bit ones.

### Setup
* Install [pyWin32 extensions](http://sourceforge.net/projects/pywin32/files/pywin32/) (no need for Active Python)
* Download [latest pywinauto release](https://github.com/pywinauto/pywinauto/releases/download/0.5.1/pywinauto-0.5.1.zip)
* Just unpack and run `python setup.py install`

### pywinauto 0.5.1 release notes (2015 July, 13)
 - [x] Resolve pip issues
 - [x] Warnings about mismatched Python/application bitness
 - [x] Add "TCheckBox" class name to ButtonWrapper detection list
 - [x] Fix `DebugMessage` method
 - [x] Disable logging (actionlogger.py) by default, provide shortcuts: ``actionlogger.enable()`` and ``actionlogger.disable()``.
       For those who are familiar with standard ``logging`` module there's method ``actionlogger.set_level(level)``.

### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)

### Continuous Integration / Coverage / Code Issues
* [![Build status](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true)](https://ci.appveyor.com/project/vasily-v-ryabov/pywinauto/branch/master)
* [![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
* [![Code Issues](http://www.quantifiedcode.com/api/v1/project/9d5d994af16f46a28961f01dfc63091d/badge.svg)](https://www.quantifiedcode.com/app/project/gh:pywinauto:pywinauto)

### Downloads statistics
* PyPI: [![Daily downloads](https://img.shields.io/pypi/dd/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Weekly downloads](https://img.shields.io/pypi/dw/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Monthly downloads](https://img.shields.io/pypi/dm/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto)
* GitHub: [![GitHub downloads](https://img.shields.io/github/downloads/pywinauto/pywinauto/0.5.1/pywinauto-0.5.1.zip.svg)](https://github.com/pywinauto/pywinauto/releases/download/0.5.1/pywinauto-0.5.1.zip)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)
