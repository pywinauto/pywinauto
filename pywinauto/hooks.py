from ctypes import wintypes
from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_uint, c_long, c_longlong, c_ulong, c_void_p, byref, sizeof
from ctypes import Structure
import atexit

if sizeof(POINTER(c_int)) * 8 == 64:
    hinstance = c_longlong
else:
    hinstance = c_long

cmp_func = CFUNCTYPE(c_int, c_int, hinstance, POINTER(c_void_p))
DWORD = c_ulong

windll.kernel32.GetModuleHandleA.restype = wintypes.HMODULE
windll.kernel32.GetModuleHandleA.argtypes = [wintypes.LPCWSTR]

windll.user32.SetWindowsHookExA.restype = c_int
windll.user32.SetWindowsHookExA.argtypes = [c_int, cmp_func, hinstance, DWORD]


class MSG(Structure):
    """MGS Structure for GetMessageW methods"""
    _fields_ = [("hWnd", hinstance),
                ("message", c_uint),
                ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM),
                ("time", wintypes.DWORD),
                ("pt", wintypes.POINT)]

windll.user32.GetMessageW.argtypes = [MSG, hinstance, c_uint, c_uint]
windll.user32.TranslateMessage.argtypes = [POINTER(MSG)]
windll.user32.DispatchMessageW.argtypes = [POINTER(MSG)]


def _callback_pointer(handler):
    """Create and return C-pointer"""
    return cmp_func(handler)


class KeyboardEvent(object):
    """Is created when keyboard event catch"""
    def __init__(self, current_key=None, event_type=None, pressed_key=None):
        self.current_key = current_key
        self.event_type = event_type
        self.pressed_key = pressed_key


class MouseEvent(object):
    """Is created when mouse event catch"""

    def __init__(self, current_key=None, event_type=None):
        self.current_key = current_key
        self.event_type = event_type


