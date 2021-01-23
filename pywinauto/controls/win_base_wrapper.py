# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
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

"""Base class for all wrappers on Windows OS"""
from __future__ import unicode_literals
from __future__ import print_function

import ctypes
import locale
import time

import win32gui
import win32ui
import win32api
import win32con
import six

from ..windows.win32structures import RECT

try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None

from .. import keyboard
from ..windows import win32defines, win32functions, win32structures
from ..timings import Timings
from ..mouse import _perform_click_input

from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta


#=========================================================================
@six.add_metaclass(BaseMeta)
class WinBaseWrapper(BaseWrapper):
    """
    Abstract wrapper for elements.

    All other wrappers are derived from this.
    """

    # Properties required for _MetaWrapper class
    friendlyclassname = None
    windowclasses = []

    # Properties that describe type of the element
    can_be_label = False
    has_title = True

    #------------------------------------------------------------
    def __new__(cls, element_info):
        return WinBaseWrapper._create_wrapper(cls, element_info, WinBaseWrapper)

    #-----------------------------------------------------------
    def draw_outline(
        self,
        colour='green',
        thickness=2,
        fill=win32defines.BS_NULL,
        rect=None):
        """
        Draw an outline around the window.

        * **colour** can be either an integer or one of 'red', 'green', 'blue'
          (default 'green')
        * **thickness** thickness of rectangle (default 2)
        * **fill** how to fill in the rectangle (default BS_NULL)
        * **rect** the coordinates of the rectangle to draw (defaults to
          the rectangle of the control)
        """

        # don't draw if dialog is not visible
        if not self.is_visible():
            return

        colours = {
            "green": 0x00ff00,
            "blue": 0xff0000,
            "red": 0x0000ff,
        }

        # if it's a known colour
        if colour in colours:
            colour = colours[colour]

        if rect is None:
            rect = self.rectangle()

        # create the pen(outline)
        pen_handle = win32functions.CreatePen(
                win32defines.PS_SOLID, thickness, colour)

        # create the brush (inside)
        brush = win32structures.LOGBRUSH()
        brush.lbStyle = fill
        brush.lbHatch = win32defines.HS_DIAGCROSS
        brush_handle = win32functions.CreateBrushIndirect(ctypes.byref(brush))

        # get the Device Context
        dc = win32functions.CreateDC("DISPLAY", None, None, None)

        # push our objects into it
        win32functions.SelectObject(dc, brush_handle)
        win32functions.SelectObject(dc, pen_handle)

        # draw the rectangle to the DC
        win32functions.Rectangle(
            dc, rect.left, rect.top, rect.right, rect.bottom)

        # Delete the brush and pen we created
        win32functions.DeleteObject(brush_handle)
        win32functions.DeleteObject(pen_handle)

        # delete the Display context that we created
        win32functions.DeleteDC(dc)

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
        key_up = True,
        fast_move = False):
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
        if self.backend.name == "win32":
            self._ensure_enough_privileges('win32api.SetCursorPos(x, y)')
        # TODO: check it in more general way for both backends

        if isinstance(coords, win32structures.RECT):
            coords = coords.mid_point()
        # allow points objects to be passed as the coords
        elif isinstance(coords, win32structures.POINT):
            coords = [coords.x, coords.y]
        else:
            coords = list(coords)

        # set the default coordinates
        if coords[0] is None:
            coords[0] = int(self.rectangle().width() / 2)
        if coords[1] is None:
            coords[1] = int(self.rectangle().height() / 2)

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
                             key_down=key_down, key_up=key_up, fast_move=fast_move)

        if message:
            self.actions.log(message)

    # -----------------------------------------------------------
    def drag_mouse_input(self,
                         dst=(0, 0),
                         src=None,
                         button="left",
                         pressed="",
                         absolute=True,
                         duration=None):
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

        if not isinstance(duration, float) and duration is not None:
            raise TypeError("duration must be float (in seconds) or None")

        if isinstance(duration, float):
            total_pause = 0.5 + Timings.before_drag_wait + Timings.before_drop_wait + Timings.after_drag_n_drop_wait
            if duration < total_pause:
                raise ValueError("duration must be >= " + str(total_pause))
            duration -= total_pause

        if isinstance(src, WinBaseWrapper):
            press_coords = src._calc_click_coords()
        elif isinstance(src, win32structures.POINT):
            press_coords = (src.x, src.y)
        else:
            press_coords = src

        if isinstance(dst, WinBaseWrapper):
            release_coords = dst._calc_click_coords()
        elif isinstance(dst, win32structures.POINT):
            release_coords = (dst.x, dst.y)
        else:
            release_coords = dst
        self.actions.log('Drag mouse from coordinates {0} to {1}'.format(press_coords, release_coords))

        self.press_mouse_input(button, press_coords, pressed, absolute=absolute)
        time.sleep(Timings.before_drag_wait)

        if duration is None:
            duration = 0.0
            # this is necessary for testDragMouseInput
            for i in range(5):
                self.move_mouse_input((press_coords[0] + i, press_coords[1]), pressed=pressed, absolute=absolute)
                time.sleep(Timings.drag_n_drop_move_mouse_wait)

        self.move_mouse_input(release_coords, pressed=pressed, absolute=absolute, duration=duration)

        self.move_mouse_input(release_coords, pressed=pressed, absolute=absolute)  # "left"
        time.sleep(Timings.before_drop_wait)

        self.release_mouse_input(button, release_coords, pressed, absolute=absolute)
        time.sleep(Timings.after_drag_n_drop_wait)
        return self

    # -----------------------------------------------------------
    def type_keys(
        self,
        keys,
        pause = None,
        with_spaces = False,
        with_tabs = False,
        with_newlines = False,
        turn_off_numlock = True,
        set_foreground = True,
        vk_packet = True):
        """
        Type keys to the element using keyboard.send_keys

        This uses the re-written keyboard_ python module where you can
        find documentation on what to use for the **keys**.

        .. _keyboard: pywinauto.keyboard.html
        """
        self.verify_actionable()
        friendly_class_name = self.friendly_class_name()

        if pause is None:
            pause = Timings.after_sendkeys_key_wait

        if set_foreground:
            self.set_focus()

        # attach the Python process with the process that self is in
        if self.element_info.handle:
            window_thread_id = win32functions.GetWindowThreadProcessId(self.handle, None)
            win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), window_thread_id, win32defines.TRUE)
            # TODO: check return value of AttachThreadInput properly
        else:
            # TODO: UIA stuff maybe
            pass

        if isinstance(keys, six.text_type):
            aligned_keys = keys
        elif isinstance(keys, six.binary_type):
            aligned_keys = keys.decode(locale.getpreferredencoding())
        else:
            # convert a non-string input
            aligned_keys = six.text_type(keys)

        # Play the keys to the active window
        keyboard.send_keys(
            aligned_keys,
            pause,
            with_spaces,
            with_tabs,
            with_newlines,
            turn_off_numlock,
            vk_packet)

        # detach the python process from the window's process
        if self.element_info.handle:
            win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), window_thread_id, win32defines.FALSE)
            # TODO: check return value of AttachThreadInput properly
        else:
            # TODO: UIA stuff
            pass

        self.wait_for_idle()

        self.actions.log('Typed text to the ' + friendly_class_name + ': ' + aligned_keys)
        return self

    #-----------------------------------------------------------
    def set_focus(self):
        """Set the focus to this element"""
        pass

    # -----------------------------------------------------------
    def was_maximized(self):
        """Indicate whether the window was maximized before minimizing or not"""
        if self.handle:
            (flags, _, _, _, _) = win32gui.GetWindowPlacement(self.handle)
            return (flags & win32con.WPF_RESTORETOMAXIMIZED == win32con.WPF_RESTORETOMAXIMIZED)
        else:
            return None

    #-----------------------------------------------------------
    def capture_as_image(self, rect=None):
        """
        Return a PIL image of the control.

        See PIL documentation to know what you can do with the resulting
        image.
        """
        control_rectangle = self.rectangle()
        if not (control_rectangle.width() and control_rectangle.height()):
            return None

        # PIL is optional so check first
        if not ImageGrab:
            print("PIL does not seem to be installed. "
                  "PIL is required for capture_as_image")
            self.actions.log("PIL does not seem to be installed. "
                             "PIL is required for capture_as_image")
            return None

        if rect:
            if not isinstance(rect, RECT):
                raise TypeError("capture_as_image() takes rect of type {} while incorrect type {} is given"
                                .format(RECT, type(rect)))
            control_rectangle = rect

        # get the control rectangle in a way that PIL likes it
        width = control_rectangle.width()
        height = control_rectangle.height()
        left = control_rectangle.left
        right = control_rectangle.right
        top = control_rectangle.top
        bottom = control_rectangle.bottom
        box = (left, top, right, bottom)

        # check the number of monitors connected
        if (len(win32api.EnumDisplayMonitors()) > 1):
                hwin = win32gui.GetDesktopWindow()
                hwindc = win32gui.GetWindowDC(hwin)
                srcdc = win32ui.CreateDCFromHandle(hwindc)
                memdc = srcdc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(srcdc, width, height)
                memdc.SelectObject(bmp)
                memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

                bmpinfo = bmp.GetInfo()
                bmpstr = bmp.GetBitmapBits(True)
                pil_img_obj = Image.frombuffer('RGB',
                                               (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                               bmpstr,
                                               'raw',
                                               'BGRX',
                                               0,
                                               1)
                win32gui.DeleteObject(bmp.GetHandle())
                memdc.DeleteDC()
                win32gui.ReleaseDC(hwin, hwindc)
        else:
            # grab the image and get raw data as a string
            pil_img_obj = ImageGrab.grab(box)

        return pil_img_obj

#====================================================================
