# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2010 Mark Mc Mahon
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
from __future__ import print_function

try:
    try:
        from ez_setup import use_setuptools
        use_setuptools()
    except ImportError:
        print('No ez_setup.py. Using plain setuptools...')
    from setuptools import setup
except ImportError:
    print('Using distutils.core for setup...')
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

try:
    import win32api
    requirements = []
except ImportError:
    requirements = ["pypiwin32"]

# make sure the documentation is in the correct place for building
# todo: see how to build the website
#if "sdist" in sys.argv:
#    import shutil
#    if not os.path.exists(SetupPath("docs")):
#        shutil.move(SetupPath("website"), SetupPath("docs"))


setup(name='pywinauto',
    version = '0.5.4',
    description = 'pywinauto is a set of python '
        'modules to automate the Microsoft Windows GUI',
    keywords = "windows automation gui GuiAuto",
    url = "http://pywinauto.github.io/",
    author = 'Mark Mc Mahon',
    author_email = 'mark.m.mcmahon@gmail.com',
    long_description = """
At it's simplest it allows you to send mouse and keyboard
actions to windows dialogs and controls, but It has support for more complex
controls also.
""",
    platforms=['win32'],

    packages = ["pywinauto", "pywinauto.tests", "pywinauto.controls"],

    license = "LGPL",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
            'GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
        ],
    install_requires=requirements,
    )
