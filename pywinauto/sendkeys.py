# -*- coding: utf-8 -*-
"""
Check that SendInput can work the way we want it to

"""
import time
import ctypes

__all__ = ['KeySequenceError', 'SendKeys']

MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
SendInput = ctypes.windll.user32.SendInput

DWORD = ctypes.c_ulong
LONG = ctypes.c_long
WORD = ctypes.c_ushort

# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4283
class MOUSEINPUT(ctypes.Structure):
    "Needed for complete definition of INPUT structure - not used"
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4283
        ('dx', LONG),
        ('dy', LONG),
        ('mouseData', DWORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', DWORD),
    ]
assert ctypes.sizeof(MOUSEINPUT) == 24, ctypes.sizeof(MOUSEINPUT)
assert ctypes.alignment(MOUSEINPUT) == 2, ctypes.alignment(MOUSEINPUT)

# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4292
class KEYBDINPUT(ctypes.Structure):
    "A particular keyboard event"
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4292
        ('wVk', WORD),
        ('wScan', WORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', DWORD),
    ]
assert ctypes.sizeof(KEYBDINPUT) == 16, ctypes.sizeof(KEYBDINPUT)
assert ctypes.alignment(KEYBDINPUT) == 2, ctypes.alignment(KEYBDINPUT)


class HARDWAREINPUT(ctypes.Structure):
    "Needed for complete definition of INPUT structure - not used"
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4300
        ('uMsg', DWORD),
        ('wParamL', WORD),
        ('wParamH', WORD),
    ]
assert ctypes.sizeof(HARDWAREINPUT) == 8, ctypes.sizeof(HARDWAREINPUT)
assert ctypes.alignment(HARDWAREINPUT) == 2, ctypes.alignment(HARDWAREINPUT)


# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4314
class UNION_INPUT_STRUCTS(ctypes.Union):
    "The C Union type representing a single Event of any type"
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4314
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT),
    ]
assert ctypes.sizeof(UNION_INPUT_STRUCTS) == 24, \
    ctypes.sizeof(UNION_INPUT_STRUCTS)
assert ctypes.alignment(UNION_INPUT_STRUCTS) == 2, \
    ctypes.alignment(UNION_INPUT_STRUCTS)

# C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4310
class INPUT(ctypes.Structure):
    "See: http://msdn.microsoft.com/en-us/library/ms646270%28VS.85%29.aspx"
    _pack_ = 2
    _fields_ = [
        # C:/PROGRA~1/MICROS~4/VC98/Include/winuser.h 4310
        ('type', DWORD),
        # Unnamed field renamed to '_'
        ('_', UNION_INPUT_STRUCTS),
    ]
assert ctypes.sizeof(INPUT) == 28, ctypes.sizeof(INPUT)
assert ctypes.alignment(INPUT) == 2, ctypes.alignment(INPUT)


INPUT_KEYBOARD  = 1
KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP       = 2
KEYEVENTF_UNICODE     = 4
KEYEVENTF_SCANCODE    = 8
VK_SHIFT        = 16
VK_CONTROL      = 17
VK_MENU         = 18

