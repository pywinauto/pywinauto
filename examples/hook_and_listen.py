import win32api
import win32con
from threading import Timer
from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent
from pywinauto.win32_hooks import MouseEvent


def on_timer():
    """Callback by timer out"""
    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0);


def on_event(args):
    """Callback for keyboard and mouse events"""
    if isinstance(args, KeyboardEvent):
        if args.current_key == 'A' and args.event_type == 'key down' and 'Lcontrol' in args.pressed_key:
            print("Ctrl + A was pressed");

        if args.current_key == 'K' and args.event_type == 'key down':
            print("K was pressed");

        if args.current_key == 'M' and args.event_type == 'key down' and 'U' in args.pressed_key:
            hk.unhook_mouse()
            print("Unhook mouse")

        if args.current_key == 'K' and args.event_type == 'key down' and 'U' in args.pressed_key:
            hk.unhook_keyboard()
            print("Unhook keyboard")

    if isinstance(args, MouseEvent):
        if args.current_key == 'RButton' and args.event_type == 'key down':
            print ("Right button pressed")

        if args.current_key == 'WheelButton' and args.event_type == 'key down':
            print("Wheel button pressed")

hk = Hook()
hk.handler = on_event
main_thread_id = win32api.GetCurrentThreadId()
t = Timer(5.0, on_timer)  # Quit after 5 seconds
t.start()
hk.hook(keyboard=True, mouse=True)
