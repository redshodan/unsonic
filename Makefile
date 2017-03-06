TOPDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VBIN=$(TOPDIR)build/venv/bin
VLIB=$(TOPDIR)build/venv/lib
PYTHON=$(VBIN)/python
PYTEST=$(VBIN)/pytest
PIP=$(VBIN)/pip
FLAKE8=$(VBIN)/flake8
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
	virtualenv -p python3 build/venv

external: mishmash

mishmash: external/mishmash mishmash.egg

mishmash-update:
	cd external/mishmash; git fetch
	cd external/mishmash; $(PIP) install -Ue .

external/mishmash:
	cd external; git clone 'https://github.com/nicfit/mishmash.git' mishmash

mishmash.egg: $(PY_LIB)/MishMash*.egg/mishmash
$(PY_LIB)/MishMash*.egg/mishmash:
	cd external/mishmash; $(PIP) install -Ue .

$(PYTEST): requirements-test.txt
	$(PIP) install -r requirements-test.txt

flake8: $(FLAKE8)
$(FLAKE8):
	$(PIP) install flake8

devel: $(PY_LIB)/unsonic.egg-link flake8

$(PY_LIB)/unsonic.egg-link: build/venv/bin/python setup.py setup.cfg README.rst 
$(PY_LIB)/unsonic.egg-link: development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	touch $@

db: devel-db
devel-db: devel build/development.sqlite
build/development.sqlite:
	bin/unsonic -c development.ini sync
	bin/unsonic -c development.ini adduser test test

run: devel-run
devel-run: bin/unsonic build/development.sqlite
	bin/unsonic -c development.ini serve -- --reload

check: $(FLAKE8)
	$(FLAKE8)

tests: $(PYTEST) tests-clean
	$(PYTHON) setup.py test $(FTF)

dist: sdist
sdist:
	$(PYTHON) setup.py sdist

clean:
	find unsonic external -name '*.pyc' | xargs rm -f

devel-clean:
	rm build/development.sqlite

dist-clean: clean
	rm -rf build/* bin/unsonic bin/unsonic-server dist

tests-clean:
	rm -f build/testing.sqlite build/testing.sqlite.org

docker:
	test -n "${MUSIC_DIR}" || (echo "MUSIC_DIR volume directy required" && false)
	docker-compose -f ./docker/docker-compose.yml build
	docker-compose -f ./docker/docker-compose.yml create

docker-sqlite: docker
	docker-compose -f ./docker/docker-compose.yml up unsonic-sqlite

docker-postgres: docker
	docker-compose -f ./docker/docker-compose.yml up -d postgres
	sleep 3
	docker-compose -f ./docker/docker-compose.yml up unsonic-postgres

.PHONY: devel db pyramid paste sqlalchemy psycopg2 run tests clean mishmash mishmash.egg
.PHONY: dist-clean external docker
