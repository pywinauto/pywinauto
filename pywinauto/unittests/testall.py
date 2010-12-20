import os
import sys
import unittest

import coverage

# needs to be called before importing the modules
cov = coverage.coverage(branch = True)
cov.start()

testfolder = os.path.abspath(os.path.dirname(__file__))
package_root = os.path.abspath(os.path.join(testfolder, r"..\.."))
sys.path.append(package_root)

import pywinauto

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
    #print cov.analysis()
    print cov.report()
    cov.html_report(
        directory = os.path.join(package_root, "Coverage_report"))


if __name__ == '__main__':
    run_tests()