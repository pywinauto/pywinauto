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

# pylint: disable-msg=W0611

"""Truncation Test

**What is checked**
Checks for controls where the text does not fit in the space provided by the
control.

**How is it checked**
There is a function in windows (DrawText) that allows us to find the size that
certain text will need. We use this function with correct fonts and other
relevant information for the control to be as accurate as possible.

**When is a bug reported**
When the calculated required size for the text is greater than the size of the
space available for displaying the text.

**Bug Extra Information**
The bug contains the following extra information
Name	Description
Strings		The list of the truncated strings as explained above
StringIndices		The list of indices (0 based) that are truncated. This
will often just be 0 but if there are many strings in the control untranslated
it will report ALL the strings e.g. 0,2,5,19,23


**Is Reference dialog needed**
The reference dialog does not need to be available. If it is available then
for each bug discovered it is checked to see if it is a problem in the
reference dialog.

**False positive bug reports**
Certain controls do not display the text that is the title of the control, if
this is not handled in a standard manner by the software then DLGCheck will
report that the string is truncated.

**Test Identifier**
The identifier for this test/bug is "Truncation"
"""

testname = "Truncation"

import ctypes
import six

from pywinauto import win32defines
from pywinauto import win32functions
from pywinauto import win32structures


#==============================================================================
def TruncationTest(windows):
    """Actually do the test"""
    truncations = []

    # for each of the windows in the dialog
    for win in windows:

        truncIdxs, truncStrings = _FindTruncations(win)

        isInRef = -1

        # if there were any truncations for this control
        if truncIdxs:

            # now that we know there was at least one truncation
            # check if the reference control has truncations
            if win.ref:
                isInRef = 0
                refTruncIdxs, refTruncStrings = _FindTruncations(win.ref)

                if refTruncIdxs:
                    isInRef = 1

            truncIdxs = ",".join([six.text_type(index) for index in truncIdxs])
            truncStrings = '"%s"' % ",".join(
                [six.text_type(string) for string in truncStrings])
            truncations.append((
                [win,],
                {
                    "StringIndices": truncIdxs,
                    "Strings": truncStrings,
                },
                testname,
                isInRef)
            )

    # return all the truncations
    return truncations

#==============================================================================
def _FindTruncations(ctrl):
    """Return the index of the texts that are truncated for this control"""
    truncIdxs = []
    truncStrings = []

    # for each of the titles this dialog
    for idx, (text, rect, font, flags) in enumerate(_GetTruncationInfo(ctrl)):

        # skip if there is no text
        if not text:
            continue

        # get the minimum rectangle
        minRect = _GetMinimumRect(text, font, rect, flags)

        # if the min rectangle is bigger than the rectangle of the
        # object
        if minRect.right > rect.right or \
            minRect.bottom > rect.bottom:

            # append the index and the rectangle to list of bug items
            truncIdxs.append(idx)
            truncStrings.append(text)

            #print "%s'\n\tRECT: %s\n\t MIN: %s" %(text, rect, minRect)

    return truncIdxs, truncStrings



#==============================================================================
def _GetMinimumRect(text, font, usableRect, drawFlags):
    """Return the minimum rectangle that the text will fit into

    Uses font, usableRect and drawFlags information to find how
    to do it accurately.
    """

    # try to create the font
    # create a Display DC (compatible to the screen)
    txtDC = win32functions.CreateDC(u"DISPLAY", None, None, None )

    hFontGUI = win32functions.CreateFontIndirect(ctypes.byref(font))

#    # Maybe we could not get the font or we got the system font
#    if not hFontGUI:
#
#        # So just get the default system font
#        hFontGUI = win32functions.GetStockObject(win32defines.DEFAULT_GUI_FONT)
#
#        # if we still don't have a font!
#        # ----- ie, we're on an antiquated OS, like NT 3.51
#        if not hFontGUI:
#
#            # ----- On Asian platforms, ANSI font won't show.
#            if win32functions.GetSystemMetrics(win32defines.SM_DBCSENABLED):
#                # ----- was...(SYSTEM_FONT)
#                hFontGUI = win32functions.GetStockObject(
#                    win32defines.SYSTEM_FONT)
#            else:
#                # ----- was...(SYSTEM_FONT)
#                hFontGUI = win32functions.GetStockObject(
#                    win32defines.ANSI_VAR_FONT)

    # put our font into the Device Context
    win32functions.SelectObject (txtDC, hFontGUI)

    modifiedRect = win32structures.RECT(usableRect)
    # Now write the text to our DC with our font to get the
    # rectangle that the text needs to fit in
    win32functions.DrawText (txtDC, # The DC
        six.text_type(text),		# The Title of the control
        -1,			# -1 because sTitle is NULL terminated
        ctypes.byref(modifiedRect),	# The rectangle to be calculated to
        #truncCtrlData.drawTextFormat |
        win32defines.DT_CALCRECT | drawFlags)

    #elif modifiedRect.right == usableRect.right and \
    #	modifiedRect.bottom == usableRect.bottom:
    #	print "Oh so you thought you were perfect!!!"


    # Delete the font we created
    win32functions.DeleteObject(hFontGUI)

    # delete the Display context that we created
    win32functions.DeleteDC(txtDC)

    return modifiedRect




