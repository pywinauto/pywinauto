from ..recorder_defines import EVENT, PROPERTY, STRUCTURE_EVENT
from ..recorder_defines import ApplicationEvent

from ...uia_defines import IUIA

EVENT_ID_TO_NAME_MAP = {
    IUIA().UIA_dll.UIA_AsyncContentLoadedEventId: EVENT.ASYNC_CONTENT_LOADED,
    IUIA().UIA_dll.UIA_Drag_DragCancelEventId: EVENT.DRAG_CANCEL,
    IUIA().UIA_dll.UIA_Drag_DragCompleteEventId: EVENT.DRAG_COMPLETE,
    IUIA().UIA_dll.UIA_DropTarget_DroppedEventId: EVENT.DRAG_DROPPED,
    IUIA().UIA_dll.UIA_DropTarget_DragEnterEventId: EVENT.DRAG_ENTER,
    IUIA().UIA_dll.UIA_DropTarget_DragLeaveEventId: EVENT.DRAG_LEAVE,
    IUIA().UIA_dll.UIA_Drag_DragStartEventId: EVENT.DRAG_START,
    IUIA().UIA_dll.UIA_TextEdit_ConversionTargetChangedEventId: EVENT.EDIT_CONVERSION_TARGET_CHANGED,
    IUIA().UIA_dll.UIA_TextEdit_TextChangedEventId: EVENT.EDIT_TEXT_CHANGED,
    IUIA().UIA_dll.UIA_AutomationFocusChangedEventId: EVENT.FOCUS_CHANGED,
    IUIA().UIA_dll.UIA_HostedFragmentRootsInvalidatedEventId: EVENT.HOSTED_FRAGMENT_ROOTS_INVALIDATED,
    IUIA().UIA_dll.UIA_InputDiscardedEventId: EVENT.INPUT_DISCARDED,
    IUIA().UIA_dll.UIA_InputReachedOtherElementEventId: EVENT.INPUT_REACHED_OTHER_ELEMENT,
    IUIA().UIA_dll.UIA_InputReachedTargetEventId: EVENT.INPUT_REACHED_TARGET,
    IUIA().UIA_dll.UIA_Invoke_InvokedEventId: EVENT.INVOKED,
    IUIA().UIA_dll.UIA_LayoutInvalidatedEventId: EVENT.LAYOUT_INVALIDATED,
    IUIA().UIA_dll.UIA_LiveRegionChangedEventId: EVENT.LIVE_REGION_CHANGED,
    IUIA().UIA_dll.UIA_MenuClosedEventId: EVENT.MENU_CLOSED,
    IUIA().UIA_dll.UIA_MenuModeEndEventId: EVENT.MENU_END,
    IUIA().UIA_dll.UIA_MenuOpenedEventId: EVENT.MENU_OPENED,
    IUIA().UIA_dll.UIA_MenuModeStartEventId: EVENT.MENU_START,
    IUIA().UIA_dll.UIA_AutomationPropertyChangedEventId: EVENT.PROPERTY_CHANGED,
    IUIA().UIA_dll.UIA_SelectionItem_ElementAddedToSelectionEventId: EVENT.SELECTION_ELEMENT_ADDED,
    IUIA().UIA_dll.UIA_SelectionItem_ElementRemovedFromSelectionEventId: EVENT.SELECTION_ELEMENT_REMOVED,
    IUIA().UIA_dll.UIA_SelectionItem_ElementSelectedEventId: EVENT.SELECTION_ELEMENT_SELECTED,
    IUIA().UIA_dll.UIA_Selection_InvalidatedEventId: EVENT.SELECTION_INVALIDATED,
    IUIA().UIA_dll.UIA_StructureChangedEventId: EVENT.STRUCTURE_CHANGED,
    IUIA().UIA_dll.UIA_SystemAlertEventId: EVENT.SYSTEM_ALERT,
    IUIA().UIA_dll.UIA_Text_TextChangedEventId: EVENT.TEXT_CHANGED,
    IUIA().UIA_dll.UIA_Text_TextSelectionChangedEventId: EVENT.TEXT_SELECTION_CHANGED,
    IUIA().UIA_dll.UIA_ToolTipClosedEventId: EVENT.TOOLTIP_CLOSED,
    IUIA().UIA_dll.UIA_ToolTipOpenedEventId: EVENT.TOOLTIP_OPENED,
    IUIA().UIA_dll.UIA_Window_WindowClosedEventId: EVENT.WINDOW_CLOSED,
    IUIA().UIA_dll.UIA_Window_WindowOpenedEventId: EVENT.WINDOW_OPENED
}

