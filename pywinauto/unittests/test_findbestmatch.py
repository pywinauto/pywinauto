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

"Tests for findbestmatch.py"

__revision__ = "$Revision: 234 $"

import unittest
import os.path

test_path = os.path.split(__file__)[0]

import sys
sys.path.append(".")
from pywinauto import findbestmatch
from pywinauto import win32structures


class TestFindBestMatch(unittest.TestCase):

    def setUp(self):
        # load the test strings
        self.strings = open(os.path.join(test_path, "testtext.txt"), "rb").readlines()
        self.strings = (line.decode('utf-8')[:-1] for line in self.strings)

    def testclean_text_1(self):
        s = "nothingremovedhere"
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual(s, result)

    def testclean_text_2(self):
        s = "#$%#^$%&**"
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual('', result)

    def testclean_text_3(self):
        s = ""
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual('', result)


class DummyCtrl():
    def __init__(self, l, t, r, b):
        self.rect = win32structures.RECT(l, t, r, b)
    def Rectangle(self):
        return self.rect
        
class TestIsAboveOrToLeft(unittest.TestCase):
    def testSameRect(self):
        "both rectangles are the same so false"
        other = DummyCtrl(10, 20, 200, 40)
        this = DummyCtrl(10, 20, 200, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, False)

    def testToLeft(self):
        other = DummyCtrl(10, 20, 200, 40)
        this = DummyCtrl(100, 20, 200, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, True)

    def testAbove(self):
        other = DummyCtrl(10, 10, 200, 30)
        this = DummyCtrl(10, 20, 200, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, True)

    def testLeftAndTop(self):
        other = DummyCtrl(5, 10, 200, 20)
        this = DummyCtrl(10, 20, 200, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, True)

    def testBelow(self):
        other = DummyCtrl(10, 120, 200, 140)
        this = DummyCtrl(10, 20, 20, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, False)

    def testToRight(self):
        other = DummyCtrl(110, 20, 120, 40)
        this = DummyCtrl(10, 20, 20, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, False)


    def testTopLeftInSideControl(self):
        other = DummyCtrl(15, 25, 120, 40)
        this = DummyCtrl(10, 20, 20, 40)
        
        result = findbestmatch.IsAboveOrToLeft(this, other)
        self.assertEqual(result, False)


if __name__ == "__main__":

    unittest.main()


