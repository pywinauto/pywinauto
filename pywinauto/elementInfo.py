from . import handleprops

class ElementInfo(object):
    "Wrapper for window handler"

    @property
    def handle(self):
        "Return the handle of the window"
        return self._handle

    @handle.setter
    def handle(self, handle):
        assert handle
        self._handle = handle

    @property
    def windowText(self):
        "Return the text of the window"
        return self._windowText

    @windowText.setter
    def windowText(self, windowText):
        self._windowText = windowText

    @property
    def controlId(self):
        "Return the ID of the control"
        return self._controlId

    @property
    def processId(self):
        "Return the ID of process that controls this window"
        return self._processId
    
    @property
    def className(self):
        "Return the class name of the window"
        return self._className

    @property
    def enabled(self):
        "Return True if the window is enabled"
        self._enabled = handleprops.isenabled(self._handle)
        return self._enabled
        
    @property
    def visible(self):
        "Return True if the window is visible"
        self._visible = handleprops.isvisible(self._handle)
        return self._visible
       
    @property
    def parent(self):
        "Return the handle of the parent of the window"
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
    
    def children(self):
        pass

    def dumpWindow(self):
        pass

class NativeElementInfo(ElementInfo):
    def __init__(self, handle):
        self._handle = handle
        self._windowText = handleprops.text(handle)
        self._controlId = handleprops.controlid(handle)
        self._processId = handleprops.processid(handle)
        self._className = handleprops.classname(handle)
        self._enabled = handleprops.isenabled(handle)
        self._visible = handleprops.isvisible(handle)
        self._parent  = handleprops.parent(handle)
        
    def children(self):
        "Return a list of handles to the children of this window"
        child_handles = handleprops.children(self.handle)
        return [NativeElementInfo(ch) for ch in child_handles]

    def dumpWindow(self):
        "Dump a window to a set of properties"
        return handleprops.dumpwindow(self.handle)

