from pywinauto.hooks import Hook
from pywinauto.hooks import KeyboardEvent
from pywinauto.hooks import MouseEvent


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
hk.hook(keyboard=True, mouse=True)