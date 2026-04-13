"""UI Automation Event Handlers for pywinauto.

Provides real-time event-driven UI monitoring via Windows UI Automation
COM events. Detects window opens/closes, focus changes, and structure
changes without polling.

Uses comtypes to implement COM event handler objects running in a
dedicated STA (Single-Threaded Apartment) daemon thread with a Win32
message pump for COM callback delivery.

Usage example::

    from pywinauto.windows.uia_event_handlers import UIAEventHandler

    handler = UIAEventHandler()

    @handler.on("window_opened")
    def on_window(event):
        print(f"Window opened: {event['element_name']}")

    handler.start()
    # ... do work ...
    events = handler.get_events()
    handler.stop()
"""

import ctypes
import ctypes.wintypes
import logging
import queue
import threading
import time
from datetime import datetime, timezone

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


# UIA Event IDs
UIA_WINDOW_OPENED_EVENT_ID = 20016
UIA_WINDOW_CLOSED_EVENT_ID = 20017

# TreeScope values (from UIAutomationClient.h)
TREE_SCOPE_ELEMENT = 0x1
TREE_SCOPE_CHILDREN = 0x2
TREE_SCOPE_SUBTREE = 0x7  # Element | Children | Descendants

# StructureChangeType names (from UIAutomationClient.h)
STRUCTURE_CHANGE_NAMES = {
    0: "ChildAdded",
    1: "ChildRemoved",
    2: "ChildrenInvalidated",
    3: "ChildrenBulkAdded",
    4: "ChildrenBulkRemoved",
    5: "ChildrenReordered",
}

# PeekMessage constant
_PM_REMOVE = 0x0001

# Maximum buffered events before oldest are evicted
MAX_EVENTS = 500

# Valid event types users can subscribe to
VALID_EVENT_TYPES = frozenset({
    "window_opened",
    "window_closed",
    "focus_changed",
    "structure_changed",
})


def _load_com_types():
    """Load UIA COM type library via comtypes.

    Must be called from an STA-initialized thread. Returns a tuple of
    the COM interface types needed for event handler registration.

    Returns
    -------
    tuple
        (IUIAutomationEventHandler, IUIAutomationFocusChangedEventHandler,
         IUIAutomationStructureChangedEventHandler, CUIAutomation)

    Raises
    ------
    ImportError
        If comtypes is not installed.
    OSError
        If UIAutomationCore.dll cannot be loaded.
    """
    import comtypes
    import comtypes.client

    comtypes.client.GetModule("UIAutomationCore.dll")

    from comtypes.gen.UIAutomationClient import (
        CUIAutomation,
        IUIAutomationEventHandler,
        IUIAutomationFocusChangedEventHandler,
        IUIAutomationStructureChangedEventHandler,
    )

    return (
        IUIAutomationEventHandler,
        IUIAutomationFocusChangedEventHandler,
        IUIAutomationStructureChangedEventHandler,
        CUIAutomation,
    )


def _extract_element_info(element):
    """Extract basic info from an IUIAutomationElement.

    Every property access is wrapped in a try/except because this function
    is called inside COM callbacks which must never raise.

    Parameters
    ----------
    * **element** :
        An IUIAutomationElement COM object provided by the callback.

    Returns
    -------
    dict
        Dictionary with keys: element_name, process_id, process_name,
        control_type, class_name. Missing values default to empty string
        or 0 for process_id.
    """
    info = {}

    try:
        info["element_name"] = element.CurrentName or ""
    except Exception:
        info["element_name"] = ""

    try:
        pid = element.CurrentProcessId
        info["process_id"] = pid
        if psutil is not None:
            try:
                info["process_name"] = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                info["process_name"] = ""
        else:
            info["process_name"] = ""
    except Exception:
        info["process_id"] = 0
        info["process_name"] = ""

    try:
        info["control_type"] = element.CurrentLocalizedControlType or ""
    except Exception:
        info["control_type"] = ""

    try:
        info["class_name"] = element.CurrentClassName or ""
    except Exception:
        info["class_name"] = ""

    return info


