# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Install and build pywinauto distributions"""

from __future__ import print_function

from setuptools import setup

import os.path
import sys

# We need the path to setup.py to be able to run
# the setup from a different folder
def setup_path(path = ""):
    # get the path to the setup file
    setup_path = os.path.abspath(os.path.split(__file__)[0])

    return os.path.join(setup_path, path)

# add it to the system path
sys.path.append(setup_path())

# make sure the documentation is in the correct place for building
# todo: see how to build the website
#if "sdist" in sys.argv:
#    import shutil
#    if not os.path.exists(setup_path("docs")):
#        shutil.move(setup_path("website"), setup_path("docs"))

if sys.platform == 'win32':
    install_requires = ['six', 'comtypes']
    try:
        import win32api # check if it was already installed manually
    except ImportError:
        install_requires.append('pywin32')

    packages = ["pywinauto", "pywinauto.tests", "pywinauto.controls", "pywinauto.linux"]
else:
    install_requires = ['six', 'python-xlib']
    packages = ["pywinauto", "pywinauto.linux"]

setup(name='pywinauto',
    version = '0.6.5',
    description = 'A set of Python modules to automate the Microsoft Windows GUI',
    keywords = "windows gui automation GuiAuto testing test desktop mouse keyboard",
    url = "http://pywinauto.github.io/",
    author = 'Mark Mc Mahon and Contributors',
    author_email = 'pywinauto-users@lists.sourceforge.net',
    long_description = """
At it's simplest it allows you to send mouse and keyboard
actions to windows dialogs and controls, but It has support for more complex
controls also.

Useful links
-------------
- Home page: http://pywinauto.github.io/
- Docs Intro: https://pywinauto.readthedocs.io/en/latest/
- Getting Started Guide: https://pywinauto.readthedocs.io/en/latest/getting_started.html
- StackOverflow tag: https://stackoverflow.com/questions/tagged/pywinauto
""",
    platforms=['win32'],

    packages = packages,

    license = "BSD 3-clause",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Quality Assurance',
        ],
    install_requires=install_requires,
    )
