pywinauto-64
============

This pywinauto branch (0.5.x) supports 64-bit and 32-bit Python from 2.6 to 3.4.

### Dependencies
* pyWin32 package only ([build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/) is recommended).

ActiveState Python 2.x already contains pyWin32 by default.

### Setup

Just unpack and run **python setup.py install**

### Testing status

| Platform | unit tests pass rate |
|-----------------------------|-----------------|
| Win7 x64, Python 2.6 32-bit | 88,8% (231/260) |
| Win7 x64, Python 2.6 64-bit | 84,6% (220/260) |
| Win7 x64, Python 3.4 32-bit | 85%   (221/260) |
| Win7 x64, Python 3.4 64-bit | 80,4% (209/260) |

#### Packages required for running unit tests
* [Pillow](https://pypi.python.org/pypi/Pillow/2.7.0) or PIL
* [coverage](https://pypi.python.org/pypi/coverage)