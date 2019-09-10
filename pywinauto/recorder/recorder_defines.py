# encoding: utf-8
import time
import sys
import locale
from abc import ABCMeta, abstractmethod
from ast import parse

import six

HOOK_KEY_DOWN = "key down"
HOOK_KEY_UP = "key up"

HOOK_MOUSE_LEFT_BUTTON = "LButton"
HOOK_MOUSE_RIGHT_BUTTON = "RButton"
HOOK_MOUSE_MIDDLE_BUTTON = "MButton"


class EVENT(object):
    ASYNC_CONTENT_LOADED = "AsyncContentLoaded"
    DRAG_CANCEL = "DragCancel"
    DRAG_COMPLETE = "DragComplete"
    DRAG_DROPPED = "DragDropped"
    DRAG_ENTER = "DragEnter"
    DRAG_LEAVE = "DragLeave"
    DRAG_START = "DragStart"
    EDIT_CONVERSION_TARGET_CHANGED = "EditConversionTargetChanged"
    EDIT_TEXT_CHANGED = "EditTextChanged"
    FOCUS_CHANGED = "FocusChanged"
    HOSTED_FRAGMENT_ROOTS_INVALIDATED = "HostedFragmentRootsInvalidated"
    INPUT_DISCARDED = "InputDiscarded"
    INPUT_REACHED_OTHER_ELEMENT = "InputReachedOtherElement"
    INPUT_REACHED_TARGET = "InputReachedTarget"
    INVOKED = "Invoked"
    LAYOUT_INVALIDATED = "LayoutInvalidated"
    LIVE_REGION_CHANGED = "LiveRegionChanged"
    MENU_CLOSED = "MenuClosed"
    MENU_END = "MenuEnd"
    MENU_OPENED = "MenuOpened"
    MENU_START = "MenuStart"
    PROPERTY_CHANGED = "PropertyChanged"
    SELECTION_ELEMENT_ADDED = "SelectionElementAdded"
    SELECTION_ELEMENT_REMOVED = "SelectionElementRemoved"
    SELECTION_ELEMENT_SELECTED = "SelectionElementSelected"
    SELECTION_INVALIDATED = "SelectionInvalidated"
    STRUCTURE_CHANGED = "StructureChanged"
    SYSTEM_ALERT = "SystemAlert"
    TEXT_CHANGED = "TextChanged"
    TEXT_SELECTION_CHANGED = "TextSelectionChanged"
    TOOLTIP_CLOSED = "ToolTipClosed"
    TOOLTIP_OPENED = "ToolTipOpened"
    WINDOW_CLOSED = "WindowClosed"
    WINDOW_OPENED = "WindowOpened"


