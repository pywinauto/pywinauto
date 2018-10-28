# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""tests a set of controls for repeated hotkey errors"""

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
##				if AsianHotkeyFormatIncorrect(item['text']):
##					bugs.append(
##					(
##						[win,],
##						{
##							"MenuItem": item['text'],
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
