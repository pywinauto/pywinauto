"""Wrap various WPF windows controls. To be used with 'wpf' backend."""
import locale
import time
import six

from . import wpfwrapper
from . import common_controls
from .. import findbestmatch
from .. import timings


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

    """Wrap a WPF Button, CheckBox or RadioButton control"""

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
        Switch state of checkable controls in cycle between CHECKED/UNCHECKED or
        CHECKED/UNCHECKED/INDETERMINATE (if a control is  three-state)

        Usually applied for the check box control.
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

    """Wrap a WPF CoboBox control"""

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

    """Wrap an WPF MenuItem control"""

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


class TreeItemWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF TreeItem control

    In addition to the provided methods of the wrapper
    additional inherited methods can be especially helpful:
    select(), extend(), collapse(), is_extended(), is_collapsed(),
    click_input(), rectangle() and many others
    """

    _control_types = ['TreeItem']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(TreeItemWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def ensure_visible(self):
        """Make sure that the TreeView item is visible"""
        self.invoke_method('BringIntoView')

    # -----------------------------------------------------------
    def get_child(self, child_spec, exact=False):
        """Return the child item of this item

        Accepts either a string or an index.
        If a string is passed then it returns the child item
        with the best match for the string.
        """
        cc = self.children(control_type='TreeItem')
        if isinstance(child_spec, six.string_types):
            texts = [c.window_text() for c in cc]
            if exact:
                if child_spec in texts:
                    index = texts.index(child_spec)
                else:
                    raise IndexError('There is no child equal to "' + str(child_spec) + '" in ' + str(texts))
            else:
                indices = range(0, len(texts))
                index = findbestmatch.find_best_match(
                    child_spec, texts, indices, limit_ratio=.6)

        else:
            index = child_spec

        return cc[index]

    # -----------------------------------------------------------
    def _calc_click_coords(self):
        """Override the BaseWrapper helper method

        Set coordinates close to a left part of the item rectangle

        The returned coordinates are always absolute
        """
        
        # TODO get rectangle of text area
        rect = self.rectangle()
        coords = (rect.left + int(float(rect.width()) / 4.),
                  rect.top + int(float(rect.height()) / 2.))
        return coords

    # -----------------------------------------------------------
    def sub_elements(self, depth=None):
        """Return a list of all visible sub-items of this control"""
        return self.descendants(control_type="TreeItem", depth=depth)

    def expand(self):
        self.set_property('IsExpanded', True)
        return self

    # -----------------------------------------------------------
    def collapse(self):
        self.set_property('IsExpanded', False)
        return self

    # -----------------------------------------------------------
    def is_expanded(self):
        """Test if the control is expanded"""
        return self.get_property('IsExpanded')

    # -----------------------------------------------------------
    def is_collapsed(self):
        """Test if the control is collapsed"""
        return not self.get_property('IsExpanded')

    # -----------------------------------------------------------
    def select(self):
        self.set_property('IsSelected', True)
        return self

    # -----------------------------------------------------------
    def is_selected(self):
        """Test if the control is expanded"""
        return self.get_property('IsSelected')


# ====================================================================
class TreeViewWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF Tree control"""

    _control_types = ['Tree']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(TreeViewWrapper, self).__init__(elem)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(TreeViewWrapper, self).writable_props
        props.extend(['item_count'])
        return props

    # -----------------------------------------------------------
    def item_count(self, depth=None):
        """Return a number of items in TreeView"""
        return len(self.descendants(control_type="TreeItem", depth=depth))

    # -----------------------------------------------------------
    def roots(self):
        """Return root elements of TreeView"""
        return self.children(control_type="TreeItem")

    # -----------------------------------------------------------
    def get_item(self, path, exact=False):
        r"""Read a TreeView item

        * **path** a path to the item to return. This can be one of
          the following:

          * A string separated by \\ characters. The first character must
            be \\. This string is split on the \\ characters and each of
            these is used to find the specific child at each level. The
            \\ represents the root item - so you don't need to specify the
            root itself.
          * A list/tuple of strings - The first item should be the root
            element.
          * A list/tuple of integers - The first item the index which root
            to select. Indexing always starts from zero: get_item((0, 2, 3))

        * **exact** a flag to request exact match of strings in the path
          or apply a fuzzy logic of best_match thus allowing non-exact
          path specifiers
        """
        if not self.item_count():
            return None

        # Ensure the path is absolute
        if isinstance(path, six.string_types):
            if not path.startswith("\\"):
                raise RuntimeError(
                    "Only absolute paths allowed - "
                    "please start the path with \\")
            path = path.split("\\")[1:]

        # find the correct root elem
        if isinstance(path[0], int):
            current_elem = self.roots()[path[0]]
        else:
            roots = self.roots()
            texts = [r.window_text() for r in roots]
            if exact:
                if path[0] in texts:
                    current_elem = roots[texts.index(path[0])]
                else:
                    raise IndexError("There is no root element equal to '{0}'".format(path[0]))
            else:
                try:
                    current_elem = findbestmatch.find_best_match(
                        path[0], texts, roots, limit_ratio=.6)
                except IndexError:
                    raise IndexError("There is no root element similar to '{0}'".format(path[0]))

        # now for each of the lower levels
        # just index into it's children
        for child_spec in path[1:]:
            try:
                # ensure that the item is expanded as this is sometimes
                # required for loading tree view branches
                current_elem.expand()
                current_elem = current_elem.get_child(child_spec, exact)
            except IndexError:
                if isinstance(child_spec, six.string_types):
                    raise IndexError("Item '{0}' does not have a child '{1}'".format(
                                     current_elem.window_text(), child_spec))
                else:
                    raise IndexError("Item '{0}' does not have {1} children".format(
                                     current_elem.window_text(), child_spec + 1))

        return current_elem

    # -----------------------------------------------------------
    def print_items(self, max_depth=None):
        """Print all items with line indents"""
        self.text = ""

        def _print_one_level(item, ident):
            """Get texts for the item and its children"""
            self.text += " " * ident + item.window_text() + "\n"
            if max_depth is None or ident <= max_depth:
                for child in item.children(control_type="TreeItem"):
                    _print_one_level(child, ident + 1)

        for root in self.roots():
            _print_one_level(root, 0)

        return self.text


class ListItemWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF ListViewItem and DataGrid row controls"""

    _control_types = ['ListItem', ]

    # -----------------------------------------------------------
    def __init__(self, elem, container=None):
        """Initialize the control"""
        super(ListItemWrapper, self).__init__(elem)

        # Init a pointer to the item's container wrapper.
        # It must be set by a container wrapper producing the item.
        # Notice that the self.parent property isn't the same
        # because it results in a different instance of a wrapper.
        self.container = container

    def texts(self):
        """Return a list of item texts"""
        children = self.children()
        if len(children) == 1 and children[0].element_info.control_type == 'Pane':
            items_holder = children[0]  # grid ListViewItem

            descendants = items_holder.children()
            if len(descendants) == 1 and descendants[0].element_info.control_type == 'Pane':
                return [self.window_text()]  # ListBoxItem or non-grid ListViewItem
        else:
            items_holder = self  # DataGridRow
        return [elem.window_text() for elem in items_holder.children()]

    def select(self):
        """Select the item

        Usually applied for controls like: a radio button, a tree view item
        or a list item.
        """
        self.set_property('IsSelected', True)

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
        return self.get_property('IsSelected')


class ListViewWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF ListView control"""

    _control_types = ['List']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ListViewWrapper, self).__init__(elem)

    def __getitem__(self, key):
        return self.get_item(key)

    # -----------------------------------------------------------
    def item_count(self):
        """A number of items in the List"""
        return len(self.children())

    # -----------------------------------------------------------
    def cells(self):
        """Return list of list of cells for any type of control"""
        return self.children(content_only=True)

    # -----------------------------------------------------------
    def get_item(self, row):
        """Return an item of the ListView control

        * **row** can be either an index of the row or a string
          with the text of a cell in the row you want returned.
        """
        # Verify arguments
        if isinstance(row, six.string_types):
            # Get DataGrid row
            try:
                itm = self.descendants(name=row)[0]
                # Applications like explorer.exe usually return ListItem
                # directly while other apps can return only a cell.
                # In this case we need to take its parent - the whole row.
                if not isinstance(itm, ListItemWrapper):
                    itm = itm.parent()
            except IndexError:
                raise ValueError("Element '{0}' not found".format(row))
        elif isinstance(row, six.integer_types):
            # Get the item by a row index
            list_items = self.children(content_only=True)
            itm = list_items[row]
        else:
            raise TypeError("String type or integer is expected")

        # Give to the item a pointer on its container
        itm.container = self
        return itm

    item = get_item  # this is an alias to be consistent with other content elements

    # -----------------------------------------------------------
    def get_items(self):
        """Return all items of the ListView control"""
        return self.children(content_only=True)

    items = get_items  # this is an alias to be consistent with other content elements

    # -----------------------------------------------------------
    def get_item_rect(self, item_index):
        """Return the bounding rectangle of the list view item

        The method is kept mostly for a backward compatibility
        with the native ListViewWrapper interface
        """
        itm = self.get_item(item_index)
        return itm.rectangle()

    def get_selection(self):
        # TODO get selected items directly from SelectedItems property
        return [child for child in self.iter_children() if child.is_selected()]

    # -----------------------------------------------------------
    def get_selected_count(self):
        """Return a number of selected items

        The call can be quite expensive as we retrieve all
        the selected items in order to count them
        """
        selection = self.get_selection()
        if selection:
            return len(selection)
        else:
            return 0

    # -----------------------------------------------------------
    def texts(self):
        """Return a list of item texts"""
        return [elem.texts() for elem in self.children(content_only=True)]

    # -----------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ListViewWrapper, self).writable_props
        props.extend(['item_count',
                      # 'items',
                      ])
        return props


