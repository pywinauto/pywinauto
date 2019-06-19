import sys
import os
import unittest
import time
#import pprint
#import pdb

# sys.path.append(".")
if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    sys.path.append(parent_dir + '/macos')
    os.path.join
    from pywinauto.macos import macos_functions
    from pywinauto.macos.macos_functions import running_applications, get_app_instance_by_bundle,get_ws_instance
    from pywinauto.application import Application

if sys.platform == 'darwin':
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(parent_dir)
    os.path.join
    from pywinauto.base_application import AppStartError, ProcessNotFoundError, AppNotConnected, BaseApplication



def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/SendKeysTester")
    return os.path.join(test_folder, r"send_keys_test_app")





sys.path.append(".")

if sys.platform == 'darwin':
    class ApplicationTestCases(unittest.TestCase):

        """Unit tests for the application.Application class"""

        def setUp(self):

            pass


        def tearDown(self):

            pass

        
        def test__init__(self):
            """Verify that Application instance is initialized or not"""
            self.assertRaises(ValueError, Application, backend='unregistered')



        def test_not_connected(self):
            """Verify that it raises when the app is not connected"""
            self.assertRaises(AppNotConnected, Application().__getattribute__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().__getitem__, 'Hiya')
            self.assertRaises(AppNotConnected, Application().window_, title='Hiya')
            self.assertRaises(AppNotConnected, Application().top_window, )
            
        

        # def test_start_by_cmd_line(self):
        #     """test start() works correctly after being called by name"""
        #     app=Application()
        #     self.assertEqual(app.ns_app, None)
        #     app.start('send_keys_test_app')
        #     self.assertNotEqual(app.ns_app, None)
        #     app.kill()


        def test_kill_soft(self):
            
            app= Application()
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=True))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)

        def test_already_killed_hard(self):
            app= Application()
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=False))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)
            self.assertFalse(app.kill(soft=False)) # already killed, returned True anyway

        def test_already_killed_soft(self):
            app= Application()
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            process = app.process_id
            self.assertTrue(app.kill(soft=False))
            self.assertRaises(ProcessNotFoundError, Application().connect, process=process)
            self.assertFalse(app.kill(soft=True)) # already killed, returned True anyway

        

            

        def test_is_process_running(self):
            """test is_process_running of the application"""
            app= Application()
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            self.assertTrue(app.is_process_running())
            app.kill()
            app.wait_for_process_exit()
            self.assertFalse(app.is_process_running())
            

        def test_start_by_bundle(self):
            """test start() works correctly after being called by bundle"""
            app = Application()
            self.assertEqual(app.ns_app, None)
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            self.assertNotEqual(app.ns_app, None)
            app.kill()
            
        

        def test_process_id(self):
            """Test that connect_() works with a path"""
            app = Application()
            self.assertEqual(app.process_id, None)
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            self.assertNotEqual(app.process_id, None)
            app.kill()


        # def test_start_problem(self):
        #     """Verify start_ raises on unknown command"""
        #     app = Application()
        #     self.assertRaises(AppStartError,app.start, 'Hiya')



        def test_cpu_usage(self):
            """Verify that cpu_usage() works correctly"""
            app = Application()
            app.start(bundleID='com.yourcompany.send-keys-test-app')
            self.assertEqual(0.0 <= app.cpu_usage() <= 100.0, True)
            app.kill()

           

        def test_connect_by_process(self):
            """Test that connect_() works with a process"""
            app1 = Application()
            app1.start(bundleID='com.yourcompany.send-keys-test-app')
           
            app_conn = Application()
            app_conn.connect(process=app1.process_id)
         
            self.assertEqual(app1.process_id, app_conn.process_id)
            app1.kill()
         
        def test_connect_by_bundle(self):
            """Test that connect_() works with a bundle"""
            app1 = Application()
            app1.start(bundleID='com.yourcompany.send-keys-test-app')
          
            app_conn = Application()
            app_conn.connect(bundle='com.yourcompany.send-keys-test-app')
           
            self.assertEqual(app1.process_id, app_conn.process_id)
            app1.kill()
         
        def test_connect_by_name(self):
            """Test that connect_() works with a bundle"""
            app1 = Application()
            app1.start(bundleID='com.yourcompany.send-keys-test-app')
          
            app_conn = Application()
            app_conn.connect(name='send_keys_test_app')
           
            self.assertEqual(app1.process_id, app_conn.process_id)
            app1.kill()    


if __name__ == "__main__":
    unittest.main()


