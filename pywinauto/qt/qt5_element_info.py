"""Qt5 backend element info implementation."""

from pywinauto.qt.common_element_info import BaseQtElementInfo, PIDNotFound


class Qt5ElementInfo(BaseQtElementInfo):
    """ElementInfo implementation for Qt5 applications automated via injected DLL."""

    pywinauto_backend_name = "qt5"
    injectlib_backend_name = "qt5"
    injectlib_dll_name = "qt5_srv"
    desktop_class_name = "Qt5Desktop"
    desktop_auto_id = "Qt5Desktop"
