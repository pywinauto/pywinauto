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

"Module to find the closest match of a string in a list"

__revision__ = "$Revision$"

import re
import difflib

import fuzzydict

# need to use sets.Set for python 2.3 compatability
import sets

find_best_control_match_cutoff = .6

#====================================================================
class MatchError(IndexError):
    "A suitable match could not be found"
    def __init__(self, items = None, tofind = ''):
        "Init the parent with the message"
        self.tofind = tofind
        self.items = items
        if self.items is None:
            self.items = []

        IndexError.__init__(self,
            "Could not find '%s' in '%s'"% (tofind, self.items))




# given a list of texts return the match score for each
# and the best score and text with best score
#====================================================================
def _get_match_ratios(texts, match_against):
    "Get the match ratio of how each item in texts compared to match_against"

    # now time to figre out the matching
    ratio_calc = difflib.SequenceMatcher()
    ratio_calc.set_seq1(match_against)

    ratios = {}
    best_ratio = 0
    best_text = ''

    for text in texts:
        # set up the SequenceMatcher with other text
        ratio_calc.set_seq2(text)

        # calculate ratio and store it
        ratios[text] = ratio_calc.ratio()

        # if this is the best so far then update best stats
        if ratios[text] > best_ratio:
            best_ratio = ratios[text]
            best_text = text

    return ratios, best_ratio, best_text




#====================================================================
def find_best_match(search_text, item_texts, items):
    "Return the item that best matches the search_text"
    search_text = _cut_at_tab(search_text)


    text_item_map = UniqueDict()
    # Clean each item, make it unique and map to
    # to the item index
    for text, item in zip(item_texts, items):
        text_item_map[_cut_at_tab(text)] = item

    ratios, best_ratio, best_text = \
        _get_match_ratios(text_item_map.keys(), search_text)

    if best_ratio < .5:
        raise MatchError(items = text_item_map.keys(), tofind = search_text)

    return text_item_map[best_text]





#====================================================================
_after_tab = re.compile(ur"\t.*", re.UNICODE)
_non_word_chars = re.compile(ur"\W", re.UNICODE)

def _cut_at_tab(text):
    "Clean out non characters from the string and return it"

    # remove anything after the first tab
    return  _after_tab.sub("", text)

def _clean_non_chars(text):
    "Remove non word characters"
    # should this also remove everything after the first tab?

    # remove non alphanumeric characters
    return _non_word_chars.sub("", text)


def IsAboveOrToLeft(ref_control, other_ctrl):
    "Return true if the other_ctrl is above or to the left of ref_control"
    text_r = other_ctrl.Rectangle()
    ctrl_r = ref_control.Rectangle()

    # skip controls where text win is to the right of ctrl
    if text_r.left >= ctrl_r.right:
        return False

    # skip controls where text win is below ctrl
    if text_r.top >= ctrl_r.bottom:
        return False

    return True


#====================================================================
distance_cuttoff = 999
def GetNonTextControlName(ctrl, controls):
    """return the name for this control by finding the closest
    text control above and to its left"""


    names = []

    ctrl_index = controls.index(ctrl)

    if ctrl_index != 0:
        prev_ctrl = controls[ctrl_index-1]

        if prev_ctrl.FriendlyClassName() == "Static" and \
            prev_ctrl.IsVisible() and prev_ctrl.WindowText() and \
            IsAboveOrToLeft(ctrl, prev_ctrl):

            names.append(
                prev_ctrl.WindowText() +
                    ctrl.FriendlyClassName())


    # get the visible text controls so that we can get
    # the closest text if the control has no text
    text_ctrls = [ctrl_ for ctrl_ in controls
        if ctrl_.IsVisible() and ctrl_.WindowText()]


    best_name = ''
    closest = distance_cuttoff
    # now for each of the visible text controls
    for text_ctrl in text_ctrls:

        # get aliases to the control rectangles
        text_r = text_ctrl.Rectangle()
        ctrl_r = ctrl.Rectangle()

        # skip controls where text win is to the right of ctrl
        if text_r.left >= ctrl_r.right:
            continue

        # skip controls where text win is below ctrl
        if text_r.top >= ctrl_r.bottom:
            continue

        # calculate the distance between the controls
        # at first I just calculated the distance from the top let
        # corner of one control to the top left corner of the other control
        # but this was not best, so as a text control should either be above
        # or to the left of the control I get the distance between
        # the top left of the non text control against the
        #    Top-Right of the text control (text control to the left)
        #    Bottom-Left of the text control (text control above)
        # then I get the min of these two

        # (x^2 + y^2)^.5
        distance = (
            (text_r.left - ctrl_r.left) ** 2 +  #  (x^2 + y^2)
            (text_r.bottom - ctrl_r.top) ** 2) \
            ** .5  # ^.5

        distance2 = (
            (text_r.right - ctrl_r.left) ** 2 +  #  (x^2 + y^2)
            (text_r.top - ctrl_r.top) ** 2) \
            ** .5  # ^.5

        distance = min(distance, distance2)

        # if this distance was closer then the last one
        if distance < closest:
            closest = distance
            best_name = text_ctrl.WindowText() + ctrl.FriendlyClassName()

    names.append(best_name)

    return names


