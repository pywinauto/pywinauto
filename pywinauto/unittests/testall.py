import unittest

import os.path
import os
import sys
sys.path.append(".")

#from pywinauto.timings import Timings
#Timings.Fast()

excludes = ['test_sendkeys']

def run_tests():
    testfolder = os.path.abspath(os.path.split(__file__)[0])

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
            #print imported_mod.__dict__
            globals().update(imported_mod.__dict__)


    #runner = unittest.TextTestRunner(verbosity = 2)
    unittest.main()#testRunner = runner)

if __name__ == '__main__':
    run_tests()