# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""Basic wrapping of UI Automation elements"""
import six

from ..macos.ax_element_info import AxElementInfo

from ..macos.macos_functions import set_ax_attribute
from ..macos.macos_functions import setAppFrontmost

from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta


# ====================================================================
class InvalidWindowHandle(RuntimeError):

    """Raised when an invalid handle is passed to AXWrapper"""

    def __init__(self, hwnd):
        """Initialise the RuntimeError parent with the mesage"""
        RuntimeError.__init__(self,
                              "Handle {0} is not a vaild window handle".format(hwnd))


# =========================================================================
class AXMeta(BaseMeta):

    """Metaclass for AXWrapper objects"""

    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""
        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls._control_types:
            AXMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this AX element"""
        # Set a general wrapper by default
        wrapper_match = AXWrapper
        # print('element.control_type:', element.control_type)

        # Check for a more specific wrapper in the registry
        if element.control_type in AXMeta.control_type_to_cls:
            wrapper_match = AXMeta.control_type_to_cls[element.control_type]

        return wrapper_match


# =========================================================================
@six.add_metaclass(AXMeta)
class AXWrapper(BaseWrapper):

    """
    Default wrapper for User Interface Automation (AX) controls.

    All other AX wrappers are derived from this.

    This class wraps a lot of functionality of underlying AX features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """

    _control_types = []

    # ------------------------------------------------------------
    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(AXWrapper, cls)._create_wrapper(cls, element_info, AXWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid AXElementInfo or it can be an
          instance or subclass of AXWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['ax'])

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value"""
        if hasattr(self.element_info,'hash'):
            return self.element_info.hash()
        else:
            return ''

    # ------------------------------------------------------------

    def set_focus(self):
        # If element can be focusable we must take the following steps to make it focused:
        # 1. Make element keyboard focused
        # 2. Make the window that contains this element focused as well
        # Otherwise just focus the window
        window = None
        is_window = self.element_info.control_type == 'Window'
        if is_window:
            window = self.element_info
        else:
            window = self.element_info.window

        # Focus the element
        # Check the control type to avoid focusing twice
        if not is_window and self.element_info.can_be_keyboard_focusable:
            set_ax_attribute(self.element_info.ref,"AXFocused",True)
        
        # Focus the window
        if window and window.control_type == 'Window':
            set_ax_attribute(self.element_info.ref, "AXFocused", True)
            set_ax_attribute(self.element_info.ref, "AXMinimized", False)
            setAppFrontmost(self.element_info.process_id)

    def friendly_class_name(self):
        return self.element_info.control_type


backend.register('ax', AxElementInfo, AXWrapper)
backend.activate('ax')  # default for macOS