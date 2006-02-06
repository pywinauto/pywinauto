import unittest

import os.path
import os
import sys

testfolder = os.path.split(__file__)[0]

sys.path.append(testfolder)


for root, dirs, files in os.walk(testfolder):
    test_modules = [
        file.replace('.py', '') for file in files if
            file.startswith('test_') and
            file.endswith('.py')]

    for mod in test_modules:
        globals().update(__import__(mod).__dict__)


unittest.main()