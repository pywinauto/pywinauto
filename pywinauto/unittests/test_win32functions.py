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

"""Tests for win32functions.py"""

import unittest

import sys
import ctypes
sys.path.append(".")
from pywinauto.win32structures import Structure, POINT, RECT  # noqa: E402
from pywinauto.win32functions import MakeLong, HiWord, LoWord  # noqa: E402


class Win32FunctionsTestCases(unittest.TestCase):
    "Unit tests for the win32function methods"

    def testMakeLong(self):
        data = (
            (0, (0, 0)),
            (1, (0, 1)),
            (0x10000, (1, 0)),
            (0xffff, (0, 0xffff)),
            (0xffff0000, (0xffff, 0)),
            (0xffffffff, (0xffff, 0xffff)),
            (0, (0x10000, 0x10000)),
        )

        for result, (hi, lo) in data:
            self.assertEqual(result, MakeLong(hi, lo))

    def testMakeLong_zero(self):
        "test that makelong(0,0)"
        self.assertEqual(0, MakeLong(0, 0))

    def testMakeLong_lowone(self):
        "Make sure MakeLong() function works with low word == 1"
        self.assertEqual(1, MakeLong(0, 1))

    def testMakeLong_highone(self):
        "Make sure MakeLong() function works with high word == 1"
        self.assertEqual(0x10000, MakeLong(1, 0))

    def testMakeLong_highbig(self):
        "Make sure MakeLong() function works with big numder in high word"
        self.assertEqual(0xffff0000, MakeLong(0xffff, 0))

    def testMakeLong_lowbig(self):
        "Make sure MakeLong() function works with big numder in low word"
        self.assertEqual(0xffff, MakeLong(0, 0xffff))

    def testMakeLong_big(self):
        "Make sure MakeLong() function works with big numders in 2 words"
        self.assertEqual(0xffffffff, MakeLong(0xffff, 0xffff))

    def testLowWord_zero(self):
        self.assertEqual(0, LoWord(0))

    def testLowWord_one(self):
        self.assertEqual(1, LoWord(1))

    def testLowWord_big(self):
        self.assertEqual(1, LoWord(MakeLong(0xffff, 1)))

    def testLowWord_vbig(self):
        self.assertEqual(0xffff, LoWord(MakeLong(0xffff, 0xffff)))

    def testHiWord_zero(self):
        self.assertEqual(0, HiWord(0))

    def testHiWord_one(self):
        self.assertEqual(0, HiWord(1))

    def testHiWord_bigone(self):
        self.assertEqual(1, HiWord(0x10000))

    def testHiWord_big(self):
        self.assertEqual(0xffff, HiWord(MakeLong(0xffff, 1)))

    def testHiWord_vbig(self):
        self.assertEqual(0xffff, HiWord(MakeLong(0xffff, 0xffff)))

    def testPOINTindexation(self):
        p = POINT(1, 2)
        self.assertEqual(p[0], p.x)
        self.assertEqual(p[1], p.y)
        self.assertEqual(p[-2], p.x)
        self.assertEqual(p[-1], p.y)
        self.assertRaises(IndexError, lambda: p[2])
        self.assertRaises(IndexError, lambda: p[-3])

    def testPOINTiteration(self):
        p = POINT(1, 2)
        self.assertEqual([1, 2], [i for i in p])

    def testPOINTcomparision(self):
        """Test POINT comparision operations"""
        p0 = POINT(1, 2)
        p1 = POINT(0, 2)
        self.assertNotEqual(p0, p1)
        p1.x = p0.x
        self.assertEqual(p0, p1)

        # tuple comparision
        self.assertEqual(p0, (1, 2))
        self.assertNotEqual(p0, (0, 2))

        # wrong type comparision
        self.assertNotEqual(p0, 1)

    def test_RECT_hash(self):
        """Test RECT is not hashable"""
        self.assertRaises(TypeError, hash, RECT())

    def test_RECT_eq(self):
        r0 = RECT(1, 2, 3, 4)
        self.assertEqual(r0, RECT(1, 2, 3, 4))
        self.assertEqual(r0, [1, 2, 3, 4])
        self.assertNotEqual(r0, RECT(1, 2, 3, 5))
        self.assertNotEqual(r0, [1, 2, 3, 5])
        self.assertNotEqual(r0, [1, 2, 3])
        self.assertNotEqual(r0, [1, 2, 3, 4, 5])
        r0.bottom = 5
        self.assertEqual(r0, RECT(1, 2, 3, 5))
        self.assertEqual(r0, (1, 2, 3, 5))

    def test_RECT_repr(self):
        """Test RECT repr"""
        r0 = RECT(0)
        self.assertEqual(r0.__repr__(), "<RECT L0, T0, R0, B0>")

    def test_Structure(self):
        class Structure0(Structure):
            _fields_ = [("f0", ctypes.c_int)]

        class Structure1(Structure):
            _fields_ = [("f1", ctypes.c_int)]

        s0 = Structure0(0)
        self.assertEqual(str(s0), "%20s\t%s" % ("f0", s0.f0))
        s1 = Structure1(0)
        self.assertNotEqual(s0, s1)
        s0._fields_.append(("f1", ctypes.c_int))
        self.assertNotEqual(s0, [0, 1])


if __name__ == "__main__":
    unittest.main()
