# TODO crossplatform join these tests with test_application.py
import sys
import os
import unittest
import subprocess
import time

sys.path.append(".")
from pywinauto.application import WindowSpecification  # noqa: E402
if sys.platform.startswith('linux'):
    from pywinauto.controls import atspiwrapper  # register atspi backend
    from pywinauto.linux.application import Application  # noqa: E402
    from pywinauto.linux.application import AppStartError  # noqa: E402
    from pywinauto.linux.application import AppNotConnected  # noqa: E402
    from pywinauto.linux.application import ProcessNotFoundError  # noqa: E402

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

if sys.platform.startswith('linux'):
    class ApplicationTestCases(unittest.TestCase):

        """Unit tests for the application.Application class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            self.subprocess_app = None
            self.app = Application()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()
            if self.subprocess_app:
                self.subprocess_app.communicate()

        def test__init__(self):
            """Verify that Application instance is initialized or not"""
            self.assertRaises(ValueError, Application, backend='unregistered')

        def test_not_connected(self):
            """Verify that it raises when the app is not connected"""
            self.assertRaises(AppNotConnected, Application().__getattribute__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().__getitem__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().window_, name='Hiya')
            self.assertRaises(AppNotConnected, Application().top_window, )

        def test_start_problem(self):
            """Verify start_ raises on unknown command"""
            self.assertRaises(AppStartError, Application().start, 'Hiya')

        def test_start(self):
            """test start() works correctly"""
            self.assertEqual(self.app.process, None)
            self.app.start(_test_app())
            self.assertNotEqual(self.app.process, None)

        def test_connect_by_pid(self):
            """Create an application via subprocess then connect it to Application"""
            self.subprocess_app = subprocess.Popen(_test_app().split(), stdout=subprocess.PIPE, shell=False)
            time.sleep(1)
            self.app.connect(pid=self.subprocess_app.pid)
            self.assertEqual(self.app.process, self.subprocess_app.pid)

        def test_connect_by_path(self):
            """Create an application via subprocess then connect it to Application by application name"""
            self.subprocess_app = subprocess.Popen(_test_app().split(), stdout=subprocess.PIPE, shell=False)
            time.sleep(1)
            self.app.connect(path=_test_app())
            self.assertEqual(self.app.process, self.subprocess_app.pid)

        def test_cpu_usage(self):
            self.app.start(_test_app())
            self.assertGreater(self.app.cpu_usage(0.1), 0)
            self.app.wait_cpu_usage_lower(threshold=0.1, timeout=4.0, usage_interval=0.3)
            # default timings
            self.assertEqual(self.app.cpu_usage(), 0)

            # non-existing process
            self.app.kill()
            self.assertRaises(ProcessNotFoundError, self.app.cpu_usage, 7.8)

            # not connected or not started app
            self.assertRaises(AppNotConnected, Application().cpu_usage, 12.3)

        def test_is_process_running(self):
            self.app.start(_test_app())
            time.sleep(1)
            self.assertTrue(self.app.is_process_running())
            self.app.kill()
            self.assertFalse(self.app.is_process_running())

        def test_kill_killed_app(self):
            self.app.start(_test_app())
            time.sleep(1)
            self.app.kill()
            self.assertTrue(self.app.kill())

        def test_kill_connected_app(self):
            self.subprocess_app = subprocess.Popen(_test_app().split(), stdout=subprocess.PIPE, shell=False)
            time.sleep(1)
            self.app.connect(pid=self.subprocess_app.pid)
            self.app.kill()

            # Unlock the subprocess explicity, otherwise
            # it's presented in /proc as a zombie waiting for
            # the parent process to pickup the return code
            self.subprocess_app.communicate()
            self.subprocess_app = None

            self.assertFalse(self.app.is_process_running())


    class WindowSpecificationTestCases(unittest.TestCase):

        """Unit tests for the application.WindowSpecification class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            self.app = Application()

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def test_app_binding(self):
            self.app.start(_test_app())
            self.assertEqual(self.app.NonExistingDialog.app, self.app)
            self.assertEqual(self.app.Application.Panel.exists(), True)
            self.assertEqual(self.app.Application.Panel.app, self.app)
            self.assertIsInstance(self.app.Application.find(), atspiwrapper.AtspiWrapper)

            wspec = WindowSpecification(dict(name=u"blah", app=self.app))
            self.assertEqual(wspec.app, self.app)

        def test_app_binding_after_app_restart(self):
            self.app.start(_test_app())
            old_pid = self.app.process
            wspec = self.app.Application.Panel
            self.app.kill()
            self.assertEqual(wspec.app, self.app)
            self.app.start(_test_app())
            new_pid = self.app.process
            self.assertNotEqual(old_pid, new_pid)
            self.assertEqual(wspec.app, self.app)


if __name__ == "__main__":
    unittest.main()
