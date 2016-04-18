"Tests for HwndWrapper"

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

        # self.assertEqual(datetime())

    def testCanSetCurrenDateInCalendar(self):       
        self.calendar.SetDate(2016, 4, 3, 13)
        self.assertThatSystemTimeIsEqualCurrentDateTime(self.calendar.GetCurrentDate(),
                                                datetime.date(2016, 4, 13)) 

    def testCanGetCalendarBorder(self):
        width = self.calendar.GetCalendarBorderWidths()
        self.assertEqual(width,4)

    def testCanSetCalendarBorder(self):
        self.calendar.SetCalendarBorderWidths(6)
        self.assertEqual(self.calendar.GetCalendarBorderWidths(), 6)



    def assertThatSystemTimeIsEqualCurrentDateTime(self,systemTime, now):        
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

# .<wYear=2016, wMonth=4, wDayOfWeek=1, wDay=18, wHour=11, wMinute=51, wSecond=9, wMilliseconds=582>
if __name__ == "__main__":
    unittest.main()



# import sys, os

# os.chdir(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]))) # running at repo root folder

# import pywinauto

# mfc_samples_folder = os.path.join(
#    os.path.dirname(sys.argv[0]), r"apps\MFC_samples")
# if pywinauto.sysinfo.is_x64_Python():
#     mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

# app = pywinauto.Application().start(os.path.join(mfc_samples_folder,
#                                                  u"CmnCtrl1.exe"))

# tabc = app.Common_Controls_Sample.TabControl.WrapperObject()
# tabc.Select(4)
# ddd = app.Common_Controls_Sample.CalendarWrapper.GetCurrentDate()

# print(ddd)

# app.Common_Controls_Sample.CalendarWrapper.SetDate(2016, 4, 3, 13, 1, 1, 1, 1)

# ddd = app.Common_Controls_Sample.CalendarWrapper.GetCurrentDate()

# print(ddd)

# widths = app.Common_Controls_Sample.CalendarWrapper.GetCalendarBorderWidths()

# print(widths);

# birds = tree.get_item(r'\Birds')
# dogs = tree.get_item(r'\Dogs')

# drag-n-drop without focus on the window
#tree.drag_mouse("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
#
# most natural drag-n-drop (with real moving mouse, like real user)
# tree.drag_mouse_input("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
