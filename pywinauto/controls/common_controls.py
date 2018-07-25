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
"""
Classes that wrap the Windows Common controls

.. implicitly document some private classes
.. autoclass:: _toolbar_button
   :members:
   :show-inheritance:

.. autoclass:: _treeview_element
   :members:
   :show-inheritance:

.. autoclass:: _listview_item
   :members:
   :show-inheritance:
"""
from __future__ import print_function

import time
import ctypes
from ctypes import wintypes
import warnings
import locale
import six

from .. import sysinfo
from .. import win32functions
from .. import win32defines
from .. import win32structures
from .. import findbestmatch
from ..remote_memory_block import RemoteMemoryBlock
from . import hwndwrapper

from ..timings import Timings
from ..timings import wait_until
from ..timings import TimeoutError
from ..handleprops import is64bitprocess
from ..sysinfo import is_x64_Python
from .. import deprecated

if sysinfo.UIA_support:
    from ..uia_defines import IUIA


# Todo: I should return iterators from things like items() and texts()
#       to save building full lists all the time


class _listview_item(object):

    """Wrapper around ListView items"""

    #----------------------------------------------------------------
    def __init__(self, lv_ctrl, item_index, subitem_index=0):
        """Initialize the item"""
        self.listview_ctrl = lv_ctrl

        # ensure the item_index is an integer or
        # convert it to one
        self.item_index = self._as_item_index(item_index)
        self.subitem_index = subitem_index
        #self._as_parameter_ = self.item_index

    #-----------------------------------------------------------
    def _as_item_index(self, item):
        """Ensure that item is an item index

        If a string is passed in then it will be searched for in the
        list of item titles.
        """
        index = item
        if isinstance(item, six.string_types):
            index = int((self.listview_ctrl.texts().index(item) - 1) / self.listview_ctrl.column_count())

        return index

    #-----------------------------------------------------------
    def __eq__(self, other):
        """Return True if the parent control and the indexes are the same as the other."""
        if isinstance(other, _listview_item):
            return self.listview_ctrl == other.listview_ctrl and \
                self.item_index == other.item_index and \
                self.subitem_index == other.subitem_index
        else:
            return False

    #-----------------------------------------------------------
    def __ne__(self, other):
        """Return True if not matched the parent control or an index."""
        return not self == other

    #----------------------------------------------------------------
    def _readitem(self):
        """Read the list view item"""
        # set up a memory block in the remote application
        remote_mem = RemoteMemoryBlock(self.listview_ctrl)

        # set up the item structure to get the text
        item = self.listview_ctrl.LVITEM()
        item.mask = \
            win32defines.LVIF_TEXT | \
            win32defines.LVIF_IMAGE | \
            win32defines.LVIF_INDENT | \
            win32defines.LVIF_STATE

        item.iItem = self.item_index
        item.iSubItem = self.subitem_index
        item.stateMask = win32structures.UINT(-1)

        item.cchTextMax = 2000
        item.pszText = remote_mem.Address() + \
            ctypes.sizeof(item) + 1

        # Write the local LVITEM structure to the remote memory block
        remote_mem.Write(item)

        # Fill in the requested item
        retval = self.listview_ctrl.send_message(
            self.listview_ctrl.LVM_GETITEM,
            0,  # MSDN: wParam for LVM_GETITEM must be zero
            remote_mem)

        text = ''
        # if it succeeded
        if retval:

            remote_mem.Read(item)

            # Read the remote text string
            char_data = self.listview_ctrl.create_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            text = self.listview_ctrl.text_decode(char_data.value)

        else:
            raise RuntimeError(
                "We should never get to this part of ListView.get_item(), retval = " + str(retval) +
                ', GetLastError() = ' + str(ctypes.GetLastError()) +
                ', item_index = ' + str(self.item_index) + ', subitem_index = ' + str(self.subitem_index))

        del remote_mem

        return item, text

    #----------------------------------------------------------------
    def __getitem__(self, key):
        """Return property name"""
        warnings.warn('ListView item properties "text", "state", "image" and "indent" are deprecated! ' +
                      'Use methods text(), state(), image() and indent().', DeprecationWarning)

        item, text = self._readitem()
        if key == 'text':
            return text
        if key == 'state':
            return item.state
        if key == 'image':
            return item.iImage
        if key == 'indent':
            return item.iIndent

        raise KeyError('Incorrect property: "' + str(key) + '", can be "text", "state", "image" or "indent".')

    #----------------------------------------------------------------
    def text(self):
        """Return the text of the item"""
        return self._readitem()[1]
    # Non PEP-8 alias
    Text = deprecated(text)

    #----------------------------------------------------------------
    def item(self):
        """Return the item itself (LVITEM instance)"""
        return self._readitem()[0]
    # Non PEP-8 alias
    Item = deprecated(item)

    #----------------------------------------------------------------
    def item_data(self):
        """Return the item data (dictionary)"""
        item_data = {}

        item, text = self._readitem()
        # and add it to the titles
        item_data['text'] = text
        item_data['state'] = item.state
        item_data['image'] = item.iImage
        item_data['indent'] = item.iIndent

        return item_data
    # Non PEP-8 alias
    ItemData = deprecated(item_data)

    #----------------------------------------------------------------
    def state(self):
        """Return the state of the item"""
        return self.item().state
    # Non PEP-8 alias
    State = deprecated(state)

    #----------------------------------------------------------------
    def image(self):
        """Return the image index of the item"""
        return self.item().iImage
    # Non PEP-8 alias
    Image = deprecated(image)

    #----------------------------------------------------------------
    def indent(self):
        """Return the indent of the item"""
        return self.item().iIndent
    # Non PEP-8 alias
    Indent = deprecated(indent)

    #----------------------------------------------------------------
    def rectangle(self, area="all"):
        """Return the rectangle of the item.

        Possible ``area`` values:

        * ``"all"``  Returns the bounding rectangle of the entire item, including the icon and label.
        * ``"icon"``  Returns the bounding rectangle of the icon or small icon.
        * ``"text"``  Returns the bounding rectangle of the item text.
        * ``"select"``  Returns the union of the "icon" and "text" rectangles, but excludes columns in report view.
        """
        # set up a memory block in the remote application
        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        rect = win32structures.RECT()

        # If listview_ctrl has LVS_REPORT we can get access to subitems rectangles
        is_table = self.listview_ctrl.has_style(win32defines.LVS_REPORT)

        if area.lower() == "all" or not area:
            rect.left = win32defines.LVIR_BOUNDS
        elif area.lower() == "icon":
            rect.left = win32defines.LVIR_ICON
        elif area.lower() == "text":
            rect.left = win32defines.LVIR_LABEL
        elif area.lower() == "select":
            rect.left = win32defines.LVIR_BOUNDS if is_table else win32defines.LVIR_SELECTBOUNDS
        else:
            raise ValueError('Incorrect rectangle area of the list view item: "' + str(area) + '"')

        if is_table:
            # The one-based index of the subitem.
            rect.top = self.subitem_index

        # Write the local RECT structure to the remote memory block
        remote_mem.Write(rect)

        # Depends on subitems rectangles availability
        message = win32defines.LVM_GETSUBITEMRECT if is_table else win32defines.LVM_GETITEMRECT

        # Fill in the requested item
        retval = self.listview_ctrl.send_message(
            message,
            self.item_index,
            remote_mem)

        # If it's not succeeded
        if not retval:
            del remote_mem
            raise RuntimeError("Did not succeed in getting rectangle")

        rect = remote_mem.Read(rect)

        del remote_mem

        return rect
    # Non PEP-8 alias
    Rectangle = deprecated(rectangle)

    #----------------------------------------------------------------
    def click(self, button="left", double=False, where="text", pressed=""):
        """Click on the list view item

        where can be any one of "all", "icon", "text", "select", "check"
        defaults to "text"
        """
        self.ensure_visible()
        if where.lower() != "check":
            point_to_click = self.rectangle(area=where.lower()).mid_point()
            self.listview_ctrl.click(
                button,
                coords=(point_to_click.x, point_to_click.y),
                double=double,
                pressed=pressed)
        else:
            # Click on checkbox

            point_to_click = self.rectangle(area="icon").mid_point()
            point_to_click.y = self.rectangle(area="icon").bottom - 3
            # Check ListView display mode
            # (to be able to process 'Full Row Details' mode separately
            remote_mem = RemoteMemoryBlock(self.listview_ctrl)
            hittest = win32structures.LVHITTESTINFO()
            hittest.pt = point_to_click
            # Actually, there is no need to set hittest.iItem, because
            # send_message followed by remote_mem.Read always refreshes it
            #hittest.iItem = self.item_index
            hittest.iSubItem = self.subitem_index
            remote_mem.Write(hittest)
            self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
            remote_mem.Read(hittest)

            # Hittest flag
            checkbox_found = False
            if hittest.flags == win32defines.LVHT_ONITEMICON:

                # Large Icons, Small Icons, List, Details

                while not checkbox_found and point_to_click.x > 0:
                    point_to_click.x -= 1

                    hittest = win32structures.LVHITTESTINFO()
                    hittest.pt = point_to_click
                    #hittest.iItem = self.item_index
                    hittest.iSubItem = self.subitem_index
                    remote_mem.Write(hittest)
                    self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
                    remote_mem.Read(hittest)

                    if hittest.flags == win32defines.LVHT_ONITEMSTATEICON:
                        checkbox_found = True
                        break

            elif hittest.flags == win32defines.LVHT_ONITEM:

                # Full Row Details

                warnings.warn("Full Row Details 'check' area is detected in experimental mode. Use carefully!")
                point_to_click.x = self.rectangle(area="icon").left - 8
                # Check if point_to_click is still on item
                hittest = win32structures.LVHITTESTINFO()
                hittest.pt = point_to_click
                #hittest.iItem = self.item_index
                hittest.iSubItem = self.subitem_index
                remote_mem.Write(hittest)
                self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if hittest.flags == win32defines.LVHT_ONITEM:
                    checkbox_found = True
            else:
                raise RuntimeError("Unexpected hit test flags value " + str(hittest.flags) + " trying to find checkbox")

            # Click on the found checkbox
            if checkbox_found:
                self.listview_ctrl.click(
                    button,
                    coords=(point_to_click.x, point_to_click.y),
                    double=double,
                    pressed=pressed)
            else:
                raise RuntimeError("Area ('check') not found for this list view item")
        return self
    # Non PEP-8 alias
    Click = deprecated(click)

    #----------------------------------------------------------------
    def click_input(self, button="left", double=False, wheel_dist=0, where="text", pressed=""):
        """Click on the list view item

        where can be any one of "all", "icon", "text", "select", "check"
        defaults to "text"
        """
        self.ensure_visible()
        if where.lower() != "check":
            point_to_click = self.rectangle(area=where.lower()).mid_point()
            self.listview_ctrl.click_input(
                button,
                coords=(point_to_click.x, point_to_click.y),
                double=double,
                wheel_dist=wheel_dist,
                pressed=pressed)
        else:
            # Click on checkbox

            point_to_click = self.rectangle(area="icon").mid_point()
            point_to_click.y = self.rectangle(area="icon").bottom - 3
            # Check ListView display mode
            # (to be able to process 'Full Row Details' mode separately
            remote_mem = RemoteMemoryBlock(self.listview_ctrl)
            hittest = win32structures.LVHITTESTINFO()
            hittest.pt = point_to_click
            # Actually, there is no need to set hittest.iItem, because
            # send_message followed by remote_mem.Read always refreshes it
            #hittest.iItem = self.item_index
            hittest.iSubItem = self.subitem_index
            remote_mem.Write(hittest)
            self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
            remote_mem.Read(hittest)

            # Hittest flag
            checkbox_found = False
            if hittest.flags == win32defines.LVHT_ONITEMICON:

                # Large Icons, Small Icons, List, Details

                while not checkbox_found and point_to_click.x > 0:
                    point_to_click.x -= 1

                    hittest = win32structures.LVHITTESTINFO()
                    hittest.pt = point_to_click
                    #hittest.iItem = self.item_index
                    hittest.iSubItem = self.subitem_index
                    remote_mem.Write(hittest)
                    self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
                    remote_mem.Read(hittest)

                    if hittest.flags == win32defines.LVHT_ONITEMSTATEICON:
                        checkbox_found = True
                        break

            elif hittest.flags == win32defines.LVHT_ONITEM:

                # Full Row Details

                warnings.warn("Full Row Details 'check' area is detected in experimental mode. Use carefully!")
                point_to_click.x = self.rectangle(area="icon").left - 8
                # Check if point_to_click is still on item
                hittest = win32structures.LVHITTESTINFO()
                hittest.pt = point_to_click
                #hittest.iItem = self.item_index
                hittest.iSubItem = self.subitem_index
                remote_mem.Write(hittest)
                self.listview_ctrl.send_message(win32defines.LVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if hittest.flags == win32defines.LVHT_ONITEM:
                    checkbox_found = True
            else:
                raise RuntimeError("Unexpected hit test flags value " + str(hittest.flags) + " trying to find checkbox")

            # Click on the found checkbox
            if checkbox_found:
                self.listview_ctrl.click_input(
                    button,
                    coords=(point_to_click.x, point_to_click.y),
                    double=double,
                    wheel_dist=wheel_dist,
                    pressed=pressed)
            else:
                raise RuntimeError("Area ('check') not found for this list view item")
        return self
    # Non PEP-8 alias
    ClickInput = deprecated(click_input)

    #----------------------------------------------------------------
    def ensure_visible(self):
        """Make sure that the ListView item is visible"""
        if self.state() & win32defines.LVS_NOSCROLL:
            return None  # scroll is disabled
        ret = self.listview_ctrl.send_message(
            win32defines.LVM_ENSUREVISIBLE,
            self.item_index,
            win32defines.FALSE)
        if ret != win32defines.TRUE:
            raise RuntimeError('Fail to make the list view item visible ' +
                               '(item_index = ' + str(self.item_index) + ')')
        return self
    # Non PEP-8 alias
    EnsureVisible = deprecated(ensure_visible)

    #-----------------------------------------------------------
    def uncheck(self):
        """Uncheck the ListView item"""
        def index_to_state_image_mask(i):
            return i << 12

        self.listview_ctrl.verify_actionable()

        lvitem = self.listview_ctrl.LVITEM()

        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)
        lvitem.state = win32structures.UINT(index_to_state_image_mask(1))  # win32structures.UINT(0x1000)
        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_STATEIMAGEMASK)

        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem)

        retval = self.listview_ctrl.send_message(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        del remote_mem
        return self
    # Non PEP-8 alias
    UnCheck = deprecated(uncheck, deprecated_name='UnCheck')

    #-----------------------------------------------------------
    def check(self):
        """Check the ListView item"""

        def index_to_state_image_mask(i):
            return i << 12

        self.listview_ctrl.verify_actionable()

        lvitem = self.listview_ctrl.LVITEM()

        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)
        lvitem.state = win32structures.UINT(index_to_state_image_mask(2))  # win32structures.UINT(0x2000)
        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_STATEIMAGEMASK)

        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem)

        retval = self.listview_ctrl.send_message(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        del remote_mem
        return self
    # Non PEP-8 alias
    Check = deprecated(check)

    #-----------------------------------------------------------
    def is_checked(self):
        """Return whether the ListView item is checked or not"""
        state = self.listview_ctrl.send_message(
            win32defines.LVM_GETITEMSTATE,
            self.item_index,
            win32defines.LVIS_STATEIMAGEMASK)

        return state & 0x2000 == 0x2000
    # Non PEP-8 alias
    IsChecked = deprecated(is_checked)

    #-----------------------------------------------------------
    def is_selected(self):
        """Return True if the item is selected"""
        return win32defines.LVIS_SELECTED == self.listview_ctrl.send_message(
            win32defines.LVM_GETITEMSTATE, self.item_index, win32defines.LVIS_SELECTED)
    # Non PEP-8 alias
    IsSelected = deprecated(is_selected)

    #-----------------------------------------------------------
    def is_focused(self):
        """Return True if the item has the focus"""
        return win32defines.LVIS_FOCUSED == self.listview_ctrl.send_message(
            win32defines.LVM_GETITEMSTATE, self.item_index, win32defines.LVIS_FOCUSED)
    # Non PEP-8 alias
    IsFocused = deprecated(is_focused)

    #-----------------------------------------------------------
    def _modify_selection(self, to_select):
        """Change the selection of the item

        to_select should be True to select the item and false
        to deselect the item
        """
        self.listview_ctrl.verify_actionable()

        if self.item_index >= self.listview_ctrl.item_count():
            raise IndexError("There are only %d items in the list view not %d" %
                             (self.listview_ctrl.item_count(), self.item_index + 1))

        # first we need to change the state of the item
        lvitem = self.listview_ctrl.LVITEM()
        lvitem.mask = win32structures.UINT(win32defines.LVIF_STATE)

        if to_select:
            lvitem.state = win32structures.UINT(win32defines.LVIS_FOCUSED | win32defines.LVIS_SELECTED)

        lvitem.stateMask = win32structures.UINT(win32defines.LVIS_FOCUSED | win32defines.LVIS_SELECTED)

        remote_mem = RemoteMemoryBlock(self.listview_ctrl)
        remote_mem.Write(lvitem, size=ctypes.sizeof(lvitem))

        retval = self.listview_ctrl.send_message(
            win32defines.LVM_SETITEMSTATE, self.item_index, remote_mem)
        if retval != win32defines.TRUE:
            raise ctypes.WinError()  # ('retval = ' + str(retval))
        del remote_mem

        # now we need to notify the parent that the state has changed
        nmlv = win32structures.NMLISTVIEW()
        nmlv.hdr.hwndFrom = self.listview_ctrl.handle
        nmlv.hdr.idFrom = self.listview_ctrl.control_id()
        nmlv.hdr.code = win32defines.LVN_ITEMCHANGING

        nmlv.iItem = self.item_index
        #nmlv.iSubItem = 0
        nmlv.uNewState = win32defines.LVIS_SELECTED
        #nmlv.uOldState = 0
        nmlv.uChanged = win32defines.LVIS_SELECTED
        nmlv.ptAction = win32structures.POINT()

        new_remote_mem = RemoteMemoryBlock(self.listview_ctrl, size=ctypes.sizeof(nmlv))
        new_remote_mem.Write(nmlv, size=ctypes.sizeof(nmlv))

        retval = self.listview_ctrl.parent().send_message(
            win32defines.WM_NOTIFY,
            self.listview_ctrl.control_id(),
            new_remote_mem)
        #if retval != win32defines.TRUE:
        #    print('retval = ' + str(retval))
        #    raise ctypes.WinError()
        del new_remote_mem

        win32functions.WaitGuiThreadIdle(self.listview_ctrl)
        time.sleep(Timings.after_listviewselect_wait)

    #-----------------------------------------------------------
    def select(self):
        """Mark the item as selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised
        """
        self._modify_selection(True)
        return self
    # Non PEP-8 alias
    Select = deprecated(select)

    #-----------------------------------------------------------
    def deselect(self):
        """Mark the item as not selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised
        """
        self._modify_selection(False)
        return self
    # Non PEP-8 alias
    Deselect = deprecated(deselect)

    #-----------------------------------------------------------
    def inplace_control(self, friendly_class_name=""):
        """Return the editor HwndWrapper of the item

        Possible ``friendly_class_name`` values:

        * ``""``  Return the first appeared in-place control
        * ``"friendlyclassname"``  Returns editor with particular friendlyclassname
        """
        # If currently editing in this item or some other
        self.listview_ctrl.type_keys("{ENTER}")

        # Get a list of visible controls
        parent_dlg = self.listview_ctrl.top_level_parent()
        list_before_click = [w.handle for w in parent_dlg.element_info.descendants() if w.visible]

        # After a click on the visible list an editable element should appear
        self.click_input(double=True)
        def get_list_after_click():
            return [w.handle for w in parent_dlg.element_info.descendants() if w.visible]

        try:
            def check_func():
                return len(get_list_after_click()) > len(list_before_click)
            wait_until(Timings.listviewitemcontrol_timeout, 0.05, check_func)
        except TimeoutError:
            raise TimeoutError(("In-place-edit control for item ({0},{1}) not visible, possible it not editable, " +
                                "try to set slower timings").format(self.item_index, self.subitem_index));

        possible_inplace_ctrls = set(get_list_after_click()) - set(list_before_click)

        for handle in possible_inplace_ctrls:
            hwnd_friendly_class = hwndwrapper.HwndWrapper(handle).friendlyclassname
            if (friendly_class_name == "" or hwnd_friendly_class == friendly_class_name):
                return hwndwrapper.HwndWrapper(handle)

        names_list = [hwndwrapper.HwndWrapper(handle).friendlyclassname for handle in possible_inplace_ctrls]
        raise RuntimeError('In-place-edit control "{2}" for item ({0},{1}) not found in list {3}'.format(
                           self.item_index, self.subitem_index, friendly_class_name, names_list));


#====================================================================
class ListViewWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows ListView common control

    This class derives from HwndWrapper - so has all the methods o
    that class also

    **see** hwndwrapper.HwndWrapper_

    .. _hwndwrapper.HwndWrapper: class-pywinauto.controls.hwndwrapper.HwndWrapper.html

    """

    friendlyclassname = "ListView"
    windowclasses = [
        "SysListView32",
        r"WindowsForms\d*\.SysListView32\..*",
        "TSysListView",
        "ListView.*WndClass",
        ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_ListControlTypeId
        controltypes = []

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(ListViewWrapper, self).__init__(hwnd)

        if self.is_unicode():
            self.create_buffer = ctypes.create_unicode_buffer

            if is64bitprocess(self.process_id()) or not is_x64_Python():
                self.LVCOLUMN = win32structures.LVCOLUMNW
                self.LVITEM = win32structures.LVITEMW
            else:
                self.LVCOLUMN = win32structures.LVCOLUMNW32
                self.LVITEM = win32structures.LVITEMW32

            self.LVM_GETITEM = win32defines.LVM_GETITEMW
            self.LVM_GETCOLUMN = win32defines.LVM_GETCOLUMNW
            self.text_decode = lambda v: v
        else:
            self.create_buffer = ctypes.create_string_buffer

            if is64bitprocess(self.process_id()) or not is_x64_Python():
                self.LVCOLUMN = win32structures.LVCOLUMNW
                self.LVITEM = win32structures.LVITEMW
            else:
                self.LVCOLUMN = win32structures.LVCOLUMNW32
                self.LVITEM = win32structures.LVITEMW32

            self.LVM_GETCOLUMN = win32defines.LVM_GETCOLUMNA
            self.LVM_GETITEM = win32defines.LVM_GETITEMA
            self.text_decode = lambda v: v.decode(locale.getpreferredencoding())

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ListViewWrapper, self).writable_props
        props.extend(['column_count',
                      'item_count',
                      'columns',
                      'items',
                      ])
        return props

    #-----------------------------------------------------------
    def column_count(self):
        """Return the number of columns"""
        if self.get_header_control() is not None:
            return self.get_header_control().ItemCount()
        return 0
    # Non PEP-8 alias
    ColumnCount = deprecated(column_count)

    #-----------------------------------------------------------
    def item_count(self):
        """The number of items in the ListView"""
        return self.send_message(win32defines.LVM_GETITEMCOUNT)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    #-----------------------------------------------------------
    def get_header_control(self):
        """Returns the Header control associated with the ListView"""
        try:
            return hwndwrapper.HwndWrapper(
                self.send_message(win32defines.LVM_GETHEADER))
        except hwndwrapper.InvalidWindowHandle:
            return None
    # Non PEP-8 alias
    GetHeaderControl = deprecated(get_header_control)

    #-----------------------------------------------------------
    def get_column(self, col_index):
        """Get the information for a column of the ListView"""
        col_props = {}

        col = self.LVCOLUMN()
        col.mask = \
            win32defines.LVCF_FMT | \
            win32defines.LVCF_IMAGE | \
            win32defines.LVCF_ORDER | \
            win32defines.LVCF_SUBITEM | \
            win32defines.LVCF_TEXT | \
            win32defines.LVCF_WIDTH

        remote_mem = RemoteMemoryBlock(self)

        col.cchTextMax = 2000
        col.pszText = remote_mem.Address() + ctypes.sizeof(col) + 1

        # put the information in the memory that the
        # other process can read/write
        remote_mem.Write(col)

        # ask the other process to update the information
        retval = self.send_message(
            self.LVM_GETCOLUMN,
            col_index,
            remote_mem)

        col = remote_mem.Read(col)

        # if that succeeded then there was a column
        if retval:
            col = remote_mem.Read(col)

            text = self.create_buffer(2000)
            remote_mem.Read(text, col.pszText)

            col_props['order'] = col.iOrder
            col_props['text'] = self.text_decode(text.value)
            col_props['format'] = col.fmt
            col_props['width'] = col.cx
            col_props['image'] = col.iImage
            col_props['subitem'] = col.iSubItem

        del remote_mem

        return col_props
    # Non PEP-8 alias
    GetColumn = deprecated(get_column)

    #-----------------------------------------------------------
    def columns(self):
        """Get the information on the columns of the ListView"""
        cols = []

        for i in range(0, self.column_count()):
            cols.append(self.get_column(i))

        return cols
    # Non PEP-8 alias
    Columns = deprecated(columns)

    #-----------------------------------------------------------
    def column_widths(self):
        """Return a list of all the column widths"""
        return [col['width'] for col in self.columns()]
    # Non PEP-8 alias
    ColumnWidths = deprecated(column_widths)

    #-----------------------------------------------------------
    def get_item_rect(self, item_index):
        """Return the bounding rectangle of the list view item"""
        warnings.warn("Use get_item(item).rectangle() instead", DeprecationWarning)
        return self.get_item(item_index).rectangle()
    # Non PEP-8 alias
    GetItemRect = deprecated(get_item_rect)

    #-----------------------------------------------------------
    def get_item(self, item_index, subitem_index=0):
        """Return the item of the list view"

        * **item_index** Can be either an index of the item or a string
          with the text of the item you want returned.
        * **subitem_index** A zero based index of the item you want returned.
          Defaults to 0.
        """
        return _listview_item(self, item_index, subitem_index)

    item = get_item  # this is an alias to be consistent with other content elements
    # Non PEP-8 alias
    Item = deprecated(item)
    # Non PEP-8 alias
    GetItem = deprecated(get_item)

    #-----------------------------------------------------------
    def items(self):
        """Get all the items in the list view"""
        colcount = self.column_count()

        if not colcount:
            colcount = 1

        items = []
        # now get the item values...
        # for each of the rows
        for item_index in range(0, self.item_count()):

            # and each of the columns for that row
            for subitem_index in range(0, colcount):

                # get the item
                #yield self.get_item(item_index, subitem_index) # return iterator
                items.append(self.get_item(item_index, subitem_index))

        return items
    # Non PEP-8 alias
    Items = deprecated(items)

    #-----------------------------------------------------------
    def texts(self):
        """Get the texts for the ListView control"""
        texts = [self.window_text()]
        texts.extend([item['text'] for item in self.items()])
        return texts

    #-----------------------------------------------------------
    def uncheck(self, item):
        """Uncheck the ListView item"""
        warnings.warn("Use get_item(item).uncheck() instead", DeprecationWarning)
        return self.get_item(item).uncheck()
    # Non PEP-8 alias
    UnCheck = deprecated(uncheck, deprecated_name='UnCheck')

    #-----------------------------------------------------------
    def check(self, item):
        """Check the ListView item"""
        warnings.warn("Use get_item(item).check() instead", DeprecationWarning)
        return self.get_item(item).check()
    # Non PEP-8 alias
    Check = deprecated(check)

    #-----------------------------------------------------------
    def is_checked(self, item):
        """Return whether the ListView item is checked or not"""
        warnings.warn("Use get_item(item).is_checked() instead", DeprecationWarning)
        return self.get_item(item).is_checked()
    # Non PEP-8 alias
    IsChecked = deprecated(is_checked)

    #-----------------------------------------------------------
    def is_selected(self, item):
        """Return True if the item is selected"""
        warnings.warn("Use get_item(item).is_selected() instead", DeprecationWarning)
        return self.get_item(item).is_selected()
    # Non PEP-8 alias
    IsSelected = deprecated(is_selected)

    #-----------------------------------------------------------
    def is_focused(self, item):
        """Return True if the item has the focus"""
        warnings.warn("Use get_item(item).is_focused() instead", DeprecationWarning)
        return self.get_item(item).is_focused()
    # Non PEP-8 alias
    IsFocused = deprecated(is_focused)

    #-----------------------------------------------------------
    def select(self, item):
        """Mark the item as selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised
        """
        warnings.warn("Use get_item(item).select() instead", DeprecationWarning)
        return self.get_item(item).select()
    # Non PEP-8 alias
    Select = deprecated(select)

    #-----------------------------------------------------------
    def deselect(self, item):
        """Mark the item as not selected

        The ListView control must be enabled and visible before an
        Item can be selected otherwise an exception is raised
        """
        warnings.warn("Use get_item(item).deselect() instead", DeprecationWarning)
        return self.get_item(item).deselect()

    # Naming is not clear - so create an alias.
    #UnSelect = deselect
    # Non PEP-8 alias
    Deselect = deprecated(deselect)

    #-----------------------------------------------------------
    def get_selected_count(self):
        """Return the number of selected items"""
        return self.send_message(win32defines.LVM_GETSELECTEDCOUNT)
    # Non PEP-8 alias
    GetSelectedCount = deprecated(get_selected_count)


#====================================================================
class _treeview_element(object):

    """Wrapper around TreeView items"""
    #----------------------------------------------------------------
    def __init__(self, elem, tv_handle):
        """Initialize the item"""
        self.tree_ctrl = tv_handle
        self.elem = elem
        self._as_parameter_ = self.elem

    #----------------------------------------------------------------
    def text(self):
        """Return the text of the item"""
        return self._readitem()[1]
    # Non PEP-8 alias
    Text = deprecated(text)

    #----------------------------------------------------------------
    def item(self):
        """Return the item itself"""
        return self._readitem()[0]
    # Non PEP-8 alias
    Item = deprecated(item)

    #----------------------------------------------------------------
    def state(self):
        """Return the state of the item"""
        return self.item().state
    # Non PEP-8 alias
    State = deprecated(state)

    #-----------------------------------------------------------
    def is_checked(self):
        """Return whether the TreeView item is checked or not"""
        state = self.tree_ctrl.send_message(
            win32defines.TVM_GETITEMSTATE,
            self.elem,
            win32defines.TVIS_STATEIMAGEMASK)

        return state & 0x2000 == 0x2000
    # Non PEP-8 alias
    IsChecked = deprecated(is_checked)

    #----------------------------------------------------------------
    def client_rect(self, text_area_rect=True):
        """Return a rectangle of a text area of the item

        If **text_area_rect** is set to False then it will return
        a rectangle for the whole item (usually left is equal to 0).
        Defaults to True - which returns just the rectangle of the
        text of the item
        """
        remote_mem = RemoteMemoryBlock(self.tree_ctrl)

        # this is a bit weird
        # we have to write the element handle
        # but we read the rectangle afterwards!
        remote_mem.Write(win32structures.LPARAM(self.elem))

        ret = self.tree_ctrl.send_message(
            win32defines.TVM_GETITEMRECT, text_area_rect, remote_mem)

        # the item is not visible
        if not ret:
            rect = None
        else:
            # OK - it's visible so read it
            rect = win32structures.RECT()
            remote_mem.Read(rect)

        del remote_mem
        return rect
    # Non PEP-8 alias
    ClientRect = deprecated(client_rect)

    #----------------------------------------------------------------
    def click(self, button="left", double=False, where="text", pressed=""):
        """Click on the treeview item

        where can be any one of "text", "icon", "button", "check"
        defaults to "text"
        """
        self.ensure_visible()
        # find the text rectangle for the item,
        point_to_click = self.client_rect().mid_point()

        if where.lower() != "text":
            remote_mem = RemoteMemoryBlock(self.tree_ctrl)

            point_to_click.x = self.client_rect().left

            found = False
            while not found and point_to_click.x >= 0:

                hittest = win32structures.TVHITTESTINFO()
                hittest.pt = point_to_click
                hittest.hItem = self.elem

                remote_mem.Write(hittest)

                self.tree_ctrl.send_message(win32defines.TVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if where.lower() == 'button' and \
                   hittest.flags == win32defines.TVHT_ONITEMBUTTON:
                    found = True
                    break

                if where.lower() == 'icon' and \
                   hittest.flags == win32defines.TVHT_ONITEMICON:
                    found = True
                    break

                if where.lower() == 'check' and \
                   hittest.flags == win32defines.TVHT_ONITEMSTATEICON:
                    found = True
                    break

                point_to_click.x -= 1

            if not found:
                raise RuntimeError("Area ('{}') not found for this tree view item".format(where))

        self.tree_ctrl.click(
            button,
            coords=(point_to_click.x, point_to_click.y),
            double=double,
            pressed=pressed)
        return self
        # XXX: somehow it works for 64-bit explorer.exe on Win8.1,
        # but it doesn't work for 32-bit ControlSpyV6.exe
        #absolute = True)

        # TODO: if we use click instead of clickInput - then we need to tell the
        # treeview to update itself
        #self.tree_ctrl.
    # Non PEP-8 alias
    Click = deprecated(click)

    #----------------------------------------------------------------
    def click_input(self, button="left", double=False, wheel_dist=0, where="text", pressed=""):
        """Click on the treeview item

        where can be any one of "text", "icon", "button", "check"
        defaults to "text"
        """
        self.ensure_visible()
        # find the text rectangle for the item,
        point_to_click = self.client_rect().mid_point()

        if where.lower() != "text":
            remote_mem = RemoteMemoryBlock(self.tree_ctrl)

            point_to_click.x = self.client_rect().left

            found = False
            while not found and point_to_click.x >= 0:

                hittest = win32structures.TVHITTESTINFO()
                hittest.pt = point_to_click
                hittest.hItem = self.elem

                remote_mem.Write(hittest)

                self.tree_ctrl.send_message(win32defines.TVM_HITTEST, 0, remote_mem)
                remote_mem.Read(hittest)

                if where.lower() == 'button' and \
                   hittest.flags == win32defines.TVHT_ONITEMBUTTON:
                    found = True
                    break

                if where.lower() == 'icon' and \
                   hittest.flags == win32defines.TVHT_ONITEMICON:
                    found = True
                    break

                if where.lower() == 'check' and \
                   hittest.flags == win32defines.TVHT_ONITEMSTATEICON:
                    found = True
                    break

                point_to_click.x -= 1

            if not found:
                raise RuntimeError("Area ('%s') not found for this tree view item" % where)

        self.tree_ctrl.click_input(
            button,
            coords=(point_to_click.x, point_to_click.y),
            double=double,
            wheel_dist=wheel_dist,
            pressed=pressed)
        return self
    # Non PEP-8 alias
    ClickInput = deprecated(click_input)

    #----------------------------------------------------------------
    def start_dragging(self, button='left', pressed=''):
        """Start dragging the item"""
        #self.ensure_visible()
        # find the text rectangle for the item
        rect = self.client_rect()
        point_to_click = rect.mid_point()

        #self.tree_ctrl.set_focus()
        self.tree_ctrl.press_mouse_input(
            button, coords=(point_to_click.x, point_to_click.y), pressed=pressed, absolute=False)
        for i in range(5):
            self.tree_ctrl.move_mouse_input(
                coords=(rect.left + i, rect.top), pressed=pressed, absolute=False)
        return self
    # Non PEP-8 alias
    StartDragging = deprecated(start_dragging)

    #----------------------------------------------------------------
    def drop(self, button='left', pressed=''):
        """Drop at the item"""
        #self.ensure_visible()
        # find the text rectangle for the item
        point_to_click = self.client_rect().mid_point()

        self.tree_ctrl.move_mouse_input(
            coords=(point_to_click.x, point_to_click.y), pressed=pressed, absolute=False)
        time.sleep(Timings.drag_n_drop_move_mouse_wait)

        self.tree_ctrl.release_mouse_input(
            button, coords=(point_to_click.x, point_to_click.y), pressed=pressed, absolute=False)
        time.sleep(Timings.after_drag_n_drop_wait)
        return self
    # Non PEP-8 alias
    Drop = deprecated(drop)

    #----------------------------------------------------------------
    def collapse(self):
        """Collapse the children of this tree view item"""
        self.tree_ctrl.send_message(
            win32defines.TVM_EXPAND,
            win32defines.TVE_COLLAPSE,
            self.elem)
        return self
    # Non PEP-8 alias
    Collapse = deprecated(collapse)

    #----------------------------------------------------------------
    def expand(self):
        """Expand the children of this tree view item"""
        self.tree_ctrl.send_message(
            win32defines.TVM_EXPAND,
            win32defines.TVE_EXPAND,
            self.elem)
        return self
    # Non PEP-8 alias
    Expand = deprecated(expand)

    #----------------------------------------------------------------
    def children(self):
        """Return the direct children of this control"""
        if self.item().cChildren not in (0, 1):
            print("##### not dealing with that TVN_GETDISPINFO stuff yet")

        # No children
        #if self.__item.cChildren == 0:
        #    pass

        children_elements = []
        if self.item().cChildren == 1:

            # Get the first child of this element
            child_elem = self.tree_ctrl.send_message(
                win32defines.TVM_GETNEXTITEM,
                win32defines.TVGN_CHILD,
                self.elem)

            if child_elem:
                children_elements.append(_treeview_element(child_elem, self.tree_ctrl))

                # now get all the next children
                while True:
                    next_child = children_elements[-1].next_item()

                    if next_child is not None:
                        children_elements.append(next_child)
                    else:
                        break

            else:
                return []
                #raise ctypes.WinError()

        return children_elements
    # Non PEP-8 alias
    Children = deprecated(children)

    #----------------------------------------------------------------
    def next_item(self):
        """Return the next item"""
        # get the next element
        next_elem = self.tree_ctrl.send_message(
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_NEXT,
            self.elem)

        if next_elem:
            return _treeview_element(next_elem, self.tree_ctrl)

        return None
        # don't raise - as it just meant that there was no
        # next
        #else:
        #    raise ctypes.WinError()
    # Non PEP-8 alias
    Next = deprecated(next_item, deprecated_name='Next')

    #----------------------------------------------------------------
    def sub_elements(self):
        """Return the list of children of this control"""
        sub_elems = []

        for child in self.children():
            sub_elems.append(child)

            sub_elems.extend(child.sub_elements())

        return sub_elems
    # Non PEP-8 alias
    SubElements = deprecated(sub_elements)

    #----------------------------------------------------------------
    def get_child(self, child_spec, exact=False):
        """Return the child item of this item

        Accepts either a string or an index.
        If a string is passed then it returns the child item
        with the best match for the string.
        """
        #print child_spec

        if isinstance(child_spec, six.string_types):

            texts = [c.text() for c in self.children()]
            if exact:
                if child_spec in texts:
                    index = texts.index(child_spec)
                else:
                    raise IndexError('There is no child equal to "' + str(child_spec) + '" in ' + str(texts))
            else:
                indices = range(0, len(texts))
                index = findbestmatch.find_best_match(
                    child_spec, texts, indices, limit_ratio=.6)

            #if len(matching) > 1 :
            #    raise RuntimeError(
            #        "There are multiple children that match that spec '%s'"%
            #            child_spec)

        else:
            index = child_spec

        return self.children()[index]
    # Non PEP-8 alias
    GetChild = deprecated(get_child)

    #----------------------------------------------------------------
    def ensure_visible(self):
        """Make sure that the TreeView item is visible"""
        self.tree_ctrl.send_message(
            win32defines.TVM_ENSUREVISIBLE,
            win32defines.TVGN_CARET,
            self.elem)
        win32functions.WaitGuiThreadIdle(self.tree_ctrl)
        return self
    # Non PEP-8 alias
    EnsureVisible = deprecated(ensure_visible)

    #----------------------------------------------------------------
    def select(self):
        """Select the TreeView item"""
        # http://stackoverflow.com/questions/14111333/treeview-set-default-select-item-and-highlight-blue-this-item
        # non-focused TreeView can ignore TVM_SELECTITEM
        self.tree_ctrl.set_focus()

        retval = self.tree_ctrl.send_message(
            win32defines.TVM_SELECTITEM,  # message
            win32defines.TVGN_CARET,      # how to select
            self.elem)                    # item to select

        if retval != win32defines.TRUE:
            raise ctypes.WinError()
        return self
    # Non PEP-8 alias
    Select = deprecated(select)

    #----------------------------------------------------------------
    def is_selected(self):
        """Indicate that the TreeView item is selected or not"""
        return win32defines.TVIS_SELECTED == (win32defines.TVIS_SELECTED & self.state())
    # Non PEP-8 alias
    IsSelected = deprecated(is_selected)

    #----------------------------------------------------------------
    def is_expanded(self):
        """Indicate that the TreeView item is selected or not"""
        return win32defines.TVIS_EXPANDED == (win32defines.TVIS_EXPANDED & self.state())
    # Non PEP-8 alias
    IsExpanded = deprecated(is_expanded)

    #----------------------------------------------------------------
    def _readitem(self):
        """Read the treeview item"""
        remote_mem = RemoteMemoryBlock(self.tree_ctrl)

        if is64bitprocess(self.tree_ctrl.process_id()) or not is_x64_Python():
            item = win32structures.TVITEMW()
        else:
            item = win32structures.TVITEMW32()

        item.mask = win32defines.TVIF_TEXT | \
            win32defines.TVIF_HANDLE | \
            win32defines.TVIF_CHILDREN | \
            win32defines.TVIF_STATE

        # set the address for the text
        item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 16
        item.cchTextMax = 2000
        item.hItem = self.elem
        item.stateMask = win32structures.UINT(-1)

        # Write the local TVITEM structure to the remote memory block
        remote_mem.Write(item)

        # read the entry
        retval = self.tree_ctrl.send_message(
            win32defines.TVM_GETITEMW,
            0,
            remote_mem)

        text = ''
        if retval:
            remote_mem.Read(item)

            #self.__item = item
            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)

            text = char_data.value
        else:
            # seems that this may not always be correct
            raise ctypes.WinError()

        return item, text


#====================================================================
class TreeViewWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows TreeView common control"""

    friendlyclassname = "TreeView"
    windowclasses = [
        "SysTreeView32", r"WindowsForms\d*\.SysTreeView32\..*", "TTreeView", "TreeList.TreeListCtrl"]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_TreeControlTypeId]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(TreeViewWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(TreeViewWrapper, self).writable_props
        props.extend(['item_count'])
        return props

    #----------------------------------------------------------------
    def item_count(self):
        """Return the count of the items in the treeview"""
        return self.send_message(win32defines.TVM_GETCOUNT)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    #----------------------------------------------------------------
    def texts(self):
        """Return all the text for the tree view"""
        texts = [self.window_text(), ]
        if self.item_count():
            texts.append(self.tree_root().text())
            elements = self.tree_root().sub_elements()

            texts.extend([elem.text() for elem in elements])

        return texts

    #----------------------------------------------------------------
    def tree_root(self):
        """Return the root element of the tree view"""
        # get the root item:
        root_elem = self.send_message(
            win32defines.TVM_GETNEXTITEM,
            win32defines.TVGN_ROOT)

        # Sometimes there is no root element
        if not root_elem:
            return None

        return _treeview_element(root_elem, self)
    # Non PEP-8 alias
    Root = deprecated(tree_root, deprecated_name='Root')

    #----------------------------------------------------------------
    def roots(self):
        """Get root items of the control"""
        roots = []

        cur_elem = self.tree_root()
        while cur_elem:
            roots.append(cur_elem)

            cur_elem = cur_elem.Next()

        return roots
    # Non PEP-8 alias
    Roots = deprecated(roots)

    #----------------------------------------------------------------
    def get_properties(self):
        """Get the properties for the control as a dictionary"""
        props = super(TreeViewWrapper, self).get_properties()

        props['item_count'] = self.item_count()

        return props

    #----------------------------------------------------------------
    def get_item(self, path, exact=False):
        r"""Read the TreeView item

        * **path** the path to the item to return. This can be one of
          the following:

          * A string separated by \\ characters. The first character must
            be \\. This string is split on the \\ characters and each of
            these is used to find the specific child at each level. The
            \\ represents the root item - so you don't need to specify the
            root itself.
          * A list/tuple of strings - The first item should be the root
            element.
          * A list/tuple of integers - The first item the index which root
            to select.
        """
        # work is just based on integers for now

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
            texts = [r.text() for r in roots]
            #not used var: indices = range(0, len(texts))
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

        # get the correct lowest level item
#        current_elem.get_child
#        for i in range(0, path[0]):
#            current_elem = current_elem.next_item()
#
#            if current_elem is None:
#                raise IndexError("Root Item '%s' does not have %d sibling(s)"%
#                    (self.tree_root().window_text(), i + 1))
#
        # remove the first (empty) item and the root element as we have
        # dealt with it (string or integer)
        path = path[1:]

        # now for each of the lower levels
        # just index into it's children
        for child_spec in path:

            # ensure that the item is expanded (as this is sometimes required
            # for loading the tree view branches
            current_elem.expand()

            try:
                current_elem = current_elem.get_child(child_spec, exact)
            except IndexError:
                if isinstance(child_spec, six.string_types):
                    raise IndexError("Item '%s' does not have a child '%s'" %
                                     (current_elem.text(), child_spec))
                else:
                    raise IndexError("Item '%s' does not have %d children" %
                                     (current_elem.text(), child_spec + 1))

            # self.send_message_timeout(
            #    win32defines.TVM_EXPAND,
            #    win32defines.TVE_EXPAND,
            #    current_elem)

        return current_elem

    item = get_item  # this is an alias to be consistent with other content elements
    # Non PEP-8 alias
    Item = deprecated(item)
    # Non PEP-8 alias
    GetItem = deprecated(get_item)

    #----------------------------------------------------------------
    def select(self, path):
        """Select the treeview item"""
        # http://stackoverflow.com/questions/14111333/treeview-set-default-select-item-and-highlight-blue-this-item
        # non-focused TreeView can ignore TVM_SELECTITEM
        self.set_focus()

        elem = self.get_item(path)
        retval = self.send_message(
            win32defines.TVM_SELECTITEM,  # message
            win32defines.TVGN_CARET,      # how to select
            elem.elem)                    # item to select

        if retval != win32defines.TRUE:
            raise ctypes.WinError()

        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_treeviewselect_wait)
    # Non PEP-8 alias
    Select = deprecated(select)

    #-----------------------------------------------------------
    def is_selected(self, path):
        """Return True if the item is selected"""
        return win32defines.TVIS_SELECTED == (win32defines.TVIS_SELECTED &
                                              self.get_item(path).State())
    # Non PEP-8 alias
    IsSelected = deprecated(is_selected)

    #----------------------------------------------------------------
    def ensure_visible(self, path):
        """Make sure that the TreeView item is visible"""
        elem = self.get_item(path)
        return elem.ensure_visible()
    # Non PEP-8 alias
    EnsureVisible = deprecated(ensure_visible)

    #----------------------------------------------------------------
    def print_items(self):
        """Print all items with line indents"""
        self.text = self.window_text() + "\n"

        def print_one_level(item, ident):
            """Get texts for the item and its children"""
            self.text += " " * ident + item.text() + "\n"
            for child in item.children():
                print_one_level(child, ident + 1)

        for root in self.roots():
            print_one_level(root, 0)

        return self.text
    # Non PEP-8 alias
    PrintItems = deprecated(print_items)

