import sys
import time
import unittest

from six import PY3

if PY3:
    import unittest.mock as mock
else:
    import mock

sys.path.append(".")

import pywinauto.recorder.uia.uia_recorder
import pywinauto.windows.win32_hooks

from pywinauto.application import Application
from pywinauto.recorder.base_recorder import BaseRecorder
from pywinauto.recorder.recorder_defines import HOOK_KEY_DOWN, HOOK_KEY_UP, HOOK_MOUSE_LEFT_BUTTON, \
    HOOK_MOUSE_RIGHT_BUTTON, HOOK_MOUSE_MIDDLE_BUTTON, EVENT, PROPERTY, STRUCTURE_EVENT, RecorderEvent, \
    RecorderMouseEvent, ApplicationEvent, PropertyEvent, EventPattern, _is_identifier, \
    get_window_access_name_str
from pywinauto.recorder.uia.uia_event_handlers import EventHandler, MenuOpenedHandler, MenuClosedHandler, \
    ExpandCollapseHandler, SelectionChangedHandler, MouseClickHandler, UIA_EVENT_PATTERN_MAP
from pywinauto.recorder.uia.uia_recorder import UiaRecorder
from pywinauto.windows.uia_defines import IUIA, window_visual_state_normal, expand_state_expanded
from pywinauto.windows.win32structures import RECT


class EventPatternTestCases(unittest.TestCase):

    """Unit tests for the EventPattern class"""

    def setUp(self):
        self.log_events = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=(ApplicationEvent(name=EVENT.INVOKED),
                        PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                        ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED),
                        PropertyEvent(property_name=PROPERTY.NAME)))

    @classmethod
    def compare_patterns(cls, pattern1, pattern2):
        if str(pattern1.hook_event) != str(pattern2.hook_event):
            return False

        if bool(pattern1.app_events) != bool(pattern2.app_events):
            return False

        if pattern1.app_events is not None:
            if len(pattern1.app_events) != len(pattern2.app_events):
                return False

            for e1, e2 in zip(pattern1.app_events, pattern2.app_events):
                if str(e1) != str(e2):
                    return False

        return True

    def test_is_identifier(self):
        """Test _is_identifier() function can detect possible python variable names"""
        correct_var_name = "variable123"
        incorrect_var_name = "var with spaces"

        self.assertTrue(_is_identifier(correct_var_name))
        self.assertFalse(_is_identifier(incorrect_var_name))

    def test_get_window_access_name_str_key_only_false(self):
        """Test get_window_access_name_str() function returns correct item access with key_only=False parameter"""
        correct_var_name = "WindowName"
        expected_name = ".WindowName"

        self.assertEqual(expected_name, get_window_access_name_str(correct_var_name, key_only=False))

        incorrect_var_name = "Edit Button 1"
        expected_name = "[u'Edit Button 1']"

        self.assertEqual(expected_name, get_window_access_name_str(incorrect_var_name, key_only=False))

    def test_get_window_access_name_str_key_only_true(self):
        """Test get_window_access_name_str() function returns correct item access with key_only=True parameter"""
        name = "OKButton"
        expected_name = "[u'OKButton']"

        self.assertEqual(expected_name, get_window_access_name_str(name, key_only=True))

    def test_subpattern_single_hook_event(self):
        """Test EventPattern.get_subpattern() detects subpattern with only 1 Hook event"""
        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=None)

        self.assertTrue(self.compare_patterns(pattern, self.log_events.get_subpattern(pattern)))

    def test_subpattern_the_whole_log(self):
        """Test EventPattern.get_subpattern() detects subpattern when pattern and log are the same"""
        pattern = self.log_events

        self.assertTrue(self.compare_patterns(pattern, self.log_events.get_subpattern(pattern)))

    def test_subpattern_consecutive_app_events(self):
        """Test EventPattern.get_subpattern() detects subpattern when pattern and log are the same"""
        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=(PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                        ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED)))

        self.assertTrue(self.compare_patterns(pattern, self.log_events.get_subpattern(pattern)))

    def test_subpattern_non_consecutive_app_events(self):
        """Test EventPattern.get_subpattern() detects subpattern when pattern and log are the same"""
        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=(ApplicationEvent(name=EVENT.INVOKED),
                        PropertyEvent(property_name=PROPERTY.NAME)))

        self.assertTrue(self.compare_patterns(pattern, self.log_events.get_subpattern(pattern)))

    def test_not_subpattern_diff_hook_event(self):
        """Test EventPattern.get_subpattern() fails to detect subpattern when pattern has different hook event"""
        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_UP),
            app_events=None)

        self.assertTrue(self.log_events.get_subpattern(pattern) is None)

    def test_not_subpattern_diff_app_event(self):
        """Test EventPattern.get_subpattern() fails to detect subpattern when pattern has different application event"""
        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_UP),
            app_events=ApplicationEvent(name=EVENT.MENU_START))

        self.assertTrue(self.log_events.get_subpattern(pattern) is None)

    def test_not_subpattern_extra_app_event(self):
        """Test EventPattern.get_subpattern() fails to detect subpattern when pattern has extra application event"""
        pattern = EventPattern(
            hook_event=self.log_events.hook_event,
            app_events=[e for e in self.log_events.app_events] + [ApplicationEvent(name=EVENT.MENU_CLOSED)])

        self.assertTrue(self.log_events.get_subpattern(pattern) is None)

    def test_not_subpattern_app_events_diff_order(self):
        """Test EventPattern.get_subpattern() fails to detect subpattern when pattern's application events are in the
        different order compared to the log_events'.
        """

        pattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=(ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED),
                        PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED)))

        self.assertTrue(self.log_events.get_subpattern(pattern) is None)


