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

# get imported by all
# each class and test register themselves with this
import re

#-----------------------------------------------------------------------------
class ClassRegistry(object):
	#-------------------------------------------------------------------------
	def __init__(self):
		self.defaultClass = None
		self.registry = {}
		
	#-------------------------------------------------------------------------
	def AddClass(self, className, classObj):
		self.registry[className] = classObj
	
	#-------------------------------------------------------------------------
	def GetClass(self, className):
		# see if any registered class matches the class name passed in
		for cls in self.registry:
			if re.match(cls, className):
				return self.registry[cls]
		
		# Ok if we got here then none matched so we need to 
		# return the default class if it has been set
		if self.defaultClass:
			return self.defaultClass
		
		else:
			# oops No default class - raise an exception
			raise unicode("Nothing registered with name '%s'"% className)
	
	#-------------------------------------------------------------------------
	def RegisteredClasses(self):
		return self.registry.keys()
			


# the following functions are so that when the class is imported many times 
# the variables windowClassRegistry, testFuncRegistry are not re-set
#-----------------------------------------------------------------------------
def WindowClassRegistry():
	global windowClassRegistry

	try:
		return windowClassRegistry
	except:
		windowClassRegistry = ClassRegistry()
		return windowClassRegistry
	

#-----------------------------------------------------------------------------
def TestFuncRegistry():
	global testFuncRegistry
	
	try:
		return testFuncRegistry
	except:
		testFuncRegistry = ClassRegistry()
		return testFuncRegistry


#-----------------------------------------------------------------------------
def Config():
	global testConfiguration
	
	try:
		return testConfiguration
	except:
		testConfiguration = {}
		return testConfiguration

