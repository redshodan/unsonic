VBIN=build/venv/bin
PYTHON=$(VBIN)/python

all: devel

build/venv/bin/python:
	[ ! -d build ] && mkdir build
	virtualenv build/venv

devel: $(VBIN)/initialize_unsonic_db

$(VBIN)/initialize_unsonic_db: build/venv/bin/python setup.py setup.cfg README.rst development.ini
$(VBIN)/initialize_unsonic_db:
	$(PYTHON) setup.py develop
	touch $@

db: build/unsonic.sqlite
build/unsonic.sqlite: bin/unsonic-db development.ini $(VBIN)/initialize_unsonic_db
	$(PYTHON) bin/unsonic-db init development.ini
	$(PYTHON) bin/unsonic-db sync development.ini

run: build/unsonic.sqlite
	$(PYTHON) bin/unsonic development.ini --reload

tests:
	PYTHONPATH=external/eyed3/src/:external/mishmash/src $(PYTHON) setup.py test

clean:
	-find unsonic -name '*.pyc' | xargs rm

dist-clean: clean
	rm -rf build unsonic.egg-info unsonic.sqlite

.PHONY: devel db pyramid paste sqlalchemy psycopg2 eyed3 run tests clean dist-clean
