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
"Defines Windows(tm) functions"

__revision__ = "$Revision$"

import ctypes
from ctypes import *

UINT = c_uint
SHORT = c_short


CreateBrushIndirect	=	ctypes.windll.gdi32.CreateBrushIndirect
CreateDC			=	ctypes.windll.gdi32.CreateDCW
CreateFontIndirect	=	ctypes.windll.gdi32.CreateFontIndirectW
CreatePen			=	ctypes.windll.gdi32.CreatePen
DeleteDC 			=	ctypes.windll.gdi32.DeleteDC
GetObject           =   ctypes.windll.gdi32.GetObjectW
DeleteObject		=	ctypes.windll.gdi32.DeleteObject
DrawText			=	ctypes.windll.user32.DrawTextW
TextOut 			=	ctypes.windll.gdi32.TextOutW
Rectangle           =   ctypes.windll.gdi32.Rectangle
SelectObject        =   ctypes.windll.gdi32.SelectObject
GetStockObject      =   ctypes.windll.gdi32.GetStockObject
GetSystemMetrics    =   ctypes.windll.user32.GetSystemMetrics
GetTextMetrics      =   ctypes.windll.gdi32.GetTextMetricsW


EnumChildWindows	=	ctypes.windll.user32.EnumChildWindows
EnumDesktopWindows	=	ctypes.windll.user32.EnumDesktopWindows
EnumWindows			=	ctypes.windll.user32.EnumWindows
GetDC				=	ctypes.windll.user32.GetDC
GetDesktopWindow	=	ctypes.windll.user32.GetDesktopWindow


SendInput           =   ctypes.windll.user32.SendInput
SetCursorPos        =   ctypes.windll.user32.SetCursorPos
GetCaretPos         =   ctypes.windll.user32.GetCaretPos

# menu functions
DrawMenuBar			=	ctypes.windll.user32.DrawMenuBar
GetMenu             =   ctypes.windll.user32.GetMenu
GetMenuBarInfo		=	ctypes.windll.user32.GetMenuBarInfo
GetMenuInfo         =   ctypes.windll.user32.GetMenuInfo
GetMenuItemCount	=	ctypes.windll.user32.GetMenuItemCount
GetMenuItemInfo		=	ctypes.windll.user32.GetMenuItemInfoW
SetMenuItemInfo     =   ctypes.windll.user32.SetMenuItemInfoW
GetMenuItemRect     =   ctypes.windll.user32.GetMenuItemRect
CheckMenuItem		=	ctypes.windll.user32.CheckMenuItem
GetMenuState		=	ctypes.windll.user32.GetMenuState
GetSubMenu	        =	ctypes.windll.user32.GetSubMenu
GetSystemMenu		=	ctypes.windll.user32.GetSystemMenu
HiliteMenuItem		=	ctypes.windll.user32.HiliteMenuItem
IsMenu				=	ctypes.windll.user32.IsMenu
MenuItemFromPoint	=	ctypes.windll.user32.MenuItemFromPoint

BringWindowToTop    =   ctypes.windll.user32.BringWindowToTop

GetVersion          =   ctypes.windll.kernel32.GetVersion

GetParent			=	ctypes.windll.user32.GetParent
GetWindow			=	ctypes.windll.user32.GetWindow
ShowWindow			= 	ctypes.windll.user32.ShowWindow
GetWindowContextHelpId =	ctypes.windll.user32.GetWindowContextHelpId
GetWindowLong		=	ctypes.windll.user32.GetWindowLongW
GetWindowRect		=	ctypes.windll.user32.GetWindowRect
GetWindowText		=	ctypes.windll.user32.GetWindowTextW
GetWindowTextLength	=	ctypes.windll.user32.GetWindowTextLengthW
GetClassName        =   ctypes.windll.user32.GetClassNameW
GetClientRect       =   ctypes.windll.user32.GetClientRect
IsChild				=	ctypes.windll.user32.IsChild
IsWindow 			=	ctypes.windll.user32.IsWindow
IsWindowUnicode		=	ctypes.windll.user32.IsWindowUnicode
IsWindowVisible		=	ctypes.windll.user32.IsWindowVisible
IsWindowEnabled		=	ctypes.windll.user32.IsWindowEnabled

GetCurrentThreadId  =   ctypes.windll.Kernel32.GetCurrentThreadId
GetWindowThreadProcessId =  ctypes.windll.user32.GetWindowThreadProcessId
GetGUIThreadInfo    =   ctypes.windll.user32.GetGUIThreadInfo
AttachThreadInput   =   ctypes.windll.user32.AttachThreadInput
GetWindowThreadProcessId    =   ctypes.windll.user32.GetWindowThreadProcessId

