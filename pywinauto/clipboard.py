# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2010 Mark Mc Mahon
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

import win32clipboard


#====================================================================
def _get_standard_formats():
    "Get the known formats by looking in win32clipboard"
    formats = {}
    for define_name in win32clipboard.__dict__.keys():
        if define_name.startswith("CF_"):
            formats[getattr(win32clipboard, define_name)] = define_name
    return formats

# get all the formats names keyed on the value
_standard_formats = _get_standard_formats()


#====================================================================
def GetClipboardFormats():
    "Get a list of the formats currently in the clipboard"
    win32clipboard.OpenClipboard()
    
    available_formats = []
    format = 0
    while True:
        # retrieve the next format
        format = win32clipboard.EnumClipboardFormats(format)

        # stop enumerating because all formats have been
        # retrieved
        if not format:
            break

        available_formats.append(format)

    win32clipboard.CloseClipboard()

    return available_formats


#====================================================================
def GetFormatName(format):
    "Get the string name for a format value"

    # standard formats should not be passed to GetClipboardFormatName
    if format in _standard_formats:
        return _standard_formats[format]

    win32clipboard.OpenClipboard()
    format_name = win32clipboard.GetClipboardFormatName(format)
    win32clipboard.CloseClipboard()

    return format_name


#====================================================================
def GetData(format = win32clipboard.CF_UNICODETEXT):
    "Return the data from the clipboard in the requested format"
    if format not in GetClipboardFormats():
        raise RuntimeError("That format is not available")

    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData(format)
    win32clipboard.CloseClipboard()

    return data


#====================================================================
def EmptyClipboard():
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.CloseClipboard()


#====================================================================
# Todo: Implement setting clipboard data
#def SetData(data, formats = [win32clipboard.CF_UNICODETEXT, ]):
#    pass


#====================================================================
#if __name__ == "__main__":
#    _unittests()
