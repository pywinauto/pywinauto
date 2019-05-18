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

"""Module containing wrapper around VirtualAllocEx/VirtualFreeEx
Win32 API functions to perform custom marshalling
"""
from __future__ import print_function

import sys
import win32api

from ctypes import wintypes
from ctypes import c_void_p
from ctypes import pointer
from ctypes import sizeof
from ctypes import byref
from ctypes import c_size_t
from ctypes import WinError
from . import win32functions
from . import win32defines
from . import win32structures
from .actionlogger import ActionLogger


class AccessDenied(RuntimeError):

    """Raised when we cannot allocate memory in the control's process"""

    pass


# ====================================================================
class RemoteMemoryBlock(object):

    """Class that enables reading and writing memory in a different process"""

    #----------------------------------------------------------------
    def __init__(self, ctrl, size=4096):
        """Allocate the memory"""
        self.mem_address = 0
        self.size = size
        self.process = 0
        self.handle = ctrl.handle

        if self.handle == 0xffffffff80000000:
            raise Exception('Incorrect handle: ' + str(self.handle))

        self._as_parameter_ = self.mem_address

        pid = wintypes.DWORD()
        win32functions.GetWindowThreadProcessId(self.handle, byref(pid))
        process_id = pid.value
        if not process_id:
            raise AccessDenied(
                str(WinError()) + " Cannot get process ID from handle.")

        self.process = win32functions.OpenProcess(
            win32defines.PROCESS_VM_OPERATION |
            win32defines.PROCESS_VM_READ |
            win32defines.PROCESS_VM_WRITE,
            0,
            process_id
        )

        if not self.process:
            raise AccessDenied(
                str(WinError()) + "process: %d",
                process_id)

        self.mem_address = win32functions.VirtualAllocEx(
            c_void_p(self.process),  # remote process
            c_void_p(0),             # let Valloc decide where
            win32structures.ULONG_PTR(self.size + 4),  # how much to allocate
            win32defines.MEM_RESERVE | \
            win32defines.MEM_COMMIT,  # allocation type
            win32defines.PAGE_READWRITE  # protection
        )
        if hasattr(self.mem_address, 'value'):
            self.mem_address = self.mem_address.value

        if self.mem_address == 0:
            raise WinError()

        if hex(self.mem_address) == '0xffffffff80000000' or hex(self.mem_address).upper() == '0xFFFFFFFF00000000':
            raise Exception('Incorrect allocation: ' + hex(self.mem_address))

        self._as_parameter_ = self.mem_address

        # write guard signature at the end of memory block
        signature = wintypes.LONG(0x66666666)
        ret = win32functions.WriteProcessMemory(
            c_void_p(self.process),
            c_void_p(self.mem_address + self.size),
            pointer(signature),
            win32structures.ULONG_PTR(4),
            win32structures.ULONG_PTR(0)
        )
        if ret == 0:
            ActionLogger().log('================== Error: Failed to write guard signature: address = ' +
                               hex(self.mem_address) + ', size = ' + str(self.size))
            last_error = win32api.GetLastError()
            ActionLogger().log('LastError = ' + str(last_error) + ': ' + win32api.FormatMessage(last_error).rstrip())

    def _CloseHandle(self):
        """Close the handle to the process."""
        ret = win32functions.CloseHandle(self.process)
        #win32api.CloseHandle(self.process)

        if ret == 0:
            ActionLogger().log('Warning: cannot close process handle!')
            #raise WinError()

    #----------------------------------------------------------------
    def CleanUp(self):
        """Free Memory and the process handle"""
        if self.process != 0 and self.mem_address != 0:
            # free up the memory we allocated
            #win32api.SetLastError(0)
            self.CheckGuardSignature()

            ret = win32functions.VirtualFreeEx(
                c_void_p(self.process),
                c_void_p(self.mem_address),
                win32structures.ULONG_PTR(0),
                wintypes.DWORD(win32defines.MEM_RELEASE))
            if ret == 0:
                print('Error: CleanUp: VirtualFreeEx() returned zero for address ', hex(self.mem_address))
                last_error = win32api.GetLastError()
                print('LastError = ', last_error, ': ', win32api.FormatMessage(last_error).rstrip())
                sys.stdout.flush()
                self._CloseHandle()
                raise WinError()
            self.mem_address = 0
            self._CloseHandle()
        else:
            pass  # ActionLogger().log('\nWARNING: Cannot call VirtualFreeEx! process_id == 0.')

    #----------------------------------------------------------------
    def __del__(self):
        """Ensure that the memory is Freed"""
        # Free the memory in the remote process's address space
        self.CleanUp()

    #----------------------------------------------------------------
    def Address(self):
        """Return the address of the memory block"""
        return self.mem_address

    #----------------------------------------------------------------
    def Write(self, data, address=None, size=None):
        """Write data into the memory block"""
        # write the data from this process into the memory allocated
        # from the other process
        if not address:
            address = self.mem_address
        if hasattr(address, 'value'):
            address = address.value

        if size:
            nSize = win32structures.ULONG_PTR(size)
        else:
            nSize = win32structures.ULONG_PTR(sizeof(data))

        if self.size < nSize.value:
            raise Exception(('Write: RemoteMemoryBlock is too small ({0} bytes),' +
                            ' {1} is required.').format(self.size, nSize.value))

        if hex(address).lower().startswith('0xffffff'):
            raise Exception('Write: RemoteMemoryBlock has incorrect address = ' + hex(address))

        ret = win32functions.WriteProcessMemory(
            c_void_p(self.process),
            c_void_p(address),
            pointer(data),
            nSize,
            win32structures.ULONG_PTR(0)
        )

        if ret == 0:
            ActionLogger().log('Error: Write failed: address = ', address)
            last_error = win32api.GetLastError()
            ActionLogger().log('Error: LastError = ', last_error, ': ',
                               win32api.FormatMessage(last_error).rstrip())
            raise WinError()
        self.CheckGuardSignature()

    #----------------------------------------------------------------
    def Read(self, data, address=None, size=None):
        """Read data from the memory block"""
        if not address:
            address = self.mem_address
        if hasattr(address, 'value'):
            address = address.value

        if size:
            nSize = win32structures.ULONG_PTR(size)
        else:
            nSize = win32structures.ULONG_PTR(sizeof(data))

        if self.size < nSize.value:
            raise Exception(('Read: RemoteMemoryBlock is too small ({0} bytes),' +
                            ' {1} is required.').format(self.size, nSize.value))

        if hex(address).lower().startswith('0xffffff'):
            raise Exception('Read: RemoteMemoryBlock has incorrect address =' + hex(address))

        lpNumberOfBytesRead = c_size_t(0)

        ret = win32functions.ReadProcessMemory(
            c_void_p(self.process),
            c_void_p(address),
            byref(data),
            nSize,
            byref(lpNumberOfBytesRead)
        )

        # disabled as it often returns an error - but
        # seems to work fine anyway!!
        if ret == 0:
            # try again
            ret = win32functions.ReadProcessMemory(
                c_void_p(self.process),
                c_void_p(address),
                byref(data),
                nSize,
                byref(lpNumberOfBytesRead)
            )
            if ret == 0:
                last_error = win32api.GetLastError()
                if last_error != win32defines.ERROR_PARTIAL_COPY:
                    ActionLogger().log('Read: WARNING! self.mem_address =' +
                                       hex(self.mem_address) + ' data address =' + str(byref(data)))
                    ActionLogger().log('LastError = ' + str(last_error) +
                                       ': ' + win32api.FormatMessage(last_error).rstrip())
                else:
                    ActionLogger().log('Error: ERROR_PARTIAL_COPY')
                    ActionLogger().log('\nRead: WARNING! self.mem_address =' +
                                       hex(self.mem_address) + ' data address =' + str(byref(data)))

                ActionLogger().log('lpNumberOfBytesRead =' +
                                   str(lpNumberOfBytesRead) + ' nSize =' + str(nSize))
                raise WinError()
            else:
                ActionLogger().log('Warning! Read OK: 2nd attempt!')
        #else:
        #    print 'Read OK: lpNumberOfBytesRead =', lpNumberOfBytesRead, ' nSize =', nSize

        self.CheckGuardSignature()
        return data

    #----------------------------------------------------------------
    def CheckGuardSignature(self):
        """read guard signature at the end of memory block"""
        signature = win32structures.LONG(0)
        lpNumberOfBytesRead = c_size_t(0)
        ret = win32functions.ReadProcessMemory(
            c_void_p(self.process),
            c_void_p(self.mem_address + self.size),
            pointer(signature),  # 0x66666666
            win32structures.ULONG_PTR(4),
            byref(lpNumberOfBytesRead))
        if ret == 0:
            ActionLogger().log('Error: Failed to read guard signature: address = ' +
                               hex(self.mem_address) + ', size = ' + str(self.size) +
                               ', lpNumberOfBytesRead = ' + str(lpNumberOfBytesRead))
            raise WinError()
        else:
            if hex(signature.value) != '0x66666666':
                raise Exception('----------------------------------------   ' +
                                'Error: read incorrect guard signature = ' + hex(signature.value))
