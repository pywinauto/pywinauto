"""Example: monitoring UI Automation events with pywinauto.

Demonstrates how to use UIAEventHandler to subscribe to real-time
window and focus events on Windows. Open and close applications while
this script is running to see events printed to the console.

Usage::

    python example_uia_events.py

Press Ctrl+C to stop.
"""

import time

from pywinauto.windows.uia_event_handlers import UIAEventHandler


def main():
    handler = UIAEventHandler()

    # Register callbacks using the decorator API
    @handler.on("window_opened")
    def on_window_opened(event):
        name = event.get("element_name", "")
        proc = event.get("process_name", "")
        if name:
            print("[OPENED] {} ({})".format(name, proc))

    @handler.on("window_closed")
    def on_window_closed(event):
        name = event.get("element_name", "")
        proc = event.get("process_name", "")
        if name:
            print("[CLOSED] {} ({})".format(name, proc))

    @handler.on("focus_changed")
    def on_focus_changed(event):
        name = event.get("element_name", "")
        ctrl = event.get("control_type", "")
        print("[FOCUS]  {} [{}]".format(name, ctrl))

    # Start the event monitor
    handler.start()
    print("UIA Event Handler started. Open/close windows to see events.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        handler.stop()
        print("Stopped.")

    # Print summary of buffered events
    events = handler.get_events(limit=10)
    if events:
        print("\nLast {} buffered events:".format(len(events)))
        for ev in events:
            print("  [{type}] {element_name} ({process_name})".format(**ev))


if __name__ == "__main__":
    main()
