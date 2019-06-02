import os
import sys

from .base_application import WindowSpecification

if sys.platform == 'win32':
    from .windows.application import Application
elif sys.platform == 'darwin':
    from .macos.application import Application
else:
    from .linux.application import Application
