.. mpl-events documentation master file, created by
   sphinx-quickstart on Wed May 22 19:22:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mpl-events: matplotlib event handling
=====================================

**mpl-events** is a tiny library for simple and convenient `matplotlib <https://matplotlib.org/>`_ event handling
with minimum boilerplate code. In other words, the library provides high level API for using
`matplotlib event system <https://matplotlib.org/users/event_handling.html>`_.

Quickstart
----------

All mouse matplotlib events handling:

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
