import re
import sys

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
from ApplicationServices import AXUIElementGetPid

from ApplicationServices import kAXErrorSuccess
from ApplicationServices import kAXErrorNoValue
# Those constants are supported only in pyobjc 6.2 and later
# pyobjc 6.2 supports Python 3.6 and later
if sys.version_info[0] < 3.6:
    from .macos_defines import kAXValueTypeCGPoint
    from .macos_defines import kAXValueTypeCGSize
    from .macos_defines import kAXValueTypeCGRect
    from .macos_defines import kAXValueTypeCFRange
    from .macos_defines import kAXValueTypeAXError
    from .macos_defines import kAXValueTypeIllegal
else:
    from ApplicationServices import kAXValueTypeCGPoint
    from ApplicationServices import kAXValueTypeCGSize
    from ApplicationServices import kAXValueTypeCGRect
    from ApplicationServices import kAXValueTypeCFRange
    from ApplicationServices import kAXValueTypeAXError
    from ApplicationServices import kAXValueTypeIllegal

from Foundation import * 

from AppKit import NSRunningApplication
from AppKit import NSSizeFromString
from AppKit import NSRectFromString
from AppKit import NSRangeFromString

from .macos_functions import check_attribute_valid
from .macos_functions import get_list_of_attributes
from .macos_functions import get_screen_frame
from .macos_functions import get_list_of_actions
from .macos_functions import getAXUIElementForApp

from .macos_defines import ax_attributes
from .ax_error import AXError
from .macos_structures import AX_RECT, AX_POINT, AX_SIZE
from ..element_info import ElementInfo

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
            kAXValueTypeCGSize:  NSSizeFromString,
            kAXValueTypeCGPoint: NSPointFromString,
            kAXValueTypeCGRect:  NSRectFromString,
            kAXValueTypeCFRange: NSRangeFromString,
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

    re_props = ["class_name", "name", "placeholder", "control_type","subrole"]
    exact_only_props = ["pid", "visible", "enabled", "rectangle", "description"]
    search_order = ["control_type", "class_name", "placeholder", "subrole", "pid",
        "visible", "enabled", "name", "rectangle", "description"]
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
            self.ref = getAXUIElementForApp(pid)
        elif isinstance(ref,(AXUIElementRef,type(None))):
            self.ref = ref
        else:
            print('Unknown type: {}'.format(type(ref)))

    def __repr__(self):
        """Build a descriptive string for UIElements."""
        c = repr(self.__class__).partition('<class \'')[-1].rpartition('\'>')[0]
        title = repr(self.name)
        role = self.control_type
        subrole = self.subrole
        return '<Class:{} Role:{} Subrole:{} Title{}>'.format(c, role, subrole, title)

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

    def _is_minimized(self):
        """
        Get the value of the the specified ax attribute
        Should be called for Windows only
        """
        return self._get_ax_attribute_value(ax_attributes['Minimized'])


    def _is_hidden(self):
        """
        Returns True if AXUIElement is hidden
        Should be called for Applications only
        """
        return self._get_ax_attribute_value(ax_attributes['Hidden'])

    @property
    def _app_info(self):
        native_ref = getAXUIElementForApp(self.process_id)
        return AxElementInfo(native_ref)

    def children(self, **kwargs):
        """Return children of the element"""
        process = kwargs.get("process", None)
        class_name = kwargs.get("class_name", None)
        title = kwargs.get("title", None)
        control_type = kwargs.get("control_type", None)
        subrole = kwargs.get("subrole", None)
        if self.is_desktop:
            cls = type(self)
            ws = NSWorkspace.sharedWorkspace()
            running_apps = ws.runningApplications()
            top_level_windows = []
            for app in running_apps:
                pid = app.processIdentifier()
                app_ref = cls(getAXUIElementForApp(pid))
                ax_app = AxElementInfo(app_ref)
                # We don't care about apps which does not support ax
                if len(get_list_of_attributes(ax_app.ref)) == 0:
                    continue
                top_level_windows_for_app = ax_app.children()
                top_level_windows = top_level_windows + top_level_windows_for_app
            return top_level_windows
        try:
            children = self._get_ax_attribute_value(ax_attributes["Children"])
            if children is None:
                return []
            filtred_res = []
            for child in children:
                if child.control_type is None:
                    continue
                if process and child.process_id != process:
                    continue
                if class_name and child.class_name != class_name:
                    continue
                if title and child.name != title:
                    continue
                if control_type and child.control_type != control_type:
                    continue
                if subrole and child.subrole != subrole:
                    continue
                filtred_res.append(child)
            return filtred_res
        except AXError as exc:
            return []

    def descendants(self, **kwargs):
        process = kwargs.get("process", None)
        class_name = kwargs.get("class_name", None)
        title = kwargs.get("title", None)
        control_type = kwargs.get("control_type", None)
        depth = kwargs.get("depth", None)

        liste = self.children()
        all_desc = list(liste)
        def _collect_desc(elem,lvl):
            next_lvl = lvl+1
            children = elem.children()
            if children is not None and len(children) > 0:
                for child in children:
                    all_desc.append(child)
                    if depth and next_lvl > depth:
                        continue
                    else:
                        _collect_desc(child,next_lvl)
        for child in liste:
            _collect_desc(child,1)
        filtred_res = []
        for desc in all_desc:
            if process and desc.process_id != process:
                continue
            if class_name and desc.class_name != class_name:
                continue
            if title and desc.name != title:
                continue
            if control_type and desc.control_type != control_type:
                continue
            filtred_res.append(desc)
        return filtred_res

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
                    return str(val)
            except Exception:
                continue
        # print('Empty name for:{}'.format(self.control_type))
        # print('available attr list: {}'.format(get_list_of_attributes(self.ref)))
        return ""

    @property
    def description(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Description"])
        except AXError:
            return ""

    @property
    def label(self):
        try:
            return self._get_ax_attribute_value("AXLabel")
        except AXError:
            return ""

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
            return AX_POINT(nspoint=native_obj)
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
        try:
            window_obj = self._get_ax_attribute_value(ax_attributes["Window"])
            if window_obj:
                return AxElementInfo(window_obj)
        except AXError:
            return None

    @property
    def rectangle(self):

        invalid_result = AX_RECT(left=-1,right=-1,top=-1,bottom=-1)
        if self.is_desktop:
            return AX_RECT(nsrect=get_screen_frame())
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

        if not role:
            return 'InvalidControlType'
        if role.startswith('AX'):
            return role.replace('AX', '')
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
    def subrole(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Subrole"])
        except AXError:
            return ''

    @property
    def visible(self):
        app = self._app_info
        window = self if self.control_type == 'Window' else self.window
        is_app_hidden = app._is_hidden()
        is_minimized = window._is_minimized()

        return not (is_app_hidden or is_minimized)

    @property
    def value(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Value"])
        except AXError:
            return ''
    
    @property
    def placeholder(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Placeholder"])
        except AXError:
            return ''

    @property
    def process_id(self):
        if self.is_desktop:
            return None
        err, pid = AXUIElementGetPid(self.ref, None)
        if err != kAXErrorSuccess:
            raise AXError(err)
        return pid

    pid = process_id

    @property
    def rich_text(self):
        """Return the text of the element"""
        return self.name

    @property
    def is_expanded(self):
        try:
            return self._get_ax_attribute_value(ax_attributes["Expanded"])
        except AXError:
            return False

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

    def get_avaliable_actions(self):
        return get_list_of_attributes(self)
