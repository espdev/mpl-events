Changelog
=========

v0.0.5
------

* Rename ``connection`` method to ``make_connection`` in ``MplEvent`` class
* Use dict instead of list for stroring all connections in dispatcher class (``mpl_connections``)
* Add sphinx-based documentation
* Update README

v0.0.4
------

* Add ``connection`` method to ``MplEvent`` class
* Improve README
* Add tox/CI configuration
* Fix ``figure`` fixture (closing figure at theardown)
* Fix flake8 errors

v0.0.3
------

* Add ``connect`` argument to constructor of ``MplEventDispatcher`` class
* Add ``disable_default_handlers`` attribute to ``MplEventDispatcher`` class
* Improve README

v0.0.2
------

* The first PyPI release
* Add tests
* Add the description to README

v0.0.1
------

* Initial implementation
