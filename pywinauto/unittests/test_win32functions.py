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
sys.path.append(".")
from pywinauto.win32structures import POINT
from pywinauto.win32functions import MakeLong, HiWord, LoWord


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
            self.assertEquals(result, MakeLong(hi,lo))



    def testMakeLong_zero(self):
        "test that makelong(0,0)"
        self.assertEquals(0, MakeLong(0,0))

    def testMakeLong_lowone(self):
        "Make sure MakeLong() function works with low word == 1"
        self.assertEquals(1, MakeLong(0,1))

    def testMakeLong_highone(self):
        "Make sure MakeLong() function works with high word == 1"
        self.assertEquals(0x10000, MakeLong(1,0))

    def testMakeLong_highbig(self):
        "Make sure MakeLong() function works with big numder in high word"
        self.assertEquals(0xffff0000, MakeLong(0xffff,0))

    def testMakeLong_lowbig(self):
        "Make sure MakeLong() function works with big numder in low word"
        self.assertEquals(0xffff, MakeLong(0, 0xffff))

    def testMakeLong_big(self):
        "Make sure MakeLong() function works with big numders in 2 words"
        self.assertEquals(0xffffffff, MakeLong(0xffff, 0xffff))

    def testLowWord_zero(self):
        self.assertEquals(0, LoWord(0))

    def testLowWord_one(self):
        self.assertEquals(1, LoWord(1))

    def testLowWord_big(self):
        self.assertEquals(1, LoWord(MakeLong(0xffff, 1)))

    def testLowWord_vbig(self):
        self.assertEquals(0xffff, LoWord(MakeLong(0xffff, 0xffff)))

    def testHiWord_zero(self):
        self.assertEquals(0, HiWord(0))

    def testHiWord_one(self):
        self.assertEquals(0, HiWord(1))

    def testHiWord_bigone(self):
        self.assertEquals(1, HiWord(0x10000))

    def testHiWord_big(self):
        self.assertEquals(0xffff, HiWord(MakeLong(0xffff, 1)))

    def testHiWord_vbig(self):
        self.assertEquals(0xffff, HiWord(MakeLong(0xffff, 0xffff)))

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
        self.assertEquals([1, 2], [i for i in p])


if __name__ == "__main__":
    unittest.main()


