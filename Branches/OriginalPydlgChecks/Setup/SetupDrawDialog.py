# to build files:
# setup.py py2exe

from distutils.core import setup 
import py2exe 
 
import sys
sys.argv.insert(1, "py2exe")

sys.path.append(r"..")

setupInfo = {
	# these are the main modules
	'console' : [r"..\DrawDialogFromXML.py",],
	

	# tell it the name of the Zip file
	'zipfile' : "Python24.zip",
	'py_modules' : [],
	'options' : {
		"py2exe": {
			#"bundle": 3,
			"packages": ["encodings"],
			'dist_dir': "DrawDialog",
		},
	},
}

setup(**setupInfo)