#====================================================================
def get_control_names(control, allcontrols):
    "Returns a list of names for this control"
    names = []

    # if it has a reference control - then use that
    #if hasattr(control, 'ref') and control.ref:
    #    control = control.ref

    # Add the control based on it's friendly class name
    names.append(control.FriendlyClassName())

    # if it has some character text then add it base on that
    # and based on that with friendly class name appended
    cleaned = control.WindowText()
    if cleaned:
        names.append(cleaned)
        names.append(cleaned + control.FriendlyClassName())

    # it didn't have visible text
    else:
        # so find the text of the nearest text visible control
        non_text_names = GetNonTextControlName(control, allcontrols)
        # and if one was found - add it
        if non_text_names:
            names.extend(non_text_names)

    # return the names - and make sure there are no duplicates
    return sets.Set(names)





#====================================================================
class UniqueDict(dict):
    "A dictionary subclass that handles making it's keys unique"
    def __setitem__(self, text, item):
        "Set an item of the dictionary"

        # this text is already in the map
        # so we need to make it unique
        if text in self:
            # find next unique text after text1
            unique_text = text
            counter = 2
            while unique_text in self:
                unique_text = text + str(counter)
                counter += 1

            # now we also need to make sure the original item
            # is under text0 and text1 also!
            if text + '0' not in self:
                dict.__setitem__(self, text+'0', self[text])
                dict.__setitem__(self, text+'1', self[text])

            # now that we don't need original 'text' anymore
            # replace it with the uniq text
            text = unique_text

        # add our current item
        dict.__setitem__(self, text, item)


    def FindBestMatches(
        self,
        search_text,
        clean = False,
        ignore_case = False):

        """Return the best matches for search_text in the items

        :search_text: the text to look for
        :clean: whether to clean non text characters out of the strings
        :ignore_case: compare strings case insensitively
        """

        # now time to figure out the matching
        ratio_calc = difflib.SequenceMatcher()

        if ignore_case:
            search_text = search_text.lower()

        ratio_calc.set_seq1(search_text)

        ratios = {}
        best_ratio = 0
        best_texts = []

        for text_ in self:

            # make a copy of the text as we need the original later
            text = text_

            if clean:
                text = _clean_non_chars(text)

            if ignore_case:
                text = text.lower()

            # set up the SequenceMatcher with other text
            ratio_calc.set_seq2(text)

            # calculate ratio and store it
            ratios[text_] = ratio_calc.ratio()

            # if this is the best so far then update best stats
            if ratios[text_] > best_ratio:
                best_ratio = ratios[text_]
                best_texts = [text_]

            elif ratios[text_] == best_ratio:
                best_texts.append(text_)

        if clean:
            best_ratio *= .9

        if ignore_case:
            best_ratio *= .9

        return best_ratio, best_texts





#====================================================================
def find_best_control_matches(search_text, controls):
    """Returns the control that is the the best match to search_text

    This is slightly differnt from find_best_match in that it builds
    up the list of text items to search through using information
    from each control. So for example for there is an OK, Button
    then the following are all added to the search list:
    "OK", "Button", "OKButton"

    But if there is a ListView (which do not have visible 'text')
    then it will just add "ListView".
    """

    name_control_map = UniqueDict()


    # collect all the possible names for all controls
    # and build a list of them
    for ctrl in controls:
        ctrl_names = get_control_names(ctrl, controls)

        # for each of the names
        for name in ctrl_names:
            name_control_map[name] = ctrl


    best_ratio, best_texts = name_control_map.FindBestMatches(search_text)

    best_ratio_ci, best_texts_ci = \
        name_control_map.FindBestMatches(search_text, ignore_case = True)

    best_ratio_clean, best_texts_clean = \
        name_control_map.FindBestMatches(search_text, clean = True)

    best_ratio_clean_ci, best_texts_clean_ci = \
        name_control_map.FindBestMatches(
            search_text, clean = True, ignore_case = True)


    if best_ratio_ci > best_ratio:
        best_ratio = best_ratio_ci
        best_texts = best_texts_ci

    if best_ratio_clean > best_ratio:
        best_ratio = best_ratio_clean
        best_texts = best_texts_clean

    if best_ratio_clean_ci > best_ratio:
        best_ratio = best_ratio_clean_ci
        best_texts = best_texts_clean_ci

    if best_ratio < find_best_control_match_cutoff:
        raise MatchError(items = name_control_map.keys(), tofind = search_text)

    return [name_control_map[best_text] for best_text in best_texts]






#
#def GetControlMatchRatio(text, ctrl):
#    # get the texts for the control
#    ctrl_names = get_control_names(ctrl)
#
#    #get the best match for these
#    matcher = UniqueDict()
#    for name in ctrl_names:
#        matcher[name] = ctrl
#
#    best_ratio, unused = matcher.FindBestMatches(text)
#
#    return best_ratio
#
#
#
#def get_controls_ratios(search_text, controls):
#    name_control_map = UniqueDict()
#
#    # collect all the possible names for all controls
#    # and build a list of them
#    for ctrl in controls:
#        ctrl_names = get_control_names(ctrl)
#
#        # for each of the names
#        for name in ctrl_names:
#            name_control_map[name] = ctrl
#
#    match_ratios, best_ratio, best_text = \
#        _get_match_ratios(name_control_map.keys(), search_text)
#
#    return match_ratios, best_ratio, best_text,
