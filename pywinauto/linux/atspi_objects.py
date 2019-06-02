import ctypes
import subprocess
import six
from ctypes import *  #Structure, c_char_p, c_int, c_bool, POINTER, c_uint32, c_short, c_double, addressof, c_void_p, c_char, create_string_buffer
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

    def __eq__(self, other):
        "return true if the two rectangles have the same coordinates"
        try:
            return \
                self.left == other.left and \
                self.top == other.top and \
                self.right == other.right and \
                self.bottom == other.bottom
        except AttributeError:
            return False

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


AtspiStateEnum = {
    0: 'STATE_INVALID',
    1: 'STATE_ACTIVE',
    2: 'STATE_ARMED',
    3: 'STATE_BUSY',
    4: 'STATE_CHECKED',
    5: 'STATE_COLLAPSED',
    6: 'STATE_DEFUNCT',
    7: 'STATE_EDITABLE',
    8: 'STATE_ENABLED',
    9: 'STATE_EXPANDABLE',
    10: 'STATE_EXPANDED',
    11: 'STATE_FOCUSABLE',
    12: 'STATE_FOCUSED',
    13: 'STATE_HAS_TOOLTIP',
    14: 'STATE_HORIZONTAL',
    15: 'STATE_ICONIFIED',
    16: 'STATE_MODAL',
    17: 'STATE_MULTI_LINE',
    18: 'STATE_MULTISELECTABLE',
    19: 'STATE_OPAQUE',
    20: 'STATE_PRESSED',
    21: 'STATE_RESIZABLE',
    22: 'STATE_SELECTABLE',
    23: 'STATE_SELECTED',
    24: 'STATE_SENSITIVE',
    25: 'STATE_SHOWING',
    26: 'STATE_SINGLE_LINE',
    27: 'STATE_STALE',
    28: 'STATE_TRANSIENT',
    29: 'STATE_VERTICAL',
    30: 'STATE_VISIBLE',
    31: 'STATE_MANAGES_DESCENDANTS',
    32: 'STATE_INDETERMINATE',
    33: 'STATE_REQUIRED',
    34: 'STATE_TRUNCATED',
    35: 'STATE_ANIMATED',
    36: 'STATE_INVALID_ENTRY',
    37: 'STATE_SUPPORTS_AUTOCOMPLETION',
    38: 'STATE_SELECTABLE_TEXT',
    39: 'STATE_IS_DEFAULT',
    40: 'STATE_VISITED',
    41: 'STATE_CHECKABLE',
    42: 'STATE_HAS_POPUP',
    43: 'STATE_READ_ONLY',
    44: 'STATE_LAST_DEFINED',
}


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


class _GTypeInstance(Structure):
    pass


class _GData(Structure):
    pass


class _GObject(Structure):
    _fields_ = [
        ('g_type_instance', _GTypeInstance),
        ('ref_count', c_uint),
        ('qdata', POINTER(_GData)),
    ]


class _GError(Structure):
    _fields_ = [
        ('domain', c_uint32),
        ('code', c_int),
        ('message', c_char_p),
    ]


class _GArray(Structure):
    _fields_ = [
        ('data', POINTER(c_char)),
        ('len', c_uint32),
    ]


class _GHashTable(Structure):
    pass


class _GPtrArray(Structure):
    pass

class _GTypeInterface(Structure):
    pass


class _AtspiRole(Structure):
    pass


class _AtspiApplication(Structure):
    pass


class _AtspiComponent(Structure):
    pass


class _AtspiStateSet(Structure):
    pass


class _AtspiAccessiblePrivate(Structure):
    pass


class _AtspiObject(Structure):
    _fields_ = [
        ('parent', _GObject),
        ('accessible_parent', POINTER(_AtspiApplication)),
        ('path', c_char_p),
    ]


