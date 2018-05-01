# TODO crossplatform join this tests with test_application.py
import sys
import os
import unittest
import time
#import pprint
#import pdb
import warnings
from threading import Thread

from pywinauto.application_linux import Application, AppStartError, AppNotConnected

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)

sys.path.append(".")

class ApplicationTestCases(unittest.TestCase):

    """Unit tests for the application.Application class"""

    def setUp(self):
        """Set some data and ensure the application is in the state we want"""
        pass

    def tearDown(self):
        """Close the application after tests"""
        pass

    def test__init__(self):
        """Verify that Application instance is initialized or not"""
        self.assertRaises(ValueError, Application, backend='unregistered')

    def test_not_connected(self):
        """Verify that it raises when the app is not connected"""
        self.assertRaises(AppNotConnected, Application().__getattribute__, 'Hiya')
        self.assertRaises(AppNotConnected, Application().__getitem__, 'Hiya')
        self.assertRaises(AppNotConnected, Application().window_, title='Hiya')
        self.assertRaises(AppNotConnected, Application().top_window_,)

    def test_start_problem(self):
        """Verify start_ raises on unknown command"""
        self.assertRaises(AppStartError, Application().start, 'Hiya')

    def test_start(self):
        """test start() works correctly"""
        app = Application()
        self.assertEqual(app.process, None)
        app.start(_test_app())
        self.assertNotEqual(app.process, None)

        self.assertEqual(app.UntitledNotepad.process_id(), app.process)

        notepadpath = os.path.join(os.environ['systemroot'], self.notepad_subpath)
        # self.assertEqual(str(process_module(app.process)).lower(), str(notepadpath).lower())

        app.UntitledNotepad.MenuSelect("File->Exit")