class HeaderItemWrapper(wpfwrapper.WPFWrapper):

    """Wrap an WPF Header Item control"""

    _control_types = ['HeaderItem']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(HeaderItemWrapper, self).__init__(elem)


class DataGridWrapper(wpfwrapper.WPFWrapper):

    """Wrap WPF ListView (with a GridView view) or DataGrid control"""

    _control_types = ['DataGrid']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(DataGridWrapper, self).__init__(elem)

    def __getitem__(self, key):
        return self.get_item(key)

    # -----------------------------------------------------------
    def item_count(self):
        """A number of items in the Grid"""
        return len(self.children(control_type='ListItem'))

    # -----------------------------------------------------------
    def column_count(self):
        """Return the number of columns"""
        return len(self.children(control_type='HeaderItem'))

    # -----------------------------------------------------------
    def get_header_controls(self):
        """Return Header controls associated with the Table"""
        return self.children(control_type='HeaderItem')

    columns = get_header_controls

    # -----------------------------------------------------------
    def get_column(self, col_index):
        """Get the information for a column of the ListView"""
        col = self.columns()[col_index]
        return col

    # -----------------------------------------------------------
    def cells(self):
        """Return list of list of cells for any type of control"""
        rows = self.children(control_type='ListItem')

        result = []
        for row in rows:
            children = row.children()
            if len(children) == 1 and children[0].element_info.control_type == 'Pane':
                result.append(children[0].children())
            else:
                result.append(children)
        return result

    # -----------------------------------------------------------
    def cell(self, row, column):
        """Return a cell in the with a GridView view

        Only for controls with Grid pattern support

        * **row** is an index of a row in the list.
        * **column** is an index of a column in the specified row.

        The returned cell can be of different control types.
        Mostly: TextBlock, ImageControl, EditControl, DataItem
        or even another layer of data items (Group, DataGrid)
        """
        if not isinstance(row, six.integer_types) or not isinstance(column, six.integer_types):
            raise TypeError("row and column must be numbers")

        _row = self.get_item(row).children()
        if len(_row) == 1 and _row[0].element_info.control_type == 'Pane':
            cell_elem = _row[0].children()[column]
        else:
            cell_elem = _row[column]
        return cell_elem

    # -----------------------------------------------------------
    def get_item(self, row):
        """Return an item of the ListView control

        * **row** can be either an index of the row or a string
          with the text of a cell in the row you want returned.
        """
        # Verify arguments
        if isinstance(row, six.string_types):
            # Get DataGrid row
            try:
                itm = self.descendants(name=row)[0]
                # Applications like explorer.exe usually return ListItem
                # directly while other apps can return only a cell.
                # In this case we need to take its parent - the whole row.
                while itm is not None and not isinstance(itm, ListItemWrapper):
                    itm = itm.parent()
            except IndexError:
                raise ValueError("Element '{0}' not found".format(row))
        elif isinstance(row, six.integer_types):
            # Get the item by a row index
            list_items = self.children(control_type='ListItem')
            itm = list_items[row]
        else:
            raise TypeError("String type or integer is expected")

        # Give to the item a pointer on its container
        if itm is not None:
            itm.container = self
        return itm

    item = get_item  # this is an alias to be consistent with other content elements

    # -----------------------------------------------------------
    def get_items(self):
        """Return all items of the ListView control"""
        return self.children(control_type='ListItem')

    items = get_items  # this is an alias to be consistent with other content elements

    # -----------------------------------------------------------
    def get_item_rect(self, item_index):
        """Return the bounding rectangle of the list view item

        The method is kept mostly for a backward compatibility
        with the native ListViewWrapper interface
        """
        itm = self.get_item(item_index)
        return itm.rectangle()

    def get_selection(self):
        # TODO get selected items directly from SelectedItems property
        return [child for child in self.iter_children(control_type='ListItem') if child.is_selected()]

    # -----------------------------------------------------------
    def get_selected_count(self):
        """Return a number of selected items

        The call can be quite expensive as we retrieve all
        the selected items in order to count them
        """
        selection = self.get_selection()
        if selection:
            return len(selection)
        else:
            return 0

    # -----------------------------------------------------------
    def texts(self):
        """Return a list of item texts"""
        return [elem.texts() for elem in self.descendants(control_type='ListItem')]

    # -----------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(DataGridWrapper, self).writable_props
        props.extend(['column_count',
                      'item_count',
                      'columns',
                      # 'items',
                      ])
        return props
