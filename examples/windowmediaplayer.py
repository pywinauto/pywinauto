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

"""Some automation of Windows Media player"""
from __future__ import unicode_literals
from __future__ import print_function

#import os
import time
import sys

try:
    from pywinauto import application
except ImportError:
    import os.path
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    sys.path.append(pywinauto_path)
    from pywinauto import application


def windows_media():

    app = application.Application()

    try:
        app.start(   # connect_(path =
            r"C:\Program Files\Windows Media Player\wmplayer.exe")
    except application.ProcessNotFoundError:
        print("You must first start Windows Media "\
            "Player before running this script")
        sys.exit()

    app.WindowsMediaPlayer.menu_select("View->GoTo->Library")
    app.WindowsMediaPlayer.menu_select("View->Choose Columns")

    #for ctrl in app.ChooseColumns.children():
    #    print ctrl.class_name()


    print("Is it checked already:", app.ChooseColumsn.ListView.is_checked(1))

    # Check an Item in the listview
    app.ChooseColumns.ListView.check(1)
    time.sleep(.5)
    print("Shold be checked now:", app.ChooseColumsn.ListView.is_checked(1))

    # Uncheck it
    app.ChooseColumns.ListView.uncheck(1)
    time.sleep(.5)
    print("Should not be checked now:", app.ChooseColumsn.ListView.is_checked(1))

    # Check it again
    app.ChooseColumns.ListView.check(1)
    time.sleep(.5)

    app.ChooseColumsn.Cancel.click()

    app.WindowsMediaPlayer.menu_select("File->Exit")


def main():
    start = time.time()

    windows_media()

    print("Total time taken:", time.time() - start)

if __name__ == "__main__":
    main()