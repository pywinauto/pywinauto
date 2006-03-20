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

# to build files:
# setup.py py2exe

from distutils.core import setup

import pywinauto


setup(name='pywinauto',
    version = pywinauto.__version__,
    description = 'pywinauto is a set of python modules to automate the Microsoft Windows GUI',
    keywords = "windows automation gui GuiAuto",
    url = "http://sourceforge.net/projects/pywinauto",
	author = 'Mark Mc Mahon',
	author_email = 'mark.m.mcmahon@gmail.com',
    long_description = """
At it's simplest it allows you to send mouse and keyboard
actions to windows dialogs and controls, but It has support for more complex
controls also.
""",

	packages = ["pywinauto", "pywinauto.tests", "pywinauto.controls"],

	#data_files=[
	#	('examples', ['examples/notepad_fast.pkl', ]),
	#],

	license = "LGPL",
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
		],
	)


