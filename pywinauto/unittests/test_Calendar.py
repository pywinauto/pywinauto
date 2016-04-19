"Tests for CalendarWrapper"

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
    "Unit tests for the CalendarWrapperTests class"

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""

        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.calendar = self.app.Common_Controls_Sample.CalendarWrapper

    def tearDown(self):
        "Close the application after tests"
        # close the application
        self.dlg.type_keys("%{F4}")

    def testCanGetCurrenDateFromCalendar(self):
        date = self.calendar.GetCurrentDate()
        self.assertThatSystemTimeIsEqualCurrentDateTime(date,datetime.date.today())

    def testCanSetCurrenDateInCalendar(self):
        self.calendar.SetDate(2016, 4, 3, 13)
        self.assertThatSystemTimeIsEqualCurrentDateTime(self.calendar.GetCurrentDate(),
                                                datetime.date(2016, 4, 13)) 

    def testShouldReturnErrorwhenTryToSetInvalidDate(self):
        self.assertRaises(RuntimeError, self.calendar.SetDate, -2016, -4, -3, -13)

    def testCanGetCalendarBorder(self):
        width = self.calendar.GetCalendarBorderWidth()
        self.assertEqual(width,4)

    def testCanSetCalendarBorder(self):
        self.calendar.SetCalendarBorderWidth(6)
        self.assertEqual(self.calendar.GetCalendarBorderWidth(), 6)

    def testCanGetCalendarsCount(self):
        count = self.calendar.GetCalendarsCount()
        self.assertEqual(count, 1)
    
    def testCanGetCalendarsView(self):
        view = self.calendar.GetCalendarView()
        self.assertEqual(view, 0)

    def testShouldReturnErrorwhenTryToSetInvalidView(self):
        self.assertRaises(RuntimeError, self.calendar.SetCalendarView, -1)

    def testCanSetCalendarsViewIntoMonth(self):
        self.calendar.SetCalendarView(win32defines.MCMV_MONTH)
        self.assertEqual(self.calendar.GetCalendarView(), win32defines.MCMV_MONTH)

    def testCanSetCalendarsViewIntoYears(self):
        self.calendar.SetCalendarView(win32defines.MCMV_YEAR)
        self.assertEqual(self.calendar.GetCalendarView(), win32defines.MCMV_YEAR)

    def testCanSetCalendarsViewIntoDecade(self):
        self.calendar.SetCalendarView(win32defines.MCMV_DECADE)
        self.assertEqual(self.calendar.GetCalendarView(), win32defines.MCMV_DECADE)

    def testCanSetCalendarsViewIntoCentury(self):
        self.calendar.SetCalendarView(win32defines.MCMV_CENTURY)
        self.assertEqual(self.calendar.GetCalendarView(), win32defines.MCMV_CENTURY)

    def assertThatSystemTimeIsEqualCurrentDateTime(self,systemTime, now):
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

if __name__ == "__main__":
    unittest.main()
