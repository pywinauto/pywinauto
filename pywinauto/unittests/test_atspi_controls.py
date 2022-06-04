# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
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

"""Tests for Linux AtspiWrapper-based controls"""

import os
import sys
import time
import unittest
import six
import mock
import ctypes


if sys.platform.startswith("linux"):
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.application import Application
    from pywinauto.controls.atspiwrapper import AtspiWrapper
    from pywinauto.linux.atspi_objects import AtspiAccessible
    from pywinauto.linux.atspi_objects import AtspiDocument
    from pywinauto.linux.atspi_objects import _GError
    from pywinauto.linux.atspi_objects import GHashTable
    from pywinauto.linux.atspi_objects import GErrorException
    from pywinauto.controls.atspi_controls import DocumentWrapper
    from pywinauto.linux.atspi_objects import IATSPI
    from pywinauto.linux.atspi_objects import AtspiImage
    from pywinauto.linux.atspi_objects import _AtspiRect
    from pywinauto.linux.atspi_objects import _AtspiPoint
    from pywinauto.linux.atspi_objects import _AtspiCoordType
    from pywinauto.linux.atspi_objects import RECT
    from pywinauto.linux.atspi_objects import POINT
    from pywinauto.controls.atspi_controls import ImageWrapper
    from pywinauto.findbestmatch import MatchError

app_name = r"gtk_example.py"
app_new_name = r"gtk_controls.py"
text = "This is some text inside of a Gtk.TextView. \n" \
       "Select text and click one of the buttons 'bold', 'italic', \n" \
       "or 'underline' to modify the text accordingly."
countries = ['Austria', 'Brazil', 'Belgium', 'France', 'Germany', 'Switzerland', 'United Kingdom',
             'United States of America', 'Uruguay']


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


def _test_new_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_new_name)


def print_tree(start_el_info, level_shifter=""):
    if level_shifter == "":
        print(start_el_info.control_type, "  ", start_el_info.name, "!")
        level_shifter += "-"

    for children in start_el_info.children():
        print(level_shifter, "  ", children.control_type, "    ", children.name, "!")
        print_tree(children, level_shifter + "-")


