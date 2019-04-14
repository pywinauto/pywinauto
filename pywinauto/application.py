import sys

from .base_application import WindowSpecification  # noqa: W0611

if sys.platform == 'win32':
    from .windows.application import Application  # noqa: W0611
else:
    from .linux.application import Application  # noqa: W0611

__all__ = [WindowSpecification, Application]
