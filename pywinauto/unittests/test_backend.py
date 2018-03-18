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

"""Tests for backend.py"""

import unittest

import mock
import pythoncom
import sys
sys.path.append(".")
from pywinauto import backend  # noqa: E402
from pywinauto import _get_com_threading_mode  # noqa: E402
from pywinauto.win32_element_info import HwndElementInfo  # noqa: E402
from pywinauto.controls.hwndwrapper import HwndWrapper  # noqa: E402


class BackendTestCases(unittest.TestCase):

    """Unit tests for backend registry"""

    def setUp(self):
        """Activate default win32 backend just in case"""
        backend.activate('win32')

    def test_register(self):
        """Test backend registration"""
        self.assertRaises(TypeError, backend.register, 'dummy', object, HwndWrapper)
        self.assertRaises(TypeError, backend.register, 'dummy', HwndElementInfo, object)

    def test_backend_attrs(self):
        """Test backend attributes"""
        self.assertEqual(backend.name(), 'win32')
        self.assertEqual(backend.element_class(), HwndElementInfo)
        self.assertEqual(backend.wrapper_class(), HwndWrapper)

    def test_activate(self):
        """Test activate throws exception on unsupported backend"""
        self.assertRaises(ValueError, backend.activate, 'invalid backend')


class ComInitTestCases(unittest.TestCase):

    """Unit tests for Windows COM threading mode initialization"""

    def setUp(self):
        """Mockup calls to COM API"""
        self.mock_coinitex = mock.MagicMock()
        self.orig_coinitex = pythoncom.CoInitializeEx
        pythoncom.CoInitializeEx = self.mock_coinitex

        self.orig_couninit = pythoncom.CoUninitialize
        self.mock_couninit = mock.MagicMock()
        pythoncom.CoUninitialize = self.mock_couninit

    def tearDown(self):
        """Restore real COM API"""
        pythoncom.CoInitializeEx = self.orig_coinitex
        pythoncom.CoUninitialize = self.orig_couninit

    def test_adapt_to_external_flags(self):
        """Test COM init by adapting to already defined external flags"""
        mock_sys = mock.MagicMock()

        with mock.patch("warnings.warn") as mockWarn:
            external = 3
            mock_sys.coinit_flags = external
            self.assertEqual(external, _get_com_threading_mode(mock_sys))
            args, _ = mockWarn.call_args
            assert len(args) == 2
            assert "Apply externally defined coinit_flags: 3" in args[0]
            assert args[1].__name__ == 'UserWarning'
            self.assertTrue(pythoncom.CoInitializeEx.called)
            self.assertTrue(pythoncom.CoUninitialize.called)

        external = 0  # MTA
        mock_sys.coinit_flags = external
        self.assertEqual(external, _get_com_threading_mode(mock_sys))

        external = 2  # STA
        mock_sys.coinit_flags = external
        self.assertEqual(external, _get_com_threading_mode(mock_sys))

    def test_fallback_to_sta(self):
        """Test fallback to STA if MTA probe fails"""
        local_sys = None
        expected = 2  # STA
        pythoncom.CoInitializeEx.side_effect = pythoncom.com_error
        with mock.patch("warnings.warn") as mockWarn:
            self.assertEqual(expected, _get_com_threading_mode(local_sys))
            args, _ = mockWarn.call_args
            assert len(args) == 2
            assert "Revert to STA COM threading mode" in args[0]
            assert args[1].__name__ == 'UserWarning'
            self.assertTrue(pythoncom.CoInitializeEx.called)
            self.assertFalse(pythoncom.CoUninitialize.called)

    def test_init_mta(self):
        """Test init MTA"""
        local_sys = None
        external = 0  # MTA
        self.assertEqual(external, _get_com_threading_mode(local_sys))
        self.assertTrue(pythoncom.CoInitializeEx.called)
        self.assertTrue(pythoncom.CoUninitialize.called)


if __name__ == "__main__":
    unittest.main()
