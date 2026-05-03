from pywinauto import backend
from pywinauto.qt6.element_info import Qt6ElementInfo
from pywinauto.controls.qt6wrapper import Qt6Wrapper

backend.register("qt6", Qt6ElementInfo, Qt6Wrapper, can_list_top_windows=False)
