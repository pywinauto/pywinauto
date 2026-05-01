# -*- coding: utf-8 -*-
"""Basic wrapping of Qt5 elements."""

from __future__ import unicode_literals

from .qt_common_wrapper import BaseQtMeta, BaseQtWrapper


class Qt5Meta(BaseQtMeta):

    """Metaclass for Qt5 wrapper objects."""

    control_type_to_cls = {}


class Qt5Wrapper(BaseQtWrapper, metaclass=Qt5Meta):

    """Default wrapper for Qt5 controls."""

    _control_types = []
    backend_name = "qt5"
