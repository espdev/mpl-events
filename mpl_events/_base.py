# -*- coding: utf-8 -*-

import enum
import weakref

from typing import List, Optional

from .mpl import (
    FigureCanvas,
    Figure,
    Axes,
    KeyEvent,
    MouseEvent,
    PickEvent,
    LocationEvent,
    ResizeEvent,
    CloseEvent,
    DrawEvent,
)

from ._types import (
    MplObject_Type,
    EventHandler_Type,
    WeakRefFigure_Type,
)

from ._logging import logger


class MplEvent(enum.Enum):
    """The enum defines all actual matplotlib events

    value of enum item defines original matplotlib event name.
    """

    KEY_PRESS = 'key_press_event'
    KEY_RELEASE = 'key_release_event'
    MOUSE_BUTTON_PRESS = 'button_press_event'
    MOUSE_BUTTON_RELEASE = 'button_release_event'
    MOUSE_MOVE = 'motion_notify_event'
    MOUSE_WHEEL_SCROLL = 'scroll_event'
    FIGURE_RESIZE = 'resize_event'
    FIGURE_ENTER = 'figure_enter_event'
    FIGURE_LEAVE = 'figure_leave_event'
    FIGURE_CLOSE = 'close_event'
    AXES_ENTER = 'axes_enter_event'
    AXES_LEAVE = 'axes_leave_event'
    PICK = 'pick_event'
    DRAW = 'draw_event'


def _get_mpl_figure(mpl_obj: MplObject_Type) -> Figure:
    if isinstance(mpl_obj, Axes):
        figure = mpl_obj.figure
    elif isinstance(mpl_obj, Figure):
        figure = mpl_obj
    elif isinstance(mpl_obj, FigureCanvas):
        figure = mpl_obj.figure
    else:
        raise TypeError(
            'Invalid MPL object {}. '.format(mpl_obj)
            + 'The object must be one of these types: "Axes", "Figure" or "FigureCanvas".'
        )

    if not figure.canvas:
        raise ValueError('The figure object has not a canvas.')

    return figure


class MplEventConnection:
    """Implements the connection to matplotlib event

    The class manages the connection between a matplotlib event and a handler callable.
    """

    def __init__(self, mpl_obj: MplObject_Type,
                 event: MplEvent,
                 handler: EventHandler_Type):
        self._figure = weakref.ref(_get_mpl_figure(mpl_obj))
        self._event = event
        self._handler = handler
        self._id = -1

    def __del__(self):
        self.disconnect()

    def __repr__(self) -> str:
        return '{}(event=<{}:{}>, handler={}, id={})'.format(
            type(self).__name__, self.event.name,
            self.event.value, self.handler, self.id)

    @property
    def figure(self) -> WeakRefFigure_Type:
        """Returns the ref to the related matplotlib figure
        """
        return self._figure()

    @property
    def event(self) -> MplEvent:
        """Returns matplotlib event type as MplEvent enum item
        """
        return self._event

    @property
    def handler(self) -> EventHandler_Type:
        """Returns the event handler callable
        """
        return self._handler

    @property
    def id(self) -> int:
        """Returns matplotlib event connection id
        """
        return self._id

    @property
    def valid(self) -> bool:
        """Retuns True if the connection is valid

        The connection is valid if the related matplotlib figure has not been destroyed.
        """
        return self.figure is not None

    @property
    def connected(self) -> bool:
        """Returns True if the handler callable is connected to the event
        """
        return self._id > 0 and self.valid

    def connect(self):
        """Connects the matplotlib event and the handler callable
        """
        if not self.valid:
            logger.error('Figure ref is dead')
            self._id = -1
            return

        if self.connected:
            return

        self._id = self.figure.canvas.mpl_connect(self._event.value, self._handler)
        logger.debug('"%s" was connected to %s handler (id=%d)',
                     self.event.value, self._handler, self._id)

    def disconnect(self):
        """Disconnects the matplotlib event and the handler callable
        """
        if not self.connected:
            return

        self.figure.canvas.mpl_disconnect(self._id)
        logger.debug('"%s" was disconnected from %s handler (id=%d)',
                     self.event.value, self._handler, self._id)
        self._id = -1


def mpl_event_handler(event_type: MplEvent):
    """Marks the decorated method as given matplotlib event handler

    This decorator should be used only for methods of classes that
    inherited from `MplEventDispatcher` class.

    You can use this decorator for reassignment event handlers in your dispatcher class.

    Example:

        class MyEventDispatcher(MplEventDispatcher):
            @mpl_event_handler(MplEvent.KEY_PRESS)
            def on_my_key_press(self, event: mpl.KeyPress):
                pass
    """
    class HandlerDescriptor:
        def __init__(self, handler):
            self.handler = handler

        def __get__(self, obj, cls=None):
            return self.handler.__get__(obj, cls)

        def __set_name__(self, owner, name):
            if 'mpl_event_handlers' not in owner.__dict__:
                owner.mpl_event_handlers = {}
            owner.mpl_event_handlers[event_type] = name

    return HandlerDescriptor


