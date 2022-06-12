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

"""Tests for class FuzzyDict"""
import unittest
import sys
from collections import OrderedDict

sys.path.append(".")
from pywinauto.fuzzydict import FuzzyDict


class FuzzyTestCase(unittest.TestCase):

    """Perform some tests"""

    test_dict = OrderedDict([
        (u'Hiya', 1),
        (u'hiy\xe4', 2),
        (u'test3', 3),
        (1, 324),
        ])

    def test_creation_empty(self):
        """Verify that not specifying any values creates an empty dictionary"""
        fd = FuzzyDict()

        self.assertEqual(fd, {})

    def test_creation_dict(self):
        """Test creating a fuzzy dict"""
        fd = FuzzyDict(self.test_dict)
        self.assertEqual(fd, self.test_dict)
        self.assertEqual(self.test_dict[u'Hiya'], fd[u'hiya'])

        fd2 = FuzzyDict(self.test_dict, cutoff = .8)
        self.assertEqual(fd, self.test_dict)
        self.assertRaises(KeyError, fd2.__getitem__, u'hiya')

    def test_contains(self):
        """Test checking if an item is in a FuzzyDict"""
        fd = FuzzyDict(self.test_dict)

        self.assertEqual(True, fd.__contains__(u'hiya'))

        self.assertEqual(True, fd.__contains__(u'test3'))

        self.assertEqual(True, fd.__contains__(u'hiy\xe4'))

        self.assertEqual(False, fd.__contains__(u'FuzzyWuzzy'))

        self.assertEqual(True, fd.__contains__(1))

        self.assertEqual(False, fd.__contains__(23))

    def test_get_item(self):
        """Test getting items from a FuzzyDict"""
        fd = FuzzyDict(self.test_dict)

        self.assertEqual(self.test_dict[u"Hiya"], fd[u'hiya'])
        self.assertRaises(KeyError, fd.__getitem__, u'FuzzyWuzzy')

        fd2 = FuzzyDict(self.test_dict, cutoff = .14)

        self.assertEqual(1, fd2[u'FuzzyWuzzy'])
        self.assertEqual(324, fd2[1])
        self.assertRaises(KeyError, fd2.__getitem__, 23)


if __name__ == '__main__':
    unittest.main()