if sys.platform.startswith("linux"):
    class AtspiControlTests(unittest.TestCase):

        """Unit tests for the AtspiWrapper class"""

        def setUp(self):
            self.app = Application()
            self.app.start(_test_app())
            time.sleep(1)
            self.app_window = self.app.gtk_example
            self.button_wrapper = self.app_window.Frame.Panel.Click.find()
            self.button_info = self.app_window.Frame.Panel.Click.element_info
            self.text_area = self.app_window.Frame.Panel.ScrollPane.Text.find()

        def tearDown(self):
            self.app.kill()

        def _get_state_label_text(self):
            return self.app.gtk_example.Frame.Panel.Label.window_text()

        def test_get_action(self):
            actions_count = self.button_wrapper.action.get_n_actions()
            print("Button actions count is: {}".format(actions_count))
            for i in range(actions_count):
                print("action {} is: {}. Description: {}".format(i, self.button_wrapper.action.get_action_name(i),
                                                                 self.button_wrapper.action.get_action_description(i)))

            self.assertEqual(self.button_wrapper.action.get_localized_name(0).decode('utf-8'), "Click")

        def test_do_action(self):
            status = self.button_wrapper.action.do_action(0)
            print("Action invoked, action status is: {}".format(status))
            self.assertTrue(status)

        def test_button_click(self):
            self.assertEqual(self.button_info.rich_text, "Click")
            self.button_wrapper.click()
            self.assertEqual(self.button_info.rich_text, "Click clicked")
            self.assertEqual(self._get_state_label_text(), "\"Click\" clicked")

        def test_button_toggle(self):
            toggle_button = self.app_window.Frame.Panel.Button
            toggle_button.click()
            self.assertEqual(self._get_state_label_text(), "Button 1 turned on")

        def test_button_toggle_state(self):
            toggle_button = self.app_window.Frame.Panel.Button
            self.assertFalse(toggle_button.get_toggle_state())
            self.assertTrue(toggle_button.toggle().get_toggle_state())

        def test_text_area_is_editable(self):
            editable_state_button = self.app_window.Frame.Panel.Editable
            self.assertTrue(self.text_area.is_editable())
            editable_state_button.click()
            self.assertFalse(self.text_area.is_editable())

        def test_text_area_get_window_text(self):
            self.assertEqual(text, self.text_area.window_text())

        def test_text_area_get_text_block(self):
            self.assertEqual(text, self.text_area.text_block())

        def test_text_area_line_count(self):
            self.assertEqual(self.text_area.line_count(), 3)

        def test_text_area_line_length(self):
            split_text = text.splitlines()
            for i, line in enumerate(split_text):
                self.assertEqual(self.text_area.line_length(i), len(line))

        def test_text_area_get_line(self):
            split_text = text.splitlines()
            for i, line in enumerate(split_text):
                self.assertEqual(self.text_area.get_line(i), line)

        def test_text_area_get_texts(self):
            self.assertEqual(self.text_area.texts(), text.splitlines())

        def test_text_area_get_selection_indices(self):
            self.assertEqual(self.text_area.selection_indices(), (len(text), len(text)))

        def test_text_area_set_text(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text)
            self.assertEqual(self.text_area.window_text(), new_text)

        def test_text_area_set_not_str(self):
            new_text = 111
            self.text_area.set_text(new_text)
            self.assertEqual(self.text_area.window_text(), str(new_text))

        def test_text_area_set_byte_str(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text.encode("utf-8"))
            self.assertEqual(self.text_area.window_text(), str(new_text))

        def test_text_area_set_text_at_start_position(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text, pos_start=0, pos_end=0)
            self.assertEqual(self.text_area.window_text(), new_text + text)

        def test_text_area_set_selection(self):
            self.text_area.select(0, 10)
            self.assertEqual(self.text_area.selection_indices(), (0, 10))

        def test_combobox_is_expanded(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertFalse(combo_box.is_expanded())

        def test_combobox_expand(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertFalse(combo_box.is_expanded())
            combo_box.expand()
            self.assertTrue(combo_box.is_expanded())

        def test_combobox_collapse(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.expand()
            self.assertTrue(combo_box.is_expanded())
            combo_box.collapse()
            self.assertFalse(combo_box.is_expanded())

        def test_combobox_texts(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.texts(), countries)

        def test_combobox_selected_text(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.selected_text(), countries[0])

        def test_combobox_selected_index(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.selected_index(), 0)

        def test_combobox_item_count(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.item_count(), len(countries))

        def test_combobox_select_by_index(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.select(1)
            self.assertEqual(combo_box.selected_text(), countries[1])

        def test_combobox_select_by_text(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.select(countries[1])
            self.assertEqual(combo_box.selected_text(), countries[1])

        def test_text_area_set_selection_by_text(self):
            text_to_select = "Select text"
            self.text_area.select(text_to_select)
            self.assertEqual(self.text_area.selection_indices(),
                             (text.find(text_to_select), text.find(text_to_select) + len(text_to_select)))


    class AtspiWrapperDocumentMockedTests(unittest.TestCase):

        """Mocked unit tests for atspi_controls.DocumentWrapper.document property"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = IATSPI().known_control_types["DocumentFrame"]
            self.wrp = AtspiWrapper(self.info)

        def tearDown(self):
            self.patch_get_role.stop()

        def test_document_success(self):
            self.assertEqual(type(self.wrp), DocumentWrapper)
            self.assertEqual(type(self.wrp.document), AtspiDocument)

        def test_document_fail_on_wrong_role(self):
            self.mock_get_role.return_value = IATSPI().known_control_types["Invalid"]
            self.wrp = AtspiWrapper(self.info)
            self.assertRaises(AttributeError, lambda: self.wrp.document)

        @mock.patch.object(AtspiDocument, 'get_locale')
        def test_document_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"C"
            self.assertEqual(self.wrp.locale(), u"C")

        @mock.patch.object(AtspiDocument, '_get_locale')
        def test_document_get_locale_gerror_fail(self, mock_get_locale):
            gerror = _GError()
            gerror.code = 222
            gerror.message = b"Mocked GError message"

            def stub_get_locale(atspi_doc_ptr, gerr_pp):
                self.assertEqual(type(atspi_doc_ptr), AtspiAccessible.get_document.restype)
                self.assertEqual(type(gerr_pp), (ctypes.POINTER(ctypes.POINTER(_GError))))
                gerr_pp[0] = ctypes.pointer(gerror)
                return b"C"

            mock_get_locale.side_effect = stub_get_locale

            expected_err_msg = "GError with code: {0}, message: '{1}'".format(
                               gerror.code, gerror.message.decode(encoding='UTF-8'))
            six.assertRaisesRegex(self,
                                  GErrorException,
                                  expected_err_msg,
                                  self.wrp.locale)

        @mock.patch.object(AtspiDocument, '_get_attribute_value')
        def test_document_get_attribute_value_success(self, mock_get_attribute_value):
            attrib = u"dummy attribute"
            mock_get_attribute_value.return_value = b"dummy val"
            self.assertEqual(self.wrp.attribute_value(attrib), u"dummy val")
            self.assertEqual(type(mock_get_attribute_value.call_args[0][1]), ctypes.c_char_p)

        @mock.patch.object(AtspiDocument, '_get_attributes')
        def test_document_get_attributes_success(self, mock_get_attributes):
            attrib = b"dummy attribute"
            mock_get_attributes.return_value = GHashTable.dic2ghash({attrib: b"dummy val"})
            res = self.wrp.attributes()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[attrib.decode('utf-8')], u"dummy val")

    class AtspiWrapperImageMockedTests(unittest.TestCase):

        """Mocked unit tests for atspi_controls.ImageWrapper.image property"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = IATSPI().known_control_types["Image"]
            self.wrp = AtspiWrapper(self.info)

        def tearDown(self):
            self.patch_get_role.stop()

        def test_image_success(self):
            self.assertEqual(type(self.wrp), ImageWrapper)
            self.assertEqual(type(self.wrp.image), AtspiImage)

            # Icon role should be also handled by AtspiImage
            self.mock_get_role.return_value = IATSPI().known_control_types["Icon"]
            iconWrp = AtspiWrapper(self.info)
            self.assertEqual(type(iconWrp.image), AtspiImage)

        def test_image_fail_on_wrong_role(self):
            self.mock_get_role.return_value = IATSPI().known_control_types["Invalid"]
            self.wrp = AtspiWrapper(self.info)
            self.assertEqual(type(self.wrp), AtspiWrapper)
            self.assertRaises(AttributeError, lambda: self.wrp.image)

        @mock.patch.object(AtspiImage, '_get_image_locale')
        def test_image_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"I"
            self.assertEqual(self.wrp.image.get_locale(), b"I")

        @mock.patch.object(AtspiImage, '_get_image_description')
        def test_image_get_description_success(self, mock_get_description):
            mock_get_description.return_value = b"descr"
            self.assertEqual(self.wrp.image.get_description(), b"descr")

        @mock.patch.object(AtspiImage, '_get_image_extents')
        def test_image_get_image_extents_success(self, mock_get_extents):
            extents_rect = _AtspiRect(22, 11, 33, 44)
            mock_get_extents.return_value = ctypes.pointer(extents_rect)
            self.assertEqual(self.wrp.image.get_extents(), RECT(extents_rect))
            self.assertEqual(mock_get_extents.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)

        @mock.patch.object(AtspiImage, '_get_image_position')
        def test_image_get_image_position_success(self, mock_get_position):
            pnt = _AtspiPoint()
            pnt.x = 55
            pnt.y = 66
            mock_get_position.return_value = ctypes.pointer(pnt)
            self.assertEqual(self.wrp.image.get_position(), POINT(pnt.x, pnt.y))
            self.assertEqual(mock_get_position.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)


    class AtspiMenuWrapperTests(unittest.TestCase):

        """Unit tests for atspi_controls.MenuWrapper"""

        def setUp(self):
            self.app = Application()
            self.app.start(_test_new_app())
            time.sleep(1)
            self.app_window = self.app.gtk_controls
            self.app_wrapper = self.app_window.find()

        def tearDown(self):
            self.app.kill()

        def test_menu_item_count(self):
            menu_bar = self.app_wrapper.get_menu()
            self.assertEqual(menu_bar.item_count(), 4)

        def test_menu_selected_name(self):
            menu_bar = self.app_wrapper.get_menu()
            menu = menu_bar.item_by_path("File")
            self.assertEqual(menu.selected_menu_name(), "File")

        def test_menu_selected_index(self):
            menu_bar = self.app_wrapper.get_menu()
            menu = menu_bar.item_by_path("#0 -> #2")
            self.assertEqual(menu.selected_index(), 2)

        def test_menu_select_by_text(self):
            menu_bar = self.app_wrapper.get_menu()
            menu = menu_bar.item_by_path("File")
            self.assertTrue(menu.element_info.control_type == "Menu" and menu.selected_menu_name() == "File")

        def test_menu_select_by_index(self):
            menu_bar = self.app_wrapper.get_menu()
            menu = menu_bar.item_by_path("#0")
            self.assertTrue(menu.element_info.control_type == "Menu" and menu.selected_menu_name() == "File")

        def test_menu_item_select_by_text(self):
            menu_bar = self.app_wrapper.get_menu()
            menu_item = menu_bar.item_by_path("File -> Open")
            self.assertTrue(
                menu_item.element_info.control_type == "MenuItem" and menu_item.selected_menu_name() == "Open")

        def test_menu_item_select_by_index(self):
            menu_bar = self.app_wrapper.get_menu()
            menu_item = menu_bar.item_by_path("#0 -> #2")
            self.assertTrue(
                menu_item.element_info.control_type == "MenuItem" and menu_item.selected_menu_name() == "Exit")

        def test_menu_wrong_name(self):
            menu_bar = self.app_wrapper.get_menu()
            with self.assertRaises(MatchError):
                menu_bar.item_by_path("Tool")

        def test_menu_wrong_index(self):
            menu_bar = self.app_wrapper.get_menu()
            with self.assertRaises(IndexError):
                menu_bar.item_by_path("#2")

        def test_menu_empty_submenu_by_name(self):
            menu_bar = self.app_wrapper.get_menu()
            with self.assertRaises(IndexError):
                menu_bar.item_by_path("File -> -> Template")

        def test_menu_empty_submenu_by_index(self):
            menu_bar = self.app_wrapper.get_menu()
            with self.assertRaises(IndexError):
                menu_bar.item_by_path("#0 -> -> #1")

        def test_menu_exact_name_true(self):
            menu_bar = self.app_wrapper.get_menu()
            with self.assertRaises(IndexError):
                menu_bar.item_by_path("File -> Ope", exact=True)

        def test_menu_exact_name_false(self):
            menu_bar = self.app_wrapper.get_menu()
            menu_item = menu_bar.item_by_path("Fi -> Ex")
            self.assertTrue(
                menu_item.element_info.control_type == "MenuItem" and menu_item.selected_menu_name() == "Exit")



    class AtspiScrollBarWrapperTests(unittest.TestCase):

        """Unit tests for atspi_controls.ScrollBarWrapper"""

        def setUp(self):
            self.app = Application()
            self.app.start(_test_new_app())
            self.app_window = self.app.gtk_controls
            self.app_wrapper = self.app_window.find()

        def tearDown(self):
            self.app.kill()

        def test_min_value_is_float(self):
            scrollbar = self.app_wrapper.get_slider()
            self.assertTrue(type(scrollbar.min_value()) == float)

        def test_scrollbar_value_less_than_minimum(self):
            scrollbar = self.app_wrapper.get_slider()
            min_value = scrollbar.min_value()
            with self.assertRaises(ValueError):
                scrollbar.set_value(min_value - 1)

        def test_scrollbar_value_more_than_maximum(self):
            scrollbar = self.app_wrapper.get_slider()
            max_value = scrollbar.max_value()
            with self.assertRaises(ValueError):
                scrollbar.set_value(max_value + 1)


if __name__ == "__main__":
    unittest.main()