#   #-----------------------------------------------------------
#    def uncheck(self, path):
#        """Uncheck the ListView item"""
#        self.verify_actionable()
#
#        elem = self.get_item(path)
#
##        lvitem = win32structures.LVITEMW()
##
##        lvitem.mask = win32defines.LVIF_STATE
##        lvitem.state = 0x1000
##        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK
##
##        remote_mem = RemoteMemoryBlock(self)
##        remote_mem.Write(lvitem)
##
##        self.send_message(
##            win32defines.LVM_SETITEMSTATE, item, remote_mem)
##
##        del remote_mem
#
#
#    #-----------------------------------------------------------
#    def check(self, path):
#        """Check the ListView item"""
#        self.verify_actionable()
#
#        elem = self.get_item(path)
#
#        #lvitem = win32structures.LVITEMW()
#
#        lvitem.mask = win32defines.LVIF_STATE
#        lvitem.state = 0x2000
#        lvitem.stateMask = win32defines.LVIS_STATEIMAGEMASK
#
#        remote_mem = RemoteMemoryBlock(self)
#        remote_mem.Write(lvitem)
#
#        self.send_message(
#            win32defines.LVM_SETITEMSTATE, item, remote_mem)
#
#        del remote_mem
#
#    #-----------------------------------------------------------
#    def is_checked(self, path):
#        """Return whether the ListView item is checked or not"""
#        elem = self.get_item(path)
#
#        elem.state
#
#        state = self.send_message(
#            win32defines.LVM_GETITEMSTATE,
#            item,
#            win32defines.LVIS_STATEIMAGEMASK)
#
#        return state & 0x2000


