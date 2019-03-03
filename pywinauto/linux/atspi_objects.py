import ctypes
import subprocess
import six
from ctypes import Structure, c_char_p, c_int, c_bool, POINTER, c_uint32, c_short, c_double

from ..backend import Singleton


class CtypesEnum(object):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class RECT(Structure):

    """Wrap the RECT structure and add extra functionality"""

    _fields_ = [
        ('left', c_int),
        ('top', c_int),
        ('right', c_int),
        ('bottom', c_int),
    ]

    # ----------------------------------------------------------------
    def __init__(self, otherRect_or_left = 0, top = 0, right = 0, bottom = 0):
        """Provide a constructor for RECT structures

        A RECT can be constructed by:
        - Another RECT (each value will be copied)
        - Values for left, top, right and bottom

        e.g. my_rect = RECT(otherRect)
        or   my_rect = RECT(10, 20, 34, 100)
        """
        if isinstance(otherRect_or_left, RECT):
            self.left = otherRect_or_left.left
            self.right = otherRect_or_left.right
            self.top = otherRect_or_left.top
            self.bottom = otherRect_or_left.bottom
        elif isinstance(otherRect_or_left, AtspiRect):
            self.left = otherRect_or_left.x
            self.right = otherRect_or_left.x + otherRect_or_left.width
            self.top = otherRect_or_left.y
            self.bottom = otherRect_or_left.y + otherRect_or_left.height
        else:
            #if not isinstance(otherRect_or_left, (int, long)):
            #    print type(self), type(otherRect_or_left), otherRect_or_left
            self.left = otherRect_or_left
            self.right = right
            self.top = top
            self.bottom = bottom


#    # ----------------------------------------------------------------
#    def __eq__(self, otherRect):
#        "return true if the two rectangles have the same coordinates"
#
#        try:
#            return \
#                self.left == otherRect.left and \
#                self.top == otherRect.top and \
#                self.right == otherRect.right and \
#                self.bottom == otherRect.bottom
#        except AttributeError:
#            return False

    # ----------------------------------------------------------------
    def __str__(self):
        """Return a string representation of the RECT"""
        return "(L%d, T%d, R%d, B%d)" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __repr__(self):
        """Return some representation of the RECT"""
        return "<RECT L%d, T%d, R%d, B%d>" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __sub__(self, other):
        """Return a new rectangle which is offset from the one passed in"""
        newRect = RECT()

        newRect.left = self.left - other.left
        newRect.right = self.right - other.left

        newRect.top = self.top - other.top
        newRect.bottom = self.bottom - other.top

        return newRect

    # ----------------------------------------------------------------
    def __add__(self, other):
        """Allow two rects to be added using +"""
        newRect = RECT()

        newRect.left = self.left + other.left
        newRect.right = self.right + other.left

        newRect.top = self.top + other.top
        newRect.bottom = self.bottom + other.top

        return newRect

    # ----------------------------------------------------------------
    def width(self):
        """Return the width of the  rect"""
        return self.right - self.left

    # ----------------------------------------------------------------
    def height(self):
        """Return the height of the rect"""
        return self.bottom - self.top

    # ----------------------------------------------------------------
    def mid_point(self):
        """Return a POINT structure representing the mid point"""
        pt = AtspiPoint()
        pt.x = self.left + int(float(self.width())/2.)
        pt.y = self.top + int(float(self.height())/2.)
        return pt


class _AtspiCoordType(CtypesEnum):
    ATSPI_COORD_TYPE_SCREEN = 0
    ATSPI_COORD_TYPE_WINDOW = 1


class _AtspiComponentLayer(CtypesEnum):
    ATSPI_LAYER_INVALID = 0
    ATSPI_LAYER_BACKGROUND = 1
    ATSPI_LAYER_CANVAS = 2
    ATSPI_LAYER_WIDGET = 3
    ATSPI_LAYER_MDI = 4
    ATSPI_LAYER_POPUP = 5
    ATSPI_LAYER_OVERLAY = 6
    ATSPI_LAYER_WINDOW = 7
    ATSPI_LAYER_LAST_DEFINED = 8


class _AtspiScrollType(CtypesEnum):
    ATSPI_SCROLL_TOP_LEFT = 0
    ATSPI_SCROLL_BOTTOM_RIGHT = 1
    ATSPI_SCROLL_TOP_EDGE = 2
    ATSPI_SCROLL_BOTTOM_EDGE = 3
    ATSPI_SCROLL_LEFT_EDGE = 4
    ATSPI_SCROLL_RIGHT_EDGE = 5
    ATSPI_SCROLL_ANYWHERE = 6


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


