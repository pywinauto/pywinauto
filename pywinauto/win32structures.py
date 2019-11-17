# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
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

"""Definition of Windows structures"""

import six
from ctypes import Structure as Struct
from ctypes import \
    c_int, c_long, c_void_p, c_char, memmove, addressof, \
    POINTER, sizeof, alignment, Union, c_longlong, c_size_t, wintypes

from .win32defines import LF_FACESIZE
from . import sysinfo


class StructureMixIn(object):

    """Define printing and comparison behaviors to be used for the Structure class from ctypes"""

    #----------------------------------------------------------------
    def __str__(self):
        """Print out the fields of the ctypes Structure

        fields in exceptList will not be printed"""
        lines = []
        for field_name, _ in getattr(self, "_fields_", []):
            lines.append("%20s\t%s"% (field_name, getattr(self, field_name)))

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


#LPTTTOOLINFOW = POINTER(tagTOOLINFOW)
#PTOOLINFOW = POINTER(tagTOOLINFOW)
BOOL = wintypes.BOOL
BYTE = wintypes.BYTE
CHAR = c_char
DWORD = wintypes.DWORD
HANDLE = wintypes.HANDLE
HBITMAP = HANDLE
LONG = wintypes.LONG
LPVOID = wintypes.LPVOID
PVOID = c_void_p
UINT = wintypes.UINT
WCHAR = wintypes.WCHAR
WORD = wintypes.WORD
LRESULT = wintypes.LPARAM

COLORREF = wintypes.COLORREF
LPBYTE = POINTER(BYTE)
LPWSTR = c_size_t #POINTER(WCHAR)
DWORD_PTR = UINT_PTR = ULONG_PTR = c_size_t
PDWORD_PTR = POINTER(DWORD_PTR)
if sysinfo.is_x64_Python():
    INT_PTR = LONG_PTR = c_longlong
else:
    INT_PTR = LONG_PTR = c_long

HINSTANCE = LONG_PTR #LONG
HMENU = LONG_PTR #LONG
HBRUSH = wintypes.HBRUSH  # LONG_PTR #LONG
HTREEITEM = LONG_PTR #LONG
HWND = wintypes.HWND

# Notice that wintypes definition of LPARAM/WPARAM differs between 32/64 bit
LPARAM = wintypes.LPARAM
WPARAM = wintypes.WPARAM


class POINT(wintypes.POINT, StructureMixIn):

    """Wrap the POINT structure and add extra functionality"""

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


assert sizeof(POINT) == 8, sizeof(POINT)
assert alignment(POINT) == 4, alignment(POINT)


# ====================================================================
class RECT(wintypes.RECT, StructureMixIn):

    """Wrap the RECT structure and add extra functionality"""

    # ----------------------------------------------------------------
    def __init__(self, otherRect_or_left=0, top=0, right=0, bottom=0):
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
        else:
            #if not isinstance(otherRect_or_left, (int, long)):
            #    print type(self), type(otherRect_or_left), otherRect_or_left
            long_int = six.integer_types[-1]
            self.left = long_int(otherRect_or_left)
            self.right = long_int(right)
            self.top = long_int(top)
            self.bottom = long_int(bottom)

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
        pt = POINT()
        pt.x = self.left + int(float(self.width()) / 2.)
        pt.y = self.top + int(float(self.height()) / 2.)
        return pt

    __reduce__ = _reduce


assert sizeof(RECT) == 16, sizeof(RECT)
assert alignment(RECT) == 4, alignment(RECT)


class SETTEXTEX(Structure):
    _pack_ = 1
    _fields_ = [
        ('flags', DWORD),
        ('codepage', UINT),
    ]
assert sizeof(SETTEXTEX) == 8, sizeof(SETTEXTEX)


class LVCOLUMNW(Structure):

    """The main layout for LVCOLUMN on x86 and x64 archs"""

    # _pack_ is not specified, we rely on a default alignment:
    # 8 bytes in x64 system and 4 bytes in x86
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2982
        ('mask', UINT),
        ('fmt', c_int),
        ('cx', c_int),
        ('pszText', c_void_p), #LPWSTR),
        ('cchTextMax', c_int),
        ('iSubItem', c_int),
        ('iImage', c_int),
        ('iOrder', c_int),
        ('cxMin', c_int),
        ('cxDefault', c_int),
        ('cxIdeal', c_int),
    ]


