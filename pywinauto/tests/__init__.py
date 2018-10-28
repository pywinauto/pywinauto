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

"""Package of tests that can be run on controls or lists of controls"""
from __future__ import print_function

import six


def run_tests(controls, tests_to_run = None, test_visible_only = True):
    """Run the tests"""
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
    """Print the bugs"""
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
    """Initialize each test by loading it and then register it"""
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