class _AtspiAction(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiText(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiValue(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiAccessible(Structure):
    pass


_AtspiAccessible._fields_ = [
    ('parent', _AtspiObject),
    ('accessible_parent', POINTER(_AtspiAccessible)),
    ('children', POINTER(_GPtrArray)),
    ('role', _AtspiRole),
    ('gint', c_int),
    ('name', c_char_p),
    ('description', c_char_p),
    ('states', POINTER(_AtspiStateSet)),
    ('attributes', POINTER(_GHashTable)),
    ('cached_properties', c_uint),
    ('cached_properties', _AtspiAccessiblePrivate),
]

_AtspiStateSet._fields_ = [
    ('fake', c_uint64 * 4),
    ('states', c_uint64),
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
                    return lib.split()[3]

        except FileNotFoundError:
            # ldconfig not installed will use default lib name
            return cls.DEFAULT_LIB_NAME

    def __init__(self):
        try:
            print(self.__find_library())
            self.atspi = ctypes.cdll.LoadLibrary(self.__find_library())
            self.atspi.atspi_init()
            if not self.atspi.atspi_is_initialized():
                raise Exception("Cannot initialize atspi module")

        except Exception:
            message = "atspi library not installed. Please install at-spi2 library or choose another backend"
            raise Exception(message)

    def get_iface_func(self, func_name):
        if hasattr(self.atspi, func_name + "_iface"):
            return getattr(self.atspi, func_name + "_iface")
        elif hasattr(self.atspi, func_name):
            return getattr(self.atspi, func_name)
        else:
            print("Warning! method: {} not found in libatspi.".format(func_name))
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

    is_action = IATSPI().get_iface_func("atspi_accessible_is_action")
    is_action.argtypes = [POINTER(_AtspiAccessible)]
    is_action.restype = c_bool

    get_action = IATSPI().get_iface_func("atspi_accessible_get_action")
    get_action.argtypes = [POINTER(_AtspiAccessible)]
    get_action.restype = POINTER(_AtspiAction)

    get_text = IATSPI().get_iface_func("atspi_accessible_get_text")
    get_text.argtypes = [POINTER(_AtspiAccessible)]
    get_text.restype = POINTER(_AtspiText)

    get_value = IATSPI().get_iface_func("atspi_accessible_get_value_iface")
    get_value.argtypes = [POINTER(_AtspiAccessible)]
    get_value.restype = POINTER(_AtspiValue)


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
    _get_layer.restype = c_int

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
        self._grab_focus(self._pointer, pp)

    def get_rectangle(self, coord_type="window"):
        if coord_type not in ["window", "screen"]:
            raise ValueError('Wrong coord_type "{}".'.format(coord_type))
        error = _GError()
        pp = POINTER(POINTER(_GError))(error)
        prect = self._get_rectangle(self._pointer, 0 if coord_type == "screen" else 1, pp)
        return RECT(prect.contents)

    def get_layer(self):
        error = _GError()
        pp = POINTER(POINTER(_GError))(error)
        return self._get_layer(self._pointer, pp)

    def get_mdi_x_order(self):
        error = _GError()
        pp = POINTER(POINTER(_GError))(error)
        return self._get_layer(self._pointer, pp)


class AtspiStateSet(object):
    _new = IATSPI().get_iface_func("atspi_state_set_new")
    _new.argtypes = [POINTER(_GArray)]
    _new.restype = POINTER(_AtspiStateSet)

    _set_by_name = IATSPI().get_iface_func("atspi_state_set_set_by_name")
    _set_by_name.argtypes = [POINTER(_AtspiStateSet), POINTER(c_char), c_bool]

    _add = IATSPI().get_iface_func("atspi_state_set_add")
    _add.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]

    _compare = IATSPI().get_iface_func("atspi_state_set_compare")
    _compare.argtypes = [POINTER(_AtspiStateSet), POINTER(_AtspiStateSet)]
    _compare.restype = POINTER(_AtspiStateSet)

    _contains = IATSPI().get_iface_func("atspi_state_set_contains")
    _contains.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]
    _contains.restype = c_bool

    _equals = IATSPI().get_iface_func("atspi_state_set_equals")
    _equals.argtypes = [POINTER(_AtspiStateSet), POINTER(_AtspiStateSet)]
    _equals.restype = c_bool

    _get_states = IATSPI().get_iface_func("atspi_state_set_get_states")
    _get_states.argtypes = [POINTER(_AtspiStateSet)]
    _get_states.restype = POINTER(_GArray)

    _is_empty = IATSPI().get_iface_func("atspi_state_set_is_empty")
    _is_empty.argtypes = [POINTER(_AtspiStateSet)]
    _is_empty.restype = c_bool

    _remove = IATSPI().get_iface_func("atspi_state_set_remove")
    _remove.argtypes = [POINTER(_AtspiStateSet), _AtspiStateType]

    def __init__(self, pointer):
        self._pointer = pointer

    def get_states(self):
        states = self._get_states(self._pointer)
        return states.contents

    def set_by_name(self, state_name, status):
        buffer = create_string_buffer(state_name)
        self._set_by_name(self._pointer, buffer, status)


class AtspiAction(object):
    _get_action_description = IATSPI().get_iface_func("atspi_action_get_action_description")
    _get_action_description.argtypes = [POINTER(_AtspiAction), c_int, POINTER(POINTER(_GError))]
    _get_action_description.restype = c_char_p

    _get_action_name = IATSPI().get_iface_func("atspi_action_get_action_name")
    _get_action_name.argtypes = [POINTER(_AtspiAction), c_int, POINTER(POINTER(_GError))]
    _get_action_name.restype = c_char_p

    _get_n_actions = IATSPI().get_iface_func("atspi_action_get_n_actions")
    _get_n_actions.argtypes = [POINTER(_AtspiAction), POINTER(POINTER(_GError))]
    _get_n_actions.restype = c_int

    _get_key_binding = IATSPI().get_iface_func("atspi_action_get_key_binding")
    _get_key_binding.argtypes = [POINTER(_AtspiAction), c_int, POINTER(POINTER(_GError))]
    _get_key_binding.restype = c_char_p

    _get_localized_name = IATSPI().get_iface_func("atspi_action_get_localized_name")
    _get_localized_name.argtypes = [POINTER(_AtspiAction), c_int, POINTER(POINTER(_GError))]
    _get_localized_name.restype = c_char_p

    _do_action = IATSPI().get_iface_func("atspi_action_do_action")
    _do_action.argtypes = [POINTER(_AtspiAction), c_int, POINTER(POINTER(_GError))]
    _do_action.restype = c_bool

    def __init__(self, pointer):
        self._pointer = pointer

    def get_action_description(self, action_number):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        description = self._get_action_description(self._pointer, action_number, ep)
        return description

    def get_action_name(self, action_number):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        name = self._get_action_name(self._pointer, action_number, ep)
        return name

    def get_n_actions(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        actions_number = self._get_n_actions(self._pointer, ep)
        return actions_number

    def get_key_binding(self, action_number):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        key_binding = self._get_key_binding(self._pointer, action_number, ep)
        return key_binding

    def get_localized_name(self, action_number):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        name = self._get_localized_name(self._pointer, action_number, ep)
        return name

    def do_action(self, action_number):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        status = self._do_action(self._pointer, action_number, ep)
        return status

    def get_action_by_name(self, name):
        actions_count = self.get_n_actions()
        for i in range(actions_count):
            if self.get_action_name(i).decode('utf-8').lower() == name.lower():
                return i
        else:
            return None

    def get_all_actions(self):
        actions_count = self.get_n_actions()
        actions = []
        for i in range(actions_count):
            actions.append(self.get_action_name(i).decode('utf-8'))
        return actions

    def do_action_by_name(self, name):
        action_number = self.get_action_by_name(name)
        if action_number is None:
            return False
        return self.do_action(action_number)


class AtspiText(object):
    _get_character_count = IATSPI().get_iface_func("atspi_text_get_character_count")
    _get_character_count.argtypes = [POINTER(_AtspiText), POINTER(POINTER(_GError))]
    _get_character_count.restype = c_int

    _get_text = IATSPI().get_iface_func("atspi_text_get_text")
    _get_text.argtypes = [POINTER(_AtspiText), c_int, c_int, POINTER(POINTER(_GError))]
    _get_text.restype = c_char_p

    def __init__(self, pointer):
        self._pointer = pointer

    def get_character_count(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        character_count = self._get_character_count(self._pointer, ep)
        return character_count

    def get_text(self, start_offset, end_offset):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        text = self._get_character_count(self._pointer, start_offset, end_offset, ep)
        return text


class AtspiValue(object):
    _get_minimum_value = IATSPI().get_iface_func("atspi_value_get_minimum_value")
    _get_minimum_value.argtypes = [POINTER(_AtspiValue), POINTER(POINTER(_GError))]
    _get_minimum_value.restype = c_double

    _get_current_value = IATSPI().get_iface_func("atspi_value_get_current_value")
    _get_current_value.argtypes = [POINTER(_AtspiValue), POINTER(POINTER(_GError))]
    _get_current_value.restype = c_double

    _get_maximum_value = IATSPI().get_iface_func("atspi_value_get_maximum_value")
    _get_maximum_value.argtypes = [POINTER(_AtspiValue), POINTER(POINTER(_GError))]
    _get_maximum_value.restype = c_double

    _get_minimum_increment = IATSPI().get_iface_func("atspi_value_get_minimum_increment")
    _get_minimum_increment.argtypes = [POINTER(_AtspiValue), POINTER(POINTER(_GError))]
    _get_minimum_increment.restype = c_double

    _set_current_value = IATSPI().get_iface_func("atspi_value_set_current_value")
    _set_current_value.argtypes = [POINTER(_AtspiValue), c_double, POINTER(POINTER(_GError))]
    _set_current_value.restype = c_bool

    def __init__(self, pointer):
        self._pointer = pointer

    def get_minimum_value(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        min_value = self._get_minimum_value(self._pointer, ep)
        return min_value

    def get_current_value(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        curr_value = self._get_minimum_value(self._pointer, ep)
        return curr_value

    def get_maximum_value(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        max_value = self._get_maximum_value(self._pointer, ep)
        return max_value

    def get_minimum_increment(self):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        min_increment = self._get_minimum_increment(self._pointer, ep)
        return min_increment

    def set_current_value(self, new_value):
        error = _GError()
        ep = POINTER(POINTER(_GError))(error)
        status = self._set_current_value(self._pointer, new_value, ep)
        return status
