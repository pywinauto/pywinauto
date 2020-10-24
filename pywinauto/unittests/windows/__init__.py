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

"""Auto screenshot base class."""


import unittest


try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


SCREENSHOTMASK = "scr-{name}.jpg"


def save_screenshot(name):
    """
    Try to save a screenshot.

    Do nothing if ImageGrab was not imported.
    Use this method instead of direct `ImageGrab.grab()` call in your tests,
    to be sure a screenshot named according to the CI config.
    """
    if ImageGrab is not None:
        ImageGrab.grab().save(SCREENSHOTMASK.format(name=name), "JPEG")


class AutoScreenshotTestCase(unittest.TestCase):
    """
    Base class for pywinauto UI tests.

    Make screen shots if a test fails.
    """

    def _proxify(self, method_name):
        """
        Proxy call for a regular unittest.TestCase method.

        It is the only solution to intercept an error immediately
        and immediately make a screenshot.
        Screenshots names example:
        scr-testEnableDisable.jpg - failed in the main test section.
        scr-testEnableDisable_setUp - failed in the setUp method.
        """
        # save original method to a local variable
        original_method = getattr(self, method_name)

        def proxy(*args, **kwargs):
            """A proxy of the original method."""
            try:
                original_return = original_method(*args, **kwargs)

            except BaseException:
                if self._testMethodName == method_name:
                    # test's main execution section
                    name = method_name
                else:
                    # setUp or tearDown failed
                    name = "{test_name}_{method_name}".format(
                        test_name=self._testMethodName,
                        method_name=method_name)

                save_screenshot(name)

                # re-raise the original exception
                raise

            else:
                return original_return

        # replace the original method by own handler
        setattr(self, method_name, proxy)

    def __init__(self, *args, **kwargs):
        """Register methods to check for failures/errors."""
        super(AutoScreenshotTestCase, self).__init__(*args, **kwargs)

        # proxify needed methods
        self._proxify(self._testMethodName)
        self._proxify('setUp')
        self._proxify('tearDown')
