from pywinauto import backend
from pywinauto.qt.element_info import QtElementInfo
from pywinauto.controls.qtwrapper import QtWrapper

backend.register("qt", QtElementInfo, QtWrapper)
