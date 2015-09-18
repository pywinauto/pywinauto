pywinauto
============
pywinauto (c) Mark Mc Mahon

pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it’s simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls, but It has support for more complex controls also.

Recommended usage: 64-bit Python is for 64-bit applications; 32-bit Python is for 32-bit ones.

### Setup
* Install [pyWin32 extensions](http://sourceforge.net/projects/pywin32/files/pywin32/) (no need for Active Python)
* Download [latest pywinauto release](https://github.com/pywinauto/pywinauto/releases/download/0.5.2/pywinauto-0.5.2.zip)
* Just unpack and run `python setup.py install`

### Documentation
* [Introduction](http://pywinauto.github.io/docs/)
* [Table of contents](http://pywinauto.github.io/docs/contents.html)
* [Change Log / History](http://pywinauto.github.io/docs/HISTORY.html)
* [HowTo's](http://pywinauto.github.io/docs/HowTo.html)
* [Code examples (gists) on gist.github.com](https://gist.github.com/vasily-v-ryabov)

### pywinauto 0.5.2 release notes (2015 September, 8)
 - [x] `ListViewWrapper` interface is aligned with `TreeViewWrapper`. `GetItem()` returns a `_listview_item` object that looks like `_treeview_element` now.
 - [x] Add DPI awareness API support (Win8+). It allows correct work when all fonts (globally or per monitor) are scaled at 125%, 150% etc.
 - [x] Add new `Application` methods: `CPUUsage` and `WaitCPUUsageLower`.
 - [x] Fix `TreeViewWrapper.Select` method when tree view is not in focus.
 - [x] Fix `TabControlWrapper.Select` method in case of TCS_BUTTONS style set.
 - [x] Fix `ListViewWrapper` methods: `Check` and `UnCheck`.
 - [x] Fix toolbar button access by tooltip text.

### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)

### Continuous Integration / Coverage / Code Issues
* [![Build status](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true)](https://ci.appveyor.com/project/vasily-v-ryabov/pywinauto/branch/master)
* [![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
* [![Code Issues](http://www.quantifiedcode.com/api/v1/project/9d5d994af16f46a28961f01dfc63091d/badge.svg)](https://www.quantifiedcode.com/app/project/gh:pywinauto:pywinauto)
* [![Code Health](https://landscape.io/github/pywinauto/pywinauto/master/landscape.svg?style=flat)](https://landscape.io/github/pywinauto/pywinauto/master)

### Downloads statistics
* PyPI: [![Daily downloads](https://img.shields.io/pypi/dd/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Weekly downloads](https://img.shields.io/pypi/dw/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Monthly downloads](https://img.shields.io/pypi/dm/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto)
* GitHub: [![GitHub downloads](https://img.shields.io/github/downloads/pywinauto/pywinauto/0.5.2/pywinauto-0.5.2.zip.svg)](https://github.com/pywinauto/pywinauto/releases/download/0.5.2/pywinauto-0.5.2.zip)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)
