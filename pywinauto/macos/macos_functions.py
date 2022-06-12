# -*- coding: utf-8 -*-
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
from __future__ import print_function

import subprocess
import six

from .ax_error import AXError

from Quartz import kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from Quartz import CGDisplayBounds
from Quartz import CGMainDisplayID

from ApplicationServices import AXUIElementSetAttributeValue
from ApplicationServices import AXIsProcessTrusted
from ApplicationServices import AXUIElementCopyAttributeNames 
from ApplicationServices import kAXErrorSuccess
from ApplicationServices import AXUIElementCopyAttributeValue 
from ApplicationServices import AXUIElementCopyActionNames
from ApplicationServices import AXUIElementCopyParameterizedAttributeNames
from ApplicationServices import AXUIElementPerformAction
from ApplicationServices import CGWindowListCopyWindowInfo
from ApplicationServices import NSWorkspaceLaunchAllowingClassicStartup
from ApplicationServices import AXUIElementCreateApplication

from AppKit import NSWorkspace
from AppKit import NSRunningApplication
from AppKit import NSBundle
from AppKit import NSWorkspaceLaunchNewInstance
from AppKit import NSApplicationActivateIgnoringOtherApps

from Foundation import NSAppleEventDescriptor, NSRectFromCGRect
from PyObjCTools import AppHelper

is_debug = False

def __get_string_value(value):
    if isinstance(value, six.string_types):
        return six.text_type(value)

def launch_application(name):
    # Open application by name(without package name)
    # Return the application instance
    # TODO: Should open unique app
    return get_ws_instance().launchApplication_(name)

def bundle_identifier_for_application_name(app_name):
    path = NSWorkspace.sharedWorkspace().fullPathForApplication_(app_name)
    bundle = NSBundle.bundleWithPath_(path)
    bundleIdentifier = bundle.bundleIdentifier()
    return bundleIdentifier

def launch_application_by_bundle(bundle_id, new_instance=True):
    if (new_instance):
        param = NSWorkspaceLaunchNewInstance
    else:
        param = NSWorkspaceLaunchAllowingClassicStartup

    r = get_ws_instance().launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(bundle_id,
            param,
            NSAppleEventDescriptor.nullDescriptor(),
            None)
    if not r[0]:
        raise RuntimeError('Error launching specified application. Result: {}'.format(r))

def url_for_application_name(app_name):
    path = NSWorkspace.sharedWorkspace().fullPathForApplication_(app_name)
    bundle = NSBundle.bundleWithPath_(path)
    return bundle.executableURL()

def launch_application_by_url(url, new_instance=True):
    if (new_instance):
        param = NSWorkspaceLaunchNewInstance
    else:
        param = NSWorkspaceLaunchAllowingClassicStartup

    r = get_ws_instance().launchApplicationAtURL_options_configuration_error_(url, param, {}, None)
    if not r[0]:
        raise RuntimeError('Error launching specified application. Result: {}'.format(r))

def terminate_application(obj):
    if check_if_its_nsrunning_application(obj):
        obj.terminate();
    else:
        print("Object is not instance of NSRunningApplication. Can not terminate this.")

def check_if_its_nsrunning_application(obj):
    return True if ("NSRunningApplication" in str(type(obj))) else False

def get_ws_instance():
    ws = NSWorkspace.sharedWorkspace()
    return ws

def running_applications():
    """Return all running apps(system too)"""
    cache_update()
    rApps = get_ws_instance().runningApplications()
    return rApps


def get_instance_of_app(name):
    # Return NSRunningApplication instance if
    # app with such name is already running
    for app in running_applications():
        if app.localizedName() == name:
            return app
    if (is_debug):
        print ("App is not already running.Can't get instance")
    return None

def get_app_instance_by_pid(pid):
    return NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)

def get_app_instance_by_bundle(bundle):
    return NSRunningApplication.runningApplicationsWithBundleIdentifier_(bundle)

def get_screen_frame():
    mainMonitor = CGDisplayBounds(CGMainDisplayID())
    return NSRectFromCGRect(mainMonitor)

def read_from_clipboard():
    return subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

def get_windows_list_info():
    list_info = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    if list_info is not None:
        return list_info

def check_is_process_trusted():
    if not (AXIsProcessTrusted()):
        if (is_debug):
            print("Process is not Trusted")
        exit(-1)

