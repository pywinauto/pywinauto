from . import handleprops
from .ElementInfo import ElementInfo

class NativeElementInfo(ElementInfo):
    "Wrapper for window handler"
    def __init__(self, handle):
        self._cache = {}
        self._handle = handle

    @property
    def handle(self):
        "Return the handle of the window"
        return self._handle

    @property
    def richText(self):
        "Return the text of the window"
        if not "richText" in self._cache.keys():
            self._cache["richText"] = handleprops.text(self._handle)
        return self._cache["richText"]

    name = richText

    @property
    def controlId(self):
        "Return the ID of the window"
        if not "controlId" in self._cache.keys():
            self._cache["controlId"] = handleprops.controlid(self._handle)
        return self._cache["controlId"]

    @property
    def processId(self):
        "Return the ID of process that controls this window"
        if not "processId" in self._cache.keys():
            self._cache["processId"] = handleprops.processid(self._handle)
        return self._cache["processId"]

    @property
    def className(self):
        "Return the class name of the window"
        if not "className" in self._cache.keys():
            self._cache["className"] = handleprops.classname(self._handle)
        return self._cache["className"]

    @property
    def enabled(self):
        "Return True if the window is enabled"
        if not "enabled" in self._cache.keys():
            self._cache["enabled"] = handleprops.isenabled(self._handle)
        return self._cache["enabled"]

    @property
    def visible(self):
        "Return True if the window is visible"
        if not "visible" in self._cache.keys():
            self._cache["visible"] = handleprops.isvisible(self._handle)
        return self._cache["visible"]

    @property
    def parent(self):
        "Return the parent of the window"
        if not "parent" in self._cache.keys():
            self._cache["parent"] = handleprops.parent(self._handle)
        return self._cache["parent"]

    @property
    def children(self):
        "Return a list of children of the window"
        child_handles = handleprops.children(self._handle)
        return [NativewindowInfo(ch) for ch in child_handles]

    @property
    def descendants(self):
        "Return descendants of the window"
        child_handles = handleprops.children(self._handle)
        return [NativewindowInfo(ch) for ch in child_handles]

    def dumpWindow(self):
        "Dump a window to a set of properties"
        return handleprops.dumpwindow(self._handle)
