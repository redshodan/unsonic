Unsonic, the ultimate un-music server.

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
  * ./bin/unsonic-db -c <config.ini> init
  * ./bin/unsonic-db -c <config.ini> sync
  * ./bin/unsonic-db -c <config.ini> adduser name pass
  * ./bin/unsonic <config.ini> --reload

Adjusting the configuration
===========================
The main configuration settings are the location of the database ::

  sqlalchemy.url = sqlite:///%(here)s/build/development.sqlite

and the location of the music directory ::

  mishmash.paths = 
      Music: %(here)s/test/music

Adjust them to fit your deployment needs. The mishmash.paths can have multiple 
music directories, one per line. %(here)s refers to the location of the 
configuration file itself.


License
=======
Unsonic is licensed under the GPL v2 license. See the COPYING file for details or
http://www.gnu.org/licenses/gpl-2.0.html#SEC1
