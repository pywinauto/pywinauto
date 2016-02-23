from __future__ import unicode_literals
from __future__ import print_function

import time
import re
import ctypes
import locale

from .. import SendKeysCtypes as SendKeys
from .. import six
from .. import win32defines, win32structures, win32functions
from ..timings import Timings
from ..actionlogger import ActionLogger

import comtypes
import comtypes.client

from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from .HwndWrapper import HwndWrapper
from .HwndWrapper import HwndMeta

from ..UIAElementInfo import UIAElementInfo
from ..UIAElementInfo import _UIA_dll
from ..UIAElementInfo import _iuia

#region PATTERNS
AutomationElement = comtypes.gen.UIAutomationClient.IUIAutomationElement

DockPattern = comtypes.gen.UIAutomationClient.IUIAutomationDockPattern
ExpandCollapsePattern = comtypes.gen.UIAutomationClient.IUIAutomationExpandCollapsePattern
GridItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationGridItemPattern
GridPattern = comtypes.gen.UIAutomationClient.IUIAutomationGridPattern
InvokePattern = comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern
ItemContainerPattern = comtypes.gen.UIAutomationClient.IUIAutomationItemContainerPattern
LegacyIAccessiblePattern = comtypes.gen.UIAutomationClient.IUIAutomationLegacyIAccessiblePattern
MultipleViewPattern = comtypes.gen.UIAutomationClient.IUIAutomationMultipleViewPattern
RangeValuePattern = comtypes.gen.UIAutomationClient.IUIAutomationRangeValuePattern
ScrollItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationScrollItemPattern
ScrollPattern = comtypes.gen.UIAutomationClient.IUIAutomationScrollPattern
SelectionItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationSelectionItemPattern
SelectionPattern = comtypes.gen.UIAutomationClient.IUIAutomationSelectionPattern
SynchronizedInputPattern = comtypes.gen.UIAutomationClient.IUIAutomationSynchronizedInputPattern
TableItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationTableItemPattern
TablePattern = comtypes.gen.UIAutomationClient.IUIAutomationTablePattern
TextPattern = comtypes.gen.UIAutomationClient.IUIAutomationTextPattern
TogglePattern = comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern
TransformPattern = comtypes.gen.UIAutomationClient.IUIAutomationTransformPattern
ValuePattern = comtypes.gen.UIAutomationClient.IUIAutomationValuePattern
VirtualizedItemPattern = comtypes.gen.UIAutomationClient.IUIAutomationVirtualizedItemPattern
WindowPattern = comtypes.gen.UIAutomationClient.IUIAutomationWindowPattern
#endregion

#=========================================================================
_control_types = [attr[len('UIA_'):-len('ControlTypeId')] for attr in dir(_UIA_dll) if attr.endswith('ControlTypeId')]
_known_control_types = {}
for type in _control_types:
    _known_control_types[_UIA_dll.__getattribute__('UIA_' + type + 'ControlTypeId')] = type

#=========================================================================
pywinauto_control_types = {'Custom': None,
                           'DataGrid': None,
                           'Document': None,
                           'Group': 'GroupBox',
                           'Hyperlink': None,
                           'Image': None,
                           'List': 'ListBox',
                           'MenuBar': None,
                           'Menu': None,
                           'Pane': None,
                           'ProgressBar': 'Progress',
                           'ScrollBar': None,
                           'Separator': None,
                           'Slider': None,
                           'Spinner': 'UpDown',
                           'SplitButton': None,
                           'Tab': 'TabControl',
                           'Table': None,
                           'Text': 'Static',
                           'Thumb': None,
                           'TitleBar': None,
                           'ToolBar': 'Toolbar',
                           'ToolTip': 'ToolTips',
                           'Tree': None,
                           'Window': 'Dialog',
                           }

#=========================================================================
class UiaMeta(BaseMeta):
    "Metaclass for UiaWrapper objects"
    control_types = {}

    def __init__(cls, name, bases, attrs):
        "Register the control types"

        type.__init__(cls, name, bases, attrs)

        for control_type in cls.controltypes:
            UiaMeta.control_types[control_type] = cls

    @staticmethod
    def find_wrapper(element):
        "Find the correct wrapper for this UI element"

        # TODO: temporary thing (there is no UIA based wrappers tree yet)
        return UIAWrapper

#=========================================================================
@six.add_metaclass(UiaMeta)
class UIAWrapper(BaseWrapper):
    """
    Default wrapper for User Interface Automation (UIA) controls.

    All other UIA wrappers are derived from this.

    This class wraps a lot of functionality of underlying UIA features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can Click() on any element.
    """

    #------------------------------------------------------------
    # TODO: can't inherit __new__ function from BaseWrapper?
    def __new__(cls, element_info):
        # only use the meta class to find the wrapper for BaseWrapper
        # so allow users to force the wrapper if they want
        if cls != UIAWrapper:
            obj = object.__new__(cls)
            obj.__init__(element_info)
            return obj

        new_class = cls.find_wrapper(element_info)
        obj = object.__new__(new_class)

        obj.__init__(element_info)

        return obj

    #-----------------------------------------------------------
    def __init__(self, elementInfo):
        """Initialize the control
        * **elementInfo** is either a valid UIAElementInfo or it can be an
          instance or subclass of UIAWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, elementInfo, backend.registry.backends['uia'])

    #------------------------------------------------------------
    def __hash__(self):
        "Return unique hash value based on element's Runtime ID"
        return hash(self.elementInfo.runtime_id)

    #------------------------------------------------------------
    def friendly_class_name(self):
        """
        Return the friendly class name for the control

        This differs from the class of the control in some cases.
        class_name() is the actual 'Registered' window class of the control
        while friendly_class_name() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if self.friendlyclassname is None:
            if self.element_info.controlType not in _known_control_types.keys():
                self.friendlyclassname = str(self.element_info.controlType)
            else:
                ControlType = _known_control_types[self.element_info.controlType]
                if (ControlType not in pywinauto_control_types.keys()) or (pywinauto_control_types[ControlType] is None):
                    self.friendlyclassname = ControlType
                else:
                    self.friendlyclassname = pywinauto_control_types[ControlType]
        return self.friendlyclassname

    #-----------------------------------------------------------
    def IsKeyboardFocusable(self):
        "Return True if element can be focused with keyboard"
        return self.element_info.element.CurrentIsKeyboardFocusable == 1

    #-----------------------------------------------------------
    def HasKeyboardFocus(self):
        "Return True if element is focused with keyboard"
        return self.element_info.element.CurrentHasKeyboardFocus == 1

    #-----------------------------------------------------------
    def set_focus(self):
        "Set the focus to this element"
        if self.IsKeyboardFocusable() and not self.HasKeyboardFocus():
            try:
                self.element_info.element.SetFocus()
            except comtypes.COMError as exc:
                pass # TODO: add RuntimeWarning here

        return self


backend.register('uia', UIAElementInfo, UIAWrapper)
