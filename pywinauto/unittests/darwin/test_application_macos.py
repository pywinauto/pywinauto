import sys
import os
import unittest
import subprocess
from subprocess import Popen, PIPE

if sys.platform == 'darwin':
    sys.path.append(".")
    from pywinauto.application import Application
    from pywinauto.base_application import ProcessNotFoundError, AppNotConnected

def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/SendKeysTester")
    return os.path.join(test_folder, r"send_keys_test_app")

sys.path.append(".")

if sys.platform == 'darwin':
    class ApplicationEspecialTestCases(unittest.TestCase):
        """
        Unit tests for the application.Application class
        There are test cases which has unique start/end logic
        """ 
        def test__init__(self):
            """Verify that Application instance is initialized or not"""
            self.assertRaises(ValueError, Application, backend='unregistered')

        def test_not_connected(self):
            """Verify that it raises when the app is not connected"""
            self.assertRaises(AppNotConnected, Application().__getattribute__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().__getitem__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().window_, title='Hiya')
            self.assertRaises(AppNotConnected, Application().top_window, )

        def test_cpu_app_not_started(self):
            """Verify that it raises when the app is not connected"""
            app = Application()
            self.assertRaises(AppNotConnected, app.cpu_usage, interval = 1)

        def test_not_connected(self):
            """Verify that it raises when the app is not connected"""
            self.assertRaises(ValueError, Application().start, name = 'send_keys_test_app', bundle_id = 'pywinauto.testapps.send-keys-test-app')

        def test_start_by_cmd_line(self):
            """test start() works correctly after being called by name"""
            app = Application()
            self.assertEqual(app.ns_app, None)
            app.start('send_keys_test_app')
            self.assertNotEqual(app.ns_app, None)
            app.kill()

        def test_kill_soft(self):
            app = Application()
            app.start(bundle_id='pywinauto.testapps.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=True))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)

        def test_already_killed_hard(self):
            app = Application()
            app.start(bundle_id='pywinauto.testapps.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=False))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)
            self.assertFalse(app.kill(soft=False))

        def test_already_killed_soft(self):
            app = Application()
            app.start(bundle_id='pywinauto.testapps.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=False))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)
            self.assertFalse(app.kill(soft=True))

        def test_is_process_running(self):
            """test is_process_running of the application"""
            app = Application()
            app.start(bundle_id='pywinauto.testapps.send-keys-test-app')
            self.assertTrue(app.is_process_running())
            app.kill()
            app.wait_for_process_exit()
            self.assertFalse(app.is_process_running())

        def test_not_connected_app(self):
            app = Application()
            self.assertEqual(app.ns_app, None)

        def test_not_running_app(self):
            app = Application()
            self.assertFalse(app.is_process_running())

    class ApplicationTestCases(unittest.TestCase):

        """Unit tests for the application.Application class"""

        def setUp(self):
            self.app = Application()
            self.app.start(bundle_id = 'pywinauto.testapps.send-keys-test-app',new_instance=False)

        def tearDown(self):
            self.app.kill()

        def test_cpu_error(self):
            """Verify that it raises when the app is not connected"""
            Popen(["kill", "-9", str(self.app.process_id)], stdout=PIPE).communicate()[0]
            self.assertRaises(ProcessNotFoundError, self.app.cpu_usage, interval = 1)

        def test_start_with_same_instance(self):
            """test start() works correctly after being called by name"""
            first = self.app.process_id
            self.app.start(bundle_id = 'pywinauto.testapps.send-keys-test-app', new_instance=False)
            second = self.app.process_id
            self.assertEqual(first, second)

        def test_start_by_bundle(self):
            """test start() works correctly after being called by bundle"""
            self.assertNotEqual(self.app.ns_app, None)

        def test_process_id(self):
            """Test process_id method of the application"""
            self.assertNotEqual(self.app.process_id, None)

        def test_cpu_usage(self):
            """Verify that cpu_usage() works correctly"""
            self.assertEqual(0.0 <= self.app.cpu_usage() <= 100.0, True)

        def test_wait_for_process_running(self):
            """test is_process_running of the application"""
            self.app.wait_for_process_running()
            self.assertTrue(self.app.is_process_running())

        def test_connect_by_process(self):
            """Test that connect_() works with a process"""
            app_conn = Application()
            app_conn.connect(process = self.app.process_id)
            self.assertEqual(self.app.process_id, app_conn.process_id)

        def test_connect_by_bundle(self):
            """Test that connect_() works with a bundle"""
            app_conn = Application()
            app_conn.connect(bundle='pywinauto.testapps.send-keys-test-app')
            self.assertEqual(self.app.process_id, app_conn.process_id)

        def test_connect_by_name(self):
            app_conn = Application()
            app_conn.connect(name='send_keys_test_app')
            self.assertEqual(self.app.process_id, app_conn.process_id)

if __name__ == "__main__":
    unittest.main()
