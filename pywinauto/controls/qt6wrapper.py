# -*- coding: utf-8 -*-
"""Basic wrapping of Qt6 elements."""

from __future__ import unicode_literals

from .qt_common_wrapper import BaseQtMeta, BaseQtWrapper


class Qt6Meta(BaseQtMeta):

    """Metaclass for Qt6 wrapper objects."""

    control_type_to_cls = {}


class Qt6Wrapper(BaseQtWrapper, metaclass=Qt6Meta):

    """Default wrapper for Qt6 controls."""

    _control_types = []
    backend_name = "qt6"
