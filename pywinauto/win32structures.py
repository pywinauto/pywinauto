# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"Definition of Windows structures"

__revision__ = "$Revision$"

from win32defines import LF_FACESIZE, NMTTDISPINFOW_V1_SIZE, HDITEMW_V1_SIZE

import ctypes
from ctypes import (
    c_int, c_uint, c_long, c_ulong, c_void_p, c_wchar, c_char,
    c_ubyte, c_ushort, c_wchar_p,
    POINTER, sizeof, alignment)


class Structure(ctypes.Structure):
    #----------------------------------------------------------------
    def __str__(self):
        """Print out the fields of the ctypes Structure

        fields in exceptList will not be printed"""

        lines = []
        for f in self._fields_:
            name = f[0]
            lines.append("%20s\t%s"% (name, getattr(self, name)))

        return "\n".join(lines)

    #----------------------------------------------------------------
    def __eq__(self, other_struct):
        "return true if the two rectangles have the same coordinates"

        try:
            are_equal = True
            for field in self._fields_:
                name = field[0]
                if getattr(self, name) != getattr(other_struct, name):
                    are_equal = False
                    break

            return are_equal

        except AttributeError:
            return False

##====================================================================
#def PrintCtypesStruct(struct, exceptList = []):
#    """Print out the fields of the ctypes Structure
#
#    fields in exceptList will not be printed"""
#    for f in struct._fields_:
#        name = f[0]
#        if name in exceptList:
#            continue
#        print "%20s "% name, getattr(struct, name)



#LPTTTOOLINFOW = POINTER(tagTOOLINFOW)
#PTOOLINFOW = POINTER(tagTOOLINFOW)
BOOL = c_int
BYTE = c_ubyte
CHAR = c_char
DWORD = c_ulong
HANDLE = c_void_p
HBITMAP = c_long
LONG = c_long
LPARAM = LONG
LPVOID = c_void_p
PVOID = c_void_p
UINT = c_uint
WCHAR = c_wchar
WORD = c_ushort
WPARAM = UINT


COLORREF = DWORD
HBITMAP = LONG
HINSTANCE = LONG
HMENU = LONG
HTREEITEM = LONG
HWND = LONG
LPARAM = LONG
LPBYTE = POINTER(BYTE)
LPWSTR = c_long# POINTER(WCHAR)





class POINT(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/windef.h 307
        ('x', LONG),
        ('y', LONG),
    ]
assert sizeof(POINT) == 8, sizeof(POINT)
assert alignment(POINT) == 4, alignment(POINT)



#====================================================================
class RECT(Structure):
    "Wrap the RECT structure and add extra functionality"
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/windef.h 287
        ('left', LONG),
        ('top', LONG),
        ('right', LONG),
        ('bottom', LONG),
    ]

    #----------------------------------------------------------------
    def __init__(self, otherRect_or_left = 0, top = 0, right = 0, bottom = 0):
        """Provide a constructor for RECT structures

        A RECT can be constructed by:
        - Another RECT (each value will be copied)
        - Values for left, top, right and bottom

        e.g. my_rect = RECT(otherRect)
        or   my_rect = RECT(10, 20, 34, 100)
        """
        if type(otherRect_or_left) == type(self):
            self.left = otherRect_or_left.left
            self.right = otherRect_or_left.right
            self.top = otherRect_or_left.top
            self.bottom = otherRect_or_left.bottom
        else:
            self.left = long(otherRect_or_left)
            self.right = long(right)
            self.top = long(top)
            self.bottom = long(bottom)


