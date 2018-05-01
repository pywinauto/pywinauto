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

"""Wrap various UIA windows controls"""
import locale
import comtypes
import six

from .. import uia_element_info
from .. import findbestmatch
from .. import timings

from . import uiawrapper
from ..uia_defines import IUIA
from ..uia_defines import NoPatternInterfaceError
from ..uia_defines import toggle_state_on
from ..uia_defines import get_elem_interface


# ====================================================================
class ButtonWrapper(uiawrapper.UIAWrapper):

    """Wrap a UIA-compatible Button, CheckBox or RadioButton control"""

    _control_types = ['Button',
        'CheckBox',
        'RadioButton',
    ]

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
        name = self.element_info.name
        control_type = self.element_info.control_type

        self.iface_toggle.Toggle()

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

        The following constants are defined in the uia_defines module
        toggle_state_off = 0
        toggle_state_on = 1
        toggle_state_inderteminate = 2
        """
        return self.iface_toggle.CurrentToggleState

    # -----------------------------------------------------------
    def is_dialog(self):
        """Buttons are never dialogs so return False"""
        return False

    # -----------------------------------------------------------
    def click(self):
        """Click the Button control by using Invoke pattern"""
        self.invoke()

        # Return itself so that action can be chained
        return self


# ====================================================================
class ComboBoxWrapper(uiawrapper.UIAWrapper):

    """Wrap a UIA CoboBox control"""

    _control_types = ['ComboBox']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def texts(self):
        """Return the text of the items in the combobox"""
        texts = []
        # ComboBox has to be expanded to populate a list of its children items
        try:
            self.expand()
            for c in self.children():
                texts.append(c.window_text())
        except NoPatternInterfaceError:
            return texts
        else:
            # Make sure we collapse back
            self.collapse()
        return texts

    def select(self, item):
        """
        Select the ComboBox item

        The item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        # ComboBox has to be expanded to populate a list of its children items
        self.expand()
        try:
            self._select(item)
        # TODO: do we need to handle ValueError/IndexError for a wrong index ?
        #except ValueError:
        #    raise  # re-raise the last exception
        finally:
            # Make sure we collapse back in any case
            self.collapse()
        return self

    # -----------------------------------------------------------
    # TODO: add selected_texts for a combobox with a multi-select support
    def selected_text(self):
        """
        Return the selected text or None

        Notice, that in case of multi-select it will be only the text from
        a first selected item
        """
        selection = self.get_selection()
        if selection:
            return selection[0].name
        else:
            return None

    # -----------------------------------------------------------
    # TODO: add selected_indices for a combobox with multi-select support
    def selected_index(self):
        """Return the selected index"""
        return self.selected_item_index()

    # -----------------------------------------------------------
    def item_count(self):
        """
        Return the number of items in the combobox

        The interface is kept mostly for a backward compatibility with
        the native ComboBox interface
        """
        return self.control_count()


# ====================================================================
class EditWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Edit control"""
    # TODO: this class supports only 1-line textboxes so there is no point
    # TODO: in methods such as line_count(), line_length(), get_line(), etc

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
        return self.iface_value.CurrentValue

    # -----------------------------------------------------------
    def texts(self):
        """Get the text of the edit control"""
        texts = [self.window_text(), ]

        for i in range(self.line_count()):
            texts.append(self.get_line(i))

        return texts

    # -----------------------------------------------------------
    def text_block(self):
        """Get the text of the edit control"""
        return self.window_text()

    # -----------------------------------------------------------
    def selection_indices(self):
        """The start and end indices of the current selection"""
        selected_text = self.iface_text.GetSelection().GetElement(0).GetText(-1)
        start = self.window_text().find(selected_text)
        end = start + len(selected_text)

        return (start, end)

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

        self.set_focus()

        # Set text using IUIAutomationValuePattern
        self.iface_value.SetValue(text)

        raise UserWarning("set_window_text() should probably not be called for Edit Controls")

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
        # Set text using IUIAutomationValuePattern
        self.iface_value.SetValue(new_text)

        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_editsetedittext_wait)

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

        # if we have been asked to select a string
        if isinstance(start, six.text_type):
            string_to_select = start
        elif isinstance(start, six.binary_type):
            string_to_select = start.decode(locale.getpreferredencoding())
        elif isinstance(start, six.integer_types):
            if isinstance(end, six.integer_types) and start > end:
                start, end = end, start
            string_to_select = self.window_text()[start:end]

        if string_to_select:
            document_range = self.iface_text.DocumentRange
            search_range = document_range.FindText(string_to_select, False, False)

            try:
                search_range.Select()
            except ValueError:
                raise RuntimeError("Text '{0}' hasn't been found".format(string_to_select))

        # return this control so that actions can be chained.
        return self


# ====================================================================
class TabControlWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Tab control"""

    _control_types = ['Tab']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(TabControlWrapper, self).__init__(elem)

    # ----------------------------------------------------------------
    def get_selected_tab(self):
        """Return an index of a selected tab"""
        return self.selected_item_index()

    # ----------------------------------------------------------------
    def tab_count(self):
        """Return a number of tabs"""
        return self.control_count()

    # ----------------------------------------------------------------
    def select(self, item):
        """Select a tab by index or by name"""
        self._select(item)
        return self

    # ----------------------------------------------------------------
    def texts(self):
        """Tabs texts"""
        return self.children_texts()


