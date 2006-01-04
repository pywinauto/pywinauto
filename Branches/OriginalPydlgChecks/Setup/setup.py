# to build files:
# setup.py py2exe

from distutils.core import setup 
import py2exe 
import os.path
import glob
import sys


sys.argv.insert(1, "py2exe")
sys.path.append(os.path.abspath(r".."))

#setupInfo = {
#	# these are the main modules
#	'console' : [r"..\FindDialog.py",],
#	
#
#	# tell it the name of the Zip file
#	'zipfile' : "Python24.zip",
#	'data_files' : [
#		(".", [r"..\..\Basecontrol\dlgcheck2.dll"]),
#		#(".", [r"..\..\_Develop\Basecontrol\PythonConfig.py"]),
#		(".", [r"..\Readme.txt"]),
#	],
#	'py_modules' : [],
#	'options' : {
#		"py2exe": {
#			"packages": ["encodings"],
#			#"includes": ["passadd", "CUI_4_parser", "Testing_parser"],
#			
#		}
#	},
#}



setupInfo = {
	# these are the main modules
	'console' : [r"..\FindDialog.py",],
		
	# tell it the name of the Zip file
	'zipfile' : "Python24.zip",
	'data_files' : [
		(".", [r"..\..\Basecontrol\dlgcheck2.dll"]),
		(".", [r"..\Readme.txt"]),
	],
	'py_modules' : [],
	'options' : {
		"py2exe": {
			"packages": ["encodings", "tests", "controls"],
			"compressed" : 0,
			#"bundle_files" : 1,
			#"includes": ["passadd", "CUI_4_parser", "Testing_parser"],
			
		}
	},
}



#for file in glob.glob(r"..\*.py"):
	#setupInfo['data_files'].append((".", [file]))

	# fix the Py file so it is a module namec
	#moduleName = file.lstrip("..\\")
	#moduleName = moduleName[:-3]
	#setupInfo['py_modules'].append(file)
	#print "########################################", file
	

setup(**setupInfo)


print "\n*** Finished creating distribution *** "
print "Delete win9xpopen.exe"

