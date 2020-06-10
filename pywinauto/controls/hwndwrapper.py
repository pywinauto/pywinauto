# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Basic wrapping of Windows controls"""
from __future__ import unicode_literals
from __future__ import print_function

# pylint:  disable-msg=W0611

# import sys
import copy
import time
import re
import ctypes
import win32api
import win32gui
import win32con
import win32process
import win32event
import six
import pywintypes
import warnings

# the wrappers may be used in an environment that does not need
# the actions - as such I don't want to require sendkeys - so
# the following makes the import optional.

from .. import win32functions
from .. import win32defines
from .. import win32structures
from .. import controlproperties
from ..actionlogger import ActionLogger
from .. import keyboard
from .. import mouse
from ..timings import Timings
from .. import timings
from .. import handleprops
from ..win32_element_info import HwndElementInfo
from .. import backend

# I leave this optional because PIL is a large dependency
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

# also import MenuItemNotEnabled so that it is
# accessible from HwndWrapper module
from .menuwrapper import Menu #, MenuItemNotEnabled

from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta
from .. import deprecated


#====================================================================
class ControlNotEnabled(RuntimeError):

    """Raised when a control is not enabled"""
    pass

#====================================================================
class ControlNotVisible(RuntimeError):

    """Raised when a control is not visible"""
    pass

#====================================================================
class InvalidWindowHandle(RuntimeError):

    """Raised when an invalid handle is passed to HwndWrapper"""

    def __init__(self, hwnd):
        """Initialise the RuntimError parent with the mesage"""
        RuntimeError.__init__(self,
            "Handle {0} is not a vaild window handle".format(hwnd))

