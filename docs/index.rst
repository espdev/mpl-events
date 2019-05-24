.. mpl-events documentation master file, created by
   sphinx-quickstart on Wed May 22 19:22:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mpl-events: matplotlib event handling
=====================================

**mpl-events** is a tiny library for simple and convenient `matplotlib <https://matplotlib.org/>`_ event handling
with minimum boilerplate code. In other words, the library provides high-level API for using
`matplotlib event system <https://matplotlib.org/users/event_handling.html>`_.

Why do we need yet another library?
-----------------------------------

You need to handling matplotlib events if you want to manipulate figures and visualizations interactively.
Matplotlib contains a low-level API for event handling: using ``FigureCanvasBase.mpl_connect`` and
``FigureCanvasBase.mpl_disconnect`` methods, string-based names of events and integer connection identifiers.

Here are a few things that might be helpful:

* mpl-events provides high-level API, auto disconnecting and cleanup
* Strings-based event types/names are not used. Intstead, :class:`mpl_events.MplEvent` enum class is used for all event types.
* Integer connection identifiers are not used. Instead, the connection between event and handler is incapsulated via class :class:`mpl_events.MplEventConnection`
* mpl-events objects do not own mpl figure and do not create additional references to figure or canvas
* mpl-events provides convenient base class :class:`mpl_events.MplEventDispatcher` that contains handlers API (with type-hints)
  for handling all mpl events inside one class without boilerplate code

Quickstart
----------

Event dispatcher for handling all mouse events:

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

Event connection to handle figure closing:

.. code-block:: python

      from matplotlib import pyplot as plt
      from mpl_events import MplEvent, mpl

      def close_handler(event: mpl.CloseEvent):
         print('figure closing')

      figure = plt.figure()
      conn = MplEvent.FIGURE_CLOSE.make_connection(figure, close_handler)
      plt.show()

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
