# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"Wraps various standard windows controls"

__revision__ = "$Revision$"

import time

import ctypes

import HwndWrapper

from pywinauto import win32functions
from pywinauto import win32defines
from pywinauto import win32structures
#from pywinauto import findbestmatch

from pywinauto import tests
from pywinauto.timings import Timings

#====================================================================
class ButtonWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Button control"

    friendlyclassname = "Button"
    windowclasses = [
        "Button",
        r"WindowsForms\d*\.BUTTON\..*",
        "TButton" ]


    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ButtonWrapper, self).__init__(hwnd)

        #self._set_if_needs_image()


    def _set_if_needs_image(self, value):
        "Does nothing see _get_if_needs_image"
        pass
    #-----------------------------------------------------------
    def _get_if_needs_image(self):
        "Set the _NeedsImageProp attribute if it is an image button"

        # optimization call Style once and work with that rather than
        # calling HasStyle a number of times
        style = self.Style()

        if self.IsVisible() and (\
            style & win32defines.BS_BITMAP == style or \
            style & win32defines.BS_ICON == style or \
            style & win32defines.BS_OWNERDRAW == style):

            #self._NeedsImageProp = True
            return True
        else:
            return False
    _NeedsImageProp = property(_get_if_needs_image, _set_if_needs_image)

    #-----------------------------------------------------------
    def FriendlyClassName(self):
        """Return the friendly class name of the button

        Windows controls with the class "Button" can look like different
        controls based on their style. They can look like the following
        controls:

          - Buttons, this method returns "Button"
          - CheckBoxes, this method returns "CheckBox"
          - RadioButtons, this method returns "RadioButton"
          - GroupBoxes, this method returns "GroupBox"

        """
        # get the least significant bit
        style_lsb = self.Style() & 0xF

        f_class_name = 'Button'

        if style_lsb == win32defines.BS_3STATE or \
            style_lsb == win32defines.BS_AUTO3STATE or \
            style_lsb == win32defines.BS_AUTOCHECKBOX or \
            style_lsb == win32defines.BS_CHECKBOX:
            f_class_name = "CheckBox"

        elif style_lsb == win32defines.BS_RADIOBUTTON or \
            style_lsb == win32defines.BS_AUTORADIOBUTTON:
            f_class_name = "RadioButton"

        elif style_lsb ==  win32defines.BS_GROUPBOX:
            f_class_name = "GroupBox"

        if self.Style() & win32defines.BS_PUSHLIKE:
            f_class_name = "Button"

        return f_class_name


    #-----------------------------------------------------------
    def GetCheckState(self):
        """Return the check state of the checkbox

        The check state is represented by an integer
        0 - unchecked
        1 - checked
        2 - indeterminate

        The following constants are defined in the win32defines module
        BST_UNCHECKED = 0
        BST_CHECKED = 1
        BST_INDETERMINATE = 2
        """
        return self.SendMessage(win32defines.BM_GETCHECK)

    #-----------------------------------------------------------
    def Check(self):
        "Check a checkbox"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_CHECKED)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self


    #-----------------------------------------------------------
    def UnCheck(self):
        "Uncheck a checkbox"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_UNCHECKED)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    def SetCheckIndeterminate(self):
        "Set the checkbox to indeterminate"
        self.SendMessageTimeout(win32defines.BM_SETCHECK,
            win32defines.BST_INDETERMINATE)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_buttoncheck_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    def IsDialog(self):
        "Buttons are never dialogs so return False"
        return False

    #-----------------------------------------------------------
    def Click(self, *args, **kwargs):
        "Click the Button control"
    #    import win32functions
    #    win32functions.WaitGuiThreadIdle(self)
    #    self.NotifyParent(win32defines.BN_CLICKED)
        HwndWrapper.HwndWrapper.Click(self, *args, **kwargs)
    #    win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_button_click_wait)


    #def IsSelected (self):
    #    (for radio buttons)