def get_list_of_attributes(ax_element):
    list_of_options_result_with_error_code = AXUIElementCopyAttributeNames(ax_element,None)
    if not (check_error(list_of_options_result_with_error_code)):
        list_of_options = list_of_options_result_with_error_code[1]
        return list_of_options
    else:
        return []

def get_list_of_parameterized_attributes(ax_element):
    list_of_options_result_with_error_code = AXUIElementCopyParameterizedAttributeNames(ax_element,None)
    if not (check_error(list_of_options_result_with_error_code)):
        list_of_options = list_of_options_result_with_error_code[1]
        return list_of_options
    else:
        return []

def check_error(obj):
    if obj[0] == kAXErrorSuccess:
        return False
    else:
        if (is_debug):
            print("Capture the error with code"+str(obj[0]))
        return True

def check_attribute_valid(ax_element,attribute):
    list_of_options = get_list_of_attributes(ax_element)
    if list_of_options is None:
        return False
    for option in list_of_options:
        if option == attribute:
            return True
    return False

def get_ax_attribute(ax_element,attribute_name):
    if check_attribute_valid(ax_element,attribute_name):
        fetch_result_with_error = AXUIElementCopyAttributeValue(ax_element,__get_string_value(attribute_name),None)
        if not (check_error(fetch_result_with_error)):
            fetchResult = fetch_result_with_error[1]
            return fetchResult
        if (is_debug):
            print("Attribute " + attribute_name + " is not defined" )

# Sets the accessibility object's attribute to the specified value.
def set_ax_attribute(ax_element,attribute_name,value):
    result_code = AXUIElementSetAttributeValue(ax_element,__get_string_value(attribute_name),value)
    is_success = (result_code == 0)
    if is_success:
        return True
    else:
        raise AXError(result_code)

def get_list_of_actions(ax_element):
    list_of_options_result_with_error_code = AXUIElementCopyActionNames(ax_element,None)
    if not (check_error(list_of_options_result_with_error_code)):
        list_of_options = list_of_options_result_with_error_code[1]
        return list_of_options
    else:
        return []

def perform_action(ax_element,action):
    AXUIElementPerformAction(ax_element,action)

def print_child_tree(ui_element_ref, count=0):
    role = get_ax_attribute(ui_element_ref,"AXRole")
    if role is not None:
        print("-"*count + role)
    childrens = get_ax_attribute(ui_element_ref,"AXChildren")
    if childrens is not None:
        for item in childrens:
            if item is None:
                continue
            print_child_tree(item,count + 1)

# not used
# def get_descendants(root, descendants):
#    childrens = get_ax_attribute(ui_element_ref, "AXChildren")
#    if childrens is not None:
#        for child in childrens:
#            if child is not None:
#                descendants.append(child)
#            get_descendants(child, descendants)

def get_all_ax_elements_of_a_particular_type_from_app(ui_element_ref, input_type, store):
    if ( isinstance(store, list) and isinstance(input_type,str) ):
        if (check_attribute_valid(ui_element_ref,"AXRole") and get_ax_attribute(ui_element_ref,"AXRole") is not None):
            if (get_ax_attribute(ui_element_ref,"AXRole")==input_type):
                store.append(ui_element_ref)
        if (check_attribute_valid(ui_element_ref,"AXChildren")):
            childrens = get_ax_attribute(ui_element_ref,"AXChildren")
            if childrens is not None:
                for child in childrens:
                    get_all_ax_elements_of_a_particular_type_from_app(child,input_type,store)


def filter_list_of_ax_element_by_attr(ui_element_refs_list, attribute_name, attr_expected_value, store):
    if (isinstance(ui_element_refs_list,list) and isinstance(attribute_name, str) and isinstance(store, list)):
        for element in ui_element_refs_list:
            if (check_attribute_valid(element,attribute_name) and get_ax_attribute(element,attribute_name) is not None):
                if (get_ax_attribute(element,attribute_name) == attr_expected_value):
                    store.append(element)


def run_loop_and_exit():
    AppHelper.stopEventLoop()

def cache_update():
    AppHelper.callAfter(run_loop_and_exit)
    AppHelper.runConsoleEventLoop()

def getAXUIElementForApp(pid):
    return AXUIElementCreateApplication(pid)

def setAppFrontmost(pid):
    """
    The application is activated regardless of the currently active app.
    All windows of application will be frontmost
    """
    runnning_application = get_app_instance_by_pid(pid)
    runnning_application.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)

