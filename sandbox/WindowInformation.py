import time
import sys
from pywinauto.controls import HwndWrapper
#from pywinauto.application import PrintControlIdentifiers
from pywinauto import win32functions, win32structures
import ctypes


#option to use WX if it is available
#option to output window declarations
# output escaping options


lastwindow = 0
lastpt = win32structures.POINT(0 , 0)
while True:
    pt = win32structures.POINT()
    win32functions.GetCursorPos(ctypes.byref(pt))

    # if the mouse is over the same window -
    # then don't bother printing it again
    #if lastwindow == win32functions.WindowFromPoint(pt):
        #continue

    if pt == lastpt:
        continue
    lastpt = pt

    wrapped_win = HwndWrapper.HwndWrapper(win32functions.WindowFromPoint(pt))

    print "========= %s =========="% wrapped_win.FriendlyClassName()
    print "'%s'" % wrapped_win.WindowText().encode('unicode-escape', 'replace')

    parent =  wrapped_win.Parent()
    if parent:
        s = u"In Window '%s' - '%s'" % (parent.FriendlyClassName(), parent.WindowText())
        print(s)
        print pt.x, pt.y, win32functions.WindowFromPoint(pt)

    parent2 =  wrapped_win.TopLevelParent()
    #print(sys.getfilesystemencoding())
    #print(sys.getdefaultencoding())
    if parent2:
        s = u"In Window '%s' - '%s'" % (parent2.FriendlyClassName(), parent2.WindowText())
        print(s)
        print pt.x, pt.y, win32functions.WindowFromPoint(pt)



    lastwindow = win32functions.WindowFromPoint(pt)

    time.sleep(1)
