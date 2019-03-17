import ctypes
import subprocess
import six
from ctypes import Structure, c_char_p, c_int, c_bool, POINTER, c_uint32, c_short, c_double, addressof
from collections import namedtuple

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


class _AtspiStateType(CtypesEnum):
    ATSPI_STATE_INVALID = 0
    ATSPI_STATE_ACTIVE = 1
    ATSPI_STATE_ARMED = 2
    ATSPI_STATE_BUSY = 3
    ATSPI_STATE_CHECKED = 4
    ATSPI_STATE_COLLAPSED = 5
    ATSPI_STATE_DEFUNCT = 6
    ATSPI_STATE_EDITABLE = 7
    ATSPI_STATE_ENABLED = 8
    ATSPI_STATE_EXPANDABLE = 9
    ATSPI_STATE_EXPANDED = 10
    ATSPI_STATE_FOCUSABLE = 11
    ATSPI_STATE_FOCUSED = 12
    ATSPI_STATE_HAS_TOOLTIP = 13
    ATSPI_STATE_HORIZONTAL = 14
    ATSPI_STATE_ICONIFIED = 15
    ATSPI_STATE_MODAL = 16
    ATSPI_STATE_MULTI_LINE = 17
    ATSPI_STATE_MULTISELECTABLE = 18
    ATSPI_STATE_OPAQUE = 19
    ATSPI_STATE_PRESSED = 20
    ATSPI_STATE_RESIZABLE = 21
    ATSPI_STATE_SELECTABLE = 22
    ATSPI_STATE_SELECTED = 23
    ATSPI_STATE_SENSITIVE = 24
    ATSPI_STATE_SHOWING = 25
    ATSPI_STATE_SINGLE_LINE = 26
    ATSPI_STATE_STALE = 27
    ATSPI_STATE_TRANSIENT = 28
    ATSPI_STATE_VERTICAL = 29
    ATSPI_STATE_VISIBLE = 30
    ATSPI_STATE_MANAGES_DESCENDANTS = 31
    ATSPI_STATE_INDETERMINATE = 32
    ATSPI_STATE_REQUIRED = 33
    ATSPI_STATE_TRUNCATED = 34
    ATSPI_STATE_ANIMATED = 35
    ATSPI_STATE_INVALID_ENTRY = 36
    ATSPI_STATE_SUPPORTS_AUTOCOMPLETION = 37
    ATSPI_STATE_SELECTABLE_TEXT = 38
    ATSPI_STATE_IS_DEFAULT = 39
    ATSPI_STATE_VISITED = 40
    ATSPI_STATE_CHECKABLE = 41
    ATSPI_STATE_HAS_POPUP = 42
    ATSPI_STATE_READ_ONLY = 43
    ATSPI_STATE_LAST_DEFINED = 44


class AtspiRect(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
        ('width', c_int),
        ('height', c_int),
    ]


class AtspiPoint(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
    ]


class _AtspiAccessible(Structure):
    pass


class _AtspiComponent(Structure):
    pass


class _AtspiStateSet(Structure):
    pass


class _GError(Structure):
    _fields_ = [
        ('domain', c_uint32),
        ('code', c_int),
        ('message', c_char_p),
    ]

class _GArray(Structure):
    _fields_ = [
        ('data', c_char_p),
        ('len', c_uint32),
    ]


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

    def get_iface_func(self, func_name):
        if hasattr(self.atspi, func_name + "_iface"):
            return getattr(self.atspi, func_name + "_iface")
        elif hasattr(self.atspi, func_name):
            return getattr(self.atspi, func_name)
        else:
            # TODO raise warning or add version check
            return None


