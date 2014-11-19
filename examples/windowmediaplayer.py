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

"Some automation of Windows Media player"

__revision__ = "$Revision$"


#import os
import time
import sys

try:
    from pywinauto import application
except ImportError:
    import os.path
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    import sys
    sys.path.append(pywinauto_path)
    from pywinauto import application


def WindowsMedia():

    app = application.Application()

    try:
        app.start_(   # connect_(path =
            ur"C:\Program Files\Windows Media Player\wmplayer.exe")
    except application.ProcessNotFoundError:
        print "You must first start Windows Media "\
            "Player before running this script"
        sys.exit()

    app.WindowsMediaPlayer.MenuSelect("View->GoTo->Library")
    app.WindowsMediaPlayer.MenuSelect("View->Choose Columns")

    #for ctrl in app.ChooseColumns.Children():
    #    print ctrl.Class()


    print "Is it checked already:", app.ChooseColumsn.ListView.IsChecked(1)

    # Check an Item in the listview
    app.ChooseColumns.ListView.Check(1)
    time.sleep(.5)
    print "Shold be checked now:", app.ChooseColumsn.ListView.IsChecked(1)

    # Uncheck it
    app.ChooseColumns.ListView.UnCheck(1)
    time.sleep(.5)
    print "Should not be checked now:", app.ChooseColumsn.ListView.IsChecked(1)

    # Check it again
    app.ChooseColumns.ListView.Check(1)
    time.sleep(.5)

    app.ChooseColumsn.Cancel.Click()

    app.WindowsMediaPlayer.MenuSelect("File->Exit")


def Main():
    start = time.time()

    WindowsMedia()

    print "Total time taken:", time.time() - start

if __name__ == "__main__":
    Main()