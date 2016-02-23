from __future__ import print_function
from __future__ import unicode_literals

import re

import comtypes
import comtypes.client

from .. import base_wrapper
from ..UIAElementInfo import _UIA_dll

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
def remove_non_alphanumeric_symbols(s):
    return re.sub("\W", "_", s)

#=========================================================================
class UIAWrapper(base_wrapper.BaseWrapper):
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
    def __new__(cls, elementInfo):
        # only use the meta class to find the wrapper for BaseWrapper
        # so allow users to force the wrapper if they want
        if cls != UIAWrapper:
            obj = object.__new__(cls)
            obj.__init__(elementInfo)
            return obj

        new_class = cls.FindWrapperUIA(elementInfo)
        obj = object.__new__(new_class)

        obj.__init__(elementInfo)

        return obj

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
            if self._elementInfo.controlType not in _known_control_types.keys():
                self.friendlyclassname = str(self._elementInfo.controlType)
            else:
                ControlType = _known_control_types[self._elementInfo.controlType]
                if (ControlType not in pywinauto_control_types.keys()) or (pywinauto_control_types[ControlType] is None):
                    self.friendlyclassname = ControlType
                else:
                    self.friendlyclassname = pywinauto_control_types[ControlType]
        return self.friendlyclassname

    #-----------------------------------------------------------
    def IsKeyboardFocusable(self):
        "Return True if element can be focused with keyboard"
        return self._elementInfo.element.CurrentIsKeyboardFocusable == 1

    #-----------------------------------------------------------
    def HasKeyboardFocus(self):
        "Return True if element is focused with keyboard"
        return self._elementInfo.element.CurrentHasKeyboardFocus == 1

    #-----------------------------------------------------------
    def set_focus(self):
        "Set the focus to this element"
        if self.IsKeyboardFocusable() and not self.HasKeyboardFocus():
            try:
                self._elementInfo.element.SetFocus()
            except comtypes.COMError as exc:
                pass # TODO: add RuntimeWarning here

        return self
