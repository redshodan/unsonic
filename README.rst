Unsonic, the ultimate un-music server.

Installation
============

Prerequisites
-------------
  * Install eyeD3-0.7.4 (FIXME) into external/eyed3
  * Install mishmash (FIXME) into external/mishmash

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
===================

Requirements
------------
  * virtualenv $venv
  * Install eyeD3-0.7.4 (FIXME) into external/eyed3
  * Install mishmash (FIXME) into external/mishmash

Building
-----
  * $venv/bin/python setup.py develop

Running
---
  * ./bin/unsonic-db init <config.ini>
  * ./bin/unsonic-db sync <config.ini>
  * ./bin/unsonic <config.ini>

License
=======
Unsonic is licensed under the GPL v2 license. See the COPYING file for details or
http://www.gnu.org/licenses/gpl-2.0.html#SEC1
