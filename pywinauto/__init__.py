# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Python package for automating GUI manipulation on Windows"""

__version__ = "0.6.5"

import sys  # noqa: E402
import warnings  # noqa: E402


def deprecated(method):
    """Decorator for deprecated methods"""

    def wrap(*args, **kwargs):
        warnings.simplefilter("default", DeprecationWarning)
        warnings.warn("Non PEP-8 compliant methods are deprecated", DeprecationWarning, stacklevel=2)
        return method(*args, **kwargs)

    return wrap


if sys.platform == 'win32':
    # Importing only pythoncom can fail with the errors like:
    #     ImportError: No system module 'pywintypes' (pywintypes27.dll)
    # So try to facilitate pywintypes*.dll loading with implicit import of win32api
    import win32api  # noqa: E402
    import pythoncom  # noqa: E402


    def _get_com_threading_mode(module_sys):
        """Set up COM threading model

        The ultimate goal is MTA, but the mode is adjusted
        if it was already defined prior to pywinauto import.
        """
        com_init_mode = 0  # COINIT_MULTITHREADED = 0x0
        if hasattr(module_sys, "coinit_flags"):
            warnings.warn("Apply externally defined coinit_flags: {0}"
                          .format(module_sys.coinit_flags), UserWarning)
            com_init_mode = module_sys.coinit_flags

        try:
            # Probe the selected COM threading mode
            pythoncom.CoInitializeEx(com_init_mode)
            pythoncom.CoUninitialize()
        except pythoncom.com_error:
            warnings.warn("Revert to STA COM threading mode", UserWarning)
            com_init_mode = 2  # revert back to STA

        return com_init_mode


    sys.coinit_flags = _get_com_threading_mode(sys)
    from .sysinfo import UIA_support

    from . import findwindows

    WindowAmbiguousError = findwindows.WindowAmbiguousError
    ElementNotFoundError = findwindows.ElementNotFoundError

    if UIA_support:
        ElementNotFoundError = findwindows.ElementNotFoundError
        ElementAmbiguousError = findwindows.ElementAmbiguousError

    from . import findbestmatch
    from . import backend as backends

    MatchError = findbestmatch.MatchError

    from .application import Application, WindowSpecification


    class Desktop(object):

        """Simple class to call something like ``Desktop().WindowName.ControlName.method()``"""

        def __init__(self, backend=None):
            """Create desktop element description"""
            if backend:
                self.backend = backend
            else:
                self.backend = backends.registry.name

        def window(self, **criterion):
            """Create WindowSpecification object for top-level window"""
            if 'top_level_only' not in criterion:
                criterion['top_level_only'] = True
            if 'backend' not in criterion:
                criterion['backend'] = self.backend
            return WindowSpecification(criterion)

        def __getitem__(self, key):
            """Allow describe top-level window as Desktop()['Window Caption']"""
            return self.window(best_match=key)

        def __getattribute__(self, attr_name):
            """Attribute access for this class"""
            try:
                return object.__getattribute__(self, attr_name)
            except AttributeError:
                return self[attr_name]  # delegate it to __get_item__
