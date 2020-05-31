import re

from CoreFoundation import CFNumberGetValue
from CoreFoundation import CFStringGetTypeID
from CoreFoundation import CFArrayGetTypeID
from CoreFoundation import CFGetTypeID
from CoreFoundation import CFNumberGetTypeID
from CoreFoundation import CFBooleanGetTypeID

from CoreFoundation import kCFNumberIntType
from CoreFoundation import kCFNumberDoubleType

from ApplicationServices import AXValueGetType
from ApplicationServices import AXUIElementGetTypeID
from ApplicationServices import AXUIElementCopyAttributeNames
from ApplicationServices import AXUIElementCopyAttributeValue
from ApplicationServices import AXUIElementRef
from ApplicationServices import AXUIElementCreateApplication
from ApplicationServices import AXUIElementGetPid

from ApplicationServices import kAXErrorSuccess
from ApplicationServices import kAXErrorNoValue
from ApplicationServices import kAXValueTypeCGPoint
from ApplicationServices import kAXValueTypeCGSize
from ApplicationServices import kAXValueTypeCGRect
from ApplicationServices import kAXValueTypeCFRange
from ApplicationServices import kAXValueTypeAXError
from ApplicationServices import kAXValueTypeIllegal

from Foundation import * # TODO: eliminate wildcard import
import AppKit
from AppKit import NSScreen
from AppKit import NSRunningApplication

from .macos_functions import check_attribute_valid, get_list_of_attributes
from .macos_defines import ax_attributes
from .ax_error import AXError
from ..element_info import ElementInfo
from .macos_structures import AX_RECT, AX_POINT, AX_SIZE
from pywinauto.macos.application import Application

import re

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

    def _cg_val_to_py_obj(cg_value):
        ax_type_from_string = {
            kAXValueTypeCGSize:  AppKit.NSSizeFromString,
            kAXValueTypeCGPoint: AppKit.NSPointFromString,
            kAXValueTypeCGRect:  AppKit.NSRectFromString,
            kAXValueTypeCFRange: AppKit.NSRangeFromString,
        }

        ax_attr_type = AXValueGetType(attrValue)
        if ax_attr_type == kAXValueTypeAXError or ax_attr_type == kAXValueTypeIllegal:
            return None
        string_val = re.search('{.*}', cg_value.description()).group()
        selector = ax_type_from_string[ax_attr_type]
        return selector(string_val)

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
        try:
            # AXValueGetValue is not yet supported, it requires a manual wrapper.
            # Implement macos structures and update the _cg_val_to_py_obj!!
            # Think about axstructures
            return _cg_val_to_py_obj(attrValue)

        except KeyError:
            raise NotImplementedError("Type conversion for {} and {} is not implemented".format(str(cf_attr_type), str(ax_attr_type)))

