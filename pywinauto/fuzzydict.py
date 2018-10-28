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

"""Match items in a dictionary using fuzzy matching

Implemented for pywinauto.

This class uses difflib to match strings.
This class uses a linear search to find the items as it HAS to iterate over
every item in the dictionary (otherwise it would not be possible to know which
is the 'best' match).

If the exact item is in the dictionary (no fuzzy matching needed - then it
doesn't do the linear search and speed should be similar to standard Python
dictionaries.

>>> fuzzywuzzy = FuzzyDict({"hello" : "World", "Hiya" : 2, "Here you are" : 3})
>>> fuzzywuzzy['Me again'] = [1,2,3]
>>>
>>> fuzzywuzzy['Hi']
2
>>>
>>>
>>> # next one doesn't match well enough - so a key error is raised
...
>>> fuzzywuzzy['There']
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "pywinauto\fuzzydict.py", line 125, in __getitem__
    raise KeyError(
KeyError: "'There'. closest match: 'hello' with ratio 0.400"
>>>
>>> fuzzywuzzy['you are']
3
>>> fuzzywuzzy['again']
[1, 2, 3]
>>>
"""
from __future__ import unicode_literals

import difflib
from collections import OrderedDict

class FuzzyDict(OrderedDict):

    """Provides a dictionary that performs fuzzy lookup"""

    def __init__(self, items = None, cutoff = .6):
        """
        Construct a new FuzzyDict instance

        items is an dictionary to copy items from (optional)
        cutoff is the match ratio below which mathes should not be considered
        cutoff needs to be a float between 0 and 1 (where zero is no match
        and 1 is a perfect match).
        """
        super(FuzzyDict, self).__init__()

        # short wrapper around some super (OrderedDict) methods
        self._dict_contains = lambda key: \
            super(FuzzyDict, self).__contains__(key)

        self._dict_getitem = lambda key: \
            super(FuzzyDict, self).__getitem__(key)

        self.cutoff =  cutoff
        if items:
            self.update(items)

    def _search(self, lookfor, stop_on_first = False):
        """
        Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item.
        """
        # if the item is in the dictionary then just return it
        if self._dict_contains(lookfor):
            return True, lookfor, self._dict_getitem(lookfor), 1

        # set up the fuzzy matching tool
        ratio_calc = difflib.SequenceMatcher()
        ratio_calc.set_seq1(lookfor)

        # test each key in the dictionary
        best_ratio = 0
        best_match = None
        best_key = None
        for key in self:

            # if the current key is not a string
            # then we just skip it
            try:
                # set up the SequenceMatcher with other text
                ratio_calc.set_seq2(key)
            except TypeError:
                continue

            # we get an error here if the item to look for is not a
            # string - if it cannot be fuzzy matched and we are here
            # this it is defintely not in the dictionary
            try:
                # calculate the match value
                ratio = ratio_calc.ratio()
            except TypeError:
                break

            # if this is the best ratio so far - save it and the value
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = key
                best_match = self._dict_getitem(key)

            if stop_on_first and ratio >= self.cutoff:
                break

        return (
            best_ratio >= self.cutoff,
            best_key,
            best_match,
            best_ratio)

    def __contains__(self, item):
        """Overides OrderedDict __contains__ to use fuzzy matching"""
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor):
        """Overides OrderedDict __getitem__ to use fuzzy matching"""
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError("'{0}'. closest match: '{1}' with ratio {2}".\
                format(str(lookfor), str(key), ratio))

        return item