OpenProcess			=	ctypes.windll.kernel32.OpenProcess
CloseHandle         =   ctypes.windll.kernel32.CloseHandle
CreateProcess       = ctypes.windll.kernel32.CreateProcessW
TerminateProcess    = ctypes.windll.kernel32.TerminateProcess
ExitProcess         = ctypes.windll.kernel32.ExitProcess

ReadProcessMemory   =   ctypes.windll.kernel32.ReadProcessMemory
GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock

SendMessage			=	ctypes.windll.user32.SendMessageW
SendMessageTimeout  =   ctypes.windll.user32.SendMessageTimeoutW
SendMessageA		=	ctypes.windll.user32.SendMessageA
PostMessage			=	ctypes.windll.user32.PostMessageW
GetMessage          =   ctypes.windll.user32.GetMessageW

MoveWindow          =   ctypes.windll.user32.MoveWindow
EnableWindow        =   ctypes.windll.user32.EnableWindow
SetActiveWindow		=	ctypes.windll.user32.SetActiveWindow
GetFocus			=	ctypes.windll.user32.GetFocus
SetFocus			=	ctypes.windll.user32.SetFocus
SetForegroundWindow	=	ctypes.windll.user32.SetForegroundWindow
GetForegroundWindow	=	ctypes.windll.user32.GetForegroundWindow
SetWindowLong		=	ctypes.windll.user32.SetWindowLongW
SystemParametersInfo =	ctypes.windll.user32.SystemParametersInfoW
VirtualAllocEx		=	ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx		=	ctypes.windll.kernel32.VirtualFreeEx
WriteProcessMemory	=	ctypes.windll.kernel32.WriteProcessMemory
GetActiveWindow		=	ctypes.windll.user32.GetActiveWindow
GetLastActivePopup 	=	ctypes.windll.user32.GetLastActivePopup
FindWindow			=	ctypes.windll.user32.FindWindowW
GetTopWindow		=	ctypes.windll.user32.GetTopWindow

SetCapture			=	ctypes.windll.user32.SetCapture
ReleaseCapture		=	ctypes.windll.user32.ReleaseCapture

ShowOwnedPopups		=	ctypes.windll.user32.ShowOwnedPopups
WindowFromPoint 	=	ctypes.windll.user32.WindowFromPoint

WideCharToMultiByte	=	ctypes.windll.kernel32.WideCharToMultiByte
GetACP				=	ctypes.windll.kernel32.GetACP

WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
WaitForInputIdle	= ctypes.windll.user32.WaitForInputIdle

OpenProcess				=	ctypes.windll.kernel32.OpenProcess
GetModuleFileNameEx		=	ctypes.windll.psapi.GetModuleFileNameExW

GetClipboardData = ctypes.windll.user32.GetClipboardData
OpenClipboard = ctypes.windll.user32.OpenClipboard
CountClipboardFormats = ctypes.windll.user32.CountClipboardFormats
EnumClipboardFormats = ctypes.windll.user32.EnumClipboardFormats
CloseClipboard = ctypes.windll.user32.CloseClipboard

GetQueueStatus = ctypes.windll.user32.GetQueueStatus

LoadString = ctypes.windll.user32.LoadStringW


def VkKeyScanW(p1):
    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4225
    return VkKeyScanW._api_(p1)
VkKeyScan = stdcall(SHORT, 'user32', [c_wchar]) (VkKeyScanW)

def MapVirtualKeyExW(p1, p2, p3):
    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4376
    return MapVirtualKeyExW._api_(p1, p2, p3)
MapVirtualKeyEx = stdcall(
    UINT, 'user32', [c_uint, c_uint, c_long]) (MapVirtualKeyExW)

def MapVirtualKeyW(p1, p2):
    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4355
    return MapVirtualKeyW._api_(p1, p2)
MapVirtualKey = stdcall(UINT, 'user32', [c_uint, c_uint]) (MapVirtualKeyW)


#====================================================================
def MakeLong(high, low):
    "Pack high into the high word of a long and low into the low word"

    # we need to AND each value with 0xFFFF to account for numbers
    # greater then normal WORD (short) size
    return ((high & 0xFFFF) << 16) | (low & 0xFFFF)

#====================================================================
def HiWord(value):
    "Return the high word from a long"
    #return (value & (~ 0xFFFF)) / 0xFFFF
    return (value >> 16) & 0xffff

#====================================================================
def LoWord(value):
    "Return the low word from a long"
    return value & 0xFFFF

#====================================================================
def WaitGuiThreadIdle(handle, timeout = 1):
    "Wait until the thread of the specified handle is ready"
    import win32defines

    process_id = ctypes.c_int()
    GetWindowThreadProcessId(handle, ctypes.byref(process_id))

    # ask the control if it has finished processing the message
    hprocess = OpenProcess(
        win32defines.PROCESS_QUERY_INFORMATION,
        0,
        process_id.value)

    # wait timout number of seconds
    ret = WaitForInputIdle(hprocess, timeout * 1000)

    CloseHandle(hprocess)

    return ret