class LVCOLUMNW32(Structure):

    """A special layout for LVCOLUMN for a 32-bit process running on x64"""

    # _pack_ is not specified, we rely on a default alignment:
    # 8 bytes in x64 system and 4 bytes in x86
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2982
        ('mask', UINT),
        ('fmt', c_int),
        ('cx', c_int),
        ('pszText', UINT), # keep 4-byte size address
        ('cchTextMax', c_int),
        ('iSubItem', c_int),
        ('iImage', c_int),
        ('iOrder', c_int),
        ('cxMin', c_int),
        ('cxDefault', c_int),
        ('cxIdeal', c_int),
    ]


class LVITEMW(Structure):

    """The main layout for LVITEM, naturally fits for x86 and x64 archs"""

    # _pack_ is not specified, we rely on a default alignment:
    # 8 bytes on x64 system and 4 bytes on x86
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2679
        ('mask', UINT),
        ('iItem', c_int),
        ('iSubItem', c_int),
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', c_void_p), #LPTSTR), #c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('lParam', LPARAM),

        ('iIndent', c_int), #if (_WIN32_IE >= 0x0300)

        ('iGroupId', c_int), #if (_WIN32_WINNT >= 0x0501)
        ('cColumns', UINT),
        ('puColumns', POINTER(UINT)),

        ('piColFmt', POINTER(c_int)), #if (_WIN32_WINNT >= 0x0600)
        ('iGroup', c_int),
    ]

if sysinfo.is_x64_Python():
    assert sizeof(LVITEMW) == 88, sizeof(LVITEMW)
    assert alignment(LVITEMW) == 8, alignment(LVITEMW)
else:
    assert sizeof(LVITEMW) == 60, sizeof(LVITEMW)
    assert alignment(LVITEMW) == 4, alignment(LVITEMW)


class LVITEMW32(Structure):

    """A special layout for LVITEM for a 32-bit process running on x64"""

    _pack_  = 4
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2679
        ('mask', UINT),
        ('iItem', c_int),
        ('iSubItem', c_int),
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', UINT), # keep 4-byte size
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('lParam', LPARAM),

        ('iIndent', c_int), #if (_WIN32_IE >= 0x0300)

        ('iGroupId', c_int), #if (_WIN32_WINNT >= 0x0501)
        ('cColumns', UINT),
        ('puColumns', UINT), # keep 4-byte size

        ('piColFmt', c_int), #if (_WIN32_WINNT >= 0x0600), but keep 4-byte size
        ('iGroup', c_int),
    ]

assert alignment(LVITEMW32) == 4, alignment(LVITEMW32)


class TVITEMW(Structure):

    """The main layout for TVITEM, naturally fits for x86 and x64 archs"""

    #_pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 3755
        ('mask', UINT),
        ('hItem', HTREEITEM),
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', LPWSTR), #, c_long),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('iSelectedImage', c_int),
        ('cChildren', c_int),
        ('lParam', LPARAM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TVITEMW) == 56, sizeof(TVITEMW)
    assert alignment(TVITEMW) == 8, alignment(TVITEMW)
else:
    assert sizeof(TVITEMW) == 40, sizeof(TVITEMW)
    assert alignment(TVITEMW) == 4, alignment(TVITEMW)


class TVITEMW32(Structure):

    """An additional layout for TVITEM, used in a combination of 64-bit python and 32-bit app"""

    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 3755
        ('mask', UINT),
        ('hItem', UINT), # must be 4 bytes in 32-bit app
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', UINT), # must be 4 bytes in 32-bit app
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('iSelectedImage', c_int),
        ('cChildren', c_int),
        ('lParam', UINT), # must be 4 bytes in 32-bit app
    ]

assert sizeof(TVITEMW32) == 40, sizeof(TVITEMW32)
assert alignment(TVITEMW32) == 4, alignment(TVITEMW32)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2225
class NMHDR(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2225
        ('hwndFrom', HWND),
        ('idFrom', UINT_PTR),
        ('code', UINT),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(NMHDR) == 24, sizeof(NMHDR)
    assert alignment(NMHDR) == 8, alignment(NMHDR)
else:
    assert sizeof(NMHDR) == 12, sizeof(NMHDR)
    assert alignment(NMHDR) == 4, alignment(NMHDR)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4275
class NMTVDISPINFOW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4275
        ('hdr', NMHDR),
        ('item', TVITEMW),
    ]
#assert sizeof(NMTVDISPINFOW) == 52, sizeof(NMTVDISPINFOW)
assert alignment(NMTVDISPINFOW) == 1, alignment(NMTVDISPINFOW)


