# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
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
    """Reset pywinauto logging level to default one (logging.NOTSET)"""
    logger = logging.getLogger(__package__)
    logger.level = logging.NOTSET

def disable():
    """Disable logging pywinauto actions"""
    set_level(logging.WARNING)

def enable():
    """Enable logging pywinauto actions"""
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