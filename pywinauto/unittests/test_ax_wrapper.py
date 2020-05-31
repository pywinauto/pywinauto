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

"""Tests for mac os AxWrapper"""

import os
import sys
import unittest

import sys
import os
import time
import unittest
if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    sys.path.append(parent_dir + '/macos')
    os.path.join

    from pywinauto.macos.ax_element_info import AXError, _cf_attr_to_py_object, AxElementInfo
    from pywinauto.macos.ax_element_info_object import known_control_types
    from pywinauto.macos.application import Application
    from pywinauto.controls.ax_wrapper import AXWrapper
    from pywinauto.macos.macos_structures import AX_POINT

class AXWrapperTests(unittest.TestCase):

    """Unit tests for the AXWrapper class"""

    def setUp(self):
        self.app_name = "ControlsTestAppSB"
        self.desktop_info = AxElementInfo()
        self.desktop_wrapper = AXWrapper(self.desktop_info)
        self.app = Application()
        self.app.start(name = self.app_name,new_instance = False)
        self.app_window = self.app.RootWindow.wrapper_object()
        self.app_window.set_focus()

    def tearDown(self):
        self.app.kill()

    def test_top_level_parent_for_button_return_app(self):
        button = self.app.RootWindow.TexturedRoundedButton
        top_level_parent = button.top_level_parent()
        self.assertEqual(top_level_parent.element_info.control_type,
                         "Window")

    def test_can_get_rectangle(self):
        rect = self.app.RootWindow.TexturedRoundedButton.wrapper_object().rectangle()
        self.assertAlmostEqual(rect.height(), 23, delta=2)

    def test_client_to_screen(self):
        rect = self.app_window.rectangle()
        self.assertEqual(self.app_window.client_to_screen((0, 0)),
                (rect.left, rect.top))
        self.assertEqual(self.app_window.client_to_screen(AX_POINT(x=20,y=20)),
                (rect.left + 20, rect.top + 20))

    def test_can_get_children(self):
        parent = self.app_window.parent()
        is_success = False
        for child in parent.children():
            if child == self.app_window:
                is_success = True
                break
        self.assertTrue(is_success)

    def test_can_get_descendants(self):
        self.assertTrue(len(self.app_window.descendants()) >= len(self.app_window.children()))

    def test_can_get_control_count(self):
        # Number of controls in test application is not static
        # Zero check is enough
        self.assertTrue(self.app_window.control_count() > 0)

    def test_can_get_properties(self):
        props = self.app_window.get_properties()
        self.assertEqual(props['class_name'], 'Window')
        self.assertEqual(props['friendly_class_name'], 'Window')
        self.assertEqual(props['texts'],['RootWindow'])
        self.assertEqual(props['is_enabled'], False)
        # TODO: Discuss what should we do with control_id

    def test_app_is_child_of_desktop(self):
        self.assertTrue(self.app_window.is_child(self.desktop_wrapper))

    def test_can_get_process_id(self):
        self.assertEqual(self.app_window.process_id(), self.app.process)

    def test_top_level_parent_for_window_return_window(self):
        self.assertEqual(self.app_window.top_level_parent().element_info.control_type, "Window")

    def test_window_text(self):
        self.assertEqual(self.app_window.window_text(), 'RootWindow')

    def test_root_return_desktop(self):
        self.assertEqual(self.app_window.root(), self.desktop_info)

    def test_class_name_return_element_info_class_name(self):
        self.assertEqual(self.app_window.class_name(), "Window")

if __name__ == "__main__":
    unittest.main()
