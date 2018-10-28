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

"""Some clipboard wrapping functions - more to be added later"""

import win32clipboard


#====================================================================
def _get_standard_formats():
    """Get the known formats by looking in win32clipboard"""
    formats = {}
    for define_name in win32clipboard.__dict__.keys():
        if define_name.startswith("CF_"):
            formats[getattr(win32clipboard, define_name)] = define_name
    return formats

# get all the formats names keyed on the value
_standard_formats = _get_standard_formats()


#====================================================================
def GetClipboardFormats():
    """Get a list of the formats currently in the clipboard"""
    win32clipboard.OpenClipboard()

    available_formats = []
    current_format = 0
    while True:
        # retrieve the next format
        current_format = win32clipboard.EnumClipboardFormats(current_format)

        # stop enumerating because all formats have been
        # retrieved
        if not current_format:
            break

        available_formats.append(current_format)

    win32clipboard.CloseClipboard()

    return available_formats


#====================================================================
def GetFormatName(format_id):
    """Get the string name for a format value"""
    # standard formats should not be passed to GetClipboardFormatName
    if format_id in _standard_formats:
        return _standard_formats[format_id]

    win32clipboard.OpenClipboard()
    format_name = win32clipboard.GetClipboardFormatName(format_id)
    win32clipboard.CloseClipboard()

    return format_name


#====================================================================
def GetData(format_id = win32clipboard.CF_UNICODETEXT):
    """Return the data from the clipboard in the requested format"""
    if format_id not in GetClipboardFormats():
        raise RuntimeError("That format is not available")

    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(format_id)
    finally:
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
