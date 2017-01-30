Unsonic, the ultimate un-Subsonic music server.

Status
======
.. image:: https://img.shields.io/pypi/v/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Latest Version
.. image:: https://img.shields.io/pypi/status/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Project Status
.. image:: https://travis-ci.org/redshodan/unsonic.svg?branch=master
   :target: https://travis-ci.org/redshodan/unsonic
   :alt: Build Status
.. image:: https://img.shields.io/pypi/l/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: License
.. image:: https://img.shields.io/pypi/pyversions/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Supported Python versions
.. image:: https://coveralls.io/repos/redshodan/unsonic/badge.svg
   :target: https://coveralls.io/r/redshodan/unsonic
   :alt: Coverage Status

Installation
============

TLDR: The uber short version
++++++++++++++++++++++++++++
  * make run

The longer version
++++++++++++++++++

Development build
-----------------
  * make devel
  * make devel-db
  * make devel-run

Release build
-------------
  * make release
  * make release-db
  * make release-run

Manual Installation
+++++++++++++++++++

Building
--------
  * make

Running
-------
  * ./bin/unsonic -c <config.ini> sync
  * ./bin/unsonic -c <config.ini> adduser name pass
  * ./bin/unsonic -c <config.ini> serve [--reload]

Adjusting the configuration
===========================
The main configuration settings are the location of the database ::

  sqlalchemy.url = sqlite:///%(here)s/build/development.sqlite

and the location of the music directory ::

  [mishmash]
      paths = Music: /%(here)s/test/music

Adjust them to fit your deployment needs. The mishmash.paths can have multiple 
music directories, one per line. %(here)s refers to the location of the 
configuration file itself.


License
=======
Unsonic is licensed under the GPL v2 license. See the COPYING file for details or
http://www.gnu.org/licenses/gpl-2.0.html#SEC1
