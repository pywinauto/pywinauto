from pywinauto import backend
from pywinauto.qt5.element_info import Qt5ElementInfo
from pywinauto.controls.qt5wrapper import Qt5Wrapper

backend.register("qt5", Qt5ElementInfo, Qt5Wrapper, can_list_top_windows=False)
