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

"""Module containing tests for xml_helpers Module"""

import os
import sys
import unittest
import six
sys.path.append(".")

from pywinauto.xml_helpers import WriteDialogToFile
from pywinauto.xml_helpers import ReadPropertiesFromFile
from pywinauto.xml_helpers import LOGFONTW
from pywinauto.xml_helpers import RECT


class XMLHelperTestCases(unittest.TestCase):

    """Unit tests for the ListViewWrapper class"""

    #def setUp(self):
    #    """Actually does nothing!"""
    #    pass

    def tearDown(self):
        """delete the file we have created"""
        os.unlink("__unittests.xml")

    def assertReadWriteSame(self, props):
        """Make sure that roundtripping produces identical file"""
        WriteDialogToFile("__unittests.xml", props)

        read_props = ReadPropertiesFromFile("__unittests.xml")
        self.assertEqual(props, read_props)

    def testOneUnicode(self):
        """Test writing/reading a unicode string"""
        props = [dict(test = u"hiya")]
        self.assertReadWriteSame(props)

    def testOneString(self):
        """Test writing/reading a string"""
        props = [dict(test = "hiya")]
        self.assertReadWriteSame(props)

    def testSomeEscapes(self):
        """Test writing/reading a dictionary with some escape sequences"""
        test_string = []
        for i in range(0, 50000):
            test_string.append(six.unichr(i))

        test_string = "".join(test_string)

        props = [dict(test = test_string)]
        self.assertReadWriteSame(props)


    def testOneBool(self):
        """Test writing/reading Bool"""
        props = [dict(test = True)]
        self.assertReadWriteSame(props)

    def testOneList(self):
        """Test writing/reading a list"""
        props = [dict(test = [1, 2, 3, 4, 5, 6])]
        self.assertReadWriteSame(props)

    def testOneDict(self):
        """Test writing/reading a dictionary with one element"""
        props = [dict(test_value = dict(test = 1))]
        self.assertReadWriteSame(props)

    def testOneLong(self):
        """Test writing/reading one long is correct"""
        props = [dict(test = 1)]
        self.assertReadWriteSame(props)

    def testLOGFONTW(self):
        """Test writing/reading one LOGFONTW is correct"""
        font = LOGFONTW()
        font.lfWeight = 23
        font.lfFaceName = u"wowow"
        props = [dict(test = font)]
        self.assertReadWriteSame(props)

    def testRECT(self):
        """Test writing/reading one RECT is correct"""
        props = [dict(test = RECT(1, 2, 3, 4))]
        self.assertReadWriteSame(props)

    def testTwoLong(self):
        """Test writing/reading two longs is correct"""
        props = [dict(test = 1), dict(test_blah = 2)]
        self.assertReadWriteSame(props)

    def testEmptyList(self):
        """Test writing/reading empty list"""
        props = [dict(test = [])]
        self.assertReadWriteSame(props)

    def testEmptyDict(self):
        """Test writing/reading empty dict"""
        props = [dict(test = {})]
        self.assertReadWriteSame(props)


#====================================================================
if __name__ == "__main__":
    unittest.main()