#    #----------------------------------------------------------------
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

    #----------------------------------------------------------------
    def __str__(self):
        "Return a string representation of the RECT"
        return "(L%d, T%d, R%d, B%d)" % (
            self.left, self.top, self.right, self.bottom)

    #----------------------------------------------------------------
    def __repr__(self):
        "Return some representation of the RECT"
        return "<RECT L%d, T%d, R%d, B%d>" % (
            self.left, self.top, self.right, self.bottom)

    #----------------------------------------------------------------
    def __sub__(self, other):
        "Return a new rectangle which is offset from the one passed in"
        newRect = RECT()

        newRect.left = self.left - other.left
        newRect.right = self.right - other.left

        newRect.top = self.top - other.top
        newRect.bottom = self.bottom - other.top

        return newRect

    #----------------------------------------------------------------
    def __add__(self, other):
        "Allow two rects to be added using +"
        newRect = RECT()

        newRect.left = self.left + other.left
        newRect.right = self.right + other.left

        newRect.top = self.top + other.top
        newRect.bottom = self.bottom + other.top

        return newRect

    #----------------------------------------------------------------
    def width(self):
        "Return the width of the  rect"
        return self.right - self.left

    #----------------------------------------------------------------
    def height(self):
        "Return the height of the rect"
        return self.bottom - self.top

    #def __hash__(self):
    #	return hash (self.left, self.top, self.right, self.bottom)


assert sizeof(RECT) == 16, sizeof(RECT)
assert alignment(RECT) == 4, alignment(RECT)


class LVCOLUMNW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2982
        ('mask', UINT),
        ('fmt', c_int),
        ('cx', c_int),
        ('pszText', c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iSubItem', c_int),
        ('iImage', c_int),
        ('iOrder', c_int),
    ]


class LVITEMW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2679
        ('mask', UINT),
        ('iItem', c_int),
        ('iSubItem', c_int),
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('lParam', LPARAM),
        ('iIndent', c_int),
    ]
assert sizeof(LVITEMW) == 40, sizeof(LVITEMW)
assert alignment(LVITEMW) == 1, alignment(LVITEMW)



class TVITEMW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 3755
        ('mask', UINT),
        ('hItem', HTREEITEM),
        ('state', UINT),
        ('stateMask', UINT),
        ('pszText', c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('iSelectedImage', c_int),
        ('cChildren', c_int),
        ('lParam', LPARAM),
    ]
assert sizeof(TVITEMW) == 40, sizeof(TVITEMW)
assert alignment(TVITEMW) == 1, alignment(TVITEMW)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2225
class NMHDR(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 2225
        ('hwndFrom', HWND),
        ('idFrom', UINT),
        ('code', UINT),
    ]
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
assert sizeof(NMTVDISPINFOW) == 52, sizeof(NMTVDISPINFOW)
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
    _pack_ = 2
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
        ('dwItemData', DWORD),
        ('dwTypeData', c_wchar_p), #LPWSTR),
        ('cch', UINT),
    ]
assert sizeof(MENUITEMINFOW) == 44, sizeof(MENUITEMINFOW)
assert alignment(MENUITEMINFOW) == 2, alignment(MENUITEMINFOW)



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

assert sizeof(MSG) == 28, sizeof(MSG)
assert alignment(MSG) == 4, alignment(MSG)









# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 1865
class TOOLINFOW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 1865
        ('cbSize', UINT),
        ('uFlags', UINT),
        ('hwnd', HWND),
        ('uId', UINT),
        ('rect', RECT),
        ('hinst', HINSTANCE),
        ('lpszText', c_long),#LPWSTR),
        ('lParam', LPARAM),
    ]
assert sizeof(TOOLINFOW) == 44, sizeof(TOOLINFOW)
assert alignment(TOOLINFOW) == 1, alignment(TOOLINFOW)






# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2068
class NMTTDISPINFOW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 2068
        ('hdr', NMHDR),
        ('lpszText', LPWSTR),
        ('szText', WCHAR * 80),
        ('hinst', HINSTANCE),
        ('uFlags', UINT),
        ('lParam', LPARAM),
    ]

assert sizeof(NMTTDISPINFOW) == 188, sizeof(NMTTDISPINFOW)
assert alignment(NMTTDISPINFOW) == 1, alignment(NMTTDISPINFOW)



class HDITEMW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 617
        ('mask', UINT),
        ('cxy', c_int),
        ('pszText', c_long),#LPWSTR),
        ('hbm', HBITMAP),
        ('cchTextMax', c_int),
        ('fmt', c_int),
        ('lParam', LPARAM),
        ('iImage', c_int),
        ('iOrder', c_int),
    ]
assert sizeof(HDITEMW) == 36, sizeof(HDITEMW)
assert alignment(HDITEMW) == 1, alignment(HDITEMW)