# ====================================================================
class SliderWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Slider control"""

    _control_types = ['Slider']
    has_title = False

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(SliderWrapper, self).__init__(elem)

    # -----------------------------------------------------------
    def min_value(self):
        """Get the minimum value of the Slider"""
        return self.iface_range_value.CurrentMinimum

    # -----------------------------------------------------------
    def max_value(self):
        """Get the maximum value of the Slider"""
        return self.iface_range_value.CurrentMaximum

    # -----------------------------------------------------------
    def small_change(self):
        """
        Get a small change of slider's thumb

        This change is achieved by pressing left and right arrows
        when slider's thumb has keyboard focus.
        """
        return self.iface_range_value.CurrentSmallChange

    # -----------------------------------------------------------
    def large_change(self):
        """
        Get a large change of slider's thumb

        This change is achieved by pressing PgUp and PgDown keys
        when slider's thumb has keyboard focus.
        """
        return self.iface_range_value.CurrentLargeChange

    # -----------------------------------------------------------
    def value(self):
        """Get a current position of slider's thumb"""
        return self.iface_range_value.CurrentValue

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

        self.iface_range_value.SetValue(value_to_set)


# ====================================================================
class HeaderWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Header control"""

    _control_types = ['Header']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(HeaderWrapper, self).__init__(elem)


# ====================================================================
class HeaderItemWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Header Item control"""

    _control_types = ['HeaderItem']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(HeaderItemWrapper, self).__init__(elem)