class PROPERTY(object):
    ACCELERATOR_KEY = "AcceleratorKey"
    ACCESS_KEY = "AccessKey"
    ANNOTATION_TYPE_ID = "AnnotationTypeId"
    ANNOTATION_TYPE_NAME = "AnnotationTypeName"
    ANNOTATION_AUTHOR = "AnnotationAuthor"
    ANNOTATION_DATE_TIME = "AnnotationDateTime"
    ANNOTATION_OBJECTS = "AnnotationObjects"
    ANNOTATION_TARGET = "AnnotationTarget"
    ANNOTATION_TYPES = "AnnotationTypes"
    ARIA_PROPERTIES = "AriaProperties"
    ARIA_ROLE = "AriaRole"
    AUTOMATION_ID = "AutomationId"
    BOUNDING_RECTANGLE = "BoundingRectangle"
    CLASS_NAME = "ClassName"
    CLICKABLE_POINT = "ClickablePoint"
    CONTROL_TYPE = "ControlType"
    CONTROLLER_FOR = "ControllerFor"
    CULTURE = "Culture"
    DESCRIBED_BY = "DescribedBy"
    DOCK_POSITION = "DockPosition"
    DRAG_DROP_EFFECT = "DragDropEffect"
    DRAG_DROP_EFFECTS = "DragDropEffects"
    DRAG_GRABBED_ITEMS = "DragGrabbedItems"
    DRAG_IS_GRABBED = "DragIsGrabbed"
    DROP_TARGET_EFFECT = "DropTargetEffect"
    DROP_TARGET_EFFECTS = "DropTargetEffects"
    EXPAND_COLLAPSE_STATE = "ExpandCollapseState"
    FLOWS_FROM = "FlowsFrom"
    FLOWS_TO = "FlowsTo"
    FRAMEWORK_ID = "FrameworkId"
    FULL_DESCRIPTION = "FullDescription"
    GRID_COLUMN_COUNT = "GridColumnCount"
    GRID_ITEM_COLUMN = "GridItemColumn"
    GRID_ITEM_COLUMN_SPAN = "GridItemColumnSpan"
    GRID_ITEM_CONTAINING_GRID = "GridItemContainingGrid"
    GRID_ITEM_ROW = "GridItemRow"
    GRID_ITEM_ROW_SPAN = "GridItemRowSpan"
    GRID_ROW_COUNT = "GridRowCount"
    HAS_KEYBOARD_FOCUS = "HasKeyboardFocus"
    HELP_TEXT = "HelpText"
    IS_ANNOTATION_PATTERN_AVAILABLE = "IsAnnotationPatternAvailable"
    IS_CONTENT_ELEMENT = "IsContentElement"
    IS_CONTROL_ELEMENT = "IsControlElement"
    IS_CUSTOM_NAVIGATION_PATTERN_AVAILABLE = "IsCustomNavigationPatternAvailable"
    IS_DATA_VALID_FOR_FORM = "IsDataValidForForm"
    IS_DOCK_PATTERN_AVAILABLE = "IsDockPatternAvailable"
    IS_DRAG_PATTERN_AVAILABLE = "IsDragPatternAvailable"
    IS_DROP_TARGET_PATTERN_AVAILABLE = "IsDropTargetPatternAvailable"
    IS_ENABLED = "IsEnabled"
    IS_EXPAND_COLLAPSE_PATTERN_AVAILABLE = "IsExpandCollapsePatternAvailable"
    IS_GRID_ITEM_PATTERN_AVAILABLE = "IsGridItemPatternAvailable"
    IS_GRID_PATTERN_AVAILABLE = "IsGridPatternAvailable"
    IS_INVOKE_PATTERN_AVAILABLE = "IsInvokePatternAvailable"
    IS_ITEM_CONTAINER_PATTERN_AVAILABLE = "IsItemContainerPatternAvailable"
    IS_KEYBOARD_FOCUSABLE = "IsKeyboardFocusable"
    IS_LEGACY_I_ACCESSIBLE_PATTERN_AVAILABLE = "IsLegacyIAccessiblePatternAvailable"
    IS_MULTIPLE_VIEW_PATTERN_AVAILABLE = "IsMultipleViewPatternAvailable"
    IS_OBJECT_MODEL_PATTERN_AVAILABLE = "IsObjectModelPatternAvailable"
    IS_OFFSCREEN = "IsOffscreen"
    IS_PASSWORD = "IsPassword"
    IS_PERIPHERAL = "IsPeripheral"
    IS_RANGE_VALUE_PATTERN_AVAILABLE = "IsRangeValuePatternAvailable"
    IS_REQUIRED_FOR_FORM = "IsRequiredForForm"
    IS_SCROLL_ITEM_PATTERN_AVAILABLE = "IsScrollItemPatternAvailable"
    IS_SCROLL_PATTERN_AVAILABLE = "IsScrollPatternAvailable"
    IS_SELECTION_ITEM_PATTERN_AVAILABLE = "IsSelectionItemPatternAvailable"
    IS_SELECTION_PATTERN_AVAILABLE = "IsSelectionPatternAvailable"
    IS_SPREADSHEET_ITEM_PATTERN_AVAILABLE = "IsSpreadsheetItemPatternAvailable"
    IS_SPREADSHEET_PATTERN_AVAILABLE = "IsSpreadsheetPatternAvailable"
    IS_STYLES_PATTERN_AVAILABLE = "IsStylesPatternAvailable"
    IS_SYNCHRONIZED_INPUT_PATTERN_AVAILABLE = "IsSynchronizedInputPatternAvailable"
    IS_TABLE_ITEM_PATTERN_AVAILABLE = "IsTableItemPatternAvailable"
    IS_TABLE_PATTERN_AVAILABLE = "IsTablePatternAvailable"
    IS_TEXT_CHILD_PATTERN_AVAILABLE = "IsTextChildPatternAvailable"
    IS_TEXT_EDIT_PATTERN_AVAILABLE = "IsTextEditPatternAvailable"
    IS_TEXT_PATTERN2_AVAILABLE = "IsTextPattern2Available"
    IS_TEXT_PATTERN_AVAILABLE = "IsTextPatternAvailable"
    IS_TOGGLE_PATTERN_AVAILABLE = "IsTogglePatternAvailable"
    IS_TRANSFORM_PATTERN2_AVAILABLE = "IsTransformPattern2Available"
    IS_TRANSFORM_PATTERN_AVAILABLE = "IsTransformPatternAvailable"
    IS_VALUE_PATTERN_AVAILABLE = "IsValuePatternAvailable"
    IS_VIRTUALIZED_ITEM_PATTERN_AVAILABLE = "IsVirtualizedItemPatternAvailable"
    IS_WINDOW_PATTERN_AVAILABLE = "IsWindowPatternAvailable"
    ITEM_STATUS = "ItemStatus"
    ITEM_TYPE = "ItemType"
    LABELED_BY = "LabeledBy"
    LANDMARK_TYPE = "LandmarkType"
    LEGACY_I_ACCESSIBLE_CHILD_ID = "LegacyIAccessibleChildId"
    LEGACY_I_ACCESSIBLE_DEFAULT_ACTION = "LegacyIAccessibleDefaultAction"
    LEGACY_I_ACCESSIBLE_DESCRIPTION = "LegacyIAccessibleDescription"
    LEGACY_I_ACCESSIBLE_HELP = "LegacyIAccessibleHelp"
    LEGACY_I_ACCESSIBLE_KEYBOARD_SHORTCUT = "LegacyIAccessibleKeyboardShortcut"
    LEGACY_I_ACCESSIBLE_NAME = "LegacyIAccessibleName"
    LEGACY_I_ACCESSIBLE_ROLE = "LegacyIAccessibleRole"
    LEGACY_I_ACCESSIBLE_SELECTION = "LegacyIAccessibleSelection"
    LEGACY_I_ACCESSIBLE_STATE = "LegacyIAccessibleState"
    LEGACY_I_ACCESSIBLE_VALUE = "LegacyIAccessibleValue"
    LEVEL = "Level"
    LIVE_SETTING = "LiveSetting"
    LOCALIZED_CONTROL_TYPE = "LocalizedControlType"
    LOCALIZED_LANDMARK_TYPE = "LocalizedLandmarkType"
    MULTIPLE_VIEW_CURRENT_VIEW = "MultipleViewCurrentView"
    MULTIPLE_VIEW_SUPPORTED_VIEWS = "MultipleViewSupportedViews"
    NAME = "Name"
    NATIVE_WINDOW_HANDLE = "NativeWindowHandle"
    OPTIMIZE_FOR_VISUAL_CONTENT = "OptimizeForVisualContent"
    ORIENTATION = "Orientation"
    POSITION_IN_SET = "PositionInSet"
    PROCESS_ID = "ProcessId"
    PROVIDER_DESCRIPTION = "ProviderDescription"
    RANGE_VALUE_IS_READ_ONLY = "RangeValueIsReadOnly"
    RANGE_VALUE_LARGE_CHANGE = "RangeValueLargeChange"
    RANGE_VALUE_MAXIMUM = "RangeValueMaximum"
    RANGE_VALUE_MINIMUM = "RangeValueMinimum"
    RANGE_VALUE_SMALL_CHANGE = "RangeValueSmallChange"
    RANGE_VALUE_VALUE = "RangeValueValue"
    RUNTIME_ID = "RuntimeId"
    SCROLL_HORIZONTAL_SCROLL_PERCENT = "ScrollHorizontalScrollPercent"
    SCROLL_HORIZONTAL_VIEW_SIZE = "ScrollHorizontalViewSize"
    SCROLL_HORIZONTALLY_SCROLLABLE = "ScrollHorizontallyScrollable"
    SCROLL_VERTICAL_SCROLL_PERCENT = "ScrollVerticalScrollPercent"
    SCROLL_VERTICAL_VIEW_SIZE = "ScrollVerticalViewSize"
    SCROLL_VERTICALLY_SCROLLABLE = "ScrollVerticallyScrollable"
    SELECTION_CAN_SELECT_MULTIPLE = "SelectionCanSelectMultiple"
    SELECTION_IS_SELECTION_REQUIRED = "SelectionIsSelectionRequired"
    SELECTION_ITEM_IS_SELECTED = "SelectionItemIsSelected"
    SELECTION_ITEM_SELECTION_CONTAINER = "SelectionItemSelectionContainer"
    SELECTION_SELECTION = "SelectionSelection"
    SIZE_OF_SET = "SizeOfSet"
    SPREADSHEET_ITEM_ANNOTATION_OBJECTS = "SpreadsheetItemAnnotationObjects"
    SPREADSHEET_ITEM_ANNOTATION_TYPES = "SpreadsheetItemAnnotationTypes"
    SPREADSHEET_ITEM_FORMULA = "SpreadsheetItemFormula"
    STYLES_EXTENDED_PROPERTIES = "StylesExtendedProperties"
    STYLES_FILL_COLOR = "StylesFillColor"
    STYLES_FILL_PATTERN_COLOR = "StylesFillPatternColor"
    STYLES_FILL_PATTERN_STYLE = "StylesFillPatternStyle"
    STYLES_SHAPE = "StylesShape"
    STYLES_STYLE_ID = "StylesStyleId"
    STYLES_STYLE_NAME = "StylesStyleName"
    TABLE_COLUMN_HEADERS = "TableColumnHeaders"
    TABLE_ITEM_COLUMN_HEADER_ITEMS = "TableItemColumnHeaderItems"
    TABLE_ITEM_ROW_HEADER_ITEMS = "TableItemRowHeaderItems"
    TABLE_ROW_HEADERS = "TableRowHeaders"
    TABLE_ROW_OR_COLUMN_MAJOR = "TableRowOrColumnMajor"
    TOGGLE_STATE = "ToggleState"
    TRANSFORM2_CAN_ZOOM = "Transform2CanZoom"
    TRANSFORM2_ZOOM_LEVEL = "Transform2ZoomLevel"
    TRANSFORM2_ZOOM_MAXIMUM = "Transform2ZoomMaximum"
    TRANSFORM2_ZOOM_MINIMUM = "Transform2ZoomMinimum"
    TRANSFORM_CAN_MOVE = "TransformCanMove"
    TRANSFORM_CAN_RESIZE = "TransformCanResize"
    TRANSFORM_CAN_ROTATE = "TransformCanRotate"
    VALUE_IS_READ_ONLY = "ValueIsReadOnly"
    VALUE_VALUE = "ValueValue"
    WINDOW_CAN_MAXIMIZE = "WindowCanMaximize"
    WINDOW_CAN_MINIMIZE = "WindowCanMinimize"
    WINDOW_IS_MODAL = "WindowIsModal"
    WINDOW_IS_TOPMOST = "WindowIsTopmost"
    WINDOW_WINDOW_INTERACTION_STATE = "WindowWindowInteractionState"
    WINDOW_WINDOW_VISUAL_STATE = "WindowWindowVisualState"


