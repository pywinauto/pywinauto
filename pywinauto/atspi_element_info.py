from .atspi_functions import AtspiRect, AtspiCoordType, AtspiFunctions
from .element_info import ElementInfo


class AtspiElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        self.atspi_functions = AtspiFunctions()
        if handle is None:
            self._handle = self.atspi_functions.get_desktop(0, None)
        else:
            self._handle = handle

    def _get_elements(self, root, tree):
        tree.append(root)
        for el in root.children():
            self._get_elements(el, tree)

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def name(self):
        """Return the text of the window"""
        return self.atspi_functions.get_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def control_id(self):
        """Return the ID of the window"""
        return self.atspi_functions.get_id(self._handle, None)

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return self.atspi_functions.get_process_id(self._handle, None)

    @property
    def class_name(self):
        """Return the class name of the element"""
        return self.atspi_functions.get_role_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def parent(self):
        """Return the parent of the element"""
        return AtspiElementInfo(self.atspi_functions.get_parent(self._handle, None))

    def children(self, **kwargs):
        """Return children of the element"""
        len = self.atspi_functions.get_child_count(self._handle, None)
        childrens = []
        for i in range(len):
            childrens.append(self.atspi_functions.get_child_at_index(self._handle, i, None))
        return [AtspiElementInfo(ch) for ch in childrens]

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        tree = []
        for obj in self.children():
            self._get_elements(obj, tree)
        return tree

    @property
    def rectangle(self):
        """Return rectangle of element"""
        component = self.atspi_functions.get_component(self._handle)
        prect = self.atspi_functions.get_rectangle(component, AtspiCoordType.ATSPI_COORD_TYPE_SCREEN, None)
        return prect.contents
