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

from __future__ import print_function
import os
import sys
import unittest

import coverage

testfolder = os.path.abspath(os.path.dirname(__file__))
package_root = os.path.abspath(os.path.join(testfolder, r"..\.."))
sys.path.append(package_root)

# needs to be called before importing the modules
cov = coverage.coverage(branch = True, omit = os.path.join(package_root, 'pywinauto', '*tests', '*.py'))
cov.start()

import pywinauto

pywinauto.actionlogger.enable()

# increase timings for AppVeyor
pywinauto.timings.Timings.app_start_timeout = 20
pywinauto.timings.Timings.window_find_timeout = 50

modules_to_test = [pywinauto]


def run_tests():
    excludes = ['test_sendkeys']

    suite = unittest.TestSuite()

    sys.path.append(testfolder)

    for root, dirs, files in os.walk(testfolder):
        test_modules = [
            file.replace('.py', '') for file in files if
                file.startswith('test_') and
                file.endswith('.py')]

        test_modules = [mod for mod in test_modules if mod.lower() not in excludes]
        for mod in test_modules:

            #globals().update(__import__(mod, globals(), locals()).__dict__)
            # import it
            imported_mod = __import__(mod, globals(), locals())

            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(imported_mod))

    #unittest.main()#testRunner = runner)

    #runner = unittest.TextTestRunner(verbosity = 2)
    unittest.TextTestRunner(verbosity=1).run(suite)
    cov.stop()
    #print(cov.analysis())
    print(cov.report())
    cov.html_report(
        directory = os.path.join(package_root, "Coverage_report"),
        omit = [os.path.join(package_root, 'pywinauto', '*tests', '*.py'),
                os.path.join(package_root, 'pywinauto', 'six.py'), ]
        )


if __name__ == '__main__':
    run_tests()