#====================================================================
class HeaderWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows ListView Header common control"""

    friendlyclassname = "Header"
    windowclasses = ["SysHeader32", "msvb_lib_header"]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_HeaderControlTypeId]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(HeaderWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def item_count(self):
        """Return the number of columns in this header"""
        # get the number of items in the header...
        return self.send_message(win32defines.HDM_GETITEMCOUNT)
    # Non PEP-8 alias
    ItemCount = deprecated(item_count)

    #----------------------------------------------------------------
    def get_column_rectangle(self, column_index):
        """Return the rectangle for the column specified by column_index"""

        remote_mem = RemoteMemoryBlock(self)
        # get the column rect
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        retval = self.send_message(
            win32defines.HDM_GETITEMRECT,
            column_index,
            remote_mem)

        if retval:
            rect = remote_mem.Read(rect)
        else:
            raise ctypes.WinError()

        del remote_mem

        return rect
    # Non PEP-8 alias
    GetColumnRectangle = deprecated(get_column_rectangle)

    #----------------------------------------------------------------
    def client_rects(self):
        """Return all the client rectangles for the header control"""
        rects = [self.client_rect(), ]

        for col_index in range(0, self.item_count()):

            rects.append(self.get_column_rectangle(col_index))

        return rects

    #----------------------------------------------------------------
    def get_column_text(self, column_index):
        """Return the text for the column specified by column_index"""
        remote_mem = RemoteMemoryBlock(self)

        item = win32structures.HDITEMW()
        item.mask = win32defines.HDI_FORMAT | \
            win32defines.HDI_WIDTH | \
            win32defines.HDI_TEXT  # | HDI_ORDER
        item.cchTextMax = 2000

        # set up the pointer to the text
        # it should be at the
        item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1

        # put the information in the memory that the
        # other process can read/write
        remote_mem.Write(item)

        # ask the other process to update the information
        retval = self.send_message(
            win32defines.HDM_GETITEMW,
            column_index,
            remote_mem)

        if retval:
            item = remote_mem.Read(item)

            # Read the remote text string
            char_data = ctypes.create_unicode_buffer(2000)
            remote_mem.Read(char_data, item.pszText)
            return char_data.value

        return None
    # Non PEP-8 alias
    GetColumnText = deprecated(get_column_text)

    #----------------------------------------------------------------
    def texts(self):
        """Return the texts of the Header control"""
        texts = [self.window_text(), ]
        for i in range(0, self.item_count()):
            texts.append(self.get_column_text(i))

        return texts

#    #----------------------------------------------------------------
#    def _fill_header_info(self):
#        """Get the information from the header control"""
#        remote_mem = RemoteMemoryBlock(self)
#
#        for col_index in range(0, self.Count()):
#
#            item = win32structures.HDITEMW()
#            item.mask = win32defines.HDI_FORMAT | \
#                win32defines.HDI_WIDTH | \
#                win32defines.HDI_TEXT #| HDI_ORDER
#            item.cchTextMax = 2000
#
#            # set up the pointer to the text
#            # it should be at the
#            item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
#
#            # put the information in the memory that the
#            # other process can read/write
#            remote_mem.Write(item)
#
#            # ask the other process to update the information
#            retval = self.send_message(
#                win32defines.HDM_GETITEMW,
#                col_index,
#                remote_mem)
#
#            if retval:
#                item = remote_mem.Read(item)
#
#                # Read the remote text string
#                charData = ctypes.create_unicode_buffer(2000)
#                remote_mem.Read(charData, item.pszText)
#                self._extra_texts.append(charData.value)


#====================================================================
class StatusBarWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Status Bar common control"""

    friendlyclassname = "StatusBar"
    windowclasses = [
        "msctls_statusbar32",
        ".*StatusBar",
        r"WindowsForms\d*\.msctls_statusbar32\..*"]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_StatusBarControlTypeId]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(StatusBarWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(StatusBarWrapper, self).writable_props
        props.extend(['border_widths',
                      'part_count',
                      'part_right_edges',
                      ])
        return props

    #----------------------------------------------------------------
    def border_widths(self):
        """Return the border widths of the StatusBar

        A dictionary of the 3 available widths is returned:
        Horizontal - the horizontal width
        Vertical - The width above and below the status bar parts
        Inter - The width between parts of the status bar
        """
        remote_mem = RemoteMemoryBlock(self)

        # get the borders for each of the areas there can be a border.
        borders = (ctypes.c_int * 3)()
        remote_mem.Write(borders)
        self.send_message(
            win32defines.SB_GETBORDERS,
            0,
            remote_mem
        )
        borders = remote_mem.Read(borders)
        borders_widths = {}
        borders_widths['Horizontal'] = borders[0]
        borders_widths['Vertical'] = borders[1]
        borders_widths['Inter'] = borders[2]

        del remote_mem

        return borders_widths
    # Non PEP-8 alias
    BorderWidths = deprecated(border_widths)

    #----------------------------------------------------------------
    def part_count(self):
        """Return the number of parts"""
        # get the number of parts for this status bar
        return self.send_message(
            win32defines.SB_GETPARTS,
            0,
            0)
    # Non PEP-8 alias
    PartCount = deprecated(part_count)

    #----------------------------------------------------------------
    def part_right_edges(self):
        """Return the widths of the parts"""
        remote_mem = RemoteMemoryBlock(self)

        # get the number of parts for this status bar
        parts = (ctypes.c_int * self.part_count())()
        remote_mem.Write(parts)
        self.send_message(
            win32defines.SB_GETPARTS,
            self.part_count(),
            remote_mem
        )

        parts = remote_mem.Read(parts)

        del remote_mem

        return [int(part) for part in parts]
    # Non PEP-8 alias
    PartRightEdges = deprecated(part_right_edges)

    #----------------------------------------------------------------
    def get_part_rect(self, part_index):
        """Return the rectangle of the part specified by part_index"""
        if part_index >= self.part_count():
            raise IndexError(
                "Only {0} parts available you asked for part {1} (zero based)".format(
                    self.part_count(), part_index))

        remote_mem = RemoteMemoryBlock(self)

        # get the rectangle for this item
        rect = win32structures.RECT()
        remote_mem.Write(rect)
        self.send_message(
            win32defines.SB_GETRECT,
            part_index,
            remote_mem)

        rect = remote_mem.Read(rect)
        del remote_mem
        return rect
    # Non PEP-8 alias
    GetPartRect = deprecated(get_part_rect)

    #----------------------------------------------------------------
    def client_rects(self):
        """Return the client rectangles for the control"""
        rects = [self.client_rect()]

        for i in range(self.part_count()):
            rects.append(self.get_part_rect(i))

        return rects

    #----------------------------------------------------------------
    def get_part_text(self, part_index):
        """Return the text of the part specified by part_index"""
        if part_index >= self.part_count():
            raise IndexError(
                "Only {0} parts available you asked for part {1} (zero based)".format(
                    self.part_count(), part_index))

        remote_mem = RemoteMemoryBlock(self)

        textlen = self.send_message(
            win32defines.SB_GETTEXTLENGTHW,
            part_index,
            0
        )

        #draw_operation = win32functions.HiWord(textlen)
        textlen = win32functions.LoWord(textlen)

        # get the text for this item
        text = ctypes.create_unicode_buffer(textlen + ctypes.sizeof(ctypes.c_wchar))
        remote_mem.Write(text)
        self.send_message(
            win32defines.SB_GETTEXTW,
            part_index,
            remote_mem
        )

        text = remote_mem.Read(text)

        del remote_mem
        return text.value
    # Non PEP-8 alias
    GetPartText = deprecated(get_part_text)

    #----------------------------------------------------------------
    def texts(self):
        """Return the texts for the control"""
        texts = [self.window_text()]

        for i in range(self.part_count()):
            texts.append(self.get_part_text(i))

        return texts


#====================================================================
class TabControlWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Tab common control"""

    friendlyclassname = "TabControl"
    windowclasses = [
        "SysTabControl32",
        r"WindowsForms\d*\.SysTabControl32\..*"]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_TabControlTypeId]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(TabControlWrapper, self).__init__(hwnd)

        #self.writable_props.append("TabStates")

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(TabControlWrapper, self).writable_props
        props.extend(['tab_count'])
        return props

    #----------------------------------------------------------------
    def row_count(self):
        """Return the number of rows of tabs"""
        return self.send_message(win32defines.TCM_GETROWCOUNT)
    # Non PEP-8 alias
    RowCount = deprecated(row_count)

    #----------------------------------------------------------------
    def get_selected_tab(self):
        """Return the index of the selected tab"""
        return self.send_message(win32defines.TCM_GETCURSEL)
    # Non PEP-8 alias
    GetSelectedTab = deprecated(get_selected_tab)

    #----------------------------------------------------------------
    def tab_count(self):
        """Return the number of tabs"""
        return self.send_message(win32defines.TCM_GETITEMCOUNT)
    # Non PEP-8 alias
    TabCount = deprecated(tab_count)

    #----------------------------------------------------------------
    def get_tab_rect(self, tab_index):
        """Return the rectangle to the tab specified by tab_index"""
        if tab_index >= self.tab_count():
            raise IndexError(
                "Only {0} tabs available you asked for tab {1} (zero based)".format(
                    self.tab_count(), tab_index))

        remote_mem = RemoteMemoryBlock(self)

        rect = win32structures.RECT()
        remote_mem.Write(rect)

        self.send_message(
            win32defines.TCM_GETITEMRECT, tab_index, remote_mem)

        remote_mem.Read(rect)

        del remote_mem

        return rect
    # Non PEP-8 alias
    GetTabRect = deprecated(get_tab_rect)

#    #----------------------------------------------------------------
#    def get_tab_state(self, tab_index):
#        """Return the state of the tab"""
#        if tab_index >= self.tab_count():
#            raise IndexError(
#                "Only %d tabs available you asked for tab %d (zero based)" % (
#                self.tab_count(),
#                tab_index))
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        item = win32structures.TCITEMW()
#        item.mask = win32defines.TCIF_STATE
#        remote_mem.Write(item)
#
#        ret = self.send_message(
#            win32defines.TCM_GETITEMW, tab_index, remote_mem)
#
#        remote_mem.Read(item)
#        del remote_mem
#
#        if not ret:
#            raise ctypes.WinError()
#
#        return item.dwState
#    # Non PEP-8 alias
#    GetTabState = deprecated(get_tab_state)

    #----------------------------------------------------------------
    def get_tab_text(self, tab_index):
        """Return the text of the tab"""
        if tab_index >= self.tab_count():
            raise IndexError(
                "Only {0} tabs available you asked for tab {1} (zero based)".format(
                    self.tab_count(), tab_index))

        remote_mem = RemoteMemoryBlock(self)

        item = win32structures.TCITEMW()
        item.mask = win32defines.TCIF_TEXT
        item.cchTextMax = 1999
        item.pszText = remote_mem.Address() + ctypes.sizeof(item)
        remote_mem.Write(item)

        self.send_message(
            win32defines.TCM_GETITEMW, tab_index, remote_mem)

        remote_mem.Read(item)

        # Read the text that has been written
        text = ctypes.create_unicode_buffer(2000)
        text = remote_mem.Read(text, remote_mem.Address() + ctypes.sizeof(item))

        return text.value
    # Non PEP-8 alias
    GetTabText = deprecated(get_tab_text)

    #----------------------------------------------------------------
    def get_properties(self):
        """Return the properties of the TabControl as a Dictionary"""
        props = super(TabControlWrapper, self).get_properties()

        props['tab_count'] = self.tab_count()

        return props

#    #----------------------------------------------------------------
#    def tab_states(self):
#        """Return the tab state for all the tabs"""
#        states = []
#        for i in range(0, self.tab_count()):
#            states.append(self.GetTabState(i))
#        return states
#    # Non PEP-8 alias
#    TabStates = deprecated(tab_states)

    #----------------------------------------------------------------
    def client_rects(self):
        """Return the client rectangles for the Tab Control"""
        rects = [self.client_rect()]
        for tab_index in range(0, self.tab_count()):
            rects.append(self.get_tab_rect(tab_index))

        return rects

    #----------------------------------------------------------------
    def texts(self):
        """Return the texts of the Tab Control"""
        texts = [self.window_text()]

        for i in range(0, self.tab_count()):
            texts.append(self.get_tab_text(i))

        return texts

    #----------------------------------------------------------------
    def select(self, tab):
        """Select the specified tab on the tab control"""
        self.verify_actionable()
        logging_tab = tab

        # if it's a string then find the index of
        # the tab with that text
        if isinstance(tab, six.string_types):
            # find the string in the tab control
            best_text = findbestmatch.find_best_match(
                tab, self.texts(), self.texts())
            tab = self.texts().index(best_text) - 1

        if tab >= self.tab_count():
            raise IndexError(
                "Only {0} tabs available you asked for tab {1} (zero based)".format(
                    self.tab_count(), tab))

        if self.has_style(win32defines.TCS_BUTTONS):
            # workaround for TCS_BUTTONS case
            self.click(coords=self.get_tab_rect(tab))

            # TCM_SETCURFOCUS changes focus, but doesn't select the tab
            # TCM_SETCURSEL selects the tab, but tab content is not re-drawn
            # (TODO: need to find a solution without WM_CLICK)

            #self.Notify(win32defines.TCN_SELCHANGING)
            #self.send_message(win32defines.TCM_SETCURSEL, tab)
            #self.Notify(win32defines.TCN_SELCHANGE)
        else:
            self.send_message(win32defines.TCM_SETCURFOCUS, tab)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_tabselect_wait)
        self.actions.log('Selected tab "' + str(logging_tab) + '"')

        return self
    # Non PEP-8 alias
    Select = deprecated(select)


#====================================================================
class _toolbar_button(object):

    """Wrapper around Toolbar button (TBBUTTONINFO) items"""

    #----------------------------------------------------------------
    def __init__(self, index_, tb_handle):
        """Initialize the item"""
        self.toolbar_ctrl = tb_handle
        self.index = index_
        self.info = self.toolbar_ctrl.get_button(self.index)

    #----------------------------------------------------------------
    def rectangle(self):
        """Get the rectangle of a button on the toolbar"""
        remote_mem = RemoteMemoryBlock(self.toolbar_ctrl)

        rect = win32structures.RECT()

        remote_mem.Write(rect)
        self.toolbar_ctrl.send_message(win32defines.TB_GETRECT,
                                       self.info.idCommand,
                                       remote_mem)
        rect = remote_mem.Read(rect)

        if rect == win32structures.RECT(0, 0, 0, 0):
            self.toolbar_ctrl.send_message(win32defines.TB_GETITEMRECT,
                                           self.index,
                                           remote_mem)
            rect = remote_mem.Read(rect)

        del remote_mem

        return rect
    # Non PEP-8 alias
    Rectangle = deprecated(rectangle)

#    #----------------------------------------------------------------
#    def press(self, press = True):
#        """Find where the button is and click it"""
#        if press:
#            press_flag = win32functions.MakeLong(0, 1)
#        else:
#            press_flag = 0
#
#        ret = self.toolbar_ctrl.send_message_timeout(
#            win32defines.TB_PRESSBUTTON,
#            self.info.idCommand,
#            press_flag)
#
#        # Notify the parent that we are finished selecting
#        #self.toolbar_ctrl.notify_parent(win32defines.TBN_TOOLBARCHANGE)
#
#        win32functions.WaitGuiThreadIdle(self.toolbar_ctrl)
#        time.sleep(Timings.after_toobarpressbutton_wait)
#    # Non PEP-8 alias
#    Press = deprecated(press)
#
#    #----------------------------------------------------------------
#    def press(self):
#        """Find where the button is and click it"""
#        self.Press(press = False)
#    # Non PEP-8 alias
#    Press = deprecated(press)
#
#    #----------------------------------------------------------------
#    def check(self, check = True):
#        """Find where the button is and click it"""
#        if check:
#            check_flag = win32functions.MakeLong(0, 1)
#        else:
#            check_flag = 0
#
#        ret = self.toolbar_ctrl.send_message_timeout(
#            win32defines.TB_CHECKBUTTON,
#            self.info.idCommand,
#            check_flag)
#
#        # Notify the parent that we are finished selecting
#        #self.toolbar_ctrl.notify_parent(win32defines.TBN_TOOLBARCHANGE)
#
#        win32functions.WaitGuiThreadIdle(self.toolbar_ctrl)
#        time.sleep(Timings.after_toobarpressbutton_wait)
#
#    #----------------------------------------------------------------
#    def uncheck(self):
#        self.check(check = False)

    #----------------------------------------------------------------
    def text(self):
        """Return the text of the button"""
        return self.info.text
    # Non PEP-8 alias
    Text = deprecated(text)

    #----------------------------------------------------------------
    def style(self):
        """Return the style of the button"""
        return self.toolbar_ctrl.send_message(
            win32defines.TB_GETSTYLE, self.info.idCommand)
    # Non PEP-8 alias
    Style = deprecated(style)

    #----------------------------------------------------------------
    def has_style(self, style):
        """Return True if the button has the specified style"""
        return self.style() & style == style
    # Non PEP-8 alias
    HasStyle = deprecated(has_style)

    #----------------------------------------------------------------
    def state(self):
        """Return the state of the button"""
        return self.toolbar_ctrl.send_message(
            win32defines.TB_GETSTATE, self.info.idCommand)
    # Non PEP-8 alias
    State = deprecated(state)

    #----------------------------------------------------------------
    def is_checkable(self):
        """Return if the button can be checked"""
        return self.has_style(win32defines.TBSTYLE_CHECK)
    # Non PEP-8 alias
    IsCheckable = deprecated(is_checkable)

    #----------------------------------------------------------------
    def is_pressable(self):
        """Return if the button can be pressed"""
        return self.has_style(win32defines.TBSTYLE_BUTTON)
    # Non PEP-8 alias
    IsPressable = deprecated(is_pressable)

    #----------------------------------------------------------------
    def is_checked(self):
        """Return if the button is in the checked state"""
        return self.state() & win32defines.TBSTATE_CHECKED == win32defines.TBSTATE_CHECKED
    # Non PEP-8 alias
    IsChecked = deprecated(is_checked)

    #----------------------------------------------------------------
    def is_pressed(self):
        """Return if the button is in the pressed state"""
        return self.state() & win32defines.TBSTATE_PRESSED == win32defines.TBSTATE_PRESSED
    # Non PEP-8 alias
    IsPressed = deprecated(is_pressed)

    #----------------------------------------------------------------
    def is_enabled(self):
        """Return if the button is in the pressed state"""
        # make sure it has an ID
        if not self.info.idCommand:
            return False

        return self.state() & win32defines.TBSTATE_ENABLED == win32defines.TBSTATE_ENABLED
    # Non PEP-8 alias
    IsEnabled = deprecated(is_enabled)

    #----------------------------------------------------------------
    def click(self, button="left", pressed=""):
        """Click on the Toolbar button"""
        self.toolbar_ctrl.click(button=button, coords=self.rectangle(), pressed=pressed)
        time.sleep(Timings.after_toobarpressbutton_wait)
    # Non PEP-8 alias
    Click = deprecated(click)

    #----------------------------------------------------------------
    def click_input(self, button="left", double=False, wheel_dist=0, pressed=""):
        """Click on the Toolbar button"""
        self.toolbar_ctrl.click_input(button=button, coords=self.rectangle().mid_point(),
                                      double=double, wheel_dist=wheel_dist, pressed=pressed)
        time.sleep(Timings.after_toobarpressbutton_wait)
    # Non PEP-8 alias
    ClickInput = deprecated(click_input)


#====================================================================
class ToolbarWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Toolbar common control"""

    friendlyclassname = "Toolbar"
    windowclasses = [
        "ToolbarWindow32",
        r"WindowsForms\d*\.ToolbarWindow32\..*",
        "Afx:ToolBar:.*"]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(ToolbarWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ToolbarWrapper, self).writable_props
        props.extend(['button_count'])
        return props

    #----------------------------------------------------------------
    def button_count(self):
        """Return the number of buttons on the ToolBar"""
        return self.send_message(win32defines.TB_BUTTONCOUNT)
    # Non PEP-8 alias
    ButtonCount = deprecated(button_count)

    #----------------------------------------------------------------
    def button(self, button_identifier, exact=True, by_tooltip=False):
        """Return the button at index button_index"""
        if isinstance(button_identifier, six.string_types):
            texts = self.texts()[1:]
            self.actions.log('Toolbar buttons: ' + str(texts))
            # one of these will be returned for the matching text
            indices = [i for i in range(0, len(texts))]

            if by_tooltip:
                texts = self.tip_texts()
                self.actions.log('Toolbar tooltips: ' + str(texts))

            if exact:
                try:
                    button_index = texts.index(button_identifier)
                except ValueError:
                    raise findbestmatch.MatchError(items=texts, tofind=button_identifier)
            else:
                # find which index best matches that text
                button_index = findbestmatch.find_best_match(button_identifier, texts, indices)
        else:
            button_index = button_identifier

        return _toolbar_button(button_index, self)
    # Non PEP-8 alias
    Button = deprecated(button)

    #----------------------------------------------------------------
    def get_button_struct(self, button_index):
        """Return TBBUTTON structure on the Toolbar button"""
        if button_index >= self.button_count():
            raise IndexError(
                "0 to {0} are acceptaple for button_index".format(self.button_count()))

        remote_mem = RemoteMemoryBlock(self)

        if is64bitprocess(self.process_id()) or not is_x64_Python():
            button = win32structures.TBBUTTON()
        else:
            button = win32structures.TBBUTTON32()

        remote_mem.Write(button)

        ret = self.send_message(
            win32defines.TB_GETBUTTON, button_index, remote_mem)

        if not ret:
            del remote_mem
            raise RuntimeError(
                "get_button failed for button index {0}".format(button_index))

        remote_mem.Read(button)
        del remote_mem

        return button
    # Non PEP-8 alias
    GetButtonStruct = deprecated(get_button_struct)

    #----------------------------------------------------------------
    def get_button(self, button_index):
        """Return information on the Toolbar button"""
        button = self.get_button_struct(button_index)

        if is64bitprocess(self.process_id()) or not is_x64_Python():
            button_info = win32structures.TBBUTTONINFOW()
        else:
            button_info = win32structures.TBBUTTONINFOW32()

        button_info.cbSize = ctypes.sizeof(button_info)
        button_info.dwMask = \
            win32defines.TBIF_COMMAND | \
            win32defines.TBIF_SIZE | \
            win32defines.TBIF_STYLE | \
            win32defines.TBIF_IMAGE | \
            win32defines.TBIF_LPARAM | \
            win32defines.TBIF_STATE | \
            win32defines.TBIF_TEXT
        #win32defines.TBIF_IMAGELABEL | \

        button_info.cchText = 2000

        remote_mem = RemoteMemoryBlock(self)

        # set the text address to after the structures
        button_info.pszText = remote_mem.Address() + \
            ctypes.sizeof(button_info)

        # fill the button_info structure
        remote_mem.Write(button_info)
        ret = self.send_message(
            win32defines.TB_GETBUTTONINFOW,
            button.idCommand,
            remote_mem)
        remote_mem.Read(button_info)

        if ret == -1:
            del remote_mem
            raise RuntimeError('GetButtonInfo failed for button with command' +
                               ' id {0}'.format(button.idCommand))

        # read the text
        button_info.text = ctypes.create_unicode_buffer(1999)
        remote_mem.Read(button_info.text, remote_mem.Address() +
                        ctypes.sizeof(button_info))

        button_info.text = button_info.text.value

        del remote_mem

        return button_info
    # Non PEP-8 alias
    GetButton = deprecated(get_button)

    #----------------------------------------------------------------
    def texts(self):
        """Return the texts of the Toolbar"""
        texts = [self.window_text()]
        for i in range(0, self.button_count()):
            btn_text = self.get_button(i).text
            lines = btn_text.split('\n')
            if lines:
                texts.append(lines[0])
            else:
                texts.append(btn_text)

        return texts

    #----------------------------------------------------------------
    def tip_texts(self):
        """Return the tip texts of the Toolbar (without window text)"""
        texts = []
        for i in range(0, self.button_count()):

            # it works for MFC
            btn_tooltip_index = self.get_button_struct(i).iString
            # usually iString == -1 for separator

            # other cases if any
            if not (-1 <= btn_tooltip_index < self.get_tool_tips_control().tool_count()):
                btn_tooltip_index = i

            btn_text = self.get_tool_tips_control().get_tip_text(btn_tooltip_index + 1)
            texts.append(btn_text)

        return texts
    # Non PEP-8 alias
    TipTexts = deprecated(tip_texts)

    #----------------------------------------------------------------
    def get_button_rect(self, button_index):
        """Get the rectangle of a button on the toolbar"""
        return self.button(button_index).rectangle()
    # Non PEP-8 alias
    GetButtonRect = deprecated(get_button_rect)

    #----------------------------------------------------------------
    def get_tool_tips_control(self):
        """Return the tooltip control associated with this control"""
        return ToolTipsWrapper(self.send_message(win32defines.TB_GETTOOLTIPS))
    # Non PEP-8 alias
    GetToolTipsControl = deprecated(get_tool_tips_control)

#    def right_click(self, button_index, **kwargs):
#        """Right click for Toolbar buttons"""
#
#        win32functions.SetCapture(self)
#
#        button = self.get_button(button_index)
#        #print button.text
#
#        rect = self.get_button_rect(button_index)
#
#        x = (rect.left + rect.right) /2
#        y = (rect.top + rect.bottom) /2
#
#        #print x, y
#
#
#        self.move_mouse_input(coords = (x, y))
#        self.send_message(
#            win32defines.WM_MOUSEACTIVATE,
#            self.parent().parent().parent(),
#            win32functions.MakeLong(
#                win32defines.WM_RBUTTONDOWN,
#                win32defines.HTCLIENT)
#            )
#
#        self.press_mouse(pressed = "right", button = "right", coords = (x, y))
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        # now we need to notify the parent that the state has changed
#        nmlv = win32structures.NMMOUSE()
#        nmlv.hdr.hwndFrom = self.handle
#        nmlv.hdr.idFrom = self.control_id()
#        nmlv.hdr.code = win32defines.NM_RCLICK
#
#
#        nmlv.dwItemSpec = button.idCommand
#        #nmlv.dwItemData
#
#        nmlv.pt = win32structures.POINT()
#
#        remote_mem.Write(nmlv)
#
#        self.send_message(
#            win32defines.WM_NOTIFY,
#            self.control_id(),
#            remote_mem)
#
#        del remote_mem
#
#
#        self.release_mouse(button = "right", coords = (x, y))
#
#        win32functions.ReleaseCapture()
#    # Non PEP-8 alias
#    Right_Click = deprecated(right_click)

    #----------------------------------------------------------------
    def press_button(self, button_identifier, exact=True):
        """Find where the button is and click it"""
        msg = 'Clicking "' + self.window_text() + '" toolbar button "' + str(button_identifier) + '"'
        self.actions.logSectionStart(msg)
        self.actions.log(msg)
        button = self.button(button_identifier, exact=exact)

        # transliterated from
        # http://source.winehq.org/source/dlls/comctl32/toolbar.c

        # if the button is enabled
        if button.is_enabled():
            button.click_input()
        else:
            raise RuntimeError('Toolbar button "' + str(button_identifier) + '" is disabled! Cannot click it.')
        self.actions.logSectionEnd()
    # Non PEP-8 alias
    PressButton = deprecated(press_button)

    #----------------------------------------------------------------
    def check_button(self, button_identifier, make_checked, exact=True):
        """Find where the button is and click it if it's unchecked and vice versa"""
        self.actions.logSectionStart('Checking "' + self.window_text() +
                                     '" toolbar button "' + str(button_identifier) + '"')
        button = self.button(button_identifier, exact=exact)
        if make_checked:
            self.actions.log('Pressing down toolbar button "' + str(button_identifier) + '"')
        else:
            self.actions.log('Pressing up toolbar button "' + str(button_identifier) + '"')

        # TODO: add waiting for a button state
        if not button.is_enabled():
            self.actions.log('Toolbar button is not enabled!')
            raise RuntimeError("Toolbar button is not enabled!")

        if button.is_checked() != make_checked:
            button.click_input()

            # wait while button has changed check state
            #i = 0
            #while button.is_checked() != make_checked:
            #    time.sleep(0.5)
            #    i += 1
            #    if i > 10:
            #        raise RuntimeError("Cannot wait button check state!")
        self.actions.logSectionEnd()
    # Non PEP-8 alias
    CheckButton = deprecated(check_button)

    #----------------------------------------------------------------
    def menu_bar_click_input(self, path, app):
        """Select menu bar items by path (experimental!)

        The path is specified by a list of items separated by '->' each Item
        can be the zero based index of the item to return prefaced by # e.g. #1.

        Example:
            "#1 -> #0",
            "#1->#0->#0"
        """
        warnings.warn("menu_bar_click_input method is experimental. Use carefully!")

        self.actions.logSectionStart('Clicking "{0}" menu bar path "{1}"'.format(self.window_text(), path))
        if isinstance(path, list):
            parts = path
        else:
            parts = path.split("->")
        indices = []
        for part in parts:
            if isinstance(part, int):
                indices.append(part)
            else:
                item_string = part.strip().lstrip('#')
                try:
                    index = int(item_string)
                except Exception:
                    raise TypeError('Path must contain integers only!')
                indices.append(index)

        # circle import doesn't work with current package structure
        # so use the app instance as a method param
        #app = Application().Connect(handle=self.handle)

        current_toolbar = self
        for i, index in enumerate(indices):
            windows_before = app.Windows_(visible_only=True)
            current_toolbar.button(index).click_input()
            if i < len(indices) - 1:
                wait_until(5, 0.1, lambda: len(app.Windows_(visible_only=True)) > len(windows_before))
                windows_after = app.Windows_(visible_only=True)
                new_window = set(windows_after) - set(windows_before)
                current_toolbar = list(new_window)[0].children()[0]
        self.actions.logSectionEnd()
    # Non PEP-8 alias
    MenuBarClickInput = deprecated(menu_bar_click_input)

#    #----------------------------------------------------------------
#    def _fill_toolbar_info(self):
#        """Get the information from the toolbar"""
#        buttonCount = self.send_message(win32defines.TB_BUTTONCOUNT)
#        self._extra_props['button_count'] = buttonCount
#
#        remote_mem = RemoteMemoryBlock(self)
#
#        for i in range(0, buttonCount):
#
#            button = win32structures.TBBUTTON()
#
#            remote_mem.Write(button)
#
#            self.send_message(
#                win32defines.TB_GETBUTTON, i, remote_mem)
#
#            remote_mem.Read(button)
#
#            buttonInfo = win32structures.TBBUTTONINFOW()
#            buttonInfo.cbSize = ctypes.sizeof(buttonInfo)
#            buttonInfo.dwMask = win32defines.TBIF_TEXT | \
#                win32defines.TBIF_COMMAND | \
#                win32defines.TBIF_SIZE | \
#                win32defines.TBIF_COMMAND | \
#                win32defines.TBIF_STYLE | \
#                win32defines.TBIF_STATE
#
#            buttonInfo.cchText = 2000
#
#            # set the text address to after the structures
#            buttonInfo.pszText = remote_mem.Address() + \
#                ctypes.sizeof(buttonInfo)
#
#            # fill the buttonInfo structure
#            remote_mem.Write(buttonInfo)
#            self.send_message(
#                win32defines.TB_GETBUTTONINFOW,
#                button.idCommand,
#                remote_mem)
#            remote_mem.Read(buttonInfo)
#
#            # read the text
#            text = ctypes.create_unicode_buffer(1999)
#            remote_mem.Read(text, remote_mem.Address() + \
#                ctypes.sizeof(buttonInfo))
#
#            extendedStyle = self.send_message(win32defines.TB_GETEXTENDEDSTYLE)
#
#            self._extra_props.setdefault('Buttons', []).append(
#                dict(
#                    iBitMap = button.iBitmap,
#                    idCommand = button.idCommand,
#                    fsState = button.fsState,
#                    fsStyle = button.fsStyle,
#                    cx = buttonInfo.cx,
#                    exstyle = extendedStyle
#                )
#            )
#    #        if button.fsStyle & TBSTYLE_DROPDOWN == TBSTYLE_DROPDOWN and \
#    #            (extendedStyle & TBSTYLE_EX_DRAWDDARROWS) != \
#    #                TBSTYLE_EX_DRAWDDARROWS:
#    #            props['Buttons'][-1]["DROPDOWNMENU"] = 1
#    #
#    #            self.send_message(WM_COMMAND, button.idCommand)
#    #
#    #            print "Pressing", text.value
#    #            handle.send_message(TB_PRESSBUTTON, button.idCommand, 1)
#    #            handle.send_message(TB_PRESSBUTTON, button.idCommand, 0)
#
#            self._extra_texts.append(text.value)
#
#
# RB_GETBANDBORDERS


class BandWrapper(win32structures.REBARBANDINFOW):

    """Simple wrapper around REBARBANDINFOW to allow setting new attributes"""

    pass


#====================================================================
class ReBarWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows ReBar common control"""

    friendlyclassname = "ReBar"
    windowclasses = ["ReBarWindow32", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(ReBarWrapper, self).__init__(hwnd)

    @property
    def writable_props(self):
        """Extend default properties list."""
        props = super(ReBarWrapper, self).writable_props
        props.extend(['band_count'])
        return props

    #----------------------------------------------------------------
    def band_count(self):
        """Return the number of bands in the control"""
        return self.send_message(win32defines.RB_GETBANDCOUNT)
    # Non PEP-8 alias
    BandCount = deprecated(band_count)

    #----------------------------------------------------------------
    def get_band(self, band_index):
        """Get a band of the ReBar control"""
        if band_index >= self.band_count():
            raise IndexError(('band_index {0} greater then number of' +
                              ' available bands: {1}').format(band_index, self.band_count()))

        remote_mem = RemoteMemoryBlock(self)

        band_info = BandWrapper()

        band_info.cbSize = ctypes.sizeof(band_info)
        band_info.fMask = \
            win32defines.RBBIM_CHILD | \
            win32defines.RBBIM_CHILDSIZE | \
            win32defines.RBBIM_COLORS | \
            win32defines.RBBIM_HEADERSIZE | \
            win32defines.RBBIM_ID | \
            win32defines.RBBIM_IDEALSIZE | \
            win32defines.RBBIM_SIZE | \
            win32defines.RBBIM_STYLE | \
            win32defines.RBBIM_TEXT

        # set the pointer for the text
        band_info.lpText = win32structures.LPWSTR(
            remote_mem.Address() + ctypes.sizeof(band_info))
        band_info.cch = 2000

        # write the structure
        remote_mem.Write(band_info)

        # Fill the structure
        self.send_message(
            win32defines.RB_GETBANDINFOW,
            band_index,
            remote_mem)

        # read it back
        remote_mem.Read(band_info)

        # read the text
        band_info.text = ctypes.create_unicode_buffer(2000)
        remote_mem.Read(band_info.text, remote_mem.Address() + ctypes.sizeof(band_info))

        band_info.text = band_info.text.value

        del remote_mem
        return band_info
    # Non PEP-8 alias
    GetBand = deprecated(get_band)

    #----------------------------------------------------------------
    def get_tool_tips_control(self):
        """Return the tooltip control associated with this control"""
        tips_handle = self.send_message(win32defines.RB_GETTOOLTIPS)

        if tips_handle:
            return ToolTipsWrapper(tips_handle)
    # Non PEP-8 alias
    GetToolTipsControl = deprecated(get_tool_tips_control)

    #----------------------------------------------------------------
    def texts(self):
        """Return the texts of the Rebar"""
        texts = [self.window_text()]
        for i in range(0, self.band_count()):
            band = self.get_band(i)
            lines = band.text.split('\n')
            if lines:
                texts.append(lines[0])
            else:
                texts.append(band.text)

        return texts


#====================================================================
class ToolTip(object):

    """Class that Wraps a single tip from a ToolTip control"""

    def __init__(self, ctrl, tip_index):
        """Read the required information"""
        self.ctrl = ctrl
        self.index = tip_index

        remote_mem = RemoteMemoryBlock(self.ctrl)
        tipinfo = win32structures.TOOLINFOW()
        tipinfo.cbSize = ctypes.sizeof(tipinfo)
        #tipinfo.uId = self.index
        tipinfo.lpszText = remote_mem.Address() + \
            ctypes.sizeof(tipinfo) + 1

        remote_mem.Write(tipinfo)

        self.ctrl.send_message(
            win32defines.TTM_ENUMTOOLSW,
            self.index,
            remote_mem)

        remote_mem.Read(tipinfo)

        self.info = tipinfo

        # now get the text
        self.info.lpszText = remote_mem.Address() + \
            ctypes.sizeof(self.info) + 1

        remote_mem.Write(self.info)

        self.ctrl.send_message(
            win32defines.TTM_GETTEXTW, 160, remote_mem)

        # There is no way to determine the required buffer size.
        # However, tool text, as returned at the lpszText member of the TOOLINFO structure,
        # has a maximum length of 80 TCHARs, including the terminating NULL.
        # If the text exceeds this length, it is truncated.
        # https://msdn.microsoft.com/en-us/library/windows/desktop/bb760375(v=vs.85).aspx
        text = ctypes.create_unicode_buffer(80)

        remote_mem.Read(text, self.info.lpszText)

        self.text = text.value

        del remote_mem


#====================================================================
class ToolTipsWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows ToolTips common control (not fully implemented)"""

    # mask this class as it is not ready for prime time yet!
    friendlyclassname = "ToolTips"
    windowclasses = ["tooltips_class32",
                     ".*ToolTip",
                     "#32774", "MS_WINNOTE", "VBBubble", ]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialize the instance"""
        super(ToolTipsWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def get_tip(self, tip_index):
        """Return the particular tooltip"""
        if tip_index >= self.tool_count():
            raise IndexError(('tip_index {0} is greater than number of' +
                              ' available tips: {1}').format(tip_index, self.tool_count()))
        return ToolTip(self, tip_index)
    # Non PEP-8 alias
    GetTip = deprecated(get_tip)

    #----------------------------------------------------------------
    def tool_count(self):
        """Return the number of tooltips"""
        return self.send_message(win32defines.TTM_GETTOOLCOUNT)
    # Non PEP-8 alias
    ToolCount = deprecated(tool_count)

    #----------------------------------------------------------------
    def get_tip_text(self, tip_index):
        """Return the text of the tooltip"""
        return ToolTip(self, tip_index).text
    # Non PEP-8 alias
    GetTipText = deprecated(get_tip_text)

    #----------------------------------------------------------------
    def texts(self):
        """Return the text of all the tooltips"""
        texts = [self.window_text(), ]
        for tip_index in range(0, self.tool_count()):
            texts.append(self.get_tip_text(tip_index))

        return texts


#====================================================================
class UpDownWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows UpDown common control"""

    friendlyclassname = "UpDown"
    windowclasses = ["msctls_updown32", "msctls_updown", ]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_SpinnerControlTypeId]

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(UpDownWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def get_value(self):
        """Get the current value of the UpDown control"""
        pos = self.send_message(
            win32defines.UDM_GETPOS,
            win32structures.LPARAM(0),
            win32structures.WPARAM(0),
        )
        return win32functions.LoWord(pos)
    # Non PEP-8 alias
    GetValue = deprecated(get_value)

    #----------------------------------------------------------------
    def get_base(self):
        """Get the base the UpDown control (either 10 or 16)"""
        return self.send_message(win32defines.UDM_GETBASE)
    # Non PEP-8 alias
    GetBase = deprecated(get_base)

    #----------------------------------------------------------------
    def set_base(self, base_value):
        """Get the base the UpDown control (either 10 or 16)"""
        return self.send_message(win32defines.UDM_SETBASE, base_value)
    # Non PEP-8 alias
    SetBase = deprecated(set_base)

    #----------------------------------------------------------------
    def get_range(self):
        """Return the lower, upper range of the up down control"""
        updown_range = self.send_message(win32defines.UDM_GETRANGE)
        updown_range = (
            win32functions.HiWord(updown_range),
            win32functions.LoWord(updown_range)
        )
        return updown_range
    # Non PEP-8 alias
    GetRange = deprecated(get_range)

    #----------------------------------------------------------------
    def get_buddy_control(self):
        """Get the buddy control of the updown control"""
        #from wraphandle import WrapHandle
        #from HwndWrapper import WrapHandle
        buddy_handle = self.send_message(win32defines.UDM_GETBUDDY)
        return hwndwrapper.HwndWrapper(buddy_handle)
    # Non PEP-8 alias
    GetBuddyControl = deprecated(get_buddy_control)

    #----------------------------------------------------------------
    def set_value(self, new_pos):
        """Set the value of the of the UpDown control to some integer value"""
        for _ in range(3):
            result = ctypes.c_long()
            win32functions.SendMessageTimeout(self,
                win32defines.UDM_SETPOS, 0, win32functions.MakeLong(0, new_pos),
                win32defines.SMTO_NORMAL,
                int(Timings.after_updownchange_wait * 1000),
                ctypes.byref(result))
            win32functions.WaitGuiThreadIdle(self)
            time.sleep(Timings.after_updownchange_wait)
            if self.get_value() == new_pos:
                break
            # make one more attempt elsewhere
    # Non PEP-8 alias
    SetValue = deprecated(set_value)

    #----------------------------------------------------------------
    def increment(self):
        """Increment the number in the UpDown control by one"""
        # hmmm - VM_SCROLL and UDN_DELTAPOS don't seem to be working for me :-(
        # I will fake it for now either use click, or get_value() + 1
        rect = self.client_rect()
        self.click_input(coords=(rect.left + 5, rect.top + 5))

        #self.set_value(self.get_value() + 1)
        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_updownchange_wait)
    # Non PEP-8 alias
    Increment = deprecated(increment)

    #----------------------------------------------------------------
    def decrement(self):
        """Decrement the number in the UpDown control by one"""
        rect = self.client_rect()
        self.click_input(coords=(rect.left + 5, rect.bottom - 5))

        #self.set_value(self.get_value() - 1)
        #win32functions.WaitGuiThreadIdle(self)
        #time.sleep(Timings.after_updownchange_wait)
    # Non PEP-8 alias
    Decrement = deprecated(decrement)


