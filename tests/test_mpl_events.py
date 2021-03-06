# -*- coding: utf-8 -*-

import pytest

import matplotlib
matplotlib.use('Agg')  # We do not use a gui toolkit for testing
from matplotlib import pyplot

from mpl_events import MplEvent, MplEventConnection, MplEventDispatcher, mpl_event_handler
from mpl_events import mpl


@pytest.fixture
def figure():
    fig = pyplot.figure()
    yield fig
    pyplot.close(fig)


PROCESS_EVENTS_PARAM = [
    (MplEvent.KEY_PRESS, lambda canvas: canvas.key_press_event(None)),
    (MplEvent.KEY_RELEASE, lambda canvas: canvas.key_release_event(None)),

    (MplEvent.MOUSE_BUTTON_PRESS, lambda canvas: canvas.button_press_event(0, 0, None)),
    (MplEvent.MOUSE_BUTTON_RELEASE, lambda canvas: canvas.button_release_event(0, 0, None)),
    (MplEvent.MOUSE_MOVE, lambda canvas: canvas.motion_notify_event(0, 0)),
    (MplEvent.MOUSE_WHEEL_SCROLL, lambda canvas: canvas.scroll_event(0, 0, 1)),

    (MplEvent.PICK, lambda canvas: canvas.pick_event(
        mpl.MouseEvent(MplEvent.MOUSE_BUTTON_PRESS.value, canvas, 0, 0), canvas.figure)),

    (MplEvent.DRAW, lambda canvas: canvas.draw_event(None)),

    (MplEvent.FIGURE_CLOSE, lambda canvas: canvas.close_event()),
    (MplEvent.FIGURE_RESIZE, lambda canvas: canvas.resize_event()),

    (MplEvent.FIGURE_ENTER, lambda canvas: canvas.enter_notify_event()),

    (MplEvent.FIGURE_LEAVE, lambda canvas: canvas.callbacks.process(
        MplEvent.FIGURE_LEAVE.value,
        mpl.LocationEvent(MplEvent.FIGURE_LEAVE.value, canvas, 0, 0))),

    (MplEvent.AXES_ENTER, lambda canvas: canvas.callbacks.process(
        MplEvent.AXES_ENTER.value,
        mpl.LocationEvent(MplEvent.AXES_ENTER.value, canvas, 0, 0))),

    (MplEvent.AXES_LEAVE, lambda canvas: canvas.callbacks.process(
        MplEvent.AXES_LEAVE.value,
        mpl.LocationEvent(MplEvent.AXES_LEAVE.value, canvas, 0, 0))),
]


@pytest.mark.parametrize('event', list(MplEvent))
def test_event_connection(figure, event: MplEvent):
    def event_handler(e):
        pass

    connection = MplEventConnection(figure, event, event_handler, connect=False)

    connection.connect()
    assert connection.connected

    connection.disconnect()
    assert not connection.connected


@pytest.mark.parametrize('event_type, process_event', PROCESS_EVENTS_PARAM)
def test_handle_event(figure, event_type, process_event):
    event = None

    def event_handler(e):
        nonlocal event
        event = e.name

    connection = MplEventConnection(figure, event_type, event_handler)
    assert connection.connected

    process_event(figure.canvas)
    assert event == event_type.value


@pytest.mark.parametrize('event_type, process_event', PROCESS_EVENTS_PARAM)
def test_event_dispatcher(figure, event_type, process_event):

    class EventDispatcher(MplEventDispatcher):
        latest_event = None

        def on_key_press(self, event):
            self.update_latest(event)

        def on_key_release(self, event):
            self.update_latest(event)

        def on_mouse_button_press(self, event):
            self.update_latest(event)

        def on_mouse_button_release(self, event):
            self.update_latest(event)

        def on_mouse_move(self, event):
            self.update_latest(event)

        def on_mouse_wheel_scroll(self, event):
            self.update_latest(event)

        def on_figure_resize(self, event):
            self.update_latest(event)

        def on_figure_enter(self, event):
            self.update_latest(event)

        def on_figure_leave(self, event):
            self.update_latest(event)

        def on_figure_close(self, event):
            self.update_latest(event)

        def on_axes_enter(self, event):
            self.update_latest(event)

        def on_axes_leave(self, event):
            self.update_latest(event)

        def on_pick(self, event):
            self.update_latest(event)

        def on_draw(self, event):
            self.update_latest(event)

        def update_latest(self, event):
            if not self.latest_event:
                self.latest_event = event.name

    dispatcher = EventDispatcher(figure)

    process_event(figure.canvas)

    assert dispatcher.latest_event == event_type.value