# 'codes' recognized as {CODE( repeat)?}
CODES = {
    'BACK':         8,
    'BACKSPACE':    8,
    'BACKSPACE':    8,
    'BKSP':         8,
    'BREAK':        3,
    'BS':           8,
    'CAP':          20,
    'CAPSLOCK':     20,
    'DEL':          46,
    'DELETE':       46,
    'DOWN':         40,
    'DOWN':         40,
    'END':          35,
    'ENTER':        13,
    'ESC':          27,
    'F1':           112,
    'F10':          121,
    'F11':          122,
    'F12':          123,
    'F13':          124,
    'F14':          125,
    'F15':          126,
    'F16':          127,
    'F17':          128,
    'F18':          129,
    'F19':          130,
    'F2':           113,
    'F20':          131,
    'F21':          132,
    'F22':          133,
    'F23':          134,
    'F24':          135,
    'F3':           114,
    'F4':           115,
    'F5':           116,
    'F6':           117,
    'F7':           118,
    'F8':           119,
    'F9':           120,
    'HELP':         47,
    'HOME':         36,
    'INS':          45,
    'INSERT':       45,
    'LEFT':         37,
    'LWIN':         91,
    'NUMLOCK':      144,
    'PGDN':         34,
    'PGUP':         33,
    'PRTSC':        44,
    'RIGHT':        39,
    'RMENU':        165,
    'RWIN':         92,
    'SCROLLLOCK':   145,
    'SPACE':        32,
    'TAB':          9,
    'UP':           38,

    'VK_ACCEPT':      30,
    'VK_ADD':      107,
    'VK_APPS':      93,
    'VK_ATTN':      246,
    'VK_BACK':      8,
    'VK_CANCEL':      3,
    'VK_CAPITAL':      20,
    'VK_CLEAR':      12,
    'VK_CONTROL':      17,
    'VK_CONVERT':      28,
    'VK_CRSEL':      247,
    'VK_DECIMAL':      110,
    'VK_DELETE':      46,
    'VK_DIVIDE':      111,
    'VK_DOWN':      40,
    'VK_END':      35,
    'VK_EREOF':      249,
    'VK_ESCAPE':      27,
    'VK_EXECUTE':      43,
    'VK_EXSEL':      248,
    'VK_F1':      112,
    'VK_F10':      121,
    'VK_F11':      122,
    'VK_F12':      123,
    'VK_F13':      124,
    'VK_F14':      125,
    'VK_F15':      126,
    'VK_F16':      127,
    'VK_F17':      128,
    'VK_F18':      129,
    'VK_F19':      130,
    'VK_F2':      113,
    'VK_F20':      131,
    'VK_F21':      132,
    'VK_F22':      133,
    'VK_F23':      134,
    'VK_F24':      135,
    'VK_F3':      114,
    'VK_F4':      115,
    'VK_F5':      116,
    'VK_F6':      117,
    'VK_F7':      118,
    'VK_F8':      119,
    'VK_F9':      120,
    'VK_FINAL':      24,
    'VK_HANGEUL':      21,
    'VK_HANGUL':      21,
    'VK_HANJA':      25,
    'VK_HELP':      47,
    'VK_HOME':      36,
    'VK_INSERT':      45,
    'VK_JUNJA':      23,
    'VK_KANA':      21,
    'VK_KANJI':      25,
    'VK_LBUTTON':      1,
    'VK_LCONTROL':      162,
    'VK_LEFT':      37,
    'VK_LMENU':      164,
    'VK_LSHIFT':      160,
    'VK_LWIN':      91,
    'VK_MBUTTON':      4,
    'VK_MENU':      18,
    'VK_MODECHANGE':      31,
    'VK_MULTIPLY':      106,
    'VK_NEXT':      34,
    'VK_NONAME':      252,
    'VK_NONCONVERT':      29,
    'VK_NUMLOCK':      144,
    'VK_NUMPAD0':      96,
    'VK_NUMPAD1':      97,
    'VK_NUMPAD2':      98,
    'VK_NUMPAD3':      99,
    'VK_NUMPAD4':      100,
    'VK_NUMPAD5':      101,
    'VK_NUMPAD6':      102,
    'VK_NUMPAD7':      103,
    'VK_NUMPAD8':      104,
    'VK_NUMPAD9':      105,
    'VK_OEM_CLEAR':      254,
    'VK_PA1':      253,
    'VK_PAUSE':      19,
    'VK_PLAY':      250,
    'VK_PRINT':      42,
    'VK_PRIOR':      33,
    'VK_PROCESSKEY':      229,
    'VK_RBUTTON':      2,
    'VK_RCONTROL':      163,
    'VK_RETURN':      13,
    'VK_RIGHT':      39,
    'VK_RMENU':      165,
    'VK_RSHIFT':      161,
    'VK_RWIN':      92,
    'VK_SCROLL':    145,
    'VK_SELECT':    41,
    'VK_SEPARATOR': 108,
    'VK_SHIFT':     16,
    'VK_SNAPSHOT':  44,
    'VK_SPACE':     32,
    'VK_SUBTRACT':  109,
    'VK_TAB':       9,
    'VK_UP':        38,
    'ZOOM':         251,
}

# modifier keys
MODIFIERS = {
    '+': VK_SHIFT,
    '^': VK_CONTROL,
    '%': VK_MENU,
}


class KeySequenceError(Exception):
    """Exception raised when a key sequence string has a syntax error"""
    def __str__(self):
        return ' '.join(self.args)


class KeyDown(object):
    "class representing a key press"
    def __init__(self, key):
        self.key = key
        self.keydown = True
        self.keyup = False
    def __str__(self):
        return "<KD %s>"% self.key
    __repr__ = __str__


class KeyUp(object):
    "class representing a key release"
    def __init__(self, key):
        self.key = key
        self.keydown = False
        self.keyup = True
    def __str__(self):
        return "<KU %s>"% self.key
    __repr__ = __str__


