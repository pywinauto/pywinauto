import re
from CoreFoundation import (CFNumberGetValue, CFStringGetTypeID, CFArrayGetTypeID, CFGetTypeID,
                            CFNumberGetTypeID, CFBooleanGetTypeID, kCFNumberIntType, kCFNumberDoubleType)
from ApplicationServices import (AXUIElementGetTypeID, AXValueGetType, kAXValueCGSizeType, kAXValueCGPointType,
                                 kAXValueCFRangeType, kAXErrorAPIDisabled, kAXErrorActionUnsupported,
                                 kAXErrorAttributeUnsupported, kAXErrorCannotComplete, kAXErrorFailure,
                                 kAXErrorIllegalArgument, kAXErrorInvalidUIElement, kAXErrorInvalidUIElementObserver,
                                 kAXErrorNoValue, kAXErrorNotEnoughPrecision, kAXErrorNotImplemented, kAXErrorSuccess,
                                 AXUIElementCopyAttributeNames, AXUIElementCopyAttributeValue,
                                 AXUIElementCopyActionNames, AXUIElementCreateApplication,AXUIElementGetPid)
import sys
import os
import AppKit
import subprocess
from subprocess import Popen, PIPE

# parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(parent_dir)

import macos_functions
from macos_functions import get_ws_instance

def _cf_attr_to_py_object(self, attrValue):

    def _cf_array_to_py_list(list_value):
        list_builder = []
        for item in list_value:
            list_builder.append(_cf_attr_to_py_object(self, item))
        return list_builder

    def _cf_number_to_py_number(number_value):
        success, int_value = CFNumberGetValue(number_value, kCFNumberIntType, None)
        if success:
            return int(int_value)

        success, float_value = CFNumberGetValue(number_value, kCFNumberDoubleType, None)
        if success:
            return float(float_value)

        raise ErrorUnsupported('Error converting numeric attribute: {}'.format(number_value))

    cf_attr_type = CFGetTypeID(attrValue)
    cf_type_to_py_type = {
        CFStringGetTypeID(): str,
        CFBooleanGetTypeID(): bool,
        CFArrayGetTypeID(): _cf_array_to_py_list,
        CFNumberGetTypeID(): _cf_number_to_py_number,
        AXUIElementGetTypeID(): AxElementInfo,
    }
    try:
        return cf_type_to_py_type[cf_attr_type](attrValue)
    except KeyError:
        # did not get a supported CF type. Move on to AX type
        ax_attr_type = AXValueGetType(attrValue)
        ax_type_from_string = {
            kAXValueCGSizeType: AppKit.NSSizeFromString,
            kAXValueCGPointType: AppKit.NSPointFromString,
            kAXValueCFRangeType: AppKit.NSRangeFromString,
        }
        try:
            # print("Description = {}".format(dir(attrValue)))
            # print("DescriptionType = {}".format(type(attrValue.description())))
            extracted_str = re.search('{.*}', attrValue.description()).group()
            return tuple(ax_type_from_string[ax_attr_type](extracted_str))
        except KeyError:
            raise ErrorUnsupported('Return value not supported yet: {}'.format(ax_attr_type))


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
        raise Exception(self.message)


