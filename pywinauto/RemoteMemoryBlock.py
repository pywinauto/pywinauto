# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
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

from __future__ import absolute_import
from __future__ import print_function

import ctypes, win32api, sys

from . import win32functions
from . import win32defines
from . import win32structures
from . import sysinfo
from .actionlogger import ActionLogger

class AccessDenied(RuntimeError):
    "Raised when we cannot allocate memory in the control's process"
    pass

#====================================================================
class RemoteMemoryBlock(object):
    "Class that enables reading and writing memory in a different process"
    #----------------------------------------------------------------
    def __init__(self, handle, size = 4096): #4096): #16384):
        "Allocate the memory"
        self.memAddress = 0
        self.size = size
        self.process = 0
        
        if handle == 0xffffffff80000000:
            raise Exception('Incorrect handle: ' + str(handle))

        self._as_parameter_ = self.memAddress

        if sysinfo.is_x64_Python():
            process_id = ctypes.c_ulonglong()
        else:
            process_id = ctypes.c_ulong()
        win32functions.GetWindowThreadProcessId(
            handle, ctypes.byref(process_id))
        if not process_id.value:
            raise AccessDenied(
                str(ctypes.WinError()) + " Cannot get process ID from handle.")

        self.process = win32functions.OpenProcess(
                win32defines.PROCESS_VM_OPERATION |
                win32defines.PROCESS_VM_READ |
                win32defines.PROCESS_VM_WRITE,
            0,
            process_id)

        if not self.process:
            raise AccessDenied(
                str(ctypes.WinError()) + "process: %d",
                process_id.value)

        self.memAddress = win32functions.VirtualAllocEx(
            ctypes.c_void_p(self.process),	# remote process
            ctypes.c_void_p(0),				# let Valloc decide where
            win32structures.ULONG_PTR(self.size + 4),# how much to allocate
                win32defines.MEM_RESERVE |
                win32defines.MEM_COMMIT, # allocation type
            win32defines.PAGE_READWRITE  # protection
            )
        if hasattr(self.memAddress, 'value'):
            self.memAddress = self.memAddress.value

        if self.memAddress == 0:
            raise ctypes.WinError()
        
        if hex(self.memAddress) == '0xffffffff80000000' or hex(self.memAddress).upper() == '0xFFFFFFFF00000000':
            raise Exception('Incorrect allocation: ' + hex(self.memAddress))

        self._as_parameter_ = self.memAddress
        
        # write guard signature at the end of memory block
        signature = win32structures.LONG(0x66666666)
        ret = win32functions.WriteProcessMemory(
            ctypes.c_void_p(self.process),
            ctypes.c_void_p(self.memAddress + self.size),
            ctypes.pointer(signature),
            win32structures.ULONG_PTR(4),
            win32structures.ULONG_PTR(0));
        if ret == 0:
            ActionLogger().log('================== Error: Failed to write guard signature: address = ' +
                               hex(self.memAddress) + ', size = ' + str(self.size))
            last_error = win32api.GetLastError()
            ActionLogger().log('LastError = ' + str(last_error) + ': ' + win32api.FormatMessage(last_error).rstrip())


    #----------------------------------------------------------------
    def _CloseHandle(self):
        "Close the handle to the process."
        ret = win32functions.CloseHandle(self.process)
        #win32api.CloseHandle(self.process)

        if ret == 0:
            ActionLogger().log('Warning: cannot close process handle!')
            #raise ctypes.WinError()

    #----------------------------------------------------------------
    def CleanUp(self):
        "Free Memory and the process handle"
        if self.process != 0 and self.memAddress != 0:
            # free up the memory we allocated
            #win32api.SetLastError(0)
            self.CheckGuardSignature()
            
            ret = win32functions.VirtualFreeEx(
                ctypes.c_void_p(self.process), ctypes.c_void_p(self.memAddress), win32structures.ULONG_PTR(0), win32structures.DWORD(win32defines.MEM_RELEASE))
            if ret == 0:
                print('Error: CleanUp: VirtualFreeEx() returned zero for address ', hex(self.memAddress))
                last_error = win32api.GetLastError()
                print('LastError = ', last_error, ': ', win32api.FormatMessage(last_error).rstrip())
                sys.stdout.flush()
                #self._CloseHandle()
                raise ctypes.WinError()
            self.memAddress = 0
            #self._CloseHandle()
        else:
            pass #ActionLogger().log('\nWARNING: Cannot call VirtualFreeEx! process_id == 0.')


    #----------------------------------------------------------------
    def __del__(self):
        "Ensure that the memory is Freed"
        # Free the memory in the remote process's address space
        self.CleanUp()

    #----------------------------------------------------------------
    def Address(self):
        "Return the address of the memory block"
        return self.memAddress

    #----------------------------------------------------------------
    def Write(self, data, address = None, size = None):
        "Write data into the memory block"
        # write the data from this process into the memory allocated
        # from the other process
        if not address:
            address = self.memAddress
        if hasattr(address, 'value'):
            address = address.value

        if size:
            nSize = win32structures.ULONG_PTR(size)
        else:
            nSize = win32structures.ULONG_PTR(ctypes.sizeof(data))
        
        if self.size < nSize.value:
            raise Exception('Write: RemoteMemoryBlock is too small (' + str(self.size) + ' bytes), ' + str(nSize.value) + ' is required.')
        
        if hex(address).lower().startswith('0xffffff'):
            raise Exception('Write: RemoteMemoryBlock has incorrect address = ' + hex(address))
        
        ret = win32functions.WriteProcessMemory(
            ctypes.c_void_p(self.process),
            ctypes.c_void_p(address),
            ctypes.pointer(data),
            nSize,
            win32structures.ULONG_PTR(0));

        if ret == 0:
            ActionLogger().log('Error: Write failed: address = ', address)
            last_error = win32api.GetLastError()
            ActionLogger().log('Error: LastError = ', last_error, ': ', win32api.FormatMessage(last_error).rstrip())
            raise ctypes.WinError()
        self.CheckGuardSignature()

    #----------------------------------------------------------------
    def Read(self, data, address = None, size = None):
        "Read data from the memory block"
        if not address:
            address = self.memAddress
        if hasattr(address, 'value'):
            address = address.value

        if size:
            nSize = win32structures.ULONG_PTR(size)
        else:
            nSize = win32structures.ULONG_PTR(ctypes.sizeof(data))

        if self.size < nSize.value:
            raise Exception('Read: RemoteMemoryBlock is too small (' + str(self.size) + ' bytes), ' + str(nSize.value) + ' is required.')
        
        if hex(address).lower().startswith('0xffffff'):
            raise Exception('Read: RemoteMemoryBlock has incorrect address =' + hex(address))
        
        lpNumberOfBytesRead = ctypes.c_size_t(0)
        
        ret = win32functions.ReadProcessMemory(
            ctypes.c_void_p(self.process),
            ctypes.c_void_p(address),
            ctypes.byref(data),
            nSize,
            ctypes.byref(lpNumberOfBytesRead))

        # disabled as it often returns an error - but
        # seems to work fine anyway!!
        if ret == 0:
            # try again
            ret = win32functions.ReadProcessMemory(
                ctypes.c_void_p(self.process),
                ctypes.c_void_p(address),
                ctypes.byref(data),
                nSize,
                ctypes.byref(lpNumberOfBytesRead))
            if ret == 0:
                last_error = win32api.GetLastError()
                if last_error != win32defines.ERROR_PARTIAL_COPY:
                    ActionLogger().log('Read: WARNING! self.memAddress =' + hex(self.memAddress) + ' data address =' + str(ctypes.byref(data)))
                    ActionLogger().log('LastError = ' + str(last_error) + ': ' + win32api.FormatMessage(last_error).rstrip())
                else:
                    ActionLogger().log('Error: ERROR_PARTIAL_COPY')
                    ActionLogger().log('\nRead: WARNING! self.memAddress =' + hex(self.memAddress) + ' data address =' + str(ctypes.byref(data)))
                
                ActionLogger().log('lpNumberOfBytesRead =' + str(lpNumberOfBytesRead) + ' nSize =' + str(nSize))
                raise ctypes.WinError()
            else:
                ActionLogger().log('Warning! Read OK: 2nd attempt!')
        #else:
        #    print 'Read OK: lpNumberOfBytesRead =', lpNumberOfBytesRead, ' nSize =', nSize
        
        self.CheckGuardSignature()
        return data

    #----------------------------------------------------------------
    def CheckGuardSignature(self):
        "read guard signature at the end of memory block"
        signature = win32structures.LONG(0)
        lpNumberOfBytesRead = ctypes.c_size_t(0)
        ret = win32functions.ReadProcessMemory(
            ctypes.c_void_p(self.process),
            ctypes.c_void_p(self.memAddress + self.size),
            ctypes.pointer(signature), # 0x66666666
            win32structures.ULONG_PTR(4),
            ctypes.byref(lpNumberOfBytesRead));
        if ret == 0:
            ActionLogger().log('Error: Failed to read guard signature: address = ' + hex(self.memAddress) +
                               ', size = ' + str(self.size) + ', lpNumberOfBytesRead = ' + str(lpNumberOfBytesRead))
            raise ctypes.WinError()
        else:
            if hex(signature.value) != '0x66666666':
                raise Exception('----------------------------------------   Error: read incorrect guard signature = ' + hex(signature.value))
