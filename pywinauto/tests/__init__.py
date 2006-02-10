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

"Package of tests that can be run on controls or lists of controls"

__revision__ = "$Revision$"

import os.path
import sys

_test_names = (
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
    #	"menux",
)



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
        controls = [ctrl for ctrl in controls if ctrl.IsVisible()]

    bugs = []
    # run each test
    for test_name in tests_to_run:
        #print test_name
        bugs.extend(_registered[test_name](controls))

    return bugs


def print_bugs(bugs):
    "Print the bugs"
    for (ctrls, info, bug_type, is_in_ref) in  bugs:
        print "BugType:", bug_type, is_in_ref,

        for i in info:
            print i, info[i],
        print


        for i, ctrl in enumerate(ctrls):
            print '\t"%s" "%s" (%d %d %d %d) Vis: %d'% (
                ctrl.Text(),
                ctrl.FriendlyClassName(),
                ctrl.Rectangle().left,
                ctrl.Rectangle().top,
                ctrl.Rectangle().right,
                ctrl.Rectangle().bottom,
                ctrl.IsVisible(),)


            try:
                ctrl.DrawOutline()
            except (AttributeError, KeyError):
                #print e
                pass

        print


# we need to register the modules
_registered = {}
def __init_tests():
    "Initialize each test by loading it and then register it"
    global _registered

    for test_name in _test_names:

        test_module = __import__(test_name.lower())

        # class name is the test name + "Test"
        test_class = getattr(test_module, test_name + "Test")

        _registered[test_name] = test_class


_package_path = os.path.split(__file__)[0]
sys.path.append(_package_path)
del _package_path

if not _registered:
    __init_tests()

sys.path = sys.path[:-1]

def _unittests():
    "Some unit tests"
    pass

if __name__ == "__main__":
    _unittests()

