# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Base class for all wrappers in all backends"""
from __future__ import unicode_literals
from __future__ import print_function

import abc
import ctypes
import locale
import re
import time
import win32process
import six

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

from .. import keyboard
from .. import win32defines, win32structures, win32functions
from ..timings import Timings
from ..actionlogger import ActionLogger
from ..mouse import _perform_click_input

from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta, InvalidElement, ElementNotEnabled, ElementNotVisible, \
    remove_non_alphanumeric_symbols

#=========================================================================
@six.add_metaclass(BaseMeta)
class Win32Wrapper(BaseWrapper):
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
        return Win32Wrapper._create_wrapper(cls, element_info, Win32Wrapper)

    #------------------------------------------------------------
    def client_to_screen(self, client_point):
        """Maps point from client to screen coordinates"""
        # Use a direct call to element_info.rectangle instead of self.rectangle
        # because the latter can be overriden in one of derived wrappers
        # (see _treeview_element.rectangle or _listview_item.rectangle)
        rect = self.element_info.rectangle
        if isinstance(client_point, win32structures.POINT):
            return (client_point.x + rect.left, client_point.y + rect.top)
        else:
            return (client_point[0] + rect.left, client_point[1] + rect.top)

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
        dc = win32functions.CreateDC("DISPLAY", None, None, None )

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
        key_up = True):
        """Click at the specified coordinates

        * **button** The mouse button to click. One of 'left', 'right',
          'middle' or 'x' (Default: 'left')
        * **coords** The coordinates to click at.(Default: center of control)
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
        ctrl_text = self.window_text()
        if isinstance(coords, win32structures.RECT):
            coords = [coords.left, coords.top]

        # allow points objects to be passed as the coords
        if isinstance(coords, win32structures.POINT):
            coords = [coords.x, coords.y]
        #else:
        coords = list(coords)

        # set the default coordinates
        if coords[0] is None:
            coords[0] = int(self.rectangle().width() / 2)
        if coords[1] is None:
            coords[1] = int(self.rectangle().height() / 2)

        if not absolute:
            coords = self.client_to_screen(coords)

        _perform_click_input(button, coords, double, button_down, button_up,
                             wheel_dist=wheel_dist, pressed=pressed,
                             key_down=key_down, key_up=key_up)

        if use_log:
            if ctrl_text is None:
                ctrl_text = six.text_type(ctrl_text)
            message = 'Clicked ' + self.friendly_class_name() + ' "' + ctrl_text + \
                      '" by ' + str(button) + ' button mouse click (x,y=' + \
                      ','.join([str(coord) for coord in coords]) + ')'
            if double:
                message = 'Double-c' + message[1:]
            if button.lower() == 'move':
                message = 'Moved mouse over ' + self.friendly_class_name() + \
                          ' "' + ctrl_text + '" to screen point (x,y=' + \
                          ','.join([str(coord) for coord in coords]) + ')'
            ActionLogger().log(message)

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

        if dst is src:
            raise AttributeError("Can't drag-n-drop on itself")

        if isinstance(src, Win32Wrapper):
            press_coords = src._calc_click_coords()
        elif isinstance(src, win32structures.POINT):
            press_coords = (src.x, src.y)
        else:
            press_coords = src

        if isinstance(dst, Win32Wrapper):
            release_coords = dst._calc_click_coords()
        elif isinstance(dst, win32structures.POINT):
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
    def type_keys(
        self,
        keys,
        pause = None,
        with_spaces = False,
        with_tabs = False,
        with_newlines = False,
        turn_off_numlock = True,
        set_foreground = True):
        """
        Type keys to the element using keyboard.SendKeys

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
            window_thread_id, _ = win32process.GetWindowThreadProcessId(int(self.handle))
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
        keyboard.SendKeys(
            aligned_keys,
            pause,
            with_spaces,
            with_tabs,
            with_newlines,
            turn_off_numlock)

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

#====================================================================
