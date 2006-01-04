"tests a set of controls for repeated hotkey errors"

__revision__ = "0.0.1"
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
#	from InfoManager import TestFuncRegistry
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
