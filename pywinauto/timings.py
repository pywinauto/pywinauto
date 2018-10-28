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

"""Global timing settings for all of pywinauto

This module has one object that should be used for all timing adjustments:

 * timings.Timings

There are a couple of predefined settings:

 * ``timings.Timings.fast()``
 * ``timings.Timings.defaults()``
 * ``timings.Timings.slow()``

The Following are the individual timing settings that can be adjusted:

* window_find_timeout (default 5)
* window_find_retry (default .09)

* app_start_timeout (default 10)
* app_start_retry   (default .90)

* app_connect_timeout (default 5.)
* app_connect_retry (default .1)

* cpu_usage_interval (default .5)
* cpu_usage_wait_timeout (default 20)

* exists_timeout  (default .5)
* exists_retry   (default .3)

* after_click_wait  (default .09)
* after_clickinput_wait (default .09)

* after_menu_wait   (default .1)

* after_sendkeys_key_wait   (default .01)

* after_button_click_wait   (default 0)

* before_closeclick_wait    (default .1)
* closeclick_retry  (default .05)
* closeclick_dialog_close_wait  (default 2)
* after_closeclick_wait (default .2)

* after_windowclose_timeout (default 2)
* after_windowclose_retry (default .5)

* after_setfocus_wait   (default .06)
* setfocus_timeout   (default 2)
* setfocus_retry   (default .1)

* after_setcursorpos_wait   (default .01)

* sendmessagetimeout_timeout   (default .01)

* after_tabselect_wait   (default .05)

* after_listviewselect_wait   (default .01)
* after_listviewcheck_wait  default(.001)
* listviewitemcontrol_timeout default(1.5)

* after_treeviewselect_wait  default(.1)

* after_toobarpressbutton_wait  default(.01)

* after_updownchange_wait  default(.1)

* after_movewindow_wait  default(0)
* after_buttoncheck_wait  default(0)
* after_comboboxselect_wait  default(.001)
* after_listboxselect_wait  default(0)
* after_listboxfocuschange_wait  default(0)
* after_editsetedittext_wait  default(0)
* after_editselect_wait  default(.02)

* drag_n_drop_move_mouse_wait  default(.1)
* before_drag_wait  default(.2)
* before_drop_wait  default(.1)
* after_drag_n_drop_wait  default(.1)
* scroll_step_wait  default(.1)

"""

import six
import time
import operator
from functools import wraps

from . import deprecated


