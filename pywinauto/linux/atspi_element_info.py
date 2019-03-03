from .atspi_objects import AtspiRect, _AtspiCoordType, AtspiAccessible, RECT, known_control_types, AtspiComponent
from ..element_info import ElementInfo


class AtspiElementInfo(ElementInfo):

    """Wrapper for window handler"""
    atspi_accessible = AtspiAccessible()

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = self.atspi_accessible.get_desktop(0, None)
        else:
            self._handle = handle

    def __get_elements(self, root, tree):
        tree.append(root)
        for el in root.children():
            self.__get_elements(el, tree)

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def name(self):
        """Return the text of the window"""
        return self.atspi_accessible.get_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def control_id(self):
        """Return the ID of the window"""
        return self.atspi_accessible.get_id(self._handle, None)

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return self.atspi_accessible.get_process_id(self._handle, None)

    @property
    def class_name(self):
        """Return the class name of the element"""
        return self.atspi_accessible.get_role_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def control_type(self):
        """Return the class name of the element"""
        role_id = self.atspi_accessible.get_role(self._handle, None)
        return known_control_types[role_id]

    @property
    def parent(self):
        """Return the parent of the element"""
        return AtspiElementInfo(self.atspi_accessible.get_parent(self._handle, None))

    def children(self, **kwargs):
        """Return children of the element"""
        len = self.atspi_accessible.get_child_count(self._handle, None)
        childrens = []
        for i in range(len):
            childrens.append(self.atspi_accessible.get_child_at_index(self._handle, i, None))
        return [AtspiElementInfo(ch) for ch in childrens]

    @property
    def component(self):
        component = self.atspi_accessible.get_component(self._handle)
        return AtspiComponent(component)

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        tree = []
        for obj in self.children():
            self.__get_elements(obj, tree)
        return tree

    def description(self):
        return self.atspi_accessible.get_description(self._handle, None).decode(encoding='UTF-8')

    def framework_id(self):
        return self.atspi_accessible.get_toolkit_version(self._handle, None).decode(encoding='UTF-8')

    def framework_name(self):
        return self.atspi_accessible.get_toolkit_name(self._handle, None).decode(encoding='UTF-8')

    def atspi_version(self):
        return self.atspi_accessible.get_atspi_version(self._handle, None).decode(encoding='UTF-8')

    @property
    def rectangle(self):
        """Return rectangle of element"""
        return self.component.get_rectangle(coord_type="screen")
