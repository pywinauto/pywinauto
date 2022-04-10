# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""Basic wrapping of UI Automation elements"""
import six

try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None

from ..macos.ax_element_info import AxElementInfo

from ..macos.macos_functions import set_ax_attribute
from ..macos.macos_functions import setAppFrontmost

from ..macos.macos_structures import AX_RECT, AX_POINT

from .. import backend
from .. import keyboard

from ..timings import Timings
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta
from ..mouse import _perform_click_input


# ====================================================================
class InvalidWindowHandle(RuntimeError):

    """Raised when an invalid handle is passed to AXWrapper"""

    def __init__(self, hwnd):
        """Initialise the RuntimeError parent with the mesage"""
        RuntimeError.__init__(self,
                              "Handle {0} is not a vaild window handle".format(hwnd))


# =========================================================================
class AXMeta(BaseMeta):

    """Metaclass for AXWrapper objects"""

    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""
        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls._control_types:
            AXMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this AX element"""
        # Set a general wrapper by default
        wrapper_match = AXWrapper
        # print('element.control_type:', element.control_type)

        # Check for a more specific wrapper in the registry
        if element.control_type in AXMeta.control_type_to_cls:
            wrapper_match = AXMeta.control_type_to_cls[element.control_type]

        return wrapper_match


# =========================================================================
@six.add_metaclass(AXMeta)
class AXWrapper(BaseWrapper):

    """
    Default wrapper for User Interface Automation (AX) controls.

    All other AX wrappers are derived from this.

    This class wraps a lot of functionality of underlying AX features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """

    _control_types = []

    # ------------------------------------------------------------
    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(AXWrapper, cls)._create_wrapper(cls, element_info, AXWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid AXElementInfo or it can be an
          instance or subclass of AXWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['ax'])

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value"""
        if hasattr(self.element_info,'hash'):
            return self.element_info.hash()
        else:
            return ''

    # ------------------------------------------------------------

    def set_focus(self):
        # If element can be focusable we must take the following steps to make it focused:
        # 1. Make element keyboard focused
        # 2. Make the window that contains this element focused as well
        # Otherwise just focus the window
        window = None
        is_window = self.element_info.control_type == 'Window'
        if is_window:
            window = self.element_info
        else:
            window = self.element_info.window

        # Focus the element
        # Check the control type to avoid focusing twice
        if not is_window and self.element_info.can_be_keyboard_focusable:
            set_ax_attribute(self.element_info.ref,"AXFocused",True)
        
        # Focus the window
        if window and window.control_type == 'Window':
            set_ax_attribute(self.element_info.ref, "AXFocused", True)
            set_ax_attribute(self.element_info.ref, "AXMinimized", False)
            setAppFrontmost(self.element_info.process_id)

    def friendly_class_name(self):
        return self.element_info.control_type

    # ------------------------------------------------------------

    def type_keys(
        self,
        keys,
        pause = None,
        with_spaces = True,
        with_tabs = True,
        with_newlines = True,
        turn_off_numlock = False,
        set_foreground = True,
        vk_packet = True):

        friendly_class_name = self.friendly_class_name()

        if pause is None:
            pause = Timings.after_sendkeys_key_wait

        if set_foreground:
            self.set_focus()

        if isinstance(keys, six.text_type):
            aligned_keys = keys
        elif isinstance(keys, six.binary_type):
            aligned_keys = keys.decode(locale.getpreferredencoding())
        else:
            # convert a non-string input
            aligned_keys = six.text_type(keys)

        keyboard.send_keys(
            aligned_keys,
            pause,
            with_spaces,
            with_tabs,
            with_newlines,
            vk_packet
        )

        self.wait_for_idle()

        self.actions.log('Typed text to the ' + friendly_class_name + ': ' + aligned_keys)
        return  self

