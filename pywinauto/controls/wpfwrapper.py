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
from .hwndwrapper import HwndWrapper
from ..base_wrapper import BaseMeta

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

backend.register('wpf', WPFElementInfo, WPFWrapper)