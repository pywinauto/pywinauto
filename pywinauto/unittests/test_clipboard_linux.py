"""Module containing tests for linux clipboard module"""

import sys
import os
import unittest
import subprocess
import time
if sys.platform != 'win32':
    sys.path.append(".")
    from pywinauto import mouse
    from pywinauto.linux.keyboard import SendKeys
    from pywinauto.linux import clipboard


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/SendKeysTester")
    return os.path.join(test_folder, r"send_keys_test_app")


if sys.platform != 'win32':
    class SendKeysTests(unittest.TestCase):
        """Unit tests for the linux clipboard module"""

        def setUp(self):
            """Start the application set some data and ensure the application is in the state we want it."""
            self.app = subprocess.Popen("exec " + _test_app(), shell=True)
            time.sleep(0.1)
            mouse.click(coords=(300, 300))
            time.sleep(0.1)

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        @staticmethod
        def receive_text():
            """Receive data from text field"""
            time.sleep(0.2)
            SendKeys('^a')
            time.sleep(0.2)
            SendKeys('^c')
            SendKeys('{RIGHT}')
            received = clipboard.get_data()
            return received

        def test_get_data(self):
            """Make sure that get text from clipboard works"""
            SendKeys('abc')
            received = self.receive_text()
            self.assertEquals('abc', received)

        def test_set_data(self):
            """Make sure that set text to clipboard works"""
            clipboard.set_data('abc1')
            received = clipboard.get_data()
            self.assertEquals('abc1', received)


if __name__ == "__main__":
        unittest.main()
