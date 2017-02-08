# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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

"""Tests for backend.py"""

import unittest

import sys
sys.path.append(".")
from pywinauto import backend
from pywinauto.win32_element_info import HwndElementInfo
from pywinauto.controls.hwndwrapper import HwndWrapper


class BackendTestCases(unittest.TestCase):

    """Unit tests for backend registry"""

    def setUp(self):
        """Activate default win32 backend just in case"""
        backend.activate('win32')

    def test_register(self):
        self.assertRaises(TypeError, backend.register, 'dummy', object, HwndWrapper)
        self.assertRaises(TypeError, backend.register, 'dummy', HwndElementInfo, object)

    def test_backend_attrs(self):
        self.assertEqual(backend.name(), 'win32')
        self.assertEqual(backend.element_class(), HwndElementInfo)
        self.assertEqual(backend.wrapper_class(), HwndWrapper)

    def test_activate(self):
        self.assertRaises(ValueError, backend.activate, 'invalid backend')


if __name__ == "__main__":
    unittest.main()
