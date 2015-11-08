import comtypes
import comtypes.client

from .handleprops import text, dumpwindow
from .elementInfo import ElementInfo

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
_iuia = comtypes.CoCreateInstance(
    comtypes.gen.UIAutomationClient.CUIAutomation._reg_clsid_,
    interface=comtypes.gen.UIAutomationClient.IUIAutomation,
    clsctx=comtypes.CLSCTX_INPROC_SERVER
)

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

class UIAElementInfo(ElementInfo):
    "UI element wrapper for IUIAutomation API"

    def __init__(self, handle = None):
        """Create instane of UIAElementInfo from handle.
        If handle is None create instanse for UI root element"""        
        if handle is not None:
            self._element = _iuia.ElementFromHandle(handle)
        else:
            self._element = _iuia.GetRootElement()            

    @classmethod
    def fromElement(cls, element):
        "Create instance of UIAElementInfo from IUIAutomationElement"
        elementInfo = cls(None)
        elementInfo._element = element
        return elementInfo

    @property
    def automationId(self):
        "Return AutomationId of element"
        return self._element.CurrentAutomationId
    controlId = automationId

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
    def windowText(self):
        "Return windowText of element"
        framework = self.frameworkId
        if framework == "Win32":
            return self._getTextFromHandle(self.handle)
        elif framework == "WinForm":
            return self._getTextFromHandle(self.handle)
        
        return self._getTextFromElementViaTextPattern(self._element)

    @property
    def ControlType(self):
        "Return control type of element"
        return self._element.CurrentControlType

    @property
    def handle(self):
        "Return handle of element"
        return self._element.CurrentNativeWindowHandle

    @handle.setter
    def handle(self, handle):
        assert handle
        self._element = _iuia.ElementFromHandle(handle)

    @property
    def parent(self):
        "Return parent of element"
        return UIAElementInfo(_iuia.ControlViewWalker.GetParentElement(self._element).CurrentNativeWindowHandle)

    def children(self):
        "Return list of children for element"
        children = []
        
        trueCondition = _iuia.CreateTrueCondition()
        childrenArray = self._element.FindAll(_treeScope['children'], trueCondition)
        for childNumber in range(childrenArray.Length):
            childElement = childrenArray.GetElement(childNumber)
            if childElement.CurrentNativeWindowHandle is not None:
                children.append(UIAElementInfo(childElement.CurrentNativeWindowHandle))
            else:
                children.append(UIAElementInfo.fromElement(childElement))
            
        return children

    @property
    def descendants(self):
        "Return list of children for element"
        descendants = []

        trueCondition = _iuia.CreateTrueCondition()
        descendantsArray = self._element.FindAll(_treeScope['descendants'], trueCondition)
        for descendantNumber in range(descendantsArray.Length):
            descendantElement = descendantsArray.GetElement(descendantNumber)
            if descendantElement.CurrentNativeWindowHandle is not None:
                descendants.append(UIAElementInfo(descendantElement.CurrentNativeWindowHandle))
            else:
                descendants.append(UIAElementInfo.fromElement(descendantElement))

        return descendants

    @property
    def visible(self):
        "Check if element is visible"
        return bool(not self._element.CurrentIsOffscreen and self._element.GetClickablePoint()[1])

    @property
    def enabled(self):
        "Check if element is enabled"
        return bool(self._element.CurrentIsEnabled)

    def dumpWindow(self):
        "Dump a window to a set of properties"
        return dumpwindow(self.handle)

    def _getTextFromHandle(self, handle):
        return text(self.handle)

    def _getTextFromElementViaTextPattern(self, element):
        supportedPatterns = _iuia.PollForPotentialSupportedPatterns(element)[0]
        if _patternId['textPattern'] in supportedPatterns:
            textpattern = element.GetCurrentPatternAs(_patternId['textPattern'], "32eba289-3583-42c9-9c59-3b6d9a1e9b6a")
        else:
            raise NotImplementedError()
            
        return textPattern.DocumentRange.GetText()

    def __eq__(self, other):
        "Check if 2 UIAElementInfo objects describe 1 actual element"
        if not isinstance(other, UIAElementInfo):
            return False;
        return self.handle == other.handle and self.className == other.className and self.name == other.name and \
               self.processId == other.processId and self.controlId == other.controlId and \
               self.frameworkId == other.frameworkId and self.ControlType == other.ControlType