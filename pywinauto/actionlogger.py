# simple module for hierarchical logging
# Copyright (C) 2015 Intel Corporation
# Copyright (C) 2015 airelil
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

try:
    from logger import logger
    foundLogger = True
except ImportError:
    foundLogger = False

import logging
logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO)

def set_level(level):
    """Set pywinauto logging level for default logger.
    Use logging.WARNING (30) or higher to disable pywinauto logging."""
    logger = logging.getLogger(__package__)
    logger.level = level

def reset_level():
    "Reset pywinauto logging level to default one (logging.NOTSET)"
    logger = logging.getLogger(__package__)
    logger.level = logging.NOTSET

def disable():
    "Disable logging pywinauto actions"
    set_level(logging.WARNING)

def enable():
    "Enable logging pywinauto actions"
    reset_level()

class CustomLogger(object):

    def __init__(self, logFilePath = None):
        self.logger = logger.Logger(logFilePath)

    def log(self, *args):
        for msg in args:
            self.logger.message(msg)

    def logSectionStart(self, msg):
        self.logger.sectionStart(msg)

    def logSectionEnd(self):
        self.logger.sectionEnd()


class StandardLogger(object):

    def __init__(self, logFilePath = None):
        self.logFilePath = logFilePath
        self.logger = logging.getLogger(__package__)

    def log(self, *args):
        self.logger.info(*args)

    def logSectionStart(self, msg):
        pass

    def logSectionEnd(self):
        pass

if foundLogger:
    ActionLogger = CustomLogger
else:
    ActionLogger = StandardLogger

disable() # disable standard logging by default