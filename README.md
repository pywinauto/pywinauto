[![Join the chat at https://gitter.im/pywinauto/pywinauto](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pywinauto/pywinauto?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Documentation Status](https://readthedocs.org/projects/pywinauto/badge/?version=latest)](http://pywinauto.readthedocs.org/en/latest/?badge=latest)
[![Windows Tests](https://ci.appveyor.com/api/projects/status/ykk30v7vcvkmpnoq/branch/master?svg=true&passingText=Windows%20tests%20-%20OK&pendingText=Windows%20tests%20-%20running&failingText=Windows%20tests%20-%20fail)](https://ci.appveyor.com/project/pywinauto/pywinauto)
[![Linux Tests](https://travis-ci.org/pywinauto/pywinauto.svg?branch=master)](https://travis-ci.org/pywinauto/pywinauto)
[![codecov.io](http://codecov.io/github/pywinauto/pywinauto/coverage.svg?branch=master)](http://codecov.io/github/pywinauto/pywinauto?branch=master)
[![Code Health](https://landscape.io/github/pywinauto/pywinauto/master/landscape.svg?style=flat)](https://landscape.io/github/pywinauto/pywinauto/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b823b31c0f2b48d6873326d038c5a516)](https://www.codacy.com/app/pywinauto/pywinauto?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pywinauto/pywinauto&amp;utm_campaign=Badge_Grade)

pywinauto
============
pywinauto is a set of python modules to automate the Microsoft Windows GUI. 
At its simplest it allows you to send mouse and keyboard actions to windows 
dialogs and controls, but it has support for more complex actions like getting text data.

Supported technologies under the hood: Win32 API (`backend="win32"`; used by default),
MS UI Automation (`backend="uia"`). User input emulation modules
 `mouse` and `keyboard` work on both Windows and Linux.

### Setup
* run `pip install -U pywinauto` (dependencies will be installed automatically)

### Examples
It is simple and the resulting scripts are very readable. How simple?

```python
from pywinauto.application import Application
app = Application().start("notepad.exe")

app.UntitledNotepad.menu_select("Help->About Notepad")
app.AboutNotepad.OK.click()
app.UntitledNotepad.Edit.type_keys("pywinauto Works!", with_spaces = True)
```

More detailed example for `explorer.exe` (using **MS UI Automation**):

```python
from pywinauto import Desktop, Application

Application().start('explorer.exe "C:\\Program Files"')

# connect to another process spawned by explorer.exe
app = Application(backend="uia").connect(path="explorer.exe", title="Program Files")

app.ProgramFiles.set_focus()
common_files = app.ProgramFiles.ItemsView.get_item('Common Files')
common_files.right_click_input()
app.ContextMenu.Properties.invoke()

# this dialog is open in another process (Desktop object doesn't rely on any process id)
Properties = Desktop(backend='uia').Common_Files_Properties
Properties.print_control_identifiers()
Properties.Cancel.click()
Properties.wait_not('visible') # make sure the dialog is closed
```

### Documentation
* [Latest documentation on ReadTheDocs](http://pywinauto.readthedocs.io/en/latest/)
* [Getting Started Guide](http://pywinauto.readthedocs.io/en/latest/getting_started.html)
* [Code examples (gists) on gist.github.com](https://gist.github.com/vasily-v-ryabov)
* [Mailing list](https://sourceforge.net/p/pywinauto/mailman/)

### Dependencies (if install manually)
* Windows:
  - [pyWin32](http://sourceforge.net/projects/pywin32/files/pywin32/)
  - [comtypes](https://github.com/enthought/comtypes)
  - [six](https://pypi.python.org/pypi/six)
* Linux:
  - [python-xlib](https://github.com/python-xlib/python-xlib)
  - [six](https://pypi.python.org/pypi/six)
* Optional packages:
  - Install [Pillow](https://pypi.python.org/pypi/Pillow) (by `pip install -U Pillow`) to be able to call `capture_as_image()` method for making a control's snapshot.

### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow)
* [coverage](https://pypi.python.org/pypi/coverage)

Run all the tests: `python ./pywinauto/unittests/testall.py`

### Contribution
Pull requests are very welcome. Read [Contribution Guide](https://github.com/pywinauto/pywinauto/wiki/Contribution-Guide-(draft)) for more details about unit tests, coding conventions, etc.

### Copyrights
Pywinauto for native Windows GUI was initially written by **Mark Mc Mahon**. 
Mark brought many great ideas into the life using power of Python. 
Further contributors are inspired of the nice API so that the development continues.

Starting from 0.6.0 pywinauto is distributed under the BSD 3-clause license.
Pywinauto 0.5.4 and before was distributed under the LGPL v2.1 or later.
* (c) [The Open Source Community](https://github.com/pywinauto/pywinauto/graphs/contributors), 2015-2017 (0.6.0+ development)
* (c) Intel Corporation, 2015 (led 0.5.x maintenance)
* (c) Michael Herrmann, 2012-2013 (0.4.2)
* (c) Mark Mc Mahon, 2006-2010 (0.4.0 and before)
