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

Requirements
------------
  * virtualenv $venv
  * Install eyeD3-0.7.4 into external/eyed3
	* cd external; hg clone 'https://bitbucket.org/redshodan/eyed3-for-unsonic' eyed3
	* cd external/eyed3; hg up stable
	* cd external/eyed3; paver build
  * Install mishmash (FIXME) into external/mishmash
	* cd external; hg clone 'https://bitbucket.org/redshodan/mishmash-music-server' mishmash

Building
--------
  * $venv/bin/python setup.py develop

Running
-------
  * ./bin/unsonic-db -c <config.ini> init
  * ./bin/unsonic-db -c <config.ini> sync
  * ./bin/unsonic-db -c <config.ini> adduser name pass
  * ./bin/unsonic <config.ini> --reload

License
=======
Unsonic is licensed under the GPL v2 license. See the COPYING file for details or
http://www.gnu.org/licenses/gpl-2.0.html#SEC1
