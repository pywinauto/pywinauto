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

"""Cross-platform module to emulate mouse events like a real user"""

import sys

if sys.platform == 'win32':
    from .windows.mouse import MouseEvent, MouseHook
    from .windows.mouse import _get_cursor_pos, _set_cursor_pos, _perform_click_input
    from .windows.mouse import click, double_click, right_click, move, press, release, scroll, wheel_click
else:
    import time

    from Xlib.display import Display
    from Xlib import X
    from Xlib.ext.xtest import fake_input

    BUTTON_MAPPING = {'left': 0, 'middle': 1, 'right': 2, 'up_scroll': 3,
                  'down_scroll': 4, 'left_scroll': 5, 'right_scroll': 6}

    _display = Display()

    # TODO: check this method
    def _get_cursor_pos():  # get global coordinate
        data = _display.screen().root.query_pointer()._data
        return data["root_x"], data["root_y"]

    def _perform_click_input(button='left', coords=(0, 0),
                             button_down=True, button_up=True, double=False,
                             wheel_dist=0, pressed="", key_down=True, key_up=True,
                             fast_move=False):
        """Perform a click action using Python-xlib"""
        #Move mouse
        x = int(coords[0])
        y = int(coords[1])
        fake_input(_display, X.MotionNotify, x=x, y=y)
        if not fast_move:
            _display.sync()
        if button == 'wheel':
            if wheel_dist == 0:
                return
            if wheel_dist > 0:
                button = 'up_scroll'
            if wheel_dist < 0:
                button = 'down_scroll'
            for _ in range(abs(wheel_dist)):
                _perform_click_input(button, coords)
        else:
            pointer_map = _display.get_pointer_mapping()
            button = pointer_map[BUTTON_MAPPING[button]]
            repeat = 1
            if double:
                repeat = 2
            for _ in range(repeat):
                if button_down:
                    fake_input(_display, X.ButtonPress, button)
                    _display.sync()
                if button_up:
                    fake_input(_display, X.ButtonRelease, button)
                    _display.sync()


    def click(button='left', coords=(0, 0)):
        """Click at the specified coordinates"""
        _perform_click_input(button=button, coords=coords)


    def double_click(button='left', coords=(0, 0)):
        """Double click at the specified coordinates"""
        _perform_click_input(button=button, coords=coords, double=True)


    def right_click(coords=(0, 0)):
        """Right click at the specified coords"""
        _perform_click_input(button='right', coords=coords)


    def move(coords=(0, 0), duration=0.0):
        """Move the mouse"""
        if not isinstance(duration, float):
            raise TypeError("duration must be float (in seconds)")
        minimum_duration = 0.05
        if duration >= minimum_duration:
            x_start, y_start = _get_cursor_pos()
            delta_x = coords[0] - x_start
            delta_y = coords[1] - y_start
            max_delta = max(abs(delta_x), abs(delta_y))
            num_steps = max_delta
            sleep_amount = duration / max(num_steps, 1)
            if sleep_amount < minimum_duration:
                num_steps = int(num_steps * sleep_amount / minimum_duration)
                sleep_amount = minimum_duration
            delta_x /= max(num_steps, 1)
            delta_y /= max(num_steps, 1)
            for step in range(num_steps):
                _perform_click_input(button='move', coords=(x_start + int(delta_x*step), y_start + int(delta_y*step)),
                                    button_down=False, button_up=False, fast_move=True)
                time.sleep(sleep_amount)
        _perform_click_input(button='move', coords=coords, button_down=False, button_up=False)


    def press(button='left', coords=(0, 0)):
        """Press the mouse button"""
        _perform_click_input(button=button, coords=coords, button_down=True, button_up=False)


    def release(button='left', coords=(0, 0)):
        """Release the mouse button"""
        _perform_click_input(button=button, coords=coords, button_down=False, button_up=True)


    def scroll(coords=(0, 0), wheel_dist=1):
        """Do mouse wheel"""
        if wheel_dist:
            _perform_click_input(button='wheel', wheel_dist=wheel_dist, coords=coords)


    def wheel_click(coords=(0, 0)):
        """Middle mouse button click at the specified coords"""
        _perform_click_input(button='middle', coords=coords)
