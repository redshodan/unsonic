VBIN=build/venv/bin
VLIB=build/venv/lib
PYTHON=$(VBIN)/python
PY_LIB=$(VLIB)/python*/site-packages


all: bins devel

bins: bin/unsonic bin/unsonic-db

bin/unsonic: bin/unsonic.in
	sed "s?/usr/bin/env python?`pwd`/${PYTHON}?" $< > $@
	chmod +x $@

bin/unsonic-db: bin/unsonic-db.in
	sed "s?/usr/bin/env python?`pwd`/${PYTHON}?" $< > $@
	chmod +x $@

build/venv/bin/python:
	[ ! -d build ] && mkdir build
	virtualenv build/venv

devel: $(PY_LIB)/unsonic.egg-link 

$(PY_LIB)/unsonic.egg-link: build/venv/bin/python setup.py setup.cfg README.rst development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	touch $@

db: devel-db
devel-db: build/unsonic.sqlite
build/unsonic.sqlite: bin/unsonic-db development.ini $(PY_LIB)/unsonic.egg-link
	bin/unsonic-db init development.ini
	bin/unsonic-db sync development.ini

run: devel-run
devel-run: bin/unsonic build/unsonic.sqlite
	bin/unsonic development.ini --reload

tests:
	PYTHONPATH=external/eyed3/src/:external/mishmash/src $(PYTHON) setup.py test

clean:
	-find unsonic -name '*.pyc' | xargs rm

dist-clean: clean
	rm -rf build unsonic.egg-info unsonic.sqlite bin/unsonic bin/unsonic-db

.PHONY: devel db pyramid paste sqlalchemy psycopg2 eyed3 run tests clean dist-clean
