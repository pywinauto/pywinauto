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

"""Base class for all wrappers in all backends"""
from __future__ import unicode_literals
from __future__ import print_function

import abc
import locale
import re
import sys

import six

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

from time import sleep
from .actionlogger import ActionLogger
from .mouse import _get_cursor_pos
from .timings import TimeoutError
from .timings import Timings
from .timings import wait_until


#=========================================================================
def remove_non_alphanumeric_symbols(s):
    """Make text usable for attribute name"""
    return re.sub(r"\W", "_", s)

#=========================================================================
class InvalidElement(RuntimeError):

    """Raises when an invalid element is passed"""
    pass

#=========================================================================
class ElementNotEnabled(RuntimeError):

    """Raised when an element is not enabled"""
    pass

#=========================================================================
class ElementNotVisible(RuntimeError):

    """Raised when an element is not visible"""
    pass

#=========================================================================
class ElementNotActive(RuntimeError):

    """Raised when an element is not active"""
    pass

#=========================================================================
@six.add_metaclass(abc.ABCMeta)
class BaseMeta(abc.ABCMeta):

    """Abstract metaclass for Wrapper objects"""

    @staticmethod
    def find_wrapper(element):
        """Abstract static method to find an appropriate wrapper"""
        raise NotImplementedError()

#=========================================================================
@six.add_metaclass(BaseMeta)
class BaseWrapper(object):
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
    def __new__(cls, element_info, active_backend):
        return BaseWrapper._create_wrapper(cls, element_info, BaseWrapper)

    #------------------------------------------------------------
    @staticmethod
    def _create_wrapper(cls_spec, element_info, myself):
        """Create a wrapper object according to the specified element info"""
        # only use the meta class to find the wrapper for BaseWrapper
        # so allow users to force the wrapper if they want
        if cls_spec != myself:
            obj = object.__new__(cls_spec)
            obj.__init__(element_info)
            return obj

        new_class = cls_spec.find_wrapper(element_info)
        obj = object.__new__(new_class)

        obj.__init__(element_info)

        return obj

    #------------------------------------------------------------
    def __init__(self, element_info, active_backend):
        """
        Initialize the element

        * **element_info** is instance of int or one of ElementInfo childs
        """
        self.backend = active_backend
        if element_info:
            #if isinstance(element_info, six.integer_types):
            #    element_info = self.backend.element_info_class(element_info)

            self._element_info = element_info

            self.handle = self._element_info.handle
            self._as_parameter_ = self.handle

            self.ref = None
            self.appdata = None
            self._cache = {}
            self.actions = ActionLogger()
        else:
            raise RuntimeError('NULL pointer was used to initialize BaseWrapper')

    def by(self, **criteria):
        """
        Create WindowSpecification for search in descendants by criteria

        Current wrapper object is used as a parent while searching in the subtree.
        """
        from .base_application import WindowSpecification
        # default to non top level windows because we are usually
        # looking for a control
        if 'top_level_only' not in criteria:
            criteria['top_level_only'] = False

        criteria['backend'] = self.backend.name
        criteria['parent'] = self.element_info
        child_specification = WindowSpecification(criteria)

        return child_specification

    def __repr_texts(self):
        """Internal common method to be called from __str__ and __repr__"""
        module = self.__class__.__module__
        module = module[module.rfind('.') + 1:]

        type_name = module + "." + self.__class__.__name__
        title = self.window_text()
        class_name = self.friendly_class_name()
        if six.PY2:
            if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding is not None:
                # some frameworks override sys.stdout without encoding attribute (Tee Stream),
                # some users replace sys.stdout with file descriptor which can have None encoding
                title = title.encode(sys.stdout.encoding, errors='backslashreplace')
            else:
                title = title.encode(locale.getpreferredencoding(), errors='backslashreplace')
        return type_name, title, class_name

    def __repr__(self):
        """Representation of the wrapper object

        The method prints the following info:
        * type name as a module name and a class name of the object
        * title of the control or empty string
        * friendly class name of the control
        * unique ID of the control calculated as a hash value from a backend specific ID.

        Notice that the reported title and class name can be used as hints to prepare
        a windows specification to access the control, while the unique ID is more for
        debugging purposes helping to distinguish between the runtime objects.
        """
        type_name, title, class_name = self.__repr_texts()
        if six.PY2:
            return b"<{0} - '{1}', {2}, {3}>".format(type_name, title, class_name, self.__hash__())
        else:
            return "<{0} - '{1}', {2}, {3}>".format(type_name, title, class_name, self.__hash__())

    def __str__(self):
        """Pretty print representation of the wrapper object

        The method prints the following info:
        * type name as a module name and class name of the object
        * title of the wrapped control or empty string
        * friendly class name of the wrapped control

        Notice that the reported title and class name can be used as hints
        to prepare a window specification to access the control
        """
        type_name, title, class_name = self.__repr_texts()
        if six.PY2:
            return b"{0} - '{1}', {2}".format(type_name, title, class_name)
        else:
            return "{0} - '{1}', {2}".format(type_name, title, class_name)

    #------------------------------------------------------------
    @property
    def writable_props(self):
        """
        Build the list of the default properties to be written.

        Derived classes may override or extend this list depending
        on how much control they need.
        """
        props = ['class_name',
                 'friendly_class_name',
                 'texts',
                 'control_id',
                 'rectangle',
                 'is_visible',
                 'is_enabled',
                 'control_count',
                 ]
        return props

    #------------------------------------------------------------
    @property
    def _needs_image_prop(self):
        """Specify whether we need to grab an image of ourselves

        when asked for properties.
        """
        return False

    #------------------------------------------------------------
    @property
    def element_info(self):
        """Read-only property to get **ElementInfo** object"""
        return self._element_info

    #------------------------------------------------------------
    def from_point(self, x, y):
        """Get wrapper object for element at specified screen coordinates (x, y)"""
        element_info = self.backend.element_info_class.from_point(x, y)
        return self.backend.generic_wrapper_class(element_info)

    #------------------------------------------------------------
    def top_from_point(self, x, y):
        """Get wrapper object for top level element at specified screen coordinates (x, y)"""
        top_element_info = self.backend.element_info_class.top_from_point(x, y)
        return self.backend.generic_wrapper_class(top_element_info)

    #------------------------------------------------------------
    def get_active(self):
        """Get wrapper object for active element"""
        element_info = self.backend.element_info_class.get_active()
        return self.backend.generic_wrapper_class(element_info)

    #------------------------------------------------------------
    def friendly_class_name(self):
        """
        Return the friendly class name for the control

        This differs from the class of the control in some cases.
        class_name() is the actual 'Registered' element class of the control
        while friendly_class_name() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if self.friendlyclassname is None:
            self.friendlyclassname = self.class_name()
        return self.friendlyclassname

    #------------------------------------------------------------
    def class_name(self):
        """Return the class name of the elenemt"""
        return self.element_info.class_name

    #------------------------------------------------------------
    def window_text(self):
        """
        Window text of the element

        Quite a few controls have other text that is visible, for example
        Edit controls usually have an empty string for window_text but still
        have text displayed in the edit window.
        """
        return self.element_info.rich_text

    #------------------------------------------------------------
    def control_id(self):
        """
        Return the ID of the element

        Only controls have a valid ID - dialogs usually have no ID assigned.

        The ID usually identified the control in the window - but there can
        be duplicate ID's for example lables in a dialog may have duplicate
        ID's.
        """
        return self.element_info.control_id

    #------------------------------------------------------------
    def is_visible(self):
        """
        Whether the element is visible or not

        Checks that both the top level parent (probably dialog) that
        owns this element and the element itself are both visible.

        If you want to wait for an element to become visible (or wait
        for it to become hidden) use ``BaseWrapper.wait_visible()`` or
        ``BaseWrapper.wait_not_visible()``.

        If you want to raise an exception immediately if an element is
        not visible then you can use the ``BaseWrapper.verify_visible()``.
        ``BaseWrapper.verify_actionable()`` raises if the element is not both
        visible and enabled.
        """
        return self.element_info.visible #and self.top_level_parent().element_info.visible

    #------------------------------------------------------------
    def is_enabled(self):
        """
        Whether the element is enabled or not

        Checks that both the top level parent (probably dialog) that
        owns this element and the element itself are both enabled.

        If you want to wait for an element to become enabled (or wait
        for it to become disabled) use ``BaseWrapper.wait_enabled()`` or
        ``BaseWrapper.wait_not_enabled()``.

        If you want to raise an exception immediately if an element is
        not enabled then you can use the ``BaseWrapper.verify_enabled()``.
        ``BaseWrapper.VerifyReady()`` raises if the window is not both
        visible and enabled.
        """
        return self.element_info.enabled #and self.top_level_parent().element_info.enabled

    # ------------------------------------------------------------
    def is_active(self):
        """
        Whether the element is active or not

        Checks that both the top level parent (probably dialog) that
        owns this element and the element itself are both active.

        If you want to wait for an element to become active (or wait
        for it to become not active) use ``BaseWrapper.wait_active()`` or
        ``BaseWrapper.wait_not_active()``.

        If you want to raise an exception immediately if an element is
        not active then you can use the ``BaseWrapper.verify_active()``.
        """
        return self.element_info.active

    # -----------------------------------------------------------
    def was_maximized(self):
        """Indicate whether the window was maximized before minimizing or not"""
        raise NotImplementedError

    #------------------------------------------------------------
    def rectangle(self):
        """
        Return the rectangle of element

        The rectangle() is the rectangle of the element on the screen.
        Coordinates are given from the top left of the screen.

        This method returns a RECT structure, Which has attributes - top,
        left, right, bottom. and has methods width() and height().
        See win32structures.RECT for more information.
        """
        return self.element_info.rectangle

    #------------------------------------------------------------
    def client_to_screen(self, client_point):
        """Maps point from client to screen coordinates"""
        # Use a direct call to element_info.rectangle instead of self.rectangle
        # because the latter can be overriden in one of derived wrappers
        # (see _treeview_element.rectangle or _listview_item.rectangle)
        rect = self.element_info.rectangle
        return (client_point[0] + rect.left, client_point[1] + rect.top)

    #-----------------------------------------------------------
    def process_id(self):
        """Return the ID of process that owns this window"""
        return self.element_info.process_id

    #-----------------------------------------------------------
    def is_dialog(self):
        """Return True if the control is a top level window"""
        if self.parent():
            return self == self.top_level_parent()
        else:
            return False

    #-----------------------------------------------------------
    def parent(self):
        """
        Return the parent of this element

        Note that the parent of a control is not necesarily a dialog or
        other main window. A group box may be the parent of some radio
        buttons for example.

        To get the main (or top level) window then use
        BaseWrapper.top_level_parent().
        """
        parent_elem = self.element_info.parent

        if parent_elem:
            return self.backend.generic_wrapper_class(parent_elem)
        else:
            return None

    #-----------------------------------------------------------
    def root(self):
        """Return wrapper for root element (desktop)"""
        return self.backend.generic_wrapper_class(self.backend.element_info_class())

    #-----------------------------------------------------------
    def top_level_parent(self):
        """
        Return the top level window of this control

        The TopLevel parent is different from the parent in that the parent
        is the element that owns this element - but it may not be a dialog/main
        window. For example most Comboboxes have an Edit. The ComboBox is the
        parent of the Edit control.

        This will always return a valid window element (if the control has
        no top level parent then the control itself is returned - as it is
        a top level window already!)
        """
        if not ("top_level_parent" in self._cache.keys()):
            self._cache["top_level_parent"] = self.backend.generic_wrapper_class(self.element_info.top_level_parent)
        return self._cache["top_level_parent"]

    #-----------------------------------------------------------
    def texts(self):
        """
        Return the text for each item of this control

        It is a list of strings for the control. It is frequently overridden
        to extract all strings from a control with multiple items.

        It is always a list with one or more strings:

          * The first element is the window text of the control
          * Subsequent elements contain the text of any items of the
            control (e.g. items in a listbox/combobox, tabs in a tabcontrol)
        """
        texts_list = [self.window_text(), ]
        return texts_list

    #-----------------------------------------------------------
    def children(self, **kwargs):
        """
        Return the children of this element as a list

        It returns a list of BaseWrapper (or subclass) instances.
        An empty list is returned if there are no children.
        """
        child_elements = self.element_info.children(**kwargs)
        return [self.backend.generic_wrapper_class(element_info) for element_info in child_elements]

    #-----------------------------------------------------------
    def iter_children(self, **kwargs):
        """
        Iterate over the children of this element

        It returns a generator of BaseWrapper (or subclass) instances.
        """
        child_elements = self.element_info.iter_children(**kwargs)
        for element_info in child_elements:
            yield self.backend.generic_wrapper_class(element_info)

    #-----------------------------------------------------------
    def descendants(self, **kwargs):
        """
        Return the descendants of this element as a list

        It returns a list of BaseWrapper (or subclass) instances.
        An empty list is returned if there are no descendants.
        """
        desc_elements = self.element_info.descendants(**kwargs)
        return [self.backend.generic_wrapper_class(element_info) for element_info in desc_elements]

    #-----------------------------------------------------------
    def iter_descendants(self, **kwargs):
        """
        Iterate over the descendants of this element

        It returns a generator of BaseWrapper (or subclass) instances.
        """
        desc_elements = self.element_info.iter_descendants(**kwargs)
        for element_info in desc_elements:
            yield self.backend.generic_wrapper_class(element_info)

    #-----------------------------------------------------------
    def control_count(self):
        """Return the number of children of this control"""
        return len(self.element_info.children(process=self.process_id()))

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
            control_rectangle = rect

        # get the control rectangle in a way that PIL likes it
        left = control_rectangle.left
        right = control_rectangle.right
        top = control_rectangle.top
        bottom = control_rectangle.bottom
        box = (left, top, right, bottom)

        # TODO: maybe check the number of monitors on Linux

        # grab the image and get raw data as a string
        return ImageGrab.grab(box)

    #-----------------------------------------------------------
    def get_properties(self):
        """Return the properties of the control as a dictionary."""
        props = {}

        # for each of the properties that can be written out
        for propname in self.writable_props:
            # set the item in the props dictionary keyed on the propname
            props[propname] = getattr(self, propname)()

        if self._needs_image_prop:
            props["image"] = self.capture_as_image()

        return props

    #-----------------------------------------------------------
    def draw_outline(
        self,
        colour='green',
        thickness=2,
        fill=None,
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
        raise NotImplementedError()

    #-----------------------------------------------------------
    def is_child(self, parent):
        """
        Return True if this element is a child of 'parent'.

        An element is a child of another element when it is a direct of the
        other element. An element is a direct descendant of a given
        element if the parent element is the the chain of parent elements
        for the child element.
        """
        return self in parent.children(class_name = self.class_name())

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value based on the element's handle"""
        return self.element_info.__hash__()

    #-----------------------------------------------------------
    def __eq__(self, other):
        """Return True if 2 BaseWrapper's describe 1 actual element"""
        if hasattr(other, "element_info"):
            return self.element_info == other.element_info
        else:
            return self.element_info == other

    #-----------------------------------------------------------
    def __ne__(self, other):
        """Return False if the elements described by 2 BaseWrapper's are different"""
        return not self == other

    #-----------------------------------------------------------
    def verify_actionable(self):
        """
        Verify that the element is both visible and enabled

        Raise either ElementNotEnalbed or ElementNotVisible if not
        enabled or visible respectively.
        """
        self.wait_for_idle()
        self.verify_visible()
        self.verify_enabled()

    #-----------------------------------------------------------
    def verify_enabled(self):
        """
        Verify that the element is enabled

        Check first if the element's parent is enabled (skip if no parent),
        then check if element itself is enabled.
        """
        if not self.is_enabled():
            raise ElementNotEnabled()

    #-----------------------------------------------------------
    def verify_visible(self):
        """
        Verify that the element is visible

        Check first if the element's parent is visible. (skip if no parent),
        then check if element itself is visible.
        """
        if not self.is_visible():
            raise ElementNotVisible()

    # -----------------------------------------------------------
    def verify_active(self):
        """
        Verify that the element is active

        Check first if the element's parent is active. (skip if no parent),
        then check if element itself is active.
        """
        if not self.is_active():
            raise ElementNotActive()

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
        raise NotImplementedError()

    #-----------------------------------------------------------
    def double_click_input(self, button ="left", coords = (None, None)):
        """Double click at the specified coordinates"""
        self.click_input(button, coords, double=True)

    #-----------------------------------------------------------
    def right_click_input(self, coords = (None, None)):
        """Right click at the specified coords"""
        self.click_input(button='right', coords=coords)

    #-----------------------------------------------------------
    def press_mouse_input(
            self,
            button = "left",
            coords = (None, None),
            pressed = "",
            absolute = True,
            key_down = True,
            key_up = True
    ):
        """Press a mouse button using SendInput"""
        self.click_input(
            button=button,
            coords=coords,
            button_down=True,
            button_up=False,
            pressed=pressed,
            absolute=absolute,
            key_down=key_down,
            key_up=key_up
        )

    #-----------------------------------------------------------
    def release_mouse_input(
            self,
            button = "left",
            coords = (None, None),
            pressed = "",
            absolute = True,
            key_down = True,
            key_up = True
    ):
        """Release the mouse button"""
        self.click_input(
            button,
            coords,
            button_down=False,
            button_up=True,
            pressed=pressed,
            absolute=absolute,
            key_down=key_down,
            key_up=key_up
        )

    #-----------------------------------------------------------
    def move_mouse_input(self, coords=(0, 0), pressed="", absolute=True, duration=0.0):
        """Move the mouse"""
        if not absolute:
            self.actions.log('Moving mouse to relative (client) coordinates ' + str(coords).replace('\n', ', '))
            coords = self.client_to_screen(coords)  # make coords absolute

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
                self.click_input(button='move',
                                 coords=(x_start + int(delta_x * step), y_start + int(delta_y * step)),
                                 absolute=True, pressed=pressed, fast_move=True)
                sleep(sleep_amount)
        self.click_input(button='move', coords=coords, absolute=True, pressed=pressed)

        self.wait_for_idle()
        return self

    # -----------------------------------------------------------
    def _calc_click_coords(self):
        """A helper that tries to get click coordinates of the control

        The calculated coordinates are absolute and returned as
        a tuple with x and y values.
        """
        coords = self.rectangle().mid_point()
        return (coords.x, coords.y)

    # -----------------------------------------------------------
    def drag_mouse_input(self,
                         dst=(0, 0),
                         src=None,
                         button="left",
                         pressed="",
                         absolute=True,
                         duration=0.0):
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
        raise NotImplementedError()

    #-----------------------------------------------------------
    def wheel_mouse_input(self, coords = (None, None), wheel_dist = 1, pressed =""):
        """Do mouse wheel"""
        self.click_input(button='wheel', coords=coords, wheel_dist=wheel_dist, pressed=pressed)
        return self

    #-----------------------------------------------------------
    def wait_for_idle(self):
        """Backend specific function to wait for idle state of a thread or a window"""
        pass # do nothing by deafault
        # TODO: implement wait_for_idle for backend="uia"

    #-----------------------------------------------------------
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
        raise NotImplementedError()

    #-----------------------------------------------------------
    def set_focus(self):
        """Set the focus to this element"""
        pass

    # -----------------------------------------------------------
    def wait_visible(self, timeout, retry_interval):
        """
        Wait until control is visible.

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is not visible after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        try:
            wait_until(timeout, retry_interval, self.is_visible)
            return self
        except TimeoutError as e:
            raise e

    # -----------------------------------------------------------
    def wait_not_visible(self, timeout, retry_interval):
        """
        Wait until control is not visible.

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is still visible after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        try:
            wait_until(timeout, retry_interval, self.is_visible, False)
        except TimeoutError as e:
            raise e

    # -----------------------------------------------------------
    def wait_enabled(self, timeout, retry_interval):
        """
        Wait until control is enabled.

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is not enabled after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        try:
            wait_until(timeout, retry_interval, self.is_enabled)
            return self
        except TimeoutError as e:
            raise e

    # -----------------------------------------------------------

    def wait_not_enabled(self, timeout, retry_interval):
        """
        Wait until control is not enabled.

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is still enabled after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            wait_until(timeout, retry_interval, self.is_enabled, False)
        except TimeoutError as e:
            raise e

    # -----------------------------------------------------------
    def wait_active(self, timeout, retry_interval):
        """
        Wait until control is active.

        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is not active after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry
        try:
            wait_until(timeout, retry_interval, self.is_active)
            return self
        except TimeoutError as e:
            raise e

    # -----------------------------------------------------------
    def wait_not_active(self, timeout, retry_interval):
        """
        :param timeout: Raise an :func:`pywinauto.timings.TimeoutError` if the window
            is still active after this number of seconds.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_timeout`.

        :param retry_interval: How long to sleep between each retry.
            Default: :py:attr:`pywinauto.timings.Timings.window_find_retry`.
        """
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            wait_until(timeout, retry_interval, self.is_active, False)
        except TimeoutError as e:
            raise e

#====================================================================
