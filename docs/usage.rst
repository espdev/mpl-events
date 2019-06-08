.. _usage:

*****
Usage
*****

.. contents:: Contents
    :local:

Event dispatchers
=================

Custom event dispatcher class might be created to handle some matplotlib events just
inheriting :class:`mpl_events.MplEventDispatcher` class and implementing the required event handlers.

The following example shows how we can create the dispatcher for handling all mouse events:

.. code-block:: python

    from matplotlib import pyplot as plt
    from mpl_events import MplEventDispatcher, mpl

    class MouseEventDispatcher(MplEventDispatcher):

        def on_mouse_button_press(self, event: mpl.MouseEvent):
            print(f'mouse button {event.button} pressed')

        def on_mouse_button_release(self, event: mpl.MouseEvent):
            print(f'mouse button {event.button} released')

        def on_mouse_move(self, event: mpl.MouseEvent):
            print(f'mouse moved')

        def on_mouse_wheel_scroll(self, event: mpl.MouseEvent):
            print(f'mouse wheel scroll {event.step}')

    figure = plt.figure()

    # setup figure and make plots is here ...

    mouse_dispatcher = MouseEventDispatcher(figure)

    plt.show()

:class:`MplEventDispatcher` class provides API (handler methods interface) for all matplotlib events.
You may override and implement some of these methods for handling corresponding events.

The dispatcher might be connected to a canvas using mpl objects ``figure`` or ``axes`` (or ``canvas``).
In general, we do not need to think about it. We just pass ``figure`` instance to constructor usually.
By default connection to events is made automatically. This behavior is controlled by ``connect`` argument.

And it is all. We do not need to worry about connecting/disconnecting or remember mpl event names.

If we want to use another methods (not ``MplEventDispatcher`` API) for handling events we can
use :func:`mpl_events.mpl_event_handler` decorator inside our dispatcher class.

.. code-block:: python

    from mpl_events import MplEventDispatcher, MplEvent, mpl_event_handler, mpl

    class CloseEventDispatcher(MplEventDispatcher):

        @mpl_event_handler(MplEvent.FIGURE_CLOSE)
        def _close_event_handler(self, event: mpl.CloseEvent):
            print(f'figure {event.canvas.figure} closing')

Also we can create event dispatchers hierarchies:

.. code-block:: python

    from mpl_events import MplEventDispatcher, mpl

    class MyEventDispatcherBase(MplEventDispatcher):
        def on_figure_close(self, event: mpl.CloseEvent):
            print('figure closing from MyEventDispatcherBase')

    class MyEventDispatcher(MyEventDispatcherBase):

        def on_figure_close(self, event: mpl.CloseEvent):
            super().on_figure_close(event)
            print('figure closing from MyEventDispatcher')

        def on_figure_resize(self, event: mpl.ResizeEvent):
            print('figure resizing')

Event filters
-------------

Sometimes we need to look at, and possibly intercept, the events that are handled in dispatcher classes.
We can use :func:`mpl_events.MplEventDispatcher.add_event_filter` method for adding an event filter callable that will intercept events.

event filter signature:

.. code-block:: python

    def event_filter(obj: MplEventDispatcher, event: mpl.Event) -> Optional[bool]:
        pass

The first argument if referecne to dispatcher object, the second argument is mpl event object.
If the filter callable returns ``True``, other filters and the handler for the event in the
dispatcher class will not be called.

The example:

.. code-block:: python

    class Dispatcher(MplEventDispatcher):
        def on_key_press(self, event: mpl.KeyEvent):
            print('key press')

        def on_key_release(self, event: mpl.KeyEvent):
            print('key release')

    def event_filter(obj: MplEventDispatcher, event: mpl.Event):
        if isinstance(obj, Dispatcher):
            if event.name == MplEvent.KEY_PRESS.value:
                print('key press filtering')
                # No handling KEY_PRESS in "Dispatcher"
                return True

            elif event.name == MplEvent.KEY_RELEASE.value:
                print('key release filtering')
                # Handling KEY_RELEASE in "Dispatcher" after filtering
                return False

    dispatcher = Dispatcher(figure)
    dispatcher.add_event_filter(event_filter)

Event connections
=================

The connection between event and handler incapsulated in :class:`mpl_events.MplEventConnection` class.
This class is high level wrapper for ``figure.canvas.mpl_connect``/``figure.canvas.mpl_disconnect`` mpl API.

:class:`MplEventConnection` can be used if we want to handle events and do not use event dispatcher interface.

In this case we just create instance of :class:`MplEventConnection` class and pass to constructor
mpl object for connecting (``figure``, ``axes`` or ``canvas``), event type as :class:`MplEvent` enum and handler as callable.
By default connection is made automatically. This behavior is controlled by ``connect`` argument.

.. code-block:: python

    from matplotlib import pyplot as plt
    from mpl_events import MplEventConnection, MplEvent, mpl

    def close_handler(event: mpl.CloseEvent):
        print('figure closing')

    figure = plt.figure()

    conn = MplEventConnection(figure, MplEvent.FIGURE_CLOSE, close_handler)

    print(conn)
    # MplEventConnection(event=<FIGURE_CLOSE:close_event>, handler=<function close_handler at 0x0000013FD1002E18>, id=5)

    plt.show()

Also we can use the shortcut for :class:`MplEventConnection` constuction using :func:`MplEvent.make_connection` method of :class:`MplEvent` class:

.. code-block:: python

    from mpl_events import MplEvent
    ...

    conn = MplEvent.FIGURE_CLOSE.make_connection(figure, close_handler)

Disable default key press event handler
=======================================

Matplotlib figures usually contain navigation bar for some interactions with axes and this navigation bar handles key presses.
By default key press handler is connected in ``FigureManagerBase`` mpl class.
mpl-events provides :func:`disable_default_key_press_handler` function to disconnect the default key press handler.
Also in event dispatcher classes we can use ``disable_default_handlers`` attribute.

Here is a simple example:

.. code-block:: python

    from matplotlib import pyplot as plt
    from mpl_events import MplEventDispatcher, mpl

    class KeyEventDispatcher(MplEventDispatcher):
        disable_default_handlers = True

        def on_key_press(self, event: mpl.KeyEvent):
            print(f'Pressed key {event.key}')

        def on_key_release(self, event: mpl.KeyEvent):
            print(f'Released key {event.key}')

    figure = plt.figure()

    dispatcher = KeyEventDispatcher(figure)

    plt.show()
