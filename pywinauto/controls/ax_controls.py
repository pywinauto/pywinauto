# -*- coding: utf-8 -*-
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

"""Wrap various macos controls. It is used with 'ax' backend"""
import six

from . import ax_wrapper
from ..macos.macos_functions import get_list_of_actions
from ..macos.macos_functions import perform_action
from ..macos.macos_functions import set_ax_attribute

class ButtonWrapper(ax_wrapper.AXWrapper):

    """Wraps all kind of ax button controls"""
    # All actions should be tested

    _control_types = [
    	'Button',
		'PopUpButton',
		'RadioButton',
        'CheckBox',
        'MenuButton',
        'MenuItem'
    ]

    def __init__(self, elem):
        """Initialize the control"""
        self.click_action_names = ["AXPress"]
        super(ButtonWrapper, self).__init__(elem)

    def click(self):
        """Click the Button control"""
        ref = self.element_info.ref
        action_to_perform = None
        for action in get_list_of_actions(ref):
            if action in self.click_action_names:
                action_to_perform = action
                break
        if action_to_perform:
            perform_action(ref,action_to_perform)

    def toggle(self):
        """Method to change toggle button state

        Currently, just a wrapper around the click() method
        """
        return self.click()

    def get_toggle_state(self):
        """Get a toggle state of a radio button control"""
        return self.element_info.value

    def is_dialog(self):
        """Buttons are never dialogs so return False"""
        return False

    def is_window_managment_button(self):
        """Return true for full screen, minimize, close buttons"""
        subtypes = ['AXCloseButton', 'AXMinimizeButton' ,'AXCloseButton']
        return self.element_info.subrole in subtypes

class ImageWrapper(ax_wrapper.AXWrapper):

    """Wrap image controls"""

    _control_types = ['Image']

    def __init__(self, elem):
        """Initialize the control"""
        super(ImageWrapper, self).__init__(elem)

    @property
    def description(self):
        """Get image description"""
        return self.element_info.description

    @property
    def size(self):
        """Get image size. Return a tuple with width and height"""
        frame = self.element_info.frame
        return (frame.width, frame.height)

    @property
    def bounding_box(self):
        """Get image bounding box"""
        return self.element_info.frame

    @property
    def position(self):
        """Get image position coordinates"""
        return self.element_info.position

class ComboBoxWrapper(ax_wrapper.AXWrapper):

    """Wrap AX ComboBox control"""

    _control_types = ['ComboBox']

    def __init__(self, elem):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(elem)

    def expand(self):
        """Drop down list of items of the control"""
        if not self.is_expanded:
            set_ax_attribute(self.element_info.ref, 'AXExpanded', True)

    def collapse(self):
        """Hide list of items of the control"""
        if self.is_expanded:
            set_ax_attribute(self.element_info.ref, 'AXExpanded', False)

    def confirm(self):
        """Confirms entered value"""
        perform_action(self.element_info.ref, 'AXConfirm')

    @property
    def texts(self):
        """
        Get texts of all items in the control as list
        Combobox UI elements structure:
        -AXComboBox
        --AXButton(expand button)
        --AXScrollArea(visible ONLY if combobox is expanded)
        ---AXList
        ----AXTextField(1st option)
        ----AXTextField(2nd option)
        ---- *******
        ----AXTextField(last option)
        
        Note: there is only one way to find all options:
        1.Expand the combobox.
        2.Find scroll area
        3.Find List
        4.Grep textfield values
        5.Collapse the combox if needed
        """
        is_expanded_on_start = self.is_expanded
        self.expand()
        texts = []
        for option in self.descendants(control_type='TextField'):
            texts.append(option.window_text())
        if not is_expanded_on_start:
            self.collapse()
        return texts

    @property
    def is_expanded(self):
        """Test if the control is expanded"""
        return self.element_info.is_expanded

    @property
    def selected_text(self):
        """Return the selected text"""
        return self.element_info.name

    @property
    def selected_index(self):
        """Return the selected index"""
        return self.texts.index(self.selected_text)

    @property
    def item_count(self):
        """Number of items in the control"""
        return len(self.texts)

    def select(self, item):
        """Select the control item.

        Item can be specified as string or as index
        """
        self.expand()
        if isinstance(item, six.string_types):
            if item in self.texts:
                set_ax_attribute(self.element_info.ref,'AXValue',item)
        else:
            if item < self.item_count:
                text = self.texts[item]
                set_ax_attribute(self.element_info.ref,'AXValue',text)
            else:
                raise IndexError('Item number #{} is out of range '
                                 '({} items in total)'.format(item, self.item_count))

        self.collapse()
        return self
    