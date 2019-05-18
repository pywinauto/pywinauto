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

import sys
import os.path
import time

try:
    from pywinauto import application
except ImportError:
    pywinauto_path = os.path.abspath(__file__)
    pywinauto_path = os.path.split(os.path.split(pywinauto_path)[0])[0]
    sys.path.append(pywinauto_path)
    from pywinauto import application

import pywinauto
from pywinauto import tests
#from pywinauto.findbestmatch import MatchError

from pywinauto.timings import Timings

def run_notepad():
    """Run notepad and do some small stuff with it"""
    print("Run with option 'language' e.g. notepad_fast.py language to use")
    print("application data. This should work on any language Windows/Notepad")
    print()
    print("Trying fast timing settings - it's  possible these won't work")
    print("if pywinauto tries to access a window that is not accessible yet")

    # use fast timings - but allow to wait for windows a long time
    Timings.fast()
    Timings.window_find_timeout = 10

    start = time.time()

    run_with_appdata = False
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'language':
        run_with_appdata = True

    scriptdir = os.path.split(os.path.abspath(__file__))[0]
    if run_with_appdata:
        print("\nRunning this script so it will load application data and run")
        print("against any lanuguage version of Notepad/Windows")

        # make sure that the app data gets read from the same folder as
        # the script
        app = application.Application(
            os.path.join(scriptdir, "Notepad_fast.pkl"))
    else:
        app = application.Application()

    ## for distribution we don't want to connect to anybodies application
    ## because we may mess up something they are working on!
    #try:
    #    app.connect_(path = r"c:\windows\system32\notepad.exe")
    #except application.ProcessNotFoundError:
    #    app.start_(r"c:\windows\system32\notepad.exe")
    app.start(r"notepad.exe")

    app.Notepad.menu_select("File->PageSetup")

    # ----- Page Setup Dialog ----
    # Select the 4th combobox item
    app.PageSetupDlg.SizeComboBox.select(4)

    # Select the 'Letter' combobox item or the Letter
    try:
        app.PageSetupDlg.SizeComboBox.select("Letter")
    except ValueError:
        app.PageSetupDlg.SizeComboBox.select('Letter (8.5" x 11")')

    app.PageSetupDlg.SizeComboBox.select(2)

    # run some tests on the Dialog. List of available tests:
    #        "AllControls",
    #        "AsianHotkey",
    #        "ComboBoxDroppedHeight",
    #        "CompareToRefFont",
    #        "LeadTrailSpaces",
    #        "MiscValues",
    #        "Missalignment",
    #        "MissingExtraString",
    #        "Overlapping",
    #        "RepeatedHotkey",
    #        "Translation",
    #        "Truncation",

    bugs = app.PageSetupDlg.run_tests('RepeatedHotkey Truncation')

    # if there are any bugs they will be printed to the console
    # and the controls will be highlighted
    tests.print_bugs(bugs)

    # ----- Next Page Setup Dialog ----
    app.PageSetupDlg.Printer.click()

    # do some radio button clicks
    # Open the Connect to printer dialog so we can
    # try out checking/unchecking a checkbox
    app.PageSetupDlg.Network.click()

    # ----- Connect To Printer Dialog ----
    # Select a checkbox
    app.ConnectToPrinter.ExpandByDefault.check()

    app.ConnectToPrinter.ExpandByDefault.uncheck()

    # try doing the same by using click
    app.ConnectToPrinter.ExpandByDefault.click()

    app.ConnectToPrinter.ExpandByDefault.click()

    # close the dialog
    app.ConnectToPrinter.Cancel.close_click()

    # ----- 2nd Page Setup Dialog again ----
    app.PageSetupDlg.Properties.click()

    doc_props = app.window(title_re = ".*Properties$")
    doc_props.wait('exists', timeout=40)

