from pywinauto.controls.win_base_wrapper import WinBaseWrapper
from pywinauto.actionlogger import ActionLogger
from pywinauto import backend

FRIENDLY_BY_QT = {
    'QPushButton':'Button', 'QToolButton':'Button',
    'QCheckBox':'CheckBox', 'QRadioButton':'RadioButton',
    'QLineEdit':'Edit', 'QTextEdit':'Edit', 'QPlainTextEdit':'Edit',
    'QComboBox':'ComboBox', 'QSpinBox':'Spinner', 'QDoubleSpinBox':'Spinner',
    'QSlider':'Slider', 'QProgressBar':'ProgressBar',
    'QLabel':'Static', 'QGroupBox':'GroupBox',
    'QTabWidget':'TabControl', 'QTabBar':'Tab',
    'QTreeView':'TreeView', 'QListView':'List', 'QListWidget':'ListBox',
    'QTableView':'Table', 'QTableWidget':'Table',
    'QMenuBar':'MenuBar', 'QMenu':'Menu', 'QToolBar':'ToolBar', 'QStatusBar':'StatusBar',
    'QMainWindow':'Window', 'QDialog':'Dialog', 'QWindow':'Window',
    'QWidget':'Pane',
}

class QtWrapper(WinBaseWrapper):
    def __init__(self, element_info):
        """
        Initialize the element

        * **element_info** is instance of int or one of ElementInfo childs
        """
        self.backend = backend.registry.backends['qt']
        if element_info:

            self._element_info = element_info

            self.id = self._element_info.id

            self.ref = None
            self.appdata = None
            self._cache = {}
            self.actions = ActionLogger()
        else:
            raise RuntimeError('NULL pointer was used to initialize BaseWrapper')

    def friendly_class_name(self):
        qt_cls = self.class_name()
        ctl = getattr(self.element_info, 'control_type', None)
        # prefer control_type if server classifies it
        return ctl or FRIENDLY_BY_QT.get(qt_cls, qt_cls or 'Pane')
    
    def click(self):
        self._element_info.click()

    def set_text(self, text):
        self._element_info.set_text(text)
