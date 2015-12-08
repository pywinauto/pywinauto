from __future__ import unicode_literals
from __future__ import print_function

#region IMPORTS
#import sys
import time
import re
import ctypes
#import win32api
#import win32gui
#import win32con
#import pywintypes # TODO: get rid of pywintypes because it's not compatible with Python 3.5
import locale

from .. import SendKeysCtypes as SendKeys
from .. import six
from .. import win32defines, win32structures, win32functions
from ..timings import Timings
from ..actionlogger import ActionLogger

import comtypes
import comtypes.client

from .HwndWrapper import _MetaWrapper, HwndWrapper, _perform_click_input
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
class ElementNotEnabled(RuntimeError):
    "Raised when an element is not enabled"
    pass

#=========================================================================
class ElementNotVisible(RuntimeError):
    "Raised when an element is not visible"
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

            self._as_parameter_ = self._elementInfo.handle

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
        if self._elementInfo.controlType not in _known_control_types.keys():
            return str(self._elementInfo.controlType)
        ControlType = _known_control_types[self._elementInfo.controlType]
        if ControlType not in pywinauto_control_types.keys():
            return ControlType
        if pywinauto_control_types[ControlType] is None:
            return ControlType
        return pywinauto_control_types[ControlType]

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
        return self._elementInfo.richText

    #------------------------------------------------------------
    def Style(self):
        pass

    #------------------------------------------------------------
    def ExStyle(self):
        pass

    #------------------------------------------------------------
    def ControlID(self):
        """
        Return the ID of the element

        Only controls have a valid ID - dialogs usually have no ID assigned.

        The ID usually identified the control in the window - but there can
        be duplicate ID's for example lables in a dialog may have duplicate
        ID's.
        """
        return self._elementInfo.controlId

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

        Checks that both the Top Level Parent (probably dialog) that
        owns this element and the element itself are both visible.

        If you want to wait for an element to become visible (or wait
        for it to become hidden) use ``Application.Wait('visible')`` or
        ``Application.WaitNot('visible')``.

        If you want to raise an exception immediately if an element is
        not visible then you can use the ElementWrapper.VerifyVisible().
        ElementWrapper.VerifyActionable() raises if the window is not both
        visible and enabled.
        """
        return self._elementInfo.visible# and self.TopLevelParent()._elementInfo.visible

    #------------------------------------------------------------
    def IsEnabled(self):
        """
        Whether the element is enabled or not

        Checks that both the Top Level Parent (probably dialog) that
        owns this element and the element itself are both enabled.

        If you want to wait for an element to become enabled (or wait
        for it to become disabled) use ``Application.Wait('visible')`` or
        ``Application.WaitNot('visible')``.

        If you want to raise an exception immediately if an element is
        not enabled then you can use the ElementWrapper.VerifyEnabled().
        ElementWrapper.VerifyReady() raises if the window is not both
        visible and enabled.
        """
        return self._elementInfo.enabled# and self.TopLevelParent()._elementInfo.enabled

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
        "Maps point from client to screen coordinates"
        rect = self.Rectangle()
        if isinstance(client_point, win32structures.POINT):
            return (client_point.x + rect.left, client_point.y + rect.top)
        else:
            return (client_point[0] + rect.left, client_point[1] + rect.top)

        #point = win32structures.POINT()
        #if isinstance(client_point, win32structures.POINT):
        #    point.x = client_point.x
        #    point.y = client_point.y
        #else:
        #    point.x = client_point[0]
        #    point.y = client_point[1]
        #win32functions.ClientToScreen(self, ctypes.byref(point))

        # return tuple in any case because
        # coords param is always expected to be tuple
        #return point.x, point.y

    #------------------------------------------------------------
    def Font(self):
        pass

    #-----------------------------------------------------------
    def ProcessID(self):
        "Return the ID of process that owns this window"
        return self._elementInfo.processId

    #-----------------------------------------------------------
    def HasStyle(self, style):
        pass

    #-----------------------------------------------------------
    def HasExStyle(self, exstyle):
        pass

    #-----------------------------------------------------------
    def IsDialog(self):
        "Return true if the control is a top level window"
        if not ("isdialog" in self._cache.keys()):
            if self.Parent():
                self._cache['isdialog'] = (self == self.TopLevelParent())
            else:
                self._cache['isdialog'] = False

        return self._cache['isdialog']

    #-----------------------------------------------------------
    def Parent(self):
        """
        Return the parent of this element

        Note that the parent of a control is not necesarily a dialog or
        other main window. A group box may be the parent of some radio
        buttons for example.

        To get the main (or top level) window then use
        ElementWrapper.TopLevelParent().
        """
        if not ("parent" in self._cache.keys()):
            parent_elem = self._elementInfo.parent

            if parent_elem:
                self._cache["parent"] = ElementWrapper(parent_elem)
            else:
                self._cache["parent"] = None

        return self._cache["parent"]

    #-----------------------------------------------------------
    def TopLevelParent(self):
        """
        Return the top level window of this control

        The TopLevel parent is different from the parent in that the Parent
        is the element that owns this element - but it may not be a dialog/main
        window. For example most Comboboxes have an Edit. The ComboBox is the
        parent of the Edit control.

        This will always return a valid window element (if the control has
        no top level parent then the control itself is returned - as it is
        a top level window already!)
        """
        if not ("top_level_parent" in self._cache.keys()):
            if self.Parent() == ElementWrapper(UIAElementInfo(_iuia.getRootElement())):
                self._cache["top_level_parent"] = self
            else:
                return self.Parent().TopLevelParent()

        return self._cache["top_level_parent"]

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
        """
        Return the children of this element as a list

        It returns a list of ElementWrapper (or subclass) instances, it
        returns an empty list if there are no children.
        """
        child_elements = self._elementInfo.children
        return [ElementWrapper(elementInfo) for elementInfo in child_elements]

    #-----------------------------------------------------------
    def Descendants(self):
        """
        Return the descendants of this element as a list

        It returns a list of ElementWrapper (or subclass) instances, it
        returns an empty list if there are no descendants.
        """
        desc_elements = self._elementInfo.descendants
        return [ElementWrapper(elementInfo) for elementInfo in desc_elements]

    #-----------------------------------------------------------
    def ControlCount(self):
        "Return the number of children of this control"
        return len(self._elementInfo.children)

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
    def Notify(self, code):
        pass

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
    def NotifyMenuSelect(self, menu_id):
        pass

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
        "Returns true if 2 ElementWrapper's describe 1 actual element"
        if isinstance(other, ElementWrapper):
            return self._elementInfo == other._elementInfo
        else:
            return False

    #-----------------------------------------------------------
    def __ne__(self, other):
        "Returns False if the elements described by 2 ElementWrapper's are different"
        return not self == other

    #-----------------------------------------------------------
    def VerifyActionable(self):
        """
        Verify that the element is both visible and enabled

        Raise either ElementNotEnalbed or ElementNotVisible if not
        enabled or visible respectively.
        """
        win32functions.WaitGuiThreadIdle(self)
        self.VerifyVisible()
        self.VerifyEnabled()

    #-----------------------------------------------------------
    def VerifyEnabled(self):
        """
        Verify that the element is enabled

        Check first if the element's parent is enabled (skip if no parent),
        then check if element itself is enabled.
        """

        # Check if the element and it's parent are enabled
        if not self.IsEnabled():
            raise ElementNotEnabled()

    #-----------------------------------------------------------
    def VerifyVisible(self):
        """
        Verify that the element is visible

        Check first if the element's parent is visible. (skip if no parent),
        then check if element itself is visible.
        """

        # check if the control and it's parent are visible
        if not self.IsVisible():
            raise ElementNotVisible()

    #-----------------------------------------------------------
    def Click(self):
        pass

    #-----------------------------------------------------------
    def ClickInput(
        self,
        button = "left",
        coords = (None, None),
        double = False,
        wheel_dist = 0,
        use_log = True,
        pressed = "",
        absolute = False
    ):
        """
        Click at the specified coordinates

        * **button** The mouse button to click. One of 'left', 'right',
          'middle' or 'x' (Default: 'left')
        * **coords** The coordinates to click at.(Default: center of control)
        * **double** Whether to perform a double click or not (Default: False)
        * **wheel_dist** The distance to move the mouse wheel (default: 0)

        NOTES:
           This is different from Click in that it requires the control to
           be visible on the screen but performs a more realistic 'click'
           simulation.

           This method is also vulnerable if the mouse is moved by the user
           as that could easily move the mouse off the control before the
           Click has finished.
        """
        _perform_click_input(
            self, button, coords, double, wheel_dist = wheel_dist, use_log = use_log, pressed = pressed,
            absolute = absolute
        )

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
        "Double click at the specified coordinates"
        _perform_click_input(self, button, coords, double = True)

    #-----------------------------------------------------------
    def RightClick(self):
        pass

    #-----------------------------------------------------------
    def RightClickInput(self, coords = (None, None)):
        "Right click at the specified coords"
        _perform_click_input(self, 'right', coords)

    #-----------------------------------------------------------
    def PressMouse(self, button = "left", coords = (0, 0), pressed = ""):
        pass

    #-----------------------------------------------------------
    def PressMouseInput(
            self,
            button = "left",
            coords = (None, None),
            pressed = "",
            absolute = False,
            key_down = True,
            key_up = True
    ):
        "Press a mouse button using SendInput"
        _perform_click_input(
            self,
            button,
            coords,
            button_down=True,
            button_up=False,
            pressed=pressed,
            absolute=absolute,
            key_down=key_down,
            key_up=key_up
        )

    #-----------------------------------------------------------
    def ReleaseMouse(self, button = "left", coords = (0, 0), pressed = ""):
        pass

    #-----------------------------------------------------------
    def ReleaseMouseInput(
            self,
            button = "left",
            coords = (None, None),
            pressed = "",
            absolute = False,
            key_down = True,
            key_up = True
    ):
        "Release the mouse button"
        _perform_click_input(
            self,
            button,
            coords,
            button_down=False,
            button_up=True,
            pressed=pressed,
            absolute=absolute,
            key_down=key_down,
            key_up=key_up
        )

    #-----------------------------------------------------------
    def MoveMouse(self, coords = (0, 0), pressed = "", absolute = False):
        pass

    #-----------------------------------------------------------
    def MoveMouseInput(self, coords = (0, 0), pressed = "", absolute = False):
        "Move the mouse"
        if not absolute:
            self.actions.log('Moving mouse to relative (client) coordinates ' + str(coords).replace('\n', ', '))

        _perform_click_input(self, button='move', coords=coords, absolute=absolute, pressed=pressed)

        win32functions.WaitGuiThreadIdle(self)
        return self

    #-----------------------------------------------------------
    def DragMouse(self):
        pass

    #-----------------------------------------------------------
    def DragMouseInput(self):
        pass

    #-----------------------------------------------------------
    def WheelMouseInput(self, coords = (None, None), wheel_dist = 1, pressed = ""):
        "Do mouse wheel"
        _perform_click_input(self, button='wheel', coords=coords, wheel_dist = 120 * wheel_dist, pressed=pressed)
        return self

    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        pass

    #-----------------------------------------------------------
    def TypeKeys(
        self,
        keys,
        pause = None,
        with_spaces = False,
        with_tabs = False,
        with_newlines = False,
        turn_off_numlock = True,
        set_foreground = True):
        """
        Type keys to the element using SendKeys

        This uses the SendKeys python module from
        http://www.rutherfurd.net/python/sendkeys/ .This is the best place
        to find documentation on what to use for the **keys**
        """
        self.VerifyActionable()

        if pause is None:
            pause = Timings.after_sendkeys_key_wait

        if set_foreground:
            self.SetFocus()

        if isinstance(keys, six.text_type):
            aligned_keys = keys
        elif isinstance(keys, six.binary_type):
            aligned_keys = keys.decode(locale.getpreferredencoding())
        else:
            # convert a non-string input
            aligned_keys = six.text_type(keys)

        # Play the keys to the active window
        SendKeys.SendKeys(
            aligned_keys + '\n',
            pause,
            with_spaces,
            with_tabs,
            with_newlines,
            turn_off_numlock)

        win32functions.WaitGuiThreadIdle(self)
        self.actions.log('Typed text to the ' + self.FriendlyClassName() + ': ' + aligned_keys)
        return self

        # TODO: select all text from edit field before typing new text
        """
        base_pattern = self._elementInfo._element.GetCurrentPattern(_UIA_dll.UIA_TextPatternId)
        if base_pattern:
            pattern = base_pattern.QueryInterface(TextPattern)
            pattern.DocumentRange.Select()
        """

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
        "Set the focus to this element"
        try:
            self._elementInfo._element.SetFocus()
        except comtypes.COMError as exc:
            pass

        return self

    #-----------------------------------------------------------
    def SetApplicationData(self, appdata):
        pass

    #-----------------------------------------------------------
    def Scroll(self, direction, amount, count = 1, retry_interval = None):
        pass

    #-----------------------------------------------------------
    def GetToolbar(self):
        pass

#====================================================================

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
