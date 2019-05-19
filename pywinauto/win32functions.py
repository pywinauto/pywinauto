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

"""Defines Windows(tm) functions"""

from ctypes import windll
from ctypes import wintypes
from . import win32defines, win32structures
from .actionlogger import ActionLogger
from ctypes import c_short
from ctypes import WINFUNCTYPE
from ctypes import c_void_p
from ctypes import c_int
from ctypes import byref
from ctypes import POINTER
from ctypes import c_ubyte
from ctypes import c_size_t


SHORT = c_short


CreateBrushIndirect = windll.gdi32.CreateBrushIndirect
CreateBrushIndirect.restype = wintypes.HBRUSH
CreateBrushIndirect.argtypes = [
    c_void_p,
]
CreateDC = windll.gdi32.CreateDCW
CreateDC.restype = wintypes.HDC
CreateDC.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    c_void_p,
]
CreateFontIndirect = windll.gdi32.CreateFontIndirectW
CreateFontIndirect.restype = wintypes.HFONT
CreateFontIndirect.argtypes = [
    POINTER(win32structures.LOGFONTW),
]
CreatePen = windll.gdi32.CreatePen
CreatePen.restype = wintypes.HPEN
CreatePen.argtypes = [
    c_int,
    c_int,
    wintypes.COLORREF,
]
DeleteDC = windll.gdi32.DeleteDC
DeleteDC.restype = wintypes.BOOL
DeleteDC.argtypes = [
    wintypes.HDC,
]
GetObject = windll.gdi32.GetObjectW
GetObject.restype = c_int
GetObject.argtypes = [
    wintypes.HANDLE,
    c_int,
    wintypes.LPVOID,
]
DeleteObject = windll.gdi32.DeleteObject
DeleteObject.restype = wintypes.BOOL
DeleteObject.argtypes = [
    wintypes.HGDIOBJ,
]
DrawText = windll.user32.DrawTextW
DrawText.restype = c_int
DrawText.argtypes = [
    wintypes.HDC,
    wintypes.LPCWSTR,
    c_int,
    POINTER(wintypes.RECT),
    wintypes.UINT,
]
TextOut = windll.gdi32.TextOutW
TextOut.restype = wintypes.BOOL
TextOut.argtypes = [
    wintypes.HDC,
    c_int,
    c_int,
    wintypes.LPCWSTR,
    c_int,
]
Rectangle = windll.gdi32.Rectangle
Rectangle.restype = wintypes.BOOL
Rectangle.argtypes = [
    wintypes.HDC,
    c_int,
    c_int,
    c_int,
    c_int,
]
SelectObject = windll.gdi32.SelectObject
SelectObject.restype = wintypes.HGDIOBJ
SelectObject.argtypes = [
    wintypes.HDC,
    wintypes.HGDIOBJ,
]
GetStockObject = windll.gdi32.GetStockObject
GetStockObject.restype = wintypes.HGDIOBJ
GetStockObject.argtypes = [
    c_int,
]
GetSystemMetrics = windll.user32.GetSystemMetrics
GetSystemMetrics.restype = c_int
GetSystemMetrics.argtypes = [
    c_int,
]
GetTextMetrics = windll.gdi32.GetTextMetricsW
GetTextMetrics.restype = wintypes.BOOL
GetTextMetrics.argtypes = [
    wintypes.HDC,
    POINTER(win32structures.TEXTMETRICW),
]
EnumChildWindows = windll.user32.EnumChildWindows
EnumChildWindows.restype = wintypes.BOOL
EnumChildWindows.argtypes = [
    wintypes.HWND,
    WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
    wintypes.LPARAM,
]
EnumDesktopWindows = windll.user32.EnumDesktopWindows
EnumDesktopWindows.restype = wintypes.BOOL
EnumDesktopWindows.argtypes = [
    wintypes.LPVOID,
    WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
    wintypes.LPARAM,
]
EnumWindows = windll.user32.EnumWindows
EnumWindows.restype = wintypes.BOOL
EnumWindows.argtypes = [
    WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
    wintypes.LPARAM,
]
GetDC = windll.user32.GetDC
GetDC.restype = wintypes.LPVOID
GetDC.argtypes = [
    wintypes.HWND,
]
GetDesktopWindow = windll.user32.GetDesktopWindow
GetDesktopWindow.restype = wintypes.HWND
GetDesktopWindow.argtypes = [
]
SendInput = windll.user32.SendInput
SendInput.restype = wintypes.UINT
SendInput.argtypes = [
    wintypes.UINT,
    c_void_p,  # using POINTER(win32structures.INPUT) needs rework in keyboard.py
    c_int,
]
SetCursorPos = windll.user32.SetCursorPos
SetCursorPos.restype = wintypes.BOOL
SetCursorPos.argtypes = [
    c_int,
    c_int,
]
GetCursorPos = windll.user32.GetCursorPos
GetCursorPos.restype = wintypes.BOOL
GetCursorPos.argtypes = [
    POINTER(wintypes.POINT),
]
GetCaretPos = windll.user32.GetCaretPos
GetCaretPos.restype = wintypes.BOOL
GetCaretPos.argtypes = [
    POINTER(wintypes.POINT),
]
GetKeyboardState = windll.user32.GetKeyboardState
GetKeyboardState.restype = wintypes.BOOL
GetKeyboardState.argtypes = [
    POINTER(c_ubyte),
]
SetKeyboardState = windll.user32.SetKeyboardState
SetKeyboardState.restype = wintypes.BOOL
SetKeyboardState.argtypes = [
    POINTER(c_ubyte),
]
GetKeyboardLayout = windll.user32.GetKeyboardLayout
GetKeyboardLayout.restype = wintypes.HKL
GetKeyboardLayout.argtypes = [
    wintypes.DWORD,
]
VkKeyScanExW = windll.user32.VkKeyScanExW
VkKeyScanExW.restype = SHORT
VkKeyScanExW.argtypes = [
    wintypes.WCHAR,
    wintypes.HKL,
]
# menu functions
DrawMenuBar = windll.user32.DrawMenuBar
DrawMenuBar.restype = wintypes.BOOL
DrawMenuBar.argstype = [
    wintypes.HWND,
]
GetMenu = windll.user32.GetMenu
GetMenu.restype = wintypes.HMENU
GetMenu.argtypes = [
    wintypes.HWND,
]
GetMenuBarInfo = windll.user32.GetMenuBarInfo
GetMenuBarInfo.restype = wintypes.BOOL
GetMenuBarInfo.argtypes = [
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    POINTER(win32structures.MENUBARINFO),
]
GetMenuInfo = windll.user32.GetMenuInfo
GetMenuInfo.restype = wintypes.BOOL
GetMenuInfo.argtypes = [
    wintypes.HWND,
    POINTER(win32structures.MENUINFO),
]
GetMenuItemCount = windll.user32.GetMenuItemCount
GetMenuItemCount.restype = c_int
GetMenuItemCount.argtypes = [
    wintypes.HMENU,
]
GetMenuItemInfo = windll.user32.GetMenuItemInfoW
GetMenuItemInfo.restype = wintypes.BOOL
GetMenuItemInfo.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    wintypes.BOOL,
    POINTER(win32structures.MENUITEMINFOW),
]
SetMenuItemInfo = windll.user32.SetMenuItemInfoW
SetMenuItemInfo.restype = wintypes.BOOL
SetMenuItemInfo.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    wintypes.BOOL,
    POINTER(win32structures.MENUITEMINFOW),
]
GetMenuItemRect = windll.user32.GetMenuItemRect
GetMenuItemRect.restype = wintypes.BOOL
GetMenuItemRect.argtypes = [
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.UINT,
    POINTER(wintypes.RECT),
]
CheckMenuItem = windll.user32.CheckMenuItem
CheckMenuItem.restype = wintypes.DWORD
CheckMenuItem.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    wintypes.UINT,
]
GetMenuState = windll.user32.GetMenuState
GetMenuState.restype = wintypes.UINT
GetMenuState.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    wintypes.UINT,
]
GetSubMenu = windll.user32.GetSubMenu
GetSubMenu.restype = wintypes.HMENU
GetSubMenu.argtypes = [
    wintypes.HMENU,
    c_int,
]
GetSystemMenu = windll.user32.GetSystemMenu
GetSystemMenu.restype = wintypes.HMENU
GetSystemMenu.argtypes = [
    wintypes.HWND,
    wintypes.BOOL,
]
HiliteMenuItem = windll.user32.HiliteMenuItem
HiliteMenuItem.restype = wintypes.BOOL
HiliteMenuItem.argtypes = [
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.UINT,
    wintypes.UINT,
]
IsMenu = windll.user32.IsMenu
IsMenu.restype = wintypes.BOOL
IsMenu.argtypes = [
    wintypes.HMENU,
]
MenuItemFromPoint = windll.user32.MenuItemFromPoint
MenuItemFromPoint.restype = c_int
MenuItemFromPoint.argtypes = [
    wintypes.HWND,
    wintypes.HMENU,
    POINTER(wintypes.POINT),
]
BringWindowToTop = windll.user32.BringWindowToTop
BringWindowToTop.restype = wintypes.BOOL
BringWindowToTop.argtypes = [
    wintypes.HWND,
]