class LOGFONTW(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/wingdi.h 1090
        ('lfHeight', LONG),
        ('lfWidth', LONG),
        ('lfEscapement', LONG),
        ('lfOrientation', LONG),
        ('lfWeight', LONG),
        ('lfItalic', BYTE),
        ('lfUnderline', BYTE),
        ('lfStrikeOut', BYTE),
        ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE),
        ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE),
        ('lfPitchAndFamily', BYTE),
        ('lfFaceName', WCHAR * LF_FACESIZE),
    ]

    #----------------------------------------------------------------
    def __str__(self):
        return  "('%s' %d)" % (self.lfFaceName, self.lfHeight)

    #----------------------------------------------------------------
    def __repr__(self):
        return "<LOGFONTW '%s' %d>" % (self.lfFaceName, self.lfHeight)

LOGFONTW.__reduce__ = _reduce

assert sizeof(LOGFONTW) == 92, sizeof(LOGFONTW)
assert alignment(LOGFONTW) == 4, alignment(LOGFONTW)


class TEXTMETRICW(Structure):
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/wingdi.h 878
        ('tmHeight', LONG),
        ('tmAscent', LONG),
        ('tmDescent', LONG),
        ('tmInternalLeading', LONG),
        ('tmExternalLeading', LONG),
        ('tmAveCharWidth', LONG),
        ('tmMaxCharWidth', LONG),
        ('tmWeight', LONG),
        ('tmOverhang', LONG),
        ('tmDigitizedAspectX', LONG),
        ('tmDigitizedAspectY', LONG),
        ('tmFirstChar', WCHAR),
        ('tmLastChar', WCHAR),
        ('tmDefaultChar', WCHAR),
        ('tmBreakChar', WCHAR),
        ('tmItalic', BYTE),
        ('tmUnderlined', BYTE),
        ('tmStruckOut', BYTE),
        ('tmPitchAndFamily', BYTE),
        ('tmCharSet', BYTE),
    ]
assert sizeof(TEXTMETRICW) == 58, sizeof(TEXTMETRICW)
assert alignment(TEXTMETRICW) == 2, alignment(TEXTMETRICW)


class NONCLIENTMETRICSW(Structure):
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 8767
        ('cbSize', UINT),
        ('iBorderWidth', c_int),
        ('iScrollWidth', c_int),
        ('iScrollHeight', c_int),
        ('iCaptionWidth', c_int),
        ('iCaptionHeight', c_int),
        ('lfCaptionFont', LOGFONTW),
        ('iSmCaptionWidth', c_int),
        ('iSmCaptionHeight', c_int),
        ('lfSmCaptionFont', LOGFONTW),
        ('iMenuWidth', c_int),
        ('iMenuHeight', c_int),
        ('lfMenuFont', LOGFONTW),
        ('lfStatusFont', LOGFONTW),
        ('lfMessageFont', LOGFONTW),
    ]

assert sizeof(NONCLIENTMETRICSW) == 500, sizeof(NONCLIENTMETRICSW)
assert alignment(NONCLIENTMETRICSW) == 2, alignment(NONCLIENTMETRICSW)


# C:/PROGRA~1/MIAF9D~1/VC98/Include/wingdi.h 1025
class LOGBRUSH(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/wingdi.h 1025
        ('lbStyle', UINT),
        ('lbColor', COLORREF),
        ('lbHatch', LONG),
    ]
assert sizeof(LOGBRUSH) == 12, sizeof(LOGBRUSH)
assert alignment(LOGBRUSH) == 4, alignment(LOGBRUSH)