def _create_handler_classes(iface_event, iface_focus, iface_structure):
    """Create COM handler classes for UIA events.

    The handler classes are created dynamically because they reference
    COM interface types that are only available after the type library
    has been loaded via ``_load_com_types()``.

    Parameters
    ----------
    * **iface_event** :
        IUIAutomationEventHandler COM interface.
    * **iface_focus** :
        IUIAutomationFocusChangedEventHandler COM interface.
    * **iface_structure** :
        IUIAutomationStructureChangedEventHandler COM interface.

    Returns
    -------
    tuple
        (WindowEventHandler, FocusEventHandler, StructureEventHandler)
        class objects ready for instantiation.
    """
    import comtypes

    class WindowEventHandler(comtypes.COMObject):
        """Handles WindowOpened and WindowClosed automation events."""

        _com_interfaces_ = [iface_event]

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        def HandleAutomationEvent(self, sender, event_id):
            """Called by UIA when a window event fires."""
            try:
                info = _extract_element_info(sender)
                if event_id == UIA_WINDOW_OPENED_EVENT_ID:
                    event_type = "window_opened"
                elif event_id == UIA_WINDOW_CLOSED_EVENT_ID:
                    event_type = "window_closed"
                else:
                    event_type = "unknown_{}".format(event_id)
                self._callback(event_type, info)
            except Exception:
                pass  # COM callbacks must not raise
            return 0  # S_OK

    class FocusEventHandler(comtypes.COMObject):
        """Handles FocusChanged automation events."""

        _com_interfaces_ = [iface_focus]

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        def HandleFocusChangedEvent(self, sender):
            """Called by UIA when keyboard focus changes."""
            try:
                info = _extract_element_info(sender)
                self._callback("focus_changed", info)
            except Exception:
                pass
            return 0  # S_OK

    class StructureEventHandler(comtypes.COMObject):
        """Handles StructureChanged automation events."""

        _com_interfaces_ = [iface_structure]

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        def HandleStructureChangedEvent(self, sender, change_type, runtime_id):
            """Called by UIA when the element tree structure changes."""
            try:
                info = _extract_element_info(sender)
                info["change_type"] = STRUCTURE_CHANGE_NAMES.get(
                    change_type, str(change_type)
                )
                self._callback("structure_changed", info)
            except Exception:
                pass
            return 0  # S_OK

    return WindowEventHandler, FocusEventHandler, StructureEventHandler


