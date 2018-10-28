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
import logging

# Try to find a custom logger
try:
    import logger
    _found_logger = (logger.Logger.sectionStart is not None)
except (ImportError, AttributeError) as exc:
    _found_logger = False


def set_level(level):
    """Set a logging level for the pywinauto logger."""
    ActionLogger.set_level(level)


def reset_level():
    """Reset a logging level to a default"""
    ActionLogger.reset_level()


def disable():
    """Disable pywinauto logging actions"""
    ActionLogger.disable()


def enable():
    """Enable pywinauto logging actions"""
    reset_level()


class _CustomLogger(object):

    """
    Custom logger to use for pywinatuo logging actions.

    The usage of the class is optional and only if the standard
    logging facilities are not enough
    """

    def __init__(self, logFilePath=None):
        """Init the custom logger"""
        self.logger = logger.Logger(logFilePath)

    @staticmethod
    def set_level(level):
        """Set a logging level"""
        pass

    @staticmethod
    def reset_level():
        """Reset a logging level to a default"""
        pass

    @staticmethod
    def disable():
        """Set a logging level to one above INFO to disable logs emitting"""
        pass

    def log(self, *args):
        """Process a log message"""
        for msg in args:
            self.logger.message(msg)

    def logSectionStart(self, msg):
        self.logger.sectionStart(msg)

    def logSectionEnd(self):
        self.logger.sectionEnd()


def _setup_standard_logger():
    """A helper to init the standard logger"""
    logger = logging.getLogger(__package__)

    # For the meantime we allow only one handler.
    # This is the simplest way to avoid duplicates.
    if logger.handlers:
        return logger

    # Create a handler with logging.DEBUG as the default logging level,
    # means - all messages will be processed by the handler
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger


class _StandardLogger(object):

    """
    Wrapper around the standard python logger
    """

    logger = _setup_standard_logger()

    @staticmethod
    def set_level(level):
        """Set a logging level"""
        _StandardLogger.logger.level = level

    @staticmethod
    def reset_level():
        """Reset a logging level to a default one

        We use logging.INFO because 'logger.info' is called in 'log' method.
        Notice that setting up the level with logging.NOTSET results in delegating the filtering
        to other active loggers so that if another logger had set a higher level than we need,
        the messages for pywinauto logger will be dropped even if it was 'enabled'.
        """
        _StandardLogger.logger.level = logging.INFO

    @staticmethod
    def disable():
        """Set a logging level to one above INFO to disable logs emitting"""
        set_level(logging.WARNING)

    def __init__(self, logFilePath=None):
        """Init the wrapper"""
        self.logFilePath = logFilePath
        self.logger = _StandardLogger.logger

    def log(self, *args):
        """Process a log message"""
        self.logger.info(*args)

    def logSectionStart(self, msg):
        """Empty for now, just to conform with _CustomLogger"""
        pass

    def logSectionEnd(self):
        """Empty for now, just to conform with _CustomLogger"""
        pass

# Define which logging facilities should be used for pywinauto traces
if _found_logger:
    ActionLogger = _CustomLogger
else:
    ActionLogger = _StandardLogger

# Disable pywinauto prints by default.
# To re-enable, actionlogger.enable() has to be called implicitly
disable()
