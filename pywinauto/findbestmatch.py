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

"""Module to find the closest match of a string in a list"""
from __future__ import unicode_literals

import re
import difflib
import six
#import ctypes
#import ldistance
#levenshtein_distance = ctypes.cdll.levenshtein.levenshtein_distance
#levenshtein_distance = ldistance.distance

find_best_control_match_cutoff = .6

#====================================================================
class MatchError(IndexError):

    """A suitable match could not be found"""

    def __init__(self, items = None, tofind = ''):
        """Init the parent with the message"""
        self.tofind = tofind
        self.items = items
        if self.items is None:
            self.items = []

        IndexError.__init__(self,
            "Could not find '{0}' in '{1}'".format(tofind, self.items))


_cache = {}

# given a list of texts return the match score for each
# and the best score and text with best score
#====================================================================
def _get_match_ratios(texts, match_against):
    """Get the match ratio of how each item in texts compared to match_against"""
    # now time to figure out the matching
    ratio_calc = difflib.SequenceMatcher()
    ratio_calc.set_seq1(match_against)

    ratios = {}
    best_ratio = 0
    best_text = ''

    for text in texts:

        if 0:
            pass

        if (text, match_against) in _cache:
            ratios[text] = _cache[(text, match_against)]

        elif(match_against, text) in _cache:
            ratios[text] = _cache[(match_against, text)]

        else:
            # set up the SequenceMatcher with other text
            ratio_calc.set_seq2(text)

            # try using the levenshtein distance instead
            #lev_dist = levenshtein_distance(six.text_type(match_against), six.text_type(text))
            #ratio = 1 - lev_dist / 10.0
            #ratios[text] = ratio

            # calculate ratio and store it
            ratios[text] = ratio_calc.ratio()

            _cache[(match_against, text)] = ratios[text]

        # if this is the best so far then update best stats
        if ratios[text] > best_ratio:
            best_ratio = ratios[text]
            best_text = text

    return ratios, best_ratio, best_text


#====================================================================
def find_best_match(search_text, item_texts, items, limit_ratio = .5):
    """Return the item that best matches the search_text

    * **search_text** The text to search for
    * **item_texts** The list of texts to search through
    * **items** The list of items corresponding (1 to 1)
      to the list of texts to search through.
    * **limit_ratio** How well the text has to match the best match.
      If the best match matches lower then this then it is not
      considered a match and a MatchError is raised, (default = .5)
    """
    search_text = _cut_at_eol(_cut_at_tab(search_text))

    text_item_map = UniqueDict()
    # Clean each item, make it unique and map to
    # to the item index
    for text, item in zip(item_texts, items):
        text_item_map[_cut_at_eol(_cut_at_tab(text))] = item

    ratios, best_ratio, best_text = \
        _get_match_ratios(text_item_map.keys(), search_text)

    if best_ratio < limit_ratio:
        raise MatchError(items = text_item_map.keys(), tofind = search_text)

    return text_item_map[best_text]


#====================================================================
_after_tab = re.compile(r"\t.*", re.UNICODE)
_after_eol = re.compile(r"\n.*", re.UNICODE)
_non_word_chars = re.compile(r"\W", re.UNICODE)

def _cut_at_tab(text):
    """Clean out non characters from the string and return it"""
    # remove anything after the first tab
    return  _after_tab.sub("", text)

def _cut_at_eol(text):
    """Clean out non characters from the string and return it"""
    # remove anything after the first EOL
    return  _after_eol.sub("", text)

def _clean_non_chars(text):
    """Remove non word characters"""
    # should this also remove everything after the first tab?

    # remove non alphanumeric characters
    return _non_word_chars.sub("", text)


def is_above_or_to_left(ref_control, other_ctrl):
    """Return true if the other_ctrl is above or to the left of ref_control"""
    text_r = other_ctrl.rectangle()
    ctrl_r = ref_control.rectangle()

    # skip controls where text win is to the right of ctrl
    if text_r.left >= ctrl_r.right:
        return False

    # skip controls where text win is below ctrl
    if text_r.top >= ctrl_r.bottom:
        return False

    # text control top left corner is below control
    # top left corner - so not to the above or left :)
    if text_r.top >= ctrl_r.top and text_r.left >= ctrl_r.left:
        return False

    return True


