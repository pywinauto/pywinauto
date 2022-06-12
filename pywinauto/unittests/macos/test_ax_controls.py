# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""Tests for mac os Controls"""

import sys
import unittest

import sys
import os
import time
import unittest
if sys.platform == 'darwin':
    sys.path.append(".")
    from pywinauto.macos.application import Application
    from pywinauto.macos.macos_structures import AX_POINT, AX_RECT

class ButtonWrapperTests(unittest.TestCase):

    """Unit tests for the ButtonWrapper"""

    def setUp(self):
        self.app_name = "ControlsTestAppSB"
        self.app = Application()
        self.app.start(name = self.app_name,new_instance = False)
        self.app_window = self.app.RootWindow.wrapper_object()
        self.app_window.set_focus()

        self.checkbox = self.app.RootWindow.Check.wrapper_object()
        self.recessed_btn = self.app.RootWindow.Recessed.wrapper_object()

    def tearDown(self):
        self.app.kill()

    def test_click(self):
        self.assertTrue(self.checkbox.get_toggle_state())
        self.checkbox.click()
        self.assertTrue(not self.checkbox.get_toggle_state())

    def test_toggle(self):
        self.assertTrue(self.checkbox.get_toggle_state())
        self.checkbox.click()
        self.assertTrue(not self.checkbox.get_toggle_state())

    def test_get_toggle_state(self):
        self.assertTrue(self.checkbox.get_toggle_state())

    def test_is_dialog(self):
        self.assertEqual(self.checkbox.is_dialog(), False)

    def test_is_window_managment_button(self):
        children = self.app.RootWindow.children(subrole='AXFullScreenButton')
        self.assertTrue(len(children)>0)
        full_screen_button = children[0]
        self.assertTrue(full_screen_button.is_window_managment_button)

class ImageWrapperTests(unittest.TestCase):

    """Unit tests for the ImageWrapper"""

    def setUp(self):
        self.app_name = "ControlsTestAppSB"
        self.app = Application()
        self.app.start(name=self.app_name, new_instance=False)
        self.app_window = self.app.RootWindow.wrapper_object()
        self.app_window.set_focus()
        self.image = self.app.RootWindow.Image.wrapper_object()
        self.checkbox = self.app.RootWindow.Check.wrapper_object()

    def tearDown(self):
        self.app.kill()

    def test_description(self):
        """Get image description"""
        self.assertEqual(self.image.description,'pywinautoImage')

    def test_size(self):
        """Get image size. Return a tuple with width and height"""
        self.assertEqual(self.image.size,(60,60))

    def test_bounding_box(self):
        """Get image bounding box"""
        textfield1 = self.app.RootWindow.TextField1.wrapper_object().element_info.rectangle.bottom
        textfield2 = self.app.RootWindow.TextField2.wrapper_object().element_info.rectangle.bottom
        textfield3 = self.app.RootWindow.TextField3.wrapper_object().element_info.rectangle.bottom
        self.assertEqual(textfield1 + 30,textfield2)
        self.assertEqual(textfield2 + 30, textfield3)

    def test_position(self):
        """Get image position coordinates"""
        textfield1 = self.app.RootWindow.TextField1.wrapper_object().element_info.rectangle.bottom
        textfield2 = self.app.RootWindow.TextField2.wrapper_object().element_info.rectangle.bottom
        textfield3 = self.app.RootWindow.TextField3.wrapper_object().element_info.rectangle.bottom
        self.assertEqual(textfield1 + 30,textfield2)
        self.assertEqual(textfield2 + 30, textfield3)

class ComboboxWrapperTests(unittest.TestCase):

    """Unit tests for the ComboboxWrapper"""

    def setUp(self):
        self.app_name = "ControlsTestAppSB"
        self.app = Application()
        self.app.start(name = self.app_name,new_instance = False)
        self.app_window = self.app.RootWindow.wrapper_object()
        self.app_window.set_focus()

        self.combobox = self.app.RootWindow.Combobox.wrapper_object()

    def tearDown(self):
        self.app.kill()

    def test_can_expand(self):
        """Checks that combobox can be expanded"""
        self.combobox.expand()
        self.assertTrue(self.combobox.is_expanded)

    def test_can_collapse(self):
        """Checks that combobox can be expanded"""
        self.combobox.collapse()
        self.assertTrue(not self.combobox.is_expanded)

    def test_can_get_texts(self):
        """Checks that combobox options can be obtained"""
        self.assertEqual(self.combobox.texts, ['BoxItem1', 'BoxItem2', 'BoxItem3', 'Default'])

    def test_can_get_selected_text(self):
        """Checks that combobox value can be obtained"""
        self.assertEqual(self.combobox.selected_text, 'Default')

    def test_can_get_item_count(self):
        """Checks that the lenght of items can be obtained"""
        self.assertEqual(self.combobox.item_count, 4)

    def test_can_get_selected_index(self):
        """Checks that selected index can be obtained"""
        self.assertEqual(self.combobox.selected_index, self.combobox.item_count-1)

    def test_can_select_by_index(self):
        """Checks that the combobox value can set by index"""
        desired_index = 0
        self.assertNotEqual(self.combobox.selected_index, desired_index)
        self.combobox.select(desired_index)
        self.assertEqual(self.combobox.selected_index, desired_index)

if __name__ == "__main__":
    unittest.main()
