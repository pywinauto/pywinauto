import os
import sys

from pywinauto.base_application import WindowSpecification

if sys.platform == 'win32':
    from pywinauto.windows.application import Application
else:
    from pywinauto.linux.application import Application
