# GUI Application automation and testing library
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2012 Michael Herrmann
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