GetParent = windll.user32.GetParent
GetParent.restype = wintypes.HWND
GetParent.argtypes = [
    wintypes.HWND,
]
GetWindow = windll.user32.GetWindow
GetWindow.restype = wintypes.HWND
GetWindow.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
]
ShowWindow = windll.user32.ShowWindow
ShowWindow.restype = wintypes.BOOL
ShowWindow.argtypes = [
    wintypes.HWND,
    c_int,
]
GetWindowContextHelpId = windll.user32.GetWindowContextHelpId
GetWindowContextHelpId.restype = wintypes.DWORD
GetWindowContextHelpId.argtypes = [
    wintypes.HWND,
]
GetWindowLong = windll.user32.GetWindowLongW
GetWindowLong.restype = wintypes.LONG
GetWindowLong.argtypes = [
    wintypes.HWND,
    c_int,
]
GetWindowPlacement = windll.user32.GetWindowPlacement
GetWindowPlacement.restype = wintypes.BOOL
GetWindowPlacement.argtypes = [
    wintypes.HWND,
    POINTER(win32structures.WINDOWPLACEMENT),
]
GetWindowRect = windll.user32.GetWindowRect
GetWindowRect.restype = wintypes.BOOL
GetWindowRect.argtypes = [
    wintypes.HWND,
    POINTER(wintypes.RECT),
]
GetWindowText = windll.user32.GetWindowTextW
GetWindowText.restype = c_int
GetWindowText.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    c_int,
]
GetWindowTextLength = windll.user32.GetWindowTextLengthW
GetWindowTextLength.restype = c_int
GetWindowTextLength.argtypes = [
    wintypes.HWND,
]
GetClassName = windll.user32.GetClassNameW
GetClassName.restype = c_int
GetClassName.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    c_int,
]
GetClientRect = windll.user32.GetClientRect
GetClientRect.restype = wintypes.BOOL
GetClientRect.argtypes = [
    wintypes.HWND,
    POINTER(wintypes.RECT),
]
IsChild = windll.user32.IsChild
IsChild.restype = wintypes.BOOL
IsChild.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
]
IsWindow = windll.user32.IsWindow
IsWindow.restype = wintypes.BOOL
IsWindow.argtypes = [
    wintypes.HWND,
]
IsWindowUnicode = windll.user32.IsWindowUnicode
IsWindowUnicode.restype = wintypes.BOOL
IsWindowUnicode.argtypes = [
    wintypes.HWND,
]
IsWindowVisible = windll.user32.IsWindowVisible
IsWindowVisible.restype = wintypes.BOOL
IsWindowVisible.argtypes = [
    wintypes.HWND,
]
IsWindowEnabled = windll.user32.IsWindowEnabled
IsWindowEnabled.restype = wintypes.BOOL
IsWindowEnabled.argtypes = [
    wintypes.HWND,
]
ClientToScreen = windll.user32.ClientToScreen
ClientToScreen.restype = wintypes.BOOL
ClientToScreen.argtypes = [
    wintypes.HWND,
    POINTER(wintypes.POINT),
]
ScreenToClient = windll.user32.ScreenToClient
ScreenToClient.restype = wintypes.BOOL
ScreenToClient.argtypes = [
    wintypes.HWND,
    POINTER(wintypes.POINT),
]
GetCurrentThreadId = windll.kernel32.GetCurrentThreadId
GetCurrentThreadId.restype = wintypes.DWORD
GetCurrentThreadId.argtypes = [
]
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
GetWindowThreadProcessId.restype = wintypes.DWORD
GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    POINTER(wintypes.DWORD),
]
GetGUIThreadInfo = windll.user32.GetGUIThreadInfo
GetGUIThreadInfo.restype = wintypes.BOOL
GetGUIThreadInfo.argtypes = [
    wintypes.DWORD,
    POINTER(win32structures.GUITHREADINFO),
]
AttachThreadInput = windll.user32.AttachThreadInput
AttachThreadInput.restype = wintypes.BOOL
AttachThreadInput.argtypes = [
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.BOOL
]
OpenProcess = windll.kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.DWORD,
]
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [
    wintypes.HANDLE,
]
CreateProcess = windll.kernel32.CreateProcessW
CreateProcess.restype = wintypes.BOOL
CreateProcess.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    POINTER(win32structures.SECURITY_ATTRIBUTES),
    POINTER(win32structures.SECURITY_ATTRIBUTES),
    wintypes.BOOL,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.LPCWSTR,
    POINTER(win32structures.STARTUPINFOW),
    POINTER(win32structures.PROCESS_INFORMATION),
]
TerminateProcess = windll.kernel32.TerminateProcess
TerminateProcess.restype = wintypes.BOOL
TerminateProcess.argtypes = [
    wintypes.HANDLE,
    wintypes.UINT,
]
ExitProcess = windll.kernel32.ExitProcess
ExitProcess.restype = None
ExitProcess.argtypes = [
    wintypes.UINT,
]
ReadProcessMemory = windll.kernel32.ReadProcessMemory
ReadProcessMemory.restype = wintypes.BOOL
ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.LPVOID,
    c_size_t,
    POINTER(c_size_t),
]
GlobalAlloc = windll.kernel32.GlobalAlloc
GlobalLock = windll.kernel32.GlobalLock
GlobalUnlock = windll.kernel32.GlobalUnlock

