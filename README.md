[![Join the chat at https://gitter.im/pywinauto/pywinauto](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pywinauto/pywinauto?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Documentation Status](https://readthedocs.org/projects/pywinauto/badge/?version=latest)](http://pywinauto.readthedocs.org/en/latest/?badge=latest)
[![Build status](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true&passingText=unit%20tests%20-%20OK&pendingText=unit%20tests%20-%20running&failingText=unit%20tests%20-%20fail)](https://ci.appveyor.com/project/pywinauto/pywinauto)
[![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
[![Code Health](https://landscape.io/github/pywinauto/pywinauto/master/landscape.svg?style=flat)](https://landscape.io/github/pywinauto/pywinauto/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b823b31c0f2b48d6873326d038c5a516)](https://www.codacy.com/app/pywinauto/pywinauto?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pywinauto/pywinauto&amp;utm_campaign=Badge_Grade)

pywinauto
============
pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At it’s simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls, but it has support for more complex actions like getting text data.

Recommended usage: 64-bit Python is for 64-bit applications; 32-bit Python is for 32-bit ones.

### Setup
* run `pip install -U pywinauto` (dependencies will be installed automatically)

### Example
It is simple and the resulting scripts are very readable. How simple?

```python
from pywinauto.application import Application
app = Application().start("notepad.exe")

app.UntitledNotepad.MenuSelect("Help->About Notepad")
app.AboutNotepad.OK.Click()
app.UntitledNotepad.Edit.TypeKeys("pywinauto Works!", with_spaces = True)
```

### Documentation
* [Introduction](http://pywinauto.readthedocs.io/en/latest/)
* [Table of contents](http://pywinauto.readthedocs.io/en/latest/contents.html)
* [Change Log / History](http://pywinauto.readthedocs.io/en/latest/HISTORY.html)
* [HowTo's](http://pywinauto.readthedocs.io/en/latest/HowTo.html)
* [Code examples (gists) on gist.github.com](https://gist.github.com/vasily-v-ryabov)
* [Mailing list](https://sourceforge.net/p/pywinauto/mailman/)

### Dependencies (if install manually):
* [pyWin32](http://sourceforge.net/projects/pywin32/files/pywin32/) only

Optional packages:
* Install [Pillow](https://pypi.python.org/pypi/Pillow) (by `pip install -U Pillow`) to be able to call `CaptureAsImage()` method for making control's snapshot.

### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow)
* [coverage](https://pypi.python.org/pypi/coverage)

Run all the tests: `python ./pywinauto/unittests/testall.py`

### Contribution
Pull requests are very welcome. Read [Contribution Guide](https://github.com/pywinauto/pywinauto/wiki/Contribution-Guide-(draft)) for more details about unit tests, coding style etc.

### Copyrights
Pywinauto for native Windows GUI was initially written by **Mark Mc Mahon**. 
Mark brought many great ideas into the life using power of Python. 
Further contributors are inspired of the nice API so that the development continues.

Pywinauto 0.5.4 and before is distributed under the LGPL v2.1 or later. Starting from 0.6.0 pywinauto will be distributed under the BSD 3-clause license.
* (c) [The Open Source Community](https://github.com/pywinauto/pywinauto/graphs/contributors), 2015-2016 (0.6.0+ development)
* (c) Intel Corporation, 2015 (led 0.5.x maintenance)
* (c) Michael Herrmann, 2012-2013 (0.4.2)
* (c) Mark Mc Mahon, 2006-2010 (0.4.0 and before)