class _AtspiAccessible (Structure):
    pass


class _AtspiComponent (Structure):
    pass


class _GError (Structure):
    pass

"""
AtspiRole: 
https://github.com/GNOME/at-spi2-core/blob/77313dabdc76ebd012d003e253a79596e3acc72d/atspi/atspi-constants.h#L1371
"""
known_control_types = [
    "Invalid",
    "Accelerator_label",
    "Alert",
    "Animation",
    "Arrow",
    "Calendar",
    "Canvas",
    "Check_box",
    "Check_menu_item",
    "Color_chooser",
    "Column_header",
    "Combo_box",
    "Date_editor",
    "Desktop_icon",
    "Desktop_frame",
    "Dial",
    "Dialog",
    "Directory_pane",
    "Drawing_area",
    "File_chooser",
    "Filler",
    "Focus_traversable",
    "Font_chooser",
    "Frame",
    "Glass_pane",
    "Html_container",
    "Icon",
    "Image",
    "Internal_frame",
    "Label",
    "Layered_pane",
    "List",
    "List_item",
    "Menu",
    "Menu_bar",
    "Menu_item",
    "Option_pane",
    "Page_tab",
    "Page_tab_list",
    "Panel",
    "Password_text",
    "Popup_menu",
    "Progress_bar",
    "Push_button",
    "Radio_button",
    "Radio_menu_item",
    "Root_pane",
    "Row_header",
    "Scroll_bar",
    "Scroll_pane",
    "Separator",
    "Slider",
    "Spin_button",
    "Split_pane",
    "Status_bar",
    "Table",
    "Table_cell",
    "Table_column_header",
    "Table_row_header",
    "Tearoff_menu_item",
    "Terminal",
    "Text",
    "Toggle_button",
    "Tool_bar",
    "Tool_tip",
    "Tree",
    "Tree_table",
    "Unknown",
    "Viewport",
    "Window",
    "Extended",
    "Header",
    "Footer",
    "Paragraph",
    "Ruler",
    "Application",
    "Autocomplete",
    "Editbar",
    "Embedded",
    "Entry",
    "Chart",
    "Caption",
    "Document_frame",
    "Heading",
    "Page",
    "Section",
    "Redundant_object",
    "Form",
    "Link",
    "Input_method_window",
    "Table_row",
    "Tree_item",
    "Document_spreadsheet",
    "Document_presentation",
    "Document_text",
    "Document_web",
    "Document_email",
    "Comment",
    "List_box",
    "Grouping",
    "Image_map",
    "Notification",
    "Info_bar",
    "Level_bar",
    "Title_bar",
    "Block_quote",
    "Audio",
    "Video",
    "Definition",
    "Article",
    "Landmark",
    "Log",
    "Marquee",
    "Math",
    "Rating",
    "Timer",
    "Static",
    "Math_fraction",
    "Math_root",
    "Subscript",
    "Superscript",
    "Description_list",
    "Description_term",
    "Description_value",
    "Footnote",
    "Last_defined",
]

@six.add_metaclass(Singleton)
class IATSPI(object):
    """ Python wrapper around C functions from atspi library"""
    LIB = "libatspi"
    DEFAULT_LIB_NAME = "libatspi.so"

    @classmethod
    def __find_library(cls):
        try:
            process = subprocess.Popen(["ldconfig", "-p"], stdout=subprocess.PIPE, universal_newlines=True)
            stdout = process.communicate()
            libraries = stdout[0]
            for lib in libraries.split("\n"):
                if cls.LIB in lib:
                    return lib.split()[0]

        except FileNotFoundError:
            # ldconfig not installed will use default lib name
            return cls.DEFAULT_LIB_NAME

    def __init__(self):
        try:
            self.atspi = ctypes.cdll.LoadLibrary(self.__find_library())

        except Exception:
            message = "atspi library not installed. Please install at-spi2 library or choose another backend"
            raise Exception(message)


