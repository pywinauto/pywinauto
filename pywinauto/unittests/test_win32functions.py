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

"Tests for win32functions.py"

__revision__ = "$Revision: 234 $"

import unittest

import sys
sys.path.append(".")
from pywinauto.win32functions import *

import struct


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
        "Make sure the friendly class is set correctly"
        self.assertEquals(1, MakeLong(0,1))

    def testMakeLong_highone(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals(0x10000, MakeLong(1,0))

    def testMakeLong_highbig(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals(0xffff0000, MakeLong(0xffff,0))

    def testMakeLong_lowbig(self):
        "Make sure the friendly class is set correctly"
        self.assertEquals(0xffff, MakeLong(0, 0xffff))

    def testMakeLong_big(self):
        "Make sure the friendly class is set correctly"
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

if __name__ == "__main__":
    unittest.main()


