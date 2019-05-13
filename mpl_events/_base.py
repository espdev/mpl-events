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


class MplEventConnection:
    """Implements the connection to matplotlib event

    The class manages the connection between a matplotlib event and a handler callable.
    """

    def __init__(self, figure: Figure,
                 event: MplEvent,
                 handler: EventHandler_Type):
        self._figure = weakref.ref(figure, self._disconnect)
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
        if self.valid:
            self._connect(self.figure)

    def disconnect(self):
        """Disconnects the matplotlib event and the handler callable
        """
        self._disconnect(self.figure)

    def _connect(self, figure: Figure):
        self._disconnect(figure)
        self._id = figure.canvas.mpl_connect(self._event.value, self._handler)

    def _disconnect(self, figure: Figure):
        if self._id > 0 and figure:
            figure.canvas.mpl_disconnect(self._id)
            self._id = -1


class MplEventDispatcher:
    """The base dispatcher class for connecting and handling all matplotlib events
    """

    __all_connections__ = weakref.WeakKeyDictionary()
    """The weak dict contains all connected events
    """

    event_handlers = {
        MplEvent.KEY_PRESS: 'on_key_press',
        MplEvent.KEY_RELEASE: 'on_key_release',
        MplEvent.MOUSE_BUTTON_PRESS: 'on_mouse_button_press',
        MplEvent.MOUSE_BUTTON_RELEASE: 'on_mouse_button_release',
        MplEvent.MOUSE_MOVE: 'on_mouse_move',
        MplEvent.MOUSE_WHEEL_SCROLL: 'on_mouse_wheel_scroll',
        MplEvent.FIGURE_RESIZE: 'on_figure_resize',
        MplEvent.FIGURE_ENTER: 'on_figure_enter',
        MplEvent.FIGURE_LEAVE: 'on_figure_leave',
        MplEvent.FIGURE_CLOSE: 'on_figure_close',
        MplEvent.AXES_ENTER: 'on_axes_enter',
        MplEvent.AXES_LEAVE: 'on_axes_leave',
        MplEvent.PICK: 'on_pick',
        MplEvent.DRAW: 'on_draw',
    }

    def __init__(self, mpl_obj: MplObject_Type):
        self._figure = weakref.ref(self._get_figure(mpl_obj), self._destroy_figure)
        self._connections = self._init_connections()

    def __del__(self):
        self.disconnect()
        if self.valid:
            del self.__all_connections__[self.figure][self]

    @staticmethod
    def _get_figure(mpl_obj: MplObject_Type) -> Figure:
        if isinstance(mpl_obj, Axes):
            return mpl_obj.figure
        elif isinstance(mpl_obj, Figure):
            return mpl_obj
        elif isinstance(mpl_obj, FigureCanvas):
            return mpl_obj.figure
        else:
            raise TypeError(
                'Invalid MPL object {}. '.format(mpl_obj)
                + 'The object must be one of these types: "Axes", "Figure" or "FigureCanvas".'
            )

    def _init_connections(self) -> List[MplEventConnection]:
        conns = []

        for event, handler_name in self.event_handlers.items():
            handler = self._get_handler(handler_name)
            if handler:
                conn = MplEventConnection(self.figure, event, handler)
                conns.append(conn)

        if conns and self.valid:
            fig_conns = self.__all_connections__.setdefault(
                self.figure, weakref.WeakKeyDictionary())
            fig_conns[self] = conns

        return conns

    def _destroy_figure(self, figure: Figure):
        if figure:
            del self.__all_connections__[figure]

    def _get_handler(self, handler_name: str) -> Optional[EventHandler_Type]:
        for cls in type(self).__mro__:
            if cls is not MplEventDispatcher and handler_name in cls.__dict__:
                handler = getattr(self, handler_name)
                if callable(handler):
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
    def connections(self) -> List[MplEventConnection]:
        """Returns the list of connections for this event dispatcher instance
        """
        return self._connections

    def connect(self):
        """Connects the matplotlib events and implemented event handlers for this instance
        """
        self.disconnect()
        for conn in self._connections:
            conn.connect()

    def disconnect(self):
        """Disconnects the implemented handlers for the related matplotlib events for this instance
        """
        for conn in self._connections:
            conn.disconnect()

    # ########################################################################
    # The methods below define API for handling matplotlib events.
    # All handler methods of the base class (MplEventDispatcher) never
    # connected to events. Any of these methods can be implemented in
    # subclasses and will be connected to relevant events automatically.
    # ########################################################################

    def on_key_press(self, event: KeyEvent):
        """KeyEvent - key is pressed
        """

    def on_key_release(self, event: KeyEvent):
        """KeyEvent - key is released
        """

    def on_mouse_button_press(self, event: MouseEvent):
        """MouseEvent - mouse button is pressed
        """

    def on_mouse_button_release(self, event: MouseEvent):
        """MouseEvent - mouse button is released
        """

    def on_mouse_move(self, event: MouseEvent):
        """MouseEvent - mouse motion
        """

    def on_mouse_wheel_scroll(self, event: MouseEvent):
        """MouseEvent - mouse scroll wheel is rolled
        """

    def on_figure_resize(self, event: ResizeEvent):
        """ResizeEvent - figure canvas is resized
        """

    def on_figure_enter(self, event: LocationEvent):
        """LocationEvent - mouse enters a new figure
        """

    def on_figure_leave(self, event: LocationEvent):
        """LocationEvent - mouse leaves a figure
        """

    def on_figure_close(self, event: CloseEvent):
        """CloseEvent - a figure is closed
        """

    def on_axes_enter(self, event: LocationEvent):
        """LocationEvent - mouse enters a new axes
        """

    def on_axes_leave(self, event: LocationEvent):
        """LocationEvent - mouse leaves an axes
        """

    def on_pick(self, event: PickEvent):
        """PickEvent - an object in the canvas is selected
        """

    def on_draw(self, event: DrawEvent):
        """DrawEvent - canvas draw (but before screen update)
        """
