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

from pywinauto import findbestmatch


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


if __name__ == "__main__":

    unittest.main()


