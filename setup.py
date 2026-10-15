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

install_requires = []

if sys.platform == 'win32':
    packages = ["pywinauto",
                "pywinauto.tests",
                "pywinauto.controls",
                "pywinauto.windows",
                "pywinauto.qt",
                "pywinauto.linux",  # workaround to build a source release on Windows
                "pywinauto.macos"]
elif sys.platform.startswith('linux'):
    packages = ["pywinauto", "pywinauto.linux", "pywinauto.controls", "pywinauto.qt"]
elif sys.platform == 'darwin':
    install_requires = [
        'pyobjc-core',
        'pyobjc-framework-AppleScriptObjC',
        'pyobjc-framework-ApplicationServices',
        'pyobjc-framework-Cocoa',
        'pyobjc-framework-CoreText',
        'pyobjc-framework-FSEvents',
        'pyobjc-framework-Quartz',
    ]
    packages = ["pywinauto", "pywinauto.macos"]
else:
    packages = [
        "pywinauto", "pywinauto.windows", "pywinauto.linux", "pywinauto.macos", "pywinauto.qt",
        "pywinauto.controls", "pywinauto.tests",
    ]

setup(name='pywinauto',
    version = '1.0.0b1',
    description = 'A set of Python modules to automate GUI on Windows, Linux and macOS',
    keywords = "windows gui automation GuiAuto testing test desktop mouse keyboard linux macos",
    url = "https://github.com/pywinauto/pywinauto",
    project_urls = {
        "Source": "https://github.com/pywinauto/pywinauto",
    },
    author = 'Mark Mc Mahon and Contributors',
    author_email = 'pywinauto-users@lists.sourceforge.net',
    long_description = """
At it's simplest it allows you to send mouse and keyboard
actions to windows dialogs and controls, but it has support for more complex
controls also.

Useful links
-------------
- Home page: https://github.com/pywinauto/pywinauto
- Docs Intro: https://pywinauto.readthedocs.io/en/latest/
- Getting Started Guide: https://pywinauto.readthedocs.io/en/latest/getting_started.html
- StackOverflow tag: https://stackoverflow.com/questions/tagged/pywinauto
""",
    platforms=['win32', 'linux', 'darwin'],

    packages = packages,

    license = "BSD 3-clause",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Quality Assurance',
        ],
    install_requires=install_requires,
    extras_require={
        ':python_version <= "3.6"': [
            'comtypes<=1.2.1',
            'pywin32<=227',
            'injectlib',
        ],
        ':python_version > "3.6" and sys_platform == "win32"': [
            'comtypes',
            'pywin32',
            'injectlib',
        ],
        ':platform_system == "Linux"': [
            'python-xlib',
            'injectlib',  # add condition on Linux x86_64 (TODO: arm64 support)
        ],
    },
    )
