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

"""Tests for findbestmatch.py"""

import unittest
import os.path

test_path = os.path.split(__file__)[0]

import sys
sys.path.append(".")
from pywinauto import findbestmatch
from pywinauto import win32structures


class TestFindBestMatch(unittest.TestCase):

    def setUp(self):
        """load the test strings"""
        self.strings = open(os.path.join(test_path, "testtext.txt"), "rb").readlines()
        self.strings = (line.decode('utf-8')[:-1] for line in self.strings)

    def testclean_text_1(self):
        "Test for _clean_non_chars (alphanumeric symbols)"
        s = "nothingremovedhere"
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual(s, result)

    def testclean_text_2(self):
        "Test for _clean_non_chars (special symbols)"
        s = "#$%#^$%&**"
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual('', result)

    def testclean_text_3(self):
        "Test for _clean_non_chars (empty string)"
        s = ""
        result =  findbestmatch._clean_non_chars(s)
        self.assertEqual('', result)


class DummyCtrl():
    def __init__(self, l, t, r, b):
        self.rect = win32structures.RECT(l, t, r, b)
    def rectangle(self):
        return self.rect

class TestIsAboveOrToLeft(unittest.TestCase):
    def testSameRect(self):
        "both rectangles are the same so false"
        other = DummyCtrl(10, 20, 200, 40)
        this = DummyCtrl(10, 20, 200, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, False)

    def testToLeft(self):
        other = DummyCtrl(10, 20, 200, 40)
        this = DummyCtrl(100, 20, 200, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, True)

    def testAbove(self):
        other = DummyCtrl(10, 10, 200, 30)
        this = DummyCtrl(10, 20, 200, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, True)

    def testLeftAndTop(self):
        other = DummyCtrl(5, 10, 200, 20)
        this = DummyCtrl(10, 20, 200, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, True)

    def testBelow(self):
        other = DummyCtrl(10, 120, 200, 140)
        this = DummyCtrl(10, 20, 20, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, False)

    def testToRight(self):
        other = DummyCtrl(110, 20, 120, 40)
        this = DummyCtrl(10, 20, 20, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, False)


    def testTopLeftInSideControl(self):
        other = DummyCtrl(15, 25, 120, 40)
        this = DummyCtrl(10, 20, 20, 40)

        result = findbestmatch.is_above_or_to_left(this, other)
        self.assertEqual(result, False)


if __name__ == "__main__":

    unittest.main()


