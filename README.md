# mpl-events

[![PyPI version](https://img.shields.io/pypi/v/mpl-events.svg)](https://pypi.python.org/pypi/mpl-events)
[![Build status](https://travis-ci.org/espdev/mpl-events.svg?branch=master)](https://travis-ci.org/espdev/mpl-events)
[![Docs status](https://readthedocs.org/projects/mpl-events/badge/)](https://mpl-events.readthedocs.io/en/latest/)
[![License](https://img.shields.io/pypi/l/mpl-events.svg)](LICENSE)

**mpl-events** is a tiny library for simple and convenient [matplotlib](https://matplotlib.org/) event handling 
with minimum boilerplate code. In other words, the library provides high-level API for using [matplotlib event system](https://matplotlib.org/users/event_handling.html).

You need to handling matplotlib events if you want to manipulate figures and plots/visualizations interactively.
Matplotlib contains a low-level API for event handling: using ``FigureCanvasBase.mpl_connect`` and
``FigureCanvasBase.mpl_disconnect`` methods, string-based event names and integer connection identifiers.

## Pros and cons

**Pros**:

* mpl-events provides high-level API, auto disconnecting and cleanup
* Strings-based event types/names are not used. Intstead, `MplEvent` enum class is used for all event types.
* Integer connection identifiers are not used. Instead, the connection between event and handler is incapsulated via class `MplEventConnection`
* mpl-events objects do not own mpl figure and do not create additional references to figure or canvas
* mpl-events provides convenient base class `MplEventDispatcher` that contains handlers API (with type-hints) for handling all mpl events inside one class without boilerplate code

**Cons**:

* Additional level of abstraction (if this can be considered a disadvantage)
* Additional dependency in your project

## Installation

![Supported Python versions](https://img.shields.io/pypi/pyversions/mpl-events.svg)

You can use pip to install mpl-events:

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

plt.show()
```

`MplEventDispatcher` class provides API (handler methods interface) for all matplotlib events. 
You may override and implement some of these methods for handling corresponding events.

The dispatcher might be connected to a canvas using mpl objects `figure` or `axes` (or `canvas`). 
In general, we do not need to think about it. We just pass `figure` instance to constructor usually.
By default connection to events is made automatically. This behavior is controlled by `connect` argument.

And it is all. We do not need to worry about connecting/disconnecting or remember mpl event names.

If we want to use another methods (not `MplEventDispatcher` API) for handling events we can 
use `mpl_event_handler` decorator inside our dispatcher class.

```python
from mpl_events import MplEventDispatcher, MplEvent, mpl_event_handler, mpl

class CloseEventDispatcher(MplEventDispatcher):

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

In this case we just create instance of `MplEventConnection` class and pass to constructor
mpl object for connecting (`figure`, `axes` or `canvas`), event type as `MplEvent` enum and handler as callable.
By default connection is made automatically. This behavior is controlled by `connect` argument.

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

Also we can use the shortcut for `MplEventConnection` constuction using `make_connection` method of `MplEvent` class:

```python
from mpl_events import MplEvent

...

conn = MplEvent.FIGURE_CLOSE.make_connection(figure, close_handler)
```

### Disable default key press event handler

Matplotlib figures usually contain navigation bar for some interactions with axes and this navigation bar handles key presses. 
By default key press handler is connected in `FigureManagerBase` mpl class. 
mpl-events provides `disable_default_key_press_handler` function to disconnect the default key press handler.
Also in event dispatcher classes we can use `disable_default_handlers` attribute.

Here is a simple example:

```python
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
```

## Testing

We use pytest and tox for testing.

## Documentation

Please see [the latest documentation](https://mpl-events.readthedocs.io/en/latest/).