class AtspiAccessible(object):
    def __init__(self):
        self.get_desktop = IATSPI().atspi.atspi_get_desktop
        self.get_desktop.argtypes = [c_int]
        self.get_desktop.restype = POINTER(_AtspiAccessible)

        self.get_name = IATSPI().atspi.atspi_accessible_get_name
        self.get_name.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_name.restype = c_char_p

        self.get_id = IATSPI().atspi.atspi_accessible_get_id
        self.get_id.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_id.restype = c_int

        self.get_process_id = IATSPI().atspi.atspi_accessible_get_process_id
        self.get_process_id.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_process_id.restypes = c_int

        self.get_role = IATSPI().atspi.atspi_accessible_get_role
        self.get_role.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_role.restype = c_int

        self.get_role_name = IATSPI().atspi.atspi_accessible_get_role_name
        self.get_role_name.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_role_name.restype = c_char_p

        self.get_description = IATSPI().atspi.atspi_accessible_get_description
        self.get_description.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_description.restype = c_char_p

        self.get_toolkit_name = IATSPI().atspi.atspi_accessible_get_toolkit_name
        self.get_toolkit_name.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_toolkit_name.restype = c_char_p

        self.get_toolkit_version = IATSPI().atspi.atspi_accessible_get_toolkit_version
        self.get_toolkit_version.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_toolkit_version.restype = c_char_p

        self.get_atspi_version = IATSPI().atspi.atspi_accessible_get_atspi_version
        self.get_atspi_version.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_atspi_version.restype = c_char_p

        self.get_parent = IATSPI().atspi.atspi_accessible_get_parent
        self.get_parent.artypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_parent.restype = POINTER(_AtspiAccessible)

        self.get_child_count = IATSPI().atspi.atspi_accessible_get_child_count
        self.get_child_count.argtypes = [POINTER(_AtspiAccessible), POINTER(_GError)]
        self.get_child_count.restype = c_int

        self.get_child_at_index = IATSPI().atspi.atspi_accessible_get_child_at_index
        self.get_child_at_index.argtypes = [POINTER(_AtspiAccessible), c_int, POINTER(_GError)]
        self.get_child_at_index.restype = POINTER(_AtspiAccessible)

        self.get_component = IATSPI().atspi.atspi_accessible_get_component
        self.get_component.argtypes = [POINTER(_AtspiAccessible)]
        self.get_component.restype = POINTER(_AtspiComponent)


class AtspiComponent(object):
    def __init__(self):
        self.contains = IATSPI().atspi.atspi_component_contains
        self.contains.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType, POINTER(_GError)]
        self.contains.restype = c_bool

        self.get_accessible_at_point = IATSPI().atspi.atspi_component_get_accessible_at_point
        self.get_accessible_at_point.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType,
                                                 POINTER(_GError)]
        self.get_accessible_at_point.restype = POINTER(_AtspiAccessible)

        self.get_rectangle = IATSPI().atspi.atspi_component_get_extents
        self.get_rectangle.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(_GError)]
        self.get_rectangle.restype = POINTER(AtspiRect)

        self.get_position = IATSPI().atspi.atspi_component_get_position
        self.get_position.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(_GError)]
        self.get_position.restype = POINTER(AtspiPoint)

        self.get_size = IATSPI().atspi.atspi_component_get_size
        self.get_size.argtypes = [POINTER(_AtspiComponent), POINTER(_GError)]
        self.get_size.restype = POINTER(AtspiPoint)

        self.get_layer = IATSPI().atspi.atspi_component_get_layer
        self.get_layer.argtypes = [POINTER(_AtspiComponent), POINTER(_GError)]
        self.get_layer.restype = _AtspiComponentLayer

        self.get_mdi_z_order = IATSPI().atspi.atspi_component_get_mdi_z_order
        self.get_mdi_z_order.argtypes = [POINTER(_AtspiComponent), POINTER(_GError)]
        self.get_mdi_z_order.restype = c_short

        self.grab_focus = IATSPI().atspi.atspi_component_grab_focus
        self.grab_focus.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(_GError)]
        self.grab_focus.restype = c_bool

        self.get_alpha = IATSPI().atspi.atspi_component_get_alpha
        self.get_alpha.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(_GError)]
        self.get_alpha.restype = c_double

        self.set_extents = IATSPI().atspi.atspi_component_set_extents
        self.set_extents.argtypes = [POINTER(_AtspiComponent), c_int, c_int, c_int, c_int, _AtspiCoordType,
                                     POINTER(_GError)]
        self.set_extents.restype = c_bool

        self.set_position = IATSPI().atspi.atspi_component_set_position
        self.set_position.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType, POINTER(_GError)]
        self.set_position.restype = c_bool

        self.set_size = IATSPI().atspi.atspi_component_set_size
        self.set_size.argtypes = [POINTER(_AtspiComponent), c_int, c_int, POINTER(_GError)]
        self.set_size.restype = c_bool

        self.scroll_to = IATSPI().atspi.atspi_component_scroll_to
        self.scroll_to.argtypes = [POINTER(_AtspiComponent), _AtspiScrollType, POINTER(_GError)]
        self.scroll_to.restype = c_bool

        self.scroll_to_point = IATSPI().atspi.atspi_component_scroll_to_point
        self.scroll_to_point.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, c_int, c_int, POINTER(_GError)]
        self.scroll_to_point.restype = c_bool
