# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"tests a set of controls for repeated hotkey errors"

__revision__ = "$Revision$"

#
#
#from Test_AsianHotkey import AsianHotkeyFormatIncorrect
#from win32structures import RECT, LOGFONTW
#
#class DummyCtrl(dict):
#	def __getattr__(self, name):
#		if name not in self:
#			if name + "s" in self:
#				return self[name + "s"][0]
#		return self[name]
#
#
#
#
#
#
#
##-----------------------------------------------------------------------------
#def MenuRepeatedHotkeyTest(windows):
#	"Return the repeated hotkey errors"
#	bugs = []
#
#	for win in windows:
#		if win.MenuItems:
#			# we need to get all the separate menu blocks!
#			menuBlocks = GetMenuItemsAsCtrlBocks(win.MenuItems)
#
#			for menuBlock in menuBlocks:
#
#				for test in TestFuncRegistry().RegisteredClasses():
#
#					TestFunc = TestFuncRegistry().GetClass(test)
#
#					if hasattr(TestFunc, "TestsMenus") and TestFunc.TestsMenus:
#
#						testBugs = TestFunc(menuBlock)
#						bugs.extend(testBugs)
#
#
##
##				if AsianHotkeyFormatIncorrect(item['Text']):
##					bugs.append(
##					(
##						[win,],
##						{
##							"MenuItem": item['Text'],
##						},
##						"MenuAsianHotkeyFormat",
##						0)
##					)
##
##
#
#
#
##			bugs.append((
##				controls,
##				{
##					"RepeatedHotkey" : 		char,
##					"CharsUsedInDialog" :   SetAsString(hotkeys),
##					"AllCharsInDialog" :    SetAsString(allChars),
##					"AvailableInControls" : ctrlsAvailableChars,
##				},
##				"RepeatedHotkey",
##				isInRef)
#
#	return  bugs
#
#
#
#
#import tests
#tests.register("MenuRepeatedHotkey", AsiMenuRepeatedHotkeyTest)
