"""Qt backend implementation with injectlib pipe calls."""

from pywinauto.element_info import ElementInfo
from pywinauto.windows.win32structures import RECT
from injectlib.api import ConnectionManager


class PIDNotFound(Exception):
    """Raised when a Qt element operation is requested without a target app process id."""

    pass


class QtElementInfo(ElementInfo):
    """ElementInfo implementation for Qt applications automated via injected DLL."""

    re_props = ["class_name", "name", "control_type"]
    exact_only_props = ["pid", "enabled", "visible", "rectangle", "auto_id"]
    search_order = ["control_type", "class_name", "pid", "visible", "enabled", "name",
                    "auto_id", "rectangle"]
    assert set(re_props + exact_only_props) == set(search_order)

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
        self._rectangle = RECT()

        # root element requested
        if self.id is None:
            self._class_name = "QtDesktop"
            self._name = "--root--"
            self._control_type = "Desktop"
            self._auto_id = "QtDesktop"
            return

        # set injectlib Qt backend for ConnectionManager
        self._ensure_injectlib_backend_registered()

        # Main window requested
        if self.id == 0:
            app_info = self._call_injected_server("GetAppInfo")["value"]
            self._class_name = "QtApplication"
            self._name = app_info["app_name"]
            self._control_type = "Application"
            self._pid = app_info["pid"]
            self._auto_id = "MainApp"
            return

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
        process = kwargs.get("process")
        if process is not None and self._pid is None:
            self._pid = process

        if self.id is None:
            return [QtElementInfo(0, pid=self._pid)]

        if self.id == 0:
            items = self._call_injected_server("GetRoots")["value"]
        else:
            items = self._call_injected_server("GetChildren", element_id=self.id)["value"]

        return [QtElementInfo(item["id"], pid=self._pid, info=item) for item in items]

    def iter_children(self, **kwargs):
        """Iterate over immediate child elements."""
        for child in self.children(**kwargs):
            yield child

    def descendants(self, **kwargs):
        """Return all descendant elements."""
        return list(self.iter_descendants(**kwargs))

    def set_cache_strategy(self, cached=None):
        pass  # TODO: implement a cache strategy for Qt elements

    @property
    def handle(self):
        """Return id from server temporary."""
        return self.id

    @property
    def control_id(self):
        """Return id from injected server element id."""
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
        raise NotImplementedError()

    def click(self):
        """Invoke a semantic click action on this Qt element."""
        self._call_injected_server("Click", element_id=self.id)

    def set_text(self, text):
        """Set text or value for this Qt element."""
        self._call_injected_server("SetText", element_id=self.id, text=text)

    @property
    def rich_text(self):
        """Return rich text for the element."""
        return self.name

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