#====================================================================
class TrackbarWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Trackbar common control """

    friendlyclassname = "Trackbar"
    windowclasses = ["msctls_trackbar", ]

    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_SliderControlTypeId]

    def get_range_min(self):
        """Get min available trackbar value"""
        return self.send_message(win32defines.TBM_GETRANGEMIN)

    def get_range_max(self):
        """Get max available trackbar value"""
        return self.send_message(win32defines.TBM_GETRANGEMAX)

    def get_position(self):
        """Get trackbar position"""
        return self.send_message(win32defines.TBM_GETPOS)

    def get_num_ticks(self):
        """Get trackbar num ticks"""
        return self.send_message(win32defines.TBM_GETNUMTICS)

    def get_channel_rect(self):
        """Get position of the bounding rectangle for a Trackbar"""
        remote_mem = RemoteMemoryBlock(self)
        system_rect = win32structures.RECT()
        remote_mem.Write(system_rect)

        self.send_message(win32defines.TBM_GETCHANNELRECT, 0, remote_mem)
        remote_mem.Read(system_rect)
        del remote_mem

        return system_rect

    def get_line_size(self):
        """Get the number of logical positions the trackbar's slider"""
        return self.send_message(win32defines.TBM_GETLINESIZE)

    def get_tooltips_control(self):
        """Get trackbar tooltip"""
        return ToolTipsWrapper(self.send_message(win32defines.TBM_GETTOOLTIPS))

    def get_page_size(self):
        """Get the number of logical positions for the trackbar's slider"""
        return self.send_message(win32defines.TBM_GETPAGESIZE)

    def set_range_max(self, range_max):
        """Set max available trackbar value"""
        if range_max < self.get_range_min():
            raise ValueError('Cannot set range max less than range min')
        self.send_message(win32defines.TBM_SETRANGEMAX, True, range_max)

    def set_range_min(self, range_min):
        """Set min available trackbar value"""
        if range_min > self.get_range_max():
            raise ValueError('Cannot set range min more than range max')
        self.send_message(win32defines.TBM_SETRANGEMIN, True, range_min)

    def set_position(self, pos):
        """Set trackbar position"""
        if not (self.get_range_min() <= pos <= self.get_range_max()):
            raise ValueError('Cannot set position out of range')
        self.send_message(win32defines.TBM_SETPOS, True, pos)

    def set_line_size(self, line_size):
        """Set trackbar line size"""
        self.send_message(win32defines.TBM_SETLINESIZE, 0, line_size)

    def set_page_size(self, page_size):
        """Set trackbar page size"""
        self.send_message(win32defines.TBM_SETPAGESIZE, 0, page_size)

    def set_sel(self, sel_start, sel_end):
        """Set start and end of selection"""
        if not self.has_style(win32defines.TBS_ENABLESELRANGE):
            raise RuntimeError('Range selection is not supported for this trackbar')
        sel_start_val = win32functions.LoWord(sel_start)
        sel_end_val = win32functions.HiWord(sel_end)
        sel_val = win32functions.MakeLong(sel_start_val, sel_end_val)
        self.send_message(win32defines.TBM_SETSAL, 0, sel_val)

    def get_sel_start(self):
        """Get start of selection"""
        if not self.has_style(win32defines.TBS_ENABLESELRANGE):
            raise RuntimeError('Range selection is not supported for this trackbar')
        return self.send_message(win32defines.TBM_GETSELSTART)

    def get_sel_end(self):
        """Get end of selection"""
        if not self.has_style(win32defines.TBS_ENABLESELRANGE):
            raise RuntimeError('Range selection is not supported for this trackbar')
        return self.send_message(win32defines.TBM_GETSELEND)