# C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 4456
class COMBOBOXEXITEMW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/_tools/Python24/Lib/site-packages/ctypes/wrap/test/commctrl.h 4456
        ('mask', UINT),
        ('iItem', c_int),
        ('pszText', c_long),#LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('iSelectedImage', c_int),
        ('iOverlay', c_int),
        ('iIndent', c_int),
        ('lParam', LPARAM),
]
assert sizeof(COMBOBOXEXITEMW) == 36, sizeof(COMBOBOXEXITEMW)
assert alignment(COMBOBOXEXITEMW) == 1, alignment(COMBOBOXEXITEMW)




# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4757
class TCITEMHEADERW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4757
        ('mask', UINT),
        ('lpReserved1', UINT),
        ('lpReserved2', UINT),
        ('pszText', LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
    ]

assert sizeof(TCITEMHEADERW) == 24, sizeof(TCITEMHEADERW)
assert alignment(TCITEMHEADERW) == 1, alignment(TCITEMHEADERW)

# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4804
class TCITEMW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 4804
        ('mask', UINT),
        ('dwState', DWORD),
        ('dwStateMask', DWORD),
        ('pszText', c_long), #LPWSTR),
        ('cchTextMax', c_int),
        ('iImage', c_int),
        ('lParam', LPARAM),
    ]
assert sizeof(TCITEMW) == 28, sizeof(TCITEMW)
assert alignment(TCITEMW) == 1, alignment(TCITEMW)



# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1308
class TBBUTTONINFOW(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 1308
        ('cbSize', UINT),
        ('dwMask', DWORD),
        ('idCommand', c_int),
        ('iImage', c_int),
        ('fsState', BYTE),
        ('fsStyle', BYTE),
        ('cx', WORD),
        ('lParam', DWORD),
        ('pszText', LPWSTR),
        ('cchText', c_int),
    ]
assert sizeof(TBBUTTONINFOW) == 32, sizeof(TBBUTTONINFOW)
assert alignment(TBBUTTONINFOW) == 1, alignment(TBBUTTONINFOW)

# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
class TBBUTTON(Structure):
    _pack_ = 1
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 953
        ('iBitmap', c_int),
        ('idCommand', c_int),
        ('fsState', BYTE),
        ('fsStyle', BYTE),
        ('bReserved', BYTE * 2),
        ('dwData', DWORD),
        ('iString', c_int),
    ]
assert sizeof(TBBUTTON) == 20, sizeof(TBBUTTON)
assert alignment(TBBUTTON) == 1, alignment(TBBUTTON)



class REBARBANDINFOW(Structure):
    _pack_ = 1
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
    ]
assert sizeof(REBARBANDINFOW) == 80, sizeof(REBARBANDINFOW)
assert alignment(REBARBANDINFOW) == 1, alignment(REBARBANDINFOW)







# C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 223
class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 223
        ('nLength', DWORD),
        ('lpSecurityDescriptor', LPVOID),
        ('bInheritHandle', BOOL),
    ]
assert sizeof(SECURITY_ATTRIBUTES) == 12, sizeof(SECURITY_ATTRIBUTES)
assert alignment(SECURITY_ATTRIBUTES) == 4, alignment(SECURITY_ATTRIBUTES)

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
assert sizeof(STARTUPINFOW) == 68, sizeof(STARTUPINFOW)
assert alignment(STARTUPINFOW) == 4, alignment(STARTUPINFOW)

# C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 229
class PROCESS_INFORMATION(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 229
        ('hProcess', HANDLE),
        ('hThread', HANDLE),
        ('dwProcessId', DWORD),
        ('dwThreadId', DWORD),
    ]
assert sizeof(PROCESS_INFORMATION) == 16, sizeof(PROCESS_INFORMATION)
assert alignment(PROCESS_INFORMATION) == 4, alignment(PROCESS_INFORMATION)



# C:/PROGRA~1/MICROS~4/VC98/Include/commctrl.h 3417
class NMLISTVIEW(Structure):
    _pack_ = 1
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
assert sizeof(NMLISTVIEW) == 44, sizeof(NMLISTVIEW)
assert alignment(NMLISTVIEW) == 1, alignment(NMLISTVIEW)

