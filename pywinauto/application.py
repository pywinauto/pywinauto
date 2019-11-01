import sys

from .base_application import WindowSpecification  # noqa: F401

if sys.platform == 'win32':
    from .windows.application import Application  # noqa: F401
else:
    from .linux.application import Application  # noqa: F401
