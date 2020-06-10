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
import ctypes
import locale
import re
import time
import win32gui
import win32con
import win32api
import win32ui
import six
import sys

try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None

from . import keyboard
from . import win32defines, win32structures, win32functions
from .timings import Timings
from .actionlogger import ActionLogger
from .mouse import _perform_click_input


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

    def __hash__(self):
        """Returns the hash value of the handle"""
        # Must be implemented in a sub-class
        raise NotImplementedError()

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

        Quite a few contorls have other text that is visible, for example
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
        for it to become hidden) use ``Application.wait('visible')`` or
        ``Application.wait_not('visible')``.

        If you want to raise an exception immediately if an element is
        not visible then you can use the BaseWrapper.verify_visible().
        BaseWrapper.verify_actionable() raises if the element is not both
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
        for it to become disabled) use ``Application.wait('visible')`` or
        ``Application.wait_not('visible')``.

        If you want to raise an exception immediately if an element is
        not enabled then you can use the BaseWrapper.verify_enabled().
        BaseWrapper.VerifyReady() raises if the window is not both
        visible and enabled.
        """
        return self.element_info.enabled #and self.top_level_parent().element_info.enabled

    # -----------------------------------------------------------
    def was_maximized(self):
        """Indicate whether the window was maximized before minimizing or not"""
        if self.handle:
            (flags, _, _, _, _) = win32gui.GetWindowPlacement(self.handle)
            return (flags & win32con.WPF_RESTORETOMAXIMIZED == win32con.WPF_RESTORETOMAXIMIZED)
        else:
            return None

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
        if isinstance(client_point, win32structures.POINT):
            return (client_point.x + rect.left, client_point.y + rect.top)
        else:
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
            parent = self.parent()

            if parent:
                if self.parent() == self.root():
                    self._cache["top_level_parent"] = self
                else:
                    return self.parent().top_level_parent()
            else:
                self._cache["top_level_parent"] = self

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
        width = control_rectangle.width()
        height = control_rectangle.height()
        left = control_rectangle.left
        right = control_rectangle.right
        top = control_rectangle.top
        bottom = control_rectangle.bottom
        box = (left, top, right, bottom)

        # check the number of monitors connected
        if (sys.platform == 'win32') and (len(win32api.EnumDisplayMonitors()) > 1):
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
        else:
            # grab the image and get raw data as a string
            pil_img_obj = ImageGrab.grab(box)

        return pil_img_obj

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
    def is_child(self, parent):
        """
        Return True if this element is a child of 'parent'.

        An element is a child of another element when it is a direct of the
        other element. An element is a direct descendant of a given
        element if the parent element is the the chain of parent elements
        for the child element.
        """
        return self in parent.children(class_name = self.class_name())

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
                message = 'Moved mouse over {} "{}" to screen point ('.format(
                    self.friendly_class_name(), ctrl_text)
            else:
                message = 'Clicked {} "{}" by {} button mouse click at '.format(
                    self.friendly_class_name(), ctrl_text, button)
                if double:
                    message = 'Double-c' + message[1:]
            message += str(tuple(coords))

        _perform_click_input(button, coords, double, button_down, button_up,
                             wheel_dist=wheel_dist, pressed=pressed,
                             key_down=key_down, key_up=key_up)

        if message:
            self.actions.log(message)

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
    def move_mouse_input(self, coords=(0, 0), pressed="", absolute=True):
        """Move the mouse"""
        if not absolute:
            self.actions.log('Moving mouse to relative (client) coordinates ' + str(coords).replace('\n', ', '))

        self.click_input(button='move', coords=coords, absolute=absolute, pressed=pressed)

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

        if isinstance(src, BaseWrapper):
            press_coords = src._calc_click_coords()
        elif isinstance(src, win32structures.POINT):
            press_coords = (src.x, src.y)
        else:
            press_coords = src

        if isinstance(dst, BaseWrapper):
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

#====================================================================