class UIAEventHandlersTestCases(unittest.TestCase):

    """Unit tests for the Event Handlers"""

    PREFERRED_NAME = "PreferredName"
    TEXT_NAME = "TextName"

    def setUp(self):
        # RecorderConfig
        config_mock = mock.Mock(key_only=True, scale_click=False)

        # ControlNames
        get_preferred_name_mock = mock.Mock(return_value=self.PREFERRED_NAME)
        ctrl_names_mock = mock.Mock(get_preferred_name=get_preferred_name_mock, text_names=[self.TEXT_NAME])

        # BaseWrapper
        wrapper_mock = mock.Mock(element_info="ElementInfo")

        # ControlTreeNode
        ctrl_tree_node_mock = mock.Mock(names=ctrl_names_mock, wrapper=wrapper_mock, rect=RECT(0, 0, 10, 10))
        ctrl_tree_node_mock.parent = ctrl_tree_node_mock

        # List if ControlTreeNode
        subtree_mock = mock.MagicMock()
        subtree_mock.__getitem__.return_value = ctrl_tree_node_mock
        subtree_mock.__iter__.return_value = [ctrl_tree_node_mock]

        # ControlTree
        ctrl_tree_mock = mock.Mock()
        ctrl_tree_mock.sub_tree_from_node = mock.Mock(spec=["node"], return_value=subtree_mock)
        ctrl_tree_mock.node_from_element_info = mock.Mock(spec=["element_info"], return_value=ctrl_tree_node_mock)

        # BaseRecorder
        recorder_mock = mock.Mock(config=config_mock, control_tree=ctrl_tree_mock)

        # LogParser
        log_parser_mock = mock.Mock(recorder=recorder_mock, menu_sequence=[], text_sequence={})

        # Arguments for EventHandler
        self.subtree = subtree_mock
        self.log_parser = log_parser_mock
        self.subpattern = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=[ApplicationEvent(name=EVENT.DRAG_COMPLETE),
                        PropertyEvent(property_name=PROPERTY.CULTURE)])

    def build_window_access_name(self):
        return u"app[u'{}']".format(self.PREFERRED_NAME)

    def build_item_access_name(self):
        return u"app[u'{}'][u'{}']".format(self.PREFERRED_NAME, self.PREFERRED_NAME)

    def test_get_root_name(self):
        """Test EventHandler.get_root_name() method"""
        handler = EventHandler(self.subtree, self.log_parser, self.subpattern)

        # get_window_access_name_str is called inside
        self.assertEqual("[u'{}']".format(self.PREFERRED_NAME), handler.get_root_name())

    def test_get_item_name(self):
        """Test EventHandler.get_item_name() method"""
        handler = EventHandler(self.subtree, self.log_parser, self.subpattern)

        # get_window_access_name_str is called inside
        self.assertEqual("[u'{}']".format(self.PREFERRED_NAME), handler.get_item_name())

    def test_menu_opened_handler(self):
        """Test MenuOpenedHandler"""
        handler = MenuOpenedHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertTrue(result is None)
        self.assertEqual([self.TEXT_NAME], self.log_parser.menu_sequence)

    def test_menu_closed_handler(self):
        """Test MenuClosedHandler"""
        self.log_parser.menu_sequence = ["MenuItem1", "MenuItem2"]
        handler = MenuClosedHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_window_access_name() + u".menu_select('MenuItem1 -> MenuItem2 -> TextName')\n",
                         result)
        self.assertEqual([], self.log_parser.menu_sequence)

    def test_expand_collapse_handler_expand(self):
        """Test ExpandCollapseHandler, new expand/collapse state = 1"""
        self.subpattern.app_events[0] = PropertyEvent(property_name=PROPERTY.TOGGLE_STATE, new_value=1)
        handler = ExpandCollapseHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_item_access_name() + u".expand()\n", result)

    def test_expand_collapse_handler_collapse(self):
        """Test ExpandCollapseHandler, new expand/collapse state = 0"""
        self.subpattern.app_events[0] = PropertyEvent(property_name=PROPERTY.TOGGLE_STATE, new_value=0)
        handler = ExpandCollapseHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_item_access_name() + u".collapse()\n", result)

    def test_selection_changed_handler_with_sender(self):
        """Test SelectionChangedHandler, parent item is not main window"""
        self.subpattern.app_events[-1] = ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED, sender="ElementInfo")
        handler = SelectionChangedHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_item_access_name() + u".select('{}')\n".format(self.TEXT_NAME), result)

    def test_selection_changed_handler_without_sender(self):
        """Test SelectionChangedHandler, parent item is main window"""
        handler = SelectionChangedHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_item_access_name() + u".select('{}')\n".format(self.TEXT_NAME), result)

    def test_mouse_click_handler_left_no_element(self):
        """Test MouseClickHandler with left mouse click and no detected element"""
        self.subpattern.hook_event = RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN,
                                                        mouse_x=1, mouse_y=2)
        self.subpattern.hook_event.control_tree_node = None
        handler = MouseClickHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(u"pywinauto.mouse.click(button='left', coords=(1, 2))\n", result)

    def test_mouse_click_handler_right_no_element(self):
        """Test MouseClickHandler with right mouse click and no detected element"""
        self.subpattern.hook_event = RecorderMouseEvent(current_key=HOOK_MOUSE_RIGHT_BUTTON, event_type=HOOK_KEY_DOWN,
                                                        mouse_x=3, mouse_y=4)
        self.subpattern.hook_event.control_tree_node = None
        handler = MouseClickHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(u"pywinauto.mouse.click(button='right', coords=(3, 4))\n", result)

    def test_mouse_click_handler_middle_no_element(self):
        """Test MouseClickHandler with middle mouse click and no detected element"""
        self.subpattern.hook_event = RecorderMouseEvent(current_key=HOOK_MOUSE_MIDDLE_BUTTON, event_type=HOOK_KEY_DOWN,
                                                        mouse_x=5, mouse_y=6)
        self.subpattern.hook_event.control_tree_node = None
        handler = MouseClickHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(u"pywinauto.mouse.click(button='wheel', coords=(5, 6))\n", result)

    def test_mouse_click_handler_left_with_element_no_scale(self):
        """Test MouseClickHandler with left click, detected element and scale_click set to False"""
        self.subpattern.hook_event = RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN,
                                                        mouse_x=5, mouse_y=5)
        self.subpattern.hook_event.control_tree_node = self.subtree[0]
        self.log_parser.recorder.config.scale_click = False
        handler = MouseClickHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        self.assertEqual(self.build_item_access_name() + u".click_input(button='left', coords=(5, 5))\n", result)

    def test_mouse_click_handler_left_with_element_scale(self):
        """Test MouseClickHandler with left click, detected element and scale_click set to True"""
        self.subpattern.hook_event = RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN,
                                                        mouse_x=5, mouse_y=5)
        self.subpattern.hook_event.control_tree_node = self.subtree[0]
        self.log_parser.recorder.config.scale_click = True
        handler = MouseClickHandler(self.subtree, self.log_parser, self.subpattern)

        result = handler.run()

        expected = u"# Clicking on object 'PreferredName' with scale (0.5, 0.5)\n" \
                   u"_elem = app[u'PreferredName'][u'PreferredName'].wrapper_object()\n" \
                   u"_rect = _elem.rectangle()\n" \
                   u"_x = int((_rect.right - _rect.left) * 0.5)\n" \
                   u"_y = int((_rect.bottom - _rect.top) * 0.5)\n" \
                   u"_elem.click_input(button='left', coords=(_x, _y))\n"
        self.assertEqual(expected, result)


