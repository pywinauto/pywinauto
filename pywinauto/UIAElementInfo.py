import comtypes
import comtypes.client

from .six import integer_types
from .handleprops import text, dumpwindow, controlid
from .ElementInfo import ElementInfo
from .win32structures import RECT

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
_iuia = comtypes.CoCreateInstance(
    comtypes.gen.UIAutomationClient.CUIAutomation().IPersist_GetClassID(),
    interface=comtypes.gen.UIAutomationClient.IUIAutomation,
    clsctx=comtypes.CLSCTX_INPROC_SERVER
)

_trueCondition = _iuia.CreateTrueCondition()

_treeScope = {
    'ancestors': _UIA_dll.TreeScope_Ancestors,
    'children': _UIA_dll.TreeScope_Children,
    'descendants': _UIA_dll.TreeScope_Descendants,
    'element': _UIA_dll.TreeScope_Element,
    'parent': _UIA_dll.TreeScope_Parent,
    'subtree': _UIA_dll.TreeScope_Subtree
}

_patternId = {
    'textPattern': _UIA_dll.UIA_TextPatternId
}

"""
Possible properties:

CurrentAcceleratorKey
CurrentAccessKey
CurrentAriaProperties
CurrentAriaRole
CurrentControllerFor
CurrentCulture
CurrentDescribedBy
CurrentFlowsTo
CurrentHelpText
CurrentIsContentElement
CurrentIsControlElement
CurrentIsDataValidForForm
CurrentIsPassword
CurrentIsRequiredForForm
CurrentItemStatus
CurrentItemType
CurrentLabeledBy
CurrentLocalizedControlType
CurrentOrientation
CurrentProviderDescription
"""

class UIAElementInfo(ElementInfo):
    "UI element wrapper for IUIAutomation API"

    def __init__(self, handle_or_elem = None):
        """
        Create instane of UIAElementInfo from a handle (int or long)
        or from an IUIAutomationElement.
        If handle_or_elem is None create instanse for UI root element
        """
        if handle_or_elem is not None:
            if isinstance(handle_or_elem, integer_types):
                # Create instane of UIAElementInfo from a handle
                self._element = _iuia.ElementFromHandle(handle_or_elem)
            elif isinstance(handle_or_elem, comtypes.gen.UIAutomationClient.IUIAutomationElement):
                self._element = handle_or_elem
            else:
                raise TypeError("UIAElementInfo object can be initialized with integer or IUIAutomationElement \
                                instance only!")
        else:
            self._element = _iuia.GetRootElement()            

    @property
    def element(self):
        "Return AutomationElement object"
        return self._element

    @property
    def automationId(self):
        "Return AutomationId of element"
        return self._element.CurrentAutomationId

    @property
    def controlId(self):
        "Return ControlId of element if it has handle"
        if (self.handle):
            return controlid(self.handle)
        else:
            return None;

    @property
    def processId(self):
        "Return ProcessId of element"
        return self._element.CurrentProcessId

    @property
    def frameworkId(self):
        "Return FrameworkId of element"
        return self._element.CurrentFrameworkId

    @property
    def name(self):
        "Return name of element"        
        return self._element.CurrentName

    @property
    def className(self):
        "Return class name of element"
        return self._element.CurrentClassName

    @property
    def controlType(self):
        "Return control type of element"
        return self._element.CurrentControlType

    @property
    def handle(self):
        "Return handle of element"
        return self._element.CurrentNativeWindowHandle

    @property
    def parent(self):
        "Return parent of element"
        parent_elem = _iuia.ControlViewWalker.GetParentElement(self._element)
        if parent_elem:
            return UIAElementInfo(parent_elem)
        else:
            return None

    @property
    def children(self):
        "Return list of children for element"
        children = []
        
        childrenArray = self._element.FindAll(_treeScope['children'], _trueCondition)
        for childNumber in range(childrenArray.Length):
            childElement = childrenArray.GetElement(childNumber)
            children.append(UIAElementInfo(childElement))
            
        return children

    @property
    def descendants(self):
        "Return list of children for element"
        descendants = []

        descendantsArray = self._element.FindAll(_treeScope['descendants'], _trueCondition)
        for descendantNumber in range(descendantsArray.Length):
            descendantElement = descendantsArray.GetElement(descendantNumber)
            descendants.append(UIAElementInfo(descendantElement))

        return descendants

    @property
    def visible(self):
        "Check if element is visible"
        return bool(not self._element.CurrentIsOffscreen)

    @property
    def enabled(self):
        "Check if element is enabled"
        return bool(self._element.CurrentIsEnabled)

    @property
    def rectangle(self):
        "Return rectangle of element"
        bound_rect = self._element.CurrentBoundingRectangle
        rect = RECT()
        rect.left = bound_rect.left
        rect.top = bound_rect.top
        rect.right = bound_rect.right
        rect.bottom = bound_rect.bottom
        return rect

    def dumpWindow(self):
        "Dump a window to a set of properties"
        return dumpwindow(self.handle)

    @property
    def richText(self):
        "Return richText of element"
        if not self.className:
            return self.name
        try:
            pattern = self._element.GetCurrentPattern(_UIA_dll.UIA_TextPatternId).QueryInterface(
                comtypes.gen.UIAutomationClient.IUIAutomationTextPattern)
            return pattern.DocumentRange.GetText(-1)
        except Exception:
            return self.name # TODO: probably we should raise an exception here

    def _getTextFromHandle(self, handle):
        return text(self.handle)

    def _getTextFromElementViaTextPattern(self, element):
        supportedPatterns = _iuia.PollForPotentialSupportedPatterns(element)[0]
        if _patternId['textPattern'] in supportedPatterns:
            textpattern = element.GetCurrentPatternAs(_patternId['textPattern'], "32eba289-3583-42c9-9c59-3b6d9a1e9b6a")
        else:
            return ''
            raise NotImplementedError()
            
        return textPattern.DocumentRange.GetText()

    def __eq__(self, other):
        "Check if 2 UIAElementInfo objects describe 1 actual element"
        if not isinstance(other, UIAElementInfo):
            return False;
        return self.handle == other.handle and self.className == other.className and self.name == other.name and \
               self.processId == other.processId and self.automationId == other.automationId and \
               self.frameworkId == other.frameworkId and self.controlType == other.controlType
