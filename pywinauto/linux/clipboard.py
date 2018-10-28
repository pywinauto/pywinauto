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

"""Linux/Unix branch of the clipboard module

It uses some of the clipboard managers if available on the system.
Supported tools:
 * ``xsel``
 * ``xclip``
 * ``pbcopy / pbpaste`` (Mac OS X)
"""
import subprocess
import sys


def cmd_exists(cmd):
    """Check is app exist"""
    return subprocess.call("type " + cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def set_up_clipboard(is_input):
    """Find clipboard app in system"""
    command = []
    if sys.platform == 'linux' or sys.platform == 'linux2':
        if cmd_exists('xclip'):
            command.append('xclip')
            if is_input:
                command.append('-selection')
                command.append('c')
            else:
                command.append('-selection')
                command.append('c')
                command.append('-o')
        elif cmd_exists('xsel'):
            command.append('xsel')
            command.append('-b')
            if is_input:
                command.append('-i')
            else:
                command.append('-o')
    elif sys.platform == 'darwin':
        if is_input:
            command.append('pbcopy')
            command.append('w')
        else:
            command.append('pbpaste')
            command.append('r')
    if not command:
        raise NameError('No clipboard manager')
    return command


def get_data():
    """Get data from clipboard"""
    command = set_up_clipboard(is_input=False)
    process = subprocess.Popen(command,stdout=subprocess.PIPE, close_fds=True)
    stdout = process.communicate()
    return stdout[0].decode('utf-8')


def set_data(text):
    """Put some text to clipboard"""
    command = set_up_clipboard(is_input=True)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, close_fds=True)
    process.communicate(input=text.encode('utf-8'))
