# mpl-events

**mpl-events** is a tiny library for simple and convenient [matplotlib](https://matplotlib.org/) event handling 
with minimum boilerplate code. The library provides high level API for using [matplotlib event system](https://matplotlib.org/users/event_handling.html).

## Pros and cons

**Pros**:

* We do not use raw strings for event names. Intstead, we use `MplEvent` enum class for all events.
* We do not use integer id for connection. Instead, connection between event and handler incapsulated via class `MplEventConnection`
* mpl-events objects do not own figures and do not create additional references to figures
* mpl-events provides convenient base class `MplEventDispatcher` and handlers API for handling all mpl events inside one class without boilerplate code
* mpl-events provides high level API, auto disconnecting and cleanup

**Cons**:

* Additional level of abstraction (if this can be considered a disadvantage)
* Additional dependency in your project

## Installation

We supprort Python 3.6 and newer.

We can use pip to install mpl-events:

```bash
pip install mpl-events
```

or from github repo:

```bash
pip install git+https://github.com/espdev/mpl-events.git
```

## Usage

### Event dispatchers

Custom event dispatcher class might be created to handle some matplotlib events just 
inheriting `MplEventDispatcher` class and implementing the required event handlers.

The following example shows how we can create the dispatcher for handling all mouse events:

```python
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
mouse_dispatcher.mpl_connect()

plt.show()
```

`MplEventDispatcher` class provides API (handler methods interface) for all matplotlib events. 
You may override and implement some of these methods for handling corresponding events.

A dispatcher might be connected to a canvas using mpl objects `figure` or `axes` (or `canvas`). 
In general, we do not need to think about it. We just pass `figure` instance to contructor usually.

And it is all. We do not need to worry about connecting/disconnecting or remember mpl event names.

If we want to use another methods (not base API that provides `MplEventDispatcher`) for 
handling events we can use `mpl_event_handler` decorator inside our dispatcher class.

```python
from mpl_events import MplEventDispatcher, MplEvent, mpl_event_handler, mpl

class MyDrawEventDispatcher(MplEventDispatcher):

    @mpl_event_handler(MplEvent.FIGURE_CLOSE)
    def _close_event_handler(self, event: mpl.CloseEvent):
        print(f'figure {event.canvas.figure} closing')
```

Also we can create event dispatchers hierarchies:

```python
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

```

### Event connections

The connection between event and handler incapsulated in `MplEventConnection` class. 
This class is high level wrapper for `figure.canvas.mpl_connect`/`figure.canvas.mpl_disconnect` mpl API.

`MplEventConnection` can be used if we want to handle events and do not use event dispatcher interface.

In this case we just create instance of `MplEventConnection` class and pass
mpl object for connecting (`figure`, `axes` or `canvas`), event type as `MplEvent` enum and handler as callable.

```python
from matplotlib import pyplot as plt
from mpl_events import MplEventConnection, MplEvent, mpl

def close_handler(event: mpl.CloseEvent):
    print('figure closing')

figure = plt.figure()

conn = MplEventConnection(figure, MplEvent.FIGURE_CLOSE, close_handler)

print(conn)
# MplEventConnection(event=<FIGURE_CLOSE:close_event>, handler=<function close_handler at 0x0000013FD1002E18>, id=5)

plt.show()
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
