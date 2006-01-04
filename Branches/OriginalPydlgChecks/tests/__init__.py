__all__ = ['registered_tests']


test_names = (
		"AllControls",
		"AsianHotkey",
		"ComboBoxDroppedHeight",
		"CompareToRefFont",
		"LeadTrailSpaces",
		"MiscValues",
		"Missalignment",
		"MissingExtraString",
		"Overlapping",
		"RepeatedHotkey",
		"Translation",
		"Truncation",
	#	"menux",
)


def __init_tests():
	"Initialize each test by loading it and then register it"
	initialized = {}
	
	for test_name in test_names:
		# get a reference to the package
		package = __import__("tests."+ test_name.lower())  # 

		# get the reference to the module		
		test_module = getattr(package, test_name.lower())

		# class name is the test name + "Test"
		test_class = getattr(test_module, test_name + "Test")
		
		initialized[test_name] = test_class
	
	return initialized

registered = __init_tests()