class Hook(object):
    """Allow hook low level keyboard and mouse events"""
    MOUSE_ID_TO_KEY = {512: 'Move',
                       513: 'LButton',
                       514: 'LButton',
                       516: 'RButton',
                       517: 'RButton',
                       519: 'WheelButton',
                       520: 'WheelButton',
                       522: 'Wheel'}

    MOUSE_ID_TO_EVENT_TYPE = {512: None,
                              513: 'key down',
                              514: 'key up',
                              516: 'key down',
                              517: 'key up',
                              519: 'key down',
                              520: 'key up',
                              522: None}

    ID_TO_KEY = {8: 'Back',
                 9: 'Tab',
                 13: 'Return',
                 20: 'Capital',
                 27: 'Escape',
                 32: 'Space',
                 33: 'Prior',
                 34: 'Next',
                 35: 'End',
                 36: 'Home',
                 37: 'Left',
                 38: 'Up',
                 39: 'Right',
                 40: 'Down',
                 44: 'Snapshot',
                 46: 'Delete',
                 48: '0',
                 49: '1',
                 50: '2',
                 51: '3',
                 52: '4',
                 53: '5',
                 54: '6',
                 55: '7',
                 56: '8',
                 57: '9',
                 65: 'A',
                 66: 'B',
                 67: 'C',
                 68: 'D',
                 69: 'E',
                 70: 'F',
                 71: 'G',
                 72: 'H',
                 73: 'I',
                 74: 'J',
                 75: 'K',
                 76: 'L',
                 77: 'M',
                 78: 'N',
                 79: 'O',
                 80: 'P',
                 81: 'Q',
                 82: 'R',
                 83: 'S',
                 84: 'T',
                 85: 'U',
                 86: 'V',
                 87: 'W',
                 88: 'X',
                 89: 'Y',
                 90: 'Z',
                 91: 'Lwin',
                 92: 'Rwin',
                 93: 'App',
                 95: 'Sleep',
                 96: 'Numpad0',
                 97: 'Numpad1',
                 98: 'Numpad2',
                 99: 'Numpad3',
                 100: 'Numpad4',
                 101: 'Numpad5',
                 102: 'Numpad6',
                 103: 'Numpad7',
                 104: 'Numpad8',
                 105: 'Numpad9',
                 106: 'Multiply',
                 107: 'Add',
                 109: 'Subtract',
                 110: 'Decimal',
                 111: 'Divide',
                 112: 'F1',
                 113: 'F2',
                 114: 'F3',
                 115: 'F4',
                 116: 'F5',
                 117: 'F6',
                 118: 'F7',
                 119: 'F8',
                 120: 'F9',
                 121: 'F10',
                 122: 'F11',
                 123: 'F12',
                 144: 'Numlock',
                 160: 'Lshift',
                 161: 'Rshift',
                 162: 'Lcontrol',
                 163: 'Rcontrol',
                 164: 'Lmenu',
                 165: 'Rmenu',
                 186: 'Oem_1',
                 187: 'Oem_Plus',
                 188: 'Oem_Comma',
                 189: 'Oem_Minus',
                 190: 'Oem_Period',
                 191: 'Oem_2',
                 192: 'Oem_3',
                 219: 'Oem_4',
                 220: 'Oem_5',
                 221: 'Oem_6',
                 222: 'Oem_7',
                 1001: 'mouse left',  # mouse hotkeys
                 1002: 'mouse right',
                 1003: 'mouse middle',
                 1000: 'mouse move',  # single event hotkeys
                 1004: 'mouse wheel up',
                 1005: 'mouse wheel down',
                 1010: 'Ctrl',  # merged hotkeys
                 1011: 'Alt',
                 1012: 'Shift',
                 1013: 'Win'}

    event_types = {0x100: 'key down',  # WM_KeyDown for normal keys
                   0x101: 'key up',  # WM_KeyUp for normal keys
                   0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
                   0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
                   }

    WH_KEYBOARD_LL = 0x00D
    WH_MOUSE_LL = 0x0E
    WM_QUIT = 0x0012

    def __init__(self):
        self.handler = 0
        self.pressed_keys = []
        self.keyboard_id = None
        self.mouse_id = None
        self.mouse_is_hook = False
        self.keyboard_is_hook = False

    def hook(self, keyboard=True, mouse=False):
        """Hook mouse and/or keyboard events"""
        self.mouse_is_hook = mouse
        self.keyboard_is_hook = keyboard

        if not self.mouse_is_hook and not self.keyboard_is_hook:
            return

        if self.keyboard_is_hook:
            def keyboard_low_level_handler(code, event_code, kb_data_ptr):
                """Execute when keyboard low level event was catched"""
                try:
                    key_code = 0xFFFFFFFF & kb_data_ptr[0]
                    current_key = self.ID_TO_KEY[key_code]
                    event_type = self.event_types[0xFFFFFFFF & event_code]

                    if event_type == 'key down':
                        self.pressed_keys.append(current_key)

                    if event_type == 'key up':
                        self.pressed_keys.remove(current_key)

                    event = KeyboardEvent(current_key, event_type, self.pressed_keys)

                    if self.handler != 0:
                        self.handler(event)

                finally:
                    return windll.user32.CallNextHookEx(self.keyboard_id, code, event_code, kb_data_ptr)

            keyboard_pointer = _callback_pointer(keyboard_low_level_handler)

            self.keyboard_id = windll.user32.SetWindowsHookExA(self.WH_KEYBOARD_LL, keyboard_pointer,
                                                               windll.kernel32.GetModuleHandleA(None),
                                                               0)

        if self.mouse_is_hook:
            def mouse_low_level_handler(code, event_code, kb_data_ptr):
                """Execute when mouse low level event was catched"""
                try:
                    current_key = self.MOUSE_ID_TO_KEY[event_code]
                    if current_key != 'Move':
                        event_type = self.MOUSE_ID_TO_EVENT_TYPE[event_code]
                        event = MouseEvent(current_key, event_type)

                        if self.handler != 0:
                            self.handler(event)

                finally:
                    return windll.user32.CallNextHookEx(self.mouse_id, code, event_code, kb_data_ptr)

            mouse_pointer = _callback_pointer(mouse_low_level_handler)
            self.mouse_id = windll.user32.SetWindowsHookExA(self.WH_MOUSE_LL, mouse_pointer,
                                                            windll.kernel32.GetModuleHandleA(None), 0)

        self.listen()

    def unhook_mouse(self):
        """Unhook mouse events"""
        self.mouse_is_hook = False
        windll.user32.UnhookWindowsHookEx(self.mouse_id)

    def unhook_keyboard(self):
        """Unhook keyboard events"""
        self.keyboard_is_hook = False
        windll.user32.UnhookWindowsHookEx(self.keyboard_id)

    def listen(self):
        """Listen events"""
        atexit.register(windll.user32.UnhookWindowsHookEx, self.keyboard_id)
        atexit.register(windll.user32.UnhookWindowsHookEx, self.mouse_id)

        message_pointer = MSG()

        while self.mouse_is_hook or self.keyboard_is_hook:
            msg = windll.user32.GetMessageW(message_pointer, 0, 0, 0)
            windll.user32.TranslateMessage(byref(message_pointer))
            windll.user32.DispatchMessageW(byref(message_pointer))
            if message_pointer.message == self.WM_QUIT:
                exit(0)


if __name__ == "__main__":

    def on_event(args):
        """Callback for keyboard and mouse events"""
        if isinstance(args, KeyboardEvent):
            if args.current_key == 'A' and args.event_type == 'key down' and 'Lcontrol' in args.pressed_key:
                print("Ctrl + A was pressed")

            if args.current_key == 'K' and args.event_type == 'key down':
                print("K was pressed")

            if args.current_key == 'M' and args.event_type == 'key down' and 'U' in args.pressed_key:
                hk.unhook_mouse()
                print("Unhook mouse")

            if args.current_key == 'K' and args.event_type == 'key down' and 'U' in args.pressed_key:
                hk.unhook_keyboard()
                print("Unhook keyboard")

        if isinstance(args, MouseEvent):
            if args.current_key == 'RButton' and args.event_type == 'key down':
                print("Right button pressed")

            if args.current_key == 'WheelButton' and args.event_type == 'key down':
                print("Wheel button pressed")


    hk = Hook()
    hk.handler = on_event
    hk.hook(keyboard=True, mouse=True)
