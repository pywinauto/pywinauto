import sys
import win32con
from .injector import Injector
from ... import Desktop
from ctypes import wintypes
import ctypes

msg_id_to_key = {getattr(win32con, attr_name): attr_name for attr_name in dir(win32con) if attr_name.startswith('WM_')}

def print_winmsg(msg):
    print("hWnd:{}".format(str(msg.hWnd)))
    print("message:{}".format((msg_id_to_key[msg.message] if msg.message in msg_id_to_key else str(msg.message))))
    print("wParam:{}".format(str(msg.wParam)))
    print("lParam:{}".format(str(msg.lParam)))
    print("time:{}".format(str(msg.time)))
    print("pt:{}".format(str(msg.pt.x) + ',' + str(msg.pt.x)))

if (len(sys.argv) != 2):
    print("Usage: {} <Process name>".format(sys.argv[0]))
    sys.exit(0)

inj = Injector(Desktop(backend="win32")[sys.argv[1]])
sock = inj.socket

while(1):
    msg = wintypes.MSG()
    m = sock.recvfrom(1024)
    ctypes.memmove(ctypes.pointer(msg),m[0],ctypes.sizeof(msg))
    print_winmsg(msg)
    if msg.message == win32con.WM_QUIT:
        break
