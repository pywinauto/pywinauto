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

from ctypes import Structure as Struct


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
