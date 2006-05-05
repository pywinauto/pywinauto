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

"Controls package"

__revision__ = "$Revision$"

from HwndWrapper import GetDialogPropsFromHandle

# make an alias for the HwndWrapper object as WrapHandle
from HwndWrapper import HwndWrapper as WrapHandle

# import the control clases - this will register the classes they
# contain
import common_controls
import win32_controls

#
##====================================================================
#def _unittests():
#    "Run some tests on the controls"
#    from pywinauto import win32functions
#
#    "do some basic testing"
#    from pywinauto.findwindows import find_windows
#    import sys
#
#    if len(sys.argv) < 2:
#        handle = win32functions.GetDesktopWindow()
#    else:
#        try:
#            handle = int(eval(sys.argv[1]))
#
#        except ValueError:
#
#            handle = find_windows(
#                title_re = "^" + sys.argv[1], class_name = "#32770", )
#                #visible_only = False)
#
#            if not handle:
#                print "dialog not found"
#                sys.exit()
#
#
#    props = GetDialogPropsFromHandle(handle)
#    print len(props)
#    #pprint(GetDialogPropsFromHandle(handle))
#
#if __name__ == "__main__":
#    _unittests()
