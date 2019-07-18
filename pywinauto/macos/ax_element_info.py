import re
from CoreFoundation import (CFNumberGetValue, CFStringGetTypeID, CFArrayGetTypeID, CFGetTypeID,
                            CFNumberGetTypeID, CFBooleanGetTypeID, kCFNumberIntType, kCFNumberDoubleType)
from ApplicationServices import (AXUIElementGetTypeID, AXValueGetType, kAXValueCGSizeType, kAXValueCGPointType,
                                 kAXValueCFRangeType, kAXErrorAPIDisabled, kAXErrorActionUnsupported,
                                 kAXErrorAttributeUnsupported, kAXErrorCannotComplete, kAXErrorFailure,
                                 kAXErrorIllegalArgument, kAXErrorInvalidUIElement, kAXErrorInvalidUIElementObserver,
                                 kAXErrorNoValue, kAXErrorNotEnoughPrecision, kAXErrorNotImplemented, kAXErrorSuccess,
                                 AXUIElementCopyAttributeNames, AXUIElementCopyAttributeValue,
                                 AXUIElementCopyActionNames, AXUIElementCreateApplication, AXUIElementGetPid)
import AppKit
from AppKit import NSScreen
from subprocess import Popen, PIPE
import warnings
# parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(parent_dir)
from macos_functions import get_ws_instance


ax_type_from_string = {
    kAXValueCGSizeType: AppKit.NSSizeFromString,
    kAXValueCGPointType: AppKit.NSPointFromString,
    kAXValueCFRangeType: AppKit.NSRangeFromString,
}


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
        try:
            # print("Description = {}".format(dir(attrValue)))
            # print("DescriptionType = {}".format(type(attrValue.description())))
            extracted_str = re.search('{.*}', attrValue.description()).group()
            return tuple(ax_type_from_string[ax_attr_type](extracted_str))
        except KeyError:
            raise NotImplementedError()


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


class AxElementInfo(object):

    def __init__(self, ref=None):
        self.ref = ref
        cls = type(self)
        if isinstance(ref, cls):
            return cls(ref.ref)

    def __repr__(self):
        """Build a descriptive string for UIElements."""
        title = repr('')
        role = '<No role!>'
        c = repr(self.__class__).partition('<class \'')[-1].rpartition('\'>')[0]
        try:
            title = repr(self.name)
        except Exception:
            pass
        try:
            role = self.control_type
        except Exception:
            pass
        # if len(title) > 20:
        #     title = title[:20] + '...\''
        return '<{} {} {}>'.format(c, role, title)

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

    def children(self):
        if (self.ref is None):
            cls = type(self)
            appli = get_ws_instance().runningApplications()
            tab = []
            for app in appli:
                pid = app.processIdentifier()
                # print(app.localizedName())
                app_ref = cls(AXUIElementCreateApplication(pid))
                # if app_ref.name != '':
                tab.append(app_ref)
            return tab
        try:
            return (self._get_ax_attribute_value("AXChildren"))
        except Exception:
            return [] and warnings.warn("This element has no Children")

    def descendants(self):
        all_desc = []
        liste = self.children()

        def _collect_desc(elem):
            if elem._get_ax_attribute_value("AXChildren") is not None:
                children = elem._get_ax_attribute_value("AXChildren")
                for child in children:
                    all_desc.append(child)
                    _collect_desc(child)
        for child in liste:
            _collect_desc(child)
        return (all_desc)

    @property
    def name(self):
        if (self.ref is None):
            return("Desktop")
        try:
            return self._get_ax_attribute_value("AXTitle")
        except Exception:
            try:
                return self._get_ax_attribute_value("AXValue")
            except Exception:
                return ''

    @property
    def parent(self):
        if (self.ref is None):
            return(None)
        return (self._get_ax_attribute_value("AXParent"))

    @property
    def size(self):
        return (self._get_ax_attribute_value("AXSize"))

    @property
    def position(self):
        return (self._get_ax_attribute_value("AXPosition"))

    @property
    def is_selected(self):
        try:
            return (self._get_ax_attribute_value("AXSelected"))
        except Exception:
            return False

    @property
    def is_enabled(self):
        try:
            return (self._get_ax_attribute_value("AXEnabled"))
        except Exception:
            return False

    @property
    def rectangle(self):
        if (self.ref is None):
            e = NSScreen.mainScreen().frame()
            return (0, 0, int(float(e.size.width)), int(float(e.size.height)))
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
        if (self.ref is None):
            return("Desktop")
        try:
            role = self._get_ax_attribute_value("AXRole")
        except AXError:
            return ''

        if role.startswith('AX'):
            return role.replace('AX', '')
        return role

    @property
    def process_id(self):
        err, pid = AXUIElementGetPid(self.ref, None)
        if err != kAXErrorSuccess:
            raise AXError(err)
        return pid

    def kill_process(self):
        #kill like sigkill
        Popen(["kill", "-9", str(self.process_id)], stdout=PIPE).communicate()[0]
