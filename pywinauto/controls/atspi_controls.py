# -*- coding: utf-8 -*-
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

"""Wrap various ATSPI windows controls"""

import locale
import six

from . import atspiwrapper

# region PATTERNS


class ButtonWrapper(atspiwrapper.AtspiWrapper):

    """Wrap a Atspi-compatible Button, CheckBox or RadioButton control"""

    _control_types = ['PushButton',
                      'CheckBox',
                      'ToggleButton',
                      'RadioButton',
                      'MenuItem',
                      ]

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ButtonWrapper, self).__init__(elem)
        self.action = self.element_info.get_action()

    def click(self):
        """Click the Button control"""
        self.action.do_action_by_name("click")
        return self

    # -----------------------------------------------------------
    def toggle(self):
        """Method to change toggle button state"""
        self.click()

    # -----------------------------------------------------------
    def get_toggle_state(self):
        """Get a toggle state of a check box control"""
        return "STATE_CHECKED" in self.element_info.get_state_set()

    # -----------------------------------------------------------
    def is_dialog(self):
        """Buttons are never dialogs so return False"""
        return False


class ComboBoxWrapper(atspiwrapper.AtspiWrapper):

    """Wrap a AT-SPI ComboBox control"""

    _control_types = ['ComboBox']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(elem)
        self.action = self.element_info.get_action()

    def _press(self):
        self.action.do_action_by_name("press")

    def expand(self):
        if not self.is_expanded():
            self._press()
        return self

    def collapse(self):
        if self.is_expanded():
            self._press()
        return self

    def is_expanded(self):
        """Test if the control is expanded"""
        # Check that hidden element of combobox menu is visible
        return self.children()[0].is_visible()

    def texts(self):
        combo_box_container = self.children()[0]
        texts = []
        for el in combo_box_container.children():
            texts.append(el.window_text())
        return texts

    def selected_text(self):
        """Return the selected text"""
        return self.window_text()

    def selected_index(self):
        """Return the selected index"""
        return self.texts().index(self.selected_text())

    def item_count(self):
        combo_box_container = self.children()[0]
        return combo_box_container.control_count()

    def select(self, item):
        """Select the ComboBox item"""
        self.expand()
        children_lst = self.children(control_type='Menu')
        if len(children_lst) > 0:
            if isinstance(item, six.string_types):
                if self.selected_text() != item:
                    item = children_lst[0].children(title=item)[0]
                    item.click()
            elif self.selected_index() != item:
                items = children_lst[0].children(control_type='MenuItem')
                if item < len(items):
                    items[item].click()
                else:
                    raise IndexError('Item number #{} is out of range ' \
                                     '({} items in total)'.format(item, len(items)))
        # else: TODO: probably raise an exception if there is no children

        self.collapse()
        return self


class EditWrapper(atspiwrapper.AtspiWrapper):

    """Wrap single-line and multiline text edit controls"""

    _control_types = ['Text']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(EditWrapper, self).__init__(elem)

    def is_editable(self):
        """Return the edit possibility of the element"""
        return "STATE_EDITABLE" in self.element_info.get_state_set()

    def window_text(self):
        """Window text of the element"""
        return self.element_info.get_text_property().get_whole_text().decode(locale.getpreferredencoding())

    def text_block(self):
        """Get the text of the edit control"""
        return self.window_text()

    def line_count(self):
        """Return how many lines there are in the Edit"""
        return self.window_text().count("\n") + 1

    def line_length(self, line_index):
        """Return how many characters there are in the line"""
        # need to first get a character index of that line
        lines = self.window_text().splitlines()
        if line_index < len(lines):
            return len(lines[line_index])
        elif line_index == self.line_count() - 1:
            return 0
        else:
            raise IndexError("There are only {0} lines but given index is {1}".format(self.line_count(), line_index))

    def get_line(self, line_index):
        """Return the line specified"""
        lines = self.window_text().splitlines()
        if line_index < len(lines):
            return lines[line_index]
        elif line_index == self.line_count() - 1:
            return ""
        else:
            raise IndexError("There are only {0} lines but given index is {1}".format(self.line_count(), line_index))

    def texts(self):
        """Get the text of the edit control"""
        texts = [self.get_line(i) for i in range(self.line_count())]
        return texts

    def selection_indices(self):
        """The start and end indices of the current selection"""
        return self.element_info.get_text_property().get_selection()

    def set_edit_text(self, text, pos_start=None, pos_end=None):
        """Set the text of the edit control"""
        self.verify_enabled()

        # allow one or both of pos_start and pos_end to be None
        if pos_start is not None or pos_end is not None:
            # if only one has been specified - then set the other
            # to the current selection start or end
            start, end = self.selection_indices()
            if pos_start is None:
                pos_start = start
            if pos_end is None and not isinstance(start, six.string_types):
                pos_end = end
        else:
            pos_start = 0
            pos_end = len(self.window_text())

        if isinstance(text, six.text_type):
            if six.PY3:
                aligned_text = text
            else:
                aligned_text = text.encode(locale.getpreferredencoding())
        elif isinstance(text, six.binary_type):
            if six.PY3:
                aligned_text = text.decode(locale.getpreferredencoding())
            else:
                aligned_text = text
        else:
            # convert a non-string input
            if six.PY3:
                aligned_text = six.text_type(text)
            else:
                aligned_text = six.binary_type(text)

        # Calculate new text value
        current_text = self.window_text()
        new_text = current_text[:pos_start] + aligned_text + current_text[pos_end:]

        self.element_info.get_editable_text_property().set_text(new_text.encode(locale.getpreferredencoding()))

        # return this control so that actions can be chained.
        return self

    # set set_text as an alias to set_edit_text
    set_text = set_edit_text

    def select(self, start=0, end=None):
        """Set the edit selection of the edit control"""
        self.verify_enabled()
        self.set_focus()

        # if we have been asked to select a string
        string_to_select = False
        if isinstance(start, six.text_type):
            string_to_select = start
        elif isinstance(start, six.binary_type):
            string_to_select = start.decode(locale.getpreferredencoding())
        elif isinstance(start, six.integer_types):
            if isinstance(end, six.integer_types) and start > end:
                start, end = end, start

        if string_to_select:
            start = self.window_text().find(string_to_select)
            if start == -1:
                raise RuntimeError("Text '{0}' hasn't been found".format(string_to_select))

            end = start + len(string_to_select)

        self.element_info.get_text_property().add_selection(start, end)

        # return this control so that actions can be chained.
        return self


class ImageWrapper(atspiwrapper.AtspiWrapper):

    """Wrap image controls"""

    _control_types = ['Image', 'Icon']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ImageWrapper, self).__init__(elem)
        self.image = elem.image

    def description(self):
        """Get image description"""
        return self.image.get_description().decode(encoding='UTF-8')

    def locale(self):
        """Get image locale"""
        return self.image.get_locale().decode(encoding='UTF-8')

    def size(self):
        """Get image size. Return a tuple with width and height"""
        pnt = self.image.get_size()
        return (pnt.x, pnt.y)

    def bounding_box(self):
        """Get image bounding box"""
        return self.image.get_extents()

    def position(self):
        """Get image position coordinates"""
        return self.image.get_position()
