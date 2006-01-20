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

"Some clipboard wrapping functions - more to be added later"

__revision__ = "$Revision$"

import win32functions
import win32defines

import ctypes

# get all the formats names keyed on the value
all_formats = {}
for x in win32defines.__dict__.keys():
    if x.startswith("CF_"):
        all_formats[getattr(win32defines, x)] = x


#====================================================================
def GetClipboardFormats():
    "Get a list of the formats currently in the clipboard"
    if not win32functions.OpenClipboard(0):
        raise RuntimeError("Couldn't open clipboard")

    availableFormats = []
    format = 0
    while True:
        # retrieve the next format
        format = win32functions.EnumClipboardFormats(format)

        # stop enumerating because all formats have been
        # retrieved
        if not format:
            break

        availableFormats.append(format)

    win32functions.CloseClipboard()

    return availableFormats


#====================================================================
def GetFormatName(format):
    "Get the string name for a format value"
    return all_formats[format]


#====================================================================
def GetData(format = win32defines.CF_UNICODETEXT):
    "Return the data from the clipboard in the requested format"
    if not win32functions.OpenClipboard(0):
        raise RuntimeError("Couldn't open clipboard")

    handle = win32functions.GetClipboardData(format)

    buffer_ = ctypes.c_wchar_p(win32functions.GlobalLock(handle))

    data = buffer_.value

    win32functions.GlobalUnlock(handle)

    return data


#====================================================================
if __name__ == "__main__":
    formats = GetClipboardFormats()
    print formats

    print [GetFormatName(f) for f in formats]

    print repr(GetData())