class AtspiAccessible(object):
    get_desktop = IATSPI().get_iface_func("atspi_get_desktop")
    get_desktop.argtypes = [c_int]
    get_desktop.restype = POINTER(_AtspiAccessible)

    get_name = IATSPI().get_iface_func("atspi_accessible_get_name")
    get_name.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_name.restype = c_char_p

    get_id = IATSPI().get_iface_func("atspi_accessible_get_id")
    get_id.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_id.restype = c_int

    get_process_id = IATSPI().get_iface_func("atspi_accessible_get_process_id")
    get_process_id.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_process_id.restypes = c_int

    get_role = IATSPI().get_iface_func("atspi_accessible_get_role")
    get_role.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_role.restype = c_int

    get_role_name = IATSPI().get_iface_func("atspi_accessible_get_role_name")
    get_role_name.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_role_name.restype = c_char_p

    get_description = IATSPI().get_iface_func("atspi_accessible_get_description")
    get_description.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_description.restype = c_char_p

    get_toolkit_name = IATSPI().get_iface_func("atspi_accessible_get_toolkit_name")
    get_toolkit_name.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_toolkit_name.restype = c_char_p

    get_toolkit_version = IATSPI().get_iface_func("atspi_accessible_get_toolkit_version")
    get_toolkit_version.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_toolkit_version.restype = c_char_p

    get_atspi_version = IATSPI().get_iface_func("atspi_accessible_get_atspi_version")
    get_atspi_version.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_atspi_version.restype = c_char_p

    get_parent = IATSPI().get_iface_func("atspi_accessible_get_parent")
    get_parent.artypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_parent.restype = POINTER(_AtspiAccessible)

    get_child_count = IATSPI().get_iface_func("atspi_accessible_get_child_count")
    get_child_count.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_child_count.restype = c_int

    get_child_at_index = IATSPI().get_iface_func("atspi_accessible_get_child_at_index")
    get_child_at_index.argtypes = [POINTER(_AtspiAccessible), c_int, POINTER(POINTER(_GError))]
    get_child_at_index.restype = POINTER(_AtspiAccessible)

    get_component = IATSPI().get_iface_func("atspi_accessible_get_component")
    get_component.argtypes = [POINTER(_AtspiAccessible)]
    get_component.restype = POINTER(_AtspiComponent)

    get_state_set = IATSPI().get_iface_func("atspi_accessible_get_state_set")
    get_state_set.argtypes = [POINTER(_AtspiAccessible)]
    get_state_set.restype = POINTER(_AtspiStateSet)


