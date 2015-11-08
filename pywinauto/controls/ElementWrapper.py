from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

#region IMPORTS
# pylint:  disable-msg=W0611

#import sys
import time
import re
#import ctypes
#import win32api
#import win32gui
#import win32con
#import pywintypes # TODO: get rid of pywintypes because it's not compatible with Python 3.5
#import locale

# the wrappers may be used in an environment that does not need
# the actions - as such I don't want to require sendkeys - so
# the following makes the import optional.

from .. import SendKeysCtypes as SendKeys
from .. import six
#from .. import win32functions, win32defines, win32structures
from ..timings import Timings
from ..actionlogger import ActionLogger

import comtypes
import comtypes.client
'''
from System.Windows.Automation import AutomationElement, PropertyCondition, TreeScope, Condition, Automation, InvokePattern, TextPattern
from System.Windows.Automation import AutomationPattern, BasePattern, DockPattern, ExpandCollapsePattern, GridItemPattern, GridPattern
from System.Windows.Automation import ItemContainerPattern, MultipleViewPattern, RangeValuePattern, ScrollItemPattern, ScrollPattern
from System.Windows.Automation import SelectionItemPattern, SelectionPattern, SynchronizedInputPattern, TableItemPattern, TablePattern
from System.Windows.Automation import TextPattern, TogglePattern, TransformPattern, ValuePattern, VirtualizedItemPattern, WindowPattern
'''

from .HwndWrapper import _MetaWrapper, HwndWrapper
#endregion

from ..UIAElementInfo import UIAElementInfo, _UIA_dll, _iuia

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
_control_types = [attr[len('UIA_'):][:-len('ControlTypeId')] for attr in dir(_UIA_dll) if attr.endswith('ControlTypeId')]
_known_control_types = {}
for type in _control_types:
    _known_control_types[type] = _UIA_dll.__getattribute__('UIA_' + type + 'ControlTypeId')

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
def removeNonAlphaNumericSymbols(s):
    return re.sub("\W", "_", s)

#=========================================================================
class WindowNotFoundError(Exception):
    "No window could be found"
    pass

#=========================================================================
class WindowAmbiguousError(Exception):
    "There was more then one window that matched"
    pass
#=========================================================================
class InvalidWindowElement(RuntimeError):
    "Raised when an invalid handle is passed to HwndWrapper "
    def __init__(self, elementinfo):
        "Initialise the RuntimError parent with the mesage"
        RuntimeError.__init__(self,
            "Element {0} is not a vaild UIA element".format(elementinfo))


#=========================================================================
@six.add_metaclass(_MetaWrapper)
class ElementWrapper(object):
    """
    Default wrapper for User Interface Automation (UIA) controls.

    All other UIA wrappers are derived from this.

    This class wraps a lot of functionality of underlying UIA features
    for working with windows.

    Most of the methods apply to every single window type. For example
    you can Click() on any window.
    """

    windowclasses = []
    controltypes = []
    handle = None
    can_be_label = False

    #------------------------------------------------------------
    def __new__(cls, elementInfo):
        # only use the meta class to find the wrapper for ElementWrapper
        # so allow users to force the wrapper if they want
        if cls != ElementWrapper:
            obj = object.__new__(cls)
            obj.__init__(elementInfo)
            return obj

        new_class = cls.FindWrapperUIA(elementInfo)
        obj = object.__new__(new_class)
        # TODO: check what type of wrapper was found: Hwnd-type or UIA-type
        if new_class != ElementWrapper:
            obj.__init__(elementInfo.handle)
        else:
            obj.__init__(elementInfo)
        return obj

    #------------------------------------------------------------
    def __init__(self, elementInfo):
        """
        Initialize the element

        * **elementInfo** is instance of UIAElementInfo

        If **elementInfo** is not instance of UIAElementInfo then
        an InvalidWindowHandle error is raised.
        """
        if not isinstance(elementInfo, UIAElementInfo):
            raise TypeError('ElementWrapper can be initialized with UIAElementInfo instance only!')
        if elementInfo:
            self._elementInfo = elementInfo
            if self._elementInfo.ControlType in ['Button', 'Text', 'Group']:
                self.can_be_label = True
            self.actions = ActionLogger()
        else:
            raise RuntimeError('NULL COM pointer used to initialize ElementWrapper')

    #------------------------------------------------------------
