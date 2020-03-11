# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Low-level interface to Linux ATSPI"""

import subprocess
import six

from ctypes import c_int, c_bool, c_char_p, c_char, POINTER, c_uint, c_uint32, c_uint64, c_double, c_short, \
    create_string_buffer, cdll, pointer, c_void_p, CFUNCTYPE
from functools import wraps

from ..base_types import Structure
from ..base_types import PointIteratorMixin
from ..base_types import RectExtMixin
from ..backend import Singleton


class CtypesEnum(object):

    """Base class for Enums"""

    @classmethod
    def from_param(cls, obj):
        return int(obj)


class _AtspiCoordType(CtypesEnum):
    ATSPI_COORD_TYPE_SCREEN = 0
    ATSPI_COORD_TYPE_WINDOW = 1


def _coord_type_to_atspi(t="window"):
    """Helper to convert string to ATSPI coordinate types"""
    if t not in ["window", "screen"]:
        raise ValueError('Wrong coord_type "{}".'.format(t))
    if t == "screen":
        return _AtspiCoordType.ATSPI_COORD_TYPE_SCREEN
    else:
        return _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW


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


_AtspiTextGranularity = ["char", "word", "sentence", "line", "paragraph"]


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


class _AtspiRect(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
        ('width', c_int),
        ('height', c_int),
    ]


class _AtspiPoint(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
    ]


class POINT(_AtspiPoint, PointIteratorMixin):
    """Coordinates point"""
    pass


RectExtMixin._POINT = POINT


class RECT(RectExtMixin, Structure):

    """Wrap the RECT structure and add extra functionality"""

    _fields_ = [
        ('left', c_int),
        ('top', c_int),
        ('right', c_int),
        ('bottom', c_int),
    ]

    # ----------------------------------------------------------------
    def __init__(self, otherRect_or_left=0, top=0, right=0, bottom=0):
        """
        Try to construct RECT from _AtspiRect otherwise pass it down to RecExtMixin
        """
        if isinstance(otherRect_or_left, _AtspiRect):
            self.left = otherRect_or_left.x
            self.right = otherRect_or_left.x + otherRect_or_left.width
            self.top = otherRect_or_left.y
            self.bottom = otherRect_or_left.y + otherRect_or_left.height
        else:
            RectExtMixin.__init__(self, otherRect_or_left, top, right, bottom)


RectExtMixin._RECT = RECT


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


class _AtspiDocument(Structure):
    pass


class _AtspiImage(Structure):
    pass


class _AtspiAccessiblePrivate(Structure):
    pass


class _AtspiObject(Structure):
    _fields_ = [
        ('parent', _GObject),
        ('accessible_parent', POINTER(_AtspiApplication)),
        ('path', c_char_p),
    ]


class _AtspiStateSet(Structure):
    _fields_ = [
        # TODO: investigate why defining fields as per
        # at-spi2-core/atspi/atspi-stateset.h doesn't work
        ('fake', c_uint64 * 4),
        ('states', c_uint64),
    ]


