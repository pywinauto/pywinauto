"""Tests for CalendarWrapper"""

import time
import datetime
#import pprint
#import pdb
#import warnings

import ctypes
import locale
import re

import sys, os
import unittest
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.controls.HwndWrapper import HwndWrapper, \
InvalidWindowHandle, GetDialogPropsFromHandle
from pywinauto import win32structures, win32defines
from pywinauto.findwindows import ElementNotFoundError, ElementNotFoundError
from pywinauto.sysinfo import is_x64_Python, is_x64_OS
from pywinauto.RemoteMemoryBlock import RemoteMemoryBlock
from pywinauto.timings import Timings, TimeoutError
from pywinauto import clipboard
from pywinauto import backend


mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

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
        self.assertThatSystemTimeIsEqualCurrentDateTime(date,datetime.date.today())

    def test_can_set_current_date_in_calendar(self):
        self.calendar.set_current_date(2016, 4, 3, 13)
        self.assertThatSystemTimeIsEqualCurrentDateTime(self.calendar.get_current_date(), datetime.date(2016, 4, 13)) 

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

    def test_should_throw__runtime_error_when_try_to_set_invalid_view(self):
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

    def assertThatSystemTimeIsEqualCurrentDateTime(self,systemTime, now):
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

if __name__ == "__main__":
    unittest.main()
