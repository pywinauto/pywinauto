"""Some functions already exists in pywinauto, but for correctly
injector work needs full redefinition with ctypes compatible
"""

import ctypes
from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE
from ctypes.wintypes import LPVOID
from ctypes.wintypes import LPCVOID
from ...win32structures import SECURITY_ATTRIBUTES
from ... import win32defines

LPCTSTR = ctypes.c_char_p
LPWTSTR = ctypes.c_wchar_p
LPDWORD = ctypes.POINTER(DWORD)
LPTHREAD_START_ROUTINE = LPVOID
LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.restype = HANDLE
OpenProcess.argtypes = (DWORD, BOOL, DWORD)

VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = LPVOID
VirtualAllocEx.argtypes = (HANDLE, LPVOID, DWORD, DWORD, DWORD)

WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
WriteProcessMemory.argtypes = (HANDLE, LPVOID, LPCVOID, DWORD, DWORD)

CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
CreateRemoteThread.restype = HANDLE
CreateRemoteThread.argtypes = (HANDLE, LPSECURITY_ATTRIBUTES, DWORD, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD)

GetModuleHandleW = ctypes.windll.kernel32.GetModuleHandleW
GetModuleHandleW.restype = HANDLE
GetModuleHandleW.argtypes = (LPWTSTR,)

LoadLibraryW = ctypes.windll.kernel32.LoadLibraryW
LoadLibraryW.restype = HANDLE
LoadLibraryW.argtypes = (LPWTSTR,)

GetProcAddress = ctypes.windll.kernel32.GetProcAddress
GetProcAddress.restype = LPVOID
GetProcAddress.argtypes = (HANDLE, LPCTSTR)

WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
WaitForSingleObject.restype = DWORD
WaitForSingleObject.argtypes = (HANDLE, DWORD)
