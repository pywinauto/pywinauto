"""Qt backend implementation with injectlib pipe calls."""

from pywinauto.element_info import ElementInfo
from pywinauto.windows.win32structures import RECT
from injectlib.api import ConnectionManager, InjectedNotFoundError, InjectedUnsupportedActionError


def is_element_satisfying_criteria(element, process=None, class_name=None, name=None, control_type=None,
                                   auto_id=None, visible=None, enabled=None, **kwargs):
    """Check if element satisfies pywinauto search criteria."""
    if control_type is not None:
        if isinstance(control_type, str):
            if element.control_type != control_type:
                return False
        else:
            raise TypeError('control_type must be string')

    def is_none_or_equals(criteria, prop):
        return criteria is None or prop == criteria

    return is_none_or_equals(process, element.process_id) \
        and is_none_or_equals(class_name, element.class_name) \
        and is_none_or_equals(name, element.name) \
        and is_none_or_equals(auto_id, element.auto_id) \
        and is_none_or_equals(visible, element.visible) \
        and is_none_or_equals(enabled, element.enabled)


class PIDNotFound(Exception):
    """Raised when a Qt element operation is requested without a target app process id."""

    pass


class QtElementInfo(ElementInfo):
    """ElementInfo implementation for Qt applications automated via injected DLL."""

    re_props = ["class_name", "name", "control_type", "auto_id", "value"]
    exact_only_props = ["pid", "enabled", "visible", "rectangle", "handle", "control_id",
                        "framework_id", "runtime_id"]
    search_order = ["control_type", "class_name", "pid", "visible", "enabled", "name",
                    "auto_id", "rectangle", "handle", "control_id", "framework_id",
                    "runtime_id", "value"]
    assert set(re_props + exact_only_props) == set(search_order)

    renamed_props = {
        "title": ("name", None),
        "title_re": ("name_re", None),
        "process": ("pid", None),
        "visible_only": ("visible", {True: True, False: None}),
        "enabled_only": ("enabled", {True: True, False: None}),
        "top_level_only": ("depth", {True: 1, False: None}),
    }

    def __init__(self, elem_id=None, pid=None, info=None):
        """Create Qt element info from an injected server element id.

        elem_id=None creates a synthetic search root used by pywinauto before the target process is known.
        elem_id=0 represents Qt application node inside a known process.
        elem_id > 0' Positive ids represent real Qt objects returned by injected server.
        """
        self.id = elem_id
        self._pid = pid
        self._class_name = ""
        self._name = ""
        self._control_type = ""
        self._visible = True
        self._enabled = True
        self._auto_id = ""
        self._value = None
        self._rectangle = RECT()

        # root element requested
        if self.id is None:
            self._pid = None
            self._class_name = "QtDesktop"
            self._name = "--root--"
            self._control_type = "Desktop"
            self._auto_id = "QtDesktop"
            return

        # set injectlib Qt backend for ConnectionManager
        self._ensure_injectlib_backend_registered()

        if info is None:
            info = self._call_injected_server("GetElementInfo", element_id=self.id)["value"]
        self._load_info(info)

    def _ensure_injectlib_backend_registered(self):
        """Ensure that injectlib Qt backend is registered for element's process id."""
        if self._pid is None:
            raise PIDNotFound("Qt backend requires a process id before injection")
        ConnectionManager().register_backend(self._pid, "qt", "qt_srv")

    def _call_injected_server(self, action_name, **params):
        """Send an action to injected Qt DLL through ConnectionManager."""
        self._ensure_injectlib_backend_registered()
        return ConnectionManager().call_action(action_name, self._pid, **params)

    def _load_info(self, info):
        """Populate cached properties from an injected server element summary."""
        self.id = info["id"]
        self._name = info.get("name", "")
        self._class_name = info.get("class", "")
        self._control_type = info.get("control_type", "")
        self._pid = info.get("pid", self._pid)
        self._auto_id = info.get("auto_id", "")
        self._value = info.get("value", None)
        self._visible = info.get("visible", True)
        self._enabled = info.get("enabled", True)
        rect = info.get("rect", [0, 0, 0, 0])
        self._rectangle = RECT(
            rect[0],
            rect[1],
            rect[0] + rect[2],
            rect[1] + rect[3]
        )

    def __repr__(self):
        """Return a debugger-friendly representation of the element."""
        return '<{0}, {1}>'.format(self.__str__(), self.id)

    def __str__(self):
        """Return a readable element description used by tree dumps."""
        module = self.__class__.__module__
        module = module[module.rfind('.') + 1:]
        type_name = module + "." + self.__class__.__name__
        return "{0} - '{1}', {2}".format(type_name, self.name, self.class_name)

    def children(self, **kwargs):
        """Return immediate children of the element."""
        return list(self.iter_children(**kwargs))

    def _matched_win32_pids(self, **kwargs):
        """Return pids for native top-level windows matched by the win32 backend."""

        win32_keys = ("name", "name_re", "class_name", "class_name_re", "visible", "enabled")
        if not any(kwargs.get(key) is not None for key in win32_keys[:4]):
            return []

        win32_criteria = {"backend": "win32", "top_level_only": True}
        for key in win32_keys:
            if kwargs.get(key) is not None:
                win32_criteria[key] = kwargs[key]

        from pywinauto import findwindows
        try:
            win32_elements = findwindows.find_elements(**win32_criteria)
        except (findwindows.ElementNotFoundError, findwindows.ElementAmbiguousError):
            return []

        pids = []
        seen_pids = set()
        for element in win32_elements:
            pid = element.process_id
            if pid not in seen_pids:
                seen_pids.add(pid)
                pids.append(pid)
        return pids

    def _top_window_elements_from_win32_matches(self, **kwargs):
        """Return Qt top-level windows preselected through win32."""
        # Qt backend needs a process id before it can inject Qt server DLL.
        # When user starts from "Desktop(backend="qt")" there is no pid yet.
        # This method asks win32 for matching top-level windows, then creates Qt element
        # roots only for the matched pids.

        elements = []
        for pid in self._matched_win32_pids(**kwargs):
            try:
                elements.extend(self.children(process=pid))
            except Exception:
                continue
        return elements

    def iter_children(self, **kwargs):
        """Iterate over immediate child elements."""
        process = kwargs.get("process")

        if self.id is None:
            if process is None:
                items = self._top_window_elements_from_win32_matches(**kwargs)
            else:
                ConnectionManager().register_backend(process, "qt", "qt_srv")
                raw_items = ConnectionManager().call_action("GetRoots", process)["value"]
                items = [QtElementInfo(item["id"], pid=process, info=item) for item in raw_items]
        else:
            raw_items = self._call_injected_server("GetChildren", element_id=self.id)["value"]
            items = [QtElementInfo(item["id"], pid=self._pid, info=item) for item in raw_items]

        for element in items:
            if is_element_satisfying_criteria(element, **kwargs):
                yield element

    def descendants(self, **kwargs):
        """Return all descendant elements."""
        return list(self.iter_descendants(**kwargs))

    def iter_descendants(self, **kwargs):
        """Iterate over all descendant elements."""
        depth = kwargs.pop("depth", None)
        process = kwargs.pop("process", None)
        if not isinstance(depth, (int, type(None))) or isinstance(depth, int) and depth < 0:
            raise Exception("Depth must be an integer")

        if depth == 0:
            return
        for child in self.iter_children(process=process):
            if is_element_satisfying_criteria(child, **kwargs):
                yield child
            next_kwargs = dict(kwargs)
            if depth is not None:
                next_kwargs["depth"] = depth - 1
            for descendant in child.iter_descendants(process=process, **next_kwargs):
                if is_element_satisfying_criteria(descendant, **kwargs):
                    yield descendant

    def set_cache_strategy(self, cached=None):
        pass  # TODO: implement a cache strategy for Qt elements

    @property
    def handle(self):
        """Return native window handle.

        Qt backend elements are identified by injected runtime ids, not HWNDs.
        """
        return None

    @property
    def control_id(self):
        """Return id from injected server element id."""
        return self.id

    @property
    def runtime_id(self):
        """Return runtime id."""
        return self.id

    @property
    def process_id(self):
        """Return process id that owns this Qt element."""
        return self._pid

    pid = process_id

    @property
    def framework_id(self):
        """Return framework ID of the element (always is 'Qt', for compatibility with UIA)."""
        return "Qt"

    @property
    def parent(self):
        """Return parent element."""
        if self.id is None:
            return None
        try:
            parent_info = self._call_injected_server("GetParent", element_id=self.id)["value"]
        except (InjectedNotFoundError, InjectedUnsupportedActionError):
            return None
        if not parent_info:
            return None
        return QtElementInfo(parent_info["id"], pid=self._pid, info=parent_info)

    def click(self):
        """Invoke a semantic click action on this Qt element."""
        self._call_injected_server("Click", element_id=self.id)

    def set_text(self, text):
        """Set text or value for this Qt element."""
        self._call_injected_server("SetText", element_id=self.id, text=text)

    def set_focus(self):
        """Set keyboard focus to this element."""
        self._call_injected_server("SetFocus", element_id=self.id)

    def select(self, item=None):
        """Select this element or child item."""
        params = {"element_id": self.id}
        if item is not None:
            if isinstance(item, int):
                params["index"] = item
            else:
                params["text"] = item
        self._call_injected_server("Select", **params)

    def toggle(self):
        """Toggle this element."""
        self._call_injected_server("Toggle", element_id=self.id)

    def expand(self):
        """Expand this element."""
        self._call_injected_server("Expand", element_id=self.id)

    def collapse(self):
        """Collapse this element."""
        self._call_injected_server("Collapse", element_id=self.id)

    def items(self):
        """Return item texts exposed by this control."""
        try:
            return self._call_injected_server("GetItems", element_id=self.id)["value"]
        except InjectedUnsupportedActionError:
            return []

    def get_native_property(self, name, error_if_not_exists=False):
        """Return native Qt property."""
        try:
            return self._call_injected_server("GetProperty", element_id=self.id, name=name)["value"]
        except InjectedNotFoundError as exc:
            if error_if_not_exists:
                raise exc
        return None

    def set_native_property(self, name, value):
        """Set native Qt property."""
        self._call_injected_server("SetProperty", element_id=self.id, name=name, value=value)

    def invoke_method(self, name):
        """Invoke a no-argument Qt method."""
        self._call_injected_server("InvokeMethod", element_id=self.id, name=name)

    def set_value(self, value):
        """Set value for a value-like Qt control."""
        self._call_injected_server("SetValue", element_id=self.id, value=value)

    @property
    def rich_text(self):
        """Return rich text for the element."""
        value = self.value
        if value not in (None, "") and self.control_type in ("Edit", "Spinner"):
            return str(value)
        return self.name

    @property
    def value(self):
        """Return value-like text for the element."""
        if self.id in (None, 0):
            return self._value or ""
        try:
            reply = self._call_injected_server("GetValue", element_id=self.id)
            return reply["value"]
        except InjectedUnsupportedActionError:
            return self._value or ""

    @property
    def class_name(self):
        """Return Qt class name."""
        return self._class_name

    @property
    def name(self):
        """Return name of the element."""
        return self._name

    @property
    def automation_id(self):
        return self.auto_id

    @property
    def auto_id(self):
        """Return Qt objectName from injected server when available."""
        return self._auto_id

    @property
    def control_type(self):
        """Return pywinauto-friendly control type."""
        return self._control_type

    @property
    def rectangle(self):
        """Return rectangle of the element in screen coordinates."""
        return self._rectangle

    @property
    def visible(self):
        """Return whether the element is visible."""
        return self._visible

    @property
    def enabled(self):
        """Return whether the element is enabled."""
        return self._enabled

    def __hash__(self):
        """Return a stable hash for the runtime element."""
        return hash((self._pid, self.id))

    def __eq__(self, other):
        """Check if two QtElementInfo objects describe the same runtime element."""
        if not isinstance(other, QtElementInfo):
            return False
        return self._pid == other._pid and self.id == other.id

    def __ne__(self, other):
        """Check if two QtElementInfo objects describe different runtime elements."""
        return not (self == other)

    @classmethod
    def get_active(cls, app_or_pid):
        """Return current focused Qt element."""
        from pywinauto.application import Application

        if isinstance(app_or_pid, int):
            pid = app_or_pid
        elif isinstance(app_or_pid, Application):
            pid = app_or_pid.process
        else:
            raise TypeError("QtElementInfo.get_active requires an integer pid or Application instance")

        ConnectionManager().register_backend(pid, "qt", "qt_srv")
        try:
            reply = ConnectionManager().call_action("GetFocusedElement", pid)
            info = reply["value"]
            if info:
                return cls(info["id"], pid=pid, info=info)
            return None
        except InjectedUnsupportedActionError:
            return None