# C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 5147
class MENUITEMINFOW(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 5147
        ('cbSize', UINT),
        ('fMask', UINT),
        ('fType', UINT),
        ('fState', UINT),
        ('wID', UINT),
        ('hSubMenu', HMENU),
        ('hbmpChecked', HBITMAP),
        ('hbmpUnchecked', HBITMAP),
        ('dwItemData', ULONG_PTR), #DWORD),
        ('dwTypeData', LPWSTR),
        ('cch', UINT),
        ('hbmpItem', HBITMAP),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(MENUITEMINFOW) == 80, sizeof(MENUITEMINFOW)
    assert alignment(MENUITEMINFOW) == 8, alignment(MENUITEMINFOW)
else:
    assert sizeof(MENUITEMINFOW) == 48, sizeof(MENUITEMINFOW)
    assert alignment(MENUITEMINFOW) == 4, alignment(MENUITEMINFOW)

class MENUBARINFO(Structure):
    _fields_ = [
        ('cbSize',  DWORD),
        ('rcBar',  RECT),          # rect of bar, popup, item
        ('hMenu',  HMENU),          # real menu handle of bar, popup
        ('hwndMenu',  HWND),       # hwnd of item submenu if one
        ('fBarFocused',  BOOL, 1),  # bar, popup has the focus
        ('fFocused',  BOOL, 1),     # item has the focus
    ]


class MSG(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/winuser.h 1226
        ('hwnd', HWND),
        ('message', UINT),
        ('wParam', WPARAM),
        ('lParam', LPARAM),
        ('time', DWORD),
        ('pt', POINT),
]
if sysinfo.is_x64_Python():
    assert sizeof(MSG) == 48, sizeof(MSG)
    assert alignment(MSG) == 8, alignment(MSG)
else:
    assert sizeof(MSG) == 28, sizeof(MSG)
    assert alignment(MSG) == 4, alignment(MSG)


# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 1865
class TOOLINFOW(Structure):
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 1865
        ('cbSize', UINT),
        ('uFlags', UINT),
        ('hwnd', HWND),
        ('uId', UINT_PTR),
        ('rect', RECT),
        ('hinst', HINSTANCE),
        ('lpszText', LPWSTR), #c_long),
        ('lParam', LPARAM),
        ('lpReserved', LPVOID)
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TOOLINFOW) == 72, sizeof(TOOLINFOW)
    assert alignment(TOOLINFOW) == 8, alignment(TOOLINFOW)
else:
    assert sizeof(TOOLINFOW) == 48, sizeof(TOOLINFOW)
    assert alignment(TOOLINFOW) == 4, alignment(TOOLINFOW)


class HDITEMW(Structure):
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 617
        ('mask', UINT),
        ('cxy', c_int),
        ('pszText', LPWSTR), #c_long),
        ('hbm', HBITMAP),
        ('cchTextMax', c_int),
        ('fmt', c_int),
        ('lParam', LPARAM),
        ('iImage', c_int),
        ('iOrder', c_int),
        ('type', UINT),
        ('pvFilter', LPVOID),
        ('state', UINT)
    ]
if sysinfo.is_x64_Python():
    assert sizeof(HDITEMW) == 72, sizeof(HDITEMW)
    assert alignment(HDITEMW) == 8, alignment(HDITEMW)
else:
    assert sizeof(HDITEMW) == 48, sizeof(HDITEMW)
    assert alignment(HDITEMW) == 4, alignment(HDITEMW)


# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 4456
class COMBOBOXEXITEMW(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 4456
        ('mask', UINT),
        ('iItem', INT_PTR),
        ('pszText', LPWSTR), #c_long),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('iSelectedImage', c_int),
        ('iOverlay', c_int),
        ('iIndent', c_int),
        ('lParam', LPARAM),
]
if sysinfo.is_x64_Python():
    assert sizeof(COMBOBOXEXITEMW) == 56, sizeof(COMBOBOXEXITEMW)
    assert alignment(COMBOBOXEXITEMW) == 8, alignment(COMBOBOXEXITEMW)
else:
    assert sizeof(COMBOBOXEXITEMW) == 36, sizeof(COMBOBOXEXITEMW)
    assert alignment(COMBOBOXEXITEMW) == 4, alignment(COMBOBOXEXITEMW)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4757