SendMessage = windll.user32.SendMessageW
SendMessage.restype = wintypes.LPARAM
SendMessage.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPVOID,
]
SendMessageTimeout = windll.user32.SendMessageTimeoutW
SendMessageTimeout.restype = wintypes.LPARAM
SendMessageTimeout.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
    wintypes.UINT,
    wintypes.UINT,
    win32structures.PDWORD_PTR,
]
PostMessage = windll.user32.PostMessageW
PostMessage.restype = wintypes.BOOL
PostMessage.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
GetMessage = windll.user32.GetMessageW
GetMessage.restype = wintypes.BOOL
GetMessage.argtypes = [
    POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
]
RegisterWindowMessage = windll.user32.RegisterWindowMessageW
RegisterWindowMessage.restype = wintypes.UINT
RegisterWindowMessage.argtypes = [
    wintypes.LPCWSTR,
]
MoveWindow = windll.user32.MoveWindow
MoveWindow.restype = wintypes.BOOL
MoveWindow.argtypes = [
    wintypes.HWND,
    c_int,
    c_int,
    c_int,
    c_int,
    wintypes.BOOL,
]
EnableWindow = windll.user32.EnableWindow
EnableWindow.restype = wintypes.BOOL
EnableWindow.argtypes = [
    wintypes.HWND,
    wintypes.BOOL,
]
SetFocus = windll.user32.SetFocus
SetFocus.restype = wintypes.HWND
SetFocus.argtypes = [
    wintypes.HWND,
]
SetWindowLong = windll.user32.SetWindowLongW
SetWindowLong.restype = wintypes.LONG
SetWindowLong.argtypes = [
    wintypes.HWND,
    c_int,
    wintypes.LONG,
]
try:
    SetWindowLongPtr = windll.user32.SetWindowLongPtrW
    SetWindowLongPtr.argtypes = [wintypes.HWND, c_int, wintypes.LONG_PTR]
    SetWindowLongPtr.restype = wintypes.LONG_PTR