class KeyPress(object):
    "class representing a key press and release"
    def __init__(self, key):
        self.key = key
        self.keydown = True
        self.keyup = True
    def __str__(self):
        return "<KT %s>"% self.key
    __repr__ = __str__


def parse_keys(string, 
                with_spaces = False, 
                with_tabs = False, 
                with_newlines = False):
    "Return the parsed keys"    
    
    keys = []
    modifiers = []
    index = 0
    while index < len(string):
        
        c = string[index]
        index += 1
        
        if c in MODIFIERS.keys():
            modifier = MODIFIERS[c]
            # remember that we are currently modified
            modifiers.append(modifier)
            # hold down the modifier key
            keys.append(KeyDown(modifier))
            continue
            
        elif c == "(":
            # find the end of the bracketed text
            end_pos = string.find(")", index)
            if end_pos == -1:
                raise KeySequenceError ('`)` not found')
            keys.extend(parse_keys(string[index:end_pos]))
            index = end_pos + 1
            
        elif c == "{":
            end_pos = string.find("}", index)
            if end_pos == -1:
                raise KeySequenceError ('`}` not found')
            
            code = string[index:end_pos]
            index = end_pos + 1
            
            # it is a known code
            if code in CODES:
                keys.append(KeyPress(CODES[code]))
            
            # it is an escaped modifier
            elif len(code) == 1:
                keys.append(code)
            
            # it is a repetition
            elif ' ' in code:
                to_repeat, count = code.rsplit(None, 1)
                try:
                    count = int(count)
                except ValueError:
                    raise KeySequenceError (
                        'invalid repetition count %s'% count)
                
                to_repeat = parse_keys(to_repeat)
                keys.extend(to_repeat * count)
        
        elif c == ')':
            raise KeySequenceError('`)` should be preceeded by `(`')

        # unexpected "}"
        elif c == '}':
            raise KeySequenceError('`}` should be preceeded by `{`')

        # handling a single character
        else:
            if (c == ' ' and not with_spaces or
                c == '\t' and not with_tabs or
                c == '\n' and not with_newlines):
                continue        
            
            if c in ('~'):
                keys.append("\n")
            else:
                keys.append(c)
            
        # as we have handled the text - release the modifiers
        while modifiers:
            keys.append(KeyUp(modifiers.pop()))


    # just in case there were any modifiers left pressed - release them
    while modifiers:
        keys.append(KeyUp(modifiers.pop()))
    
    return keys


def SendKey(char, keyup = True, keydown = True):
    "Parse the charcter and send it"
    
    key = INPUT()
    key.type = INPUT_KEYBOARD

    # get the scan code for the character, and set up the 
    # other variables
    if isinstance(char, basestring):
        key._.ki.wScan = ord(unicode(char)) # VkKeyScanW((char))
        key._.ki.dwFlags = KEYEVENTF_UNICODE
        key._.ki.wVk = 0
    else:
        # It must have been a virtual key already
        # so set up the parameters for this

        key._.ki.wVk = char.key
        key._.ki.wScan = MapVirtualKey(char.key, 0)
        key._.ki.dwFlags = 0
        
        keyup = char.keyup
        keydown = char.keydown

    actions = 1
    if keydown and keyup:
        key_down = key
        key = (INPUT * 2)()
        key[0] = key_down
        key[1]._.ki.dwFlags |= KEYEVENTF_KEYUP
        actions = 2
    elif keyup:
        key._.ki.dwFlags |= KEYEVENTF_KEYUP

    # Now type both of those keys
    return SendInput(
        actions, 
        ctypes.pointer(key), 
        ctypes.sizeof(INPUT))


def SendKeys(keys, 
             pause=0.05, 
             with_spaces=False, 
             with_tabs=False, 
             with_newlines=False,
             turn_off_numlock=True):
    ""
    keys = parse_keys(keys, with_spaces, with_tabs, with_newlines)
    
    for k in keys:
        SendKey(k)
        time.sleep(pause)


def main():
    "Send some test strings"
    test_strings = [
        "some{ }text",
        "some{{}text",
        "some{+}text",
        "so%me{ab 4}text",
        "some +(asdf)text",
        "some %^+(asdf)text",
        "some %^+a text+",
        "some %^+a tex+{&}",
        "some %^+a tex+(dsf)",
        "",
        ]
    
    for s in test_strings:
        print repr(s)
        keys = parse_keys(s)
        print keys
        
        for k in keys:
            SendKey(k)
        print 
    
if __name__ == "__main__":
    main()