class _AtspiAction(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiText(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiEditableText(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiValue(Structure):
    _fields_ = [
        ('parent', _GTypeInterface),
    ]


class _AtspiTextRange(Structure):
    _fields_ = [
        ('start_offset', c_int),
        ('end_offset', c_int),
        ('content', c_char_p),
    ]


class _AtspiRange(Structure):
    _fields_ = [
        ('start_offset', c_int),
        ('end_offset', c_int),
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
    ('priv', POINTER(_AtspiAccessiblePrivate)),
]


class GErrorException(RuntimeError):

    """Raised when an exception occurred during libatspi method call"""

    def __init__(self, err_p):
        """Initialise the RuntimeError parent with the message"""
        RuntimeError.__init__(self, "GError with code: {0}, message: '{1}'".format(err_p[0].code,
                                                                                   err_p[0].message.decode(
                                                                                       encoding='UTF-8')))


def g_error_handler(func):
    """Helper decorator to handle GError"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        err_p = pointer(_GError())
        err_pp = pointer(err_p)
        kwargs["g_error_pointer"] = err_pp
        res = func(*args, **kwargs)
        if err_p[0].code == 0:
            return res
        else:
            raise GErrorException(err_p)

    return wrapper


ATSPI_ROLE_COUNT = 126


def _find_library(libs_list):
    """Helper for locating native system libraries from the list"""
    try:
        process = subprocess.Popen(["ldconfig", "-p"], stdout=subprocess.PIPE, universal_newlines=True)
        stdout = process.communicate()
        lines = stdout[0].split("\n")
        for lib in libs_list:
            for line in lines:
                if lib in line:
                    lib_path = line.split()[3]
                    print("Lib located: {0}".format(lib_path))
                    return lib_path

    except IOError:
        # ldconfig not installed will use default lib name
        return libs_list[-1]


@six.add_metaclass(Singleton)
class IATSPI(object):

    """Python wrapper around C functions from ATSPI library"""

    LIB = "libatspi"
    DEFAULT_LIB_NAME = "libatspi.so"

    def __get_roles(self):
        control_types = []
        get_role_name = self.atspi.atspi_role_get_name
        get_role_name.argtypes = [c_int]
        get_role_name.restype = c_char_p
        for i in range(ATSPI_ROLE_COUNT):
            role = get_role_name(i)
            if role is not None:
                role = "".join([part.capitalize() for part in role.decode("utf-8").split()])
                control_types.append(role)
        return control_types

    def __init__(self):
        try:
            self.atspi = cdll.LoadLibrary(_find_library([self.LIB, self.DEFAULT_LIB_NAME]))
            self.atspi.atspi_init()
            if not self.atspi.atspi_is_initialized():
                raise Exception("Cannot initialize atspi module")

            self._control_types = self.__get_roles()
            self.known_control_types = {}  # string id: numeric id
            self.known_control_type_ids = {}  # numeric id: string id

            for type_id, ctrl_type in enumerate(self._control_types):
                self.known_control_types[ctrl_type] = type_id
                self.known_control_type_ids[type_id] = ctrl_type

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


class GLIB(object):

    """Python wrapper around C functions from GLib library"""

    LIB12 = "libglib-1.2.so"
    LIB20 = "libglib-2.0.so"
    LIB22 = "libglib-2.2.so"
    DEFAULT_LIB_NAME = "libglib.so"
    glib = cdll.LoadLibrary(_find_library([LIB22, LIB20, LIB12, DEFAULT_LIB_NAME]))


class GHashTable(object):

    """
    Python wrapper around C GHashTable

    Limitations:
     - currently only for strings as key/value
    """

    _glib = GLIB.glib

    _GHFunc = CFUNCTYPE(c_void_p, c_char_p, c_char_p)

    _g_str_hash = _glib.g_str_hash
    _g_str_hash.restype = c_uint
    _g_str_hash.argtypes = [c_char_p]
    _GStrHashFunc = CFUNCTYPE(c_uint, c_char_p)

    _g_str_equal = _glib.g_str_equal
    _g_str_equal.restype = c_bool
    _g_str_equal.argtypes = [c_char_p, c_char_p]
    _GStrEqualFunc = CFUNCTYPE(c_bool, c_char_p, c_char_p)

    # Basic GHashTable constructor, to be used only with
    # string-based key-value pairs that are alloc/free by Python
    _g_hash_table_new = _glib.g_hash_table_new
    _g_hash_table_new.restype = c_void_p
    _g_hash_table_new.argtypes = [_GStrHashFunc, _GStrEqualFunc]

    _g_hash_table_foreach = _glib.g_hash_table_foreach
    _g_hash_table_foreach.restype = None
    _g_hash_table_foreach.argtypes = [c_void_p, _GHFunc, c_void_p]

    _g_hash_table_destroy = _glib.g_hash_table_destroy
    _g_hash_table_destroy.restype = None
    _g_hash_table_destroy.argtypes = [c_void_p]

    _g_hash_table_insert = _glib.g_hash_table_insert
    _g_hash_table_insert.restype = c_bool
    _g_hash_table_insert.argtypes = [c_void_p, c_void_p, c_void_p]

    @classmethod
    def dic2ghash(cls, d):
        """Utility function to create GLib ghash_table

        Limitations:
         - only for strings as key/value
         - to have valid pointers dictionary should consist of bytes
         - no GLib insertion/lookup operations after leaving the scope
           of the function, as hash/equal callbacks are released by GC
        """
        hash_cbk = cls._GStrHashFunc(cls._g_str_hash)
        equal_cbk = cls._GStrEqualFunc(cls._g_str_equal)

        ghash_table_p = cls._g_hash_table_new(hash_cbk, equal_cbk)
        for k, v in d.items():
            res = cls._g_hash_table_insert(ghash_table_p, k, v)
            if res is False:
                raise ValueError("Failed to insert k='{0}', v='{1}'".format(k, v))

        return ghash_table_p

    @classmethod
    def ghash2dic(cls, ghash):
        """
        Helper to convert GHashTable to Python dictionary

        The helper is limited only to strings
        """
        res_dic = {}

        def add_kvp(k, v, ud=None):
            res_dic[k.decode('utf-8')] = v.decode('utf-8')
        cbk = cls._GHFunc(add_kvp)

        cls._g_hash_table_foreach(ghash, cbk, None)
        cls._g_hash_table_destroy(ghash)
        return res_dic


class AtspiAccessible(object):

    """Access to ATSPI Accessible Interface"""

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

    get_index_in_parent = IATSPI().get_iface_func("atspi_accessible_get_index_in_parent")
    get_index_in_parent.argtypes = [POINTER(_AtspiAccessible), POINTER(POINTER(_GError))]
    get_index_in_parent.restype = c_int

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

    get_editable_text = IATSPI().get_iface_func("atspi_accessible_get_editable_text")
    get_editable_text.argtypes = [POINTER(_AtspiAccessible)]
    get_editable_text.restype = POINTER(_AtspiEditableText)

    get_document = IATSPI().get_iface_func("atspi_accessible_get_document")
    get_document.argtypes = [POINTER(_AtspiAccessible)]
    get_document.restype = POINTER(_AtspiDocument)

    get_image = IATSPI().get_iface_func("atspi_accessible_get_image")
    get_image.argtypes = [POINTER(_AtspiAccessible)]
    get_image.restype = POINTER(_AtspiImage)


class AtspiComponent(object):

    """Access to ATSPI Component Interface"""

    _contains = IATSPI().get_iface_func("atspi_component_contains")
    _contains.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType, POINTER(POINTER(_GError))]
    _contains.restype = c_bool

    _get_accessible_at_point = IATSPI().get_iface_func("atspi_component_get_accessible_at_point")
    _get_accessible_at_point.argtypes = [POINTER(_AtspiComponent), c_int, c_int, _AtspiCoordType,
                                         POINTER(POINTER(_GError))]
    _get_accessible_at_point.restype = POINTER(_AtspiAccessible)

    _get_rectangle = IATSPI().get_iface_func("atspi_component_get_extents")
    _get_rectangle.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_rectangle.restype = POINTER(_AtspiRect)

    _get_position = IATSPI().get_iface_func("atspi_component_get_position")
    _get_position.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_position.restype = POINTER(_AtspiPoint)

    _get_size = IATSPI().get_iface_func("atspi_component_get_size")
    _get_size.argtypes = [POINTER(_AtspiComponent), POINTER(POINTER(_GError))]
    _get_size.restype = POINTER(_AtspiPoint)

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

    if _scroll_to:
        _scroll_to.restype = c_bool
        _scroll_to.argtypes = [POINTER(_AtspiComponent), _AtspiScrollType, POINTER(POINTER(_GError))]

    _scroll_to_point = IATSPI().get_iface_func("atspi_component_scroll_to_point")
    if _scroll_to_point:
        _scroll_to_point.argtypes = [POINTER(_AtspiComponent), _AtspiCoordType, c_int, c_int,
                                     POINTER(POINTER(_GError))]
        _scroll_to_point.restype = c_bool

    def __init__(self, pointer):
        self._pointer = pointer

    @g_error_handler
    def grab_focus(self, coord_type="window", g_error_pointer=None):
        if coord_type not in ["window", "screen"]:
            raise ValueError('Wrong coord_type "{}".'.format(coord_type))
        self._grab_focus(self._pointer, g_error_pointer)

    @g_error_handler
    def get_rectangle(self, coord_type="window", g_error_pointer=None):
        prect = self._get_rectangle(self._pointer, _coord_type_to_atspi(coord_type), g_error_pointer)
        return RECT(prect.contents)

    @g_error_handler
    def get_layer(self, g_error_pointer=None):
        return self._get_layer(self._pointer, g_error_pointer)

    @g_error_handler
    def get_mdi_z_order(self, g_error_pointer=None):
        return self._get_mdi_z_order(self._pointer, g_error_pointer)


class AtspiStateSet(object):

    """Access to ATSPI StateSet Interface"""

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

    """Access to ATSPI Action Interface"""

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

    @g_error_handler
    def get_action_description(self, action_number, g_error_pointer=None):
        description = self._get_action_description(self._pointer, action_number, g_error_pointer)
        return description

    @g_error_handler
    def get_action_name(self, action_number, g_error_pointer=None):
        name = self._get_action_name(self._pointer, action_number, g_error_pointer)
        return name

    @g_error_handler
    def get_n_actions(self, g_error_pointer=None):
        actions_number = self._get_n_actions(self._pointer, g_error_pointer)
        return actions_number

    @g_error_handler
    def get_key_binding(self, action_number, g_error_pointer=None):
        key_binding = self._get_key_binding(self._pointer, action_number, g_error_pointer)
        return key_binding

    @g_error_handler
    def get_localized_name(self, action_number, g_error_pointer=None):
        name = self._get_localized_name(self._pointer, action_number, g_error_pointer)
        return name

    @g_error_handler
    def do_action(self, action_number, g_error_pointer=None):
        status = self._do_action(self._pointer, action_number, g_error_pointer)
        return status

    def get_action_by_name(self, name):
        actions_count = self.get_n_actions()
        for i in range(actions_count):
            if self.get_action_name(i).decode('utf-8').lower() == name.lower():
                return i
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

    """Access to ATSPI Text Interface"""

    _get_character_count = IATSPI().get_iface_func("atspi_text_get_character_count")
    _get_character_count.argtypes = [POINTER(_AtspiText), POINTER(POINTER(_GError))]
    _get_character_count.restype = c_int

    _get_text = IATSPI().get_iface_func("atspi_text_get_text")
    _get_text.argtypes = [POINTER(_AtspiText), c_int, c_int, POINTER(POINTER(_GError))]
    _get_text.restype = c_char_p

    _get_caret_offset = IATSPI().get_iface_func("atspi_text_get_caret_offset")
    _get_caret_offset.argtypes = [POINTER(_AtspiText), POINTER(POINTER(_GError))]
    _get_caret_offset.restype = c_int

    _get_text_attributes = IATSPI().get_iface_func("atspi_text_get_text_attributes")
    _get_text_attributes.argtypes = [POINTER(_AtspiText), c_int, c_int, POINTER(POINTER(_GError))]
    _get_text_attributes.restype = POINTER(_GHashTable)

    _get_attribute_run = IATSPI().get_iface_func("atspi_text_get_attribute_run")
    _get_attribute_run.argtypes = [POINTER(_AtspiText), c_int, c_bool, c_int, c_int, POINTER(POINTER(_GError))]
    _get_attribute_run.restype = POINTER(_GHashTable)

    _get_text_attribute_value = IATSPI().get_iface_func("atspi_text_get_text_attribute_value")
    _get_text_attribute_value.argtypes = [POINTER(_AtspiText), c_int, c_char_p, POINTER(POINTER(_GError))]
    _get_text_attribute_value.restype = c_char_p

    _get_default_attributes = IATSPI().get_iface_func("atspi_text_get_default_attributes")
    _get_default_attributes.argtypes = [POINTER(_AtspiText), POINTER(POINTER(_GError))]
    _get_default_attributes.restype = POINTER(_GHashTable)

    _set_caret_offset = IATSPI().get_iface_func("atspi_text_set_caret_offset")
    _set_caret_offset.argtypes = [POINTER(_AtspiText), c_int, POINTER(POINTER(_GError))]
    _set_caret_offset.restype = c_bool

    _get_string_at_offset = IATSPI().get_iface_func("atspi_text_get_string_at_offset")
    _get_string_at_offset.argtypes = [POINTER(_AtspiText), c_int, c_int, POINTER(POINTER(_GError))]
    _get_string_at_offset.restype = POINTER(_AtspiTextRange)

    _get_character_at_offset = IATSPI().get_iface_func("atspi_text_get_character_at_offset")
    _get_character_at_offset.argtypes = [POINTER(_AtspiText), c_int, POINTER(POINTER(_GError))]
    _get_character_at_offset.restype = c_uint

    _get_character_extents = IATSPI().get_iface_func("atspi_text_get_character_extents")
    _get_character_extents.argtypes = [POINTER(_AtspiText), c_int, _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_character_extents.restype = POINTER(_AtspiRect)

    _get_offset_at_point = IATSPI().get_iface_func("atspi_text_get_offset_at_point")
    _get_offset_at_point.argtypes = [POINTER(_AtspiText), c_int, c_int, _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_offset_at_point.restype = c_int

    _get_range_extents = IATSPI().get_iface_func("atspi_text_get_range_extents")
    _get_range_extents.argtypes = [POINTER(_AtspiText), c_int, c_int, _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_range_extents.restype = POINTER(_AtspiRect)

    _get_n_selections = IATSPI().get_iface_func("atspi_text_get_n_selections")
    _get_n_selections.argtypes = [POINTER(_AtspiText), POINTER(POINTER(_GError))]
    _get_n_selections.restype = c_int

    _get_selection = IATSPI().get_iface_func("atspi_text_get_selection")
    _get_selection.argtypes = [POINTER(_AtspiText), c_int, POINTER(POINTER(_GError))]
    _get_selection.restype = POINTER(_AtspiRange)

    _add_selection = IATSPI().get_iface_func("atspi_text_add_selection")
    _add_selection.argtypes = [POINTER(_AtspiText), c_int, c_int, POINTER(POINTER(_GError))]
    _add_selection.restype = c_bool

    _remove_selection = IATSPI().get_iface_func("atspi_text_remove_selection")
    _remove_selection.argtypes = [POINTER(_AtspiText), c_int, POINTER(POINTER(_GError))]
    _remove_selection.restype = c_bool

    _set_selection = IATSPI().get_iface_func("atspi_text_set_selection")
    _set_selection.argtypes = [POINTER(_AtspiText), c_int, c_int, c_int, POINTER(POINTER(_GError))]
    _set_selection.restype = c_bool

    def __init__(self, pointer):
        self._pointer = pointer

    @g_error_handler
    def get_character_count(self, g_error_pointer=None):
        character_count = self._get_character_count(self._pointer, g_error_pointer)
        return character_count

    @g_error_handler
    def get_text(self, start_offset, end_offset, g_error_pointer=None):
        return self._get_text(self._pointer, start_offset, end_offset, g_error_pointer)

    def get_whole_text(self):
        return self.get_text(0, self.get_character_count())

    @g_error_handler
    def get_caret_offset(self, g_error_pointer=None):
        return self._get_caret_offset(self._pointer, g_error_pointer)

    @g_error_handler
    def set_caret_offset(self, offset, g_error_pointer=None):
        return self._set_caret_offset(self._pointer, offset, g_error_pointer)

    @g_error_handler
    def get_string_at_offset(self, offset, granularity):
        assert granularity.lower() in _AtspiTextGranularity, \
            "wrong granularity type expected one of: {}".format(_AtspiTextGranularity)
        granularity = _AtspiTextGranularity.index(granularity.lower())
        text_range = self._get_string_at_offset(offset, granularity)
        return text_range.contents.content

    @g_error_handler
    def get_selection(self, offset=0, g_error_pointer=None):
        atspi_range = self._get_selection(self._pointer, offset, g_error_pointer)
        return atspi_range.contents.start_offset, atspi_range.contents.end_offset

    def add_selection(self, start_pos, end_pos, g_error_pointer=None):
        return self._add_selection(self._pointer, start_pos, end_pos, g_error_pointer)


class AtspiEditableText(object):

    """Access to ATSPI Editable Interface"""

    _set_text_contents = IATSPI().get_iface_func("atspi_editable_text_set_text_contents")
    _set_text_contents.argtypes = [POINTER(_AtspiEditableText), c_char_p, POINTER(POINTER(_GError))]
    _set_text_contents.restype = c_bool

    _insert_text = IATSPI().get_iface_func("atspi_editable_text_insert_text")
    _insert_text.argtypes = [POINTER(_AtspiEditableText), c_int, c_char_p, c_int, POINTER(POINTER(_GError))]
    _insert_text.restype = c_bool

    _copy_text = IATSPI().get_iface_func("atspi_editable_text_copy_text")
    _copy_text.argtypes = [POINTER(_AtspiEditableText), c_int, c_int, POINTER(POINTER(_GError))]
    _copy_text.restype = c_bool

    _cut_text = IATSPI().get_iface_func("atspi_editable_text_cut_text")
    _cut_text.argtypes = [POINTER(_AtspiEditableText), c_int, c_int, POINTER(POINTER(_GError))]
    _cut_text.restype = c_bool

    _delete_text = IATSPI().get_iface_func("atspi_editable_text_delete_text")
    _delete_text.argtypes = [POINTER(_AtspiEditableText), c_int, c_int, POINTER(POINTER(_GError))]
    _delete_text.restype = c_bool

    _paste_text = IATSPI().get_iface_func("atspi_editable_text_paste_text")
    _paste_text.argtypes = [POINTER(_AtspiEditableText), c_int, POINTER(POINTER(_GError))]
    _paste_text.restype = c_bool

    def __init__(self, pointer):
        self._pointer = pointer

    @g_error_handler
    def insert_text(self, text, start_positon=0, g_error_pointer=None):
        return self._insert_text(self._pointer, start_positon, text, len(text), g_error_pointer)

    @g_error_handler
    def set_text(self, text, g_error_pointer=None):
        return self._set_text_contents(self._pointer, c_char_p(text), g_error_pointer)


class AtspiValue(object):

    """Access to ATSPI Value Interface"""

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

    @g_error_handler
    def get_minimum_value(self, g_error_pointer=None):
        return self._get_minimum_value(self._pointer, g_error_pointer)

    @g_error_handler
    def get_current_value(self, g_error_pointer=None):
        return self._get_minimum_value(self._pointer, g_error_pointer)

    @g_error_handler
    def get_maximum_value(self, g_error_pointer=None):
        return self._get_maximum_value(self._pointer, g_error_pointer)

    @g_error_handler
    def get_minimum_increment(self, g_error_pointer=None):
        return self._get_minimum_increment(self._pointer, g_error_pointer)

    @g_error_handler
    def set_current_value(self, new_value, g_error_pointer=None):
        return self._set_current_value(self._pointer, new_value, g_error_pointer)


class AtspiDocument(object):

    """Access to ATSPI Document Interface"""

    _get_locale = IATSPI().get_iface_func("atspi_document_get_locale")
    _get_locale.argtypes = [POINTER(_AtspiDocument), POINTER(POINTER(_GError))]
    _get_locale.restype = c_char_p

    _get_attribute_value = IATSPI().get_iface_func("atspi_document_get_document_attribute_value")
    _get_attribute_value.argtypes = [POINTER(_AtspiDocument), c_char_p, POINTER(POINTER(_GError))]
    _get_attribute_value.restype = c_char_p

    _get_attributes = IATSPI().get_iface_func("atspi_document_get_document_attributes")
    _get_attributes.argtypes = [POINTER(_AtspiDocument), POINTER(POINTER(_GError))]
    _get_attributes.restype = c_void_p

    def __init__(self, pointer):
        """Init the ATSPI Document Interface"""
        self._pointer = pointer

    @g_error_handler
    def get_locale(self, g_error_pointer=None):
        """
        Get the locale associated with the document's content, e.g. the locale for LOCALE_TYPE_MESSAGES.

        Return a string compliant with the POSIX standard for locale description.
        """
        return self._get_locale(self._pointer, g_error_pointer)

    @g_error_handler
    def get_attribute_value(self, attrib, g_error_pointer=None):
        """
        Get the value of a single attribute, if specified for the document as a whole.

        Return a string corresponding to the value of the specified attribute,
        or an empty string if the attribute is unspecified for the object.
        """
        return self._get_attribute_value(self._pointer, c_char_p(attrib.encode()), g_error_pointer)

    @g_error_handler
    def get_attributes(self, g_error_pointer=None):
        """
        Get all constant attributes for the document as a whole.

        Return a dictionary containing the constant attributes of the document, as name-value pairs
        """
        res = self._get_attributes(self._pointer, g_error_pointer)
        return GHashTable.ghash2dic(res)


class AtspiImage(object):

    """Access to ATSPI Image Interface"""

    _get_image_locale = IATSPI().get_iface_func("atspi_image_get_image_locale")
    _get_image_locale.argtypes = [POINTER(_AtspiImage), POINTER(POINTER(_GError))]
    _get_image_locale.restype = c_char_p

    _get_image_extents = IATSPI().get_iface_func("atspi_image_get_image_extents")
    _get_image_extents.argtypes = [POINTER(_AtspiImage), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_image_extents.restype = POINTER(_AtspiRect)

    _get_image_position = IATSPI().get_iface_func("atspi_image_get_image_position")
    _get_image_position.argtypes = [POINTER(_AtspiImage), _AtspiCoordType, POINTER(POINTER(_GError))]
    _get_image_position.restype = POINTER(_AtspiPoint)

    _get_image_size = IATSPI().get_iface_func("atspi_image_get_image_size")
    _get_image_size.argtypes = [POINTER(_AtspiImage), POINTER(POINTER(_GError))]
    _get_image_size.restype = POINTER(_AtspiPoint)

    _get_image_description = IATSPI().get_iface_func("atspi_image_get_image_description")
    _get_image_description.argtypes = [POINTER(_AtspiImage), POINTER(POINTER(_GError))]
    _get_image_description.restype = c_char_p

    def __init__(self, pointer):
        """Init the ATSPI Image Interface"""
        self._pointer = pointer

    @g_error_handler
    def get_description(self, g_error_pointer=None):
        """
        Get the description of the image displayed in an AtspiImage object.

        Return a UTF-8 string describing the image.
        """
        return self._get_image_description(self._pointer, g_error_pointer)

    @g_error_handler
    def get_locale(self, g_error_pointer=None):
        """
        Get the locale associated with an image and its textual representation.

        Return a POSIX LC_MESSAGES-style locale value for image description and text
        """
        return self._get_image_locale(self._pointer, g_error_pointer)

    @g_error_handler
    def get_size(self, g_error_pointer=None):
        """
        Get the size of the image displayed in a specified AtspiImage object.

        Return POINT structure
        where x corresponds to the image's width and y corresponds to the image's height.
        """
        pnt = self._get_image_size(self._pointer, g_error_pointer)
        return POINT(pnt.contents.x, pnt.contents.y)

    @g_error_handler
    def get_position(self, coord_type="window", g_error_pointer=None):
        """
        Get the minimum x and y coordinates of the image displayed in a specified AtspiImage implementor

        Return POINT structure
        where x and y correspond to the minimum coordinates of the displayed image
        """
        pnt = self._get_image_position(self._pointer, _coord_type_to_atspi(coord_type), g_error_pointer)
        return POINT(pnt.contents.x, pnt.contents.y)

    @g_error_handler
    def get_extents(self, coord_type="window", g_error_pointer=None):
        """
        Get the bounding box of the image displayed in a specified AtspiImage implementor

        Return a pointer to an RECT corresponding to the image's bounding box.
        The minimum x and y coordinates, width, and height are specified.
        """
        rect = self._get_image_extents(self._pointer, _coord_type_to_atspi(coord_type), g_error_pointer)
        return RECT(rect.contents)
