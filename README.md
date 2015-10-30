pywinauto
============

[![Join the chat at https://gitter.im/pywinauto/pywinauto](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pywinauto/pywinauto?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Current 0.5.x maintainance is lead by © Intel Corporation, 2015

pywinauto (c) Mark Mc Mahon and [Contributors](https://github.com/pywinauto/pywinauto/graphs/contributors), 2006-2015

pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it’s simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls, but It has support for more complex controls also.

Recommended usage: 64-bit Python is for 64-bit applications; 32-bit Python is for 32-bit ones.

### Setup
* Install [pyWin32 extensions](http://sourceforge.net/projects/pywin32/files/pywin32/) (no need for Active Python)
* Download [latest pywinauto release](https://github.com/pywinauto/pywinauto/releases/download/0.5.3/pywinauto-0.5.3.zip)
* Just unpack and run `python setup.py install`

or

* run `pip install pywinauto` (pypiwin32 will be installed automatically)

### Optional packages
* Install [Pillow](https://pypi.python.org/pypi/Pillow) (PIL fork) to be able to call `CaptureAsImage()` method.

### Documentation
* [Introduction](http://pywinauto.github.io/docs/)
* [Table of contents](http://pywinauto.github.io/docs/contents.html)
* [Change Log / History](http://pywinauto.github.io/docs/HISTORY.html)
* [HowTo's](http://pywinauto.github.io/docs/HowTo.html)
* [Code examples (gists) on gist.github.com](https://gist.github.com/vasily-v-ryabov)
* [Mailing list](https://sourceforge.net/p/pywinauto/mailman/)

### Example
It is simple and the resulting scripts are very readable. How simple?

```python
app.UntitledNotepad.MenuSelect("Help->About Notepad")
app.AboutNotepad.OK.Click()
app.UntitledNotepad.Edit.TypeKeys ("pywinauto Works!", with_spaces = True)
```

### Supported controls
* Native Windows controls (full support through Win32 API)
* .NET Windows Forms (partial support through Win32 API, some basic controls only)

### Continuous Integration / Coverage / Code Issues
* [![Build status](https://ci.appveyor.com/api/projects/status/github/pywinauto/pywinauto?svg=true&passingText=unit%20tests%20-%20OK&pendingText=unit%20tests%20-%20running&failingText=unit%20tests%20-%20fail)](https://ci.appveyor.com/project/pywinauto/pywinauto)
* [![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
* [![Code Issues](http://www.quantifiedcode.com/api/v1/project/9d5d994af16f46a28961f01dfc63091d/badge.svg)](https://www.quantifiedcode.com/app/project/gh:pywinauto:pywinauto)
* [![Code Health](https://landscape.io/github/pywinauto/pywinauto/master/landscape.svg?style=flat)](https://landscape.io/github/pywinauto/pywinauto/master)

### Downloads statistics
* PyPI: [![Daily downloads](https://img.shields.io/pypi/dd/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Weekly downloads](https://img.shields.io/pypi/dw/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto) [![Monthly downloads](https://img.shields.io/pypi/dm/pywinauto.svg)](https://pypi.python.org/pypi/pywinauto)
* GitHub: [![GitHub downloads](https://img.shields.io/github/downloads/pywinauto/pywinauto/0.5.3/pywinauto-0.5.3.zip.svg)](https://github.com/pywinauto/pywinauto/releases/download/0.5.3/pywinauto-0.5.3.zip)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)

(Python 3.5 may require VC++ 2015 re-distributable package)