PROPERTY_ID_TO_NAME_MAP = {
    IUIA().UIA_dll.UIA_AcceleratorKeyPropertyId: PROPERTY.ACCELERATOR_KEY,
    IUIA().UIA_dll.UIA_AccessKeyPropertyId: PROPERTY.ACCESS_KEY,
    IUIA().UIA_dll.UIA_AnnotationAnnotationTypeIdPropertyId: PROPERTY.ANNOTATION_TYPE_ID,
    IUIA().UIA_dll.UIA_AnnotationAnnotationTypeNamePropertyId: PROPERTY.ANNOTATION_TYPE_NAME,
    IUIA().UIA_dll.UIA_AnnotationAuthorPropertyId: PROPERTY.ANNOTATION_AUTHOR,
    IUIA().UIA_dll.UIA_AnnotationDateTimePropertyId: PROPERTY.ANNOTATION_DATE_TIME,
    IUIA().UIA_dll.UIA_AnnotationTargetPropertyId: PROPERTY.ANNOTATION_TARGET,
    IUIA().UIA_dll.UIA_AriaPropertiesPropertyId: PROPERTY.ARIA_PROPERTIES,
    IUIA().UIA_dll.UIA_AriaRolePropertyId: PROPERTY.ARIA_ROLE,
    IUIA().UIA_dll.UIA_AutomationIdPropertyId: PROPERTY.AUTOMATION_ID,
    IUIA().UIA_dll.UIA_BoundingRectanglePropertyId: PROPERTY.BOUNDING_RECTANGLE,
    IUIA().UIA_dll.UIA_ClassNamePropertyId: PROPERTY.CLASS_NAME,
    IUIA().UIA_dll.UIA_ClickablePointPropertyId: PROPERTY.CLICKABLE_POINT,
    IUIA().UIA_dll.UIA_ControlTypePropertyId: PROPERTY.CONTROL_TYPE,
    IUIA().UIA_dll.UIA_ControllerForPropertyId: PROPERTY.CONTROLLER_FOR,
    IUIA().UIA_dll.UIA_CulturePropertyId: PROPERTY.CULTURE,
    IUIA().UIA_dll.UIA_DescribedByPropertyId: PROPERTY.DESCRIBED_BY,
    IUIA().UIA_dll.UIA_DockDockPositionPropertyId: PROPERTY.DOCK_POSITION,
    IUIA().UIA_dll.UIA_DragDropEffectPropertyId: PROPERTY.DRAG_DROP_EFFECT,
    IUIA().UIA_dll.UIA_DragDropEffectsPropertyId: PROPERTY.DRAG_DROP_EFFECTS,
    IUIA().UIA_dll.UIA_DragGrabbedItemsPropertyId: PROPERTY.DRAG_GRABBED_ITEMS,
    IUIA().UIA_dll.UIA_DragIsGrabbedPropertyId: PROPERTY.DRAG_IS_GRABBED,
    IUIA().UIA_dll.UIA_DropTargetDropTargetEffectPropertyId: PROPERTY.DROP_TARGET_EFFECT,
    IUIA().UIA_dll.UIA_DropTargetDropTargetEffectsPropertyId: PROPERTY.DROP_TARGET_EFFECTS,
    IUIA().UIA_dll.UIA_ExpandCollapseExpandCollapseStatePropertyId: PROPERTY.EXPAND_COLLAPSE_STATE,
    IUIA().UIA_dll.UIA_FlowsFromPropertyId: PROPERTY.FLOWS_FROM,
    IUIA().UIA_dll.UIA_FlowsToPropertyId: PROPERTY.FLOWS_TO,
    IUIA().UIA_dll.UIA_FrameworkIdPropertyId: PROPERTY.FRAMEWORK_ID,
    IUIA().UIA_dll.UIA_GridColumnCountPropertyId: PROPERTY.GRID_COLUMN_COUNT,
    IUIA().UIA_dll.UIA_GridItemColumnPropertyId: PROPERTY.GRID_ITEM_COLUMN,
    IUIA().UIA_dll.UIA_GridItemColumnSpanPropertyId: PROPERTY.GRID_ITEM_COLUMN_SPAN,
    IUIA().UIA_dll.UIA_GridItemContainingGridPropertyId: PROPERTY.GRID_ITEM_CONTAINING_GRID,
    IUIA().UIA_dll.UIA_GridItemRowPropertyId: PROPERTY.GRID_ITEM_ROW,
    IUIA().UIA_dll.UIA_GridItemRowSpanPropertyId: PROPERTY.GRID_ITEM_ROW_SPAN,
    IUIA().UIA_dll.UIA_GridRowCountPropertyId: PROPERTY.GRID_ROW_COUNT,
    IUIA().UIA_dll.UIA_HasKeyboardFocusPropertyId: PROPERTY.HAS_KEYBOARD_FOCUS,
    IUIA().UIA_dll.UIA_HelpTextPropertyId: PROPERTY.HELP_TEXT,
    IUIA().UIA_dll.UIA_IsAnnotationPatternAvailablePropertyId: PROPERTY.IS_ANNOTATION_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsContentElementPropertyId: PROPERTY.IS_CONTENT_ELEMENT,
    IUIA().UIA_dll.UIA_IsControlElementPropertyId: PROPERTY.IS_CONTROL_ELEMENT,
    IUIA().UIA_dll.UIA_IsDataValidForFormPropertyId: PROPERTY.IS_DATA_VALID_FOR_FORM,
    IUIA().UIA_dll.UIA_IsDockPatternAvailablePropertyId: PROPERTY.IS_DOCK_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsDragPatternAvailablePropertyId: PROPERTY.IS_DRAG_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsDropTargetPatternAvailablePropertyId: PROPERTY.IS_DROP_TARGET_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsEnabledPropertyId: PROPERTY.IS_ENABLED,
    IUIA().UIA_dll.UIA_IsExpandCollapsePatternAvailablePropertyId: PROPERTY.IS_EXPAND_COLLAPSE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsGridItemPatternAvailablePropertyId: PROPERTY.IS_GRID_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsGridPatternAvailablePropertyId: PROPERTY.IS_GRID_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsInvokePatternAvailablePropertyId: PROPERTY.IS_INVOKE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsItemContainerPatternAvailablePropertyId: PROPERTY.IS_ITEM_CONTAINER_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsKeyboardFocusablePropertyId: PROPERTY.IS_KEYBOARD_FOCUSABLE,
    IUIA().UIA_dll.UIA_IsLegacyIAccessiblePatternAvailablePropertyId: PROPERTY.IS_LEGACY_I_ACCESSIBLE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsMultipleViewPatternAvailablePropertyId: PROPERTY.IS_MULTIPLE_VIEW_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsObjectModelPatternAvailablePropertyId: PROPERTY.IS_OBJECT_MODEL_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsOffscreenPropertyId: PROPERTY.IS_OFFSCREEN,
    IUIA().UIA_dll.UIA_IsPasswordPropertyId: PROPERTY.IS_PASSWORD,
    IUIA().UIA_dll.UIA_IsPeripheralPropertyId: PROPERTY.IS_PERIPHERAL,
    IUIA().UIA_dll.UIA_IsRangeValuePatternAvailablePropertyId: PROPERTY.IS_RANGE_VALUE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsRequiredForFormPropertyId: PROPERTY.IS_REQUIRED_FOR_FORM,
    IUIA().UIA_dll.UIA_IsScrollItemPatternAvailablePropertyId: PROPERTY.IS_SCROLL_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsScrollPatternAvailablePropertyId: PROPERTY.IS_SCROLL_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsSelectionItemPatternAvailablePropertyId: PROPERTY.IS_SELECTION_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsSelectionPatternAvailablePropertyId: PROPERTY.IS_SELECTION_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsSpreadsheetItemPatternAvailablePropertyId: PROPERTY.IS_SPREADSHEET_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsSpreadsheetPatternAvailablePropertyId: PROPERTY.IS_SPREADSHEET_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsStylesPatternAvailablePropertyId: PROPERTY.IS_STYLES_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsSynchronizedInputPatternAvailablePropertyId: PROPERTY.IS_SYNCHRONIZED_INPUT_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTableItemPatternAvailablePropertyId: PROPERTY.IS_TABLE_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTablePatternAvailablePropertyId: PROPERTY.IS_TABLE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTextChildPatternAvailablePropertyId: PROPERTY.IS_TEXT_CHILD_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTextEditPatternAvailablePropertyId: PROPERTY.IS_TEXT_EDIT_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTextPattern2AvailablePropertyId: PROPERTY.IS_TEXT_PATTERN2_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTextPatternAvailablePropertyId: PROPERTY.IS_TEXT_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTogglePatternAvailablePropertyId: PROPERTY.IS_TOGGLE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTransformPattern2AvailablePropertyId: PROPERTY.IS_TRANSFORM_PATTERN2_AVAILABLE,
    IUIA().UIA_dll.UIA_IsTransformPatternAvailablePropertyId: PROPERTY.IS_TRANSFORM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsValuePatternAvailablePropertyId: PROPERTY.IS_VALUE_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsVirtualizedItemPatternAvailablePropertyId: PROPERTY.IS_VIRTUALIZED_ITEM_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_IsWindowPatternAvailablePropertyId: PROPERTY.IS_WINDOW_PATTERN_AVAILABLE,
    IUIA().UIA_dll.UIA_ItemStatusPropertyId: PROPERTY.ITEM_STATUS,
    IUIA().UIA_dll.UIA_ItemTypePropertyId: PROPERTY.ITEM_TYPE,
    IUIA().UIA_dll.UIA_LabeledByPropertyId: PROPERTY.LABELED_BY,
    IUIA().UIA_dll.UIA_LegacyIAccessibleChildIdPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_CHILD_ID,
    IUIA().UIA_dll.UIA_LegacyIAccessibleDefaultActionPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_DEFAULT_ACTION,
    IUIA().UIA_dll.UIA_LegacyIAccessibleDescriptionPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_DESCRIPTION,
    IUIA().UIA_dll.UIA_LegacyIAccessibleHelpPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_HELP,
    IUIA().UIA_dll.UIA_LegacyIAccessibleKeyboardShortcutPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_KEYBOARD_SHORTCUT,
    IUIA().UIA_dll.UIA_LegacyIAccessibleNamePropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_NAME,
    IUIA().UIA_dll.UIA_LegacyIAccessibleRolePropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_ROLE,
    IUIA().UIA_dll.UIA_LegacyIAccessibleSelectionPropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_SELECTION,
    IUIA().UIA_dll.UIA_LegacyIAccessibleStatePropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_STATE,
    IUIA().UIA_dll.UIA_LegacyIAccessibleValuePropertyId: PROPERTY.LEGACY_I_ACCESSIBLE_VALUE,
    IUIA().UIA_dll.UIA_LiveSettingPropertyId: PROPERTY.LIVE_SETTING,
    IUIA().UIA_dll.UIA_LocalizedControlTypePropertyId: PROPERTY.LOCALIZED_CONTROL_TYPE,
    IUIA().UIA_dll.UIA_MultipleViewCurrentViewPropertyId: PROPERTY.MULTIPLE_VIEW_CURRENT_VIEW,
    IUIA().UIA_dll.UIA_MultipleViewSupportedViewsPropertyId: PROPERTY.MULTIPLE_VIEW_SUPPORTED_VIEWS,
    IUIA().UIA_dll.UIA_NamePropertyId: PROPERTY.NAME,
    IUIA().UIA_dll.UIA_NativeWindowHandlePropertyId: PROPERTY.NATIVE_WINDOW_HANDLE,
    IUIA().UIA_dll.UIA_OptimizeForVisualContentPropertyId: PROPERTY.OPTIMIZE_FOR_VISUAL_CONTENT,
    IUIA().UIA_dll.UIA_OrientationPropertyId: PROPERTY.ORIENTATION,
    IUIA().UIA_dll.UIA_ProcessIdPropertyId: PROPERTY.PROCESS_ID,
    IUIA().UIA_dll.UIA_ProviderDescriptionPropertyId: PROPERTY.PROVIDER_DESCRIPTION,
    IUIA().UIA_dll.UIA_RangeValueIsReadOnlyPropertyId: PROPERTY.RANGE_VALUE_IS_READ_ONLY,
    IUIA().UIA_dll.UIA_RangeValueLargeChangePropertyId: PROPERTY.RANGE_VALUE_LARGE_CHANGE,
    IUIA().UIA_dll.UIA_RangeValueMaximumPropertyId: PROPERTY.RANGE_VALUE_MAXIMUM,
    IUIA().UIA_dll.UIA_RangeValueMinimumPropertyId: PROPERTY.RANGE_VALUE_MINIMUM,
    IUIA().UIA_dll.UIA_RangeValueSmallChangePropertyId: PROPERTY.RANGE_VALUE_SMALL_CHANGE,
    IUIA().UIA_dll.UIA_RangeValueValuePropertyId: PROPERTY.RANGE_VALUE_VALUE,
    IUIA().UIA_dll.UIA_RuntimeIdPropertyId: PROPERTY.RUNTIME_ID,
    IUIA().UIA_dll.UIA_ScrollHorizontalScrollPercentPropertyId: PROPERTY.SCROLL_HORIZONTAL_SCROLL_PERCENT,
    IUIA().UIA_dll.UIA_ScrollHorizontalViewSizePropertyId: PROPERTY.SCROLL_HORIZONTAL_VIEW_SIZE,
    IUIA().UIA_dll.UIA_ScrollHorizontallyScrollablePropertyId: PROPERTY.SCROLL_HORIZONTALLY_SCROLLABLE,
    IUIA().UIA_dll.UIA_ScrollVerticalScrollPercentPropertyId: PROPERTY.SCROLL_VERTICAL_SCROLL_PERCENT,
    IUIA().UIA_dll.UIA_ScrollVerticalViewSizePropertyId: PROPERTY.SCROLL_VERTICAL_VIEW_SIZE,
    IUIA().UIA_dll.UIA_ScrollVerticallyScrollablePropertyId: PROPERTY.SCROLL_VERTICALLY_SCROLLABLE,
    IUIA().UIA_dll.UIA_SelectionCanSelectMultiplePropertyId: PROPERTY.SELECTION_CAN_SELECT_MULTIPLE,
    IUIA().UIA_dll.UIA_SelectionIsSelectionRequiredPropertyId: PROPERTY.SELECTION_IS_SELECTION_REQUIRED,
    IUIA().UIA_dll.UIA_SelectionItemIsSelectedPropertyId: PROPERTY.SELECTION_ITEM_IS_SELECTED,
    IUIA().UIA_dll.UIA_SelectionItemSelectionContainerPropertyId: PROPERTY.SELECTION_ITEM_SELECTION_CONTAINER,
    IUIA().UIA_dll.UIA_SelectionSelectionPropertyId: PROPERTY.SELECTION_SELECTION,
    IUIA().UIA_dll.UIA_SpreadsheetItemAnnotationObjectsPropertyId: PROPERTY.SPREADSHEET_ITEM_ANNOTATION_OBJECTS,
    IUIA().UIA_dll.UIA_SpreadsheetItemAnnotationTypesPropertyId: PROPERTY.SPREADSHEET_ITEM_ANNOTATION_TYPES,
    IUIA().UIA_dll.UIA_SpreadsheetItemFormulaPropertyId: PROPERTY.SPREADSHEET_ITEM_FORMULA,
    IUIA().UIA_dll.UIA_StylesExtendedPropertiesPropertyId: PROPERTY.STYLES_EXTENDED_PROPERTIES,
    IUIA().UIA_dll.UIA_StylesFillColorPropertyId: PROPERTY.STYLES_FILL_COLOR,
    IUIA().UIA_dll.UIA_StylesFillPatternColorPropertyId: PROPERTY.STYLES_FILL_PATTERN_COLOR,
    IUIA().UIA_dll.UIA_StylesFillPatternStylePropertyId: PROPERTY.STYLES_FILL_PATTERN_STYLE,
    IUIA().UIA_dll.UIA_StylesShapePropertyId: PROPERTY.STYLES_SHAPE,
    IUIA().UIA_dll.UIA_StylesStyleIdPropertyId: PROPERTY.STYLES_STYLE_ID,
    IUIA().UIA_dll.UIA_StylesStyleNamePropertyId: PROPERTY.STYLES_STYLE_NAME,
    IUIA().UIA_dll.UIA_TableColumnHeadersPropertyId: PROPERTY.TABLE_COLUMN_HEADERS,
    IUIA().UIA_dll.UIA_TableItemColumnHeaderItemsPropertyId: PROPERTY.TABLE_ITEM_COLUMN_HEADER_ITEMS,
    IUIA().UIA_dll.UIA_TableItemRowHeaderItemsPropertyId: PROPERTY.TABLE_ITEM_ROW_HEADER_ITEMS,
    IUIA().UIA_dll.UIA_TableRowHeadersPropertyId: PROPERTY.TABLE_ROW_HEADERS,
    IUIA().UIA_dll.UIA_TableRowOrColumnMajorPropertyId: PROPERTY.TABLE_ROW_OR_COLUMN_MAJOR,
    IUIA().UIA_dll.UIA_ToggleToggleStatePropertyId: PROPERTY.TOGGLE_STATE,
    IUIA().UIA_dll.UIA_Transform2CanZoomPropertyId: PROPERTY.TRANSFORM2_CAN_ZOOM,
    IUIA().UIA_dll.UIA_Transform2ZoomLevelPropertyId: PROPERTY.TRANSFORM2_ZOOM_LEVEL,
    IUIA().UIA_dll.UIA_Transform2ZoomMaximumPropertyId: PROPERTY.TRANSFORM2_ZOOM_MAXIMUM,
    IUIA().UIA_dll.UIA_Transform2ZoomMinimumPropertyId: PROPERTY.TRANSFORM2_ZOOM_MINIMUM,
    IUIA().UIA_dll.UIA_TransformCanMovePropertyId: PROPERTY.TRANSFORM_CAN_MOVE,
    IUIA().UIA_dll.UIA_TransformCanResizePropertyId: PROPERTY.TRANSFORM_CAN_RESIZE,
    IUIA().UIA_dll.UIA_TransformCanRotatePropertyId: PROPERTY.TRANSFORM_CAN_ROTATE,
    IUIA().UIA_dll.UIA_ValueIsReadOnlyPropertyId: PROPERTY.VALUE_IS_READ_ONLY,
    IUIA().UIA_dll.UIA_ValueValuePropertyId: PROPERTY.VALUE_VALUE,
    IUIA().UIA_dll.UIA_WindowCanMaximizePropertyId: PROPERTY.WINDOW_CAN_MAXIMIZE,
    IUIA().UIA_dll.UIA_WindowCanMinimizePropertyId: PROPERTY.WINDOW_CAN_MINIMIZE,
    IUIA().UIA_dll.UIA_WindowIsModalPropertyId: PROPERTY.WINDOW_IS_MODAL,
    IUIA().UIA_dll.UIA_WindowIsTopmostPropertyId: PROPERTY.WINDOW_IS_TOPMOST,
    IUIA().UIA_dll.UIA_WindowWindowInteractionStatePropertyId: PROPERTY.WINDOW_WINDOW_INTERACTION_STATE,
    IUIA().UIA_dll.UIA_WindowWindowVisualStatePropertyId: PROPERTY.WINDOW_WINDOW_VISUAL_STATE
}