# ====================================================================
class ListItemWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible ListViewItem control"""

    _control_types = ['DataItem', 'ListItem', ]

    # -----------------------------------------------------------
    def __init__(self, elem, container=None):
        """Initialize the control"""
        super(ListItemWrapper, self).__init__(elem)

        # Init a pointer to the item's container wrapper.
        # It must be set by a container wrapper producing the item.
        # Notice that the self.parent property isn't the same
        # because it results in a different instance of a wrapper.
        self.container = container

    # -----------------------------------------------------------
    def is_checked(self):
        """Return True if the ListItem is checked

        Only items supporting Toggle pattern should answer.
        Raise NoPatternInterfaceError if the pattern is not supported
        """
        return self.iface_toggle.ToggleState_On == toggle_state_on

    def texts(self):
        """Return a list of item texts"""
        content = [ch.window_text() for ch in self.children(content_only=True)]
        if content:
            return content
        else:
            # For native list with small icons
            return super(ListItemWrapper, self).texts()


# ====================================================================
class ListViewWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible ListView control"""

    _control_types = ['DataGrid', 'List', ]

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(ListViewWrapper, self).__init__(elem)

        # Check if control supports Grid pattern
        # Control is actually a DataGrid or a List with Grid pattern support
        try:
            if self.iface_grid:
                self.iface_grid_support = True
        except NoPatternInterfaceError:
            self.iface_grid_support = False

    # -----------------------------------------------------------
    def item_count(self):
        """A number of items in the ListView"""
        if self.iface_grid_support:
            return self.iface_grid.CurrentRowCount
        else:
            # TODO: This could be implemented by getting custom ItemCount Property using RegisterProperty
            # TODO: See https://msdn.microsoft.com/ru-ru/library/windows/desktop/ff486373%28v=vs.85%29.aspx for details
            # TODO: comtypes doesn't seem to support IUIAutomationRegistrar interface
            return (len(self.children()))

    # -----------------------------------------------------------
    def column_count(self):
        """Return the number of columns"""
        if self.iface_grid_support:
            return self.iface_grid.CurrentColumnCount
        else:
            # ListBox doesn't have columns
            return 0

    # -----------------------------------------------------------
    def get_header_control(self):
        """Return Header control associated with the ListView"""
        try:
            # A data grid control may have no header
            hdr = self.children(control_type="Header")[0]
        except(IndexError, NoPatternInterfaceError):
            hdr = None

        return hdr

    # -----------------------------------------------------------
    def get_column(self, col_index):
        """Get the information for a column of the ListView"""
        col = None
        try:
            col = self.columns()[col_index]
        except comtypes.COMError:
            raise IndexError
        return col

    # -----------------------------------------------------------
    def columns(self):
        """Get the information on the columns of the ListView"""
        if self.iface_grid_support:
            arr = self.iface_table.GetCurrentColumnHeaders()
            cols = uia_element_info.elements_from_uia_array(arr)
            return [uiawrapper.UIAWrapper(e) for e in cols]
        else:
            # ListBox doesn't have columns
            return []

    # -----------------------------------------------------------
    def cell(self, row, column):
        """Return a cell in the ListView control

        Only for controls with Grid pattern support

        * **row** is an index of a row in the list.
        * **column** is an index of a column in the specified row.

        The returned cell can be of different control types.
        Mostly: TextBlock, ImageControl, EditControl, DataItem
        or even another layer of data items (Group, DataGrid)
        """
        if not isinstance(row, six.integer_types) or not isinstance(column, six.integer_types):
            raise TypeError("row and column must be numbers")

        if not self.iface_grid_support:
            return None

        try:
            e = self.iface_grid.GetItem(row, column)
            elem_info = uia_element_info.UIAElementInfo(e)
            cell_elem = uiawrapper.UIAWrapper(elem_info)
        except (comtypes.COMError, ValueError):
            raise IndexError

        return cell_elem

    # -----------------------------------------------------------
    def get_item(self, row):
        """Return an item of the ListView control

        * **row** can be either an index of the row or a string
          with the text of a cell in the row you want returned.
        """
        # Verify arguments
        if isinstance(row, six.string_types):
            # Try to find item using FindItemByProperty
            # That way we can get access to virtualized (unloaded) items
            com_elem = self.iface_item_container.FindItemByProperty(0, IUIA().UIA_dll.UIA_NamePropertyId, row)
            # Try to load element using VirtualizedItem pattern
            try:
                get_elem_interface(com_elem, "VirtualizedItem").Realize()
                itm = uiawrapper.UIAWrapper(uia_element_info.UIAElementInfo(com_elem))
            except NoPatternInterfaceError:
                # Item doesn't support VirtualizedItem pattern - item is already on screen or com_elem is NULL
                try:
                    itm = uiawrapper.UIAWrapper(uia_element_info.UIAElementInfo(com_elem))
                except ValueError:
                    # com_elem is NULL pointer
                    # Get DataGrid row
                    try:
                        itm = self.descendants(title=row)[0]
                        # Applications like explorer.exe usually return ListItem
                        # directly while other apps can return only a cell.
                        # In this case we need to take its parent - the whole row.
                        if not isinstance(itm, ListItemWrapper):
                            itm = itm.parent()
                    except IndexError:
                        raise ValueError("Element '{0}' not found".format(row))
        elif isinstance(row, six.integer_types):
            # Get the item by a row index
            # TODO: Can't get virtualized items that way
            # TODO: See TODO section of item_count() method for details
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

    # -----------------------------------------------------------
    def get_selected_count(self):
        """Return a number of selected items

        The call can be quite expensieve as we retrieve all
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
        props.extend(['column_count',
                      'item_count',
                      'columns',
                      # 'items',
                      ])
        return props


# ====================================================================
class MenuItemWrapper(uiawrapper.UIAWrapper):

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
        """Apply Select pattern"""
        try:
            self.iface_selection_item.Select()
        except(NoPatternInterfaceError):
            try:
                self.iface_invoke.Invoke()
            except(NoPatternInterfaceError):
                raise AttributeError


# ====================================================================
class MenuWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible MenuBar or Menu control"""

    _control_types = ['MenuBar', 'Menu', ]

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
    @staticmethod
    def _activate(item):
        """Activate the specified item"""
        if not item.is_active():
            item.set_focus()
        try:
            item.expand()
        except(NoPatternInterfaceError):
            pass

    # -----------------------------------------------------------
    def _sub_item_by_text(self, menu, name, exact):
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

        self._activate(sub_item)

        return sub_item

    # -----------------------------------------------------------
    def _sub_item_by_idx(self, menu, idx):
        """Find a menu sub-item by the specified index"""
        sub_item = None
        items = menu.items()
        if items:
            sub_item = items[idx]
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
        part0, parts = path.split("->", 1)
        part0 = part0.strip()
        if len(part0) == 0:
            raise IndexError()

        # Find a top level menu item and select it. After selecting this item
        # a new Menu control is created and placed on the dialog. It can be
        # a direct child or a descendant.
        # Sometimes we need to re-discover Menu again
        try:
            menu = None
            if part0.startswith("#"):
                menu = self._sub_item_by_idx(self, int(part0[1:]))
            else:
                menu = self._sub_item_by_text(self, part0, exact)

            if not menu.items():
                self._activate(menu)
                timings.wait_until(
                    timings.Timings.window_find_timeout,
                    timings.Timings.window_find_retry,
                    lambda: len(self.top_level_parent().descendants(control_type="Menu")) > 0)
                menu = self.top_level_parent().descendants(control_type="Menu")[0]

            for cur_part in [p.strip() for p in parts.split("->")]:
                if cur_part.startswith("#"):
                    menu = self._sub_item_by_idx(menu, int(cur_part[1:]))
                else:
                    menu = self._sub_item_by_text(menu, cur_part, exact)
        except(AttributeError):
            raise IndexError()

        return menu


