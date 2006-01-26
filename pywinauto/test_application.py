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

"Run some automations to test things"

__revision__ = "$Revision$"

import time

import application
import tests
from findbestmatch import MatchError

def TestExceptions():
    "Test some things that should raise exceptions"

    # test that trying to connect_ to a non existent app fails
    try:
        app = application.Application()
        app.connect_(path = ur"No process with this please")
        assert False
    except application.ProcessNotFoundError:
        pass

    # test that trying to connect_ to a non existent app fails
    try:
        app = application.Application()
        app.start_(cmd_line = ur"No process with this please")
        assert False
    except application.AppStartError:
        pass

    # try when it isn't connected
    try:
        app = application.Application()
        #app.start_(ur"c:\windows\system32\notepad.exe")
        app.Notepad.Click()
        assert False
    except application.AppNotConnected:
        pass

def MinimalNotepadTest():
    "Run a quick test on Notepad"

    app = application.Application()
    app.start_(ur"notepad.exe")

    app.Notepad.WaitExists()

    app.Notepad.MenuSelect("File->PageSetup")

    # ----- Page Setup Dialog ----
    # Select the 4th combobox item
    app.PageSetupDlg.ComboBox1.Select(4)

    try:
        # specify a control that should not exist and
        # ask for one of it's properties to make sure it is
        # resolved.
        print app.PageSetup.notFound.Font
    except MatchError, e:
        print "Text that you were looking for", e.tofind
        print "========== Available list of controls ======="
        for i in sorted(e.items):
            print "\t%s"% i


    print app.windows_()
    # Select the 'Letter' combobox item
    app.PageSetupDlg.ComboBox1.Select("Letter")

    # ----- Next Page Setup Dialog ----
    app.PageSetupDlg.Printer.Click()
    #time.sleep(.2)

    app.PageSetupDlg.Network.Click()

    # ----- Connect To Printer Dialog ----
    # Select a checkbox
    app.ConnectToPrinter.ExpandByDef.Check()
    # Uncheck it again - but use Click this time!
    app.ConnectToPrinter.ExpandByDef.Click()

    app.ConnectToPrinter.OK.CloseClick()

    # ----- 2nd Page Setup Dialog again ----
    app.PageSetupDlg2.Properties.Click()

    # ----- Document Properties Dialog ----
    docProps = app.window_(title_re = ".*Document Properties")

    # Two ways of selecting tabs
    docProps.TabCtrl.Select(2)
    docProps.TabCtrl.Select("Layout")

    # click some Radio buttons
    docProps.RotatedLandscape.Click()
    docProps.BackToFront.Click()
    docProps.FlipOnShortEdge.Click()

    docProps.Portrait.Click()
    docProps._None.Click()  # need to disambiguate from keyword None
    docProps.FrontToBack.Click()

    # open the Advanced options dialog in two steps
    advbutton = docProps.Advanced
    advbutton.Click()

    # ----- Advanced Options Dialog ----
    # close the 4 windows
    app.window_(title_re = ".* Advanced Options").Ok.Click()

    # ----- Document Properties Dialog again ----
    docProps.Cancel.CloseClick()
    # ----- 2nd Page Setup Dialog again ----
    app.PageSetup2.OK.CloseClick()
    # ----- Page Setup Dialog ----
    app.PageSetup.Ok.CloseClick()

    # type some text
    app.Notepad.Edit.SetText(u"I am typing säme text to Notepad\r\n\r\n"
        "And then I am going to quit")

    # the following shows that Sendtext does not accept
    # accented characters - but does allow 'control' characters
    #app.Notepad.Edit.TypeKeys(u"{END}{ENTER}SendText döés not "
    #   "süppôrt àcceñted characters", with_spaces = True)

    app.Notepad.MenuSelect("File->SaveAs")
    app.SaveAs.ComboBox5.Select("UTF-8")
    app.SaveAs.edit1.SetText("Example-utf8.txt")
    app.SaveAs.Save.CloseClick()

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
    app.SaveAs.Cancel.WaitNotEnabled()

    try:
        app.SaveAs.Yes.CloseClick()
    except MatchError:
        pass

    print app.NotepadDialog.handle, app.NotepadDialog.Texts, app.NotepadDialog.Class

    time.sleep(.1)
    # exit notepad
    app.NotepadDialog.MenuSelect("File->Exit")
    #app.Notepad.No.Click()



def TestNotepad():
    "Run a test on notepad"

    app = application.Application()

