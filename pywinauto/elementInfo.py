from . import handleprops

class ElementInfo(object):
    "Wrapper for window handler"

    @property
    def handle(self):
        return self._handle

    @handle.setter
    def handle(self, handle):
        assert handle
        self._handle = handle

    @property
    def windowText(self):
        return self._windowText

    @windowText.setter
    def windowText(self, windowText):
        self._windowText = windowText

    @property
    def controlId(self):
        return self._controlId

    @property
    def processId(self):
        self._processId

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

    def children(self):
        child_handles = handleprops.children(self.handle)
        return [NativeElementInfo(ch) for ch in child_handles]

    def dumpWindow(self):
        return handleprops.dumpwindow(self.handle)

