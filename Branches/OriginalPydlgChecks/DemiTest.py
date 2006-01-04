"""
First of all, thanks Thomas for ctypes..
 
Hacked a bit into Henks Venster dialog class, using a different
c-source as basis. see -> Microsoft Knowledge Base Article - 141201.

http://support.microsoft.com/default.aspx?scid=kb;en-us;141201

Out came a bit more bare bone dialog class. Though I don"t
intend to start a win32 dialog discussion here I thought this source
could come in quite handy.
 
 
     J\\xfcrgen
 
* had to reformat it tabs to spaces on the fly, using notepad, 
so I hope theres no error in there.  

"""
 
from ctypes import windll, WINFUNCTYPE, byref, c_int as BOOL, \
c_ulong as HWND, c_uint as UINT, c_long as LPARAM, \
c_ushort as WORD

WPARAM = UINT

def LOWORD(dword): return dword & 0x0000ffff
def HIWORD(dword): return dword >> 16
 
 
DIALOGPROC = WINFUNCTYPE(BOOL, HWND, UINT, WPARAM, LPARAM)
 
 
_user32 = windll.user32
 
WM_CLOSE  = 16
WS_CHILD           = 1073741824
WS_VISIBLE         = 268435456
 #**************************************************

#**************************************************
class dialog(object):
 		
    def __init__(self, title, exstyle, style, x, y, w, h):
        self._items = 0
        self._id = 0
 		
        p = [
            1,                                 # dlgversion
            0xFFFF,                       # signature
            0,                                # LOWORD(helpId)
            0,                                # HIWORD(helpId)
            LOWORD(exstyle),    # extendedstyle
            HIWORD(exstyle),    # ...
            LOWORD(style),        # style
            HIWORD(style),        # ...
            0,                                # number of items
            x,                                # x
            y,                                # x
            w,                               # w
            h,                                # h
            0,                                # menu
            0,                                # class
            ]
 		
        title = map(ord, unicode(title)) + [0]
        p += title
        if len(p) % 2:
            p.append(0)
            
        #p.append(18)
       	#p.append(700)
       	#p.append(11)
       
            
           
        self.p = p
	
    def _dlgitem(self, classname, title, exstyle, style, x, y, w, h):
        self._items += 1
        self._id += 1
 		
        style  |= WS_CHILD | WS_VISIBLE
        p = [
            0,                                    # LOWORD(helpId)
            0,                                    # HIWORD(helpId)
            LOWORD(exstyle),        # extendedstyle
            HIWORD(exstyle),        # ...
            LOWORD(style),            # style
            HIWORD(style),            # ...
            x,                                    # x
            y,                                    # y
            w,                                   # w
            h,                                    # h
            LOWORD(self._id),        # controlId
            HIWORD(self._id)         # ...
            ]
 		
        classname = map(ord, unicode(classname)) + [0]
        p += classname
        title = map(ord, unicode(title)) + [0]
        p += title
        
        if len(p) % 2:
            p.append(0)
        else:
            p += [0, 0]
        self.p += p
		
  			
    def run_modal(self, hwnd=0):
        self.p[8] = self._items
		
        self._p_template = (WORD * len(self.p))(*self.p)
        self._p_dialogproc = DIALOGPROC(self.dialogproc)
 		
        result = _user32.DialogBoxIndirectParamA(
            0, byref(self._p_template), hwnd, self._p_dialogproc, 0
            )
        return result
 
 	
    def dialogproc(self, hwnd, message, wparam, lparam):
        if message==WM_CLOSE:
            _user32.EndDialog(hwnd, 0)
        return 0
 
 
#************************************************
#d = dialog("dialog sample", 0, 0, 30, 30, 160, 100)
#d._dlgitem("button", "button1", 0, 0, 5, 5, 30, 20)
#d._dlgitem("button", "button2", 0, 0, 5, 30, 30, 20)
#d._dlgitem("edit", "edit box", 0, 0, 40, 0, 50, 60)
#d._dlgitem("combobox", "",0, 0, 100, 0, 50, 65)
#

import sys
if len(sys.argv) < 2 :
	print "Please specify the XML file to read"
	sys.exit()

import PyDlgCheckerWrapper
PyDlgCheckerWrapper.InitDialogFromFile(sys.argv[1])
dlg = PyDlgCheckerWrapper.TestInfo['Dialog']

d = None

for i, ctrl in enumerate(dlg.AllControls()):
	print i
	if i == 0:
		d = dialog(
			ctrl.Text,
			0,#ctrl.ExStyle,
			0,#ctrl.Style,
			ctrl.Rectangle.left, # x
			ctrl.Rectangle.top,	# y
			ctrl.Rectangle.right - ctrl.Rectangle.left,	# cx
			ctrl.Rectangle.bottom - ctrl.Rectangle.top,	# cy
		)	

	else:
		d._dlgitem(
			ctrl.Class,
			ctrl.Text,
			ctrl.ExStyle,
			ctrl.Style,
			ctrl.Rectangle.left, # x
			ctrl.Rectangle.top,	# y
			ctrl.Rectangle.right - ctrl.Rectangle.left,	# cx
			ctrl.Rectangle.bottom - ctrl.Rectangle.top,	# cy
		)

	print d
d.run_modal()
 