#====================================================================
distance_cuttoff = 999
def get_non_text_control_name(ctrl, controls, text_ctrls):
    """
    return the name for this control by finding the closest
    text control above and to its left
    """
    names = []

    # simply look for an instance of the control in the list,
    # we don't use list.index() method as it invokes __eq__
    ctrl_index = 0
    for i, c in enumerate(controls):
        if c is ctrl:
            ctrl_index = i
            break
    ctrl_friendly_class_name = ctrl.friendly_class_name()

    if ctrl_index != 0:
        prev_ctrl = controls[ctrl_index-1]
        prev_ctrl_text = prev_ctrl.window_text()

        if prev_ctrl.friendly_class_name() == "Static" and \
            prev_ctrl.is_visible() and prev_ctrl_text and \
            is_above_or_to_left(ctrl, prev_ctrl):

            names.append(
                prev_ctrl_text +
                ctrl_friendly_class_name)

    best_name = ''
    closest = distance_cuttoff
    # now for each of the visible text controls
    for text_ctrl in text_ctrls:

        # get aliases to the control rectangles
        text_r = text_ctrl.rectangle()
        ctrl_r = ctrl.rectangle()

        # skip controls where text win is to the right of ctrl
        if text_r.left >= ctrl_r.right:
            continue

        # skip controls where text win is below ctrl
        if text_r.top >= ctrl_r.bottom:
            continue

        # calculate the distance between the controls
        # at first I just calculated the distance from the top left
        # corner of one control to the top left corner of the other control
        # but this was not best, so as a text control should either be above
        # or to the left of the control I get the distance between
        # the top left of the non text control against the
        #    Top-Right of the text control (text control to the left)
        #    Bottom-Left of the text control (text control above)
        # then I get the min of these two

        # We do not actually need to calculate the difference here as we
        # only need a comparative number. As long as we find the closest one
        # the actual distance is not all that important to us.
        # this reduced the unit tests run on my by about 1 second
        # (from 61 ->60 s)

        # (x^2 + y^2)^.5
        #distance = (
        #    (text_r.left - ctrl_r.left) ** 2 +  #  (x^2 + y^2)
        #    (text_r.bottom - ctrl_r.top) ** 2) \
        #    ** .5  # ^.5

        #distance2 = (
        #    (text_r.right - ctrl_r.left) ** 2 +  #  (x^2 + y^2)
        #    (text_r.top - ctrl_r.top) ** 2) \
        #    ** .5  # ^.5

        distance = abs(text_r.left - ctrl_r.left) + abs(text_r.bottom - ctrl_r.top)
        distance2 = abs(text_r.right - ctrl_r.left) + abs(text_r.top - ctrl_r.top)

        distance = min(distance, distance2)

        # UpDown control should use Static text only because edit box text is often useless
        if ctrl_friendly_class_name == "UpDown" and \
                text_ctrl.friendly_class_name() == "Static" and distance < closest:
            # TODO: use search in all text controls for all non-text ones
            # (like Dijkstra algorithm vs Floyd one)
            closest = distance
            ctrl_text = text_ctrl.window_text()
            if ctrl_text is None:
                # the control probably doesn't exist so skip it
                continue
            best_name = ctrl_text + ctrl_friendly_class_name

        # if this distance was closer than the last one
        elif distance < closest:
            closest = distance
            #if text_ctrl.window_text() == '':
            #    best_name = ctrl_friendly_class_name + ' '.join(text_ctrl.texts()[1:2])
            #else:
            ctrl_text = text_ctrl.window_text()
            if ctrl_text is None:
                # the control probably doesn't exist so skip it
                continue
            best_name = ctrl_text + ctrl_friendly_class_name

    names.append(best_name)

    return names


#====================================================================
def get_control_names(control, allcontrols, textcontrols):
    """Returns a list of names for this control"""
    names = []

    # if it has a reference control - then use that
    #if hasattr(control, 'ref') and control.ref:
    #    control = control.ref

    # Add the control based on it's friendly class name
    friendly_class_name = control.friendly_class_name()
    names.append(friendly_class_name)

    # if it has some character text then add it base on that
    # and based on that with friendly class name appended
    cleaned = control.window_text()
    # Todo - I don't like the hardcoded classnames here!
    if cleaned and control.has_title:
        names.append(cleaned)
        names.append(cleaned + friendly_class_name)
    elif control.has_title and friendly_class_name != 'TreeView':
        try:
            for text in control.texts()[1:]:
                names.append(friendly_class_name + text)
        except Exception:
            #import traceback
            #from .actionlogger import ActionLogger
            pass #ActionLogger().log('Warning! Cannot get control.texts()') #\nTraceback:\n' + traceback.format_exc())

        # so find the text of the nearest text visible control
        non_text_names = get_non_text_control_name(control, allcontrols, textcontrols)

        # and if one was found - add it
        if non_text_names:
            names.extend(non_text_names)
    # it didn't have visible text
    else:
        # so find the text of the nearest text visible control
        non_text_names = get_non_text_control_name(control, allcontrols, textcontrols)

        # and if one was found - add it
        if non_text_names:
            names.extend(non_text_names)

    # return the names - and make sure there are no duplicates
    return set(names)


