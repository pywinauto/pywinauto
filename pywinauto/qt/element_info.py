from pywinauto.element_info import ElementInfo
from pywinauto.qt.client import QtClient
from pywinauto.windows.win32structures import RECT
import json

class InjectedServerNotFound(Exception):
    pass

class QtElementInfo(ElementInfo):
    re_props = ["class_name", "name", "control_type"]
    exact_only_props = ["pid", "enabled", "visible", "rectangle", "auto_id"]
    search_order = ["control_type", "class_name", "pid", "visible", "enabled", "name",
                    "auto_id", "rectangle"]
    assert set(re_props + exact_only_props) == set(search_order)

    def __init__(self, elem_id=None):
        self._client = QtClient()
        if not self._client.ping():
            raise InjectedServerNotFound
        self.id = elem_id
        if self.id is None:
            app_info = json.loads(self._client.app_info())["result"]
            self._class_name = "QtApplication"
            self._name = app_info["app_name"]
            self._control_type = "Application"
            self._pid = app_info["pid"]
            self._visible = True
            self._enabled = True
            self._auto_id = "TopMainApp"
            self._rectangle = RECT()
        elif self.id == 0:
            app_info = json.loads(self._client.app_info())["result"]
            self._class_name = "QtApplication"
            self._name = app_info["app_name"]
            self._control_type = "Application"
            self._pid = app_info["pid"]
            self._visible = True
            self._enabled = True
            self._auto_id = "MainApp"
            self._rectangle = RECT()
        elif self.id > 0:
            info = json.loads(self._client.element_info(self.id))["result"]
            self._name = info['name']
            self._class_name = info['class']
            self._control_type = info['control_type']
            self._pid = info["pid"]
            self._auto_id = info["auto_id"]
            self._visible = info["visible"]
            self._enabled = info["enabled"]
            self._rectangle = RECT(
                info['rect'][0],
                info['rect'][1],
                info['rect'][0] + info['rect'][2],
                info['rect'][1] + info['rect'][3]
            )

    def __repr__(self):
        """Representation of the element info object

        The method prints the following info:
        * type name as a module name and a class name of the object
        * title of the control or empty string
        * class name of the control
        * unique ID of the control, usually a handle
        """
        return '<{0}, {1}>'.format(self.__str__(), self.id)

    def __str__(self):
        """Pretty print representation of the element info object

        The method prints the following info:
        * type name as a module name and class name of the object
        * title of the control or empty string
        * class name of the control
        """
        module = self.__class__.__module__
        module = module[module.rfind('.') + 1:]
        type_name = module + "." + self.__class__.__name__

        tmp = self.name
        tmp = self.class_name

        return "{0} - '{1}', {2}".format(type_name, self.name, self.class_name)
    
    def children(self, **kwargs):
        child_list = []
        if self.id is None:
            child_list.append(QtElementInfo(0))
        elif self.id == 0:
            for item in json.loads(self._client.roots())["result"]:
                child_list.append(QtElementInfo(item["id"]))
        else:
            child_list = []
            tmp = self._client.children(self.id)
            for item in json.loads(self._client.children(self.id))["result"]:
                child_list.append(QtElementInfo(item["id"]))
        return child_list

    
    def set_cache_strategy(self, cached=None):
        pass

    def click(self):
        self._client.click(self.id)

    def set_text(self, text):
        self._client.set_text(self.id, text)

    def descendants(self, **kwargs):
        return self.get_descendants_with_depth(**kwargs)

    @property
    def rich_text(self):
        return self.name

    @property
    def class_name(self):
        return self._class_name
    
    @property
    def name(self):
        return self._name
    
    @property
    def automation_id(self):
        return self.auto_id

    @property
    def auto_id(self):
        return self._auto_id
    
    @property
    def pid(self):
        return self._pid
    
    @property
    def control_type(self):
        return self._control_type

    @property
    def rectangle(self):
        return self._rectangle
    
    @property
    def visible(self):
        return self._visible
    
    @property
    def enabled(self):
        return self._enabled