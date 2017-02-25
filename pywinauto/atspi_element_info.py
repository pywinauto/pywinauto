from . import atspi_functions
from .atspi_functions import AtspiRect
from .element_info import ElementInfo


class AtspiElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = atspi_functions.get_desktop(0, None)
        else:
            self._handle = handle

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def name(self):
        """Return the text of the window"""
        return atspi_functions.get_name(self._handle, None)

    @property
    def control_id(self):
        """Return the ID of the window"""
        return atspi_functions.get_id(self._handle, None)

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return atspi_functions.get_process_id(self._handle, None)

    @property
    def class_name(self):
        """Return the class name of the element"""
        return atspi_functions.get_role_name(self._handle, None)

    @property
    def parent(self):
        """Return the parent of the element"""
        return atspi_functions.get_parent(self._handle, None)

    def children(self, **kwargs):
        """Return children of the element"""
        len = atspi_functions.get_child_count(self._handle, None)
        childrens = []
        for i in range(len):
            childrens.append(atspi_functions.get_child_at_index(self._handle, i, None))
        return [AtspiElementInfo(ch) for ch in childrens]

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        raise NotImplementedError()

    @property
    def rectangle(self):
        """Return rectangle of element"""
        component = atspi_functions.get_component(self._handle)
        rect = AtspiRect()
        rect = atspi_functions.get_rectangle(component, 0, None)
        return rect

    def dump_window(self):
        """Dump an element to a set of properties"""
        raise NotImplementedError()
