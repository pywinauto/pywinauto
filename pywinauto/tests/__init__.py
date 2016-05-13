# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
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

"""Package of tests that can be run on controls or lists of controls
"""
from __future__ import print_function

from .. import six


def run_tests(controls, tests_to_run = None, test_visible_only = True):
    "Run the tests"

    # allow either a string or list to be passed
    try:
        tests_to_run = tests_to_run.split()
    except AttributeError:
        pass

    # if no tests specified run them all
    if tests_to_run is None:
        tests_to_run = _registered.keys()

    # Filter out hidden controls if requested
    if test_visible_only:
        controls = [ctrl for ctrl in controls if ctrl.is_visible()]

    bugs = []
    # run each test
    for test_name in tests_to_run:
        #print test_name
        bugs.extend(_registered[test_name](controls))

    return bugs


def get_bug_as_string(bug):
    ctrls, info, bug_type, is_in_ref = bug
    
    header = ["BugType:", str(bug_type), str(is_in_ref)]

    for i in info:
        header.append(six.text_type(i))
        header.append(six.text_type(info[i]))
    
    lines = []
    lines.append(" ".join(header))
    
    for i, ctrl in enumerate(ctrls):
        lines.append(u'\t"%s" "%s" (%d %d %d %d) Vis: %d' % (
            ctrl.window_text(),
            ctrl.friendly_class_name(),
            ctrl.rectangle().left,
            ctrl.rectangle().top,
            ctrl.rectangle().right,
            ctrl.rectangle().bottom,
            ctrl.is_visible(),))
    
    return u"\n".join(lines)


def write_bugs(bugs, filename = "BugsOutput.txt"):
    with open(filename, "w") as f:
        for b in bugs:
            f.write(get_bug_as_string(b).encode('utf-8') + "\n")


def print_bugs(bugs):
    "Print the bugs"
    for (ctrls, info, bug_type, is_in_ref) in bugs:
        print("BugType:", bug_type, is_in_ref)

        for i in info:
            print(six.text_type(i).encode('utf-8'), six.text_type(info[i]).encode('utf-8'))
        print()


        for i, ctrl in enumerate(ctrls):
            print('\t"%s" "%s" (%d %d %d %d) Vis: %d' % (
                ctrl.window_text().encode('utf-8'),
                ctrl.friendly_class_name().encode('utf-8'),
                ctrl.rectangle().left,
                ctrl.rectangle().top,
                ctrl.rectangle().right,
                ctrl.rectangle().bottom,
                ctrl.is_visible(),))

            try:
                ctrl.DrawOutline()
            except (AttributeError, KeyError):
                #print(e)
                continue

        print()


# we need to register the modules
_registered = {}
def __init_tests():
    "Initialize each test by loading it and then register it"
    global _registered

    standard_test_names = (
            "AllControls",
            "AsianHotkey",
            "ComboBoxDroppedHeight",
            "CompareToRefFont",
            "LeadTrailSpaces",
            "MiscValues",
            "Missalignment",
            "MissingExtraString",
            "Overlapping",
            "RepeatedHotkey",
            "Translation",
            "Truncation",
        #   "menux",
    )

    for test_name in standard_test_names:

        test_module = __import__(test_name.lower(), globals(), locals(), level=1)

        # class name is the test name + "Test"
        test_class = getattr(test_module, test_name + "Test")

        _registered[test_name] = test_class

    # allow extension of the tests available through a separate file
    try:
        import extra_tests
        extra_tests.ModifyRegisteredTests(_registered)
    except ImportError:
        pass


if not _registered:
    __init_tests()

