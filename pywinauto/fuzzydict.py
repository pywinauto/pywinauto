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

__revision__ = "$Rev$"

import difflib

class FuzzyDict(dict):
    "Provides a dictionary that performs fuzzy lookup"
    def __init__(self, items = None, cutoff = .6):
        """Construct a new FuzzyDict instance

        items is an dictionary to copy items from (optional)
        cutoff is the match ratio below which mathes should not be considered
        cutoff needs to be a float between 0 and 1 (where zero is no match
        and 1 is a perfect match)"""
        super(FuzzyDict, self).__init__()

        if items:
            self.update(items)
        self.cutoff =  cutoff

        # short wrapper around some super (dict) methods
        self._dict_contains = lambda key: \
            super(FuzzyDict,self).__contains__(key)

        self._dict_getitem = lambda key: \
            super(FuzzyDict,self).__getitem__(key)

    def _search(self, lookfor, stop_on_first = False):
        """Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item
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
        "Overides Dictionary __contains__ to use fuzzy matching"
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor):
        "Overides Dictionary __getitem__ to use fuzzy matching"
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError(
                "'%s'. closest match: '%s' with ratio %.3f"%
                    (str(lookfor), str(key), ratio))

        return item



if __name__ == '__main__':
    import unittest

    class FuzzyTestCase(unittest.TestCase):
        "Perform some tests"
        test_dict = {
            'Hiya'  : 1,
            u'hiy\xe4' : 2,
            'test3' : 3,
            1: 324}


        def testCreation_Empty(self):
            "Verify that not specifying any values creates an empty dictionary"
            fd = FuzzyDict()

            self.assertEquals(fd, {})

        def testCreation_Dict(self):
            "Test creating a fuzzy dict"
            fd = FuzzyDict(self.test_dict)
            self.assertEquals(fd, self.test_dict)
            self.assertEquals(self.test_dict['Hiya'], fd['hiya'])

            fd2 = FuzzyDict(self.test_dict, cutoff = .8)
            self.assertEquals(fd, self.test_dict)
            self.assertRaises(KeyError, fd2.__getitem__, 'hiya')


        def testContains(self):
            "Test checking if an item is in a FuzzyDict"
            fd = FuzzyDict(self.test_dict)

            self.assertEquals(True, fd.__contains__('hiya'))

            self.assertEquals(True, fd.__contains__(u'test3'))

            self.assertEquals(True, fd.__contains__(u'hiy\xe4'))

            self.assertEquals(False, fd.__contains__('FuzzyWuzzy'))

            self.assertEquals(True, fd.__contains__(1))

            self.assertEquals(False, fd.__contains__(23))


        def testGetItem(self):
            "Test getting items from a FuzzyDict"
            fd = FuzzyDict(self.test_dict)

            self.assertEquals(self.test_dict["Hiya"], fd['hiya'])
            self.assertRaises(KeyError, fd.__getitem__, 'FuzzyWuzzy')

            fd2 = FuzzyDict(self.test_dict, cutoff = .14)

            self.assertEquals(1, fd2['FuzzyWuzzy'])
            self.assertEquals(324, fd2[1])
            self.assertRaises(KeyError, fd2.__getitem__, 23)

    unittest.main()