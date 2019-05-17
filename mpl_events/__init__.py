# -*- coding: utf-8 -*-

import logging

logging.getLogger('mpl_events').addHandler(logging.NullHandler())

from ._types import (
    MplObject_Type,
    EventHandler_Type,
)

from ._base import (
    MplEvent,
    MplEventConnection,
    MplEventDispatcher,
)

from .__version__ import __version__


__all__ = [
    'MplEvent',
    'MplEventConnection',
    'MplEventDispatcher',
]
