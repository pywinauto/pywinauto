pywinauto-64
============

This pywinauto branch (0.5.x) supports 64-bit and 32-bit Python from 2.6 to 3.4.

### Dependencies
* pyWin32 package only ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended).

ActiveState Python 2.x already contains pyWin32 by default.

### Setup

* Install pyWin32 extensions above (no need for Active Python except 3.4 64-bit)
* Download [master branch as ZIP](https://github.com/vasily-v-ryabov/pywinauto-64/archive/master.zip)
* Just unpack and run **python.exe setup.py install**

### Testing status

* [Unit tests pass rate for master branch](https://github.com/vasily-v-ryabov/pywinauto-64/wiki/Unit-testing-status)

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)