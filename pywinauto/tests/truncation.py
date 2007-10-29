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

__revision__ = "$Revision$"

testname = "Truncation"

import ctypes

from pywinauto import win32defines
from pywinauto import win32functions
from pywinauto.win32structures import RECT


#==============================================================================
def TruncationTest(windows):
    "Actually do the test"

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

            truncIdxs = ",".join([unicode(index) for index in truncIdxs])
            truncStrings = '"%s"' % ",".join(
                [unicode(string) for string in truncStrings])
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
    "Return the index of the texts that are truncated for this control"
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
    how to do it accurately
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

    modifiedRect = RECT(usableRect)
    # Now write the text to our DC with our font to get the
    # rectangle that the text needs to fit in
    win32functions.DrawText (txtDC, # The DC
        unicode(text),		# The Title of the control
        -1,			# -1 because sTitle is NULL terminated
        ctypes.byref(modifiedRect),	# The Rectangle to be calculated to
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
    "Return truncation information specific to Button controls"
    lineFormat = win32defines.DT_SINGLELINE

    heightAdj = 4
    widthAdj = 9

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.HasStyle(win32defines.BS_BITMAP) or \
        win.HasStyle(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.ClientRects()[0]
    newRect.right -=  widthAdj
    newRect.bottom -=  heightAdj

    return [(win.WindowText(), newRect, win.Font(), lineFormat), ]


#==============================================================================
def _RadioButtonTruncInfo(win):
    "Return truncation information specific to Button controls"
    lineFormat = win32defines.DT_SINGLELINE

    if win.HasStyle(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK
    
    widthAdj = 19

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.HasStyle(win32defines.BS_BITMAP) or \
        win.HasStyle(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.ClientRects()[0]
    newRect.right -=  widthAdj

    return [(win.WindowText(), newRect, win.Font(), lineFormat), ]


#==============================================================================
def _CheckBoxTruncInfo(win):
    "Return truncation information specific to Button controls"
    lineFormat = win32defines.DT_SINGLELINE

    if win.HasStyle(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK

    widthAdj = 18
    
    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.HasStyle(win32defines.BS_BITMAP) or \
        win.HasStyle(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.ClientRects()[0]
    newRect.right -=  widthAdj
    
    return [(win.WindowText(), newRect, win.Font(), lineFormat), ]


#==============================================================================
def _ButtonTruncInfo(win):
    "Return truncation information specific to Button controls"
    lineFormat = win32defines.DT_SINGLELINE

    if win.HasStyle(win32defines.BS_MULTILINE):
        lineFormat = win32defines.DT_WORDBREAK

    heightAdj = 4
    widthAdj = 5

    if win.HasStyle(win32defines.BS_PUSHLIKE):
        widthAdj = 3
        heightAdj = 3 # 3
        if win.HasStyle(win32defines.BS_MULTILINE):
            widthAdj = 9
            heightAdj = 2 # 3

    # don't check image controls for truncation!
    # we do this by specifying huge adjustments
    # maybe a better/more pythonic way of doing this would be
    # to set some special lineFormat (None or something?)
    if win.HasStyle(win32defines.BS_BITMAP) or \
        win.HasStyle(win32defines.BS_ICON):
        heightAdj = -9000
        widthAdj = -9000
        lineFormat = win32defines.DT_WORDBREAK

    newRect = win.ClientRects()[0]
    newRect.right -=  widthAdj
    newRect.bottom -=  heightAdj

    return [(win.WindowText(), newRect, win.Font(), lineFormat), ]

#==============================================================================
def _ComboBoxTruncInfo(win):
    "Return truncation information specific to ComboBox controls"
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    if win.HasStyle(win32defines.CBS_DROPDOWN) or \
        win.HasStyle(win32defines.CBS_DROPDOWNLIST):
        widthAdj = 2#5
    else:
        widthAdj = 3

    truncData = []
    for title in win.Texts():
        newRect = win.ClientRects()[0]
        newRect.right -= widthAdj
        truncData.append((title, newRect, win.Font(), lineFormat))

    return truncData

#==============================================================================
def _ComboLBoxTruncInfo(win):
    "Return truncation information specific to ComboLBox controls"
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    truncData = []
    for title in win.Texts():
        newRect = win.ClientRects()[0]
        newRect.right -= 5
        truncData.append((title, newRect, win.Font(), lineFormat))

    return truncData


#==============================================================================
def _ListBoxTruncInfo(win):
    "Return truncation information specific to ListBox controls"
    # canot wrap and never had a hotkey
    lineFormat = win32defines.DT_SINGLELINE | win32defines.DT_NOPREFIX

    truncData = []
    for title in win.Texts():
        newRect = win.ClientRects()[0]
        newRect.right -= 2
        newRect.bottom -= 1
        truncData.append((title, newRect, win.Font(), lineFormat))

    return truncData


#==============================================================================
def _StaticTruncInfo(win):
    "Return truncation information specific to Static controls"
    lineFormat = win32defines.DT_WORDBREAK

    if win.HasStyle(win32defines.SS_CENTERIMAGE) or \
        win.HasStyle(win32defines.SS_SIMPLE) or \
        win.HasStyle(win32defines.SS_LEFTNOWORDWRAP):

        if "WindowsForms" not in win.Class():
            lineFormat = win32defines.DT_SINGLELINE

    if win.HasStyle(win32defines.SS_NOPREFIX):
        lineFormat |= win32defines.DT_NOPREFIX

    return [(win.WindowText(), win.ClientRects()[0], win.Font(), lineFormat), ]

#==============================================================================
def _EditTruncInfo(win):
    "Return truncation information specific to Edit controls"
    lineFormat = win32defines.DT_WORDBREAK | win32defines.DT_NOPREFIX

    if not win.HasStyle(win32defines.ES_MULTILINE):
        lineFormat |= win32defines.DT_SINGLELINE

    return [(win.WindowText(), win.ClientRects()[0], win.Font(), lineFormat), ]


#==============================================================================
def _DialogTruncInfo(win):
    "Return truncation information specific to Header controls"
    # move it down more into range

    newRect = win.ClientRects()[0]

    newRect.top += 5
    newRect.left += 5
    newRect.right -= 5


    if win.HasStyle(win32defines.WS_THICKFRAME):
        newRect.top += 1
        newRect.left += 1
        newRect.right -= 1

    # if it has the system menu but is a small caption
    # then the only button it can have is the close button
    if win.HasStyle(win32defines.WS_SYSMENU) and \
        (win.HasExStyle(win32defines.WS_EX_PALETTEWINDOW) or
        win.HasExStyle(win32defines.WS_EX_TOOLWINDOW)):
        newRect.right -= 15


    # all the rest only need to be considered if there is a system menu.
    elif win.HasStyle(win32defines.WS_SYSMENU):
        buttons = []
        # account for the close button
        newRect.right -= 18
        buttons.append('close')

        # account for Icon if it is not disabled
        if not win.HasExStyle(win32defines.WS_EX_DLGMODALFRAME):
            newRect.left += 19 # icon


        # account for context sensitive help if set
        if win.HasExStyle(win32defines.WS_EX_CONTEXTHELP) and not ( \
            win.HasStyle(win32defines.WS_MAXIMIZEBOX) and \
            win.HasStyle(win32defines.WS_MINIMIZEBOX)):

            newRect.right -= 17

            # there is a bigger gap if the minimize box is there
            if win.HasStyle(win32defines.WS_MINIMIZEBOX) or \
                win.HasStyle(win32defines.WS_MAXIMIZEBOX) or \
                win.HasStyle(win32defines.WS_GROUP):
                newRect.right -= 3

            buttons.append('help')


        # account for Maximize button (but skip if WS_GROUP is set
        if win.HasStyle(win32defines.WS_MINIMIZEBOX) or \
            win.HasStyle(win32defines.WS_MAXIMIZEBOX) or \
            win.HasStyle(win32defines.WS_GROUP):

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

    return [(win.WindowText(), newRect, win.Font(), win32defines.DT_SINGLELINE), ]


#==============================================================================
def _StatusBarTruncInfo(win):
    "Return truncation information specific to StatusBar controls"
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
    "Return truncation information specific to Header controls"
    truncInfo = _WindowTruncInfo(win)

    for i, (title, rect, font, flag) in enumerate(truncInfo):
        # only modify the header rectangle
        rect.right -= 12

    return truncInfo





#==============================================================================
def _WindowTruncInfo(win):
    "Return Default truncation information"
    matchedItems = []

    for i, title in enumerate(win.Texts()):

        # Use the client rects for rectangles
        if i < len(win.ClientRects()):
            rect = win.ClientRects()[i]
        else:
            # until we run out then just use the first 'main' client rectangle
            rect = win.ClientRects()[0]

        # if we have fewer fonts than titles
        if len(win.Fonts())-1 < i:
            font = win.Font()
        else:
            font = win.Fonts()[i]

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
    "Button" : _ButtonTruncInfo,
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
    "helper function to hide non special windows"
    if win.FriendlyClassName() in _TruncInfo:
        return _TruncInfo[win.FriendlyClassName()](win)
    else:
        return _WindowTruncInfo(win)