# -----------------------------------------------------------
    def drag_mouse_input(self,
                         dst=(0, 0),
                         src=None,
                         button="left",
                         pressed="",
                         absolute=True):
        """Click on **src**, drag it and drop on **dst**

        * **dst** is a destination wrapper object or just coordinates.
        * **src** is a source wrapper object or coordinates.
          If **src** is None the self is used as a source object.
        * **button** is a mouse button to hold during the drag.
          It can be "left", "right", "middle" or "x"
        * **pressed** is a key on the keyboard to press during the drag.
        * **absolute** specifies whether to use absolute coordinates
          for the mouse pointer locations
        """
        if not src:
            src = self

        if dst == src:
            raise AttributeError("Can't drag-n-drop on itself")

        if isinstance(src, AXWrapper):
            press_coords = src._calc_click_coords()
        elif isinstance(src, AX_POINT):
            press_coords = (src.x, src.y)
        else:
            press_coords = src

        if isinstance(dst, AXWrapper):
            release_coords = dst._calc_click_coords()
        elif isinstance(dst, AX_POINT):
            release_coords = (dst.x, dst.y)
        else:
            release_coords = dst
        self.actions.log('Drag mouse from coordinates {0} to {1}'.format(press_coords, release_coords))

        self.press_mouse_input(button, press_coords, pressed, absolute=absolute)
        time.sleep(Timings.before_drag_wait)
        for i in range(5):
            self.move_mouse_input((press_coords[0] + i, press_coords[1]), pressed=pressed, absolute=absolute) # "left"
            time.sleep(Timings.drag_n_drop_move_mouse_wait)
        self.move_mouse_input(release_coords, pressed=pressed, absolute=absolute) # "left"
        time.sleep(Timings.before_drop_wait)
        self.release_mouse_input(button, release_coords, pressed, absolute=absolute)
        time.sleep(Timings.after_drag_n_drop_wait)
        return self

    #-----------------------------------------------------------
    def click_input(
        self,
        button = "left",
        coords = (None, None),
        button_down = True,
        button_up = True,
        double = False,
        wheel_dist = 0,
        use_log = True,
        pressed = "",
        absolute = False,
        key_down = True,
        key_up = True):
        """Click at the specified coordinates

        * **button** The mouse button to click. One of 'left', 'right',
          'middle' or 'x' (Default: 'left', 'move' is a special case)
        * **coords** The coordinates to click at.(Default: the center of the control)
        * **double** Whether to perform a double click or not (Default: False)
        * **wheel_dist** The distance to move the mouse wheel (default: 0)

        NOTES:
           This is different from click method in that it requires the control
           to be visible on the screen but performs a more realistic 'click'
           simulation.

           This method is also vulnerable if the mouse is moved by the user
           as that could easily move the mouse off the control before the
           click_input has finished.
        """
        if self.is_dialog():
            self.set_focus()
        #if self.backend.name == "win32":
        #    self._ensure_enough_privileges('win32api.SetCursorPos(x, y)')
        # TODO: check it in more general way for both backends

        if isinstance(coords, AX_RECT):
            coords = coords.mid_point()
        # allow points objects to be passed as the coords
        elif isinstance(coords, AX_POINT):
            coords = [coords.x, coords.y]
        else:
            coords = list(coords)

        # set the default coordinates
        if coords[0] is None:
            coords[0] = int(self.rectangle().width / 2)
        if coords[1] is None:
            coords[1] = int(self.rectangle().height / 2)

        if not absolute:
            coords = self.client_to_screen(coords)

        message = None
        if use_log:
            ctrl_text = self.window_text()
            if ctrl_text is None:
                ctrl_text = six.text_type(ctrl_text)
            if button.lower() == 'move':
                message = 'Moved mouse over ' + self.friendly_class_name() + \
                          ' "' + ctrl_text + '" to screen point ('
            else:
                message = 'Clicked ' + self.friendly_class_name() + ' "' + ctrl_text + \
                          '" by ' + str(button) + ' button mouse click at '
                if double:
                    message = 'Double-c' + message[1:]
            message += str(tuple(coords))

        _perform_click_input(button, coords, double, button_down, button_up,
                             wheel_dist=wheel_dist, pressed=pressed,
                             key_down=key_down, key_up=key_up)

        if message:
            self.actions.log(message)

    def minimize(self):
        set_ax_attribute(self.element_info.ref, 'AXMinimized', True)

    def maximize(self):
        set_ax_attribute(self.element_info.ref, 'AXMaximized', True)

    #-----------------------------------------------------------
    def capture_as_image(self, rect=None, save_image=False, image_name='image.png'):
        """
        Return a PIL image of the control.

        See PIL documentation to know what you can do with the resulting
        image.
        """
        control_rectangle = self.rectangle()

        # PIL is optional so check first
        if not ImageGrab:
            print("PIL does not seem to be installed. "
                  "PIL is required for capture_as_image")
            self.actions.log("PIL does not seem to be installed. "
                             "PIL is required for capture_as_image")
            return None

        if rect:
            control_rectangle = rect

        # get the control rectangle in a way that PIL likes it
        width = control_rectangle.width()
        height = control_rectangle.height()
        left = control_rectangle.left
        right = control_rectangle.right
        top = control_rectangle.top
        bottom = control_rectangle.bottom
        box = (left, top, right, bottom)

        pil_img_obj = ImageGrab.grab(box)

        if save_image == True:
            pil_img_obj.save(image_name)

        return pil_img_obj

#====================================================================


backend.register('ax', AxElementInfo, AXWrapper)
backend.activate('ax')  # default for macOS