class TCITEMHEADERW(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4757
        ('mask', UINT),
        ('lpReserved1', UINT),
        ('lpReserved2', UINT),
        ('pszText', LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TCITEMHEADERW) == 32, sizeof(TCITEMHEADERW)
    assert alignment(TCITEMHEADERW) == 8, alignment(TCITEMHEADERW)
else:
    assert sizeof(TCITEMHEADERW) == 24, sizeof(TCITEMHEADERW)
    assert alignment(TCITEMHEADERW) == 4, alignment(TCITEMHEADERW)

# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4804
class TCITEMW(Structure):
    #if sysinfo.is_x64_Python():
    #    _pack_ = 8
    #else:
    #    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4804
        ('mask', UINT),
        ('dwState', DWORD),
        ('dwStateMask', DWORD),
        ('pszText', LPWSTR), #c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('lParam', LPARAM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TCITEMW) == 40, sizeof(TCITEMW)
    assert alignment(TCITEMW) == 8, alignment(TCITEMW)
else:
    assert sizeof(TCITEMW) == 28, sizeof(TCITEMW)
    assert alignment(TCITEMW) == 4, alignment(TCITEMW)



# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1308
class TBBUTTONINFOW(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1308
        ('cbSize', UINT),
        ('dwMask', DWORD),
        ('idCommand', c_int),
        ('iImage', c_int),
        ('fsState', BYTE),
        ('fsStyle', BYTE),
        ('cx', WORD),
        ('lParam', POINTER(DWORD)),
        ('pszText', LPWSTR),
        ('cchText', c_int),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TBBUTTONINFOW) == 48, sizeof(TBBUTTONINFOW)
    assert alignment(TBBUTTONINFOW) == 8, alignment(TBBUTTONINFOW)
else:
    assert sizeof(TBBUTTONINFOW) == 32, sizeof(TBBUTTONINFOW)
    assert alignment(TBBUTTONINFOW) == 4, alignment(TBBUTTONINFOW)


class TBBUTTONINFOW32(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1308
        ('cbSize', UINT),
        ('dwMask', DWORD),
        ('idCommand', c_int),
        ('iImage', c_int),
        ('fsState', BYTE),
        ('fsStyle', BYTE),
        ('cx', WORD),
        ('lParam', UINT), # must be 4 bytes in 32-bit app
        ('pszText', UINT), # must be 4 bytes in 32-bit app
        ('cchText', c_int),
    ]
assert sizeof(TBBUTTONINFOW32) == 32, sizeof(TBBUTTONINFOW32)
assert alignment(TBBUTTONINFOW32) == 4, alignment(TBBUTTONINFOW32)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
if sysinfo.is_x64_Python():
    class TBBUTTON(Structure):
        #_pack_ = 1
        _fields_ = [
            # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
            ('iBitmap', c_int),
            ('idCommand', c_int),
            ('fsState', BYTE),
            ('fsStyle', BYTE),
            ('bReserved', BYTE * 6),
            ('dwData', DWORD_PTR),
            ('iString', INT_PTR),
        ]
else:
    class TBBUTTON(Structure):
        #_pack_ = 1
        _fields_ = [
            # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
            ('iBitmap', c_int),
            ('idCommand', c_int),
            ('fsState', BYTE),
            ('fsStyle', BYTE),
            ('bReserved', BYTE * 2),
            ('dwData', DWORD_PTR),
            ('iString', INT_PTR),
        ]
if sysinfo.is_x64_Python():
    assert sizeof(TBBUTTON) == 32, sizeof(TBBUTTON)
    assert alignment(TBBUTTON) == 8, alignment(TBBUTTON)
else:
    assert sizeof(TBBUTTON) == 20, sizeof(TBBUTTON)
    assert alignment(TBBUTTON) == 4, alignment(TBBUTTON)


class TBBUTTON32(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
        ('iBitmap', c_int),
        ('idCommand', c_int),
        ('fsState', BYTE),
        ('fsStyle', BYTE),
        ('bReserved', BYTE * 2),
        ('dwData', UINT), # must be 4 bytes in 32-bit app
        ('iString', UINT), # must be 4 bytes in 32-bit app
    ]
assert sizeof(TBBUTTON32) == 20, sizeof(TBBUTTON32)
assert alignment(TBBUTTON32) == 4, alignment(TBBUTTON32)


class REBARBANDINFOW(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1636
        ('cbSize', UINT),
        ('fMask', UINT),
        ('fStyle', UINT),
        ('clrFore', COLORREF),
        ('clrBack', COLORREF),
        ('lpText', LPWSTR),
        ('cch', UINT),
        ('iImage', c_int),
        ('hwndChild', HWND),
        ('cxMinChild', UINT),
        ('cyMinChild', UINT),
        ('cx', UINT),
        ('hbmBack', HBITMAP),
        ('wID', UINT),
        ('cyChild', UINT),
        ('cyMaxChild', UINT),
        ('cyIntegral', UINT),
        ('cxIdeal', UINT),
        ('lParam', LPARAM),
        ('cxHeader', UINT),
        # The fields below added for _WIN32_WINNT >= 0x0600 (Vista, Win7, ...)
        # It means that sizeof(REBARBANDINFOW) is wrong for WinXP
        ('rcChevronLocation', RECT), # the rect is in client co-ord wrt hwndChild
        ('uChevronState', UINT)
    ]
if sysinfo.is_x64_Python():
    assert sizeof(REBARBANDINFOW) == 128, sizeof(REBARBANDINFOW) #128
    assert alignment(REBARBANDINFOW) == 8, alignment(REBARBANDINFOW)
else:
    assert sizeof(REBARBANDINFOW) == 100, sizeof(REBARBANDINFOW) #100
    assert alignment(REBARBANDINFOW) == 4, alignment(REBARBANDINFOW)


# C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 223
class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 223
        ('nLength', DWORD),
        ('lpSecurityDescriptor', LPVOID),
        ('bInheritHandle', BOOL),
    ]
