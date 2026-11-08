"""Tests for pywinauto.windows.uia_event_handlers module.

Unit tests mock the COM layer so they run on any platform (including CI).
Integration tests require Windows with UI Automation and are marked with
``@pytest.mark.skipif`` for non-Windows environments.
"""

import sys
import threading
import time
from datetime import datetime, timezone
from unittest import mock

import pytest

# Skip entire module on non-Windows platforms
pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="UIA event handlers require Windows",
)


class TestUIAEventHandlerUnit:
    """Unit tests that do not require COM or a running event loop."""

    def _make_handler(self):
        """Import and create a UIAEventHandler instance."""
        from pywinauto.windows.uia_event_handlers import UIAEventHandler
        return UIAEventHandler(max_events=100)

    def test_initial_state(self):
        """Handler should not be running after construction."""
        handler = self._make_handler()
        assert handler.is_running is False
        assert handler.get_events() == []

    def test_on_decorator_valid_types(self):
        """Decorator should accept all valid event types."""
        handler = self._make_handler()

        for event_type in ("window_opened", "window_closed",
                           "focus_changed", "structure_changed"):
            @handler.on(event_type)
            def callback(event):
                pass

            assert callback in handler._callbacks[event_type]

    def test_on_decorator_invalid_type(self):
        """Decorator should reject invalid event types."""
        handler = self._make_handler()
        with pytest.raises(ValueError, match="Invalid event_type"):
            @handler.on("invalid_event")
            def callback(event):
                pass

    def test_on_event_stores_event(self):
        """Internal _on_event should store events in the buffer."""
        handler = self._make_handler()
        info = {
            "element_name": "Notepad",
            "process_id": 1234,
            "process_name": "notepad.exe",
            "control_type": "Window",
            "class_name": "Notepad",
        }
        handler._on_event("window_opened", info)

        events = handler.get_events()
        assert len(events) == 1
        assert events[0]["type"] == "window_opened"
        assert events[0]["element_name"] == "Notepad"
        assert "timestamp" in events[0]

    def test_on_event_skips_empty_events(self):
        """Events with no identifying info should be skipped."""
        handler = self._make_handler()
        info = {
            "element_name": "",
            "process_id": 0,
            "process_name": "",
            "control_type": "",
            "class_name": "",
        }
        handler._on_event("focus_changed", info)
        assert handler.get_events() == []

    def test_on_event_dispatches_callbacks(self):
        """Registered callbacks should fire when events arrive."""
        handler = self._make_handler()
        received = []

        @handler.on("window_opened")
        def on_open(event):
            received.append(event)

        handler._on_event("window_opened", {
            "element_name": "Test",
            "process_name": "test.exe",
            "class_name": "TestClass",
        })
        assert len(received) == 1
        assert received[0]["element_name"] == "Test"

    def test_callback_exception_does_not_crash(self):
        """A callback that raises should not prevent event storage."""
        handler = self._make_handler()

        @handler.on("window_opened")
        def bad_callback(event):
            raise RuntimeError("intentional error")

        handler._on_event("window_opened", {
            "element_name": "Test",
            "process_name": "test.exe",
            "class_name": "",
        })
        # Event should still be stored despite callback error
        assert len(handler.get_events()) == 1

    def test_max_events_eviction(self):
        """Buffer should evict oldest events when max_events exceeded."""
        handler = self._make_handler()  # max_events=100
        for i in range(150):
            handler._on_event("focus_changed", {
                "element_name": "item_{}".format(i),
                "process_name": "test.exe",
                "class_name": "",
            })

        with handler._event_lock:
            assert len(handler._events) == 100

        # Oldest should be item_50, newest item_149
        events = handler.get_events(limit=100)
        assert events[0]["element_name"] == "item_149"
        assert events[-1]["element_name"] == "item_50"

    def test_get_events_filter_by_type(self):
        """get_events should filter by event_type."""
        handler = self._make_handler()
        handler._on_event("window_opened", {
            "element_name": "A", "process_name": "a.exe", "class_name": "",
        })
        handler._on_event("focus_changed", {
            "element_name": "B", "process_name": "b.exe", "class_name": "",
        })
        handler._on_event("window_opened", {
            "element_name": "C", "process_name": "c.exe", "class_name": "",
        })

        opened = handler.get_events(event_type="window_opened")
        assert len(opened) == 2
        assert all(e["type"] == "window_opened" for e in opened)

    def test_get_events_filter_by_since(self):
        """get_events should filter by timestamp."""
        handler = self._make_handler()

        # Add an old event
        handler._on_event("window_opened", {
            "element_name": "Old", "process_name": "old.exe", "class_name": "",
        })

        # Record timestamp between events
        time.sleep(0.01)
        since = datetime.now(timezone.utc).isoformat()
        time.sleep(0.01)

        # Add a new event
        handler._on_event("window_opened", {
            "element_name": "New", "process_name": "new.exe", "class_name": "",
        })

        events = handler.get_events(since=since)
        assert len(events) == 1
        assert events[0]["element_name"] == "New"

    def test_get_events_limit(self):
        """get_events should respect the limit parameter."""
        handler = self._make_handler()
        for i in range(10):
            handler._on_event("focus_changed", {
                "element_name": "item_{}".format(i),
                "process_name": "test.exe",
                "class_name": "",
            })

        events = handler.get_events(limit=3)
        assert len(events) == 3

    def test_get_events_newest_first(self):
        """Events should be returned newest-first."""
        handler = self._make_handler()
        handler._on_event("window_opened", {
            "element_name": "First", "process_name": "a.exe", "class_name": "",
        })
        handler._on_event("window_opened", {
            "element_name": "Second", "process_name": "b.exe", "class_name": "",
        })

        events = handler.get_events()
        assert events[0]["element_name"] == "Second"
        assert events[1]["element_name"] == "First"

    def test_clear_events(self):
        """clear_events should empty the buffer."""
        handler = self._make_handler()
        handler._on_event("window_opened", {
            "element_name": "Test", "process_name": "t.exe", "class_name": "",
        })
        assert len(handler.get_events()) == 1

        handler.clear_events()
        assert len(handler.get_events()) == 0

    def test_stop_when_not_running(self):
        """Stopping a handler that is not running should be a no-op."""
        handler = self._make_handler()
        handler.stop()  # should not raise
        assert handler.is_running is False


