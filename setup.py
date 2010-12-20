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

"Install and build pywinauto distributions"


# to build files:
# setup.py py2exe

try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path
import sys

# We need the path to setup.py to be able to run
# the setup from a different folder
def SetupPath(path = ""):
    # get the path to the setup file
    setup_path = os.path.abspath(os.path.split(__file__)[0])

    return os.path.join(setup_path, path)


# add it to the system path
sys.path.append(SetupPath())

# now it should be safe to import pywinauto
import pywinauto



# make sure the documentation is in the correct place for building
# todo: see how to build the website
#if "sdist" in sys.argv:
#    import shutil
#    if not os.path.exists(SetupPath("docs")):
#        shutil.move(SetupPath("website"), SetupPath("docs"))


setup(name='pywinauto',
    version = pywinauto.__version__,
    description = 'pywinauto is a set of python '
        'modules to automate the Microsoft Windows GUI',
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
        'License :: OSI Approved :: '
            'GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    )

# todo: see how to build the website later
#if "sdist" in sys.argv:
#    if not os.path.exists(SetupPath("website")):
#        shutil.move(SetupPath("documentation"), SetupPath("website"))


try:
    import ctypes
    import SendKeys
except ImportError, e:
    print "The following module has to be installed before running pywinauto..."
    print "\t", str(e).replace("No module named ", "")
