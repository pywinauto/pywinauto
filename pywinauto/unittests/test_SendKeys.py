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

"""Module containing tests for XMLHelpers Module

>>> from SendKeys import *
>>> SendKeys("a\\r\\n")
>>> val = raw_input()
>>> print val
a
>>>
>>> SendKeys(u"‰\\r\\n")
>>> val = raw_input()
>>> print val
‰
>>>

"""

__revision__ = "$Revision: 236 $"


from SendKeys import *

import unittest
import sys
from msvcrt import getch

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

        missed = []
        for i in range(32, 127):

            # skip characters that must be escaped
            if chr(i) in (' ', '%', '^', '+', '(', ')', '{', '}', '~'):
                continue

            SendKeys(chr(i) + "{ENTER}", pause = .001, **args)
            received = raw_input()

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
        received = raw_input()
        self.assertEquals("   ", received)

    def testSpaceWithoutSpaces(self):
        "Make sure that with spaces option works"
        SendKeys(" \t \t {ENTER}", pause = .001, with_spaces = False)
        received = raw_input()
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
        SendKeys("\t \t \t{ENTER}", pause = .001, with_tabs = True)
        received = raw_input()
        self.assertEquals("\t\t\t", received)

    def testTabWithoutTabs(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t{ENTER}", pause = .001, with_tabs = False)
        received = raw_input()
        self.assertEquals("", received)


    # Newline tests
    def testNormalWithNewlines(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_newlines = True)

    def testNormalWithoutNewlines(self):
        "Make sure that with spaces option works"
        self.__run_NormalCharacters_with_options(with_newlines = False)

    def testNewlinesWithNewlines(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t\n\{ENTER}", pause = .001, with_newlines = True)
        received = raw_input()
        self.assertEquals("", received)
        # there are actally two enter's above - so we need to clear the buffer
        received = raw_input()

    def testNewlinesWithoutNewlines(self):
        "Make sure that with spaces option works"
        SendKeys("\t \t \t\na{ENTER}", pause = .001, with_newlines = False)
        received = raw_input()
        self.assertEquals("a", received)


    def testANSIExtendedCharacters(self):
        "Make sure that sending any character in range "

        matched = 0
        extended_chars = "‰ÎÔˆ¸·ÈÌÛ˙‚ÍÓÙ˚‡ËÏÚ˘„ıÒ˝Á"
        for char in extended_chars:

            SendKeys(char + "{ENTER}", pause = .001)
            received = raw_input()

            if char == received:
                matched += 1

        self.assertEquals(matched, len(extended_chars))




#====================================================================
if __name__ == "__main__":
    unittest.main()

    #import doctest
    #doctest.testmod()


