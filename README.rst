Unsonic, the ultimate un-music server.

Installation
------------

* Development build
  * make devel
  * make db

* Run it
  * make run

Manual Installation
-------------------

* Requirements
  * virtualenv $venv
  * $venv/bin/pip install pyramid
  * $venv/bin/pip install SQLAlchemy
  * $venv/bin/pip install psycopg2
  * $venv/bin/pip install eyeD3
  * Install mishmash (FIXME)

* Build
  * $venv/bin/python setup.py develop
  * $venv/bin/initialize_unsonic_db development.ini
  * $venv/bin/pserve development.ini

License
-------

Unsonic is licensed under the GPL v2 license. See the COPYING file for details.
