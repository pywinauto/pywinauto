# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""Low-level interface to mac OS"""

from Foundation import NSRect, NSPoint, NSSize
from ..base_types import Structure, PointIteratorMixin, RectExtMixin
from ctypes import c_int

class AX_RECT():
    """Wrap the macos NSRect structure and add extra functionality"""
    def __init__(self, **kwargs):
        rect   = kwargs.get("nsrect", None)
        left   = kwargs.get("left", None)
        right  = kwargs.get("right", None)
        top    = kwargs.get("top", None)
        bottom = kwargs.get("bottom", None)
        if rect and isinstance(rect,NSRect):
            self.left = rect.origin.x
            self.right = rect.origin.x + rect.size.width
            self.top = rect.origin.y
            self.bottom = rect.origin.y + rect.size.height
            
        else:
            self.left = left
            self.right = right
            self.top = top
            self.bottom = bottom

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def width(self):
        return self.right - self.left

    @property
    def mid_point(self):
        """Return a POINT structure representing the mid point"""
        pt = AX_POINT()
        pt.x = self.left + int(float(self.width()) / 2.)
        pt.y = self.top + int(float(self.height()) / 2.)
        return pt

    def __repr__(self):
        return 'AX_RECT[left: {}, right: {}, top: {}, bottom: {}]'.format(self.left,self.right,self.top,self.bottom)

    def __eq__(self, other):
        if isinstance(other, AX_RECT):
            return self.__dict__ == other.__dict__
        return False


class AX_POINT():
    """Wrap the macos NSRect structure and add extra functionality"""
    def __init__(self, **kwargs):
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        p = kwargs.get("nspoint", None)
        if p and isinstance(p,NSPoint):
            self.x = p.x
            self.y = p.y
        else:
            self.x = x
            self.y = y

    def __repr__(self):
        return 'AX_POINT[x: {}, y: {}]'.format(self.x,self.y)

    """Support of getting x,y by index"""
    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        return None

    def __eq__(self, other):
        if isinstance(other, AX_POINT):
            return self.__dict__ == other.__dict__
        return False


class AX_SIZE():
    """Wrap the macos NSSize structure and add extra functionality"""
    def __init__(self, **kwargs):
        w = kwargs.get("width", None)
        h = kwargs.get("height", None)
        sys_obj = kwargs.get("nssize", None)
        if sys_obj and isinstance(sys_obj,NSSize):
            self.width = sys_obj.width
            self.height = sys_obj.height
        else:
            self.width = width
            self.height = height

    def __repr__(self):
        return 'AX_SIZE[width: {}, height: {}]'.format(self.width,self.height)

    def __eq__(self, other):
        if isinstance(other, AX_SIZE):
            return self.__dict__ == other.__dict__
        return False
