import time
from pywinauto.controls import HwndWrapper
#from pywinauto.application import PrintControlIdentifiers
from pywinauto import win32functions, win32structures
import ctypes


#option to use WX if it is available
#option to output window declarations
# output escaping options


lastwindow = 0
while True:
    pt = win32structures.POINT()
    win32functions.GetCursorPos(ctypes.byref(pt))

    # if the mouse is over the same window -
    # then don't bother printing it again
    if lastwindow == win32functions.WindowFromPoint(pt):
        continue

    wrapped_win = HwndWrapper.HwndWrapper(win32functions.WindowFromPoint(pt))

    print "========= %s =========="% wrapped_win.FriendlyClassName()
    print "'%s'" % wrapped_win.WindowText().encode('unicode-escape', 'replace')

    parent =  wrapped_win.Parent()
    if parent:
        print "In Window '%s' - '%s'" % (
            parent.FriendlyClassName(), parent.WindowText().encode())#'mbcs', 'replace', "?"))

    parent2 =  wrapped_win.TopLevelParent()
    if parent2:
        print "In Window '%s' - '%s'" % (
            parent2.FriendlyClassName(), parent2.WindowText().encode())#'mbcs', 'replace'))


    print

    #print pt.x, pt.y, win32functions.WindowFromPoint(pt)


    lastwindow = win32functions.WindowFromPoint(pt)

    time.sleep(1)
