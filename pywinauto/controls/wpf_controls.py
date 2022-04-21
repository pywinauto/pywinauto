"""Wrap various WPF windows controls. To be used with 'wpf' backend."""
import locale
import time
import comtypes
import six

from . import wpfwrapper
from . import win32_controls
from . import common_controls
from .. import findbestmatch
from .. import timings
from ..windows.wpf_element_info import WPFElementInfo
from ..windows.injected.api import *


# ====================================================================
class WindowWrapper(wpfwrapper.WPFWrapper):

    """Wrap a WPF Window control"""

    _control_types = ['Window']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(WindowWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def move_window(self, x=None, y=None, width=None, height=None):
        """Move the window to the new coordinates

        * **x** Specifies the new left position of the window.
                Defaults to the current left position of the window.
        * **y** Specifies the new top position of the window.
                Defaults to the current top position of the window.
        * **width** Specifies the new width of the window.
                Defaults to the current width of the window.
        * **height** Specifies the new height of the window.
                Defaults to the current height of the window.
        """
        cur_rect = self.rectangle()

        # if no X is specified - so use current coordinate
        if x is None:
            x = cur_rect.left
        else:
            try:
                y = x.top
                width = x.width()
                height = x.height()
                x = x.left
            except AttributeError:
                pass

        # if no Y is specified - so use current coordinate
        if y is None:
            y = cur_rect.top

        # if no width is specified - so use current width
        if width is None:
            width = cur_rect.width()

        # if no height is specified - so use current height
        if height is None:
            height = cur_rect.height()

        # ask for the window to be moved
        self.set_property('Left', x)
        self.set_property('Top', y)
        self.set_property('Width', width)
        self.set_property('Height', height)

        time.sleep(timings.Timings.after_movewindow_wait)

    # -----------------------------------------------------------
    def is_dialog(self):
        """Window is always a dialog so return True"""
        return True


class ButtonWrapper(wpfwrapper.WPFWrapper):

    """Wrap a UIA-compatible Button, CheckBox or RadioButton control"""

    _control_types = ['Button',
        'CheckBox',
        'RadioButton',
    ]

    UNCHECKED = 0
    CHECKED = 1
    INDETERMINATE = 2

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ButtonWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def toggle(self):
        """
        An interface to Toggle method of the Toggle control pattern.

        Control supporting the Toggle pattern cycles through its
        toggle states in the following order:
        ToggleState_On, ToggleState_Off and,
        if supported, ToggleState_Indeterminate

        Usually applied for the check box control.

        The radio button control does not implement IToggleProvider,
        because it is not capable of cycling through its valid states.
        Toggle a state of a check box control. (Use 'select' method instead)
        Notice, a radio button control isn't supported by UIA.
        https://msdn.microsoft.com/en-us/library/windows/desktop/ee671290(v=vs.85).aspx
        """

        current_state = self.get_property('IsChecked')
        if self.get_property('IsThreeState'):
            states = (True, False, None)
        else:
            states = (True, False)

        if current_state is None and not self.get_property('IsThreeState'):
            next_state = False
        else:
            next_state = states[(states.index(current_state)+1) % len(states)]

        self.set_property('IsChecked', next_state)

        name = self.element_info.name
        control_type = self.element_info.control_type

        if name and control_type:
            self.actions.log('Toggled ' + control_type.lower() + ' "' +  name + '"')
        # Return itself so that action can be chained
        return self

    # -----------------------------------------------------------
    def get_toggle_state(self):
        """
        Get a toggle state of a check box control.

        The toggle state is represented by an integer
        0 - unchecked
        1 - checked
        2 - indeterminate
        """
        val = self.get_property('IsChecked')
        if val is None:
            return self.INDETERMINATE
        return self.CHECKED if val else self.UNCHECKED


    # -----------------------------------------------------------
    def is_dialog(self):
        """Buttons are never dialogs so return False"""
        return False

    # -----------------------------------------------------------
    def click(self):
        """Click the Button control by raising the ButtonBase.Click event"""
        self.raise_event('Click')
        # Return itself so that action can be chained
        return self

    def select(self):
        """Select the item

        Usually applied for controls like: a radio button, a tree view item
        or a list item.
        """
        self.set_property('IsChecked', True)

        name = self.element_info.name
        control_type = self.element_info.control_type
        if name and control_type:
            self.actions.log("Selected " + control_type.lower() + ' "' + name + '"')

        # Return itself so that action can be chained
        return self

    # -----------------------------------------------------------
    def is_selected(self):
        """Indicate that the item is selected or not.

        Usually applied for controls like: a radio button, a tree view item,
        a list item.
        """
        return self.get_property('IsChecked')

class ComboBoxWrapper(wpfwrapper.WPFWrapper):

    """Wrap a UIA CoboBox control"""

    _control_types = ['ComboBox']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def expand(self):
        self.set_property('IsDropDownOpen', True)
        return self

    # -----------------------------------------------------------
    def collapse(self):
        self.set_property('IsDropDownOpen', False)
        return self

    # -----------------------------------------------------------
    def is_editable(self):
        return self.get_property('IsEditable')

    # -----------------------------------------------------------
    def is_expanded(self):
        """Test if the control is expanded"""
        return self.get_property('IsDropDownOpen')

    # -----------------------------------------------------------
    def is_collapsed(self):
        """Test if the control is collapsed"""
        return not self.get_property('IsDropDownOpen')

    # -----------------------------------------------------------
    def texts(self):
        """Return the text of the items in the combobox"""
        return [child.element_info.rich_text for child in self.iter_children()]

    # -----------------------------------------------------------
    def select(self, item):
        """
        Select the ComboBox item

        The item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        if isinstance(item, six.integer_types):
            self.set_property('SelectedIndex', item)
        else:
            index = None
            for i, child in enumerate(self.iter_children()):
                if child.element_info.rich_text == item:
                    index = 1
            if index is None:
                raise ValueError('no such item: {}'.format(item))
            self.set_property('SelectedIndex', index)
        return self

    # -----------------------------------------------------------
    # TODO: add selected_texts for a combobox with a multi-select support
    def selected_text(self):
        """
        Return the selected text or None

        Notice, that in case of multi-select it will be only the text from
        a first selected item
        """
        selected_index = self.get_property('SelectedIndex')
        if selected_index == -1:
            return ''
        return self.children()[selected_index].element_info.rich_text

    # -----------------------------------------------------------
    # TODO: add selected_indices for a combobox with multi-select support
    def selected_index(self):
        """Return the selected index"""
        return self.get_property('SelectedIndex')


    # -----------------------------------------------------------
    def item_count(self):
        """
        Return the number of items in the combobox

        The interface is kept mostly for a backward compatibility with
        the native ComboBox interface
        """
        return len(self.children())