assert sizeof(SECURITY_ATTRIBUTES) == 12 or sizeof(SECURITY_ATTRIBUTES) == 24, sizeof(SECURITY_ATTRIBUTES)
assert alignment(SECURITY_ATTRIBUTES) == 4 or alignment(SECURITY_ATTRIBUTES) == 8, alignment(SECURITY_ATTRIBUTES)

# C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 3794
class STARTUPINFOW(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 3794
        ('cb', DWORD),
        ('lpReserved', LPWSTR),
        ('lpDesktop', LPWSTR),
        ('lpTitle', LPWSTR),
        ('dwX', DWORD),
        ('dwY', DWORD),
        ('dwXSize', DWORD),
        ('dwYSize', DWORD),
        ('dwXCountChars', DWORD),
        ('dwYCountChars', DWORD),
        ('dwFillAttribute', DWORD),
        ('dwFlags', DWORD),
        ('wShowWindow', WORD),
        ('cbReserved2', WORD),
        ('lpReserved2', LPBYTE),
        ('hStdInput', HANDLE),
        ('hStdOutput', HANDLE),
        ('hStdError', HANDLE),
    ]
assert sizeof(STARTUPINFOW) == 68 or sizeof(STARTUPINFOW) == 104, sizeof(STARTUPINFOW)
assert alignment(STARTUPINFOW) == 4 or alignment(STARTUPINFOW) == 8, alignment(STARTUPINFOW)

# C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 229
class PROCESS_INFORMATION(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 229
        ('hProcess', HANDLE),
        ('hThread', HANDLE),
        ('dwProcessId', DWORD),
        ('dwThreadId', DWORD),
    ]
