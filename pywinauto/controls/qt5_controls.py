# -*- coding: utf-8 -*-
"""Wrap various Qt controls. To be used with the 'qt5' backend."""

from __future__ import unicode_literals

from .qt5wrapper import Qt5Wrapper
from .qt_common_controls import (
    CommonButtonWrapper,
    CommonComboBoxWrapper,
    CommonEditWrapper,
    CommonListViewWrapper,
    CommonPaneWrapper,
    CommonSliderWrapper,
    CommonTabControlWrapper,
    CommonTableWrapper,
    CommonTreeViewWrapper,
    CommonWindowWrapper,
)


class WindowWrapper(CommonWindowWrapper, Qt5Wrapper):

    """Wrap a Qt top-level window."""

    _control_types = ['Window']


class PaneWrapper(CommonPaneWrapper, Qt5Wrapper):

    """Wrap generic Qt container controls."""

    _control_types = ['Pane', 'GroupBox']


class ButtonWrapper(CommonButtonWrapper, Qt5Wrapper):

    """Wrap Qt button, checkbox, and radio button controls."""

    _control_types = ['Button', 'CheckBox', 'RadioButton']


class EditWrapper(CommonEditWrapper, Qt5Wrapper):

    """Wrap a Qt edit control."""

    _control_types = ['Edit']

class ComboBoxWrapper(CommonComboBoxWrapper, Qt5Wrapper):

    """Wrap a Qt combobox."""

    _control_types = ['ComboBox']


class TabControlWrapper(CommonTabControlWrapper, Qt5Wrapper):

    """Wrap Qt tab controls."""

    _control_types = ['TabControl']


class SliderWrapper(CommonSliderWrapper, Qt5Wrapper):

    """Wrap Qt slider, scrollbar, spinbox, and progress controls."""

    _control_types = ['Slider', 'ScrollBar', 'Spinner', 'ProgressBar']


class ListViewWrapper(CommonListViewWrapper, Qt5Wrapper):

    """Wrap Qt list controls."""

    _control_types = ['List']


class TreeViewWrapper(CommonTreeViewWrapper, Qt5Wrapper):

    """Wrap Qt tree controls."""

    _control_types = ['Tree']


class TableWrapper(CommonTableWrapper, Qt5Wrapper):

    """Wrap Qt table controls."""

    _control_types = ['Table']