class AtspiComponent(object):
    _contains = IATSPI().get_iface_func("atspi_component_contains")
    _contains.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType, POINTER(POINTER(_GError))]
    _contains.restype = c_bool

    _get_accessible_at_point = IATSPI().get_iface_func("atspi_component_get_accessible_at_point")
    _get_accessible_at_point.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType,
                                         POINTER(POINTER(_GError))]
    _get_accessible_at_point.restype = POINTER(_AtspiAccessible)

    _get_rectangle = IATSPI().get_iface_func("atspi_component_get_extents")
    _get_rectangle.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_rectangle.restype = POINTER(AtspiRect)

    _get_position = IATSPI().get_iface_func("atspi_component_get_position")
    _get_position.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_position.restype = POINTER(AtspiPoint)

    _get_size = IATSPI().get_iface_func("atspi_component_get_size")
    _get_size.argtypes = [POINTER(_AtspiComponent), POINTER(POINTER(_GError))]
    _get_size.restype = POINTER(AtspiPoint)

    _get_layer = IATSPI().get_iface_func("atspi_component_get_layer")
    _get_layer.argtypes = [POINTER(_AtspiComponent), POINTER(POINTER(_GError))]
    _get_layer.restype = _AtspiComponentLayer

    _get_mdi_z_order = IATSPI().get_iface_func("atspi_component_get_mdi_z_order")
    _get_mdi_z_order.argtypes = [POINTER(_AtspiComponent), POINTER(POINTER(_GError))]
    _get_mdi_z_order.restype = c_short

    _grab_focus = IATSPI().get_iface_func("atspi_component_grab_focus")
    _grab_focus.argtypes = [POINTER(_AtspiComponent), POINTER(POINTER(_GError))]
    _grab_focus.restype = c_bool

    _get_alpha = IATSPI().get_iface_func("atspi_component_get_alpha")
    _get_alpha.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_alpha.restype = c_double

    _set_extents = IATSPI().get_iface_func("atspi_component_set_extents")
    _set_extents.argtypes = [POINTER(_AtspiComponent), c_int, c_int, c_int, c_int, _AtspiCoordType,
                             POINTER(POINTER(_GError))]
    _set_extents.restype = c_bool

    _set_position = IATSPI().get_iface_func("atspi_component_set_position")
    _set_position.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType,
                              POINTER(POINTER(_GError))]
    _set_position.restype = c_bool

    _set_size = IATSPI().get_iface_func("atspi_component_set_size")
    _set_size.argtypes = [POINTER(_AtspiComponent), c_int, c_int, POINTER(POINTER(_GError))]
    _set_size.restype = c_bool

    _scroll_to = IATSPI().get_iface_func("atspi_component_scroll_to")

    try:
        _scroll_to.restype = c_bool
        _scroll_to.argtypes = [POINTER(_AtspiComponent), _AtspiScrollType, POINTER(POINTER(_GError))]
    except:
        # TODO add version check
        pass

    _scroll_to_point = IATSPI().get_iface_func("atspi_component_scroll_to_point")
    try:
        _scroll_to_point.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, c_int, c_int,
                                          POINTER(POINTER(_GError))]
        _scroll_to_point.restype = c_bool
    except:
        # TODO add version check
        pass

    def __init__(self, pointer):
        self._pointer = pointer

    def grab_focus(self, coord_type="window"):
        if coord_type not in ["window", "screen"]:
            raise ValueError('Wrong coord_type "{}".'.format(coord_type))
        error = _GError()
        pp = POINTER(POINTER(_GError))(error)
        # TODO segfault find root cause
        self._grab_focus(self._pointer, pp)

    def get_rectangle(self, coord_type="window"):
        if coord_type not in ["window", "screen"]:
            raise ValueError('Wrong coord_type "{}".'.format(coord_type))
        error = _GError()
        pp = POINTER(POINTER(_GError))(error)
        prect = self._get_rectangle(self._pointer, 0 if coord_type == "screen" else 1, pp)
        return RECT(prect.contents)


class AtspiStateSet(object):
    new = IATSPI().get_iface_func("atspi_state_set_new")
    new.argtypes = [POINTER(_GArray)]
    new.restype = POINTER(_AtspiStateSet)

    set_by_name = IATSPI().get_iface_func("atspi_state_set_set_by_name")
    set_by_name.argtypes = [POINTER(_AtspiStateSet), c_char_p, c_bool]

    add = IATSPI().get_iface_func("atspi_state_set_add")
    add.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]

    compare = IATSPI().get_iface_func("atspi_state_set_compare")
    compare.argtypes = [POINTER(_AtspiStateSet), POINTER(_AtspiStateSet)]
    compare.restype = POINTER(_AtspiStateSet)

    contains = IATSPI().get_iface_func("atspi_state_set_contains")
    contains.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]
    contains.restype = c_bool

    equals = IATSPI().get_iface_func("atspi_state_set_equals")
    equals.argtypes = [POINTER(_AtspiStateSet), POINTER(_AtspiStateSet)]
    equals.restype = c_bool

    get_states = IATSPI().get_iface_func("atspi_state_set_get_states")
    get_states.argtypes = [POINTER(_AtspiStateSet)]
    get_states.restype = POINTER(_GArray)

    is_empty = IATSPI().get_iface_func("atspi_state_set_is_empty")
    is_empty.argtypes = [POINTER(_AtspiStateSet)]
    is_empty.restype = c_bool

    remove = IATSPI().get_iface_func("atspi_state_set_remove")
    remove.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]

    def __init__(self, pointer):
        self._pointer = pointer

