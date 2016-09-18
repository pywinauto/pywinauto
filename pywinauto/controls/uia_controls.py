# GUI Application automation and testing library
# Copyright (C) 2006-2016 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.github.io/docs/credits.html
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

from . import uiawrapper
from ..uia_defines import IUIA
from ..uia_defines import NoPatternInterfaceError
from ..uia_defines import toggle_state_on


# ====================================================================
class ButtonWrapper(uiawrapper.UIAWrapper):

    """Wrap a UIA-compatible Button, CheckBox or RadioButton control"""

    control_types = [
        IUIA().UIA_dll.UIA_ButtonControlTypeId,
        IUIA().UIA_dll.UIA_CheckBoxControlTypeId,
        IUIA().UIA_dll.UIA_RadioButtonControlTypeId
        ]

    # -----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ButtonWrapper, self).__init__(hwnd)

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
        self.iface_toggle.Toggle()

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

    # -----------------------------------------------------------
    def select(self):
        """
        An interface to Select method of the SelectionItem control pattern.

        Usually applied for a radio button control
        """
        self.iface_selection_item.Select()

        # Return itself so that action can be chained
        return self

    # -----------------------------------------------------------
    def is_selected(self):
        """
        An interface to CurrentIsSelected method of the SelectionItem control pattern.

        Usually applied for a radio button control
        """
        return self.iface_selection_item.CurrentIsSelected