if hasattr(IUIA().UIA_dll, "UIA_AnnotationObjectsPropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_AnnotationObjectsPropertyId] = PROPERTY.ANNOTATION_OBJECTS
if hasattr(IUIA().UIA_dll, "UIA_AnnotationTypesPropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_AnnotationTypesPropertyId] = PROPERTY.ANNOTATION_TYPES
if hasattr(IUIA().UIA_dll, 'UIA_FullDescriptionPropertyId'):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_FullDescriptionPropertyId] = PROPERTY.FULL_DESCRIPTION
if hasattr(IUIA().UIA_dll, "UIA_IsCustomNavigationPatternAvailablePropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_IsCustomNavigationPatternAvailablePropertyId] = \
        PROPERTY.IS_CUSTOM_NAVIGATION_PATTERN_AVAILABLE
if hasattr(IUIA().UIA_dll, "UIA_LandmarkTypePropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_LandmarkTypePropertyId] = PROPERTY.LANDMARK_TYPE
if hasattr(IUIA().UIA_dll, "UIA_LevelPropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_LevelPropertyId] = PROPERTY.LEVEL
if hasattr(IUIA().UIA_dll, "UIA_LocalizedLandmarkTypePropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_LocalizedLandmarkTypePropertyId] = PROPERTY.LOCALIZED_LANDMARK_TYPE
if hasattr(IUIA().UIA_dll, "UIA_PositionInSetPropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_PositionInSetPropertyId] = PROPERTY.POSITION_IN_SET
if hasattr(IUIA().UIA_dll, "UIA_SizeOfSetPropertyId"):
    PROPERTY_ID_TO_NAME_MAP[IUIA().UIA_dll.UIA_SizeOfSetPropertyId] = PROPERTY.SIZE_OF_SET

STRUCTURE_CHANGE_TYPE_TO_NAME_MAP = {
    IUIA().UIA_dll.StructureChangeType_ChildAdded: STRUCTURE_EVENT.CHILD_ADDED,
    IUIA().UIA_dll.StructureChangeType_ChildRemoved: STRUCTURE_EVENT.CHILD_REMOVED,
    IUIA().UIA_dll.StructureChangeType_ChildrenInvalidated: STRUCTURE_EVENT.CHILDREN_INVALIDATED,
    IUIA().UIA_dll.StructureChangeType_ChildrenBulkAdded: STRUCTURE_EVENT.CHILDREN_ADDED,
    IUIA().UIA_dll.StructureChangeType_ChildrenBulkRemoved: STRUCTURE_EVENT.CHILDREN_REMOVED,
    IUIA().UIA_dll.StructureChangeType_ChildrenReordered: STRUCTURE_EVENT.CHILDREN_REORDERED
}


class StructureEvent(ApplicationEvent):
    def __init__(self, sender, change_type, runtime_id):
        super(StructureEvent, self).__init__(EVENT.STRUCTURE_CHANGED, sender)
        self.change_type = change_type
        self.runtime_id = runtime_id

    def __repr__(self):
        """Return a representation of the object as a string"""
        return "<StructureEvent - '{}' from {}>".format(self.change_type, self.sender)
