#encoding=latin1

"Reimplement some of the watsup tests using pywinauto"
import sys
from time import sleep
import os
import os.path

from application import Application, WindowNotFoundError


def do_test_1():
    "1st Watsup Test"
    app = Application()._start(r"c:\windows\Notepad")
    notepadWindow = app.Notepad

    notepadWindow.Edit1.SetText(u"Hello, ägain!", 0, -1)
    sleep(0.8)
    notepadWindow.Edit.SetText("\r\nYou still there?")

    sleep(0.2)
    notepadWindow.Edit.SetText("\r\nGoing Bye Bye now!!")

    sleep(1)
    notepadWindow.MenuSelect("File->Exit")

    app.Notepad.No.Click()


def do_test_2():
    "2nd Watsup Test"
    filename = 'atestfile.txt'

    if os.path.exists(filename):
        os.remove(filename)

    app = Application()
    try:
        app._connect(title ='Simple Form')
    except WindowNotFoundError:
        app._start(r'examples\simple.exe')

    form = app.SimpleForm

    form.Edit.SetText(filename)
    sleep(.6)

    print 'clicking button to create file'
    form.CreateFile.Click()

    # now check that the file is there
    if os.path.exists(filename):
        print 'file %s is present' % filename
    else:
        print "file %s isn't there" % filename

    form.MenuSelect("File->Exit")


def do_test_3():
    "3rd Watsup Test"
    app = Application()
    try:
        app._connect(title ='Performance Form 2')
    except WindowNotFoundError:
        app._start(r'examples\perform2.exe')

    app.PerformanceForm1.Clickme.Click()
    waited = 0
    while not app.PerformacneForm1.Edit1._.Texts and not waited >= 1:
        print 'waiting'
        sleep(.1)
        waited += .1

    print `app.PerformacneForm1.Edit1._.Texts`






def Main():
    "run the specified test"
    for test_num in sys.argv[1:]:
        globals()['do_test_%s'%test_num] ()


if __name__ == "__main__":
    Main()
