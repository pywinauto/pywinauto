pywinauto-64
============

This pywinauto branch (0.5.x) supports 64-bit and 32-bit Python from 2.6 to 3.4.

### Dependencies
* pyWin32 package only ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended).

ActiveState Python 2.x already contains pyWin32 by default.

### Setup

Just unpack and run **python setup.py install**

### Testing status

| Platform: Win7 x64 (1920x1080) | unit tests pass rate |
|-----------------------------|-----------------|
| Python 2.6 32-bit | 97,3% (253/260) |
| Python 2.6 64-bit | 93,1% (242/260) |
| Python 3.4 32-bit | 97,7% (254/260) |
| Python 3.4 64-bit | 92,7% (241/260) |

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)