class BaseRecorderTestCases(unittest.TestCase):

    """Unit tests for the BaseRecorder class"""

    def setUp(self):
        self.app_mock = mock.MagicMock(spec=Application, is_process_running=mock.Mock(return_value=True), process=0,
                                       backend=mock.Mock())
        self.app_mock.backend.name = "uia"

        self.config_mock = mock.Mock(verbose=True)

        self.base_recorder = BaseRecorder(self.app_mock, self.config_mock)

    def tearDown(self):
        self.base_recorder.stop()

    def test_init_without_application(self):
        self.assertRaises(TypeError, BaseRecorder, None, self.config_mock)

    def test_init_with_app_not_running(self):
        self.app_mock.is_process_running.return_value = False

        self.assertRaises(TypeError, BaseRecorder, self.app_mock, self.config_mock)

    def test_init_script_with_process(self):
        self.assertTrue("app = pywinauto.Application(backend='uia').start(r'None')" in self.base_recorder.script)

    def test_init_script_without_process(self):
        self.app_mock.process = mock.Mock(side_effect=KeyError)
        self.base_recorder = BaseRecorder(self.app_mock, None)

        self.assertTrue(
            "app = pywinauto.Application(backend='uia').start(r'INSERT_CMD_HERE')" in self.base_recorder.script)

    def test_add_to_log(self):
        self.base_recorder.add_to_log("1")
        self.base_recorder.add_to_log(2)

        self.assertEqual(self.base_recorder.event_log, ["1", 2])

    def test_clear_log(self):
        self.base_recorder.add_to_log(3.0)
        self.base_recorder.add_to_log(None)

        self.base_recorder.clear_log()

        self.assertEqual(self.base_recorder.event_log, [])

    def test_start(self):
        setup_mock = mock.Mock()
        self.base_recorder._setup = setup_mock

        self.base_recorder.start()
        time.sleep(1)

        self.assertTrue(self.base_recorder.recorder_start_event.is_set())
        self.assertTrue(setup_mock.called)

    def test_stop(self):
        cleanup_mock = mock.Mock()
        self.base_recorder._cleanup = cleanup_mock

        self.base_recorder.start()
        time.sleep(1)
        self.base_recorder.stop()
        time.sleep(1)

        self.assertTrue(self.base_recorder.recorder_stop_event.is_set())
        self.assertTrue(cleanup_mock.called)

    def test_is_active(self):
        self.base_recorder.start()
        time.sleep(1)

        self.assertTrue(self.base_recorder.is_active())

        self.base_recorder.stop()
        time.sleep(1)

        self.assertFalse(self.base_recorder.is_active())

    def test_wait(self):
        self.base_recorder.is_active = mock.Mock(return_value=True)
        self.base_recorder.recorder_thread.join = mock.Mock()

        self.base_recorder.wait()

        self.assertTrue(self.base_recorder.is_active.called)
        self.assertTrue(self.base_recorder.recorder_thread.join.called)

    def test_parse_and_clear_log(self):
        # new_script = self.log_parser.parse_current_log()
        # self.script += new_script
        # self.clear_log()
        self.base_recorder.log_parser = mock.Mock(parse_current_log=mock.Mock(return_value="script_line\n"))
        self.base_recorder.add_to_log("item")
        self.base_recorder.add_to_log(2.0)

        self.base_recorder._parse_and_clear_log()

        self.assertTrue(self.base_recorder.log_parser.parse_current_log.called)
        self.assertEqual(self.base_recorder.script.splitlines()[-1], "script_line")
        self.assertEqual(self.base_recorder.event_log, [])

    def test_event_patterns(self):
        self.assertEqual(self.base_recorder.event_patterns, [])


