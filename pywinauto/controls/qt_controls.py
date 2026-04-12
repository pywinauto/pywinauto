# -*- coding: utf-8 -*-
"""Wrap various Qt controls. To be used with the 'qt' backend."""

from __future__ import unicode_literals

from . import qtwrapper


class WindowWrapper(qtwrapper.QtWrapper):

    """Wrap a Qt top-level window."""

    _control_types = ['Window']

    def is_dialog(self):
        """Qt top-level windows are dialog-like for pywinauto purposes."""
        return True

    def close(self):
        """Close the window."""
        self.invoke_method('close')
        return self


class PaneWrapper(qtwrapper.QtWrapper):

    """Wrap generic Qt container controls."""

    _control_types = ['Pane', 'GroupBox']


class ButtonWrapper(qtwrapper.QtWrapper):

    """Wrap Qt button, checkbox, and radio button controls."""

    _control_types = ['Button', 'CheckBox', 'RadioButton']

    UNCHECKED = 0
    CHECKED = 1
    INDETERMINATE = 2

    def toggle(self):
        """Toggle a checkable button."""
        self.element_info.toggle()
        return self

    def get_toggle_state(self):
        """Return toggle state as an integer."""
        value = self.get_native_property('checked')
        if value is None:
            return self.INDETERMINATE
        return self.CHECKED if value else self.UNCHECKED

    def is_checked(self):
        """Return checked state."""
        return self.get_toggle_state() == self.CHECKED

    def check(self):
        """Check the button."""
        if not self.is_checked():
            self.toggle()
        return self

    def uncheck(self):
        """Uncheck the button."""
        if self.is_checked():
            self.toggle()
        return self

    def select(self):
        """Select a radio/check button."""
        self.element_info.select()
        return self

    def is_selected(self):
        """Return selected state."""
        return self.is_checked()


class EditWrapper(qtwrapper.QtWrapper):

    """Wrap a Qt edit control."""

    _control_types = ['Edit']
    has_title = False

    def get_value(self):
        """Return text value."""
        return self.element_info.value

    def set_edit_text(self, text, pos_start=None, pos_end=None):
        """Set the edit text."""
        self.verify_actionable()
        if pos_start is not None or pos_end is not None:
            current_text = self.window_text()
            if pos_start is None:
                pos_start = 0
            if pos_end is None:
                pos_end = len(current_text)
            text = current_text[:pos_start] + str(text) + current_text[pos_end:]
        self.element_info.set_text(text)
        return self

    set_text = set_edit_text

    def set_window_text(self, text, append=False):
        """Set edit text, optionally appending to the current value."""
        if append:
            text = self.window_text() + str(text)
        return self.set_edit_text(text)

    def line_count(self):
        """Return line count."""
        return self.window_text().count("\n") + 1

    def texts(self):
        """Return edit lines."""
        return self.window_text().splitlines() or ['']


class ComboBoxWrapper(qtwrapper.QtWrapper):

    """Wrap a Qt combobox."""

    _control_types = ['ComboBox']

    def expand(self):
        """Show combobox popup."""
        self.element_info.expand()
        return self

    def collapse(self):
        """Hide combobox popup."""
        self.element_info.collapse()
        return self

    def item_count(self):
        """Return number of combo items."""
        return int(self.get_native_property('count') or 0)

    def texts(self):
        """Return combobox item texts."""
        return self.element_info.items()

    def select(self, item):
        """Select an item by index or text."""
        self.element_info.select(item)
        return self

    def selected_index(self):
        """Return current item index."""
        return self.get_native_property('currentIndex')

    def selected_text(self):
        """Return current item text."""
        return self.get_native_property('currentText') or ''

    def is_editable(self):
        """Return whether the combobox is editable."""
        return bool(self.get_native_property('editable'))


class TabControlWrapper(qtwrapper.QtWrapper):

    """Wrap Qt tab controls."""

    _control_types = ['TabControl']

    def tab_count(self):
        """Return number of tabs."""
        return int(self.get_native_property('count') or len(self.children()))

    def get_selected_tab(self):
        """Return current tab index."""
        return self.get_native_property('currentIndex')

    def texts(self):
        """Return tab texts."""
        return self.element_info.items() or self.children_texts()

    def select(self, item):
        """Select a tab by index or text."""
        self.element_info.select(item)
        return self


class SliderWrapper(qtwrapper.QtWrapper):

    """Wrap Qt slider, scrollbar, spinbox, and progress controls."""

    _control_types = ['Slider', 'ScrollBar', 'Spinner', 'ProgressBar']
    has_title = False

    def min_value(self):
        """Return minimum value."""
        return self.get_native_property('minimum')

    def max_value(self):
        """Return maximum value."""
        return self.get_native_property('maximum')

    def value(self):
        """Return current value."""
        return self.element_info.value

    def set_value(self, value):
        """Set current value."""
        self.element_info.set_value(value)
        return self


class ListViewWrapper(qtwrapper.QtWrapper):

    """Wrap Qt list controls."""

    _control_types = ['List']

    def item_count(self):
        """Return item count."""
        return int(self.get_native_property('count') or len(self.children()))

    def texts(self):
        """Return item texts."""
        return self.element_info.items()

    def get_items(self):
        """Return visible item wrappers."""
        return self.children()

    items = get_items

    def select(self, item):
        """Select an item by index or text."""
        self.element_info.select(item)
        return self


class TreeViewWrapper(qtwrapper.QtWrapper):

    """Wrap Qt tree controls."""

    _control_types = ['Tree']

    def item_count(self, depth=None):
        """Return number of visible tree items."""
        return len(self.descendants(depth=depth))

    def roots(self):
        """Return root item wrappers."""
        return self.children()

    def expand(self):
        """Expand the current tree item/control if supported."""
        self.element_info.expand()
        return self

    def collapse(self):
        """Collapse the current tree item/control if supported."""
        self.element_info.collapse()
        return self


class TableWrapper(qtwrapper.QtWrapper):

    """Wrap Qt table controls."""

    _control_types = ['Table']

    def row_count(self):
        """Return row count."""
        return int(self.get_native_property('rowCount') or 0)

    def column_count(self):
        """Return column count."""
        return int(self.get_native_property('columnCount') or 0)

    def item_count(self):
        """Return total cell count."""
        return self.row_count() * self.column_count()
