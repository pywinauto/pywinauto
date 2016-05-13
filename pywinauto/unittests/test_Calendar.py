<<<<<<< HEAD

=======
"""Tests for CalendarWrapper"""
>>>>>>> refs/remotes/pywinauto/UIA
import time
import datetime
import ctypes
import locale
import re
import sys
import os
import unittest
<<<<<<< HEAD
import copy
import array
=======
>>>>>>> refs/remotes/pywinauto/UIA
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
<<<<<<< HEAD
    
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
        self.app['Common Controls Sample']['MCS_MULTISELECT'].WrapperObject().Click()
        
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
    
=======

class CalendarWrapperTests(unittest.TestCase):

    """Unit tests for the CalendarWrapperTests class"""
    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.calendar = self.app.Common_Controls_Sample.CalendarWrapper

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.type_keys("%{F4}")

    def test_can_get_current_date_from_calendar(self):
        date = self.calendar.get_current_date()
        self.assert_system_time_is_equal_to_current_date_time(date,datetime.date.today())

    def test_should_throw_runtime_error_when_try_to_get_current_date_from_calendar_if_calendar_state_is_multiselect(self):
        self.set_calendar_state_into_multiselect()
        self.assertRaises(RuntimeError, self.calendar.get_current_date)

    def test_can_set_current_date_in_calendar(self):
        self.calendar.set_current_date(2016, 4, 3, 13)
        self.assert_system_time_is_equal_to_current_date_time(self.calendar.get_current_date(), datetime.date(2016, 4, 13)) 

    def test_should_throw_runtime_error_when_try_to_set_invalid_date(self):
        self.assertRaises(RuntimeError, self.calendar.set_current_date, -2016, -4, -3, -13)

    def test_can_get_calendar_border(self):
        width = self.calendar.get_border()
        self.assertEqual(width, 4)

    def test_can_set_calendar_border(self):
        self.calendar.set_border(6)
        self.assertEqual(self.calendar.get_border(), 6)

    def test_can_get_calendars_count(self):
        count = self.calendar.count()
        self.assertEqual(count, 1)

    def test_can_get_calendars_view(self):
        view = self.calendar.get_view()
        self.assertEqual(view, 0)

    def test_should_throw_runtime_error_when_try_to_set_invalid_view(self):
        self.assertRaises(RuntimeError, self.calendar.set_view, -1)

    def test_can_set_calendars_view_into_month(self):
        self.calendar.set_view(win32defines.MCMV_MONTH)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_MONTH)

    def test_can_set_calendars_view_into_years(self):
        self.calendar.set_view(win32defines.MCMV_YEAR)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_YEAR)

    def test_can_set_calendars_view_into_decade(self):
        self.calendar.set_view(win32defines.MCMV_DECADE)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_DECADE)

    def test_can_set_calendars_view_into_century(self):
        self.calendar.set_view(win32defines.MCMV_CENTURY)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_CENTURY)

    def assert_system_time_is_equal_to_current_date_time(self,systemTime, now):
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

    def set_calendar_state_into_multiselect(self):
        self.app['Common Controls Sample']['MCS_MULTISELECT'].WrapperObject().Click()

    def test_can_get_today(self):
        """Test getting the control's today field"""
        date = self.calendar.get_today()
        self.assert_system_time_is_equal_to_current_date_time(date, datetime.date.today())

    def test_can_set_today(self):
        """Test setting up the control's today field"""
        self.calendar.set_today(2016, 5, 1)
        self.assert_system_time_is_equal_to_current_date_time(self.calendar.get_today(),
                                                              datetime.date(2016, 5, 1))

    def test_can_set_and_get_first_day_of_week(self):
        """Test can set and get first day of the week"""
        self.calendar.set_first_weekday(4)
        self.assertEqual((True,4), self.calendar.get_first_weekday())

if __name__ == "__main__":
    unittest.main()
>>>>>>> refs/remotes/pywinauto/UIA
