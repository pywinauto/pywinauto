import re

from CoreFoundation import CFNumberGetValue
from CoreFoundation import CFStringGetTypeID
from CoreFoundation import CFArrayGetTypeID
from CoreFoundation import CFGetTypeID
from CoreFoundation import CFNumberGetTypeID
from CoreFoundation import CFBooleanGetTypeID
from CoreFoundation import kCFNumberIntType
from CoreFoundation import kCFNumberDoubleType
from ApplicationServices import AXUIElementGetTypeID
from ApplicationServices import AXValueGetType
from ApplicationServices import kAXValueCGSizeType
from ApplicationServices import kAXValueCGPointType
# from ApplicationServices import kAXValueCFRangeType
from ApplicationServices import kAXErrorAPIDisabled
from ApplicationServices import kAXErrorActionUnsupported
from ApplicationServices import kAXErrorAttributeUnsupported
from ApplicationServices import kAXErrorCannotComplete
from ApplicationServices import kAXErrorFailure
from ApplicationServices import kAXErrorIllegalArgument
from ApplicationServices import kAXErrorInvalidUIElement
from ApplicationServices import kAXErrorInvalidUIElementObserver
from ApplicationServices import kAXErrorNoValue
from ApplicationServices import kAXErrorNotEnoughPrecision
from ApplicationServices import kAXErrorNotImplemented
from ApplicationServices import kAXErrorSuccess
from ApplicationServices import AXUIElementCopyAttributeNames
from ApplicationServices import AXUIElementCopyAttributeValue
from ApplicationServices import AXUIElementRef
from ApplicationServices import AXUIElementCreateApplication
from ApplicationServices import AXUIElementGetPid
from Foundation import * # TODO: eliminate wildcard import
import AppKit
from AppKit import NSScreen
from AppKit import NSRunningApplication
# from AppKit import NSSize
# from AppKit import NSPoint

ax_type_from_string = {
    kAXValueCGSizeType: AppKit.NSSizeFromString,
    kAXValueCGPointType: AppKit.NSPointFromString,
    # kAXValueCFRangeType: AppKit.NSRangeFromString,
}

# ax_type_from_string = {
#     kAXValueCGSizeType: AppKit.NSSizeFromCGSize,
#     kAXValueCGPointType: AppKit.NSPointFromCGPoint,
# }

# d = {
#     kAXValueCGSizeType: lambda ns_size: (NSSize().height, NSSize().width),
#     kAXValueCGPointType: lambda ns_point: (NSPoint().x, NSPoint().y),
# }

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

        raise TypeError('Value {} is not CFNumber'.format(number_value))

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
            extracted_str = re.search('{.*}', attrValue.description()).group()
            # obj = ax_type_from_string[ax_attr_type]
            # t = obj(attrValue)
            return tuple(ax_type_from_string[ax_attr_type](extracted_str))
            # return tuple(d[ax_attr_type](attrValue))
        except KeyError:
            raise NotImplementedError("Type conversion for {} and {} is not implemented".format(cf_attr_type, ax_attr_type))


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
            self.ref = ref.ref
        elif isinstance (ref, NSRunningApplication):
            pid = ref.processIdentifier()
            self.ref = AXUIElementCreateApplication(pid)
        elif isinstance(ref,(AXUIElementRef,type(None))):
            pass
        else:
            print('Unknown type: {}'.format(type(ref)))

    def __repr__(self):
        """Build a descriptive string for UIElements."""
        c = repr(self.__class__).partition('<class \'')[-1].rpartition('\'>')[0]
        title = repr(self.name)
        role = self.control_type
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
            ws = NSWorkspace.sharedWorkspace()
            appli = ws.runningApplications()
            tab = []
            for app in appli:
                pid = app.processIdentifier()
                app_ref = cls(AXUIElementCreateApplication(pid))
                # if app_ref.name != '':
                tab.append(app_ref)
            return tab
        try:
            children =self._get_ax_attribute_value("AXChildren")
            if children is None:
                return []
            return children
        except AXError as exc:
            # warnings.warn(RuntimeWarning, 'Getting AXChildren attribute caused error (code = {}): "{}"' \
            #     ''.format(exc.err_code, exc.message))
            print('Getting AXChildren attribute caused error (code = {}): "{}"' \
                ''.format(exc.err_code, exc.message))
            print(type(self.ref))
            return []

    def descendants(self):
        all_desc = []
        liste = self.children()
        def _collect_desc(elem):
            children= elem.children()
            if children is not None:
                for child in children:
                    all_desc.append(child)
                    _collect_desc(child)
        for child in liste:
            _collect_desc(child)
        return all_desc

    @property
    def name(self):
        if self.ref is None:
            return "Desktop"
        try:
            return self._get_ax_attribute_value("AXTitle")
        except Exception:
            try:
                return self._get_ax_attribute_value("AXValue")
            except Exception:
                return ''

    @property
    def parent(self):
        if self.ref is None:
            return None
        return self._get_ax_attribute_value("AXParent")

    @property
    def size(self):
        return self._get_ax_attribute_value("AXSize")

    @property
    def position(self):
        return self._get_ax_attribute_value("AXPosition")

    @property
    def is_selected(self):
        try:
            return self._get_ax_attribute_value("AXSelected")
        except Exception:
            return False

    @property
    def is_enabled(self):
        try:
            return self._get_ax_attribute_value("AXEnabled")
        except Exception:
            return False

    @property
    def rectangle(self):
        if self.ref is None:
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

        return (int(float(top)), int(float(left)), int(float(right)), int(float(bottom)))

    @property
    def control_type(self):
        if self.ref is None:
            return"Desktop"
        try:
            role = self._get_ax_attribute_value("AXRole")
        except AXError:
            return 'InvalidControlType'

        if role.startswith('AX'):
            return role.replace('AX', '')
        return role

    @property
    def process_id(self):
        if self.ref is None:
            return None
        err, pid = AXUIElementGetPid(self.ref, None)
        if err != kAXErrorSuccess:
            raise AXError(err)
        return pid
