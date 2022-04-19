"""Basic wrapping of WPF elements"""

from __future__ import unicode_literals
from __future__ import print_function

import six
import time
import warnings
import threading

from .. import backend
from .. import WindowNotFoundError  # noqa #E402
from ..timings import Timings
from .win_base_wrapper import WinBaseWrapper
from ..base_wrapper import BaseMeta
from ..windows.injected.api import *
from ..windows.wpf_element_info import WPFElementInfo

class WpfMeta(BaseMeta):

    """Metaclass for UiaWrapper objects"""
    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""

        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls._control_types:
            WpfMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this UIA element"""

        # Check for a more specific wrapper in the registry
        try:
            wrapper_match = WpfMeta.control_type_to_cls[element.control_type]
        except KeyError:
            # Set a general wrapper by default
            wrapper_match = WPFWrapper

        return wrapper_match

@six.add_metaclass(WpfMeta)
class WPFWrapper(WinBaseWrapper):
    _control_types = []

    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(WPFWrapper, cls)._create_wrapper(cls, element_info, WPFWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid UIAElementInfo or it can be an
          instance or subclass of UIAWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        WinBaseWrapper.__init__(self, element_info, backend.registry.backends['wpf'])

    def get_property(self, name, error_if_not_exists=False):
        return self.element_info.get_property(name, error_if_not_exists)

    def set_property(self, name, value, is_enum=False):
        ConnectionManager().call_action('SetProperty', self.element_info.pid,
                                        element_id=self.element_info.runtime_id,
                                        name=name,
                                        value=value, is_enum=is_enum)
        return self

    def automation_id(self):
        """Return the Automation ID of the control"""
        return self.element_info.auto_id

    def is_keyboard_focusable(self):
        """Return True if the element can be focused with keyboard"""
        return self.get_property('Focusable') or False

    def has_keyboard_focus(self):
        """Return True if the element is focused with keyboard"""
        return self.get_property('IsKeyboardFocused') or False

    def set_focus(self):
        ConnectionManager().call_action('SetFocus', self.element_info.pid,
                                        element_id=self.element_info.runtime_id)
        return self

    def get_active(self):
        """Return wrapper object for current active element"""
        element_info = self.backend.element_info_class.get_active(self.element_info._pid)
        if element_info is None:
            return None
        return self.backend.generic_wrapper_class(element_info)

    def is_active(self):
        """Whether the window is active or not"""
        focused_wrap = self.get_active()
        if focused_wrap is None:
            return False
        return (focused_wrap.top_level_parent() == self.top_level_parent())


    #  System.Windows.WindowState enum
    NORMAL=0
    MAXIMIZED=1
    MINIMIZED=2

    # -----------------------------------------------------------
    def close(self):
        """
        Close the window
        """
        ConnectionManager().call_action('InvokeMethod', self.element_info.pid,
                                        element_id=self.element_info.runtime_id,
                                        name='Close')

    # -----------------------------------------------------------
    def minimize(self):
        """
        Minimize the window
        """
        self.set_property('WindowState', 'Minimized', is_enum=True)
        return self

    # -----------------------------------------------------------
    def maximize(self):
        """
        Maximize the window

        Only controls supporting Window pattern should answer
        """
        self.set_property('WindowState', 'Maximized', is_enum=True)
        return self

    # -----------------------------------------------------------
    def restore(self):
        """
        Restore the window to normal size

        Only controls supporting Window pattern should answer
        """
        # it's very strange, but set WindowState to Normal is not enough...
        self.set_property('WindowState', 'Normal', is_enum=True)
        restore_rect = self.get_property('RestoreBounds')
        self.move_window(restore_rect['left'],
                         restore_rect['top'],
                         self.get_property('Width'),
                         self.get_property('Height'))
        self.set_property('WindowState', 'Normal', is_enum=True)
        return self

    # -----------------------------------------------------------
    def get_show_state(self):
        """Get the show state and Maximized/minimzed/restored state

        Returns values as following

        Normal = 0
        Maximized = 1
        Minimized = 2
        """
        val = self.element_info.get_property('WindowState')
        if val == 'Normal':
            return self.NORMAL
        elif val == 'Maximized':
            return self.MAXIMIZED
        elif val == 'Minimized':
            return self.MINIMIZED
        else:
            raise ValueError('Unexpected WindowState property value: ' + str(val))

    # -----------------------------------------------------------
    def is_minimized(self):
        """Indicate whether the window is minimized or not"""
        return self.get_show_state() == self.MINIMIZED

    # -----------------------------------------------------------
    def is_maximized(self):
        """Indicate whether the window is maximized or not"""
        return self.get_show_state() == self.MAXIMIZED

    # -----------------------------------------------------------
    def is_normal(self):
        """Indicate whether the window is normal (i.e. not minimized and not maximized)"""
        return self.get_show_state() == self.NORMAL

    def move_window(self, x=None, y=None, width=None, height=None):
        """Move the window to the new coordinates
        The method should be implemented explicitly by controls that
        support this action. The most obvious is the Window control.
        Otherwise the method throws AttributeError

        * **x** Specifies the new left position of the window.
          Defaults to the current left position of the window.
        * **y** Specifies the new top position of the window.
          Defaults to the current top position of the window.
        * **width** Specifies the new width of the window. Defaults to the
          current width of the window.
        * **height** Specifies the new height of the window. Default to the
          current height of the window.
        """
        raise AttributeError("This method is not supported for {0}".format(self))


backend.register('wpf', WPFElementInfo, WPFWrapper)