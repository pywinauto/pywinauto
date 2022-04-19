"""Wrap various WPF windows controls. To be used with 'wpf' backend."""
import locale
import time
import comtypes
import six

from . import wpfwrapper
from . import win32_controls
from . import common_controls
from .. import findbestmatch
from .. import timings
from ..windows.wpf_element_info import WPFElementInfo
from ..windows.injected.api import *


# ====================================================================
class WindowWrapper(wpfwrapper.WPFWrapper):

    """Wrap a WPF Window control"""

    _control_types = ['Window']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(WindowWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def move_window(self, x=None, y=None, width=None, height=None):
        """Move the window to the new coordinates

        * **x** Specifies the new left position of the window.
                Defaults to the current left position of the window.
        * **y** Specifies the new top position of the window.
                Defaults to the current top position of the window.
        * **width** Specifies the new width of the window.
                Defaults to the current width of the window.
        * **height** Specifies the new height of the window.
                Defaults to the current height of the window.
        """
        cur_rect = self.rectangle()

        # if no X is specified - so use current coordinate
        if x is None:
            x = cur_rect.left
        else:
            try:
                y = x.top
                width = x.width()
                height = x.height()
                x = x.left
            except AttributeError:
                pass

        # if no Y is specified - so use current coordinate
        if y is None:
            y = cur_rect.top

        # if no width is specified - so use current width
        if width is None:
            width = cur_rect.width()

        # if no height is specified - so use current height
        if height is None:
            height = cur_rect.height()

        # ask for the window to be moved
        self.set_property('Left', x)
        self.set_property('Top', y)
        self.set_property('Width', width)
        self.set_property('Height', height)

        time.sleep(timings.Timings.after_movewindow_wait)

    # -----------------------------------------------------------
    def is_dialog(self):
        """Window is always a dialog so return True"""
        return True