class STRUCTURE_EVENT(object):
    CHILD_ADDED = "ChildAdded"
    CHILD_REMOVED = "ChildRemoved"
    CHILDREN_INVALIDATED = "ChildrenInvalidated"
    CHILDREN_ADDED = "ChildrenAdded"
    CHILDREN_REMOVED = "ChildrenRemoved"
    CHILDREN_REORDERED = "ChildrenReordered"


# RecorderEvent
# -- HookEvent
# -- -- RecorderMouseEvent
# -- -- RecorderKeyboardEvent
# -- ApplicationEvent
# -- -- PropertyEvent

class RecorderEvent(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.timestamp = time.time()
        self.control_tree_node = None  # event sender

    def __str__(self):
        """Return a representation of the object as a string"""
        if six.PY2:
            if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding is not None:
                # some frameworks override sys.stdout without encoding attribute (Tee Stream),
                # some users replace sys.stdout with file descriptor which can have None encoding
                return self.__repr__().encode(sys.stdout.encoding, errors='backslashreplace')
            else:
                return self.__repr__().encode(locale.getpreferredencoding(), errors='backslashreplace')
        else:
            return self.__repr__()


class HookEvent(RecorderEvent):
    def __init__(self, current_key=None, event_type=None):
        super(HookEvent, self).__init__()
        self.current_key = current_key
        self.event_type = event_type


class RecorderMouseEvent(HookEvent):
    def __init__(self, current_key=None, event_type=None, mouse_x=0, mouse_y=0):
        super(RecorderMouseEvent, self).__init__(current_key, event_type)
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def __repr__(self):
        """Return a representation of the object as a string"""
        if self.control_tree_node:
            elem = u" - {}".format(self.control_tree_node)
        else:
            elem = u""
        return u"<RecorderMouseEvent - '{}' - '{}' at ({}, {}){} [{}]>".format(self.current_key, self.event_type,
                                                                               self.mouse_x, self.mouse_y, elem,
                                                                               self.timestamp)


class RecorderKeyboardEvent(HookEvent):
    def __init__(self, current_key=None, event_type=None, pressed_key=None):
        super(RecorderKeyboardEvent, self).__init__(current_key, event_type)
        self.pressed_key = pressed_key

    def __repr__(self):
        """Return a representation of the object as a string"""
        return u"<RecorderKeyboardEvent - '{}' - '{}', pressed = {} [{}]>".format(
            self.current_key, self.event_type, self.pressed_key, self.timestamp)


class ApplicationEvent(RecorderEvent):
    def __init__(self, name, sender=None):
        super(ApplicationEvent, self).__init__()
        self.name = name
        self.sender = sender

    def __repr__(self):
        """Return a representation of the object as a string"""
        return u"<ApplicationEvent - '{}' from '{}'>".format(self.name, self.sender)


class PropertyEvent(ApplicationEvent):
    def __init__(self, property_name, sender=None, new_value=None):
        super(PropertyEvent, self).__init__(EVENT.PROPERTY_CHANGED, sender)
        self.property_name = property_name
        self.new_value = new_value

    def __repr__(self):
        """Return a representation of the object as a string"""
        return u"<PropertyEvent - Change '{}' to '{}' from {}>".format(self.property_name, self.new_value, self.sender)


class EventPattern(object):
    def __init__(self, hook_event=None, app_events=None):
        self.hook_event = hook_event
        self.app_events = app_events if app_events else []

    def __str__(self):
        """Return a representation of the object as a string"""
        return u"<EventPattern: {}, {}>".format(
            self.hook_event, ", ".join([str(e) for e in self.app_events]) if self.app_events else None)

    def get_subpattern(self, pattern):
        if not isinstance(pattern, EventPattern):
            return None

        subpattern = EventPattern(hook_event=self.hook_event, app_events=[])

        if pattern.hook_event and self.hook_event:
            if not isinstance(self.hook_event, type(pattern.hook_event)):
                return None
            if pattern.hook_event.current_key and self.hook_event.current_key != pattern.hook_event.current_key:
                return None
            if pattern.hook_event.event_type and self.hook_event.event_type != pattern.hook_event.event_type:
                return None

        idx = 0
        for item_ev in pattern.app_events:
            while idx < len(self.app_events):
                idx += 1
                self_ev = self.app_events[idx - 1]
                if self_ev.name != item_ev.name:
                    continue
                if isinstance(self_ev, PropertyEvent) and self_ev.property_name != item_ev.property_name:
                    continue
                subpattern.app_events.append(self_ev)
                break
            else:
                return None

        return subpattern


def _is_identifier(name):
    try:
        parse('{} = None'.format(name))
        return True
    except (SyntaxError, ValueError, TypeError):
        return False


def get_window_access_name_str(name, key_only=False):
    if not key_only and _is_identifier(name):
        return u".{}".format(name)
    else:
        return u"[u'{}']".format(name)


class EventHandler(object):
    def __init__(self, subtree, log_parser, subpattern):
        self.subtree = subtree
        self.log_parser = log_parser
        self.subpattern = subpattern

        self.key_only = self.log_parser.recorder.config.key_only

    def get_root_name(self):
        return get_window_access_name_str(self.subtree[-1].names.get_preferred_name(), self.key_only)

    def get_item_name(self):
        return get_window_access_name_str(self.subtree[0].names.get_preferred_name(), self.key_only)

    def get_sender_name(self, event_idx):
        sender = self.subpattern.app_events[event_idx].sender
        for node in self.subtree:
            if node.wrapper.element_info == sender:
                item_name = get_window_access_name_str(node.names.get_preferred_name(), self.key_only)
                break
        else:
            item_name = self.get_item_name()
        return item_name

    @abstractmethod
    def run(self):
        raise NotImplementedError()
