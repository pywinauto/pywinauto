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

import ctypes
from ctypes import * 

import win32structures
from win32structures import *

CreateBrushIndirect	=	ctypes.windll.gdi32.CreateBrushIndirect
CreateDC			=	ctypes.windll.gdi32.CreateDCW
CreateFontIndirect	=	ctypes.windll.gdi32.CreateFontIndirectW
CreatePen			=	ctypes.windll.gdi32.CreatePen
DeleteDC 			=	ctypes.windll.gdi32.DeleteDC
DeleteObject		=	ctypes.windll.gdi32.DeleteObject
DrawText			=	ctypes.windll.user32.DrawTextW
TextOut 			=	ctypes.windll.gdi32.TextOutW
EnableWindow		=	ctypes.windll.user32.EnableWindow
EnumChildWindows	=	ctypes.windll.user32.EnumChildWindows
EnumDesktopWindows	=	ctypes.windll.user32.EnumDesktopWindows
EnumWindows			=	ctypes.windll.user32.EnumWindows
GetClassName		=	ctypes.windll.user32.GetClassNameW
GetClientRect		=	ctypes.windll.user32.GetClientRect
GetDC				=	ctypes.windll.user32.GetDC
GetDesktopWindow	=	ctypes.windll.user32.GetDesktopWindow
GetMenu				=	ctypes.windll.user32.GetMenu
GetMenuItemCount	=	ctypes.windll.user32.GetMenuItemCount
GetMenuItemInfo		=	ctypes.windll.user32.GetMenuItemInfoW
GetObject			=	ctypes.windll.gdi32.GetObjectW
GetParent			=	ctypes.windll.user32.GetParent
GetStockObject		=	ctypes.windll.gdi32.GetStockObject
GetSystemMenu		=	ctypes.windll.user32.GetSystemMenu
GetSystemMetrics	=	ctypes.windll.user32.GetSystemMetrics
GetTextMetrics		=	ctypes.windll.gdi32.GetTextMetricsW
GetVersion			=	ctypes.windll.kernel32.GetVersion
GetWindow			=	ctypes.windll.user32.GetWindow
ShowWindow			= 	ctypes.windll.user32.ShowWindow
GetWindowContextHelpId =	ctypes.windll.user32.GetWindowContextHelpId
GetWindowLong		=	ctypes.windll.user32.GetWindowLongW
GetWindowRect		=	ctypes.windll.user32.GetWindowRect
GetWindowText		=	ctypes.windll.user32.GetWindowTextW
GetWindowTextLength	=	ctypes.windll.user32.GetWindowTextLengthW
GetCurrentThreadId	=	ctypes.windll.Kernel32.GetCurrentThreadId
GetWindowThreadProcessId =	ctypes.windll.user32.GetWindowThreadProcessId
AttachThreadInput 	=	ctypes.windll.user32.AttachThreadInput
IsChild				=	ctypes.windll.user32.IsChild
IsMenu				=	ctypes.windll.user32.IsMenu
IsWindow 			=	ctypes.windll.user32.IsWindow
IsWindowUnicode		=	ctypes.windll.user32.IsWindowUnicode
IsWindowVisible		=	ctypes.windll.user32.IsWindowVisible
IsWindowEnabled		=	ctypes.windll.user32.IsWindowEnabled
MapVirtualKey		=	ctypes.windll.user32.MapVirtualKeyW
OpenProcess			=	ctypes.windll.kernel32.OpenProcess
ReadProcessMemory	=	ctypes.windll.kernel32.ReadProcessMemory
Rectangle			=	ctypes.windll.gdi32.Rectangle
SelectObject		=	ctypes.windll.gdi32.SelectObject
SendMessage			=	ctypes.windll.user32.SendMessageW
SendMessageA		=	ctypes.windll.user32.SendMessageA
PostMessage			=	ctypes.windll.user32.PostMessageW
SetActiveWindow		=	ctypes.windll.user32.SetActiveWindow
GetFocus			=	ctypes.windll.user32.GetFocus
SetFocus			=	ctypes.windll.user32.SetFocus
SetForegroundWindow	=	ctypes.windll.user32.SetForegroundWindow
GetForegroundWindow	=	ctypes.windll.user32.GetForegroundWindow
SetWindowLong		=	ctypes.windll.user32.SetWindowLongW
SystemParametersInfo =	ctypes.windll.user32.SystemParametersInfoW
VirtualAllocEx		=	ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx		=	ctypes.windll.kernel32.VirtualFreeEx
VkKeyScan			=	ctypes.windll.user32.VkKeyScanW
WriteProcessMemory	=	ctypes.windll.kernel32.WriteProcessMemory
MenuItemFromPoint	=	ctypes.windll.user32.MenuItemFromPoint
GetActiveWindow		=	ctypes.windll.user32.GetActiveWindow
GetLastActivePopup 	=	ctypes.windll.user32.GetLastActivePopup 
FindWindow			=	ctypes.windll.user32.FindWindowW
GetTopWindow		=	ctypes.windll.user32.GetTopWindow

GetGUIThreadInfo	=	ctypes.windll.user32.GetGUIThreadInfo
ShowOwnedPopups		=	ctypes.windll.user32.ShowOwnedPopups
WindowFromPoint 	=	ctypes.windll.user32.WindowFromPoint 
GetMenuBarInfo		=	ctypes.windll.user32.GetMenuBarInfo
GetMessage			=	ctypes.windll.user32.GetMessageW
SendMessageTimeout	=	ctypes.windll.user32.SendMessageTimeoutW

WideCharToMultiByte	=	ctypes.windll.kernel32.WideCharToMultiByte
GetACP				=	ctypes.windll.kernel32.GetACP


CreateProcess 		= ctypes.windll.kernel32.CreateProcessW
TerminateProcess	= ctypes.windll.kernel32.TerminateProcess
ExitProcess 		= ctypes.windll.kernel32.ExitProcess


WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
WaitForInputIdle	= ctypes.windll.user32.WaitForInputIdle

#@ stdcall(BOOL, 'kernel32', [POINTER(WCHAR), POINTER(WCHAR), c_long, c_long, c_int, c_ulong, c_long, c_long, c_long, c_long])
#def CreateProcessW(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
#    # C:/PROGRA~1/MICROS~4/VC98/Include/winbase.h 4271
#    return CreateProcessW._api_(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)
GetWindowThreadProcessId	=	ctypes.windll.user32.GetWindowThreadProcessId
OpenProcess				=	ctypes.windll.kernel32.OpenProcess
GetModuleFileNameEx		=	ctypes.windll.psapi.GetModuleFileNameExW