except AttributeError:
    SetWindowLongPtr = SetWindowLong
SystemParametersInfo = windll.user32.SystemParametersInfoW
SystemParametersInfo.restype = wintypes.UINT
SystemParametersInfo.argtypes = [
    wintypes.UINT,
    wintypes.UINT,
    wintypes.LPVOID,  # should map well to PVOID
    wintypes.UINT,
]
VirtualAllocEx = windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = wintypes.LPVOID
VirtualAllocEx.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    c_size_t,
    wintypes.DWORD,
    wintypes.DWORD,
]
VirtualFreeEx = windll.kernel32.VirtualFreeEx
VirtualFreeEx.restype = wintypes.BOOL
VirtualFreeEx.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    c_size_t,
    wintypes.DWORD,
]
VirtualAlloc = windll.kernel32.VirtualAlloc
VirtualAlloc.restype = wintypes.LPVOID
VirtualAlloc.argtypes = [
    wintypes.LPVOID,
    c_size_t,
    wintypes.DWORD,
    wintypes.DWORD,
]
VirtualFree = windll.kernel32.VirtualFree
VirtualFree.retype = wintypes.BOOL
VirtualFree.argtypes = [
    wintypes.LPVOID,
    c_size_t,
    wintypes.DWORD,
]
WriteProcessMemory = windll.kernel32.WriteProcessMemory
WriteProcessMemory.restype = wintypes.BOOL
WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.LPVOID,
    c_size_t,
    POINTER(c_size_t),
]
ReleaseCapture = windll.user32.ReleaseCapture
ReleaseCapture.restype = wintypes.BOOL
ReleaseCapture.argtypes = [
]
WindowFromPoint = windll.user32.WindowFromPoint
WindowFromPoint.restype = wintypes.HWND
WindowFromPoint.argtypes = [
    wintypes.POINT,
]
WaitForSingleObject = windll.kernel32.WaitForSingleObject
WaitForSingleObject.restype = wintypes.DWORD
WaitForSingleObject.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
]
WaitForInputIdle = windll.user32.WaitForInputIdle
WaitForInputIdle.restype = wintypes.DWORD
WaitForInputIdle.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
]
IsHungAppWindow = windll.user32.IsHungAppWindow
IsHungAppWindow.restype = wintypes.BOOL
IsHungAppWindow.argtypes = [
    wintypes.HWND,
]
GetModuleFileNameEx = windll.psapi.GetModuleFileNameExW
GetModuleFileNameEx.restype = wintypes.DWORD
GetModuleFileNameEx.argtypes = [
    wintypes.HANDLE,
    wintypes.HMODULE,
    wintypes.LPWSTR,
    wintypes.DWORD,
]
GetClipboardData = windll.user32.GetClipboardData
GetClipboardData.restype = wintypes.HANDLE
GetClipboardData.argtypes = [
    wintypes.UINT,
]
OpenClipboard = windll.user32.OpenClipboard
OpenClipboard.restype = wintypes.BOOL
OpenClipboard.argtypes = [
    wintypes.HWND,
]
EmptyClipboard = windll.user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL
EmptyClipboard.argtypes = [
]
CloseClipboard = windll.user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL
CloseClipboard.argtypes = [
]
CountClipboardFormats = windll.user32.CountClipboardFormats
CountClipboardFormats.restype = c_int
CountClipboardFormats.argtypes = [
]
EnumClipboardFormats = windll.user32.EnumClipboardFormats
EnumClipboardFormats.restype = wintypes.UINT
EnumClipboardFormats.argtypes = [
    wintypes.UINT,
]
GetClipboardFormatName = windll.user32.GetClipboardFormatNameW
GetClipboardFormatName.restype = c_int
GetClipboardFormatName.argtypes = [
    wintypes.UINT,
    wintypes.LPWSTR,
    c_int,
]

