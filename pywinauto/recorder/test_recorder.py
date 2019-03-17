import os
import sys
import codecs
import unittest

# sys.path.append(".")
sys.path.append("../..")

from pywinauto.recorder.recorder_defines import HOOK_KEY_DOWN, HOOK_KEY_UP, HOOK_MOUSE_LEFT_BUTTON, \
    HOOK_MOUSE_RIGHT_BUTTON, HOOK_MOUSE_MIDDLE_BUTTON, EVENT, PROPERTY, STRUCTURE_EVENT, RecorderEvent, HookEvent, \
    RecorderMouseEvent, RecorderKeyboardEvent, ApplicationEvent, PropertyEvent, EventPattern, _is_identifier, \
    get_window_access_name_str


class EventPatternTestCases(unittest.TestCase):
    """Unit tests for the EventPattern class"""

    def setUp(self):
        self.log_events = EventPattern(
            hook_event=RecorderMouseEvent(current_key=HOOK_MOUSE_LEFT_BUTTON, event_type=HOOK_KEY_DOWN),
            app_events=(ApplicationEvent(name=EVENT.INVOKED),
                        PropertyEvent(property_name=PROPERTY.SELECTION_ITEM_IS_SELECTED),
                        ApplicationEvent(name=EVENT.SELECTION_ELEMENT_SELECTED),
                        PropertyEvent(property_name=PROPERTY.NAME)))

    def tearDown(self):
        pass

    def compare_patterns(self, pattern1, pattern2):
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
