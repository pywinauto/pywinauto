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
_control_types = [attr[len('UIA_'):-len('ControlTypeId')] for attr in dir(_UIA_dll) if attr.endswith('ControlTypeId')]
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
    has_title = True

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
            if self._elementInfo.controlType in ['Button', 'Text', 'Group']:
                self.can_be_label = True

            self._cache = {}

            self.actions = ActionLogger()
        else:
            raise RuntimeError('NULL COM pointer used to initialize ElementWrapper')

    #------------------------------------------------------------
    def FriendlyClassName(self):
        """
        Return the friendly class name for the control

        This differs from the class of the control in some cases.
        Class() is the actual 'Registered' window class of the control
        while FriendlyClassName() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if self._elementInfo.controlType not in pywinauto_control_types.keys():
            return self._elementInfo.controlType
        if pywinauto_control_types[self._elementInfo.controlType] is None:
            return self._elementInfo.controlType
        return pywinauto_control_types[self._elementInfo.controlType]

    #------------------------------------------------------------
    def Class(self):
        """Return the class name of the elenemt"""
        if not ("class" in self._cache.keys()):
            self._cache['class'] = self._elementInfo.className
        return self._cache['class']

    #------------------------------------------------------------
    def WindowText(self):
        """
        Window text of the element

        Quite  a few contorls have other text that is visible, for example
        Edit controls usually have an empty string for WindowText but still
        have text displayed in the edit window.
        """
        return self._elementInfo.windowText

    #------------------------------------------------------------
    def Style(self):
        pass

    #------------------------------------------------------------
    def ExStyle(self):
        pass

    #------------------------------------------------------------
    def ControlID(self):
        pass

    #------------------------------------------------------------
    def UserData(self):
        pass

    #------------------------------------------------------------
    def ContextHelpID(self):
        pass

    #------------------------------------------------------------
    def IsActive(self):
        pass

    #------------------------------------------------------------
    def IsUnicode(self):
        pass

    #------------------------------------------------------------
    def IsVisible(self):
        """
        Whether the element is visible or not
        """
        return self._elementInfo.visible

    #------------------------------------------------------------
    def IsEnabled(self):
        pass

    #------------------------------------------------------------
    def Rectangle(self):
        """
        Return the rectangle of window

        The rectangle is the rectangle of the element on the screen,
        coordinates are given from the top left of the screen.

        This method returns a RECT structure, Which has attributes - top,
        left, right, bottom. and has methods width() and height().
        See win32structures.RECT for more information.
        """
        return self._elementInfo.rectangle

    #------------------------------------------------------------
    def ClientRect(self):
        pass

    #------------------------------------------------------------
    def ClientToScreen(self, client_point):
        pass

    #------------------------------------------------------------
    def Font(self):
        pass

    #-----------------------------------------------------------
    def ProcessID(self):
        pass

    #-----------------------------------------------------------
    def HasStyle(self, style):
        pass

    #-----------------------------------------------------------
    def HasExStyle(self, exstyle):
        pass

    #-----------------------------------------------------------
    def IsDialog(self):
        pass

    #-----------------------------------------------------------
    def Parent(self):
        pass

    #-----------------------------------------------------------
    def TopLevelParent(self):
        pass

    #-----------------------------------------------------------
    def Texts(self):
        """Return the text for each item of this control"

        It is a list of strings for the control. It is frequently over-ridden
        to extract all strings from a control with multiple items.

        It is always a list with one or more strings:

          * First elemtent is the window text of the control
          * Subsequent elements contain the text of any items of the
            control (e.g. items in a listbox/combobox, tabs in a tabcontrol)
        """
        texts = [self.WindowText(), ]
        return texts

    #-----------------------------------------------------------
    def ClientRects(self):
        pass

    #-----------------------------------------------------------
    def Fonts(self):
        pass

    #-----------------------------------------------------------
    def Children(self):
        pass

    #-----------------------------------------------------------
    def ControlCount(self):
        pass

    #-----------------------------------------------------------
    def IsChild(self, parent):
        pass

    #-----------------------------------------------------------
    def SendCommand(self, commandID):
        pass

    #-----------------------------------------------------------
    def PostCommand(self, commandID):
        pass

    #-----------------------------------------------------------
    #def Notify(self, code):

    #-----------------------------------------------------------
    def SendMessage(self, message, wparam = 0 , lparam = 0):
        pass

    #-----------------------------------------------------------
    def SendMessageTimeout(self):
        pass

    #-----------------------------------------------------------
    def PostMessage(self, message, wparam = 0 , lparam = 0):
        pass

    #-----------------------------------------------------------
    #def NotifyMenuSelect(self, menu_id):

    #-----------------------------------------------------------
    def NotifyParent(self, message, controlID = None):
        pass

    #-----------------------------------------------------------
    def GetProperties(self):
        pass

    #-----------------------------------------------------------
    def CaptureAsImage(self, rect = None):
        pass

    #-----------------------------------------------------------
    def __hash__(self):
        pass

    #-----------------------------------------------------------
    def __eq__(self, other):
        pass

    #-----------------------------------------------------------
    def __ne__(self, other):
        pass

    #-----------------------------------------------------------
    def VerifyActionable(self):
        pass

    #-----------------------------------------------------------
    def VerifyEnabled(self):
        pass

    #-----------------------------------------------------------
    def VerifyVisible(self):
        pass

    #-----------------------------------------------------------
    def Click(self):
        pass

    #-----------------------------------------------------------
    def ClickInput(self):
        pass

    #-----------------------------------------------------------
    def CloseClick(self):
        pass

    #-----------------------------------------------------------
    def CloseAltF4(self):
        pass

    #-----------------------------------------------------------
    def DoubleClick(self):
        pass

    #-----------------------------------------------------------
    def DoubleClickInput(self, button = "left", coords = (None, None)):
        pass

    #-----------------------------------------------------------
    def RightClick(self):
        pass

    #-----------------------------------------------------------
    def RightClickInput(self, coords = (None, None)):
        pass

    #-----------------------------------------------------------
    def PressMouse(self, button = "left", coords = (0, 0), pressed = ""):
        pass

    #-----------------------------------------------------------
    def PressMouseInput(self, button = "left", coords = (None, None), pressed = "", absolute = False, key_down = True, key_up = True):
        pass

    #-----------------------------------------------------------
    def ReleaseMouse(self, button = "left", coords = (0, 0), pressed = ""):
        pass

    #-----------------------------------------------------------
    def ReleaseMouseInput(self, button = "left", coords = (None, None), pressed = "", absolute = False, key_down = True, key_up = True):
        pass

    #-----------------------------------------------------------
    def MoveMouse(self, coords = (0, 0), pressed = "", absolute = False):
        pass

    #-----------------------------------------------------------
    def MoveMouseInput(self, coords = (0, 0), pressed = "", absolute = False):
        pass

    #-----------------------------------------------------------
    def DragMouse(self):
        pass

    #-----------------------------------------------------------
    def DragMouseInput(self):
        pass

    #-----------------------------------------------------------
    def WheelMouseInput(self):
        pass

    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        pass

    #-----------------------------------------------------------
    def TypeKeys(self):
        pass

    #-----------------------------------------------------------
    def DebugMessage(self, text):
        pass

    #-----------------------------------------------------------
    def DrawOutline(self):
        pass

    #-----------------------------------------------------------
    def SetTransparency(self, alpha = 120):
        pass

    #-----------------------------------------------------------
    def PopupWindow(self):
        pass

    #-----------------------------------------------------------
    def Owner(self):
        pass

    #-----------------------------------------------------------
    #def ContextMenuSelect(self, path, x = None, y = None):

    #-----------------------------------------------------------
    def _menu_handle(self):
        pass

    #-----------------------------------------------------------
    def Menu(self):
        pass

    #-----------------------------------------------------------
    def MenuItem(self, path, exact = False):
        pass

    #-----------------------------------------------------------
    def MenuItems(self):
        pass

    #-----------------------------------------------------------
    #def MenuClick(self, path):

    #-----------------------------------------------------------
    def MenuSelect(self, path, exact = False, ):
        pass

    #-----------------------------------------------------------
    def MoveWindow(self):
        pass

    #-----------------------------------------------------------
    def Close(self, wait_time = 0):
        pass

    #-----------------------------------------------------------
    def Maximize(self):
        pass

    #-----------------------------------------------------------
    def Minimize(self):
        pass

    #-----------------------------------------------------------
    def Restore(self):
        pass

    #-----------------------------------------------------------
    def GetShowState(self):
        pass

    #-----------------------------------------------------------
    def GetActive(self):
        pass

    #-----------------------------------------------------------
    def GetFocus(self):
        pass

    #-----------------------------------------------------------
    def SetFocus(self):
        pass

    #-----------------------------------------------------------
    def SetApplicationData(self, appdata):
        pass

    #-----------------------------------------------------------
    def Scroll(self, direction, amount, count = 1, retry_interval = None):
        pass

    #-----------------------------------------------------------
    def GetToolbar(self):
        """Get the first child toolbar if it exists"""

        for child in self.Children():
            if child.__class__.__name__ == 'ToolbarWrapper':
                return child

        return None


#====================================================================
def _perform_click_input():
    pass

#====================================================================
def _perform_click():
    pass

"""
_mouse_flags = {
    "left": win32defines.MK_LBUTTON,
    "right": win32defines.MK_RBUTTON,
    "middle": win32defines.MK_MBUTTON,
    "shift": win32defines.MK_SHIFT,
    "control": win32defines.MK_CONTROL,
}
"""

#====================================================================
def _calc_flags_and_coords(pressed, coords):
    pass

#====================================================================
class _dummy_control(dict):
    "A subclass of dict so that we can assign attributes"
    pass

#====================================================================
def GetDialogPropsFromHandle(hwnd):
    pass