class UiaRecorderTestCases(unittest.TestCase):

    """Unit tests for the UiaRecorder class"""

    @classmethod
    def setUpClass(cls):
        cls._ignored_events_backup = pywinauto.recorder.uia.uia_recorder._ignored_events[:]

        IUIA().iuia.AddAutomationEventHandler = mock.Mock()
        IUIA().iuia.AddPropertyChangedEventHandler = mock.Mock()
        IUIA().iuia.AddFocusChangedEventHandler = mock.Mock()
        IUIA().iuia.AddStructureChangedEventHandler = mock.Mock()
        IUIA().iuia.RemoveAllEventHandlers = mock.Mock()

        cls.hook_hook_mock = mock.Mock(spec=["keyboard", "mouse"])
        pywinauto.windows.win32_hooks.Hook = mock.Mock(return_value=mock.Mock(hook=cls.hook_hook_mock))

    def setUp(self):
        self.app_mock = mock.MagicMock(spec=Application, is_process_running=mock.Mock(return_value=True), process=0,
                                       backend=mock.Mock())
        self.app_mock.backend.name = "uia"

        self.config_mock = mock.Mock(verbose=True)

        pywinauto.recorder.uia.uia_recorder._ignored_events = self._ignored_events_backup[:]

        self.uia_recorder = UiaRecorder(self.app_mock, self.config_mock, record_props=True, record_focus=False,
                                        record_struct=False)

        IUIA().iuia.AddAutomationEventHandler.reset_mock()
        IUIA().iuia.AddPropertyChangedEventHandler.reset_mock()
        IUIA().iuia.AddFocusChangedEventHandler.reset_mock()
        IUIA().iuia.AddStructureChangedEventHandler.reset_mock()
        IUIA().iuia.RemoveAllEventHandlers.reset_mock()

        self.hook_hook_mock.reset_mock()
        pywinauto.windows.win32_hooks.Hook.reset_mock()

    def tearDown(self):
        self.uia_recorder.stop()

    def test_init_with_record_struct(self):
        self.uia_recorder = UiaRecorder(self.app_mock, self.config_mock, record_struct=True)

        self.assertTrue(IUIA().known_events_ids[IUIA().UIA_dll.UIA_StructureChangedEventId] not in
                        pywinauto.recorder.uia.uia_recorder._ignored_events)

    def test_event_patterns(self):
        self.assertEqual(self.uia_recorder.event_patterns, UIA_EVENT_PATTERN_MAP)

    def test_add_handlers(self):
        self.uia_recorder = UiaRecorder(self.app_mock, self.config_mock, record_props=True, record_focus=True,
                                        record_struct=True)

        self.uia_recorder._add_handlers(None)

        self.assertTrue(IUIA().iuia.AddAutomationEventHandler.called)
        self.assertTrue(IUIA().iuia.AddPropertyChangedEventHandler.called)
        self.assertTrue(IUIA().iuia.AddFocusChangedEventHandler.called)
        self.assertTrue(IUIA().iuia.AddStructureChangedEventHandler.called)

    def test_rebuild_control_tree(self):
        rebuild_mock = mock.Mock()
        self.uia_recorder.control_tree = mock.Mock(rebuild=rebuild_mock)

        self.uia_recorder._rebuild_control_tree()

        self.assertTrue(rebuild_mock.called)

    def test_cleanup(self):
        stop_mock = mock.Mock()
        self.uia_recorder.hook = mock.Mock(stop=stop_mock)

        self.uia_recorder._cleanup()

        self.assertTrue(IUIA().iuia.RemoveAllEventHandlers.called)

    def test_update(self):
        self.uia_recorder.hook = mock.Mock(stop=mock.Mock())
        self.uia_recorder.hook_target = mock.Mock()
        self.uia_recorder.hook_thread = mock.Mock()
        self.uia_recorder.rebuild_tree_thr = mock.Mock()
        self.uia_recorder._add_handlers = mock.Mock(spec=["element"])
        self.uia_recorder._rebuild_control_tree = mock.Mock()

        self.uia_recorder._update(rebuild_tree=True, add_handlers_to="element", log_msg="test_update")

        self.uia_recorder._add_handlers.assert_called_with("element")
        self.uia_recorder._rebuild_control_tree.assert_called()

    def test_hook_target(self):
        self.uia_recorder.hook_target()

        pywinauto.windows.win32_hooks.Hook.assert_called()
        self.hook_hook_mock.assert_called_with(keyboard=True, mouse=True)


if __name__ == "__main__":
    unittest.main()
