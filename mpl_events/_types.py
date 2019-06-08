# -*- coding: utf-8 -*-

import typing as t

from .mpl import (
    FigureCanvas,
    Figure,
    Axes,
    Event,
)

MplObject_Type = t.Union[Axes, Figure, FigureCanvas]
EventHandler_Type = t.Callable[[Event], None]
EventFilter_Type = t.Callable[['MplEventDispatcher', Event], t.Optional[bool]]
WeakRefFigure_Type = t.Optional[Figure]
