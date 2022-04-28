"""Wrap various WPF windows controls. To be used with 'wpf' backend."""
import locale
import time
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


class EditWrapper(wpfwrapper.WPFWrapper):

    """Wrap an Edit control"""

    _control_types = ['Edit']
    has_title = False

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(EditWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(EditWrapper, self).writable_props
        props.extend(['selection_indices'])
        return props

    # -----------------------------------------------------------
    def line_count(self):
        """Return how many lines there are in the Edit"""
        return self.window_text().count("\n") + 1

    # -----------------------------------------------------------
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

    # -----------------------------------------------------------
    def get_line(self, line_index):
        """Return the line specified"""
        lines = self.window_text().splitlines()
        if line_index < len(lines):
            return lines[line_index]
        elif line_index == self.line_count() - 1:
            return ""
        else:
            raise IndexError("There are only {0} lines but given index is {1}".format(self.line_count(), line_index))

    # -----------------------------------------------------------
    def get_value(self):
        """Return the current value of the element"""
        return self.get_property('Text') or ''

    # -----------------------------------------------------------
    def is_editable(self):
        """Return the edit possibility of the element"""
        return not self.get_property('IsReadOnly')

    # -----------------------------------------------------------
    def texts(self):
        """Get the text of the edit control"""
        texts = [ self.get_line(i) for i in range(self.line_count()) ]

        return texts

    # -----------------------------------------------------------
    def text_block(self):
        """Get the text of the edit control"""
        return self.window_text()

    # -----------------------------------------------------------
    def selection_indices(self):
        """The start and end indices of the current selection"""
        start = self.get_property('SelectionStart')
        end = start + self.get_property('SelectionLength')

        return start, end

    # -----------------------------------------------------------
    def set_window_text(self, text, append=False):
        """Override set_window_text for edit controls because it should not be
        used for Edit controls.

        Edit Controls should either use set_edit_text() or type_keys() to modify
        the contents of the edit control.
        """
        self.verify_actionable()

        if append:
            text = self.window_text() + text

        self.set_property('Text', text)

    # -----------------------------------------------------------
    def set_edit_text(self, text, pos_start=None, pos_end=None):
        """Set the text of the edit control"""
        self.verify_actionable()

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

        self.set_property('Text', new_text)

        # time.sleep(Timings.after_editsetedittext_wait)

        if isinstance(aligned_text, six.text_type):
            self.actions.log('Set text to the edit box: ' + aligned_text)
        else:
            self.actions.log(b'Set text to the edit box: ' + aligned_text)

        # return this control so that actions can be chained.
        return self
    # set set_text as an alias to set_edit_text
    set_text = set_edit_text

    # -----------------------------------------------------------
    def select(self, start=0, end=None):
        """Set the edit selection of the edit control"""
        self.verify_actionable()
        self.set_focus()

        if isinstance(start, six.integer_types):
            if isinstance(end, six.integer_types) and start > end:
                start, end = end, start
            elif end is None:
                end = len(self.window_text())
        else:
            # if we have been asked to select a string
            if isinstance(start, six.text_type):
                string_to_select = start
            elif isinstance(start, six.binary_type):
                string_to_select = start.decode(locale.getpreferredencoding())
            else:
                raise ValueError('start and end should be integer or string')

            start = self.window_text().find(string_to_select)
            if start < 0:
                raise RuntimeError("Text '{0}' hasn't been found".format(string_to_select))
            end = start + len(string_to_select)

        self.set_property('SelectionStart', start)
        self.set_property('SelectionLength', end-start)

        # return this control so that actions can be chained.
        return self


class TabControlWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF Tab control"""

    _control_types = ['Tab']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(TabControlWrapper, self).__init__(elem)

    # ----------------------------------------------------------------
    def get_selected_tab(self):
        """Return an index of a selected tab"""
        return self.get_property('SelectedIndex')

    # ----------------------------------------------------------------
    def tab_count(self):
        """Return a number of tabs"""
        return len(self.children())

    # ----------------------------------------------------------------
    def select(self, item):
        """Select a tab by index or by name"""
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

    # ----------------------------------------------------------------
    def texts(self):
        """Tabs texts"""
        return self.children_texts()


class SliderWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF Slider control"""

    _control_types = ['Slider']
    has_title = False

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(SliderWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def min_value(self):
        """Get the minimum value of the Slider"""
        return self.get_property('Minimum')

    # -----------------------------------------------------------
    def max_value(self):
        """Get the maximum value of the Slider"""
        return self.get_property('Maximum')

    # -----------------------------------------------------------
    def small_change(self):
        """
        Get a small change of slider's thumb

        This change is achieved by pressing left and right arrows
        when slider's thumb has keyboard focus.
        """
        return self.get_property('SmallChange')

    # -----------------------------------------------------------
    def large_change(self):
        """
        Get a large change of slider's thumb

        This change is achieved by pressing PgUp and PgDown keys
        when slider's thumb has keyboard focus.
        """
        return self.get_property('LargeChange')

    # -----------------------------------------------------------
    def value(self):
        """Get a current position of slider's thumb"""
        return self.get_property('Value')

    # -----------------------------------------------------------
    def set_value(self, value):
        """Set position of slider's thumb"""
        if isinstance(value, float):
            value_to_set = value
        elif isinstance(value, six.integer_types):
            value_to_set = value
        elif isinstance(value, six.text_type):
            value_to_set = float(value)
        else:
            raise ValueError("value should be either string or number")

        min_value = self.min_value()
        max_value = self.max_value()
        if not (min_value <= value_to_set <= max_value):
            raise ValueError("value should be bigger than {0} and smaller than {1}".format(min_value, max_value))

        self.set_property('Value', value_to_set)


class ToolbarWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF ToolBar control

    The control's children usually are: Buttons, SplitButton,
    MenuItems, ThumbControls, TextControls, Separators, CheckBoxes.
    Notice that ToolTip controls are children of the top window and
    not of the toolbar.
    """

    _control_types = ['ToolBar']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ToolbarWrapper, self).__init__(elem)
        self.win32_wrapper = None
        if len(self.children()) <= 1 and self.element_info.handle is not None:
            self.win32_wrapper = common_controls.ToolbarWrapper(self.element_info.handle)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ToolbarWrapper, self).writable_props
        props.extend(['button_count'])
        return props

    # ----------------------------------------------------------------
    def texts(self):
        """Return texts of the Toolbar"""
        return [c.window_text() for c in self.buttons()]

    #----------------------------------------------------------------
    def button_count(self):
        """Return a number of buttons on the ToolBar"""
        return len(self.children())

    # ----------------------------------------------------------------
    def buttons(self):
        """Return all available buttons"""
        return self.children()

    # ----------------------------------------------------------------
    def button(self, button_identifier, exact=True):
        """Return a button by the specified identifier

        * **button_identifier** can be either an index of a button or
          a string with the text of the button.
        * **exact** flag specifies if the exact match for the text look up
          has to be applied.
        """
        cc = self.buttons()
        texts = [c.window_text() for c in cc]

        if isinstance(button_identifier, six.string_types):
            self.actions.log('Toolbar buttons: ' + str(texts))

            if exact:
                try:
                    button_index = texts.index(button_identifier)
                except ValueError:
                    raise findbestmatch.MatchError(items=texts, tofind=button_identifier)
            else:
                # one of these will be returned for the matching text
                indices = [i for i in range(0, len(texts))]

                # find which index best matches that text
                button_index = findbestmatch.find_best_match(button_identifier, texts, indices)
        else:
            button_index = button_identifier

        return cc[button_index]

    # ----------------------------------------------------------------
    def check_button(self, button_identifier, make_checked, exact=True):
        """Find where the button is and toggle it

        * **button_identifier** can be either an index of the button or
          a string with the text on the button.
        * **make_checked** specifies the required toggled state of the button.
          If the button is already in the specified state the state isn't changed.
        * **exact** flag specifies if the exact match for the text look up
          has to be applied
        """

        self.actions.logSectionStart('Checking "' + self.window_text() +
                                     '" toolbar button "' + str(button_identifier) + '"')
        button = self.button(button_identifier, exact=exact)
        if make_checked:
            self.actions.log('Pressing down toolbar button "' + str(button_identifier) + '"')
        else:
            self.actions.log('Pressing up toolbar button "' + str(button_identifier) + '"')

        if not button.is_enabled():
            self.actions.log('Toolbar button is not enabled!')
            raise RuntimeError("Toolbar button is not enabled!")

        res = (button.get_toggle_state() == ButtonWrapper.CHECKED)
        if res != make_checked:
            button.toggle()

        self.actions.logSectionEnd()
        return button

    def collapse(self):
        """Collapse overflow area of the ToolBar (IsOverflowOpen property)"""
        self.set_property('IsOverflowOpen', False)

    def expand(self):
        """Expand overflow area of the ToolBar (IsOverflowOpen property)"""
        self.set_property('IsOverflowOpen', True)

    def is_expanded(self):
        """Check if the ToolBar overflow area is currently visible"""
        return not self.get_property('HasOverflowItems') or self.get_property('IsOverflowOpen')

    def is_collapsed(self):
        """Check if the ToolBar overflow area is not visible"""
        return not self.is_expanded()


class MenuItemWrapper(wpfwrapper.WPFWrapper):

    """Wrap an UIA-compatible MenuItem control"""

    _control_types = ['MenuItem']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(MenuItemWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def items(self):
        """Find all items of the menu item"""
        return self.children(control_type="MenuItem")

    # -----------------------------------------------------------
    def select(self):
        """Select Menu item by raising Click event"""
        self.raise_event('Click')


class MenuWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF MenuBar or Menu control"""

    _control_types = ['Menu']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(MenuWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def items(self):
        """Find all menu items"""
        return self.children(control_type="MenuItem")

    # -----------------------------------------------------------
    def item_by_index(self, idx):
        """Find a menu item specified by the index"""
        item = self.items()[idx]
        return item

    # -----------------------------------------------------------
    def _activate(self, item):
        """Activate the specified item"""
        if not item.is_active():
            item.set_focus()
        item.set_property('IsSubmenuOpen', True)

    # -----------------------------------------------------------
    def _sub_item_by_text(self, menu, name, exact, is_last):
        """Find a menu sub-item by the specified text"""
        sub_item = None
        items = menu.items()
        if items:
            if exact:
                for i in items:
                    if name == i.window_text():
                        sub_item = i
                        break
            else:
                texts = []
                for i in items:
                    texts.append(i.window_text())
                sub_item = findbestmatch.find_best_match(name, texts, items)

        if sub_item is None:
            raise IndexError('Item `{}` not found'.format(name))

        self._activate(sub_item)
        return sub_item

    # -----------------------------------------------------------
    def _sub_item_by_idx(self, menu, idx, is_last):
        """Find a menu sub-item by the specified index"""
        sub_item = None
        items = menu.items()
        if items:
            sub_item = items[idx]

        if sub_item is None:
            raise IndexError('Item with index {} not found'.format(idx))

        self._activate(sub_item)
        return sub_item

    # -----------------------------------------------------------
    def item_by_path(self, path, exact=False):
        """Find a menu item specified by the path

        The full path syntax is specified in:
        :py:meth:`.controls.menuwrapper.Menu.get_menu_path`

        Note: $ - specifier is not supported
        """
        # Get the path parts
        menu_items = [p.strip() for p in path.split("->")]
        items_cnt = len(menu_items)
        if items_cnt == 0:
            raise IndexError()
        for item in menu_items:
            if not item:
                raise IndexError("Empty item name between '->' separators")

        def next_level_menu(parent_menu, item_name, is_last):
            if item_name.startswith("#"):
                return self._sub_item_by_idx(parent_menu, int(item_name[1:]), is_last)
            else:
                return self._sub_item_by_text(parent_menu, item_name, exact, is_last)

        # Find a top level menu item and select it. After selecting this item
        # a new Menu control is created and placed on the dialog. It can be
        # a direct child or a descendant.
        # Sometimes we need to re-discover Menu again
        try:
            menu = next_level_menu(self, menu_items[0], items_cnt == 1)
            if items_cnt == 1:
                return menu

            if not menu.items():
                self._activate(menu)
                timings.wait_until(
                    timings.Timings.window_find_timeout,
                    timings.Timings.window_find_retry,
                    lambda: len(self.top_level_parent().descendants(control_type="Menu")) > 0)
                menu = self.top_level_parent().descendants(control_type="Menu")[0]

            for i in range(1, items_cnt):
                menu = next_level_menu(menu, menu_items[i], items_cnt == i + 1)
        except AttributeError:
            raise IndexError()

        return menu