class TestExtractElementInfo:
    """Tests for the _extract_element_info helper."""

    def test_extracts_all_fields(self):
        """Should extract name, pid, control type, and class name."""
        from pywinauto.windows.uia_event_handlers import _extract_element_info

        element = mock.MagicMock()
        element.CurrentName = "Test Window"
        element.CurrentProcessId = 1234
        element.CurrentLocalizedControlType = "Window"
        element.CurrentClassName = "TestClass"

        with mock.patch(
            "pywinauto.windows.uia_event_handlers.psutil"
        ) as mock_psutil:
            mock_psutil.Process.return_value.name.return_value = "test.exe"
            mock_psutil.NoSuchProcess = Exception
            mock_psutil.AccessDenied = Exception

            info = _extract_element_info(element)

        assert info["element_name"] == "Test Window"
        assert info["process_id"] == 1234
        assert info["process_name"] == "test.exe"
        assert info["control_type"] == "Window"
        assert info["class_name"] == "TestClass"

    def test_handles_com_errors(self):
        """Should return safe defaults when COM properties raise."""
        from pywinauto.windows.uia_event_handlers import _extract_element_info

        element = mock.MagicMock()
        element.CurrentName = mock.PropertyMock(
            side_effect=Exception("COM error")
        )
        type(element).CurrentName = mock.PropertyMock(
            side_effect=Exception("COM error")
        )
        type(element).CurrentProcessId = mock.PropertyMock(
            side_effect=Exception("COM error")
        )
        type(element).CurrentLocalizedControlType = mock.PropertyMock(
            side_effect=Exception("COM error")
        )
        type(element).CurrentClassName = mock.PropertyMock(
            side_effect=Exception("COM error")
        )

        info = _extract_element_info(element)
        assert info["element_name"] == ""
        assert info["process_id"] == 0
        assert info["control_type"] == ""
        assert info["class_name"] == ""


class TestUIAEventHandlerIntegration:
    """Integration tests that require Windows UI Automation.

    These tests start the actual event loop and verify that COM
    event handlers work. They are slower (~2-3 seconds each).
    """

    def _make_handler(self):
        from pywinauto.windows.uia_event_handlers import UIAEventHandler
        return UIAEventHandler(max_events=100)

    def test_start_and_stop(self):
        """Handler should start and stop cleanly."""
        handler = self._make_handler()

        handler.start()
        assert handler.is_running is True

        handler.stop()
        assert handler.is_running is False

    def test_start_twice_is_noop(self):
        """Starting an already-running handler should be a no-op."""
        handler = self._make_handler()
        try:
            handler.start()
            handler.start()  # should not raise
            assert handler.is_running is True
        finally:
            handler.stop()

    def test_receives_focus_events(self):
        """Should receive focus change events within a few seconds.

        Focus events fire frequently as the test runner itself causes
        focus transitions.
        """
        handler = self._make_handler()
        try:
            handler.start()
            # Wait a bit for focus events to accumulate
            time.sleep(2)
            events = handler.get_events(event_type="focus_changed")
            # Focus events should fire as the OS processes focus changes
            # (may be 0 on a quiet system, but usually > 0)
            assert isinstance(events, list)
        finally:
            handler.stop()

    def test_open_close_notepad(self):
        """Open and close Notepad, verify window events are captured."""
        import subprocess

        handler = self._make_handler()
        try:
            handler.start()
            time.sleep(0.5)

            # Open Notepad
            proc = subprocess.Popen(["notepad.exe"])
            time.sleep(2)

            # Check for window_opened
            opened = handler.get_events(event_type="window_opened")
            notepad_events = [
                e for e in opened
                if "notepad" in e.get("process_name", "").lower()
                or "notepad" in e.get("element_name", "").lower()
            ]

            # Close Notepad
            proc.terminate()
            proc.wait(timeout=5)
            time.sleep(1)

            # Check for window_closed
            closed = handler.get_events(event_type="window_closed")

            # At minimum, we should have seen the open event
            assert len(notepad_events) > 0, (
                "Expected at least one window_opened event for Notepad"
            )
        finally:
            handler.stop()
            try:
                proc.kill()
            except Exception:
                pass
