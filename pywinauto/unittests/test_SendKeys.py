# -*- coding: latin-1 -*-
# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
# Copyright (C) 2012 Michael Herrmann
# Copyright (C) 2010 Mark Mc Mahon
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
from __future__ import unicode_literals
from __future__ import print_function

"""Module containing tests for SendKeys Module

>>> from SendKeys import *
>>> SendKeys("a\\r\\n")
>>> val = input()
>>> print val
a
>>>
>>> SendKeys(u"\x01\\r\\n")
>>> val = input()
>>> print val
u"\x01"
>>>
"""

__revision__ = "$Revision: 236 $"


import sys
sys.path.append(".")
from pywinauto.SendKeysCtypes import *
from pywinauto import six
#from SendKeys import *
import os
import unittest
#from msvcrt import getch

# Fix Python 2.x.
if six.PY2:
    input = raw_input


class SendKeysTests(unittest.TestCase):
    "Unit tests for the Sendkeys module"

    def setUp(self):
        """Actualy does nothing!"""
        #sys.stdin.flush()
        pass

    def tearDown(self):
        "delete the file we have created"
        pass

    def __run_NormalCharacters_with_options(self, **args):
        "Make sure that sending any character in range "

        #unused var: missed = []
        for i in range(32, 127):

            # skip characters that must be escaped
            if chr(i) in (' ', '%', '^', '+', '(', ')', '{', '}', '~'):
                continue

            SendKeys(chr(i) + "{ENTER}", pause = .001, **args)
            received = input()

            self.assertEquals(i, ord(received))

    # Space tests
    def testNormalWithSpaces(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_spaces = True)

    def testNormalWithoutSpaces(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_spaces = False)

    def testSpaceWithSpaces(self):
        "Make sure that with spaces option works"
        SendKeys(" \t \t {ENTER}", pause = .001, with_spaces = True)
        received = input()
        self.assertEquals("   ", received)

    def testSpaceWithoutSpaces(self):
        "Make sure that with spaces option works"
        SendKeys(" \t \t {ENTER}", pause = .001, with_spaces = False)
        received = input()
        self.assertEquals("", received)


    # Tab tests
    def testNormalWithTabs(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_tabs = True)

    def testNormalWithoutTabs(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_tabs = False)

    def testTabWithTabs(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t{ENTER}", pause = .1, with_tabs = True)
        received = input()
        self.assertEquals("\t\t\t", received)

    def testTabWithoutTabs(self):
        "Make sure that with spaces option works"
        SendKeys("\t a\t b\t{ENTER}", pause = .1, with_tabs = False)
        received = input()
        self.assertEquals("ab", received)


    def testTab(self):
        "Make sure that with spaces option works"
        SendKeys("{TAB}  {TAB} {ENTER}", pause = .3)
        received = input()
        self.assertEquals("\t\t", received)



    # Newline tests
    def testNormalWithNewlines(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_newlines = True)

    def testNormalWithoutNewlines(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_newlines = False)

    def testNewlinesWithNewlines(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t a~\tb\nc{ENTER}", pause = .1, with_newlines = True)
        received = input()
        self.assertEquals("a", received)

        received = input()
        self.assertEquals("b", received)

        received = input()
        self.assertEquals("c", received)

    def testNewlinesWithoutNewlines(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t\na{ENTER}", pause = .01, with_newlines = False)
        received = input()
        self.assertEquals("a", received)


    def testANSIExtendedCharacters(self):
        "Make sure that sending any character in range "
        os.system("chcp 850")
        matched = 0
        extended_chars = b"\x81\x82\x83\xa1\xe1\xff"
        for char in extended_chars:

            if six.PY3:
                c = str(char)
            else:
                c = char.decode('cp850')
            SendKeys(c + "{ENTER}", pause = .01)
            received = input()

            if str(char) == received:
                matched += 1
            else:
                print("expected %s, recieved %s"% (
                    repr(char), repr(received)))

        self.assertEquals(matched, len(extended_chars))

    def testCharsThatMustBeEscaped(self):
        "Make sure that escaping characters works"
        SendKeys("{%}{^}{+}{(}{)}{{}{}}{~}{ENTER}")
        received = input()
        self.assertEquals("%^+(){}~", received)


#====================================================================
if __name__ == "__main__":
    unittest.main()

    #import doctest
    #doctest.testmod()