class AxElementInfo(ElementInfo):
    # TODO: Check other string props
    re_props = ["class_name", "name", "control_type"]
    exact_only_props = ["pid", "visible", "enabled", "rectangle",
        "framework_id", "framework_name", "atspi_version", "description"]
    search_order = ["control_type", "class_name", "pid",
        "visible", "enabled", "name", "rectangle",
        "framework_id", "framework_name", "atspi_version", "description"]
    # "auto_id", "full_control_type"
    assert set(re_props + exact_only_props) == set(search_order)

    renamed_props = {
        "title": ("name", None),
        "title_re": ("name_re", None),
        "process": ("pid", None),
        "visible_only": ("visible", {True: True, False: None}),
        "enabled_only": ("enabled", {True: True, False: None}),
        "top_level_only": ("depth", {True: 1, False: None}),
    }

    def __init__(self, ref=None):
        cls = type(self)
        self.is_desktop = ref is None
        self.__is_app = isinstance (ref, NSRunningApplication)
        if isinstance(ref, cls):
            self.ref = ref.ref
        elif self.__is_app:
            pid = ref.processIdentifier()
            self.ref = AXUIElementCreateApplication(pid)
        elif isinstance(ref,(AXUIElementRef,type(None))):
            self.ref = ref
        else:
            print('Unknown type: {}'.format(type(ref)))

    def __repr__(self):
        """Build a descriptive string for UIElements."""
        c = repr(self.__class__).partition('<class \'')[-1].rpartition('\'>')[0]
        title = repr(self.name)
        role = self.control_type
        return '<{} {} {}>'.format(c, role, title)

    def __eq__(self, other):
        """Check if two AxElementInfo objects describe the same element"""
        if not isinstance(other, AxElementInfo):
            return False
        if self.control_type == "Application" and other.control_type == "Application":
            return self.process_id == other.process_id
        return self.ref == other.ref

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
            ax_error = AXError(err)
            # print('Getting {} attribute caused error (code = {}): "{}"'.format(attr,ax_error.err_code, ax_error.message))
            raise ax_error
        else:
            return _cf_attr_to_py_object(self, attrValue)

    def children(self, **kwargs):
        """Return children of the element"""
        process = kwargs.get("process", None)
        class_name = kwargs.get("class_name", None)
        title = kwargs.get("title", None)
        control_type = kwargs.get("control_type", None)
        if self.is_desktop:
            cls = type(self)
            ws = NSWorkspace.sharedWorkspace()
            running_apps = ws.runningApplications()
            top_level_windows = []
            for app in running_apps:
                pid = app.processIdentifier()
                app_ref = cls(AXUIElementCreateApplication(pid))
                ax_app = AxElementInfo(app_ref)
                # We don't care about apps which does not support ax
                if len(get_list_of_attributes(ax_app.ref)) == 0:
                    continue
                top_level_windows_for_app = ax_app.children()
                top_level_windows = top_level_windows + top_level_windows_for_app
            return top_level_windows
        try:
            children = self._get_ax_attribute_value("AXChildren")
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

    def descendants(self, **kwargs):
        liste = self.children()
        all_desc = liste
        def _collect_desc(elem):
            children = elem.children()
            if children is not None:
                for child in children:
                    all_desc.append(child)
                    _collect_desc(child)
        for child in liste:
            _collect_desc(child)
        return all_desc

    @property
    def name(self):
        if self.is_desktop:
            return "Desktop"
        if self.control_type == "MenuBar":
            return "MenuBar"
        name_related_attrs_list = [
            "AXTitle",
            "AXLabel",
            "AXValue",
            "AXIdentifier",
            "AXDescription",
            "AXHelp"]
        # NOTE: Value for AXIdentifier key could be a system identifier like:_NS:XXX
        # Where: XXX - int value
        # In addition, the value may be a unique identifier provided by the developer.
        for attr in name_related_attrs_list:
            try:
                val = self._get_ax_attribute_value(attr)
                if val:
                    return val
            except Exception:
                return ''

    @property
    def parent(self):
        if self.is_desktop:
            return None
        try:
            parent = self._get_ax_attribute_value(ax_attributes["Parent"])
            if (parent.class_name == 'Application'):
                # User should not work with NSRunningApplication as AXElementInfo
                # Because it's not a GUI element
                # Desktop object will be returned
                return AxElementInfo()
            else:
                return parent
        except AXError as err:
            return None
        return self._get_ax_attribute_value("AXParent")

    @property
    def size(self):
        try:
            native_obj = self._get_ax_attribute_value(ax_attributes["Size"])
            return AX_SIZE(nssize=native_obj)
        except AXError as err:
            return AX_SIZE(width=-1,height=-1)

    @property
    def position(self):
        try:
            native_obj = self._get_ax_attribute_value(ax_attributes["Position"])
            return AX_POINT(nspoint = native_obj)
        except AXError as err:
            return AX_POINT(x=-1,y=-1)

    @property
    def is_selected(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Selected"])
        except AXError:
            return False

    @property
    def enabled(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Enabled"])
        except AXError:
            return False

    @property
    def frame(self):
        try:
            native_obj = self._get_ax_attribute_value(ax_attributes["Frame"])
            return AX_RECT(nsrect=native_obj)
        except AXError:
            return AX_RECT(left=-1,right=-1,top=-1,bottom=-1)

    @property
    def is_focused(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Focused"])
        except AXError:
            return False

    @property
    def can_be_keyboard_focusable(self):
        return check_attribute_valid(self.ref,ax_attributes["Focused"])

    @property
    def window(self):
        #TODO: What should we return when element is Window object? Should we return self?
        try:
            window_obj = self._get_ax_attribute_value(ax_attributes["Window"])
            if window_obj:
                return AxElementInfo(window_obj)
        except AXError:
            return None

    @property
    def app(self):
        # TODO: Should we have such help method as a part of this class?
        # If yes, what kind of object should be returned? ElementInfo or Application???
        # SHOULD be reviewed
        # Mark: use AXUIElementCreateApplication if we must return ElementInfo
        return Application().connect(process=self.process_id);

    @property
    def rectangle(self):

        invalid_result = AX_RECT(left=-1,right=-1,top=-1,bottom=-1)
        if self.is_desktop:
            e = NSScreen.mainScreen().frame()
            return AX_RECT(nsrect=e)
        if self.control_type == "Application":
            # The application object has not frame/position
            # Such properties should be taken from window object
            try:
                focused_window = self._get_ax_attribute_value("AXFocusedWindow")
                if focused_window:
                    window_info = AxElementInfo(focused_window)
                    return window_info.rectangle
                else:
                    return invalid_result
            except AXError as err:
                return invalid_result

        return self.frame

    @property
    def control_type(self):
        if self.is_desktop:
            return 'Desktop'
        try:
            role = self._get_ax_attribute_value("AXRole")
        except AXError:
            return 'InvalidControlType'

        if role.startswith('AX'):
            return role.replace('AX', '')
        if not role:
            return 'InvalidControlType'
        return role

    @property
    def class_name(self):
        if self.is_desktop:
            return 'Desktop'
        try:
            role = self._get_ax_attribute_value("AXRole")
            if role.startswith('AX'):
                role = role.replace('AX', '')
            return role
        except AXError:
            return 'InvalidClassName'

    @property
    def visible(self):
        # TODO: Implement
        pass

    @property
    def process_id(self):
        if self.is_desktop:
            return None
        err, pid = AXUIElementGetPid(self.ref, None)
        if err != kAXErrorSuccess:
            raise AXError(err)
        return pid
    # TODO: Is there any better way? To have pid or process id in whole code.s
    pid = process_id

    @property
    def rich_text(self):
        """Return the text of the element"""
        return self.name

    def set_cache_strategy(self, cached):
        """Set a cache strategy for frequently used attributes of the element"""
        pass  # TODO: implement a cache strategy for ax elements

    @property
    def control_id(self):
        """
        AXUIElement does not have unique id.
        Use hash instead of this one
        """
        # TODO: Discuss, is it a good idea to use hash as a control id?
        return -1


def runLoopAndExit():
    AppHelper.stopEventLoop()

def cache_update():
    AppHelper.callAfter(runLoopAndExit)
    AppHelper.runConsoleEventLoop()