#====================================================================
class AnimationWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Animation common control"""

    friendlyclassname = "Animation"
    windowclasses = ["SysAnimate32", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []


#====================================================================
class ComboBoxExWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows ComboBoxEx common control"""

    friendlyclassname = "ComboBoxEx"
    windowclasses = ["ComboBoxEx32", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []
    has_title = False


#====================================================================
class DateTimePickerWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows DateTimePicker common control"""

    friendlyclassname = "DateTimePicker"
    windowclasses = ["SysDateTimePick32",
                     r"WindowsForms\d*\.SysDateTimePick32\..*", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []
    has_title = False

    #----------------------------------------------------------------
    def get_time(self):
        """Get the currently selected time"""
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()
        remote_mem.Write(system_time)

        res = self.send_message(win32defines.DTM_GETSYSTEMTIME, 0, remote_mem)
        remote_mem.Read(system_time)
        del remote_mem

        if res != win32defines.GDT_VALID:
            raise RuntimeError('Failed to get time from Date Time Picker (result = ' + str(res) + ')')

        #year = system_time.wYear
        #month = system_time.wMonth
        #day_of_week = system_time.wDayOfWeek
        #day = system_time.wDay
        #hour = system_time.wHour
        #minute = system_time.wMinute
        #second = system_time.wSecond
        #milliseconds = system_time.wMilliseconds
        #return (year, month, day_of_week, day, hour, minute, second, milliseconds)
        return system_time
    # Non PEP-8 alias
    GetTime = deprecated(get_time)

    #----------------------------------------------------------------
    def set_time(self, year=0, month=0, day_of_week=0, day=0, hour=0, minute=0, second=0, milliseconds=0):
        """Get the currently selected time"""
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()

        system_time.wYear = year
        system_time.wMonth = month
        system_time.wDayOfWeek = day_of_week
        system_time.wDay = day
        system_time.wHour = hour
        system_time.wMinute = minute
        system_time.wSecond = second
        system_time.wMilliseconds = milliseconds

        remote_mem.Write(system_time)

        res = self.send_message(win32defines.DTM_SETSYSTEMTIME, win32defines.GDT_VALID, remote_mem)
        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to set time in Date Time Picker')
    # Non PEP-8 alias
    SetTime = deprecated(set_time)


#====================================================================
class HotkeyWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Hotkey common control"""

    friendlyclassname = "Hotkey"
    windowclasses = ["msctls_hotkey32", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []
    has_title = False


#====================================================================
class IPAddressWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows IPAddress common control"""

    friendlyclassname = "IPAddress"
    windowclasses = ["SysIPAddress32", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []
    has_title = False


#====================================================================
class CalendarWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Calendar common control"""

    friendlyclassname = "Calendar"
    windowclasses = ["SysMonthCal32", ]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_CalendarControlTypeId]
    has_title = False

    place_in_calendar = {
        'background': win32defines.MCSC_BACKGROUND,
        'month_background': win32defines.MCSC_MONTHBK,
        'text': win32defines.MCSC_TEXT,
        'title_background': win32defines.MCSC_TITLEBK,
        'title_text': win32defines.MCSC_TITLETEXT,
        'trailing_text': win32defines.MCSC_TRAILINGTEXT
    }

    #----------------------------------------------------------------
    def __init__(self, hwnd):
        """Initialise the instance"""
        super(CalendarWrapper, self).__init__(hwnd)

    #----------------------------------------------------------------
    def get_current_date(self):
        """Get the currently selected date"""
        remote_mem = RemoteMemoryBlock(self)
        system_date = win32structures.SYSTEMTIME()
        remote_mem.Write(system_date)

        res = self.send_message(win32defines.MCM_GETCURSEL , 0, remote_mem)
        remote_mem.Read(system_date)
        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to get the currently selected date in Calendar')
        return system_date

    #----------------------------------------------------------------
    def set_current_date(self, year, month, day_of_week, day):
        """Set the currently selected date"""
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()

        system_time.wYear = year
        system_time.wMonth = month
        system_time.wDayOfWeek = day_of_week
        system_time.wDay = day
        system_time.wHour = 0
        system_time.wMinute = 0
        system_time.wSecond = 0
        system_time.wMilliseconds = 0

        remote_mem.Write(system_time)

        res = self.send_message(win32defines.MCM_SETCURSEL, win32defines.GDT_VALID, remote_mem)

        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to set the currently selected date in Calendar')

    #----------------------------------------------------------------
    def get_border(self):
        """Get the calendar border"""
        return self.send_message(win32defines.MCM_GETCALENDARBORDER, 0, 0)

    #----------------------------------------------------------------
    def set_border(self, border):
        """Set the calendar border"""
        self.send_message(win32defines.MCM_SETCALENDARBORDER, True, border)

    #----------------------------------------------------------------
    def count(self):
        """Get the calendars count"""
        return self.send_message(win32defines.MCM_GETCALENDARCOUNT, 0, 0)

    #----------------------------------------------------------------
    def get_view(self):
        """Get the calendar view"""
        return self.send_message(win32defines.MCM_GETCURRENTVIEW, 0, 0)

    #----------------------------------------------------------------
    def set_view(self, viewType):
        """Set the calendar view"""
        res = self.send_message(win32defines.MCM_SETCURRENTVIEW, 0, viewType)
        if res == 0:
            raise RuntimeError('Failed to set view in Calendar')

    #----------------------------------------------------------------
    def set_day_states(self, month_states):
        """Sets the day states for all months that are currently visible"""
        remote_mem = RemoteMemoryBlock(self)
        day_states = (wintypes.DWORD * len(month_states))(*month_states)

        remote_mem.Write(day_states)
        res = self.send_message(win32defines.MCM_SETDAYSTATE, len(day_states), remote_mem)
        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to set the day states in Calendar')

        return res

    #----------------------------------------------------------------
    def calc_min_rectangle(self, left, top, right, bottom):
        """Calculates the minimum size that a rectangle needs to be to fit that number of calendars"""
        remote_mem = RemoteMemoryBlock(self)

        minimized_rect = win32structures.RECT()
        minimized_rect.left = left
        minimized_rect.top = top
        minimized_rect.right = right
        minimized_rect.bottom = bottom

        remote_mem.Write(minimized_rect)
        self.send_message(win32defines.MCM_SIZERECTTOMIN, 0, remote_mem)

        remote_mem.Read(minimized_rect)
        del remote_mem

        return minimized_rect

    #----------------------------------------------------------------
    def hit_test(self, x, y):
        """Determines which portion of a month calendar control is at a given point on the screen"""
        remote_mem = RemoteMemoryBlock(self)
        hit_test_info = win32structures.MCHITTESTINFO()
        point = win32structures.POINT()
        point.x = x
        point.y = y
        hit_test_info.pt = point
        hit_test_info.cbSize = ctypes.sizeof(hit_test_info)

        remote_mem.Write(hit_test_info)
        res = self.send_message(win32defines.MCM_HITTEST, 0, remote_mem)
        del remote_mem

        return res

    # ----------------------------------------------------------------
    def set_id(self, ID):
        """
        Set the calendar type.

        Receive only one parameter, which takes variants below:
        'gregorian', 'gregorian_us', 'japan', 'taiwan', 'korea',
        'hijri', 'thai', 'hebrew', 'gregorian_me_french',
        'gregorian_arabic', 'gregorian_english_xlit',
        'gregorian_french_xlit', 'umalqura'
        """

        dict_types = {
            'gregorian': win32defines.CAL_GREGORIAN,
            'gregorian_us': win32defines.CAL_GREGORIAN_US,
            'japan': win32defines.CAL_JAPAN,
            'taiwan': win32defines.CAL_TAIWAN,
            'korea': win32defines.CAL_KOREA,
            'hijri': win32defines.CAL_HIJRI,
            'thai': win32defines.CAL_THAI,
            'hebrew': win32defines.CAL_HEBREW,
            'gregorian_me_french': win32defines.CAL_GREGORIAN_ME_FRENCH,
            'gregorian_arabic': win32defines.CAL_GREGORIAN_ARABIC,
            'gregorian_english_xlit': win32defines.CAL_GREGORIAN_XLIT_ENGLISH,
            'gregorian_french_xlit': win32defines.CAL_GREGORIAN_XLIT_FRENCH,
            'umalqura': win32defines.CAL_UMALQURA
        }
        if ID in dict_types:
            self.send_message(win32defines.MCM_SETCALID, dict_types[ID], 0)
        else:
            raise ValueError('Incorrect calendar ID (use one of {0})'.format(dict_types.keys()))

    # ----------------------------------------------------------------
    def get_id(self):
        """Get type of calendar"""
        return self.send_message(win32defines.MCM_GETCALID, 0, 0)

    # ----------------------------------------------------------------
    def set_color(self, place_of_color, red, green, blue):
        """
        Set some color in some place of calendar which you specify.

        Receive four parameters:
        - The first parameter may take few variants below:
        'background', 'month_background', 'text', 'title_background',
        'title_text', 'trailing_text' ;
        - All other parameters should be integer from 0 to 255.
        """
        if not (0 <= red <= 255):
            raise RuntimeError('Incorrect range of red color, must be from 0 to 255')
        if not (0 <= green <= 255):
            raise RuntimeError('Incorrect range of green color, must be from 0 to 255')
        if not (0 <= blue <= 255):
            raise RuntimeError('Incorrect range of blue color, must be from 0 to 255')
        color = (red << 16) | (green << 8) | blue
        if place_of_color in self.place_in_calendar:
            result = self.send_message(win32defines.MCM_SETCOLOR, self.place_in_calendar[place_of_color], color)
        else:
            raise ValueError('Incorrect calendar place ID (use one of {0})'.format(self.place_in_calendar.keys()))
        if result == -1:
            raise RuntimeError('Incorrect color')
        return result

    # ----------------------------------------------------------------
    #TODO create method get_color in future
    '''
    def get_color(self, place_of_color):
        """
        Return color of place in calendar, which you specify.

        Receive only one parameter, which takes variants below:
        'background', 'month_background', 'text', 'title_background', 'title_text', 'trailing_text'
        """

        if place_of_color in self.place_in_calendar:
            return self.send_message(win32defines.MCM_GETCOLOR, self.place_in_calendar[place_of_color], 0)
        else:
            raise ValueError('Incorrect calendar place ID (use one of {0})'.format(self.place_in_calendar.keys()))
    '''

    def set_today(self, year, month, day):
        """Set today date"""
        remote_mem = RemoteMemoryBlock(self)
        system_time = win32structures.SYSTEMTIME()

        system_time.wYear = year
        system_time.wMonth = month
        system_time.wDay = day
        system_time.wHour = 0
        system_time.wMinute = 0
        system_time.wSecond = 0
        system_time.wMilliseconds = 0

        remote_mem.Write(system_time)

        res = self.send_message(win32defines.MCM_SETTODAY, 0, remote_mem)

        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to set today date in Calendar')

    # ----------------------------------------------------------------
    def get_today(self):
        """Get today date"""
        remote_mem = RemoteMemoryBlock(self)
        system_date = win32structures.SYSTEMTIME()
        remote_mem.Write(system_date)

        res = self.send_message(win32defines.MCM_GETTODAY, 0, remote_mem)
        remote_mem.Read(system_date)
        del remote_mem

        if res == 0:
            raise RuntimeError('Failed to get today date in Calendar')
        return system_date

    # ----------------------------------------------------------------
    def set_first_weekday(self, dayNum):
        """Set first day of the week"""
        self.send_message(win32defines.MCM_SETFIRSTDAYOFWEEK, 0, dayNum)

    # ----------------------------------------------------------------
    def get_first_weekday(self):
        """Get is not in current locale and if so first day of the week"""
        res = self.send_message(win32defines.MCM_GETFIRSTDAYOFWEEK, 0, 0)
        return (win32functions.HiWord(res), win32functions.LoWord(res))

    # ----------------------------------------------------------------
    def get_month_delta(self):
        """Retrieves the scroll rate for a month calendar control"""
        return self.send_message(win32defines.MCM_GETMONTHDELTA, 0, 0)

    # ----------------------------------------------------------------
    def set_month_delta(self, delta):
        """Sets the scroll rate for a month calendar control."""
        if (delta < 0):
            raise ValueError("Month delta must be greater than 0")

        self.send_message(win32defines.MCM_SETMONTHDELTA, delta, 0)

    # ----------------------------------------------------------------
    def get_month_range(self, scope_of_range):
        """Retrieves date information that represents the high and low limits of a month calendar control's display."""
        if scope_of_range not in [win32defines.GMR_DAYSTATE, win32defines.GMR_VISIBLE]:
            raise ValueError("scope_of_range value must be one of the following: GMR_DAYSTATE or GMR_VISIBLE")

        remote_mem = RemoteMemoryBlock(self)
        system_date_arr = (win32structures.SYSTEMTIME * 2)()

        system_date_arr[0] = win32structures.SYSTEMTIME()
        system_date_arr[1] = win32structures.SYSTEMTIME()

        remote_mem.Write(system_date_arr)

        res = self.send_message(win32defines.MCM_GETMONTHRANGE, scope_of_range, remote_mem)

        remote_mem.Read(system_date_arr)
        del remote_mem

        return (res, system_date_arr)

#====================================================================
class PagerWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Pager common control"""

    friendlyclassname = "Pager"
    windowclasses = ["SysPager", ]
    if sysinfo.UIA_support:
        #controltypes is empty to make wrapper search result unique
        #possible control types: IUIA().UIA_dll.UIA_PaneControlTypeId
        controltypes = []

    #----------------------------------------------------------------
    def get_position(self):
        """Return the current position of the pager"""
        self._ensure_enough_privileges('PGM_GETPOS')
        return self.send_message(win32defines.PGM_GETPOS)
    # Non PEP-8 alias
    GetPosition = deprecated(get_position)

    #----------------------------------------------------------------
    def set_position(self, pos):
        """Set the current position of the pager"""
        self._ensure_enough_privileges('PGM_SETPOS')
        return self.send_message(win32defines.PGM_SETPOS, pos)
    # Non PEP-8 alias
    SetPosition = deprecated(set_position)


#====================================================================
class ProgressWrapper(hwndwrapper.HwndWrapper):

    """Class that wraps Windows Progress common control"""

    friendlyclassname = "Progress"
    windowclasses = ["msctls_progress", "msctls_progress32", ]
    if sysinfo.UIA_support:
        controltypes = [IUIA().UIA_dll.UIA_ProgressBarControlTypeId]
    has_title = False

    #----------------------------------------------------------------
    def get_position(self):
        """Return the current position of the progress bar"""
        self._ensure_enough_privileges('PBM_GETPOS')
        return self.send_message(win32defines.PBM_GETPOS)
    # Non PEP-8 alias
    GetPosition = deprecated(get_position)

    #----------------------------------------------------------------
    def set_position(self, pos):
        """Set the current position of the progress bar"""
        self._ensure_enough_privileges('PBM_SETPOS')
        return self.send_message(win32defines.PBM_SETPOS, pos)
    # Non PEP-8 alias
    SetPosition = deprecated(set_position)

    #----------------------------------------------------------------
    def get_state(self):
        """Get the state of the progress bar

        State will be one of the following constants:
         * PBST_NORMAL
         * PBST_ERROR
         * PBST_PAUSED
        """
        self._ensure_enough_privileges('PBM_GETSTATE')
        return self.send_message(win32defines.PBM_GETSTATE)
    # Non PEP-8 alias
    GetState = deprecated(get_state)

    #----------------------------------------------------------------
    def get_step(self):
        """Get the step size of the progress bar"""
        self._ensure_enough_privileges('PBM_GETSTEP')
        return self.send_message(win32defines.PBM_GETSTEP)
    # Non PEP-8 alias
    GetStep = deprecated(get_step)

    #----------------------------------------------------------------
    def step_it(self):
        """Move the progress bar one step size forward"""
        self._ensure_enough_privileges('PBM_STEPIT')
        return self.send_message(win32defines.PBM_STEPIT)
    # Non PEP-8 alias
    StepIt = deprecated(step_it)

#
##
###hwndwrapper._HwndWrappers["ComboBoxEx32"] = ComboBoxEx
##


###====================================================================
##class ComboBoxEx(Controls_Standard.ComboBox):
##    #----------------------------------------------------------------
##    def __init__(self, hwndOrXML):
#        Window.__init__(self, hwndOrXML)
##
#        if isinstance(hwndOrXML, (int, long)):
##            comboCntrl = send_message(
##                hwndOrXML,
##                CBEM_GETCOMBOCONTROL,
##                0,
##                0)
##
##            print "--"*20, comboCntrl
##            Controls_Standard.ComboBox.__init__(self, comboCntrl)
##            print self.dropped_rect
##
##
##
##            droppedRect = win32structures.RECT()
##
##            send_message(
##                self,
##                CB_GETDROPPEDCONTROLRECT,
##                0,
##                ctypes.byref(droppedRect))
##
##            props['dropped_rect'] = droppedRect
#
#
#
#
#
#
#            # find out how many text items are in the combobox
#            numItems = send_message(
#                self,
#                CB_GETCOUNT,
#                0,
#                0)
#
#            print "*"*20, numItems
##            remote_mem = RemoteMemoryBlock(self)
##
##
##            # get the text for each item in the combobox
##            while True:
##                item = COMBOBOXEXITEMW()
##
##                item.mask = CBEIF_TEXT
##                item.cchTextMax = 4000
##                item.pszText = remote_mem.Address() + ctypes.sizeof(item) + 1
##
##                remote_mem.Write(item)
##
##                retval = send_message (
##                    self,
##                    CBEM_GETITEMW,
##                    0,
##                    remote_mem
##                    )
##
##                if retval:
##                    item = remote_mem.Read(item)
##
##                    # Read the remote text string
##                  charData = ctypes.create_unicode_buffer(4000)
##                    remote_mem.Read(charData, item.pszText)
##                    self.Titles.append(charData.value)
##                else:
##                    break
##
#
#        else:
#
#            # get the dropped Rect form
#            droppedRect = XMLToRect(hwndOrXML.find("DROPPEDRECT"))
#            props['dropped_rect'] = droppedRect
