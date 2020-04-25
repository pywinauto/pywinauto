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

"""Definition of cross-platform types and structures"""

import six
from ctypes import Structure as Struct
from ctypes import memmove
from ctypes import addressof


##====================================================================
#def PrintCtypesStruct(struct, exceptList = []):
#    """Print out the fields of the ctypes Structure
#
#    fields in exceptList will not be printed"""
#    for f in struct._fields_:
#        name = f[0]
#        if name in exceptList:
#            continue
#        print("%20s "% name, getattr(struct, name))


# allow ctypes structures to be pickled
# set struct.__reduce__ = _reduce
# e.g. RECT.__reduce__ = _reduce
def _construct(typ, buf):
    obj = typ.__new__(typ)
    memmove(addressof(obj), buf, len(buf))
    return obj


def _reduce(self):
    return (_construct, (self.__class__, bytes(memoryview(self))))


class StructureMixIn(object):

    """Define printing and comparison behaviors to be used for the Structure class from ctypes"""

    #----------------------------------------------------------------
    def __str__(self):
        """Print out the fields of the ctypes Structure"""
        lines = []
        for field_name, _ in getattr(self, "_fields_", []):
            lines.append("%20s\t%s" % (field_name, getattr(self, field_name)))

        return "\n".join(lines)

    #----------------------------------------------------------------
    def __eq__(self, other):
        """Return True if the two instances have the same coordinates"""
        fields = getattr(self, "_fields_", [])
        if isinstance(other, Struct):
            try:
                # pretend they are two structures - check that they both
                # have the same value for all fields
                if len(fields) != len(getattr(other, "_fields_", [])):
                    return False
                for field_name, _ in fields:
                    if getattr(self, field_name) != getattr(other, field_name):
                        return False
                return True

            except AttributeError:
                return False

        elif isinstance(other, (list, tuple)):
            # Now try to see if we have been passed in a list or tuple
            if len(fields) != len(other):
                return False
            try:
                for i, (field_name, _) in enumerate(fields):
                    if getattr(self, field_name) != other[i]:
                        return False
                return True

            except Exception:
                return False

        return False

    #----------------------------------------------------------------
    def __ne__(self, other):
        """Return False if the two instances have the same coordinates"""
        return not self.__eq__(other)

    __hash__ = None


class Structure(Struct, StructureMixIn):

    """Override the Structure class from ctypes to add printing and comparison"""

    pass


class PointIteratorMixin(object):

    """Add iterator functionality to POINT structure"""

    x = None
    y = None

    def __iter__(self):
        """Allow iteration through coordinates"""
        yield self.x
        yield self.y

    def __getitem__(self, key):
        """Allow indexing of coordinates"""
        if key == 0 or key == -2:
            return self.x
        elif key == 1 or key == -1:
            return self.y
        else:
            raise IndexError("Illegal index")


# ====================================================================
class RectExtMixin(object):

    """Wrap the RECT structure and add extra functionality"""

    # To be initiated by OS-specific types
    _RECT = type(None)
    _POINT = type(None)

    # ----------------------------------------------------------------
    def __init__(self, other=0, top=0, right=0, bottom=0):
        """Provide a constructor for _RECT structures

        A _RECT can be constructed by:
        - Another RECT (each value will be copied)
        - Values for left, top, right and bottom

        e.g. my_rect = _RECT(otherRect)
        or   my_rect = _RECT(10, 20, 34, 100)
        """
        if isinstance(other, self._RECT):
            self.left = other.left
            self.right = other.right
            self.top = other.top
            self.bottom = other.bottom
        else:
            #if not isinstance(other, (int, long)):
            #    print type(self), type(other), other
            long_int = six.integer_types[-1]
            self.left = long_int(other)
            self.right = long_int(right)
            self.top = long_int(top)
            self.bottom = long_int(bottom)

    # ----------------------------------------------------------------
    def __str__(self):
        """Return a string representation of the _RECT"""
        return "(L%d, T%d, R%d, B%d)" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __repr__(self):
        """Return some representation of the _RECT"""
        return "<RECT L%d, T%d, R%d, B%d>" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __iter__(self):
        """Allow iteration through coordinates"""
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    # ----------------------------------------------------------------
    def __sub__(self, other):
        """Return a new rectangle which is offset from the one passed in"""
        new_rect = self._RECT()

        new_rect.left = self.left - other.left
        new_rect.right = self.right - other.left

        new_rect.top = self.top - other.top
        new_rect.bottom = self.bottom - other.top

        return new_rect

    # ----------------------------------------------------------------
    def __add__(self, other):
        """Allow two rects to be added using +"""
        new_rect = self._RECT()

        new_rect.left = self.left + other.left
        new_rect.right = self.right + other.left

        new_rect.top = self.top + other.top
        new_rect.bottom = self.bottom + other.top

        return new_rect

    # ----------------------------------------------------------------
    def width(self):
        """Return the width of the rect"""
        return self.right - self.left

    # ----------------------------------------------------------------
    def height(self):
        """Return the height of the rect"""
        return self.bottom - self.top

    # ----------------------------------------------------------------
    def mid_point(self):
        """Return a POINT structure representing the mid point"""
        pt = self._POINT()
        pt.x = self.left + int(float(self.width()) / 2.)
        pt.y = self.top + int(float(self.height()) / 2.)
        return pt

    __reduce__ = _reduce
