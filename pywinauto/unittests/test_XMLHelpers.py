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

"""Module containing tests for XMLHelpers Module"""

__revision__ = "$Revision: 236 $"

import sys
sys.path.append(".")

from pywinauto.XMLHelpers import *

import unittest

class XMLHelperTestCases(unittest.TestCase):
    "Unit tests for the ListViewWrapper class"

    def setUp(self):
        """Actually does nothing!"""
        pass

    def tearDown(self):
        "delete the file we have created"
        import os
        os.unlink("__unittests.xml")

    def assertReadWriteSame(self, props):
        "Make sure that roundtripping produces identical file"
        WriteDialogToFile("__unittests.xml", props)

        read_props = ReadPropertiesFromFile("__unittests.xml")
        self.assertEquals(props, read_props)

    def testOneUnicode(self):
        "Make sure the friendly class is set correctly"
        props = [dict(test = u"hiya")]
        self.assertReadWriteSame(props)

    def testOneString(self):
        "Make sure the friendly class is set correctly"
        props = [dict(test = "hiya")]
        self.assertReadWriteSame(props)

    def testSomeEscapes(self):
        "Make sure the friendly class is set correctly"

        test_string = []
        for i in range(0, 50000):
            test_string.append(unichr(i))

        test_string = "".join(test_string)

        props = [dict(test = test_string)]
        self.assertReadWriteSame(props)


    def testOneBool(self):
        "Test writing/reading Bool"
        props = [dict(test = True)]
        self.assertReadWriteSame(props)

    def testOneList(self):
        "Test writing/reading a list"
        props = [dict(test = [1, 2, 3, 4, 5, 6])]
        self.assertReadWriteSame(props)

    def testOneDict(self):
        "Make sure the friendly class is set correctly"
        props = [dict(test_value = dict(test = 1))]
        self.assertReadWriteSame(props)

    def testOneLong(self):
        "Test writing/reading one long is correct"
        props = [dict(test = 1)]
        self.assertReadWriteSame(props)

    def testLOGFONTW(self):
        "Test writing/reading one LOGFONTW is correct"
        font = LOGFONTW()
        font.lfWeight = 23
        font.lfFaceName = u"wowow"
        props = [dict(test = font)]
        self.assertReadWriteSame(props)

    def testRECT(self):
        "Test writing/reading one RECT is correct"
        props = [dict(test = RECT(1, 2, 3, 4))]
        self.assertReadWriteSame(props)

    def testTwoLong(self):
        "Test writing/reading two longs is correct"
        props = [dict(test = 1), dict(test_blah = 2)]
        self.assertReadWriteSame(props)

    def testEmptyList(self):
        "Test writing/reading empty list"
        props = [dict(test = [])]
        self.assertReadWriteSame(props)

    def testEmptyDict(self):
        "Test writing/reading empty dict"
        props = [dict(test = {})]
        self.assertReadWriteSame(props)


#====================================================================
if __name__ == "__main__":
    unittest.main()


