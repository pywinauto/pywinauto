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

"""Run some automations to test things"""
from __future__ import unicode_literals
from __future__ import print_function

try:
    from pywinauto import application
except ImportError:
    import os.path
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    import sys
    sys.path.append(pywinauto_path)
    from pywinauto import application

#from pywinauto import tests
#from pywinauto.findbestmatch import MatchError
from pywinauto.timings import Timings

Timings.window_find_timeout = 10

def test_exceptions():
    """Test some things that should raise exceptions"""
    # test that trying to connect_ to a non existent app fails
    try:
        app = application.Application()
        app.connect(path=r"No process with this please")
        assert False
    except application.ProcessNotFoundError:
        print('ProcessNotFoundError has been raised. OK.')

    # test that trying to connect_ to a non existent app fails
    try:
        app = application.Application()
        app.start(cmd_line = r"No process with this please")
        assert False
    except application.AppStartError:
        print('AppStartError has been raised. OK.')

#    # try when it isn't connected
#    try:
#        app = application.Application()
#        #app.start_(ur"c:\windows\system32\notepad.exe")
#        app.Notepad.click()
#        #assert False
#    except application.AppNotConnected:
#        pass



def get_info():
    """Run Notepad, print some identifiers and exit"""
    app = application.Application()

    app.start(r"notepad.exe")

    app.Notepad.menu_select("File->PageSetup")

    print("==" * 20)
    print("Windows of this application:", app.windows())

    print("The list of identifiers for the Page Setup dialog in Notepad")
    print("==" * 20)
    app.PageSetup.print_control_identifiers()
    print("==" * 20)
    print("The list of identifiers for the 2nd Edit control in the dialog")
    app.PageSetup.Edit2.print_control_identifiers()
    print("==" * 20)

    app.PageSetup.OK.close_click()
    app.Notepad.menu_select("File->Exit")



if __name__ == '__main__':
    test_exceptions()
    get_info()
