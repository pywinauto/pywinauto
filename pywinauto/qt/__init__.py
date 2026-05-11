"""Qt backends for pywinauto."""

from pywinauto import backend
from pywinauto.qt.qt5_element_info import Qt5ElementInfo
from pywinauto.qt.qt6_element_info import Qt6ElementInfo
from pywinauto.controls.qt5wrapper import Qt5Wrapper
from pywinauto.controls.qt6wrapper import Qt6Wrapper

backend.register("qt5", Qt5ElementInfo, Qt5Wrapper, can_list_top_windows=False)
backend.register("qt6", Qt6ElementInfo, Qt6Wrapper, can_list_top_windows=False)