#==============================================================================
def _GroupBoxTruncInfo(win):
    """Return truncation information specific to Button controls"""
    lineFormat = win32defines.DT_SINGLELINE

    heightAdj = 4
    widthAdj = 9

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.has_style(win32defines.BS_BITMAP) or \
        win.has_style(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.client_rects()[0]
    newRect.right -=  widthAdj
    newRect.bottom -=  heightAdj

    return [(win.window_text(), newRect, win.font(), lineFormat), ]


#==============================================================================
def _RadioButtonTruncInfo(win):
    """Return truncation information specific to Button controls"""
    lineFormat = win32defines.DT_SINGLELINE

    if win.has_style(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK

    widthAdj = 19

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.has_style(win32defines.BS_BITMAP) or \
        win.has_style(win32defines.BS_ICON):
        #unused var: heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.client_rects()[0]
    newRect.right -=  widthAdj

    return [(win.window_text(), newRect, win.font(), lineFormat), ]


#==============================================================================
def _CheckBoxTruncInfo(win):
    """Return truncation information specific to Button controls"""
    lineFormat = win32defines.DT_SINGLELINE

    if win.has_style(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK

    widthAdj = 18

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.has_style(win32defines.BS_BITMAP) or \
        win.has_style(win32defines.BS_ICON):
        #unused var: heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.client_rects()[0]
    newRect.right -=  widthAdj

    return [(win.window_text(), newRect, win.font(), lineFormat), ]


#==============================================================================
def _ButtonTruncInfo(win):
    """Return truncation information specific to Button controls"""
    lineFormat = win32defines.DT_SINGLELINE

    if win.has_style(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK

    heightAdj = 4
    widthAdj = 5

    if win.has_style(win32defines.BS_PUSHLIKE):
        widthAdj = 3
        heightAdj = 3 # 3
        if win.has_style(win32defines.BS_MULTILINE):
            widthAdj = 9
            heightAdj = 2 # 3

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.has_style(win32defines.BS_BITMAP) or \
        win.has_style(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.client_rects()[0]
    newRect.right -=  widthAdj
    newRect.bottom -=  heightAdj

    return [(win.window_text(), newRect, win.font(), lineFormat), ]

#==============================================================================
def _ComboBoxTruncInfo(win):
    """Return truncation information specific to ComboBox controls"""
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    if win.has_style(win32defines.CBS_DROPDOWN) or \
        win.has_style(win32defines.CBS_DROPDOWNLIST):
        widthAdj = 2#5
    else:
        widthAdj = 3

    truncData = []
    for title in win.texts():
        newRect = win.client_rects()[0]
        newRect.right -= widthAdj
        truncData.append((title, newRect, win.font(), lineFormat))

    return truncData

#==============================================================================
def _ComboLBoxTruncInfo(win):
    """Return truncation information specific to ComboLBox controls"""
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    truncData = []
    for title in win.texts():
        newRect = win.client_rects()[0]
        newRect.right -= 5
        truncData.append((title, newRect, win.font(), lineFormat))

    return truncData


#==============================================================================
def _ListBoxTruncInfo(win):
    """Return truncation information specific to ListBox controls"""
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    truncData = []
    for title in win.texts():
        newRect = win.client_rects()[0]
        newRect.right -= 2
        newRect.bottom -= 1
        truncData.append((title, newRect, win.font(), lineFormat))

    return truncData


#==============================================================================
def _StaticTruncInfo(win):
    """Return truncation information specific to Static controls"""
    lineFormat = win32defines.DT_WORDBREAK

    if win.has_style(win32defines.SS_CENTERIMAGE) or \
            win.has_style(win32defines.SS_SIMPLE) or \
            win.has_style(win32defines.SS_LEFTNOWORDWRAP) and \
            "WindowsForms" not in win.class_name():

        lineFormat = win32defines.DT_SINGLELINE

    if win.has_style(win32defines.SS_NOPREFIX):
        lineFormat |= win32defines.DT_NOPREFIX

    return [(win.window_text(), win.client_rects()[0], win.font(), lineFormat), ]

#==============================================================================
def _EditTruncInfo(win):
    """Return truncation information specific to Edit controls"""
    lineFormat = win32defines.DT_WORDBREAK | win32defines.DT_NOPREFIX

    if not win.has_style(win32defines.ES_MULTILINE):
        lineFormat |= win32defines.DT_SINGLELINE

    return [(win.window_text(), win.client_rects()[0], win.font(), lineFormat), ]


#==============================================================================
def _DialogTruncInfo(win):
    """Return truncation information specific to Header controls"""
    # move it down more into range

    newRect = win.client_rects()[0]

    newRect.top += 5
    newRect.left += 5
    newRect.right -= 5


    if win.has_style(win32defines.WS_THICKFRAME):
        newRect.top += 1
        newRect.left += 1
        newRect.right -= 1

    # if it has the system menu but is a small caption
    # then the only button it can have is the close button
    if win.has_style(win32defines.WS_SYSMENU) and \
        (win.HasExStyle(win32defines.WS_EX_PALETTEWINDOW) or
        win.HasExStyle(win32defines.WS_EX_TOOLWINDOW)):
        newRect.right -= 15


    # all the rest only need to be considered if there is a system menu.
    elif win.has_style(win32defines.WS_SYSMENU):
        buttons = []
        # account for the close button
        newRect.right -= 18
        buttons.append('close')

        # account for Icon if it is not disabled
        if not win.HasExStyle(win32defines.WS_EX_DLGMODALFRAME):
            newRect.left += 19 # icon


        # account for context sensitive help if set
        if win.HasExStyle(win32defines.WS_EX_CONTEXTHELP) and not ( \
            win.has_style(win32defines.WS_MAXIMIZEBOX) and \
            win.has_style(win32defines.WS_MINIMIZEBOX)):

            newRect.right -= 17

            # there is a bigger gap if the minimize box is there
            if win.has_style(win32defines.WS_MINIMIZEBOX) or \
                win.has_style(win32defines.WS_MAXIMIZEBOX) or \
                win.has_style(win32defines.WS_GROUP):
                newRect.right -= 3

            buttons.append('help')


        # account for Maximize button (but skip if WS_GROUP is set
        if win.has_style(win32defines.WS_MINIMIZEBOX) or \
            win.has_style(win32defines.WS_MAXIMIZEBOX) or \
            win.has_style(win32defines.WS_GROUP):

            newRect.right -= 32
            buttons.append('min')
            buttons.append('max')

        if buttons:
            # space between first button and dialog edge
            diff = 5

            # space for each button
            diff += len(buttons) * 16

            # space between close and next button
            if len(buttons) > 1:
                diff += 2

            # extra space between help and min buttons
            if 'min' in buttons and 'help' in buttons:
                diff += 4

    return [(win.window_text(), newRect, win.font(), win32defines.DT_SINGLELINE), ]


#==============================================================================
def _StatusBarTruncInfo(win):
    """Return truncation information specific to StatusBar controls"""
    truncInfo = _WindowTruncInfo(win)
    for i, (title, rect, font, flag) in enumerate(truncInfo):

        rect.bottom -= win.VertBorderWidth
        if i == 0:
            rect.right -= win.HorizBorderWidth
        else:
            rect.right -= win.InterBorderWidth

    return truncInfo

#==============================================================================
def _HeaderTruncInfo(win):
    """Return truncation information specific to Header controls"""
    truncInfo = _WindowTruncInfo(win)

    for i, (title, rect, font, flag) in enumerate(truncInfo):
        # only modify the header rectangle
        rect.right -= 12

    return truncInfo





#==============================================================================
def _WindowTruncInfo(win):
    """Return Default truncation information"""
    matchedItems = []

    for i, title in enumerate(win.texts()):

        # Use the client rects for rectangles
        if i < len(win.client_rects()):
            rect = win.client_rects()[i]
        else:
            # until we run out then just use the first 'main' client rectangle
            rect = win.client_rects()[0]

        # if we have fewer fonts than titles
        if len(win.fonts())-1 < i:
            font = win.font()
        else:
            font = win.fonts()[i]

        # add the item
        matchedItems.append(
            (title, rect, font, win32defines.DT_SINGLELINE))

    return matchedItems



#==============================================================================
_TruncInfo = {
    "#32770" : _DialogTruncInfo,
    "ComboBox" : _ComboBoxTruncInfo,
    "ComboLBox" : _ComboLBoxTruncInfo,
    "ListBox" : _ListBoxTruncInfo,
    "Button" : _ButtonTruncInfo,
    "CheckBox" : _CheckBoxTruncInfo,
    "GroupBox" : _GroupBoxTruncInfo,
    "RadioButton" : _RadioButtonTruncInfo,
    "Edit": _EditTruncInfo,
    "Static" : _StaticTruncInfo,

#	"msctls_statusbar32" : StatusBarTruncInfo,
#	"HSStatusBar" : StatusBarTruncInfo,
#	"SysHeader32" : HeaderTruncInfo,

#	"SysListView32" :  ListViewTruncInfo,
    #"SysTreeView32" :
}

#==============================================================================
def _GetTruncationInfo(win):
    """helper function to hide non special windows"""
    if win.friendly_class_name() in _TruncInfo:
        return _TruncInfo[win.friendly_class_name()](win)
    else:
        return _WindowTruncInfo(win)