# DPIAware API funcs are not available on WinXP
try:
    IsProcessDPIAware = windll.user32.IsProcessDPIAware
    SetProcessDPIAware = windll.user32.SetProcessDPIAware
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
    shcore = windll.LoadLibrary("Shcore.dll")
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

GetQueueStatus = windll.user32.GetQueueStatus

LoadString = windll.user32.LoadStringW


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
    """Pack high into the high word of a long and low into the low word"""

    # we need to AND each value with 0xFFFF to account for numbers
    # greater then normal WORD (short) size
    return ((high & 0xFFFF) << 16) | (low & 0xFFFF)

#====================================================================
def HiWord(value):
    """Return the high word from a long"""
    #return (value & (~ 0xFFFF)) / 0xFFFF
    return (value >> 16) & 0xffff

#====================================================================
def LoWord(value):
    """Return the low word from a long"""
    return value & 0xFFFF

#====================================================================
def WaitGuiThreadIdle(handle):
    """Wait until the thread of the specified handle is ready"""
    process_id = wintypes.DWORD(0)
    GetWindowThreadProcessId(handle, byref(process_id))

    # ask the control if it has finished processing the message
    hprocess = OpenProcess(
        win32defines.PROCESS_QUERY_INFORMATION,
        0,
        process_id.value)

    # WaitForInputIdle call is removed because it's useful only
    # while an app is starting (should be called only once)
    if IsHungAppWindow(handle) == win32defines.TRUE:
        raise RuntimeError('Window (hwnd={0}) is not responding!'.format(handle))

    CloseHandle(hprocess)

#====================================================================
def GetDpiAwarenessByPid(pid):
    """Get DPI awareness properties of a process specified by ID"""
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
            dpi_awareness = c_int()
            hRes = GetProcessDpiAwareness(
                    hProcess,
                    byref(dpi_awareness))
            CloseHandle(hProcess)
            if hRes == 0:
                return dpi_awareness.value
        finally:
            if hProcess:
                CloseHandle(hProcess)

    # GetProcessDpiAwareness is not supported or pid is not specified,
    # return a default value
    return dpi_awareness