#=========================================================================
class TimeConfig(object):

    """Central storage and manipulation of timing values"""

    __default_timing = {
        'window_find_timeout': 5.,
        'window_find_retry': .09,

        'app_start_timeout': 10.,
        'app_start_retry': .90,

        'app_connect_timeout': 5.,
        'app_connect_retry': .1,

        'cpu_usage_interval': .5,
        'cpu_usage_wait_timeout': 20.,

        'exists_timeout': .5,
        'exists_retry': .3,

        'after_click_wait': .09,
        'after_clickinput_wait': .09,

        'after_menu_wait': .1,

        'after_sendkeys_key_wait': .01,

        'after_button_click_wait': 0,

        'before_closeclick_wait': .1,
        'closeclick_retry': .05,
        'closeclick_dialog_close_wait': 2.,
        'after_closeclick_wait': .2,

        'after_windowclose_timeout': 2,
        'after_windowclose_retry': .5,

        'after_setfocus_wait': .06,
        'setfocus_timeout': 2,
        'setfocus_retry': .1,

        'after_setcursorpos_wait': .01,

        'sendmessagetimeout_timeout': .01,

        'after_tabselect_wait': .05,

        'after_listviewselect_wait': .01,
        'after_listviewcheck_wait': .001,
        'listviewitemcontrol_timeout': 1.5,

        'after_treeviewselect_wait': .1,

        'after_toobarpressbutton_wait': .01,

        'after_updownchange_wait': .1,

        'after_movewindow_wait': 0,
        'after_buttoncheck_wait': 0,
        'after_comboboxselect_wait': 0.001,
        'after_listboxselect_wait': 0,
        'after_listboxfocuschange_wait': 0,
        'after_editsetedittext_wait': 0,
        'after_editselect_wait': 0.02,
        'drag_n_drop_move_mouse_wait': 0.1,
        'before_drag_wait': 0.2,
        'before_drop_wait': 0.1,
        'after_drag_n_drop_wait': 0.1,
        'scroll_step_wait': 0.1,

        'app_exit_timeout': 10.,
        'app_exit_retry': .1,
    }

    assert(__default_timing['window_find_timeout'] >=
           __default_timing['window_find_retry'] * 2)

    _timings = __default_timing.copy()
    _cur_speed = 1

    def __getattribute__(self, attr):
        """Get the value for a particular timing"""
        if attr in ['__dict__', '__members__', '__methods__', '__class__']:
            return object.__getattribute__(self, attr)

        if attr in dir(TimeConfig):
            return object.__getattribute__(self, attr)

        if attr in self.__default_timing:
            return self._timings[attr]
        else:
            raise AttributeError("Unknown timing setting: {0}".format(attr))

    def __setattr__(self, attr, value):
        """Set a particular timing"""
        if attr == '_timings':
            object.__setattr__(self, attr, value)
        elif attr in self.__default_timing:
            self._timings[attr] = value
        else:
            raise AttributeError("Unknown timing setting: {0}".format(attr))

    def fast(self):
        """Set fast timing values

        Currently this changes the timing in the following ways:
        timeouts = 1 second
        waits = 0 seconds
        retries = .001 seconds (minimum!)

        (if existing times are faster then keep existing times)
        """

        for setting in self.__default_timing:
            # set timeouts to the min of the current speed or 1 second
            if "_timeout" in setting:
                self._timings[setting] = \
                    min(1, self._timings[setting])

            if "_wait" in setting:
                self._timings[setting] = self._timings[setting] / 2

            elif setting.endswith("_retry"):
                self._timings[setting] = 0.001

            #self._timings['app_start_timeout'] = .5

    def slow(self):
        """Set slow timing values

        Currently this changes the timing in the following ways:
        timeouts = default timeouts * 10
        waits = default waits * 3
        retries = default retries * 3

        (if existing times are slower then keep existing times)
        """
        for setting in self.__default_timing:
            if "_timeout" in setting:
                self._timings[setting] = max(
                    self.__default_timing[setting] * 10,
                    self._timings[setting])

            if "_wait" in setting:
                self._timings[setting] = max(
                    self.__default_timing[setting] * 3,
                    self._timings[setting])

            elif setting.endswith("_retry"):
                self._timings[setting] = max(
                    self.__default_timing[setting] * 3,
                    self._timings[setting])

            if self._timings[setting] < .2:
                self._timings[setting] = .2

    def defaults(self):
        """Set all timings to the default time"""
        self._timings = self.__default_timing.copy()

    Fast = deprecated(fast)
    Slow = deprecated(slow)
    Defaults = deprecated(defaults)


Timings = TimeConfig()


#=========================================================================
class TimeoutError(RuntimeError):
    pass


#=========================================================================
if six.PY3:
    _clock_func = time.perf_counter
else:
    _clock_func = time.clock


def timestamp():
    """Get a precise timestamp"""
    return _clock_func()


