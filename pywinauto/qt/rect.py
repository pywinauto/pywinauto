"""Qt backend rectangle types that do not depend on a platform backend."""

from ctypes import c_int

from pywinauto.base_types import PointIteratorMixin, RectExtMixin, Structure


class POINT(Structure, PointIteratorMixin):
    """Screen point."""

    _fields_ = [
        ("x", c_int),
        ("y", c_int),
    ]


RectExtMixin._POINT = POINT


class RECT(RectExtMixin, Structure):
    """Screen rectangle."""

    _fields_ = [
        ("left", c_int),
        ("top", c_int),
        ("right", c_int),
        ("bottom", c_int),
    ]

    def __init__(self, other=0, top=0, right=0, bottom=0):
        RectExtMixin.__init__(self, other, top, right, bottom)


RectExtMixin._RECT = RECT