#=========================================================================
class HwndMeta(BaseMeta):

    """Metaclass for HwndWrapper objects"""
    re_wrappers = {}
    str_wrappers = {}

    def __init__(cls, name, bases, attrs):
        """
        Register the class names

        Both the regular expression or the classes directly are registered.
        """
        BaseMeta.__init__(cls, name, bases, attrs)

        for win_class in cls.windowclasses:
            HwndMeta.re_wrappers[re.compile(win_class)] = cls
            HwndMeta.str_wrappers[win_class] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this native element"""
        if isinstance(element, six.integer_types):
            element = HwndElementInfo(element)
        class_name = element.class_name

        try:
            return HwndMeta.str_wrappers[class_name]
        except KeyError:
            wrapper_match = None

            for regex, wrapper in HwndMeta.re_wrappers.items():
                if regex.match(class_name):
                    wrapper_match = wrapper
                    HwndMeta.str_wrappers[class_name] = wrapper

                    return wrapper

        # if it is a dialog then override the wrapper we found
        # and make it a DialogWrapper
        if handleprops.is_toplevel_window(element.handle):
            wrapper_match = DialogWrapper

        if wrapper_match is None:
            wrapper_match = HwndWrapper
        return wrapper_match

#====================================================================
@six.add_metaclass(HwndMeta)
class HwndWrapper(BaseWrapper):

    """
    Default wrapper for controls.

    All other wrappers are derived from this.

    This class wraps a lot of functionality of underlying windows API
    features for working with windows.

    Most of the methods apply to every single window type. For example
    you can click() on any window.

    Most of the methods of this class are simple wrappers around
    API calls and as such they try do the simplest thing possible.

    An HwndWrapper object can be passed directly to a ctypes wrapped
    C function - and it will get converted to a Long with the value of
    it's handle (see ctypes, _as_parameter_).
    """
    handle = None

    # -----------------------------------------------------------
    def __new__(cls, element):
        """Construct the control wrapper"""
        return super(HwndWrapper, cls)._create_wrapper(cls, element, HwndWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid HwndElementInfo or it can be an
          instance or subclass of HwndWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        if isinstance(element_info, six.integer_types):
            element_info = HwndElementInfo(element_info)
        if hasattr(element_info, "element_info"):
            element_info = element_info.element_info

        BaseWrapper.__init__(self, element_info, backend.registry.backends['win32'])

        # verify that we have been passed in a valid windows handle
        if not handleprops.iswindow(self.handle):
            raise InvalidWindowHandle(self.handle)

        # make it so that ctypes conversion happens correctly
        self._as_parameter_ = self.handle

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(HwndWrapper, self).writable_props
        props.extend(['style',
                      'exstyle',
                      'user_data',
                      'context_help_id',
                      'fonts',
                      'client_rects',
                      'is_unicode',
                      'menu_items',
                      'automation_id',
                      ])
        return props

    # -----------------------------------------------------------
    def style(self):
        """
        Returns the style of window

        Return value is a long.

        Combination of WS_* and specific control specific styles.
        See HwndWrapper.has_style() to easily check if the window has a
        particular style.
        """
        return handleprops.style(self)
    # Non PEP-8 alias
    Style = deprecated(style)

    # -----------------------------------------------------------
    def exstyle(self):
        """
        Returns the Extended style of window

        Return value is a long.

        Combination of WS_* and specific control specific styles.
        See HwndWrapper.has_style() to easily check if the window has a
        particular style.
        """
        return handleprops.exstyle(self)
    # Non PEP-8 alias
    ExStyle = deprecated(exstyle, deprecated_name='ExStyle')

    #------------------------------------------------------------
    def automation_id(self):
        """Return the .NET name of the control"""
        return self.element_info.automation_id

    #------------------------------------------------------------
    def control_type(self):
        """Return the .NET type of the control"""
        return self.element_info.control_type

    #------------------------------------------------------------
    def full_control_type(self):
        """Return the .NET type of the control (full, uncut)"""
        return self.element_info.full_control_type

    # -----------------------------------------------------------
    def user_data(self):
        """
        Extra data associted with the window

        This value is a long value that has been associated with the window
        and rarely has useful data (or at least data that you know the use
        of).
        """
        return handleprops.userdata(self)
    # Non PEP-8 alias
    UserData = deprecated(user_data)

    # -----------------------------------------------------------
    def context_help_id(self):
        """Return the Context Help ID of the window"""
        return handleprops.contexthelpid(self)
    # Non PEP-8 alias
    ContextHelpID = deprecated(context_help_id, deprecated_name='ContextHelpID')

    # -----------------------------------------------------------
    def is_active(self):
        """Whether the window is active or not"""
        return self.top_level_parent() == self.get_active()
    # Non PEP-8 alias
    IsActive = deprecated(is_active)

    # -----------------------------------------------------------
    def is_unicode(self):
        """
        Whether the window is unicode or not

        A window is Unicode if it was registered by the Wide char version
        of RegisterClass(Ex).
        """
        return handleprops.isunicode(self)
    # Non PEP-8 alias
    IsUnicode = deprecated(is_unicode)

    # -----------------------------------------------------------
    def client_rect(self):
        """
        Returns the client rectangle of window

        The client rectangle is the window rectangle minus any borders that
        are not available to the control for drawing.

        Both top and left are always 0 for this method.

        This method returns a RECT structure, Which has attributes - top,
        left, right, bottom. and has methods width() and height().
        See win32structures.RECT for more information.
        """
        return handleprops.clientrect(self)
    # Non PEP-8 alias
    ClientRect = deprecated(client_rect)

    # -----------------------------------------------------------
    #def client_to_screen(self, client_point):
    #    """Maps point from client to screen coordinates"""
    #    point = win32structures.POINT()
    #    if isinstance(client_point, win32structures.POINT):
    #        point.x = client_point.x
    #        point.y = client_point.y
    #    else:
    #        point.x = client_point[0]
    #        point.y = client_point[1]
    #    win32functions.client_to_screen(self, ctypes.byref(point))
    #
    #    # return tuple in any case because
    #    # coords param is always expected to be tuple
    #    return point.x, point.y

    # -----------------------------------------------------------
    def font(self):
        """
        Return the font of the window

        The font of the window is used to draw the text of that window.
        It is a structure which has attributes for font name, height, width
        etc.

        See win32structures.LOGFONTW for more information.
        """
        return handleprops.font(self)
    # Non PEP-8 alias
    Font = deprecated(font)

    # -----------------------------------------------------------
    def has_style(self, style):
        """Return True if the control has the specified style"""
        return handleprops.has_style(self, style)
    # Non PEP-8 alias
    HasStyle = deprecated(has_style)

    # -----------------------------------------------------------
    def has_exstyle(self, exstyle):
        """Return True if the control has the specified extended style"""
        return handleprops.has_exstyle(self, exstyle)
    # Non PEP-8 alias
    HasExStyle = deprecated(has_exstyle, deprecated_name='HasExStyle')

    # -----------------------------------------------------------
    def is_dialog(self):
        """Return true if the control is a top level window"""
        if not ("isdialog" in self._cache.keys()):
            self._cache['isdialog'] = handleprops.is_toplevel_window(self)

        return self._cache['isdialog']

    # -----------------------------------------------------------
    def client_rects(self):
        """
        Return the client rect for each item in this control

        It is a list of rectangles for the control. It is frequently over-ridden
        to extract all rectangles from a control with multiple items.

        It is always a list with one or more rectangles:

          * First elemtent is the client rectangle of the control
          * Subsequent elements contain the client rectangle of any items of
            the control (e.g. items in a listbox/combobox, tabs in a
            tabcontrol)
        """
        return [self.client_rect(), ]
    # Non PEP-8 alias
    ClientRects = deprecated(client_rects)

    # -----------------------------------------------------------
    def fonts(self):
        """
        Return the font for each item in this control

        It is a list of fonts for the control. It is frequently over-ridden
        to extract all fonts from a control with multiple items.

        It is always a list with one or more fonts:

          * First elemtent is the control font
          * Subsequent elements contain the font of any items of
            the control (e.g. items in a listbox/combobox, tabs in a
            tabcontrol)
        """
        return [self.font(), ]
    # Non PEP-8 alias
    Fonts = deprecated(fonts)

    # -----------------------------------------------------------
    def send_command(self, commandID):
        return self.send_message(win32defines.WM_COMMAND, commandID)
    # Non PEP-8 alias
    SendCommand = deprecated(send_command)

    # -----------------------------------------------------------
    def post_command(self, commandID):
        return self.post_message(win32defines.WM_COMMAND, commandID)
    # Non PEP-8 alias
    PostCommand = deprecated(post_command)

    # -----------------------------------------------------------
    #def notify(self, code):
    #    "Send a notification to the parent (not tested yet)"

    #    # now we need to notify the parent that the state has changed
    #    nmhdr = win32structures.NMHDR()
    #    nmhdr.hwndFrom = self.handle
    #    nmhdr.idFrom = self.control_id()
    #    nmhdr.code = code

    #    from ..remote_memory_block import RemoteMemoryBlock
    #    remote_mem = RemoteMemoryBlock(self, size=ctypes.sizeof(nmhdr))
    #    remote_mem.Write(nmhdr, size=ctypes.sizeof(nmhdr))

    #    retval = self.parent().send_message(
    #        win32defines.WM_NOTIFY,
    #        self.handle,
    #        remote_mem)
    #    #if retval != win32defines.TRUE:
    #    #    print('retval = ' + str(retval))
    #    #    raise ctypes.WinError()
    #    del remote_mem

    #    return retval
    # Non PEP-8 alias
    #Notify = deprecated(notify)

    # -----------------------------------------------------------
    def _ensure_enough_privileges(self, message_name):
        """Ensure the Python process has enough rights to send some window messages"""
        pid = handleprops.processid(self.handle)
        if not handleprops.has_enough_privileges(pid):
            raise RuntimeError('Not enough rights to use {} message/function for target process ' \
                '(to resolve it run the script as Administrator)'.format(message_name))

    # -----------------------------------------------------------
    def send_message(self, message, wparam = 0, lparam = 0):
        """Send a message to the control and wait for it to return"""
        wParamAddress = wparam
        if hasattr(wparam, 'mem_address'):
            wParamAddress = wparam.mem_address
        lParamAddress = lparam
        if hasattr(lparam, 'mem_address'):
            lParamAddress = lparam.mem_address

        CArgObject = type(ctypes.byref(ctypes.c_int(0)))
        if isinstance(wparam, CArgObject):
            wParamAddress = ctypes.addressof(wparam._obj)
        if isinstance(lparam, CArgObject):
            lParamAddress = ctypes.addressof(lparam._obj)

        return win32gui.SendMessage(self.handle, message, wParamAddress, lParamAddress)

    # Non PEP-8 alias
    SendMessage = deprecated(send_message)

    # -----------------------------------------------------------
    def send_chars(self,
                   chars,
                   with_spaces=True,
                   with_tabs=True,
                   with_newlines=True):
        """
        Silently send a character string to the control in an inactive window

        If a virtual key with no corresponding character is encountered
        (e.g. VK_LEFT, VK_DELETE), a KeySequenceError is raised. Consider using
        the method send_keystrokes for such input.
        """
        input_locale_id = win32functions.GetKeyboardLayout(0)
        keys = keyboard.parse_keys(chars, with_spaces, with_tabs, with_newlines)

        for key in keys:
            key_info = key.get_key_info()
            flags = key_info[2]

            unicode_char = (
                flags & keyboard.KEYEVENTF_UNICODE ==
                keyboard.KEYEVENTF_UNICODE)

            if unicode_char:
                _, char = key_info[:2]
                vk = win32functions.VkKeyScanExW(chr(char), input_locale_id) & 0xFF
                scan = win32functions.MapVirtualKeyW(vk, 0)
            else:
                vk, scan = key_info[:2]
                char = win32functions.MapVirtualKeyW(vk, 2)

            if char > 0:
                lparam = 1 << 0 | scan << 16 | (flags & 1) << 24
                win32api.SendMessage(self.handle, win32con.WM_CHAR, char, lparam)
            else:
                raise keyboard.KeySequenceError(
                    'no WM_CHAR code for {key}, use method send_keystrokes instead'.
                    format(key=key))

    # -----------------------------------------------------------
    def send_keystrokes(self,
                   keystrokes,
                   with_spaces=True,
                   with_tabs=True,
                   with_newlines=True):
        """
        Silently send keystrokes to the control in an inactive window

        It parses modifiers Shift(+), Control(^), Menu(%) and Sequences like "{TAB}", "{ENTER}"
        For more information about Sequences and Modifiers navigate to module `keyboard`_

        .. _`keyboard`: pywinauto.keyboard.html

        Due to the fact that each application handles input differently and this method
        is meant to be used on inactive windows, it may work only partially depending
        on the target app. If the window being inactive is not essential, use the robust
        `type_keys`_ method.

        .. _`type_keys`: pywinauto.base_wrapper.html#pywinauto.base_wrapper.BaseWrapper.type_keys
        """
        PBYTE256 = ctypes.c_ubyte * 256

        win32gui.SendMessage(self.handle, win32con.WM_ACTIVATE,
                             win32con.WA_ACTIVE, 0)
        target_thread_id = win32functions.GetWindowThreadProcessId(self.handle, None)
        current_thread_id = win32functions.GetCurrentThreadId()
        attach_success = win32functions.AttachThreadInput(target_thread_id, current_thread_id, True) != 0
        if not attach_success:
            warnings.warn('Failed to attach app\'s thread to the current thread\'s message queue',
                          UserWarning, stacklevel=2)

        keyboard_state_stack = [PBYTE256()]
        win32functions.GetKeyboardState(keyboard_state_stack[-1])

        input_locale_id = win32functions.GetKeyboardLayout(0)
        context_code = 0

        keys = keyboard.parse_keys(keystrokes, with_spaces, with_tabs, with_newlines)
        key_combos_present = any([isinstance(k, keyboard.EscapedKeyAction) for k in keys])
        if key_combos_present:
            warnings.warn('Key combinations may or may not work depending on the target app',
                          UserWarning, stacklevel=2)

        try:
            for key in keys:
                vk, scan, flags = key.get_key_info()

                if vk == keyboard.VK_MENU or context_code == 1:
                    down_msg, up_msg = win32con.WM_SYSKEYDOWN, win32con.WM_SYSKEYUP
                else:
                    down_msg, up_msg = win32con.WM_KEYDOWN, win32con.WM_KEYUP

                repeat = 1
                shift_state = 0
                unicode_codepoint = flags & keyboard.KEYEVENTF_UNICODE != 0
                if unicode_codepoint:
                    char = chr(scan)
                    vk_with_flags = win32functions.VkKeyScanExW(char, input_locale_id)
                    vk = vk_with_flags & 0xFF
                    shift_state = (vk_with_flags & 0xFF00) >> 8
                    scan = win32functions.MapVirtualKeyW(vk, 0)

                if key.down and vk > 0:
                    new_keyboard_state = copy.deepcopy(keyboard_state_stack[-1])

                    new_keyboard_state[vk] |= 128
                    if shift_state & 1 == 1:
                        new_keyboard_state[keyboard.VK_SHIFT] |= 128
                    # NOTE: if there are characters with CTRL or ALT in the shift
                    # state, make sure to add these keys to new_keyboard_state

                    keyboard_state_stack.append(new_keyboard_state)

                    lparam = (
                        repeat << 0 |
                        scan << 16 |
                        (flags & 1) << 24 |
                        context_code << 29 |
                        0 << 31)

                    win32functions.SetKeyboardState(keyboard_state_stack[-1])
                    win32functions.PostMessage(self.handle, down_msg, vk, lparam)
                    if vk == keyboard.VK_MENU:
                        context_code = 1

                    # a delay for keyboard state to take effect
                    time.sleep(0.01)

                if key.up and vk > 0:
                    keyboard_state_stack.pop()

                    lparam = (
                        repeat << 0 |
                        scan << 16 |
                        (flags & 1) << 24 |
                        context_code << 29 |
                        1 << 30 |
                        1 << 31)

                    win32functions.PostMessage(self.handle, up_msg, vk, lparam)
                    win32functions.SetKeyboardState(keyboard_state_stack[-1])

                    if vk == keyboard.VK_MENU:
                        context_code = 0

                    # a delay for keyboard state to take effect
                    time.sleep(0.01)

        except pywintypes.error as e:
            if e.winerror == 1400:
                warnings.warn('Application exited before the end of keystrokes',
                              UserWarning, stacklevel=2)
            else:
                warnings.warn(e.strerror, UserWarning, stacklevel=2)
            win32functions.SetKeyboardState(keyboard_state_stack[0])

        if attach_success:
            win32functions.AttachThreadInput(target_thread_id, current_thread_id, False)

    # -----------------------------------------------------------
    def send_message_timeout(
        self,
        message,
        wparam = 0,
        lparam = 0,
        timeout = None,
        timeoutflags = win32defines.SMTO_NORMAL):
        """
        Send a message to the control and wait for it to return or to timeout

        If no timeout is given then a default timeout of .01 of a second will
        be used.
        """
        if timeout is None:
            timeout = Timings.sendmessagetimeout_timeout

        result = -1
        try:
            (_, result) = win32gui.SendMessageTimeout(
                    int(self.handle),
                    message,
                    wparam,
                    lparam,
                    timeoutflags,
                    int(timeout * 1000)
                    )
        except Exception as exc:
            #import traceback
            #print('____________________________________________________________')
            #print('self.handle =', int(self.handle), ', message =', message,
            #      ', wparam =', wparam, ', lparam =', lparam, ', timeout =', timeout)
            #print('Exception: ', exc)
            #print(traceback.format_exc())
            result = str(exc)

        return result #result.value
    # Non PEP-8 alias
    SendMessageTimeout = deprecated(send_message_timeout)

    # -----------------------------------------------------------
    def post_message(self, message, wparam = 0, lparam = 0):
        """Post a message to the control message queue and return"""
        return win32functions.PostMessage(self, message, wparam, lparam)

    # Non PEP-8 alias
    PostMessage = deprecated(post_message)

#    # -----------------------------------------------------------
#    def notify_menu_select(self, menu_id):
#        """Notify the dialog that one of it's menu items was selected
#
#        **This method is Deprecated**
#        """
#
#        import warnings
#        warning_msg = "HwndWrapper.NotifyMenuSelect() is deprecated - " \
#            "equivalent functionality is being moved to the MenuWrapper class."
#        warnings.warn(warning_msg, DeprecationWarning)
#
#        self.set_focus()
#
#        msg = win32defines.WM_COMMAND
#        return self.send_message_timeout(
#            msg,
#            win32functions.MakeLong(0, menu_id), #wparam
#            )
    # Non PEP-8 alias
    # NotifyMenuSelect = deprecated(notify_menu_select)

    # -----------------------------------------------------------
    def notify_parent(self, message, controlID = None):
        """Send the notification message to parent of this control"""
        if controlID is None:
            controlID = self.control_id()

        return self.parent().post_message(
            win32defines.WM_COMMAND,
            win32functions.MakeLong(message, controlID),
            self)
    # Non PEP-8 alias
    NotifyParent = deprecated(notify_parent)

    # -----------------------------------------------------------
    def __hash__(self):
        """Returns the hash value of the handle"""
        return hash(self.handle)

    #-----------------------------------------------------------
    def wait_for_idle(self):
        """Backend specific function to wait for idle state of a thread or a window"""
        win32functions.WaitGuiThreadIdle(self.handle)

    # -----------------------------------------------------------
    def click(self, button="left", pressed="", coords=(0, 0),
              double=False, absolute=False):
        """
        Simulates a mouse click on the control

        This method sends WM_* messages to the control, to do a more
        'realistic' mouse click use click_input() which uses mouse_event() API
        to perform the click.

        This method does not require that the control be visible on the screen
        (i.e. it can be hidden beneath another window and it will still work).
        """
        self.verify_actionable()
        self._ensure_enough_privileges('WM_*BUTTONDOWN/UP')

        _perform_click(self, button, pressed, coords, double, absolute=absolute)
        return self
    # Non PEP-8 alias
    Click = deprecated(click)

    # -----------------------------------------------------------
    def close_click(
        self, button = "left", pressed = "", coords = (0, 0), double = False):
        """
        Perform a click action that should make the window go away

        The only difference from click is that there are extra delays
        before and after the click action.
        """
        time.sleep(Timings.before_closeclick_wait)

        _perform_click(self, button, pressed, coords, double)

        def has_closed():
            closed = not (
                    handleprops.iswindow(self) or
                    handleprops.iswindow(self.parent()))
            if not closed:
                # try closing again
                try:
                    _perform_click(self, button, pressed, coords, double)
                except Exception:
                    return True # already closed
            return closed

        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        timings.wait_until(
            Timings.closeclick_dialog_close_wait,
            Timings.closeclick_retry,
            has_closed
        )

        time.sleep(Timings.after_closeclick_wait)

        return self
    # Non PEP-8 alias
    CloseClick = deprecated(close_click)

    # -----------------------------------------------------------
    def close_alt_f4(self):
        """Close the window by pressing Alt+F4 keys."""
        time.sleep(Timings.before_closeclick_wait)
        self.type_keys('%{F4}')
        time.sleep(Timings.after_closeclick_wait)

        return self
    # Non PEP-8 alias
    CloseAltF4 = deprecated(close_alt_f4)

    # -----------------------------------------------------------
    def double_click(
        self, button = "left", pressed = "", coords = (0, 0)):
        """Perform a double click action"""
        _perform_click(self, button, pressed, coords, double = True)
        return self
    # Non PEP-8 alias
    DoubleClick = deprecated(double_click)

    # -----------------------------------------------------------
    def right_click(
        self, pressed = "", coords = (0, 0)):
        """Perform a right click action"""
        _perform_click(
            self, "right", "right " + pressed, coords, button_up = False)
        _perform_click(self, "right", pressed, coords, button_down = False)
        return self
    # Non PEP-8 alias
    RightClick = deprecated(right_click)

    # -----------------------------------------------------------
    def press_mouse(self, button ="left", coords = (0, 0), pressed =""):
        """Press the mouse button"""
        #flags, click_point = _calc_flags_and_coords(pressed, coords)

        _perform_click(self, button, pressed, coords, button_down=True, button_up=False)
        return self
    # Non PEP-8 alias
    PressMouse = deprecated(press_mouse)

    # -----------------------------------------------------------
    def release_mouse(self, button ="left", coords = (0, 0), pressed =""):
        """Release the mouse button"""
        #flags, click_point = _calc_flags_and_coords(pressed, coords)
        _perform_click(self, button, pressed, coords, button_down=False, button_up=True)
        return self
    # Non PEP-8 alias
    ReleaseMouse = deprecated(release_mouse)

    # -----------------------------------------------------------
    def move_mouse(self, coords = (0, 0), pressed ="", absolute = False):
        """Move the mouse by WM_MOUSEMOVE"""
        if not absolute:
            self.actions.log('Moving mouse to relative (client) coordinates ' + str(coords).replace('\n', ', '))

        _perform_click(self, button='move', coords=coords, absolute=absolute, pressed=pressed)

        win32functions.WaitGuiThreadIdle(self.handle)
        return self
    # Non PEP-8 alias
    MoveMouse = deprecated(move_mouse)

    # -----------------------------------------------------------
    def drag_mouse(self, button ="left",
                   press_coords = (0, 0),
                   release_coords = (0, 0),
                   pressed = ""):
        """Drag the mouse"""
        if isinstance(press_coords, win32structures.POINT):
            press_coords = (press_coords.x, press_coords.y)

        if isinstance(release_coords, win32structures.POINT):
            release_coords = (release_coords.x, release_coords.y)

        _pressed = pressed
        if not _pressed:
            _pressed = "left"

        self.press_mouse(button, press_coords, pressed=pressed)
        for i in range(5):
            self.move_mouse((press_coords[0] + i, press_coords[1]), pressed=_pressed)
            time.sleep(Timings.drag_n_drop_move_mouse_wait)
        self.move_mouse(release_coords, pressed=_pressed)
        time.sleep(Timings.before_drop_wait)
        self.release_mouse(button, release_coords, pressed=pressed)
        time.sleep(Timings.after_drag_n_drop_wait)
        return self
    # Non PEP-8 alias
    DragMouse = deprecated(drag_mouse)

    # -----------------------------------------------------------
    def set_window_text(self, text, append = False):
        """Set the text of the window"""
        self.verify_actionable()

        if append:
            text = self.window_text() + text

        text = ctypes.c_wchar_p(six.text_type(text))
        self.post_message(win32defines.WM_SETTEXT, 0, text)
        win32functions.WaitGuiThreadIdle(self.handle)

        self.actions.log('Set text to the ' + self.friendly_class_name() + ': ' + str(text))
        return self
    # Non PEP-8 alias
    SetWindowText = deprecated(set_window_text)

    # -----------------------------------------------------------
    def debug_message(self, text):
        """Write some debug text over the window"""
        # don't draw if dialog is not visible

        dc = win32functions.CreateDC("DISPLAY", None, None, None )

        if not dc:
            raise ctypes.WinError()

        rect = self.rectangle()

        #ret = win32functions.TextOut(
        #    dc, rect.left, rect.top, six.text_type(text), len(text))
        ret = win32functions.DrawText(
            dc,
            six.text_type(text),
            len(text),
            ctypes.byref(rect),
            win32defines.DT_SINGLELINE)

        # delete the Display context that we created
        win32functions.DeleteDC(dc)

        if not ret:
            raise ctypes.WinError()

        return self
    # Non PEP-8 alias
    DebugMessage = deprecated(debug_message)

    # -----------------------------------------------------------
    def set_transparency(self, alpha = 120):
        """Set the window transparency from 0 to 255 by alpha attribute"""
        if not (0 <= alpha <= 255):
            raise ValueError('alpha should be in [0, 255] interval!')
        # TODO: implement SetExStyle method
        win32gui.SetWindowLong(self.handle, win32defines.GWL_EXSTYLE, self.exstyle() | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(self.handle, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)
    # Non PEP-8 alias
    SetTransparency = deprecated(set_transparency)

    # -----------------------------------------------------------
    def popup_window(self):
        """Return owned enabled Popup window wrapper if shown.

        If there is no enabled popups at that time, it returns **self**.
        See MSDN reference:
        https://msdn.microsoft.com/en-us/library/windows/desktop/ms633515.aspx

        Please do not use in production code yet - not tested fully
        """
        popup = win32functions.GetWindow(self, win32defines.GW_ENABLEDPOPUP)

        return popup
    # Non PEP-8 alias
    PopupWindow = deprecated(popup_window)

    # -----------------------------------------------------------
    def owner(self):
        """Return the owner window for the window if it exists

        Returns None if there is no owner.
        """
        owner = win32functions.GetWindow(self, win32defines.GW_OWNER)
        if owner:
            return HwndWrapper(owner)
        else:
            return None
    # Non PEP-8 alias
    Owner = deprecated(owner)

    # -----------------------------------------------------------
#    def context_menu_select(self, path, x = None, y = None):
#        "TODO context_menu_select Not Implemented"
#        pass
#        #raise NotImplementedError(
#        #    "HwndWrapper.ContextMenuSelect not implemented yet")
#    # Non PEP-8 alias
#    ContextMenuSelect = deprecated(context_menu_select)

    # -----------------------------------------------------------
    def _menu_handle(self):
        """Simple overridable method to get the menu handle"""
        hMenu = win32gui.GetMenu(self.handle)
        is_main_menu = True
        if not hMenu:
            self._ensure_enough_privileges('MN_GETHMENU')
            hMenu = self.send_message(self.handle, win32defines.MN_GETHMENU);
            is_main_menu = False
        return (hMenu, is_main_menu)

    # -----------------------------------------------------------
    def menu(self):
        """Return the menu of the control"""
        hMenu, is_main_menu = self._menu_handle()
        if hMenu: # and win32functions.IsMenu(menu_hwnd):
            return Menu(self, hMenu, is_main_menu=is_main_menu)
        return None
    # Non PEP-8 alias
    Menu = deprecated(menu)

    # -----------------------------------------------------------
    def menu_item(self, path, exact = False):
        """Return the menu item specified by path

        Path can be a string in the form "MenuItem->MenuItem->MenuItem..."
        where each MenuItem is the text of an item at that level of the menu.
        E.g. ::

          File->Export->ExportAsPNG

        spaces are not important so you could also have written... ::

          File -> Export -> Export As PNG

        """
        if self.appdata is not None:
            menu_appdata = self.appdata['menu_items']
        else:
            menu_appdata = None

        menu = self.menu()
        if menu:
            return self.menu().get_menu_path(path, appdata = menu_appdata, exact=exact)[-1]

        raise RuntimeError("There is no menu.")
    # Non PEP-8 alias
    MenuItem = deprecated(menu_item)

    # -----------------------------------------------------------
    def menu_items(self):
        """Return the menu items for the dialog

        If there are no menu items then return an empty list
        """
        if self.is_dialog() and self.menu():
            #menu_handle = win32functions.GetMenu(self)
            #self.send_message(win32defines.WM_INITMENU, menu_handle)
            return self.menu().get_properties()['menu_items']

            #self.send_message(win32defines.WM_INITMENU, menu_handle)
            #return _GetMenuItems(menu_handle, self)
        else:
            return []
    # Non PEP-8 alias
    MenuItems = deprecated(menu_items)

#    # -----------------------------------------------------------
#    def menu_click(self, path):
#        "Select the MenuItem specifed in path"
#
#        self.verify_actionable()
#
#        self.set_focus()
#
#        menu = Menu(self, self._menu_handle())
#
#        path_items = menu.get_menu_path(path)
#
#        for menu_item in path_items:
#            if not menu_item.is_enabled():
#                raise MenuItemNotEnabled(
#                    "MenuItem '%s' is disabled"% menu_item.text())
#
#            menu_item.click()
#
#        return self
#    # Non PEP-8 alias
#    MenuClick = deprecated(menu_click)

    # -----------------------------------------------------------
    def menu_select(self, path, exact=False, ):
        """Find a menu item specified by the path

        The full path syntax is specified in:
        :py:meth:`.controls.menuwrapper.Menu.get_menu_path`
        """
        self.verify_actionable()

        self.menu_item(path, exact=exact).select()
    # Non PEP-8 alias
    MenuSelect = deprecated(menu_select)

    # -----------------------------------------------------------
    def move_window(
        self,
        x = None,
        y = None,
        width = None,
        height = None,
        repaint = True):
        """Move the window to the new coordinates

        * **x** Specifies the new left position of the window.
          Defaults to the current left position of the window.
        * **y** Specifies the new top position of the window.
          Defaults to the current top position of the window.
        * **width** Specifies the new width of the window. Defaults to the
          current width of the window.
        * **height** Specifies the new height of the window. Default to the
          current height of the window.
        * **repaint** Whether the window should be repainted or not.
          Defaults to True

        """
        cur_rect = self.rectangle()

        # if no X is specified - so use current coordinate
        if x is None:
            x = cur_rect.left
        else:
            try:
                y = x.top
                width = x.width()
                height = x.height()
                x = x.left
            except AttributeError:
                pass

        # if no Y is specified - so use current coordinate
        if y is None:
            y = cur_rect.top

        # if no width is specified - so use current width
        if width is None:
            width = cur_rect.width()

        # if no height is specified - so use current height
        if height is None:
            height = cur_rect.height()

        # ask for the window to be moved
        ret = win32functions.MoveWindow(self, x, y, width, height, repaint)

        # check that it worked correctly
        if not ret:
            raise ctypes.WinError()

        win32functions.WaitGuiThreadIdle(self.handle)
        time.sleep(Timings.after_movewindow_wait)
    # Non PEP-8 alias
    MoveWindow = deprecated(move_window)

    # -----------------------------------------------------------
    def close(self, wait_time = 0):
        """Close the window

        Code modified from http://msdn.microsoft.com/msdnmag/issues/02/08/CQA/

        """
        window_text = self.window_text()

        # tell the window it must close
        self.post_message(win32defines.WM_CLOSE)

        #unused var: start = time.time()
        # Keeps trying while
        #    we have not timed out and
        #    window is still a valid handle and
        #    window is still visible
        # any one of these conditions evaluates to false means the window is
        # closed or we have timed out
        def has_closed():
            return not (handleprops.iswindow(self) and self.is_visible())

        if not wait_time:
            wait_time = Timings.closeclick_dialog_close_wait

        # Keep waiting until both this control and it's parent
        # are no longer valid controls
        timings.wait_until(
            wait_time,
            Timings.closeclick_retry,
            has_closed
        )

        self.actions.log('Closed window "{0}"'.format(window_text))
    # Non PEP-8 alias
    Close = deprecated(close)

    # -----------------------------------------------------------
    def maximize(self):
        """Maximize the window"""
        win32functions.ShowWindow(self, win32defines.SW_MAXIMIZE)
        self.actions.log('Maximized window "{0}"'.format(self.window_text()))
        return self
    # Non PEP-8 alias
    Maximize = deprecated(maximize)

    # -----------------------------------------------------------
    def minimize(self):
        """Minimize the window"""
        win32functions.ShowWindow(self, win32defines.SW_MINIMIZE)
        # TODO: wait while window is minimized
        self.actions.log('Minimized window "{0}"'.format(self.window_text()))
        return self
    # Non PEP-8 alias
    Minimize = deprecated(minimize)

    # -----------------------------------------------------------
    def restore(self):
        """Restore the window to its previous state (normal or maximized)"""
        win32functions.ShowWindow(self, win32defines.SW_RESTORE)
        self.actions.log('Restored window "{0}"'.format(self.window_text()))
        return self
    # Non PEP-8 alias
    Restore = deprecated(restore)

    # -----------------------------------------------------------
    def get_show_state(self):
        """Get the show state and Maximized/minimzed/restored state

        Returns a value that is a union of the following

        * SW_HIDE the window is hidden.
        * SW_MAXIMIZE the window is maximized
        * SW_MINIMIZE the window is minimized
        * SW_RESTORE the window is in the 'restored'
          state (neither minimized or maximized)
        * SW_SHOW The window is not hidden
        """
        wp = win32structures.WINDOWPLACEMENT()
        wp.lenght = ctypes.sizeof(wp)

        ret = win32functions.GetWindowPlacement(self, ctypes.byref(wp))

        if not ret:
            raise ctypes.WinError()

        return wp.showCmd
    # Non PEP-8 alias
    GetShowState = deprecated(get_show_state)

    # -----------------------------------------------------------
    def is_minimized(self):
        """Indicate whether the window is minimized or not"""
        return self.get_show_state() == win32defines.SW_SHOWMINIMIZED

    # -----------------------------------------------------------
    def is_maximized(self):
        """Indicate whether the window is maximized or not"""
        return self.get_show_state() == win32defines.SW_SHOWMAXIMIZED

    # -----------------------------------------------------------
    def is_normal(self):
        """Indicate whether the window is normal (i.e. not minimized and not maximized)"""
        return self.get_show_state() == win32defines.SW_SHOWNORMAL

    # -----------------------------------------------------------
    def get_active(self):
        """Return a handle to the active window within the process"""
        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        window_thread_id = win32functions.GetWindowThreadProcessId(self.handle, None)
        ret = win32functions.GetGUIThreadInfo(
            window_thread_id,
            ctypes.byref(gui_info))

        if not ret:
            raise ctypes.WinError()

        hwndActive = gui_info.hwndActive
        if hwndActive:
            return HwndWrapper(hwndActive)
        else:
            return None
    # Non PEP-8 alias
    GetActive = deprecated(get_active)

    # -----------------------------------------------------------
    def get_focus(self):
        """Return the control in the process of this window that has the Focus
        """
        gui_info = win32structures.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        window_thread_id = win32functions.GetWindowThreadProcessId(self.handle, None)
        ret = win32functions.GetGUIThreadInfo(
            window_thread_id,
            ctypes.byref(gui_info))

        if not ret:
            return None

        return HwndWrapper(gui_info.hwndFocus)
    # Non PEP-8 alias
    GetFocus = deprecated(get_focus)

    # -----------------------------------------------------------
    def set_focus(self):
        """
        Set the focus to this control.

        Bring the window to the foreground first.
        The system restricts which processes can set the foreground window
        (https://msdn.microsoft.com/en-us/library/windows/desktop/ms633539(v=vs.85).aspx)
        so the mouse cursor is removed from the screen to prevent any side effects.
        """
        # "steal the focus" if there is another active window
        # otherwise it is already into the foreground and no action required
        if not self.has_focus():
            # Notice that we need to move the mouse out of the screen
            # but we don't use the built-in methods of the class:
            # self.mouse_move doesn't do the job well even with absolute=True
            # self.move_mouse_input can't be used as it calls click_input->set_focus
            mouse.move(coords=(-10000, 500))  # move the mouse out of screen to the left

            # change active window
            if self.is_minimized():
                if self.was_maximized():
                    self.maximize()
                else:
                    self.restore()
            else:
                win32gui.ShowWindow(self.handle, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self.handle)

            # make sure that we are idle before returning
            win32functions.WaitGuiThreadIdle(self.handle)

            # only sleep if we had to change something!
            time.sleep(Timings.after_setfocus_wait)

        return self
    # Non PEP-8 alias
    SetFocus = deprecated(set_focus)

    def has_focus(self):
        """Check the window is in focus (foreground)"""
        return self.handle == win32gui.GetForegroundWindow()

    def has_keyboard_focus(self):
        """Check the keyboard focus on this control."""
        control_thread = win32functions.GetWindowThreadProcessId(self.handle, None)
        win32process.AttachThreadInput(control_thread, win32api.GetCurrentThreadId(), 1)
        focused = win32gui.GetFocus()
        win32process.AttachThreadInput(control_thread, win32api.GetCurrentThreadId(), 0)

        win32functions.WaitGuiThreadIdle(self.handle)

        return self.handle == focused

    def set_keyboard_focus(self):
        """Set the keyboard focus to this control."""
        control_thread = win32functions.GetWindowThreadProcessId(self.handle, None)
        win32process.AttachThreadInput(control_thread, win32api.GetCurrentThreadId(), 1)
        win32functions.SetFocus(self.handle)
        win32process.AttachThreadInput(control_thread, win32api.GetCurrentThreadId(), 0)

        win32functions.WaitGuiThreadIdle(self.handle)

        time.sleep(Timings.after_setfocus_wait)
        return self

    # -----------------------------------------------------------
    def set_application_data(self, appdata):
        """Application data is data from a previous run of the software

        It is essential for running scripts written for one spoke language
        on a different spoken language
        """
        self.appdata = appdata


    _scroll_types = {"left": {
            "line" : win32defines.SB_LINELEFT,
            "page" : win32defines.SB_PAGELEFT,
            "end" :  win32defines.SB_LEFT,
            },
        "right": {
                "line" : win32defines.SB_LINERIGHT,
                "page" : win32defines.SB_PAGERIGHT,
                "end" :  win32defines.SB_RIGHT,
            },
        "up": {
                "line" : win32defines.SB_LINEUP,
                "page" : win32defines.SB_PAGEUP,
                "end" :  win32defines.SB_TOP,
            },
        "down": {
                "line" : win32defines.SB_LINEDOWN,
                "page" : win32defines.SB_PAGEDOWN,
                "end" :  win32defines.SB_BOTTOM,
            },
        }
    # Non PEP-8 alias
    SetApplicationData = deprecated(set_application_data)

    # -----------------------------------------------------------
    def scroll(self, direction, amount, count = 1, retry_interval = None):
        """Ask the control to scroll itself

        **direction** can be any of "up", "down", "left", "right"
        **amount** can be one of "line", "page", "end"
        **count** (optional) the number of times to scroll
        """
        self._ensure_enough_privileges('WM_HSCROLL/WM_VSCROLL')

        # check which message we want to send
        if direction.lower() in ("left", "right"):
            message = win32defines.WM_HSCROLL
        elif direction.lower() in ("up", "down"):
            message = win32defines.WM_VSCROLL

        # the constant that matches direction, and how much
        try:
            scroll_type = \
                self._scroll_types[direction.lower()][amount.lower()]
        except KeyError:
            raise ValueError("""Wrong arguments:
                direction can be any of "up", "down", "left", "right"
                amount can be any of "line", "page", "end"
                """)

        # Scroll as often as we have been asked to
        if retry_interval is None:
            retry_interval = Timings.scroll_step_wait
        while count > 0:
            self.send_message(message, scroll_type)
            time.sleep(retry_interval)
            count -= 1

        return self
    # Non PEP-8 alias
    Scroll = deprecated(scroll)

    # -----------------------------------------------------------
    def get_toolbar(self):
        """Get the first child toolbar if it exists"""
        for child in self.children():
            if child.__class__.__name__ == 'ToolbarWrapper':
                return child

        return None
    # Non PEP-8 alias
    GetToolbar = deprecated(get_toolbar)

    # Non PEP-8 aliases for BaseWrapper methods
    # We keep them for the backward compatibility in legacy scripts
    ClickInput = deprecated(BaseWrapper.click_input)
    DoubleClickInput = deprecated(BaseWrapper.double_click_input)
    RightClickInput = deprecated(BaseWrapper.right_click_input)
    VerifyVisible = deprecated(BaseWrapper.verify_visible)
    _NeedsImageProp = deprecated(BaseWrapper._needs_image_prop, deprecated_name='_NeedsImageProp')
    FriendlyClassName = deprecated(BaseWrapper.friendly_class_name)
    Class = deprecated(BaseWrapper.class_name, deprecated_name='Class')
    WindowText = deprecated(BaseWrapper.window_text)
    ControlID = deprecated(BaseWrapper.control_id, deprecated_name='ControlID')
    IsVisible = deprecated(BaseWrapper.is_visible)
    IsEnabled = deprecated(BaseWrapper.is_enabled)
    Rectangle = deprecated(BaseWrapper.rectangle)
    ClientToScreen = deprecated(BaseWrapper.client_to_screen)
    ProcessID = deprecated(BaseWrapper.process_id, deprecated_name='ProcessID')
    IsDialog = deprecated(BaseWrapper.is_dialog)
    Parent = deprecated(BaseWrapper.parent)
    TopLevelParent = deprecated(BaseWrapper.top_level_parent)
    Texts = deprecated(BaseWrapper.texts)
    Children = deprecated(BaseWrapper.children)
    CaptureAsImage = deprecated(BaseWrapper.capture_as_image)
    GetProperties = deprecated(BaseWrapper.get_properties)
    DrawOutline = deprecated(BaseWrapper.draw_outline)
    IsChild = deprecated(BaseWrapper.is_child)
    VerifyActionable = deprecated(BaseWrapper.verify_actionable)
    VerifyEnabled = deprecated(BaseWrapper.verify_enabled)
    PressMouseInput = deprecated(BaseWrapper.press_mouse_input)
    ReleaseMouseInput = deprecated(BaseWrapper.release_mouse_input)
    MoveMouseInput = deprecated(BaseWrapper.move_mouse_input)
    DragMouseInput = deprecated(BaseWrapper.drag_mouse_input)
    WheelMouseInput = deprecated(BaseWrapper.wheel_mouse_input)
    TypeKeys = deprecated(BaseWrapper.type_keys)


#====================================================================
# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class DialogWrapper(HwndWrapper):

    """Wrap a dialog"""

    friendlyclassname = "Dialog"
    #windowclasses = ["#32770", ]
    can_be_label = True

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the DialogWrapper

        The only extra functionality here is to modify self.friendlyclassname
        to make it "Dialog" if the class is "#32770" otherwise to leave it
        the same as the window class.
        """
        HwndWrapper.__init__(self, hwnd)

        if self.class_name() == "#32770":
            self.friendlyclassname = "Dialog"
        else:
            self.friendlyclassname = self.class_name()

    #-----------------------------------------------------------
    def run_tests(self, tests_to_run = None, ref_controls = None):
        """Run the tests on dialog"""
        # the tests package is imported only when running unittests
        from .. import tests

        # get all the controls
        controls = [self] + self.children()

        # add the reference controls
        if ref_controls is not None:
            matched_flags = controlproperties.SetReferenceControls(
                controls, ref_controls)

            # todo: allow some checking of how well the controls matched
            # matched_flags says how well they matched
            # 1 = same number of controls
            # 2 = ID's matched
            # 4 = control classes matched
            # i.e. 1 + 2 + 4 = perfect match

        return tests.run_tests(controls, tests_to_run)
    # Non PEP-8 alias
    RunTests = deprecated(run_tests)

    #-----------------------------------------------------------
    def write_to_xml(self, filename):
        """Write the dialog an XML file (requires elementtree)"""
        controls = [self] + self.children()
        props = [ctrl.get_properties() for ctrl in controls]

        from .. import xml_helpers
        xml_helpers.WriteDialogToFile(filename, props)
    # Non PEP-8 alias
    WriteToXML = deprecated(write_to_xml)

    #-----------------------------------------------------------
    def client_area_rect(self):
        """Return the client area rectangle

        From MSDN:
        The client area of a control is the bounds of the control, minus the
        nonclient elements such as scroll bars, borders, title bars, and
        menus.
        """
        rect = win32structures.RECT(self.rectangle())
        self.send_message(win32defines.WM_NCCALCSIZE, 0, ctypes.byref(rect))
        return rect
    # Non PEP-8 alias
    ClientAreaRect = deprecated(client_area_rect)

    #-----------------------------------------------------------
    def hide_from_taskbar(self):
        """Hide the dialog from the Windows taskbar"""
        win32functions.ShowWindow(self, win32defines.SW_HIDE)
        win32functions.SetWindowLongPtr(self, win32defines.GWL_EXSTYLE, self.exstyle() | win32defines.WS_EX_TOOLWINDOW)
        win32functions.ShowWindow(self, win32defines.SW_SHOW)
    # Non PEP-8 alias
    HideFromTaskbar = deprecated(hide_from_taskbar)

    #-----------------------------------------------------------
    def show_in_taskbar(self):
        """Show the dialog in the Windows taskbar"""
        win32functions.ShowWindow(self, win32defines.SW_HIDE)
        win32functions.SetWindowLongPtr(self, win32defines.GWL_EXSTYLE,
            self.exstyle() | win32defines.WS_EX_APPWINDOW)
        win32functions.ShowWindow(self, win32defines.SW_SHOW)
    # Non PEP-8 alias
    ShowInTaskbar = deprecated(show_in_taskbar)

    #-----------------------------------------------------------
    def is_in_taskbar(self):
        """Check whether the dialog is shown in the Windows taskbar

        Thanks to David Heffernan for the idea:
        http://stackoverflow.com/questions/30933219/hide-window-from-taskbar-without-using-ws-ex-toolwindow
        A window is represented in the taskbar if:
        It has no owner and it does not have the WS_EX_TOOLWINDOW extended style,
        or it has the WS_EX_APPWINDOW extended style.
        """
        return self.has_exstyle(win32defines.WS_EX_APPWINDOW) or \
               (self.owner() is None and not self.has_exstyle(win32defines.WS_EX_TOOLWINDOW))
    # Non PEP-8 alias
    IsInTaskbar = deprecated(is_in_taskbar)

    #-----------------------------------------------------------
    def force_close(self):
        """Close the dialog forcefully using WM_QUERYENDSESSION and return the result

        Window has let us know that it doesn't want to die - so we abort
        this means that the app is not hung - but knows it doesn't want
        to close yet - e.g. it is asking the user if they want to save.
        """
        self.send_message_timeout(
            win32defines.WM_QUERYENDSESSION,
            timeout = .5,
            timeoutflags = (win32defines.SMTO_ABORTIFHUNG)) # |
        #win32defines.SMTO_NOTIMEOUTIFNOTHUNG)) # |
        #win32defines.SMTO_BLOCK)

        # get a handle we can wait on
        pid = ctypes.c_ulong()
        win32functions.GetWindowThreadProcessId(self.handle, ctypes.byref(pid))
        try:
            process_wait_handle = win32api.OpenProcess(
                win32con.SYNCHRONIZE | win32con.PROCESS_TERMINATE,
                0,
                pid.value)
        except win32gui.error:
            return True # already closed

        result = win32event.WaitForSingleObject(
            process_wait_handle,
            int(Timings.after_windowclose_timeout * 1000))

        return result != win32con.WAIT_TIMEOUT

#    #-----------------------------------------------------------
#    def read_controls_from_xml(self, filename):
#        from pywinauto import xml_helpers
#        [controlproperties.ControlProps(ctrl) for
#            ctrl in xml_helpers.ReadPropertiesFromFile(handle)]
#    # Non PEP-8 alias
#    ReadControlsFromXML = deprecated(read_controls_from_xml)

#    #-----------------------------------------------------------
#    def add_reference(self, reference):
#
#        if len(self.children() != len(reference)):
#            raise "different number of reference controls"
#
#        for i, ctrl in enumerate(reference):
#        # loop over each of the controls
#        # and set the reference
#            if isinstance(ctrl, dict):
#                ctrl = CtrlProps(ctrl)
#
#            self.
#            if ctrl.class_name() != self.children()[i+1].class_name():
#                print "different classes"
#    # Non PEP-8 alias
#    AddReference = deprecated(add_reference)


#====================================================================
def _perform_click(
        ctrl,
        button = "left",
        pressed = "",
        coords = (0, 0),
        double = False,
        button_down = True,
        button_up = True,
        absolute = False,
        ):
    """Low level method for performing click operations"""
    if ctrl is None:
        ctrl = HwndWrapper(win32functions.GetDesktopWindow())
    ctrl.verify_actionable()
    ctrl_text = ctrl.window_text()
    if ctrl_text is None:
        ctrl_text = six.text_type(ctrl_text)

    ctrl_friendly_class_name = ctrl.friendly_class_name()

    if isinstance(coords, win32structures.RECT):
        coords = coords.mid_point()
    # allow points objects to be passed as the coords
    elif isinstance(coords, win32structures.POINT):
        coords = [coords.x, coords.y]
    else:
        coords = list(coords)

    if absolute:
        coords = ctrl.client_to_screen(coords)

    # figure out the messages for click/press
    msgs = []
    if not double:
        if button.lower() == 'left':
            if button_down:
                msgs.append(win32defines.WM_LBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_LBUTTONUP)
        elif button.lower() == 'middle':
            if button_down:
                msgs.append(win32defines.WM_MBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_MBUTTONUP)
        elif button.lower() == 'right':
            if button_down:
                msgs.append(win32defines.WM_RBUTTONDOWN)
            if button_up:
                msgs.append(win32defines.WM_RBUTTONUP)
        elif button.lower() == 'move':
            msgs.append(win32defines.WM_MOUSEMOVE)

    # figure out the messages for double clicking
    else:
        if button.lower() == 'left':
            msgs = (
                win32defines.WM_LBUTTONDOWN,
                win32defines.WM_LBUTTONUP,
                win32defines.WM_LBUTTONDBLCLK,
                win32defines.WM_LBUTTONUP)
        elif button.lower() == 'middle':
            msgs = (
                win32defines.WM_MBUTTONDOWN,
                win32defines.WM_MBUTTONUP,
                win32defines.WM_MBUTTONDBLCLK,
                win32defines.WM_MBUTTONUP)
        elif button.lower() == 'right':
            msgs = (
                win32defines.WM_RBUTTONDOWN,
                win32defines.WM_RBUTTONUP,
                win32defines.WM_RBUTTONDBLCLK,
                win32defines.WM_RBUTTONUP)
        elif button.lower() == 'move':
            msgs.append(win32defines.WM_MOUSEMOVE)

    # figure out the flags and pack coordinates
    flags, click_point = _calc_flags_and_coords(pressed, coords)

    #control_thread = win32functions.GetWindowThreadProcessId(ctrl, None)
    #win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), control_thread, win32defines.TRUE)
    # TODO: check return value of AttachThreadInput properly

    # send each message
    for msg in msgs:
        win32functions.PostMessage(ctrl, msg, win32structures.WPARAM(flags), win32structures.LPARAM(click_point))
        #ctrl.post_message(msg, flags, click_point)
        #flags = 0

        time.sleep(Timings.sendmessagetimeout_timeout)

        # wait until the thread can accept another message
        win32functions.WaitGuiThreadIdle(ctrl.handle)

    # detach the Python process with the process that self is in
    #win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), control_thread, win32defines.FALSE)
    # TODO: check return value of AttachThreadInput properly

    # wait a certain(short) time after the click
    time.sleep(Timings.after_click_wait)

    if button.lower() == 'move':
        message = 'Moved mouse over ' + ctrl_friendly_class_name + ' "' + ctrl_text + \
                  '" to screen point ' + str(tuple(coords)) + ' by WM_MOUSEMOVE'
    else:
        message = 'Clicked ' + ctrl_friendly_class_name + ' "' + ctrl_text + \
                  '" by ' + str(button) + ' button event ' + str(tuple(coords))
        if double:
            message = 'Double-c' + message[1:]
    ActionLogger().log(message)

_mouse_flags = {
    "left": win32defines.MK_LBUTTON,
    "right": win32defines.MK_RBUTTON,
    "middle": win32defines.MK_MBUTTON,
    "shift": win32defines.MK_SHIFT,
    "control": win32defines.MK_CONTROL,
}

#====================================================================
def _calc_flags_and_coords(pressed, coords):
    """Calculate the flags to use and the coordinates for mouse actions"""
    flags = 0

    for key in pressed.split():
        flags |= _mouse_flags[key.lower()]

    click_point = win32functions.MakeLong(coords[1], coords[0])

    return flags, click_point

#====================================================================
class _DummyControl(dict):

    """A subclass of dict so that we can assign attributes"""
    pass

#====================================================================
def get_dialog_props_from_handle(hwnd):
    """Get the properties of all the controls as a list of dictionaries"""
    # wrap the dialog handle and start a new list for the
    # controls on the dialog
    try:
        controls = [hwnd, ]
        controls.extend(hwnd.children())
    except AttributeError:
        controls = [HwndWrapper(hwnd), ]

        # add all the children of the dialog
        controls.extend(controls[0].children())

    props = []

    # Add each control to the properties for this dialog
    for ctrl in controls:
        # Get properties for each control and wrap them in
        # _DummyControl so that we can assign handle
        ctrl_props = _DummyControl(ctrl.get_properties())

        # assign the handle
        ctrl_props.handle = ctrl.handle

        # offset the rectangle from the dialog rectangle
        ctrl_props['rectangle'] -= controls[0].rectangle()

        props.append(ctrl_props)

    return props
# Non PEP-8 alias
GetDialogPropsFromHandle = deprecated(get_dialog_props_from_handle)


backend.register('win32', HwndElementInfo, HwndWrapper)
backend.registry.backends['win32'].dialog_class = DialogWrapper
backend.activate('win32') # default