class AxElementInfo(object):

    def __init__(self, ref=None):
        self.ref = ref
        self.ns_app = None
        cls = type(self)
        if isinstance(ref, cls):
            return cls(ref.ref)

    def __repr__(self):
        """Build a descriptive string for UIElements."""
        title = repr('')
        role = '<No role!>'
        c = repr(self.__class__).partition('<class \'')[-1].rpartition('\'>')[0]
        try:
            title = repr(self.AXTitle)
        except Exception:
            try:
                title = repr(self.AXValue)
            except Exception:
                try:
                    title = repr(self.AXRoleDescription)
                except Exception:
                    pass
        try:
            role = self.AXRole
        except Exception:
            pass
        if len(title) > 20:
            title = title[:20] + '...\''
        return '<%s %s %s>' % (c, role, title)

    def __getattr__(self, name):
        if name.startswith('AX'):
            try:
                attr = self._get_ax_attribute_value(name)
                return attr
            except AttributeError:
                pass

    def _get_ax_attributes(self):
        """
        Get a list of the actions available on the AXUIElement
        """
        err, attr = AXUIElementCopyAttributeNames(self.ref, None)
        if err != kAXErrorSuccess:
            raise AXError(err)
        return list(attr)

    def _get_ax_attribute_value(self, attr):
        """
        Get the value of the the specified attribute
        """
        err, attrValue = AXUIElementCopyAttributeValue(self.ref, attr, None)
        if err == kAXErrorNoValue:
            return None

        if err != kAXErrorSuccess:
            raise AXError(err)
        return _cf_attr_to_py_object(self, attrValue)

    @classmethod
    def running_applications(cls):
        """Get a list of the running applications."""
        rApps = get_ws_instance().runningApplications()
        return rApps

    @classmethod
    def getAppRefByPid(cls, pid):
        """
            Get an AXUIElement reference to the application specified by the given PID.
        """
        app_ref = AXUIElementCreateApplication(pid)
        if app_ref is None:
            raise ErrorUnsupported('Error getting app ref')
        return cls(app_ref)

    @classmethod
    def getFrontmostApp(cls):
        """Get the current frontmost application.
        Raise a ValueError exception if no GUI applications are found.
        """
        apps = cls.running_applications()
        for app in apps:
            pid = app.processIdentifier()
            ref = cls.getAppRefByPid(pid)
            try:
                if ref.AXFrontmost:
                    return ref
            except:
                pass
        raise ValueError('No GUI application found.')

    def launchAppByBundleId(self, bundleID):
        """Launch the application with the specified bundle ID"""
        ws = AppKit.NSWorkspace.sharedWorkspace()

        r = ws.launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(
            bundleID,
            AppKit.NSWorkspaceLaunchNewInstance,
            AppKit.NSAppleEventDescriptor.nullDescriptor(),
            None)
        NsArray = macos_functions.get_app_instance_by_bundle(bundleID)
        self.ns_app = NsArray[0]
        if not r[0]:
            raise RuntimeError('Error launching specified application.')

    @staticmethod
    def terminateAppByBundleId(bundleID):
        """Terminate app with a given bundle ID.
        """
        ra = AppKit.NSRunningApplication
        if getattr(ra, "runningApplicationsWithBundleIdentifier_"):
            appList = ra.runningApplicationsWithBundleIdentifier_(bundleID)
            if appList and len(appList) > 0:
                app = appList[0]
                return app and app.terminate() and True or False
        return False

    def desktop(self):
        appli = self.running_applications()
        tab = []
        for app in appli:
            pid = app.processIdentifier()
            app_ref = self.getAppRefByPid(pid)
            tab.append(app_ref)
        return tab

    def app_ref(self):
        pid = self.ns_app.processIdentifier()
        app_ref = self.getAppRefByPid(pid)
        while app_ref.name == '':
            app_ref = self.getAppRefByPid(pid)
        return(app_ref)

    def children(self):
        if (self.ref == None and self.ns_app == None):
            return self.desktop()
        try:
            return (self.AXChildren)
        except:
            return(self.getFrontmostApp().AXChildren)

    def descendants(self):
        all_desc = []
        liste = self.children()

        def _collect_desc(elem):
            if elem.AXChildren is not None:
                children = elem.AXChildren
                for child in children:
                    all_desc.append(child)
                    _collect_desc(child)
        for child in liste:
            _collect_desc(child)
        return (all_desc)

    @property
    def name(self):
        try:
            return self.AXTitle
        except Exception:
            try:
                return self.AXValue
            except Exception:
                return ''

    @property
    def parent(self):
        return (self.AXParent)

    @property
    def size(self):
        return (self.AXSize)

    @property
    def position(self):
        return (self.AXPosition)

    @property
    def is_selected(self):
        try:
            return (self.AXSelected)
        except:
            return False

    @property
    def is_enabled(self):
        try:
            return (self.AXEnabled)
        except:
            return False

    @property
    def rectangle(self):
        position = self.position
        size = self.size
        top = None
        left = None
        right = None
        bottom = None
        if self.size is not None:
            left, top = position
            right, bottom = size
            right += left

        return (int(float(top)), int(float(left)), int(float(bottom)), int(float(right)))

    @property
    def control_type(self):
        return (self.AXRole.replace('AX', ''))

    @property
    def process_id(self):
        identifier = None
        if (self.ns_app):
            identifier = self.ns_app.processIdentifier()
        return identifier

    def kill_process(self):
        #kill like sigkill
        Popen(["kill", "-9", str(self.process_id)], stdout=PIPE).communicate()[0]

