import pyatspi
from .element_info import ElementInfo


class AtpsiElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = pyatspi.Registry.getDesctop(0)
        else:
            self._handle = handle

    @property
    def handle(self):
        """Return the handle of the window"""
        raise NotImplementedError()

    @property
    def rich_text(self):
        """Return the text of the window"""
        raise NotImplementedError()

    @property
    def control_id(self):
        """Return the ID of the window"""
        raise NotImplementedError()

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        raise NotImplementedError()

    @property
    def class_name(self):
        """Return the class name of the element"""
        raise NotImplementedError()

    @property
    def enabled(self):
        """Return True if the element is enabled"""
        raise NotImplementedError()

    @property
    def visible(self):
        """Return True if the element is visible"""
        raise NotImplementedError()

    @property
    def parent(self):
        """Return the parent of the element"""
        raise NotImplementedError()

    def children(self, **kwargs):
        """Return children of the element"""
        raise NotImplementedError()

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        raise NotImplementedError()

    @property
    def rectangle(self):
        """Return rectangle of element"""
        raise NotImplementedError()

    def dump_window(self):
        """Dump an element to a set of properties"""
        raise NotImplementedError()
