import comtypes
import comtypes.client

from pywinauto.handleprops import text, dumpwindow
from pywinauto.elementInfo import ElementInfo

_UIA_dll = comtypes.client.GetModule('UIAutomationCore.dll')
_iuia = comtypes.CoCreateInstance(comtypes.gen.UIAutomationClient.CUIAutomation._reg_clsid_, interface=comtypes.gen.UIAutomationClient.IUIAutomation, clsctx=comtypes.CLSCTX_INPROC_SERVER)

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
    
    @property
    def name(self):
        "Return name of element"        
        return self._element.CurrentName
    
    @property
    def windowText(self):
        "Return windowText of element"
        framework = self._element.CurrentFrameworkId
        if framework == "Win32":
            return self._getTextFromHandle(self.handle)
        elif framework == "WinForm":
            return self._getTextFromHandle(self.handle)
        
        return self._getTextFromElementViaTextPattern(self._element)

    @property
    def controlType(self):
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

    @property
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
    def processId(self):
        "Return process id of element"
        return self._element.CurrentProcessId

    @property
    def controlId(self):
        return self._element.CurrentAutomationId

    @property
    def visible(self):
        "Return is element visible"
        return bool(not self._element.CurrentIsOffscreen and self._element.GetClickablePoint()[1])

    @property
    def enabled(self):
        "Return is element enabled"
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
    
