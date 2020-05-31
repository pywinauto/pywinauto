# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2020 Mark Mc Mahon and Contributors
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

"""Wrapper for mac os errors"""

from ApplicationServices import (kAXErrorAPIDisabled, kAXErrorActionUnsupported,
                                 kAXErrorAttributeUnsupported, kAXErrorCannotComplete, kAXErrorFailure,
                                 kAXErrorIllegalArgument, kAXErrorInvalidUIElement, kAXErrorInvalidUIElementObserver,
                                 kAXErrorNoValue, kAXErrorNotEnoughPrecision, kAXErrorNotImplemented, kAXErrorSuccess)
ax_error_description = {
    kAXErrorAPIDisabled: 'Assistive applications are not enabled in System Preferences',
    kAXErrorActionUnsupported: 'The referenced action is not supported',
    kAXErrorAttributeUnsupported: 'The referenced attribute is not supported',
    kAXErrorCannotComplete: 'A fundamental error has occurred, such as a failure to allocate memory during processing',
    kAXErrorFailure: 'A system error occurred, such as the failure to allocate an object',
    kAXErrorIllegalArgument: 'The value received in this event is an invalid value for this attribute',
    kAXErrorInvalidUIElement: 'The accessibility object received in this event is invalid',
    kAXErrorInvalidUIElementObserver: 'The observer for the accessibility object received in this event is invalid',
    kAXErrorNoValue: 'The requested value or AXUIElementRef does not exist',
    kAXErrorNotEnoughPrecision: 'Not enough precision',
    kAXErrorNotImplemented: 'The function or method is not implemented',
    kAXErrorSuccess: 'No error occurred',
}


class AXError(Exception):

    def __init__(self, err_code):
        self.err_code = err_code
        self.message = ax_error_description[err_code]

    def __str__(self):    
        """Build a descriptive string for AXError."""
        return '<Error code: {}, message: {}>'.format(self.err_code, self.message)

    def __repr__(self):
        """Build a descriptive string for AXError."""
        return '<Error code: {}, message: {}>'.format(self.err_code, self.message)