#====================================================================
class UniqueDict(dict):

    """A dictionary subclass that handles making its keys unique"""

    def __setitem__(self, text, item):
        """Set an item of the dictionary"""
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

    def find_best_matches(
        self,
        search_text,
        clean = False,
        ignore_case = False):
        """Return the best matches for search_text in the items

        * **search_text** the text to look for
        * **clean** whether to clean non text characters out of the strings
        * **ignore_case** compare strings case insensitively
        """
        # now time to figure out the matching
        ratio_calc = difflib.SequenceMatcher()

        if ignore_case:
            search_text = search_text.lower()

        ratio_calc.set_seq1(search_text)

        ratios = {}
        best_ratio = 0
        best_texts = []

        ratio_offset = 1
        if clean:
            ratio_offset *= .9

        if ignore_case:
            ratio_offset *= .9

        for text_ in self:

            # make a copy of the text as we need the original later
            text = text_

            if clean:
                text = _clean_non_chars(text)

            if ignore_case:
                text = text.lower()

            # check if this item is in the cache - if yes, then retrieve it
            if (text, search_text) in _cache:
                ratios[text_] = _cache[(text, search_text)]

            elif(search_text, text) in _cache:
                ratios[text_] = _cache[(search_text, text)]

            # not in the cache - calculate it and add it to the cache
            else:
                # set up the SequenceMatcher with other text
                ratio_calc.set_seq2(text)

                # if a very quick check reveals that this is not going
                # to match then
                ratio = ratio_calc.real_quick_ratio() * ratio_offset

                if ratio  >=  find_best_control_match_cutoff:
                    ratio = ratio_calc.quick_ratio() * ratio_offset

                    if ratio >= find_best_control_match_cutoff:
                        ratio = ratio_calc.ratio() * ratio_offset

                # save the match we got and store it in the cache
                ratios[text_] = ratio
                _cache[(text, search_text)] = ratio

            # try using the levenshtein distance instead
            #lev_dist = levenshtein_distance(six.text_type(search_text), six.text_type(text))
            #ratio = 1 - lev_dist / 10.0
            #ratios[text_] = ratio
            #print "%5s" %("%0.2f"% ratio), search_text, `text`

            # if this is the best so far then update best stats
            if ratios[text_] > best_ratio and \
                ratios[text_] >= find_best_control_match_cutoff:

                best_ratio = ratios[text_]
                best_texts = [text_]

            elif ratios[text_] == best_ratio:
                best_texts.append(text_)

        #best_ratio *= ratio_offset

        return best_ratio, best_texts


#====================================================================
def build_unique_dict(controls):
    """Build the disambiguated list of controls

    Separated out to a different function so that we can get
    the control identifiers for printing.
    """
    name_control_map = UniqueDict()

    # get the visible text controls so that we can get
    # the closest text if the control has no text
    text_ctrls = [ctrl_ for ctrl_ in controls
                  if ctrl_.can_be_label and ctrl_.is_visible() and ctrl_.window_text()]

    # collect all the possible names for all controls
    # and build a list of them
    for ctrl in controls:
        ctrl_names = get_control_names(ctrl, controls, text_ctrls)

        # for each of the names
        for name in ctrl_names:
            name_control_map[name] = ctrl
    return name_control_map


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
    name_control_map = build_unique_dict(controls)

#    # collect all the possible names for all controls
#    # and build a list of them
#    for ctrl in controls:
#        ctrl_names = get_control_names(ctrl, controls)
#
#        # for each of the names
#        for name in ctrl_names:
#            name_control_map[name] = ctrl

    search_text = six.text_type(search_text)

    best_ratio, best_texts = name_control_map.find_best_matches(search_text)

    best_ratio_ci, best_texts_ci = \
        name_control_map.find_best_matches(search_text, ignore_case = True)

    best_ratio_clean, best_texts_clean = \
        name_control_map.find_best_matches(search_text, clean = True)

    best_ratio_clean_ci, best_texts_clean_ci = \
        name_control_map.find_best_matches(
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
#    best_ratio, unused = matcher.find_best_matches(text)
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
