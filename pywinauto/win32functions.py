# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
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
"""Defines Windows(tm) functions"""

import ctypes
from . import win32defines, win32structures
from .actionlogger import ActionLogger
from ctypes import c_uint, c_short, c_long

import sys
if sys.platform == "cygwin":
    windll = ctypes.cdll
    HRESULT = c_long


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
GetSystemMetrics.restype = ctypes.c_int
GetSystemMetrics.argtypes = (ctypes.c_int, )
GetTextMetrics      =   ctypes.windll.gdi32.GetTextMetricsW


EnumChildWindows	=	ctypes.windll.user32.EnumChildWindows
EnumDesktopWindows	=	ctypes.windll.user32.EnumDesktopWindows
EnumWindows			=	ctypes.windll.user32.EnumWindows
GetDC				=	ctypes.windll.user32.GetDC
GetDesktopWindow	=	ctypes.windll.user32.GetDesktopWindow


SendInput           =   ctypes.windll.user32.SendInput
SetCursorPos        =   ctypes.windll.user32.SetCursorPos
GetCursorPos        =   ctypes.windll.user32.GetCursorPos
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
GetWindowPlacement  =   ctypes.windll.user32.GetWindowPlacement
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
ClientToScreen      =   ctypes.windll.user32.ClientToScreen
ScreenToClient      =   ctypes.windll.user32.ScreenToClient

GetCurrentThreadId  =   ctypes.windll.Kernel32.GetCurrentThreadId
GetWindowThreadProcessId =  ctypes.windll.user32.GetWindowThreadProcessId
GetGUIThreadInfo    =   ctypes.windll.user32.GetGUIThreadInfo
AttachThreadInput   =   ctypes.windll.user32.AttachThreadInput
AttachThreadInput.restype = win32structures.BOOL
AttachThreadInput.argtypes = [win32structures.DWORD, win32structures.DWORD, win32structures.BOOL]
#GetWindowThreadProcessId    =   ctypes.windll.user32.GetWindowThreadProcessId
GetLastError = ctypes.windll.kernel32.GetLastError

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
try:
    SetWindowLongPtr    =   ctypes.windll.user32.SetWindowLongPtrW
    SetWindowLongPtr.argtypes = [win32structures.HWND, ctypes.c_int, win32structures.LONG_PTR]
    SetWindowLongPtr.restype = win32structures.LONG_PTR
except AttributeError:
    SetWindowLongPtr = SetWindowLong
SystemParametersInfo =	ctypes.windll.user32.SystemParametersInfoW
VirtualAllocEx		=	ctypes.windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = ctypes.c_void_p
VirtualFreeEx		=	ctypes.windll.kernel32.VirtualFreeEx
DebugBreakProcess	=	ctypes.windll.kernel32.DebugBreakProcess

VirtualAlloc		=	ctypes.windll.kernel32.VirtualAlloc
VirtualFree			=	ctypes.windll.kernel32.VirtualFree
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

GetModuleFileNameEx		=	ctypes.windll.psapi.GetModuleFileNameExW

GetClipboardData = ctypes.windll.user32.GetClipboardData
OpenClipboard    = ctypes.windll.user32.OpenClipboard
EmptyClipboard   = ctypes.windll.user32.EmptyClipboard
CloseClipboard   = ctypes.windll.user32.CloseClipboard
CountClipboardFormats  = ctypes.windll.user32.CountClipboardFormats
EnumClipboardFormats   = ctypes.windll.user32.EnumClipboardFormats
GetClipboardFormatName = ctypes.windll.user32.GetClipboardFormatNameW

# DPIAware API funcs are not available on WinXP
try:
    IsProcessDPIAware = ctypes.windll.user32.IsProcessDPIAware
    SetProcessDPIAware = ctypes.windll.user32.SetProcessDPIAware
except AttributeError:
    IsProcessDPIAware = None
    SetProcessDPIAware = None

# DpiAwareness API funcs are available only from win 8.1 and greater
# Supported types of DPI awareness described here:
# https://msdn.microsoft.com/en-us/library/windows/desktop/dn280512(v=vs.85).aspx
# typedef enum _Process_DPI_Awareness { 
#   Process_DPI_Unaware            = 0,
#   Process_System_DPI_Aware       = 1,
#   Process_Per_Monitor_DPI_Aware  = 2
# } Process_DPI_Awareness;
try:
    shcore = ctypes.windll.LoadLibrary(u"Shcore.dll")
    SetProcessDpiAwareness = shcore.SetProcessDpiAwareness
    GetProcessDpiAwareness = shcore.GetProcessDpiAwareness
    Process_DPI_Awareness = {
        "Process_DPI_Unaware"           : 0,
        "Process_System_DPI_Aware"      : 1,
        "Process_Per_Monitor_DPI_Aware" : 2
        }
except (OSError, AttributeError):
    SetProcessDpiAwareness = None
    GetProcessDpiAwareness = None
    Process_DPI_Awareness = None

# Setup DPI awareness for the python process if any is supported
if SetProcessDpiAwareness:
    ActionLogger().log("Call SetProcessDpiAwareness")
    SetProcessDpiAwareness(
            Process_DPI_Awareness["Process_Per_Monitor_DPI_Aware"])
elif SetProcessDPIAware:
    ActionLogger().log("Call SetProcessDPIAware")
    SetProcessDPIAware()

GetQueueStatus = ctypes.windll.user32.GetQueueStatus

LoadString = ctypes.windll.user32.LoadStringW


#def VkKeyScanW(p1):
#    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4225
#    return VkKeyScanW._api_(p1)
#VkKeyScan = stdcall(SHORT, 'user32', [c_wchar]) (VkKeyScanW)
#
#def MapVirtualKeyExW(p1, p2, p3):
#    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4376
#    return MapVirtualKeyExW._api_(p1, p2, p3)
#MapVirtualKeyEx = stdcall(
#    UINT, 'user32', [c_uint, c_uint, c_long]) (MapVirtualKeyExW)
#
#def MapVirtualKeyW(p1, p2):
#    # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4355
#    return MapVirtualKeyW._api_(p1, p2)
#MapVirtualKey = stdcall(UINT, 'user32', [c_uint, c_uint]) (MapVirtualKeyW)


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
    from . import win32defines

    process_id = ctypes.c_int()
    GetWindowThreadProcessId(handle, ctypes.byref(process_id))

    # ask the control if it has finished processing the message
    hprocess = OpenProcess(
        win32defines.PROCESS_QUERY_INFORMATION,
        0,
        process_id.value)

    # wait for the timeout number of seconds
    ret = WaitForInputIdle(hprocess, timeout * 1000)

    CloseHandle(hprocess)

    return ret

def GetDpiAwarenessByPid(pid):
    "Get DPI awareness properties of a process specified by ID"
        
    dpi_awareness = -1
    hProcess = None
    if GetProcessDpiAwareness and pid:
        hProcess = OpenProcess(
                    win32defines.PROCESS_QUERY_INFORMATION, 
                    0, 
                    pid)
        if not hProcess:
            # process doesn't exist, exit with a default return value
            return dpi_awareness

        try:
            dpi_awareness = ctypes.c_int()
            hRes = GetProcessDpiAwareness(
                    hProcess, 
                    ctypes.byref(dpi_awareness))
            CloseHandle(hProcess)
            if hRes == 0:
                return dpi_awareness.value
        finally:
            if hProcess:
                CloseHandle(hProcess)

    # GetProcessDpiAwareness is not supported or pid is not specified,
    # return a default value
    return dpi_awareness
