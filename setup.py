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


setup(name='pywinauto',
	version='0.1.3',
	description='Python library for GUI automation and testing',
	url="no url",
	author='Mark Mc Mahon',
	author_email='mark.m.mcmahon@gmail.com',

	packages = ["pywinauto", "pywinauto.tests", "pywinauto.controls"],

	data_files=[
		('docs', ['docs/HISTORY.TXT', 'docs/TODO.TXT', 'docs/LICENSE.txt']),
	],	
	
	license = "LGPL",
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Lesser General Public License',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python',
		],
	)


 