#
#    # ----- Document Properties Dialog ----
#    # some tab control selections
#    # Two ways of selecting tabs with indices...
#    doc_props.TabCtrl.select(0)
#    doc_props.TabCtrl.select(1)
#    try:
#        doc_props.TabCtrl.select(2)
#    except IndexError:
#        # not all users have 3 tabs in this dialog
#        pass
#
#    # or with text...
#    #doc_props.TabCtrl.select("PaperQuality")
#    doc_props.TabCtrl.select(1)
#
#    try:
#        #doc_props.TabCtrl.select("JobRetention")
#        doc_props.TabCtrl.select("3")
#    except MatchError:
#        # some people do not have the "Job Retention" tab
#        pass
#
#    doc_props.TabCtrl.select("Finishing")
#    #doc_props.TabCtrl.select(0)
#
#    # do some radio button clicks
#    doc_props.RotatedLandscape.click()
#    doc_props.BackToFront.click()
#    doc_props.FlipOnShortEdge.click()
#
#    doc_props.Portrait.click()
#    doc_props._None.click()
#    #doc_props.FrontToBack.click()
#
#    # open the Advanced options dialog in two steps
#    advbutton = doc_props.Advanced
#    advbutton.click()
#
#    # close the 4 windows
#
#    # ----- Advanced Options Dialog ----
#    app.window(title_re = ".* Advanced Options").Ok.click()

    # ----- Document Properties Dialog again ----
    doc_props.Cancel.close_click()
    
    # for some reason my current printer driver
    # window does not close cleanly :(
    if doc_props.Cancel.Exists():
        doc_props.OK.close_click()

    # ----- 2nd Page Setup Dialog again ----
    app.PageSetupDlg.OK.close_click()
    # ----- Page Setup Dialog ----
    app.PageSetupDlg.Ok.close_click()

    # type some text - note that extended characters ARE allowed
    app.Notepad.Edit.set_edit_text(u"I am typing s\xe4me text to Notepad\r\n\r\n"
        "And then I am going to quit")

    app.Notepad.Edit.right_click()
    app.Popup.menu_item("Right To Left Reading Order").click()
    #app.PopupMenu.menu_select("Paste", app.Notepad.ctrl_())
    #app.Notepad.Edit.right_click()
    #app.PopupMenu.menu_select(
    #    "Right To Left Reading Order", app.Notepad.ctrl_())
    #app.PopupMenu.menu_select(
    #    "Show unicode control characters", app.Notepad.ctrl_())
    #time.sleep(1)
    #app.Notepad.Edit.right_click()
    #app.PopupMenu.menu_select("Right To Left Reading Order", app.Notepad.ctrl_())
    #time.sleep(1)

    #app.Notepad.Edit.right_click()
    #app.PopupMenu.menu_select(
    #    "Insert Unicode control character -> IAFS", app.Notepad.ctrl_())
    #time.sleep(1)

    #app.Notepad.Edit.type_keys("{ESC}")

    # the following shows that Sendtext does not accept
    # accented characters - but does allow 'control' characters
    app.Notepad.Edit.type_keys(u"{END}{ENTER}SendText d\xf6\xe9s "
        u"s\xfcpp\xf4rt \xe0cce\xf1ted characters!!!", with_spaces = True)

    # Try and save
    app.Notepad.menu_select("File->SaveAs")
    app.SaveAs.EncodingComboBox.select("UTF-8")
    app.SaveAs.FileNameEdit.set_edit_text("Example-utf8.txt")
    app.SaveAs.Save.close_click()

    # my machine has a weird problem - when connected to the network
    # the SaveAs Dialog appears - but doing anything with it can
    # cause a LONG delay - the easiest thing is to just wait
    # until the dialog is no longer active

    # - Dialog might just be gone - because click worked
    # - dialog might be waiting to disappear
    #   so can't wait for next dialog or for it to be disabled
    # - dialog might be waiting to display message box so can't wait
    #   for it to be gone or for the main dialog to be enabled.

    # while the dialog exists wait upto 30 seconds (and yes it can
    # take that long on my computer sometimes :-( )
    app.SaveAsDialog2.Cancel.wait_not('enabled')

    # If file exists - it asks you if you want to overwrite
    try:
        app.SaveAs.Yes.wait('exists').close_click()
    except pywinauto.MatchError:
        print('Skip overwriting...')

    # exit notepad
    app.Notepad.menu_select("File->Exit")

    if not run_with_appdata:
        app.WriteAppData(os.path.join(scriptdir, "Notepad_fast.pkl"))

    print("That took %.3f to run"% (time.time() - start))

if __name__ == "__main__":
    run_notepad()
