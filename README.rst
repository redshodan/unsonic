Unsonic, the ultimate un-Subsonic music server.

Status
======

PyPi
++++
.. image:: https://img.shields.io/pypi/v/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Latest Version
.. image:: https://img.shields.io/pypi/status/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Project Status
.. image:: https://img.shields.io/pypi/l/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: License
.. image:: https://img.shields.io/pypi/pyversions/unsonic.svg
   :target: https://pypi.python.org/pypi/unsonic/
   :alt: Supported Python versions

Builds
++++++
.. image:: https://travis-ci.org/redshodan/unsonic.svg?branch=master
   :target: https://travis-ci.org/redshodan/unsonic
   :alt: Build Status
.. image:: https://coveralls.io/repos/github/redshodan/unsonic/badge.svg?branch=master
   :target: https://coveralls.io/github/redshodan/unsonic?branch=master
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

Tests
-----
  * make tests

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

Manual Testing
--------------
  * ./test/bin/tester getArtists

Installing a Web Client
-----------------------
  * Download/clone Jamstash from https://github.com/tsquillario/Jamstash
  * Edit your config.ini so that the [app:main]/unsonic.ui path points to jamstash/dist
  * With Unsonic running, point your browser at the url printed out, normally
    something like http://localhost:6543 and your will be redirected to the load
    Jamstash.
  * Jamstash is very picky about the server URL in it's configuration. Make sure
    there is no trailing '/' character otherwise Jamstash will not be able to
    build the path correctly.

Docker Installation
+++++++++++++++++++
Docker files are located in the ./docker directory. The Makefile contains some 
convenience targets but the specific ``docker`` and/or ``docker-compose`` cmmands
are also shown.

To build the Unsonic Docker image:::
    $ docker build ./docker
    # Or using docker-compose
    $ docker-compose -f ./docker/docker-compose.yml build

The docker-compose file defines 3 containers, each is geared toward a development/test setup; a
production Docker should only use these as a reference. The containers defined are of PostgreSQL,
and an Unsonic serve based on PostgreSQL and SQLite. The Unsonic containers requires a music
directory to volume mount so one must be specified.

::
    $ MUSIC_DIR=~/music/ docker-compose -f ./docker/docker-compose.yml create
    $ MUSIC_DIR=~/music/ docker-compose -f ./docker/docker-compose.yml up Unsonic-postgres

Or using the Makefile to simplify all of the above.

::
    $ make MUSIC_DIR=~/music/ docker-sqlite

See docker/Dockerfile for details about the ``unsonic`` image. The container details are 
defined ``docker/docker-compose.yml``. The files ``docker/config.ini`` and ``docker/unsonic-init``
can be used to tweak the Unsonic process itself.

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
