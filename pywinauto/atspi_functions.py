import ctypes
from ctypes import c_char_p

atspi = ctypes.cdll.LoadLibrary("libatspi.so")
get_desktop = atspi.atspi_get_desktop
get_name = atspi.atspi_accessible_get_name
get_name.restype = c_char_p
get_id = atspi.atspi_accessible_get_id
get_process_id = atspi.atspi_accessible_get_process_id
get_role_name = atspi.atspi_accessible_get_role_name
get_role_name.restype = c_char_p
get_parent = atspi.atspi_accessible_get_parent
get_child_count = atspi.atspi_accessible_get_child_count
get_child_at_index = atspi.atspi_accessible_get_child_at_index
get_position = atspi.atspi_component_get_position
get_size = atspi.atspi_component_get_size
