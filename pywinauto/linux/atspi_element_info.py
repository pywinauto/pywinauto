# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Linux AtspiElementInfo class"""

from .atspi_objects import AtspiAccessible, AtspiComponent, AtspiStateEnum, AtspiAction, AtspiValue, \
    IATSPI, RECT
from ..element_info import ElementInfo


class AtspiElementInfo(ElementInfo):

    """Search class and hierarchy walker for AT-SPI elements"""

    atspi_accessible = AtspiAccessible()

    re_props = ["class_name", "name", "control_type"]
    exact_only_props = ["handle", "pid", "control_id", "visible", "enabled", "rectangle",
        "framework_id", "framework_name", "atspi_version", "runtime_id", "description"]
    search_order = ["handle", "control_type", "class_name", "pid", "control_id",
        "visible", "enabled", "name", "rectangle",
        "framework_id", "framework_name", "atspi_version", "runtime_id", "description"]
    # "auto_id", "full_control_type"
    assert set(re_props + exact_only_props) == set(search_order)

    renamed_props = {
        "title": ("name", None),
        "title_re": ("name_re", None),
        "process": ("pid", None),
        "visible_only": ("visible", {True: True, False: None}),
        "enabled_only": ("enabled", {True: True, False: None}),
        "top_level_only": ("depth", {True: 1, False: None}),
    }


    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = self.atspi_accessible.get_desktop(0)
        else:
            self._handle = handle

        # Cache non-mutable element IDs
        self._pid = self.atspi_accessible.get_process_id(self._handle, None)
        self._root_id = self.atspi_accessible.get_id(self._handle, None)
        self._runtime_id = self.atspi_accessible.get_index_in_parent(self._handle, None)

    def __get_elements(self, root, tree, **kwargs):
        tree.append(root)
        for el in root.children(**kwargs):
            self.__get_elements(el, tree, **kwargs)

    def __hash__(self):
        """Return a unique hash value based on the element's handle"""
        return hash((self._pid, self._root_id, self._runtime_id))

    def __eq__(self, other):
        """Check if two AtspiElementInfo objects describe the same element"""
        if not isinstance(other, AtspiElementInfo):
            return False
        if self.control_type == "Application" and other.control_type == "Application":
            return self.process_id == other.process_id
        return self.rectangle == other.rectangle

    def __ne__(self, other):
        """Check if two AtspiElementInfo objects describe different elements"""
        return not (self == other)

    @staticmethod
    def _get_states_as_string(states):
        string_states = []
        for i, state in AtspiStateEnum.items():
            if states & (1 << i):
                string_states.append(state)
        return string_states

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def name(self):
        """Return the text of the window"""
        return self.atspi_accessible.get_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def control_id(self):
        """Return the ID of the window"""
        return self.atspi_accessible.get_role(self._handle, None)

    @property
    def runtime_id(self):
        """Return the runtime ID of the element"""
        return self._runtime_id

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return self._pid

    pid = process_id

    @property
    def class_name(self):
        """Return the class name of the element"""
        role = self.atspi_accessible.get_role_name(self._handle, None)
        return "".join([part.capitalize() for part in role.decode("utf-8").split()])

    @property
    def rich_text(self):
        """Return the text of the element"""
        return self.name

    @property
    def control_type(self):
        """Return the class name of the element"""
        role_id = self.atspi_accessible.get_role(self._handle, None)
        try:
            return IATSPI().known_control_type_ids[role_id]
        except KeyError:
            raise NotImplementedError('Unknown role ID has been retrieved: {0}'.format(role_id))

    @property
    def parent(self):
        """Return the parent of the element"""
        if self == AtspiElementInfo():
            return None
        return AtspiElementInfo(self.atspi_accessible.get_parent(self._handle, None))

    def children(self, **kwargs):
        """Return children of the element"""
        process = kwargs.get("process", None)
        class_name = kwargs.get("class_name", None)
        name = kwargs.get("name", None)
        control_type = kwargs.get("control_type", None)

        cnt = self.atspi_accessible.get_child_count(self._handle, None)
        childrens = []
        for i in range(cnt):
            child = AtspiElementInfo(self.atspi_accessible.get_child_at_index(self._handle, i, None))
            if class_name is not None and class_name != child.class_name:
                continue
            if name is not None and name != child.rich_text:
                continue
            if control_type is not None and control_type != child.control_type:
                continue
            if process is not None and process != child.process_id:
                continue
            childrens.append(child)
        return childrens

    @property
    def component(self):
        component = self.atspi_accessible.get_component(self._handle)
        return AtspiComponent(component)

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        tree = []
        for obj in self.children(**kwargs):
            self.__get_elements(obj, tree, **kwargs)
        depth = kwargs.get("depth", None)
        tree = self.filter_with_depth(tree, self, depth)
        return tree

    def description(self):
        return self.atspi_accessible.get_description(self._handle, None).decode(encoding='UTF-8')

    def framework_id(self):
        return self.atspi_accessible.get_toolkit_version(self._handle, None).decode(encoding='UTF-8')

    def framework_name(self):
        return self.atspi_accessible.get_toolkit_name(self._handle, None).decode(encoding='UTF-8')

    def atspi_version(self):
        return self.atspi_accessible.get_atspi_version(self._handle, None).decode(encoding='UTF-8')

    def get_layer(self):
        """Return rectangle of element"""
        if self.control_type == "Application":
            return self.children()[0].get_layer()
        return self.component.get_layer()

    def get_order(self):
        if self.control_type == "Application":
            return self.children()[0].get_order()
        return self.component.get_mdi_z_order()

    def get_state_set(self):
        val = self.atspi_accessible.get_state_set(self.handle)
        return self._get_states_as_string(val.contents.states)

    def get_action(self):
        if self.atspi_accessible.is_action(self.handle):
            return AtspiAction(self.atspi_accessible.get_action(self.handle))
        else:
            return None

    def get_atspi_value_obj(self):
        return AtspiValue(self.atspi_accessible.get_value(self.handle))

    @property
    def visible(self):
        states = self.get_state_set()
        if self.control_type == "Application":
            children = self.children()
            if children:
                states = children[0].get_state_set()
            else:
                return False
        return "STATE_VISIBLE" in states and "STATE_SHOWING" in states and "STATE_ICONIFIED" not in states

    def set_cache_strategy(self, cached):
        """Set a cache strategy for frequently used attributes of the element"""
        pass  # TODO: implement a cache strategy for atspi elements

    @property
    def enabled(self):
        states = self.get_state_set()
        if self.control_type == "Application":
            children = self.children()
            if children:
                states = children[0].get_state_set()
            else:
                return False
        return "STATE_ENABLED" in states

    @property
    def rectangle(self):
        """Return rectangle of element"""
        if self.control_type == "Application":
            # Application object have`t rectangle. It`s just a fake container which contain base application
            # info such as process ID, window name etc. Will return application frame rectangle
            children = self.children()
            if children:
                return self.children()[0].rectangle
            else:
                return RECT()
        elif self.control_type == "Invalid":
            return RECT()
        return self.component.get_rectangle(coord_type="screen")
