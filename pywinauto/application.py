# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
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

"""Application class interface for all operating systems

When starting to automate an application you must initialize an instance
of the Application class. Then you must :func:`Application.start` that
application or :func:`Application.connect()` to a running instance of that
application.

Once you have an Application instance you can access dialogs in that
application either by using one of the methods below. ::

   dlg = app.YourDialogTitle
   dlg = app.child_window(title="your title", classname="your class", ...)
   dlg = app['Your Dialog Title']

Similarly once you have a dialog you can get a control from that dialog
in almost exactly the same ways. ::

  ctrl = dlg.YourControlTitle
  ctrl = dlg.child_window(title="Your control", classname="Button", ...)
  ctrl = dlg["Your control"]

.. note::

   For attribute access of controls and dialogs you do not have to
   have the title of the control exactly, it does a best match of the
   available dialogs or controls.

.. seealso::

   :func:`pywinauto.findwindows.find_elements` for the keyword arguments that
   can be passed to both: :func:`Application.window` and
   :func:`WindowSpecification.child_window`
"""

import sys

from .base_application import WindowSpecification  # noqa: W0611

if sys.platform == 'win32':
    from .windows.application import Application  # noqa: W0611
    from .windows.application import process_module  # noqa: W0611
    from .windows.application import process_get_modules  # noqa: W0611
    from .windows.application import ProcessNotFoundError  # noqa: W0611
    from .windows.application import AppStartError  # noqa: W0611
    from .windows.application import AppNotConnected  # noqa: W0611
else:
    from .linux.application import Application  # noqa: W0611

__all__ = ["WindowSpecification", "Application"]