def test_event_dispatcher_inheritance(figure):

    class EventDispatcher1(MplEventDispatcher):
        latest_events = []

        def on_key_press(self, event):
            self.latest_events.append(event.name)

    class EventDispatcher2(EventDispatcher1):
        def on_key_release(self, event):
            self.latest_events.append(event.name)

    dispatcher = EventDispatcher2(figure)

    figure.canvas.key_press_event(None)
    figure.canvas.key_release_event(None)

    assert dispatcher.latest_events == [MplEvent.KEY_PRESS.value, MplEvent.KEY_RELEASE.value]


def test_event_dispatcher_change_handler(figure):
    class EventDispatcher(MplEventDispatcher):
        latest_event = []

        @mpl_event_handler(MplEvent.KEY_PRESS)
        def on_key_press_custom(self, event):
            self.latest_event.append(event.name)

        def on_key_release(self, event):
            self.latest_event.append(event.name)

    dispatcher = EventDispatcher(figure)

    figure.canvas.key_press_event(None)
    figure.canvas.key_release_event(None)

    assert dispatcher.latest_event == [MplEvent.KEY_PRESS.value, MplEvent.KEY_RELEASE.value]


def test_event_dispatcher_change_handler_inheritance(figure):
    class EventDispatcherBase(MplEventDispatcher):
        latest_event = []

        @mpl_event_handler(MplEvent.KEY_PRESS)
        def on_key_press_custom(self, event):
            self.latest_event.append(event.name)

        def on_key_release(self, event):
            self.latest_event.append(event.name)

    class EventDispatcher(EventDispatcherBase):
        def on_key_press_custom(self, event):
            super().on_key_press_custom(event)

        def on_key_release(self, event):
            super().on_key_release(event)

    dispatcher = EventDispatcher(figure)

    figure.canvas.key_press_event(None)
    figure.canvas.key_release_event(None)

    assert dispatcher.latest_event == [MplEvent.KEY_PRESS.value, MplEvent.KEY_RELEASE.value]


def test_several_event_dispatchers(figure):
    class EventDispatcherBase(MplEventDispatcher):
        latest_event = []

    class EventDispatcher1(EventDispatcherBase):
        @mpl_event_handler(MplEvent.KEY_PRESS)
        def on_key_press_custom(self, event):
            self.latest_event.append(event.name)

    class EventDispatcher2(EventDispatcherBase):
        def on_key_press(self, event):
            self.latest_event.append(event.name)

    class EventDispatcher3(EventDispatcherBase):
        def on_key_press(self, event):
            self.latest_event.append(event.name)

    dispatcher1 = EventDispatcher1(figure)
    dispatcher2 = EventDispatcher2(figure)
    dispatcher3 = EventDispatcher3(figure)

    figure.canvas.key_press_event(None)

    assert EventDispatcherBase.latest_event == [MplEvent.KEY_PRESS.value] * 3


@pytest.mark.parametrize('filter_flag, expected', [
    (False, ['filtered1', 'filtered2', MplEvent.KEY_PRESS.value]),
    (True, ['filtered1']),
])
def test_event_filter(figure, filter_flag, expected):
    class EventDispatcher(MplEventDispatcher):
        latest_event = []

        def on_key_press(self, event):
            self.latest_event.append(event.name)

    def event_filter1(obj, event):
        obj.latest_event.append('filtered1')
        return filter_flag

    def event_filter2(obj, event):
        obj.latest_event.append('filtered2')
        return filter_flag

    dispatcher = EventDispatcher(figure)

    dispatcher.add_event_filter(event_filter1)
    dispatcher.add_event_filter(event_filter2)

    figure.canvas.key_press_event(None)

    assert dispatcher.latest_event == expected