#=========================================================================
def always_wait_until(timeout,
                      retry_interval,
                      value=True,
                      op=operator.eq):
    """Decorator to call wait_until(...) every time for a decorated function/method"""
    def wait_until_decorator(func):
        """Callable object that must be returned by the @always_wait_until decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """pre-callback, target function call and post-callback"""
            return wait_until(timeout, retry_interval,
                              func, value, op, *args, **kwargs)
        return wrapper
    return wait_until_decorator


#=========================================================================
def wait_until(timeout,
               retry_interval,
               func,
               value=True,
               op=operator.eq,
               *args, **kwargs):
    r"""
    Wait until ``op(function(*args, **kwargs), value)`` is True or until timeout expires

    * **timeout**  how long the function will try the function
    * **retry_interval**  how long to wait between retries
    * **func** the function that will be executed
    * **value**  the value to be compared against (defaults to True)
    * **op** the comparison function (defaults to equality)\
    * **args** optional arguments to be passed to func when called
    * **kwargs** optional keyword arguments to be passed to func when called

    Returns the return value of the function
    If the operation times out then the return value of the the function
    is in the 'function_value' attribute of the raised exception.

    e.g. ::

        try:
            # wait a maximum of 10.5 seconds for the
            # the objects item_count() method to return 10
            # in increments of .5 of a second
            wait_until(10.5, .5, self.item_count, 10)
        except TimeoutError as e:
            print("timed out")
    """
    start = timestamp()

    func_val = func(*args, **kwargs)
    # while the function hasn't returned what we are waiting for
    while not op(func_val, value):

        # find out how much of the time is left
        time_left = timeout - (timestamp() - start)

        # if we have to wait some more
        if time_left > 0:
            # wait either the retry_interval or else the amount of
            # time until the timeout expires (whichever is less)
            time.sleep(min(retry_interval, time_left))
            func_val = func(*args, **kwargs)
        else:
            err = TimeoutError("timed out")
            err.function_value = func_val
            raise err

    return func_val

# Non PEP-8 alias
WaitUntil = deprecated(wait_until)


#=========================================================================
def always_wait_until_passes(timeout,
                             retry_interval,
                             exceptions=(Exception)):
    """Decorator to call wait_until_passes(...) every time for a decorated function/method"""
    def wait_until_passes_decorator(func):
        """Callable object that must be returned by the @always_wait_until_passes decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """pre-callback, target function call and post-callback"""
            return wait_until_passes(timeout, retry_interval,
                                     func, exceptions, *args, **kwargs)
        return wrapper
    return wait_until_passes_decorator


#=========================================================================
def wait_until_passes(timeout,
                      retry_interval,
                      func,
                      exceptions=(Exception),
                      *args, **kwargs):
    """
    Wait until ``func(*args, **kwargs)`` does not raise one of the exceptions

    * **timeout**  how long the function will try the function
    * **retry_interval**  how long to wait between retries
    * **func** the function that will be executed
    * **exceptions**  list of exceptions to test against (default: Exception)
    * **args** optional arguments to be passed to func when called
    * **kwargs** optional keyword arguments to be passed to func when called

    Returns the return value of the function
    If the operation times out then the original exception raised is in
    the 'original_exception' attribute of the raised exception.

    e.g. ::

        try:
            # wait a maximum of 10.5 seconds for the
            # window to be found in increments of .5 of a second.
            # P.int a message and re-raise the original exception if never found.
            wait_until_passes(10.5, .5, self.Exists, (ElementNotFoundError))
        except TimeoutError as e:
            print("timed out")
            raise e.
    """
    start = timestamp()

    # keep trying until the timeout is passed
    while True:
        try:
            # Call the function with any arguments
            func_val = func(*args, **kwargs)

            # if no exception is raised then we are finished
            break

        # An exception was raised - so wait and try again
        except exceptions as e:

            # find out how much of the time is left
            time_left = timeout - (timestamp() - start)

            # if we have to wait some more
            if time_left > 0:
                # wait either the retry_interval or else the amount of
                # time until the timeout expires (whichever is less)
                time.sleep(min(retry_interval, time_left))

            else:
                # Raise a TimeoutError - and put the original exception
                # inside it
                err = TimeoutError()
                err.original_exception = e
                raise err

    # return the function value
    return func_val

# Non PEP-8 alias
WaitUntilPasses = deprecated(wait_until_passes)