#====================================================================
def _get_multiple_text_items(wrapper, count_msg, item_len_msg, item_get_msg):
    "Helper function to get multiple text items from a control"

    texts = []

    # find out how many text items are in the combobox
    num_items = wrapper.SendMessage(count_msg)

    # get the text for each item in the combobox
    for i in range(0, num_items):
        text_len = wrapper.SendMessage (item_len_msg, i, 0)

        text = ctypes.create_unicode_buffer(text_len + 1)

        wrapper.SendMessage(item_get_msg, i, ctypes.byref(text))

        texts.append(text.value)

    return texts


#====================================================================
class ComboBoxWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows ComboBox control"

    friendlyclassname = "ComboBox"
    windowclasses = [
        "ComboBox",
        "WindowsForms\d*\.COMBOBOX\..*",
        "TComboBox"]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ComboBoxWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            "SelectedIndex",
            "DroppedRect",
            ])

    #-----------------------------------------------------------
    def DroppedRect(self):
        "Get the dropped rectangle of the combobox"
        dropped_rect = win32structures.RECT()

        self.SendMessage(
            win32defines.CB_GETDROPPEDCONTROLRECT,
            0,
            ctypes.byref(dropped_rect))

        # we need to offset the dropped rect from the control
        dropped_rect -= self.Rectangle()

        return dropped_rect

    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the combobox"
        return self.SendMessage(win32defines.CB_GETCOUNT)

    #-----------------------------------------------------------
    def SelectedIndex(self):
        "Return the selected index"
        return self.SendMessage(win32defines.CB_GETCURSEL)

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        "Get the index for the item with this 'ident'"
        if isinstance(ident, (int, long)):

            if ident >= self.ItemCount():
                raise IndexError(
                    "Combobox has %d items, you requested item %d"%
                        (self.ItemCount(),
                        ident))

            # negative index
            if ident < 0:
                # convert it to a positive index
                ident = (self.ItemCount() + ident)

        elif isinstance(ident, basestring):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.ItemTexts().index(ident)

        return ident


    #-----------------------------------------------------------
    def ItemData(self, item):
        "Return the item data associted with this item"
        index = self._get_item_index(item)
        "Returns the item data associated with the item if any"
        return self.SendMessage(win32defines.CB_GETITEMDATA, index)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text of the items of the combobox"
        return _get_multiple_text_items(
            self,
            win32defines.CB_GETCOUNT,
            win32defines.CB_GETLBTEXTLEN,
            win32defines.CB_GETLBTEXT)

    #-----------------------------------------------------------
    def Texts(self):
        "Return the text of the items in the combobox"
        texts = [self.WindowText()]
        texts.extend(self.ItemTexts())
        return texts

    #-----------------------------------------------------------
    def GetProperties(self):
        "Return the properties of the control as a dictionary"
        props = HwndWrapper.HwndWrapper.GetProperties(self)

        #props['ItemData'] = []
        #for i in range(self.ItemCount()):
        #    props['ItemData'].append(self.ItemData(i))

        return props

    #-----------------------------------------------------------
    def Select(self, item):
        """Select the ComboBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        self.VerifyActionable()

        index = self._get_item_index(item)

        # change the selected item
        self.SendMessageTimeout(win32defines.CB_SETCURSEL, index)

        # Notify the parent that we are finished selecting
        self.NotifyParent(win32defines.CBN_SELENDOK)

        # Notify the parent that we have changed
        self.NotifyParent(win32defines.CBN_SELCHANGE)

        # simple combo boxes don't have drop downs so they do not recieve
        # this notification
        if self.HasStyle(win32defines.CBS_DROPDOWN):
            # Notify the parent that the drop down has closed
            self.NotifyParent(win32defines.CBN_CLOSEUP)


        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_comboboxselect_wait)

        # return this control so that actions can be chained.
        return self

    #-----------------------------------------------------------
    #def Deselect(self, item):
    # Not implemented because it doesn't make sense for combo boxes.

    #TODO def EditControl(self):

    #TODO def ListControl(self):

    #TODO def ItemText(self, index):

    #TODO def EditText(self):  # or should this be self.EditControl.Text()?


#====================================================================
class ListBoxWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows ListBox control"

    friendlyclassname = "ListBox"
    windowclasses = [
        "ListBox",
        r"WindowsForms\d*\.LISTBOX\..*",
        "TListBox",]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(ListBoxWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            "SelectedIndices"])

    #-----------------------------------------------------------
    def SelectedIndices(self):
        "The currently selected indices of the listbox"
        num_selected = self.SendMessage(win32defines.LB_GETSELCOUNT)

        # if we got LB_ERR then it is a single selection list box
        if num_selected == win32defines.LB_ERR:
            items = [self.SendMessage(win32defines.LB_GETCURSEL)]

        # otherwise it is a multiselection list box
        else:
            items = (ctypes.c_int * num_selected)()

            self.SendMessage(
                win32defines.LB_GETSELITEMS, num_selected, ctypes.byref(items))

        return items

    #-----------------------------------------------------------
    def _get_item_index(self, ident):
        "Return the index of the item 'ident'"
        if isinstance(ident, (int, long)):

            if ident >= self.ItemCount():
                raise IndexError(
                    "ListBox has %d items, you requested item %d"%
                        (self.ItemCount(),
                        ident))

            # negative index
            if ident < 0:
                ident = (self.ItemCount() + ident)

        elif isinstance(ident, basestring):
            # todo - implement fuzzy lookup for ComboBox items
            # todo - implement appdata lookup for combobox items
            ident = self.ItemTexts().index(ident) #-1

        return ident

    #-----------------------------------------------------------
    def ItemCount(self):
        "Return the number of items in the ListBox"
        return self.SendMessage(win32defines.LB_GETCOUNT)

    #-----------------------------------------------------------
    def ItemData(self, i):
        "Return the ItemData if any associted with the item"

        index = self._get_item_index(i)

        return self.SendMessage(win32defines.LB_GETITEMDATA, index)

    #-----------------------------------------------------------
    def ItemTexts(self):
        "Return the text of the items of the listbox"
        return _get_multiple_text_items(
            self,
            win32defines.LB_GETCOUNT,
            win32defines.LB_GETTEXTLEN,
            win32defines.LB_GETTEXT)

    #-----------------------------------------------------------
    def Texts(self):
        "Return the texts of the control"
        texts = [self.WindowText()]
        texts.extend(self.ItemTexts())
        return texts

#    #-----------------------------------------------------------
#    def GetProperties(self):
#        "Return the properties as a dictionary for the control"
#        props = HwndWrapper.HwndWrapper.GetProperties(self)
#
#        props['ItemData'] = []
#        for i in range(self.ItemCount()):
#            props['ItemData'].append(self.ItemData(i))
#
#        return props

    #-----------------------------------------------------------
    def Select(self, item):
        """Select the ListBox item

        item can be either a 0 based index of the item to select
        or it can be the string that you want to select
        """
        self.VerifyActionable()

        # Make sure we have an index  so if passed in a
        # string then find which item it is
        index = self._get_item_index(item)

        # change the selected item
        self.SendMessageTimeout(win32defines.LB_SETCURSEL, index)

        # Notify the parent that we have changed
        self.NotifyParent(win32defines.LBN_SELCHANGE)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listboxselect_wait)

        return self

    #-----------------------------------------------------------
    def SetItemFocus(self, item):
        "Set the ListBox focus to the item at index"

        index = self._get_item_index(item)

        # if it is a multiple selection dialog
        if self.HasStyle(win32defines.LBS_EXTENDEDSEL) or \
            self.HasStyle(win32defines.LBS_MULTIPLESEL):
            self.SendMessageTimeout(win32defines.LB_SETCARETINDEX, index)
        else:
            self.SendMessageTimeout(win32defines.LB_SETCURSEL, index)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_listboxfocuschange_wait)

        # return this control so that actions can be chained.
        return self


    #-----------------------------------------------------------
    def GetItemFocus(self):
        "Retrun the index of current selection in a ListBox"

        # if it is a multiple selection dialog
        if self.HasStyle(win32defines.LBS_EXTENDEDSEL) or \
            self.HasStyle(win32defines.LBS_MULTIPLESEL):
            return self.SendMessage(win32defines.LB_GETCARETINDEX)
        else:
            return self.SendMessage(win32defines.LB_GETCURSEL)


#====================================================================
class EditWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Edit control"

    friendlyclassname = "Edit"
    windowclasses = [
        "Edit",
        "TEdit",
        "TMemo",
        r"WindowsForms\d*\.EDIT\..*",
        ]

    #-----------------------------------------------------------
    def __init__(self, hwnd):
        "Initialize the control"
        super(EditWrapper, self).__init__(hwnd)

        self.writable_props.extend([
            'SelectionIndices'])

    #-----------------------------------------------------------
    def LineCount(self):
        "Return how many lines there are in the Edit"
        return  self.SendMessage(win32defines.EM_GETLINECOUNT)-1

    #-----------------------------------------------------------
    def LineLength(self, line_index):
        "Return how many characters there are in the line"

        # need to first get a character index of that line
        char_index = self.SendMessage(win32defines.EM_LINEINDEX, line_index)

        # now get the length of text on that line
        return self.SendMessage (
            win32defines.EM_LINELENGTH, char_index, 0)


    #-----------------------------------------------------------
    def GetLine(self, line_index):
        "Return the line specified"

        text_len = self.LineLength(line_index)
        # create a buffer and set the length at the start of the buffer
        text = ctypes.create_unicode_buffer(text_len+3)
        text[0] = unichr(text_len)

        # retrieve the line itself
        self.SendMessage(
            win32defines.EM_GETLINE, line_index, ctypes.byref(text))

        return text.value

    #-----------------------------------------------------------
    def Texts(self):
        "Get the text of the edit control"

        texts = [self.WindowText(), ]

        for i in range(0, self.LineCount()+1):
            texts.append(self.GetLine(i))

        return texts

    #-----------------------------------------------------------
    def TextBlock(self):
        "Get the text of the edit control"

        length = self.SendMessage(win32defines.WM_GETTEXTLENGTH)
        text = ctypes.create_unicode_buffer(length + 1)
        self.SendMessage(win32defines.WM_GETTEXT, length+1, ctypes.byref(text))

        #text = text.value.replace("\r\n", "\n")
        return text.value

    #-----------------------------------------------------------
    def SelectionIndices(self):
        "The start and end indices of the current selection"
        start = ctypes.c_int()
        end = ctypes.c_int()
        self.SendMessage(
            win32defines.EM_GETSEL, ctypes.byref(start), ctypes.byref(end))

        return (start.value, end.value)

    #-----------------------------------------------------------
    def SetWindowText(self, text, append = False):
        """Override SetWindowText for edit controls because it should not be
        used for Edit controls.

        Edit Controls should either use SetEditText() or TypeKeys() to modify
        the contents of the edit control."""
        HwndWrapper.HwndWrapper.SetWindowText(self, text, append)
        raise UserWarning(
            "SetWindowText() should probably not be called for Edit Controls")

    #-----------------------------------------------------------
    def SetEditText(self, text, pos_start = None, pos_end = None):
        "Set the text of the edit control"
        self.VerifyActionable()

        # allow one or both of pos_start and pos_end to be None
        if pos_start is not None or pos_end is not None:

            # if only one has been specified - then set the other
            # to the current selection start or end
            start, end = self.SelectionIndices()
            if pos_start is None:
                pos_start = start
            if pos_end is None:
                pos_end = end

            # set the selection if either start or end has
            # been specified
            self.Select(pos_start, pos_end)
        else:
            self.Select()

        # replace the selection with
        text = ctypes.c_wchar_p(unicode(text))
        self.SendMessageTimeout(win32defines.EM_REPLACESEL, True, text)

        win32functions.WaitGuiThreadIdle(self)
        time.sleep(Timings.after_editsetedittext_wait)


        # return this control so that actions can be chained.
        return self

    # set SetText as an alias to SetEditText
    SetText = SetEditText

    #-----------------------------------------------------------
    def Select(self, start = 0, end = None):
        "Set the edit selection of the edit control"
        self.VerifyActionable()

        # if we have been asked to select a string
        if isinstance(start, basestring):
            string_to_select = start
            #
            start = self.TextBlock().index(string_to_select)

            if end is None:
                end = start + len(string_to_select)

        if end is None:
            end = -1

        self.SendMessageTimeout(win32defines.EM_SETSEL, start, end)

        # give the control a chance to catch up before continuing
        win32functions.WaitGuiThreadIdle(self)

        time.sleep(Timings.after_editselect_wait)


        # return this control so that actions can be chained.
        return self



#====================================================================
class StaticWrapper(HwndWrapper.HwndWrapper):
    "Wrap a windows Static control"

    friendlyclassname = "Static"
    windowclasses = [
        "Static",
        r"WindowsForms\d*\.STATIC\..*",
        "TPanel"]

    def __init__(self, hwnd):
        "Initialize the control"
        super(StaticWrapper, self).__init__(hwnd)

        # if the control is visible - and it shows an image
        if self.IsVisible() and (
            self.HasStyle(win32defines.SS_ICON) or \
            self.HasStyle(win32defines.SS_BITMAP) or \
            self.HasStyle(win32defines.SS_CENTERIMAGE) or \
            self.HasStyle(win32defines.SS_OWNERDRAW)):

            self._NeedsImageProp = True


#====================================================================
# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class DialogWrapper(HwndWrapper.HwndWrapper):
    "Wrap a dialog"

    friendlyclassname = "Dialog"
    #windowclasses = ["#32770", ]

    def __init__(self, hwnd):
        """Initialize the DialogWrapper

        The only extra functionality here is to modify self.friendlyclassname
        to make it "Dialog" if the class is "#32770" otherwise to leave it
        the same as the window class.
        """
        HwndWrapper.HwndWrapper.__init__(self, hwnd)

        if self.Class() == "#32770":
            self.friendlyclassname = "Dialog"
        else:
            self.friendlyclassname = self.Class()

    #-----------------------------------------------------------
    def RunTests(self, tests_to_run = None):
        "Run the tests on dialog"

        # get all the controls
        controls = [self]
        controls.extend(self.Children())

        return tests.run_tests(controls, tests_to_run)

    #-----------------------------------------------------------
    def WriteToXML(self, filename):
        "Write the dialog an XML file (requires elementtree)"
        controls = [self]
        controls.extend(self.Children())
        props = [ctrl.GetProperties() for ctrl in controls]

        from pywinauto import XMLHelpers
        XMLHelpers.WriteDialogToFile(filename, props)

    #-----------------------------------------------------------
    def ClientAreaRect(self):
        """Return the client area rectangle

        From MSDN
        The client area of a control is the bounds of the control, minus the
        nonclient elements such as scroll bars, borders, title bars, and menus."""
        rect = win32structures.RECT(self.Rectangle())
        self.SendMessage(win32defines.WM_NCCALCSIZE, 0, ctypes.byref(rect))
        return rect


#    #-----------------------------------------------------------
#    def AddReference(self, reference):
#
#        if len(self.Children() != len(reference)):
#            raise "different number of reference controls"
#
#        for i, ctrl in enumerate(reference):
#        # loop over each of the controls
#        # and set the reference
#            if isinstance(ctrl, dict):
#                ctrl = CtrlProps(ctrl)
#
#            self.
#            if ctrl.Class() != self.Children()[i+1].Class():
#                print "different classes"



#====================================================================
# the main reason for this is just to make sure that
# a Dialog is a known class - and we don't need to take
# an image of it (as an unknown control class)
class PopupMenuWrapper(HwndWrapper.HwndWrapper):
    "Wrap a Popup Menu"

    friendlyclassname = "PopupMenu"
    windowclasses = ["#32768", ]

    def IsDialog(self):
        "Return whether it is a dialog"
        return True


    def _menu_handle(self):
        "Get the menu handle for the popup menu menu"
        mbi = win32structures.MENUBARINFO()
        mbi.cbSize = ctypes.sizeof(mbi)
        ret = win32functions.GetMenuBarInfo(
            self,
            win32defines.OBJID_CLIENT,
            0,
            ctypes.byref(mbi))

        if not ret:
            raise ctypes.WinError()

        return mbi.hMenu