#	# for distribution we don't want to connect to anybodies application
#   # because we may mess up something they are working on!
#	try:
#		app.connect_(path = ur"c:\windows\system32\notepad.exe")
#	except application.ProcessNotFoundError:
#		app.start_(ur"c:\windows\system32\notepad.exe")
    app.start_(ur"notepad.exe")

    app.Notepad.MenuSelect("File->PageSetup")

    app.PageSetupDlg.ComboBox1.Select(4)
    bugs = app.PageSetupDlg.RunTests('AsianHotkey')

    tests.print_bugs(bugs)

    app.PageSetupDlg.Printer.Click()

    TestingCheckBox = 1
    if TestingCheckBox:
        # Open the Connect to printer dialog so we can
        # try out checking/unchecking a checkbox
        app.PageSetupDlg.Network.Click()

        app.ConnectToPrinter.ExpandByDefault.Check()

        app.ConnectToPrinter.ExpandByDefault.UnCheck()

        # try doing the same by using click
        app.ConnectToPrinter.ExpandByDefault.Click()

        app.ConnectToPrinter.ExpandByDefault.Click()

        # close the dialog
        app.ConnectToPrinter.Cancel.CloseClick()

    app.PageSetupDlg2.Properties.Click()

    docProps = app.window_(title_re = ".*Document Properties")

    TestingTabSelect = 1
    if TestingTabSelect:
        docProps.TabCtrl.Select(0)
        docProps.TabCtrl.Select(1)
        docProps.TabCtrl.Select(2)

        docProps.TabCtrl.Select("PaperQuality")
        docProps.TabCtrl.Select("JobRetention")
        docProps.TabCtrl.Select("Layout")


    TestingRadioButton = 1
    if TestingRadioButton:
        docProps.RotatedLandscape.Click()
        docProps.BackToFront.Click()
        docProps.FlipOnShortEdge.Click()

        docProps.Portrait.Click()
        docProps._None.Click()
        docProps.FrontToBack.Click()

    advbutton = docProps.Advanced
    advbutton.Click()

    # close the 4 windows
    app.window_(title_re = ".* Advanced Options").Ok.Click()
    docProps.Cancel.CloseClick()
    app.PageSetupDlg2.OK.CloseClick()
    app.PageSetupDlg.Ok.CloseClick()

    # type some text
    app.Notepad.Edit.SetText(u"I am typing säme text to Notepad\r\n\r\n"
        "And then I am going to quit")

    # the following shows that
    app.Notepad.Edit.TypeKeys(u"{END}{ENTER}SendText döés not süppôrt "
        u"àcceñted characters", with_spaces = True)

    # exit notepad
    app.Notepad.MenuSelect("File->Exit")
    app.Notepad.No.CloseClick()



def TestPaint():
    "Run some tests on MSPaint"
    app = application.Application()

#	# for distribution we don't want to connect to anybodies application
#   # because we may mess up something they are working on!
#	try:
#		app.connect_(path = ur"c:\windows\system32\mspaint.exe")
#	except application.ProcessNotFoundError:
#		app.start_(ur"c:\windows\system32\mspaint.exe")

    app.start_(ur"mspaint.exe")

    pwin = app.window_(title_re = ".* - Paint")

    # get the previous image size
    pwin.MenuSelect("Image->Attributes")
    prev_width = app.Attributes.Edit1.Texts[1]
    prev_height = app.Attributes.Edit2.Texts[1]

    # set our preferred area
    app.Attributes.Edit1.TypeKeys("350")  # you can use TypeKeys or
    app.Attributes.Edit2.SetText("350")   # SetText - they work differently!

    app.Attributes.OK.CloseClick()

    # get the reference to the Canvas window
    canvas = pwin.Afx100000008

    # make sure the pencil tool is selected
    pwin.Tools2.Click(coords = (91, 16))

    size = 15
    num_slants = 20

    # draw the axes
    canvas.PressMouse(coords = (size, size * num_slants))
    canvas.MoveMouse(coords = (size*num_slants, size*num_slants))
    canvas.MoveMouse(coords = (size * num_slants, size))
    canvas.ReleaseMouse()

    # now draw the lines
    print "*** if you move your mouse over Paint as it is drawing ***"
    print "*** these lines then it will mess up the drawing!      ***\n"
    for i in range(1, num_slants):

        endcoords = (size * (num_slants - i), size * num_slants)
        canvas.PressMouse(coords = (size * num_slants, i * size)) # start
        canvas.MoveMouse(coords = endcoords) # x and y axes
        canvas.ReleaseMouse(coords = endcoords)

    # may fail if PIL is not installed
    image = canvas.CaptureAsImage()
    if image:
        image.save(r"Application_Paint_test.png")
        print "Saved image as: Application_Paint_test.png"

    # set it back to  original width and height
    pwin.MenuSelect("Image->Attributes")
    # set our preferred area
    app.Attributes.Edit1.TypeKeys(prev_width)
    app.Attributes.Edit2.SetText(prev_height)
    app.Attributes.OK.CloseClick()


    # close Paint
    pwin.MenuSelect("File->Exit")

    if app.Paint.No.Exists():
        print "It existed!"
        # Click the no button on the message box asking if we want to save
        app.Paint.No.CloseClick()

def Main():
    "Run the tests"
    start = time.time()

    MinimalNotepadTest()

    TestExceptions()
    TestNotepad()
    TestPaint()

    print "Total time taken:", time.time() - start

if __name__ == "__main__":
    Main()