TOPDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VBIN=$(TOPDIR)/build/venv/bin
VLIB=$(TOPDIR)/build/venv/lib
PYTHON=$(VBIN)/python
PIP=$(VBIN)/pip
PY_LIB=$(VLIB)/python*/site-packages


all: venv bins external devel

bins: bin/unsonic bin/unsonic-server

bin/unsonic: bin/unsonic.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

bin/unsonic-server: bin/unsonic-server.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

venv: build/venv/bin/python
build/venv/bin/python:
	[ ! -d build ] && mkdir build
	virtualenv -p python3 build/venv

external: mishmash-build

mishmash-build: external/mishmash eyed3

external/mishmash:
	cd external; git clone 'https://github.com/nicfit/mishmash.git' mishmash

eyed3: $(PY_LIB)/eyed3
$(PY_LIB)/eyed3:
	cd external/mishmash; $(PYTHON) setup.py install

devel: $(PY_LIB)/unsonic.egg-link

$(PY_LIB)/unsonic.egg-link: build/venv/bin/python setup.py setup.cfg README.rst 
$(PY_LIB)/unsonic.egg-link: development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	touch $@

db: devel-db
devel-db: build/development.sqlite
build/development.sqlite:
	bin/unsonic -c development.ini sync test/music
	bin/unsonic -c development.ini adduser test test

run: devel-run
devel-run: bin/unsonic build/development.sqlite
	bin/unsonic -c development.ini serve --reload

tests: tests-clean
	PYTHONPATH=external/mishmash $(PYTHON) setup.py test $(FTF)

clean:
	find unsonic external -name '*.pyc' | xargs rm -f

devel-clean:
	rm build/development.sqlite

dist-clean: clean
	rm -rf build unsonic.egg-info development.sqlite bin/unsonic bin/unsonic-server

tests-clean:
	rm -f build/testing.sqlite build/testing.sqlite.org

.PHONY: devel db pyramid paste sqlalchemy psycopg2 run tests clean 
.PHONY: dist-clean external
