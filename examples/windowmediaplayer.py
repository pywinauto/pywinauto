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

"""Some automation of Windows Media player"""
from __future__ import unicode_literals
from __future__ import print_function

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
        app.start(r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe")
    except application.ProcessNotFoundError:
        print("You must first start Windows Media Player before running this script")
        sys.exit()

    # Wait for Window media player displays
    time.sleep(3)
    app.WindowsMediaPlayer.menu_select("View->Library")
    # Wait for the window library bar displays
    time.sleep(1)
    app.WindowsMediaPlayer.menu_select("View->Choose Columns")

    print("Is it checked already:", app.ChooseColumsn.ListView.is_checked(1))

    # Check an Item in the list view
    app.ChooseColumns.ListView.check(1)
    time.sleep(.5)
    print("Should be checked now:", app.ChooseColumsn.ListView.is_checked(1))

    # Uncheck it
    app.ChooseColumns.ListView.uncheck(1)
    time.sleep(.5)
    print("Should not be checked now:", app.ChooseColumsn.ListView.is_checked(1))

    # Check it again
    app.ChooseColumns.ListView.check(1)
    time.sleep(.5)

    app.ChooseColumsn.Cancel.click()
    time.sleep(.5)

    # Open a media file
    app.WindowsMediaPlayer.menu_select("File->Open")

    # Select and play a song
    song_path = "#push your path"
    window = app.Open
    window.Wait('ready')
    edit = window.Edit
    edit.type_keys(song_path)
    button = window[u'&Open']
    button.Click()

    # Let the music plays
    time.sleep(20)

    app.WindowsMediaPlayer.menu_select("File->Exit")


def main():
    start = time.time()

    windows_media()

    print("Total time taken:", time.time() - start)


if __name__ == "__main__":
    main()
