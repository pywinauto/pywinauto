# simple module for checking whether Python and Windows are 32-bit or 64-bit
# Copyright (C) 2015 Intel Corporation
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

import os, sys
import platform
import ctypes

def OS_architecture():
    architectureMap = {
        'x86':'x86',
        'i386':'x86',
        'i486':'x86',
        'i586':'x86',
        'i686':'x86',
        'x64':'x86_64',
        'AMD64':'x86_64',
        'amd64':'x86_64',
        'em64t':'x86_64',
        'EM64T':'x86_64',
        'x86_64':'x86_64',
        'IA64':'ia64',
        'ia64':'ia64'
    }
    if sys.platform == 'win32':
        architectureVar = os.environ.get('PROCESSOR_ARCHITEW6432', '')
        if architectureVar == '':
            architectureVar = os.environ.get('PROCESSOR_ARCHITECTURE', '')
        return architectureMap.get(architectureVar, 'Unknown')
    else:
        return architectureMap.get(platform.machine(), '')

def PythonBitness():
    return ctypes.sizeof(ctypes.POINTER(ctypes.c_int)) * 8

def is_x64_Python():
    return PythonBitness() == 64

def is_x64_OS():
    return OS_architecture() in ['x86_64', 'ia64']
