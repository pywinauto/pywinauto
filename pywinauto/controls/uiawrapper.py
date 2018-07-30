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

"""Basic wrapping of UI Automation elements"""

from __future__ import unicode_literals
from __future__ import print_function

import six
import time
import warnings
import comtypes

from .. import backend
from ..timings import Timings
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from ..uia_defines import IUIA
from .. import uia_defines as uia_defs
from ..uia_element_info import UIAElementInfo, elements_from_uia_array

# region PATTERNS
AutomationElement = IUIA().ui_automation_client.IUIAutomationElement
DockPattern = IUIA().ui_automation_client.IUIAutomationDockPattern
ExpandCollapsePattern = IUIA().ui_automation_client.IUIAutomationExpandCollapsePattern
GridItemPattern = IUIA().ui_automation_client.IUIAutomationGridItemPattern
GridPattern = IUIA().ui_automation_client.IUIAutomationGridPattern
InvokePattern = IUIA().ui_automation_client.IUIAutomationInvokePattern
ItemContainerPattern = IUIA().ui_automation_client.IUIAutomationItemContainerPattern
LegacyIAccessiblePattern = IUIA().ui_automation_client.IUIAutomationLegacyIAccessiblePattern
MultipleViewPattern = IUIA().ui_automation_client.IUIAutomationMultipleViewPattern
RangeValuePattern = IUIA().ui_automation_client.IUIAutomationRangeValuePattern
ScrollItemPattern = IUIA().ui_automation_client.IUIAutomationScrollItemPattern
ScrollPattern = IUIA().ui_automation_client.IUIAutomationScrollPattern
SelectionItemPattern = IUIA().ui_automation_client.IUIAutomationSelectionItemPattern
SelectionPattern = IUIA().ui_automation_client.IUIAutomationSelectionPattern
SynchronizedInputPattern = IUIA().ui_automation_client.IUIAutomationSynchronizedInputPattern
TableItemPattern = IUIA().ui_automation_client.IUIAutomationTableItemPattern
TablePattern = IUIA().ui_automation_client.IUIAutomationTablePattern
TextPattern = IUIA().ui_automation_client.IUIAutomationTextPattern
TogglePattern = IUIA().ui_automation_client.IUIAutomationTogglePattern
TransformPattern = IUIA().ui_automation_client.IUIAutomationTransformPattern
ValuePattern = IUIA().ui_automation_client.IUIAutomationValuePattern
VirtualizedItemPattern = IUIA().ui_automation_client.IUIAutomationVirtualizedItemPattern
WindowPattern = IUIA().ui_automation_client.IUIAutomationWindowPattern
# endregion

# =========================================================================
_friendly_classes = {
    'Custom': None,
    'DataGrid': 'ListView',
    'DataItem': 'DataItem',
    'Document': None,  # TODO: this is RichTextBox
    'Group': 'GroupBox',
    'Header': None,
    'HeaderItem': None,
    'Hyperlink': None,
    'Image': None,
    'List': 'ListBox',
    'ListItem': 'ListItem',
    'MenuBar': 'Menu',
    'Menu': 'Menu',
    'MenuItem': 'MenuItem',
    'Pane': None,
    'ProgressBar': 'Progress',
    'ScrollBar': None,
    'Separator': None,
    'Slider': None,
    'Spinner': 'UpDown',
    'SplitButton': None,
    'Tab': 'TabControl',
    'Table': None,
    'Text': 'Static',
    'Thumb': None,
    'TitleBar': None,
    'ToolBar': 'Toolbar',
    'ToolTip': 'ToolTips',
    'Tree': 'TreeView',
    'TreeItem': 'TreeItem',
    'Window': 'Dialog',
}


# =========================================================================
class LazyProperty(object):

    """
    A lazy evaluation of an object attribute.

    The property should represent immutable data, as it replaces itself.
    Provided by: http://stackoverflow.com/a/6849299/1260742
    """

    def __init__(self, fget):
        """Init the property name and method to calculate the property"""
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        """Replace the property itself on a first access"""
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value
lazy_property = LazyProperty


# =========================================================================
class UiaMeta(BaseMeta):

    """Metaclass for UiaWrapper objects"""
    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""

        BaseMeta.__init__(cls, name, bases, attrs)

        for t in cls._control_types:
            UiaMeta.control_type_to_cls[t] = cls

    @staticmethod
    def find_wrapper(element):
        """Find the correct wrapper for this UIA element"""
        # Set a general wrapper by default
        wrapper_match = UIAWrapper

        # Check for a more specific wrapper in the registry
        if element.control_type in UiaMeta.control_type_to_cls:
            wrapper_match = UiaMeta.control_type_to_cls[element.control_type]

        return wrapper_match


