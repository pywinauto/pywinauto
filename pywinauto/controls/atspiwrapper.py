# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Basic wrapping of Linux ATSPI elements"""

from __future__ import unicode_literals
from __future__ import print_function

import six

from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from ..linux.atspi_element_info import AtspiElementInfo

from Xlib import Xatom
from Xlib.display import Display


# region PATTERNS


# ====================================================================
class InvalidWindowHandle(RuntimeError):

    """Raised when an invalid handle is passed to AtspiWrapper"""

    def __init__(self, hwnd):
        """Initialise the RuntimeError parent with the mesage"""
        RuntimeError.__init__(self,
                              "Handle {0} is not a vaild window handle".format(hwnd))


# =========================================================================
class AtspiMeta(BaseMeta):

    """Metaclass for AtspiWrapper objects"""

    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""
        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls._control_types:
            AtspiMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this Atspi element"""

        # Check for a more specific wrapper in the registry
        try:
            wrapper_match = AtspiMeta.control_type_to_cls[element.control_type]
        except KeyError:
            # Set a general wrapper by default
            wrapper_match = AtspiWrapper

        return wrapper_match


# =========================================================================
@six.add_metaclass(AtspiMeta)
class AtspiWrapper(BaseWrapper):

    """
    Default wrapper for User Interface Automation (Atspi) controls.

    All other Atspi wrappers are derived from this.

    This class wraps a lot of functionality of underlying Atspi features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """

    _control_types = []

    # ------------------------------------------------------------
    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(AtspiWrapper, cls)._create_wrapper(cls, element_info, AtspiWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid AtspiElementInfo or it can be an
          instance or subclass of AtspiWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['atspi'])

    # ------------------------------------------------------------
    def set_keyboard_focus(self):
        """Set the focus to this element"""
        self.element_info.component.grab_focus("screen")
        return self

    # ------------------------------------------------------------
    def set_window_focus(self, pid):
        display = Display()
        root = display.screen().root

        def top_level_set_focus_by_pid(pid, window, indent):
            children = window.query_tree().children
            for w in children:
                if window.get_wm_class() is not None:
                    if window.get_full_property(display.get_atom("_NET_WM_PID"), Xatom.CARDINAL).value[0] == pid:
                        window.raise_window()

                top_level_set_focus_by_pid(pid, w, indent + '-')

        top_level_set_focus_by_pid(pid, root, '-')

    # ------------------------------------------------------------
    def set_focus(self):
        if self.parent() == self.root() or self.parent().parent() == self.root() and not self.is_visible():
            # Try to find first child control of current window like button or text area and set focus to it.
            # It should automatically set focus to window.
            for child in self.descendants():
                # TODO extend list of focusable elements
                if child.element_info.control_type in ['PushButton', 'CheckBox', 'ToggleButton', 'RadioButton',
                                                       'Text']:
                    child.set_keyboard_focus()
                    break

            if not self.is_visible():
                # If unable to set window focus via ATSPI try to set focus via XLIB
                self.set_window_focus(self.element_info.process_id)
        else:
            self.set_keyboard_focus()

        return self

    # ------------------------------------------------------------
    def get_states(self):
        return self.element_info.get_state_set()

    # ------------------------------------------------------------
    def get_menu(self):
        self.verify_actionable()
        menu = None
        for child in self.descendants():
            if child.element_info.control_type in ["MenuBar"]:
                menu = child
        return menu

    # -----------------------------------------------------------
    def is_active(self):
        """Whether the element is active or not"""
        for i in self.state:
            if i == 'STATE_ACTIVE':
                return True
        return False

    # -----------------------------------------------------------
    def get_slider(self):
        self.verify_actionable()
        slider = []
        for child in self.descendants():
            if child.element_info.control_type in ["ScrollBar"]:
                slider.append(child)
        return slider[0]


backend.register('atspi', AtspiElementInfo, AtspiWrapper)
backend.activate('atspi')  # default for Linux
