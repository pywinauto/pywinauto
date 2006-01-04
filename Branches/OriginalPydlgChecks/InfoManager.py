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