# ====================================================================
class TooltipWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Tooltip control"""

    _control_types = ['ToolTip']

    # -----------------------------------------------------------
    def __init__(self, elem):
        """Initialize the control"""
        super(TooltipWrapper, self).__init__(elem)


# ====================================================================
class ToolbarWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible ToolBar control

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

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ToolbarWrapper, self).writable_props
        props.extend(['button_count'])
        return props

    # ----------------------------------------------------------------
    def texts(self):
        """Return texts of the Toolbar"""
        return self.children_texts()

    #----------------------------------------------------------------
    def button_count(self):
        """Return a number of buttons on the ToolBar"""
        return len(self.children())

    # ----------------------------------------------------------------
    def button(self, button_identifier, exact=True):
        """Return a button by the specified identifier

        * **button_identifier** can be either an index of a button or
          a string with the text of the button.
        * **exact** flag specifies if the exact match for the text look up
          has to be applied.
        """

        cc = self.children()
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

        res = (button.get_toggle_state() == toggle_state_on)
        if res != make_checked:
            button.toggle()

        self.actions.logSectionEnd()
        return button


# ====================================================================
class TreeItemWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible TreeItem control

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
    def is_checked(self):
        """Return True if the TreeItem is checked

        Only items supporting Toggle pattern should answer.
        Raise NoPatternInterfaceError if the pattern is not supported
        """
        return (self.iface_toggle.ToggleState_On == toggle_state_on)

    # -----------------------------------------------------------
    def ensure_visible(self):
        """Make sure that the TreeView item is visible"""
        self.iface_scroll_item.ScrollIntoView()

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

        Try to get coordinates of a text box inside the item.
        If no text box found just set coordinates
        close to a left part of the item rectangle

        The returned coordinates are always absolute
        """
        tt = self.children(control_type="Text")
        if tt:
            point = tt[0].rectangle().mid_point()
            # convert from POINT to a simple tuple
            coords = (point.x, point.y)
        else:
            rect = self.rectangle()
            coords = (rect.left + int(float(rect.width()) / 4.),
                      rect.top + int(float(rect.height()) / 2.))
        return coords

    # -----------------------------------------------------------
    def sub_elements(self):
        """Return a list of all visible sub-items of this control"""
        return self.descendants(control_type="TreeItem")


# ====================================================================
class TreeViewWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible Tree control"""

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
    def item_count(self):
        """Return a number of items in TreeView"""
        return len(self.descendants(control_type="TreeItem"))

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

        current_elem = None

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
            except comtypes.COMError:
                raise IndexError("Item '{0}' does not have a child '{1}'".format(
                                 current_elem.window_text(), child_spec))

        return current_elem

    # -----------------------------------------------------------
    def print_items(self):
        """Print all items with line indents"""
        self.text = ""

        def _print_one_level(item, ident):
            """Get texts for the item and its children"""
            self.text += " " * ident + item.window_text() + "\n"
            for child in item.children(control_type="TreeItem"):
                _print_one_level(child, ident + 1)

        for root in self.roots():
            _print_one_level(root, 0)

        return self.text
