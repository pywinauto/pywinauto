import ctypes
from ctypes import Structure, c_char_p, c_int, POINTER
from enum import IntEnum


class CtypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class AtspiCoordType(CtypesEnum):
    ATSPI_COORD_TYPE_SCREEN = 0
    ATSPI_COORD_TYPE_WINDOW = 1


class AtspiRect (Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
        ('width', c_int),
        ('height', c_int),
    ]


class AtspiPoint (Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
    ]


class AtspiAccessible (Structure):
    pass


class AtspiComponent (Structure):
    pass


class GError (Structure):
    pass

atspi = ctypes.cdll.LoadLibrary("libatspi.so.0")
get_desktop = atspi.atspi_get_desktop
get_desktop.argtypes = [c_int]
get_desktop.restype = POINTER(AtspiAccessible)

get_name = atspi.atspi_accessible_get_name
get_name.argtypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_name.restype = c_char_p

get_id = atspi.atspi_accessible_get_id
get_id.argtypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_id.restype = c_int

get_process_id = atspi.atspi_accessible_get_process_id
get_process_id.argtypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_process_id.restypes = c_int

get_role_name = atspi.atspi_accessible_get_role_name
get_role_name.argtypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_role_name.restype = c_char_p

get_parent = atspi.atspi_accessible_get_parent
get_parent.artypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_parent.restype = POINTER(AtspiAccessible)

get_child_count = atspi.atspi_accessible_get_child_count
get_child_count.argtypes = [POINTER(AtspiAccessible), POINTER(GError)]
get_child_count.restype = c_int

get_child_at_index = atspi.atspi_accessible_get_child_at_index
get_child_at_index.argtypes = [POINTER(AtspiAccessible), c_int, POINTER(GError)]
get_child_at_index.restype = POINTER(AtspiAccessible)

get_position = atspi.atspi_component_get_position
get_position.argtypes = [POINTER(AtspiComponent), AtspiCoordType, POINTER(GError)]
get_position.restype = POINTER(AtspiPoint)

get_size = atspi.atspi_component_get_size
get_size.argtypes = [POINTER(AtspiComponent), POINTER(GError)]
get_size.restype = POINTER(AtspiPoint)

get_rectangle = atspi.atspi_component_get_extents
get_rectangle.argtypes = [POINTER(AtspiComponent), AtspiCoordType, POINTER(GError)]
get_rectangle.restype = POINTER(AtspiRect)

get_component = atspi.atspi_accessible_get_component
get_component.argtypes = [POINTER(AtspiAccessible)]
get_component.restype = POINTER(AtspiComponent)