assert sizeof(PROCESS_INFORMATION) == 16 or sizeof(PROCESS_INFORMATION) == 24, sizeof(PROCESS_INFORMATION)
assert alignment(PROCESS_INFORMATION) == 4 or alignment(PROCESS_INFORMATION) == 8, alignment(PROCESS_INFORMATION)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 3417
class NMLISTVIEW(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 3417
        ('hdr', NMHDR),
        ('iItem', c_int),
        ('iSubItem', c_int),
        ('uNewState', UINT),
        ('uOldState', UINT),
        ('uChanged', UINT),
        ('ptAction', POINT),
        ('lParam', LPARAM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(NMLISTVIEW) == 64, sizeof(NMLISTVIEW)
    assert alignment(NMLISTVIEW) == 8, alignment(NMLISTVIEW)
else:
    assert sizeof(NMLISTVIEW) == 44, sizeof(NMLISTVIEW)
    assert alignment(NMLISTVIEW) == 4, alignment(NMLISTVIEW)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 235
class NMMOUSE(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 235
        ('hdr', NMHDR),
        ('dwItemSpec', DWORD_PTR),
        ('dwItemData', DWORD_PTR),
        ('pt', POINT),
        ('dwHitInfo', LPARAM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(NMMOUSE) == 56, sizeof(NMMOUSE)
    assert alignment(NMMOUSE) == 8, alignment(NMMOUSE)
else:
    assert sizeof(NMMOUSE) == 32, sizeof(NMMOUSE)
    assert alignment(NMMOUSE) == 4, alignment(NMMOUSE)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4283
class MOUSEINPUT(Structure):
    if sysinfo.is_x64_Python():
        _pack_ = 8
    else:
        _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4283
        ('dx', LONG),
        ('dy', LONG),
        ('mouseData', DWORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', ULONG_PTR),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(MOUSEINPUT) == 32, sizeof(MOUSEINPUT)
    assert alignment(MOUSEINPUT) == 8, alignment(MOUSEINPUT)
else:
    assert sizeof(MOUSEINPUT) == 24, sizeof(MOUSEINPUT)
    assert alignment(MOUSEINPUT) == 2, alignment(MOUSEINPUT)

# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4292
class KEYBDINPUT(Structure):
    if sysinfo.is_x64_Python():
        _pack_ = 8
    else:
        _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4292
        ('wVk', WORD),
        ('wScan', WORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', ULONG_PTR),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(KEYBDINPUT) == 24, sizeof(KEYBDINPUT)
    assert alignment(KEYBDINPUT) == 8, alignment(KEYBDINPUT)
else:
    assert sizeof(KEYBDINPUT) == 16, sizeof(KEYBDINPUT)
    assert alignment(KEYBDINPUT) == 2, alignment(KEYBDINPUT)


class HARDWAREINPUT(Structure):
    if sysinfo.is_x64_Python():
        _pack_ = 8
    else:
        _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4300
        ('uMsg', DWORD),
        ('wParamL', WORD),
        ('wParamH', WORD),
    ]
assert sizeof(HARDWAREINPUT) == 8, sizeof(HARDWAREINPUT)
if sysinfo.is_x64_Python():
    assert alignment(HARDWAREINPUT) == 4, alignment(HARDWAREINPUT)
else:
    assert alignment(HARDWAREINPUT) == 2, alignment(HARDWAREINPUT)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4314
class UNION_INPUT_STRUCTS(Union):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4314
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(UNION_INPUT_STRUCTS) == 32, sizeof(UNION_INPUT_STRUCTS)
    assert alignment(UNION_INPUT_STRUCTS) == 8, alignment(UNION_INPUT_STRUCTS)
else:
    assert sizeof(UNION_INPUT_STRUCTS) == 24, sizeof(UNION_INPUT_STRUCTS)
    assert alignment(UNION_INPUT_STRUCTS) == 2, alignment(UNION_INPUT_STRUCTS)

# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4310
class INPUT(Structure):
    if sysinfo.is_x64_Python():
        _pack_ = 8
    else:
        _pack_ = 2
    _anonymous_ = ("_",)
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4310
        ('type', c_int),
        # Unnamed field renamed to '_'
        ('_', UNION_INPUT_STRUCTS),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(INPUT) == 40, sizeof(INPUT)
    assert alignment(INPUT) == 8, alignment(INPUT)
else:
    assert sizeof(INPUT) == 28, sizeof(INPUT)
    assert alignment(INPUT) == 2, alignment(INPUT)



# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 2415
class NMUPDOWN(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 2415
        ('hdr', NMHDR),
        ('iPos', c_int),
        ('iDelta', c_int),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(NMUPDOWN) == 32, sizeof(NMUPDOWN)
    assert alignment(NMUPDOWN) == 1, alignment(NMUPDOWN)
else:
    assert sizeof(NMUPDOWN) == 20, sizeof(NMUPDOWN)
    assert alignment(NMUPDOWN) == 1, alignment(NMUPDOWN)



# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 9821
class GUITHREADINFO(Structure):
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 9821
        ('cbSize', DWORD),
        ('flags', DWORD),
        ('hwndActive', HWND),
        ('hwndFocus', HWND),
        ('hwndCapture', HWND),
        ('hwndMenuOwner', HWND),
        ('hwndMoveSize', HWND),
        ('hwndCaret', HWND),
        ('rcCaret', RECT),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(GUITHREADINFO) == 72, sizeof(GUITHREADINFO)
    assert alignment(GUITHREADINFO) == 2, alignment(GUITHREADINFO)
else:
    assert sizeof(GUITHREADINFO) == 48, sizeof(GUITHREADINFO)
    assert alignment(GUITHREADINFO) == 2, alignment(GUITHREADINFO)



# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 5043
class MENUINFO(Structure):
    #_pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 5043
        ('cbSize', DWORD),
        ('fMask', DWORD),
        ('dwStyle', DWORD),
        ('cyMax', UINT),
        ('hbrBack', HBRUSH),
        ('dwContextHelpID', DWORD),
        ('dwMenuData', ULONG_PTR),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(MENUINFO) == 40, sizeof(MENUINFO)
    assert alignment(MENUINFO) == 8, alignment(MENUINFO)
else:
    assert sizeof(MENUINFO) == 28, sizeof(MENUINFO)
    assert alignment(MENUINFO) == 4, alignment(MENUINFO)



# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2068
# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 2066
class NMTTDISPINFOW(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2068
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 2066
        ('hdr', NMHDR),
        ('lpszText', LPWSTR),
        ('szText', WCHAR * 80),
        ('hinst', HINSTANCE),
        ('uFlags', UINT),
        ('lParam', LPARAM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(NMTTDISPINFOW) == 216, sizeof(NMTTDISPINFOW)
    assert alignment(NMTTDISPINFOW) == 8, alignment(NMTTDISPINFOW)
else:
    assert sizeof(NMTTDISPINFOW) == 188, sizeof(NMTTDISPINFOW)
    assert alignment(NMTTDISPINFOW) == 4, alignment(NMTTDISPINFOW)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2208
class WINDOWPLACEMENT(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2208
        ('length', UINT),
        ('flags', UINT),
        ('showCmd', UINT),
        ('ptMinPosition', POINT),
        ('ptMaxPosition', POINT),
        ('rcNormalPosition', RECT),
    ]
assert sizeof(WINDOWPLACEMENT) == 44, sizeof(WINDOWPLACEMENT)
assert alignment(WINDOWPLACEMENT) == 4, alignment(WINDOWPLACEMENT)

# TODO: use it for clicking on "check" icon etc.
class LVHITTESTINFO(Structure):
    #_pack_ = 1
    _fields_ = [
        # https://msdn.microsoft.com/en-us/library/windows/desktop/bb774754(v=vs.85).aspx
        ('pt', POINT),
        ('flags', UINT),
        ('iItem', c_int),
        ('iSubItem', c_int),
        ('iGroup', c_int),
    ]
assert sizeof(LVHITTESTINFO) == 24, sizeof(LVHITTESTINFO)
assert alignment(LVHITTESTINFO) == 4, alignment(LVHITTESTINFO)


# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4052
class TVHITTESTINFO(Structure):
    #_pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4052
        ('pt', POINT),
        ('flags', UINT),
        ('hItem', HTREEITEM),
    ]
if sysinfo.is_x64_Python():
    assert sizeof(TVHITTESTINFO) == 24, sizeof(TVHITTESTINFO)
    assert alignment(TVHITTESTINFO) == 8, alignment(TVHITTESTINFO)
else:
    assert sizeof(TVHITTESTINFO) == 16, sizeof(TVHITTESTINFO)
    assert alignment(TVHITTESTINFO) == 4, alignment(TVHITTESTINFO)


class LOGFONTA(Structure):
    _fields_ = [
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG),
        ('lfHeight', LONG)
        ]


class GV_ITEM(Structure):
    _pack_ = 1
    _fields_ = [
        ('row', c_int),
        ('col', c_int),
        ('mask', UINT),
        ('state', UINT),
        ('nFormat', UINT)
    ]
#assert sizeof(LVITEMW) == 40, sizeof(LVITEMW)
#assert alignment(LVITEMW) == 1, alignment(LVITEMW)

class SYSTEMTIME(Structure):

    """Wrap the SYSTEMTIME structure"""

    _fields_ = [
        ('wYear', WORD),
        ('wMonth', WORD),
        ('wDayOfWeek', WORD),
        ('wDay', WORD),
        ('wHour', WORD),
        ('wMinute', WORD),
        ('wSecond', WORD),
        ('wMilliseconds', WORD),
    ]

    def __repr__(self):
        return '<wYear=' + str(self.wYear) + \
            ', wMonth=' + str(self.wMonth) + \
            ', wDayOfWeek=' + str(self.wDayOfWeek) + \
            ', wDay=' + str(self.wDay) + \
            ', wHour=' + str(self.wHour) + \
            ', wMinute=' + str(self.wMinute) + \
            ', wSecond=' + str(self.wSecond) + \
            ', wMilliseconds=' + str(self.wMilliseconds) + '>'

    def __str__(self):
        return self.__repr__()

assert sizeof(SYSTEMTIME) == 16, sizeof(SYSTEMTIME)

class MCHITTESTINFO(Structure):
    _fields_ = [
        ('cbSize', UINT),
        ('pt', POINT),
        ('uHit', UINT),
        ('st', SYSTEMTIME),
        ('rc', RECT),
        ('iOffset', c_int),
        ('iRow', c_int),
        ('iCol', c_int)
    ]


class KBDLLHOOKSTRUCT(Structure):

    """Wrap KBDLLHOOKSTRUCT structure"""

    _fields_ = [
        ('vkCode', DWORD),
        ('scanCode', DWORD),
        ('flags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', DWORD),
    ]

assert sizeof(KBDLLHOOKSTRUCT) == 20, sizeof(KBDLLHOOKSTRUCT)


class MSLLHOOKSTRUCT(Structure):

    """Wrap MSLLHOOKSTRUCT structure"""

    _fields_ = [
        ('pt', POINT),
        ('mouseData', DWORD),
        ('flags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', DWORD),
    ]

assert sizeof(MSLLHOOKSTRUCT) == 24, sizeof(MSLLHOOKSTRUCT)
