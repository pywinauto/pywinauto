# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"""Timing settings for all of pywinauto

This module has one object that should be used for all timing adjustments
  timings.Timings

There are a couple of predefined settings

timings.Timings.Fast()
timings.Timings.Defaults()
timings.Timings.Slow()

The Following are the individual timing settings that can be adjusted:

* window_find_timeout	(default 3)
* window_find_retry (default .09)

* app_start_timeout (default 10)
* app_start_retry   (default .90)

* exists_timeout    (default .5)
* exists_retry  (default .3)

* after_click_wait  (default .09)
* after_clickinput_wait (default .01)

* after_menu_wait   (default .05)

* after_sendkeys_key_wait   (default .01)

* after_button_click_wait   (default 0)

* before_closeclick_wait    (default .1)
* closeclick_retry  (default .05)
* closeclick_dialog_close_wait  (default .05)
* after_closeclick_wait (default .2)

* after_setfocus_wait   (default .06)

* after_setcursorpos_wait   (default .01)

"""


class TimeConfig(object):
    __default_timing = {
        'window_find_timeout' : 3,
        'window_find_retry' : .09,

        'app_start_timeout' : 10,
        'app_start_retry' : .90,

        'exists_timeout' : .5,
        'exists_retry' : .3,

        'after_click_wait' : .09,
        'after_clickinput_wait' : .01,

        'after_menu_wait' : .05,

        'after_sendkeys_key_wait' : .01,

        'after_button_click_wait' : 0,

        'before_closeclick_wait' : .1,
        'closeclick_retry' : .05,
        'closeclick_dialog_close_wait' : .05,
        'after_closeclick_wait' : .2,

        'after_setfocus_wait' : .06,

        'after_setcursorpos_wait' : .01,

        'sendmessagetimeout_timeout' : .001

    }


    _timings = __default_timing.copy()
    _cur_speed = 1

    def __getattr__(self, attr):
        if attr in self.__default_timing:
            return self._timings[attr]
        else:
            raise KeyError(
                "Unknown timing setting: %s" % attr)

    def __setattr__(self, attr, value):
        if attr in self.__default_timing:
            self._timings[attr] = value
        else:
            raise KeyError(
                "Unknown timing setting: %s" % attr)

    def Fast(self):
        for setting in self.__default_timing:
            if "_timeout" in setting:
                self._timings[setting] = 1

            if "_wait" in setting:
                self._timings[setting] = 0


            elif setting.endswith("_retry"):
                self._timings[setting] = 0.001

            self._timings['app_start_timeout'] = .5


    def Slow(self):
        for setting in self.__default_timing:
            if "_timeout" in setting:
                self._timings[setting] = self.__default_timing[setting] * 10

            if "_wait" in setting:
                self._timings[setting] = self.__default_timing[setting] * 3

            elif setting.endswith("_retry"):
                self._timings[setting] = self.__default_timing[setting] * 3

    def Defaults(self):
        self._timings = self.__default_timing.copy()


Timings = TimeConfig()
#
#
#
#def Defaults():
#    _current_timing = __default_timing.copy()
#
#
#def Slow():
#    for setting in __default_timing:
#        if "_timeout" in setting:
#            _current_timing[setting] = _default_timing[setting] * 10
#
#        if "_wait" in setting:
#            _current_timing[setting] = _default_timing[setting] * 3
#
#        elif setting.endswith("_retry"):
#            _current_timing[setting] = _default_timing[setting] * 3
#
#
#
#def SetTiming(**kwargs):
#    ""
#
#    for setting, time in kwargs.items():
#        if setting in __default_timing:
#            _current_timing[setting] = time
#        else:
#            raise KeyError(
#                "Unknown timing setting: %s" % setting)
#
#def Get(setting):
#    if setting in __default_timing:
#        return _current_timing[setting]
#    else:
#        raise KeyError(
#            "Unknown timing setting: %s" % setting)