class MplEventDispatcher:
    """The base dispatcher class for connecting and handling all matplotlib events
    """

    mpl_event_handlers = {}

    def __init__(self, mpl_obj: MplObject_Type):
        self._figure = weakref.ref(_get_mpl_figure(mpl_obj))
        self._mpl_connections = self._init_mpl_connections()

    def __del__(self):
        self.mpl_disconnect()

    def _init_mpl_connections(self) -> List[MplEventConnection]:
        conns = []

        for event, handler_name in self.mpl_event_handlers.items():
            handler = self._get_handler(handler_name)
            if handler:
                conn = MplEventConnection(self.figure, event, handler)
                conns.append(conn)

        return conns

    def _get_handler(self, handler_name: str) -> Optional[EventHandler_Type]:
        for cls in type(self).__mro__:
            if cls is not MplEventDispatcher and handler_name in cls.__dict__:
                handler = getattr(self, handler_name)
                if callable(handler):
                    logger.debug('Found event handler: %s', handler)
                    return handler

    @property
    def figure(self) -> WeakRefFigure_Type:
        """Returns the ref to the related matplotlib figure
        """
        return self._figure()

    @property
    def valid(self) -> bool:
        """Retuns True if the connection is valid

        The connection is valid if the related matplotlib figure has not been destroyed.
        """
        return self.figure is not None

    @property
    def mpl_connections(self) -> List[MplEventConnection]:
        """Returns the list of mpl_connections for this event dispatcher instance
        """
        return self._mpl_connections

    def mpl_connect(self):
        """Connects the matplotlib events to implemented event handlers for this instance
        """
        if not self.valid:
            logger.error('The figure ref is dead')
            return

        self.mpl_disconnect()
        for conn in self._mpl_connections:
            conn.connect()

    def mpl_disconnect(self):
        """Disconnects the implemented handlers for the related matplotlib events for this instance
        """
        if not self.valid:
            return

        for conn in self._mpl_connections:
            conn.disconnect()

    # ########################################################################
    # The methods below define API for handling matplotlib events.
    # All handler methods of the base class (MplEventDispatcher) never
    # connected to events. Any of these methods can be implemented in
    # subclasses and will be connected to relevant events automatically.
    # ########################################################################

    @mpl_event_handler(MplEvent.KEY_PRESS)
    def on_key_press(self, event: KeyEvent):
        """KeyEvent - key is pressed
        """

    @mpl_event_handler(MplEvent.KEY_RELEASE)
    def on_key_release(self, event: KeyEvent):
        """KeyEvent - key is released
        """

    @mpl_event_handler(MplEvent.MOUSE_BUTTON_PRESS)
    def on_mouse_button_press(self, event: MouseEvent):
        """MouseEvent - mouse button is pressed
        """

    @mpl_event_handler(MplEvent.MOUSE_BUTTON_RELEASE)
    def on_mouse_button_release(self, event: MouseEvent):
        """MouseEvent - mouse button is released
        """

    @mpl_event_handler(MplEvent.MOUSE_MOVE)
    def on_mouse_move(self, event: MouseEvent):
        """MouseEvent - mouse motion
        """

    @mpl_event_handler(MplEvent.MOUSE_WHEEL_SCROLL)
    def on_mouse_wheel_scroll(self, event: MouseEvent):
        """MouseEvent - mouse scroll wheel is rolled
        """

    @mpl_event_handler(MplEvent.FIGURE_RESIZE)
    def on_figure_resize(self, event: ResizeEvent):
        """ResizeEvent - figure canvas is resized
        """

    @mpl_event_handler(MplEvent.FIGURE_ENTER)
    def on_figure_enter(self, event: LocationEvent):
        """LocationEvent - mouse enters a new figure
        """

    @mpl_event_handler(MplEvent.FIGURE_LEAVE)
    def on_figure_leave(self, event: LocationEvent):
        """LocationEvent - mouse leaves a figure
        """

    @mpl_event_handler(MplEvent.FIGURE_CLOSE)
    def on_figure_close(self, event: CloseEvent):
        """CloseEvent - a figure is closed
        """

    @mpl_event_handler(MplEvent.AXES_ENTER)
    def on_axes_enter(self, event: LocationEvent):
        """LocationEvent - mouse enters a new axes
        """

    @mpl_event_handler(MplEvent.AXES_LEAVE)
    def on_axes_leave(self, event: LocationEvent):
        """LocationEvent - mouse leaves an axes
        """

    @mpl_event_handler(MplEvent.PICK)
    def on_pick(self, event: PickEvent):
        """PickEvent - an object in the canvas is selected
        """

    @mpl_event_handler(MplEvent.DRAW)
    def on_draw(self, event: DrawEvent):
        """DrawEvent - canvas draw (but before screen update)
        """


def disable_default_key_press_handler(mpl_obj: MplObject_Type):
    """Disables default key_press handling for given figure/canvas

    The default key handler using the toolmanager.
    """
    figure = _get_mpl_figure(mpl_obj)

    cid = figure.canvas.manager.key_press_handler_id

    if cid:
        figure.canvas.mpl_disconnect(cid)
