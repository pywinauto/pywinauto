
import time
import datetime
import ctypes
import locale
import re
import sys
import os
import unittest
import copy
import array
sys.path.append(".")
from pywinauto import win32structures
from pywinauto import win32defines
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python
from pywinauto.sysinfo import is_x64_OS

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
    
class CalendarWrapperTests(unittest.TestCase):

    def setUp(self):
        
        from pywinauto.application import Application
        app = Application()
        app.start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.app = app
        self.dlg = app.CommonControlsSample
        self.dlg.Wait('ready', 20)
        tab = app.CommonControlsSample.TabControl.WrapperObject()
        tab.Select(4)
          
        self.calendar = self.app.Common_Controls_Sample.CalendarWrapper
        
    def tearDown(self):
        self.dlg.SendMessage(win32defines.WM_CLOSE)
        
    def test_set_max_sel_count(self):
        count = self.calendar.set_max_sel_count(4)
        self.assertNotEqual(count,0)
        
    def test_get_max_sel_count(self):
        self.calendar.set_max_sel_count(7)
        count = self.calendar.get_max_sel_count();
        self.assertEqual(count,7)
        
if __name__ == "__main__":
    unittest.main()
    
