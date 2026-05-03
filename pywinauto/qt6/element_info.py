"""Qt6 backend implementation."""

from pywinauto.qt_common.element_info import BaseQtElementInfo, PIDNotFound


class Qt6ElementInfo(BaseQtElementInfo):
    """ElementInfo implementation for Qt6 applications automated via injected DLL."""

    pywinauto_backend_name = "qt6"
    injectlib_backend_name = "qt6"
    injectlib_dll_name = "qt6_srv"
    desktop_class_name = "Qt6Desktop"
    desktop_auto_id = "Qt6Desktop"