# ====================================================================
class ComboBoxWrapper(uiawrapper.UIAWrapper):

    """Wrap a UIA CoboBox control"""

    control_types = [
        IUIA().UIA_dll.UIA_ComboBoxControlTypeId
        ]

    # -----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ComboBoxWrapper, self).__init__(hwnd)

    # -----------------------------------------------------------
    def texts(self):
        """Return the text of the items in the combobox"""
        texts = []
        # ComboBox has to be expanded to populate a list of its children items
        try:
            self.expand()
            for c in self.children():
                texts.append(c.window_text())
        finally:
            # Make sure we collapse back in any case
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

    control_types = [
        IUIA().UIA_dll.UIA_EditControlTypeId,
    ]
    has_title = False

    # -----------------------------------------------------------
    def __init__(self, elem_or_handle):
        """Initialize the control"""
        super(EditWrapper, self).__init__(elem_or_handle)

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

    control_types = [
        IUIA().UIA_dll.UIA_TabControlTypeId,
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(TabControlWrapper, self).__init__(hwnd)

    # ----------------------------------------------------------------
    def get_selected_tab(self):
        """Return the index of a selected tab"""
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

    control_types = [
        IUIA().UIA_dll.UIA_SliderControlTypeId,
    ]
    has_title = False

    # -----------------------------------------------------------
    def __init__(self, elem_or_handle):
        """Initialize the control"""
        super(SliderWrapper, self).__init__(elem_or_handle)

    # -----------------------------------------------------------
    def min_value(self):
        """Get minimum value of the Slider"""
        return self.iface_range_value.CurrentMinimum

    # -----------------------------------------------------------
    def max_value(self):
        """Get maximum value of the Slider"""
        return self.iface_range_value.CurrentMaximum

    # -----------------------------------------------------------
    def small_change(self):
        """
        Get small change of slider's thumb

        This change is achieved by pressing left and right arrows
        when slider's thumb has keyboard focus.
        """
        return self.iface_range_value.CurrentSmallChange

    # -----------------------------------------------------------
    def large_change(self):
        """
        Get large change of slider's thumb

        This change is achieved by pressing PgUp and PgDown keys
        when slider's thumb has keyboard focus.
        """
        return self.iface_range_value.CurrentLargeChange

    # -----------------------------------------------------------
    def value(self):
        """Get current position of slider's thumb"""
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

    control_types = [
        IUIA().UIA_dll.UIA_HeaderControlTypeId,
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(HeaderWrapper, self).__init__(hwnd)


# ====================================================================
class ListItemWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible ListViewItem control"""

    control_types = [
        IUIA().UIA_dll.UIA_DataItemControlTypeId,
        IUIA().UIA_dll.UIA_ListItemControlTypeId,
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd, container=None):
        """Initialize the control"""
        super(ListItemWrapper, self).__init__(hwnd)

        # Init a pointer to the item's container wrapper.
        # It must be set by a container wrapper producing the item.
        # Notice that the self.parent property isn't the same
        # because it results in a different instance of a wrapper.
        self.container = container

    # -----------------------------------------------------------
    def select(self):
        """Select/Deselect all cells in the ListItem"""
        self.iface_selection_item.Select()

    # -----------------------------------------------------------
    def is_selected(self):
        """Return True if the ListItem is selected"""
        return self.iface_selection_item.CurrentIsSelected

    # -----------------------------------------------------------
    def is_checked(self):
        """Return True if the ListItem is checked

        Only items supporting Toggle pattern should answer.
        Raise NoPatternInterfaceError if the pattern is not supported
        """
        res = (self.iface_toggle.ToggleState_On == toggle_state_on)
        return res


# ====================================================================
class ListViewWrapper(uiawrapper.UIAWrapper):

    """Wrap an UIA-compatible ListView control"""

    control_types = [
        IUIA().UIA_dll.UIA_DataGridControlTypeId,
        IUIA().UIA_dll.UIA_ListControlTypeId,
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the control"""
        super(ListViewWrapper, self).__init__(hwnd)

    # -----------------------------------------------------------
    def item_count(self):
        """A number of items in the ListView"""
        return self.iface_grid.CurrentRowCount

    # -----------------------------------------------------------
    def column_count(self):
        """Return the number of columns"""
        return self.iface_grid.CurrentColumnCount

    # -----------------------------------------------------------
    def get_header_control(self):
        """Return the Header control associated with the ListView"""
        try:
            # MSDN: A data grid control that has a header
            # should support the Table control pattern
            if self.iface_table:
                hdr = self.children()[0]
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
        arr = self.iface_table.GetCurrentColumnHeaders()
        cols = uia_element_info.elements_from_uia_array(arr)
        return [uiawrapper.UIAWrapper(e) for e in cols]

    # -----------------------------------------------------------
    def cell(self, row, column):
        """Return a cell in the ListView control

        * **row** is an index of a row in the list.
        * **column** is an index of a column in the specified row.
        The returned cell can be of different control types.
        Mostly: TextBlock, ImageControl, EditControl, DataItem
        or even another layer of data items (Group, DataGrid)
        """
        if not isinstance(row, six.integer_types) or \
           not isinstance(column, six.integer_types):
            raise ValueError

        try:
            e = self.iface_grid.GetItem(row, column)
            elem_info = uia_element_info.UIAElementInfo(e)
            cell = uiawrapper.UIAWrapper(elem_info)
        except comtypes.COMError:
            raise IndexError

        return cell

    # -----------------------------------------------------------
    def get_item(self, row):
        """Return an item of the ListView control

        * **row** Can be either an index of the row or a string
          with the text of a cell in the row you want returned.
        """
        # Verify arguments
        if isinstance(row, six.string_types):
            # Look for a cell with the text, return the first found item
            itm = self.descendants(title=row)[0]
        elif isinstance(row, six.integer_types):
            # Get the item by a row index of its first cell
            itm = self.cell(row, 0)
        else:
            raise TypeError('String type or integer is expected')

        # Applications like explorer.exe usually return ListItem
        # directly while other apps can return only a cell.
        # In this case we need to take its parent - the whole row.
        if not isinstance(itm, ListItemWrapper):
            itm = itm.parent()

        # Give to the item a pointer on its container
        itm.container = self
        return itm

    item = get_item  # this is an alias to be consistent with other content elements

    # -----------------------------------------------------------
    def get_item_rect(self, item_index):
        """Return the bounding rectangle of the list view item

        The interface is kept mostly for a backward compatibility
        with the native ListViewWrapper interface
        """
        itm = self.get_item(item_index)
        return itm.rectangle()

    # -----------------------------------------------------------
    def get_selected_count(self):
        """Return the number of selected items"""
        # The call can be quite expensieve as we retrieve all
        # the selected items in order to count them
        selection = self.get_selection()
        if selection:
            return len(selection)
        else:
            return 0

    # -----------------------------------------------------------
    def texts(self):
        """Return a list of item texts"""
        is_content_element = IUIA().iuia.CreatePropertyCondition(
            IUIA().UIA_dll.UIA_IsContentElementPropertyId, True)
        return [ch.name for ch in self.element_info._get_elements(IUIA().tree_scope["children"],
                is_content_element, cache_enable=False)]
        # TODO: add is_content_element() method to UIAWrapper
        # alternative (but slower) implementation:
        # return [ch.window_text() for ch in self.children() if ch.element_info.element.CurrentIsContentElement]

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

    control_types = [
        IUIA().UIA_dll.UIA_MenuItemControlTypeId,
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd, container=None):
        """Initialize the control"""
        super(MenuItemWrapper, self).__init__(hwnd)

    # -----------------------------------------------------------
    def _items(self):
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

    control_types = [
        IUIA().UIA_dll.UIA_MenuBarControlTypeId,
        IUIA().UIA_dll.UIA_MenuControlTypeId
    ]

    # -----------------------------------------------------------
    def __init__(self, hwnd, container=None):
        """Initialize the control"""
        super(MenuWrapper, self).__init__(hwnd)

    # -----------------------------------------------------------
    def _items(self):
        """Find all menu items"""
        return self.children(control_type="MenuItem")

    # -----------------------------------------------------------
    def item_by_index(self, idx):
        """Find a menu item specified by the index"""
        item = self._items()[idx]
        return item

    # -----------------------------------------------------------
    @staticmethod
    def _activate(item):
        """Activate the specified item"""

        if not item.is_active():
            # self.actions.log("[DEBUG] Set focus on", tem.texts())
            item.set_focus()
        try:
            item.expand()
            # self.actions.log("[DEBUG] Expand ", item.texts())
        except(NoPatternInterfaceError):
            pass

    # -----------------------------------------------------------
    def _sub_item_by_text(self, menu, name, exact):
        """Find a menu sub-item by the specified text"""
        sub_item = None

        if exact:
            for i in menu._items():
                if name == i.window_text():
                    sub_item = i
                    break
        else:
            items = []
            texts = []
            for i in menu._items():
                items.append(i)
                texts.append(i.window_text())
            sub_item = findbestmatch.find_best_match(name, texts, items)

        self._activate(sub_item)

        return sub_item

    # -----------------------------------------------------------
    def _sub_item_by_idx(self, menu, idx):
        """Find a menu sub-item by the specified index"""
        sub_item = None
        items = menu._items()
        if items:
            sub_item = items[idx]
            self._activate(sub_item)
        return sub_item

    # -----------------------------------------------------------
    def item_by_path(self, path, exact=False):
        """Find a menu item specified by the path

        The full path syntax is specified in:
        :py:meth:`pywinauto.menuwrapper.Menu.get_menu_path`
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

            if not menu._items():
                menu = self.top_level_parent().descendants(control_type="Menu")[0]

            for cur_part in [p.strip() for p in parts.split("->")]:
                if cur_part.startswith("#"):
                    menu = self._sub_item_by_idx(menu, int(cur_part[1:]))
                else:
                    menu = self._sub_item_by_text(menu, cur_part, exact)
        except(AttributeError):
            raise IndexError()

        return menu