class UIAEventHandler(object):
    """Subscribe to Windows UI Automation events in real time.

    Runs a dedicated STA daemon thread with a Win32 message pump to
    receive COM event callbacks. Events are buffered in a thread-safe
    list and can be retrieved with ``get_events()``.

    Supports decorator-based callback registration via ``on()`` and
    direct event buffer access.

    Parameters
    ----------
    * **max_events** (int):
        Maximum number of events to keep in the buffer. Oldest events
        are evicted when this limit is exceeded. Default is 500.

    Example
    -------
    ::

        handler = UIAEventHandler()

        @handler.on("window_opened")
        def on_open(event):
            print(event["element_name"])

        handler.start()
        time.sleep(10)
        handler.stop()
    """

    def __init__(self, max_events=MAX_EVENTS):
        """Initialize the event handler."""
        self._max_events = max(1, max_events)
        self._thread = None
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()
        self._events = []
        self._event_lock = threading.Lock()
        self._callbacks = {}  # event_type -> list of callables
        self._running = False
        self._start_error = None

        # COM objects (created on daemon thread only)
        self._automation = None
        self._root = None
        self._handlers = []  # prevent GC of registered COM objects

    @property
    def is_running(self):
        """Return True if the event monitor is currently running."""
        return (
            self._running
            and self._thread is not None
            and self._thread.is_alive()
        )

    def on(self, event_type):
        """Register a callback for a specific event type.

        Can be used as a decorator::

            @handler.on("focus_changed")
            def on_focus(event):
                print(event)

        Parameters
        ----------
        * **event_type** (str):
            One of: ``window_opened``, ``window_closed``,
            ``focus_changed``, ``structure_changed``.

        Raises
        ------
        ValueError
            If event_type is not a valid event type.
        """
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(
                "Invalid event_type '{}'. Must be one of: {}".format(
                    event_type, ", ".join(sorted(VALID_EVENT_TYPES))
                )
            )

        def decorator(func):
            if event_type not in self._callbacks:
                self._callbacks[event_type] = []
            self._callbacks[event_type].append(func)
            return func

        return decorator

    def start(self):
        """Start the event monitor daemon thread.

        Initializes COM in STA mode on a background thread, loads the
        UIA type library, creates event handler COM objects, and begins
        the Win32 message pump loop.

        Raises
        ------
        RuntimeError
            If the daemon thread fails to start within 10 seconds, or
            if COM initialization fails.
        """
        if self.is_running:
            return

        self._stop_event.clear()
        self._ready_event.clear()
        self._start_error = None

        with self._event_lock:
            self._events.clear()

        self._thread = threading.Thread(
            target=self._run_event_loop,
            name="pywinauto-uia-events",
            daemon=True,
        )
        self._thread.start()

        # Wait for daemon to signal ready (or fail)
        self._ready_event.wait(timeout=10.0)

        if self._start_error:
            self._running = False
            raise RuntimeError(self._start_error)

        self._running = True
        logger.info("UIA event handler started")

    def stop(self):
        """Stop the event monitor and clean up COM resources.

        Signals the daemon thread to exit, waits up to 5 seconds for
        it to join, and clears all registered COM handler references.
        """
        if not self._running:
            return

        self._stop_event.set()

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        self._running = False
        self._thread = None
        self._handlers.clear()
        logger.info("UIA event handler stopped")

    def get_events(self, event_type=None, since=None, limit=50):
        """Retrieve buffered events, optionally filtered.

        Parameters
        ----------
        * **event_type** (str or None):
            If specified, only return events of this type.
        * **since** (str or None):
            ISO 8601 timestamp string. Only return events at or after
            this time.
        * **limit** (int):
            Maximum number of events to return. Default 50.

        Returns
        -------
        list of dict
            Events sorted newest-first. Each dict contains at minimum:
            ``type``, ``timestamp``, ``element_name``, ``process_id``,
            ``process_name``, ``control_type``, ``class_name``.
        """
        limit = max(1, min(limit, self._max_events))

        with self._event_lock:
            result = list(self._events)

        if event_type is not None:
            result = [e for e in result if e.get("type") == event_type]

        if since is not None:
            try:
                since_dt = datetime.fromisoformat(since)
                result = [
                    e for e in result
                    if datetime.fromisoformat(e["timestamp"]) >= since_dt
                ]
            except (ValueError, KeyError):
                pass  # invalid since format, skip filter

        # Return newest first
        return result[-limit:][::-1]

    def clear_events(self):
        """Clear all buffered events."""
        with self._event_lock:
            self._events.clear()

    def _on_event(self, event_type, info):
        """Internal callback invoked by COM handler objects.

        Stores the event in the thread-safe buffer and dispatches to
        any registered user callbacks.
        """
        # Skip empty events with no identifying information
        if (
            not info.get("element_name")
            and not info.get("process_name")
            and not info.get("class_name")
        ):
            return

        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        event.update(info)

        with self._event_lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

        # Dispatch to registered callbacks
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(event)
            except Exception as exc:
                logger.warning(
                    "Event callback raised %s: %s",
                    type(exc).__name__, exc,
                )

    def _run_event_loop(self):
        """Daemon thread entry point.

        Initializes COM (STA), loads type library, registers event
        handlers, and runs the Win32 message pump until ``stop()``
        is called.
        """
        try:
            ctypes.windll.ole32.CoInitialize(None)
        except Exception as exc:
            self._start_error = "CoInitialize failed: {}".format(exc)
            self._ready_event.set()
            return

        try:
            # Load COM type library
            com_types = _load_com_types()
            iface_event, iface_focus, iface_structure, cls_automation = com_types

            # Create handler classes dynamically
            WindowHandler, FocusHandler, StructureHandler = (
                _create_handler_classes(iface_event, iface_focus, iface_structure)
            )

            # Create IUIAutomation instance on this STA thread
            import comtypes.client
            self._automation = comtypes.client.CreateObject(cls_automation)
            self._root = self._automation.GetRootElement()

            # Register global event handlers
            self._register_handlers(WindowHandler, FocusHandler)

            # Signal main thread that we are ready
            self._ready_event.set()

            # Win32 message pump
            msg = ctypes.wintypes.MSG()
            while not self._stop_event.is_set():
                while ctypes.windll.user32.PeekMessageW(
                    ctypes.byref(msg), 0, 0, 0, _PM_REMOVE
                ):
                    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                    ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

                # Brief sleep to avoid busy-wait
                self._stop_event.wait(0.05)

        except Exception as exc:
            logger.error("UIA event loop error: %s", exc)
            if not self._ready_event.is_set():
                self._start_error = "Event loop failed: {}".format(exc)
                self._ready_event.set()
        finally:
            self._unregister_all()
            try:
                ctypes.windll.ole32.CoUninitialize()
            except Exception:
                pass

    def _register_handlers(self, WindowHandler, FocusHandler):
        """Register WindowOpened, WindowClosed, and FocusChanged handlers.

        All handlers are registered on the desktop root element with
        subtree scope to receive events from all windows.
        """
        # WindowOpened
        try:
            h_opened = WindowHandler(self._on_event)
            self._automation.AddAutomationEventHandler(
                UIA_WINDOW_OPENED_EVENT_ID,
                self._root,
                TREE_SCOPE_SUBTREE,
                None,  # cacheRequest
                h_opened,
            )
            self._handlers.append(h_opened)
            logger.debug("Registered WindowOpened handler")
        except Exception as exc:
            logger.warning("Failed to register WindowOpened handler: %s", exc)

        # WindowClosed
        try:
            h_closed = WindowHandler(self._on_event)
            self._automation.AddAutomationEventHandler(
                UIA_WINDOW_CLOSED_EVENT_ID,
                self._root,
                TREE_SCOPE_SUBTREE,
                None,
                h_closed,
            )
            self._handlers.append(h_closed)
            logger.debug("Registered WindowClosed handler")
        except Exception as exc:
            logger.warning("Failed to register WindowClosed handler: %s", exc)

        # FocusChanged
        try:
            h_focus = FocusHandler(self._on_event)
            self._automation.AddFocusChangedEventHandler(
                None,  # cacheRequest
                h_focus,
            )
            self._handlers.append(h_focus)
            logger.debug("Registered FocusChanged handler")
        except Exception as exc:
            logger.warning("Failed to register FocusChanged handler: %s", exc)

    def _unregister_all(self):
        """Remove all registered event handlers and release COM objects."""
        if self._automation is not None:
            try:
                self._automation.RemoveAllEventHandlers()
                logger.debug("Removed all UIA event handlers")
            except Exception as exc:
                logger.warning("Error removing event handlers: %s", exc)

        self._handlers.clear()
        self._automation = None
        self._root = None