# =========================================================================
@six.add_metaclass(UiaMeta)
class UIAWrapper(BaseWrapper):

    """
    Default wrapper for User Interface Automation (UIA) controls.

    All other UIA wrappers are derived from this.

    This class wraps a lot of functionality of underlying UIA features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """

    _control_types = []

    # ------------------------------------------------------------
    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(UIAWrapper, cls)._create_wrapper(cls, element_info, UIAWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid UIAElementInfo or it can be an
          instance or subclass of UIAWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['uia'])

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value based on the element's Runtime ID"""
        return hash(self.element_info.runtime_id)

    # ------------------------------------------------------------
    @lazy_property
    def iface_expand_collapse(self):
        """Get the element's ExpandCollapse interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "ExpandCollapse")

    # ------------------------------------------------------------
    @lazy_property
    def iface_selection(self):
        """Get the element's Selection interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Selection")

    # ------------------------------------------------------------
    @lazy_property
    def iface_selection_item(self):
        """Get the element's SelectionItem interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "SelectionItem")

    # ------------------------------------------------------------
    @lazy_property
    def iface_invoke(self):
        """Get the element's Invoke interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Invoke")

    # ------------------------------------------------------------
    @lazy_property
    def iface_toggle(self):
        """Get the element's Toggle interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Toggle")

    # ------------------------------------------------------------
    @lazy_property
    def iface_text(self):
        """Get the element's Text interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Text")

    # ------------------------------------------------------------
    @lazy_property
    def iface_value(self):
        """Get the element's Value interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Value")

    # ------------------------------------------------------------
    @lazy_property
    def iface_range_value(self):
        """Get the element's RangeValue interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "RangeValue")

    # ------------------------------------------------------------
    @lazy_property
    def iface_grid(self):
        """Get the element's Grid interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Grid")

    # ------------------------------------------------------------
    @lazy_property
    def iface_grid_item(self):
        """Get the element's GridItem interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "GridItem")

    # ------------------------------------------------------------
    @lazy_property
    def iface_table(self):
        """Get the element's Table interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Table")

    # ------------------------------------------------------------
    @lazy_property
    def iface_table_item(self):
        """Get the element's TableItem interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "TableItem")

    # ------------------------------------------------------------
    @lazy_property
    def iface_scroll_item(self):
        """Get the element's ScrollItem interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "ScrollItem")

    # ------------------------------------------------------------
    @lazy_property
    def iface_scroll(self):
        """Get the element's Scroll interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Scroll")

    # ------------------------------------------------------------
    @lazy_property
    def iface_transform(self):
        """Get the element's Transform interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Transform")

    # ------------------------------------------------------------
    @lazy_property
    def iface_transformV2(self):
        """Get the element's TransformV2 interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "TransformV2")

    # ------------------------------------------------------------
    @lazy_property
    def iface_window(self):
        """Get the element's Window interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "Window")

    # ------------------------------------------------------------
    @lazy_property
    def iface_item_container(self):
        """Get the element's ItemContainer interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "ItemContainer")

    # ------------------------------------------------------------
    @lazy_property
    def iface_virtualized_item(self):
        """Get the element's VirtualizedItem interface pattern"""
        elem = self.element_info.element
        return uia_defs.get_elem_interface(elem, "VirtualizedItem")

    # ------------------------------------------------------------
    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(UIAWrapper, self).writable_props
        props.extend(['is_keyboard_focusable',
                      'has_keyboard_focus',
                      'automation_id',
                      ])
        return props

    # ------------------------------------------------------------
    def legacy_properties(self):
        """Get the element's LegacyIAccessible control pattern interface properties"""
        elem = self.element_info.element
        impl = uia_defs.get_elem_interface(elem, "LegacyIAccessible")
        property_name_identifier = 'Current'

        interface_properties = [prop for prop in dir(LegacyIAccessiblePattern)
                                if (isinstance(getattr(LegacyIAccessiblePattern, prop), property)
                                and property_name_identifier in prop)]

        return {prop.replace(property_name_identifier, '') : getattr(impl, prop) for prop in interface_properties}

    # ------------------------------------------------------------
    def friendly_class_name(self):
        """
        Return the friendly class name for the control

        This differs from the class of the control in some cases.
        class_name() is the actual 'Registered' window class of the control
        while friendly_class_name() is hopefully something that will make
        more sense to the user.

        For example Checkboxes are implemented as Buttons - so the class
        of a CheckBox is "Button" - but the friendly class is "CheckBox"
        """
        if self.friendlyclassname is None:
            if self.element_info.control_type not in IUIA().known_control_types.keys():
                self.friendlyclassname = self.element_info.control_type
            else:
                ctrl_type = self.element_info.control_type
                if (ctrl_type not in _friendly_classes) or (_friendly_classes[ctrl_type] is None):
                    self.friendlyclassname = ctrl_type
                else:
                    self.friendlyclassname = _friendly_classes[ctrl_type]
        return self.friendlyclassname

    #------------------------------------------------------------
    def automation_id(self):
        """Return the Automation ID of the control"""
        return self.element_info.automation_id

    # -----------------------------------------------------------
    def is_keyboard_focusable(self):
        """Return True if the element can be focused with keyboard"""
        return self.element_info.element.CurrentIsKeyboardFocusable == 1

    # -----------------------------------------------------------
    def has_keyboard_focus(self):
        """Return True if the element is focused with keyboard"""
        return self.element_info.element.CurrentHasKeyboardFocus == 1

    # -----------------------------------------------------------
    def set_focus(self):
        """Set the focus to this element"""
        try:
            if self.is_minimized():
                if self.was_maximized():
                    self.maximize()
                else:
                    self.restore()
        except uia_defs.NoPatternInterfaceError:
            pass
        try:
            self.element_info.element.SetFocus()
        except comtypes.COMError as exc:
            warnings.warn('The window has not been focused due to ' \
                'COMError: {}'.format(exc), RuntimeWarning)

        return self

    # TODO: figure out how to implement .has_focus() method (if no handle available)

    # -----------------------------------------------------------
    def close(self):
        """
        Close the window

        Only a control supporting Window pattern should answer.
        If it doesn't (menu shadows, tooltips,...), try to send "Esc" key
        """
        try:
            name = self.element_info.name
            control_type = self.element_info.control_type

            iface = self.iface_window
            iface.Close()

            if name and control_type:
                self.actions.log("Closed " + control_type.lower() + ' "' +  name + '"')
        except(uia_defs.NoPatternInterfaceError):
            self.type_keys("{ESC}")

    # -----------------------------------------------------------
    def minimize(self):
        """
        Minimize the window

        Only controls supporting Window pattern should answer
        """
        iface = self.iface_window
        if iface.CurrentCanMinimize:
            iface.SetWindowVisualState(uia_defs.window_visual_state_minimized)
        return self

    # -----------------------------------------------------------
    def maximize(self):
        """
        Maximize the window

        Only controls supporting Window pattern should answer
        """
        iface = self.iface_window
        if iface.CurrentCanMaximize:
            iface.SetWindowVisualState(uia_defs.window_visual_state_maximized)
        return self

    # -----------------------------------------------------------
    def restore(self):
        """
        Restore the window to normal size

        Only controls supporting Window pattern should answer
        """
        iface = self.iface_window
        iface.SetWindowVisualState(uia_defs.window_visual_state_normal)
        return self

    # -----------------------------------------------------------
    def get_show_state(self):
        """Get the show state and Maximized/minimzed/restored state

        Returns values as following

        window_visual_state_normal = 0
        window_visual_state_maximized = 1
        window_visual_state_minimized = 2
        """
        iface = self.iface_window
        ret = iface.CurrentWindowVisualState

        return ret

    # -----------------------------------------------------------
    def is_minimized(self):
        """Indicate whether the window is minimized or not"""
        return self.get_show_state() == uia_defs.window_visual_state_minimized

    # -----------------------------------------------------------
    def is_maximized(self):
        """Indicate whether the window is maximized or not"""
        return self.get_show_state() == uia_defs.window_visual_state_maximized

    # -----------------------------------------------------------
    def is_normal(self):
        """Indicate whether the window is normal (i.e. not minimized and not maximized)"""
        return self.get_show_state() == uia_defs.window_visual_state_normal

    # -----------------------------------------------------------
    def invoke(self):
        """An interface to the Invoke method of the Invoke control pattern"""
        name = self.element_info.name
        control_type = self.element_info.control_type

        self.iface_invoke.Invoke()

        if name and control_type:
            self.actions.log("Invoked " + control_type.lower() + ' "' + name + '"')
        # Return itself to allow action chaining
        return self

    # -----------------------------------------------------------
    def expand(self):
        """
        Displays all child nodes, controls, or content of the control

        An interface to Expand method of the ExpandCollapse control pattern.
        """
        self.iface_expand_collapse.Expand()

        # Return itself to allow action chaining
        return self

    # -----------------------------------------------------------
    def collapse(self):
        """
        Displays all child nodes, controls, or content of the control

        An interface to Collapse method of the ExpandCollapse control pattern.
        """
        self.iface_expand_collapse.Collapse()

        # Return itself to allow action chaining
        return self

    # -----------------------------------------------------------
    def get_expand_state(self):
        """
        Indicates the state of the control: expanded or collapsed.

        An interface to CurrentExpandCollapseState property of the ExpandCollapse control pattern.
        Values for enumeration as defined in uia_defines module:
        expand_state_collapsed = 0
        expand_state_expanded = 1
        expand_state_partially = 2
        expand_state_leaf_node = 3
        """
        return self.iface_expand_collapse.CurrentExpandCollapseState

    # -----------------------------------------------------------
    def is_expanded(self):
        """Test if the control is expanded"""
        state = self.get_expand_state()
        return state == uia_defs.expand_state_expanded

    # -----------------------------------------------------------
    def is_collapsed(self):
        """Test if the control is collapsed"""
        state = self.get_expand_state()
        return state == uia_defs.expand_state_collapsed

    # -----------------------------------------------------------
    def get_selection(self):
        """
        An interface to GetSelection of the SelectionProvider pattern

        Retrieves a UI Automation provider for each child element
        that is selected. Builds a list of UIAElementInfo elements
        from all retrieved providers.
        """
        ptrs_array = self.iface_selection.GetCurrentSelection()
        return elements_from_uia_array(ptrs_array)

    # -----------------------------------------------------------
    def selected_item_index(self):
        """Return the index of a selected item"""
        # Go through all children and look for an index
        # of an item with the same text.
        # Maybe there is another and more efficient way to do it
        selection = self.get_selection()
        if selection:
            for i, c in enumerate(self.children()):
                if c.window_text() == selection[0].name:
                    return i
        return None

    # -----------------------------------------------------------
    def select(self):
        """Select the item

        Only items supporting SelectionItem pattern should answer.
        Raise NoPatternInterfaceError if the pattern is not supported

        Usually applied for controls like: a radio button, a tree view item
        or a list item.
        """
        self.iface_selection_item.Select()

        name = self.element_info.name
        control_type = self.element_info.control_type
        if name and control_type:
            self.actions.log("Selected " + control_type.lower() + ' "' + name + '"')

        # Return itself so that action can be chained
        return self

    # -----------------------------------------------------------
    def is_selected(self):
        """Indicate that the item is selected or not.

        Only items supporting SelectionItem pattern should answer.
        Raise NoPatternInterfaceError if the pattern is not supported

        Usually applied for controls like: a radio button, a tree view item,
        a list item.
        """
        return self.iface_selection_item.CurrentIsSelected

    # -----------------------------------------------------------
    def children_texts(self):
        """Get texts of the control's children"""
        return [c.window_text() for c in self.children()]

    # -----------------------------------------------------------
    def can_select_multiple(self):
        """
        An interface to CanSelectMultiple of the SelectionProvider pattern

        Indicates whether the UI Automation provider allows more than one
        child element to be selected concurrently.
        """
        return self.iface_selection.CurrentCanSelectMultiple

    # -----------------------------------------------------------
    def is_selection_required(self):
        """
        An interface to IsSelectionRequired property of the SelectionProvider pattern.

        This property can be dynamic. For example, the initial state of
        a control might not have any items selected by default,
        meaning that IsSelectionRequired is FALSE. However,
        after an item is selected the control must always have
        at least one item selected.
        """
        return self.iface_selection.CurrentIsSelectionRequired

    # -----------------------------------------------------------
    def _select(self, item=None):
        """
        Find a child item by the name or index and select

        The action can be applied for dirrent controls with items:
        ComboBox, TreeView, Tab control
        """
        if isinstance(item, six.integer_types):
            item_index = item
            title = None
        elif isinstance(item, six.string_types):
            item_index = 0
            title = item
        else:
            err_msg = u"unsupported {0} for item {1}".format(type(item), item)
            raise ValueError(err_msg)

        list_ = self.children(title=title)
        if item_index < len(list_):
            wrp = list_[item_index]
            wrp.iface_selection_item.Select()
        else:
            raise IndexError("item not found")

    # -----------------------------------------------------------
    def is_active(self):
        """Whether the window is active or not"""
        ae = IUIA().get_focused_element()
        focused_wrap = UIAWrapper(UIAElementInfo(ae))
        return (focused_wrap.top_level_parent() == self.top_level_parent())

    # -----------------------------------------------------------
    def is_dialog(self):
        """Return true if the control is a dialog window (WindowPattern interface is available)"""
        try:
            return self.iface_window is not None
        except uia_defs.NoPatternInterfaceError:
            return False

    # -----------------------------------------------------------
    def menu_select(self, path, exact=False, ):
        """Select a menu item specified in the path

        The full path syntax is specified in:
        :py:meth:`pywinauto.menuwrapper.Menu.get_menu_path`

        There are usually at least two menu bars: "System" and "Application"
        System menu bar is a standard window menu with items like:
        'Restore', 'Move', 'Size', 'Minimize', e.t.c.
        This menu bar usually has a "Title Bar" control as a parent.
        Application menu bar is often what we look for. In most cases,
        its parent is the dialog itself so it should be found among the direct
        children of the dialog. Notice that we don't use "Application"
        string as a title criteria because it couldn't work on applications
        with a non-english localization.
        If there is no menu bar has been found we fall back to look up
        for Menu control. We try to find the control through all descendants
        of the dialog
        """
        self.verify_actionable()

        cc = self.children(control_type="MenuBar")
        if not cc:
            cc = self.descendants(control_type="Menu")
            if not cc:
                raise AttributeError
        menu = cc[0]
        menu.item_by_path(path, exact).select()

    # -----------------------------------------------------------
    _scroll_types = {
        "left": {
            "line": (uia_defs.scroll_small_decrement, uia_defs.scroll_no_amount),
            "page": (uia_defs.scroll_large_decrement, uia_defs.scroll_no_amount),
        },
        "right": {
            "line": (uia_defs.scroll_small_increment, uia_defs.scroll_no_amount),
            "page": (uia_defs.scroll_large_increment, uia_defs.scroll_no_amount),
        },
        "up": {
            "line": (uia_defs.scroll_no_amount, uia_defs.scroll_small_decrement),
            "page": (uia_defs.scroll_no_amount, uia_defs.scroll_large_decrement),
        },
        "down": {
            "line": (uia_defs.scroll_no_amount, uia_defs.scroll_small_increment),
            "page": (uia_defs.scroll_no_amount, uia_defs.scroll_large_increment),
        },
    }

    def scroll(self, direction, amount, count=1, retry_interval=Timings.scroll_step_wait):
        """Ask the control to scroll itself

        **direction** can be any of "up", "down", "left", "right"
        **amount** can be only "line" or "page"
        **count** (optional) the number of times to scroll
        **retry_interval** (optional) interval between scroll actions
        """
        def _raise_attrib_err(details):
            control_type = self.element_info.control_type
            name = self.element_info.name
            msg = "".join([control_type.lower(), ' "', name, '" ', details])
            raise AttributeError(msg)

        try:
            scroll_if = self.iface_scroll
            if direction.lower() in ("up", "down"):
                if not scroll_if.CurrentVerticallyScrollable:
                    _raise_attrib_err('is not vertically scrollable')
            elif direction.lower() in ("left", "right"):
                if not scroll_if.CurrentHorizontallyScrollable:
                    _raise_attrib_err('is not horizontally scrollable')

            h, v = self._scroll_types[direction.lower()][amount.lower()]

            # Scroll as often as we have been asked to
            for _ in range(count, 0, -1):
                scroll_if.Scroll(h, v)
                time.sleep(retry_interval)

        except uia_defs.NoPatternInterfaceError:
            _raise_attrib_err('is not scrollable')
        except KeyError:
            raise ValueError("""Wrong arguments:
                direction can be any of "up", "down", "left", "right"
                amount can be only "line" or "page"
                """)

        return self


backend.register('uia', UIAElementInfo, UIAWrapper)
