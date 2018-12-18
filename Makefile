ifeq "$(origin VIRTUAL_ENV)" "undefined"
	VENV=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))/venv
else
	VENV=$(VIRTUAL_ENV)
endif

VBIN=$(VENV)/bin
VLIB=$(VENV)/lib
VSRC=$(VENV)/src
PYTHON=$(VBIN)/python
PYTEST=$(VBIN)/pytest
PIP=$(VBIN)/pip
FLAKE8=$(VBIN)/flake8
PY_LIB=$(VLIB)/python*/site-packages

# Files to be staged for the dist build.
PKG_FILES=unsonic setup.py setup.cfg requirements.txt AUTHORS CHANGES.md CODE_OF_CONDUCT.md CONTRIBUTING.md COPYING LICENSE MANIFEST.in README.md

all: venv bins build

venv: $(VENV)/bin/python
$(VENV)/bin/python:
	virtualenv -p python3 $(VENV)

bins: bin/unsonic bin/unsonic-server

bin/unsonic: bin/unsonic.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

bin/unsonic-server: bin/unsonic-server.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

build: venv bins
	$(PIP) install .
	rm -rf unsonic.egg-info

devel: build $(PY_LIB)/unsonic.egg-link $(FLAKE8)

devel-external: build devel-eyed3 devel-mishmash

devel-eyed3: $(PY_LIB)/eyeD3.egg-link
$(PY_LIB)/eyeD3.egg-link: venv
	[ -f $(VENV)/lib/python3.6/site-packages/eyed3 ] && $(PIP) uninstall eyeD3 || true
	$(PIP) install -e git+git://github.com/nicfit/eyeD3.git#egg=eyeD3
	cd $(PY_LIB); rm -rf eyed3; ln -sf ../../../src/eyed3/src/eyed3

devel-mishmash: $(PY_LIB)/MishMash.egg-link
$(PY_LIB)/MishMash.egg-link: venv
	[ -f $(VENV)/lib/python3.6/site-packages/mishmash ] && $(PIP) uninstall mishmash || true
	$(PIP) install -e git+git://github.com/nicfit/mishmash.git#egg=mishmash
	cd $(PY_LIB); rm -rf mishmash; ln -sf ../../../src/mishmash/mishmash

$(PY_LIB)/unsonic.egg-link: $(VENV)/bin/python setup.py setup.cfg README.md
$(PY_LIB)/unsonic.egg-link: unsonic/etc/development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	cd $(PY_LIB); rm -rf unsonic; ln -sf ../../../../unsonic
	rm -rf unsonic.egg-info
	touch $@

db: $(VENV)/production.sqlite
$(VENV)/production.sqlite: bin/unsonic
	bin/unsonic -c unsonic/etc/production.ini sync
	bin/unsonic -c unsonic/etc/production.ini adduser test test

devel-db: $(VENV)/development.sqlite
$(VENV)/development.sqlite: bin/unsonic
	bin/unsonic -c unsonic/etc/development.ini sync
	bin/unsonic -c unsonic/etc/development.ini adduser test test

run: $(VENV)/production.sqlite
	bin/unsonic -c unsonic/etc/production.ini serve -- --reload

devel-run: $(VENV)/development.sqlite
	bin/unsonic -c unsonic/etc/development.ini serve -- --reload

# Ignore future warning for flake8 itself
check: $(FLAKE8)
	PYTHONWARNINGS=ignore $(FLAKE8)

TEST_POSTGRES_OPTS=--pg-image postgres:9.6-alpine
tests: pytest tests-clean
ifdef FTF
	PYTEST_ADDOPTS="${TEST_POSTGRES_OPTS}" $(PYTHON) setup.py test --addopts "-k $(FTF)"
else
	PYTEST_ADDOPTS="${TEST_POSTGRES_OPTS}" $(PYTHON) setup.py test
endif
	rm -rf unsonic.egg-info

coverage: pytest tests-clean
ifdef FTF
	PYTEST_ADDOPTS="${TEST_POSTGRES_OPTS}" $(VBIN)/coverage run --source=unsonic setup.py test --addopts "-k $(FTF)"
else
	PYTEST_ADDOPTS="${TEST_POSTGRES_OPTS}" $(VBIN)/coverage run --source=unsonic setup.py test
endif
	rm -rf unsonic.egg-info

coverage-report:
	 $(VBIN)/coverage report

coverage-clean:
	 $(VBIN)/coverage erase

pytest: $(PYTEST)
$(PYTEST): requirements-test.txt
	$(PIP) install -r requirements-test.txt

$(FLAKE8): requirements-test.txt
	$(PIP) install -r requirements-test.txt

docs:
	make -C docs man html

# Stage the files for sdist because setuptools doesn't let me filter enough
pkg-clean:
	rm -rf $(VENV)/pkg

pkg-copy: pkg-clean
	[ -d $(VENV)/pkg ] || mkdir $(VENV)/pkg
	for F in $(PKG_FILES); do cp -ar $$F $(VENV)/pkg/`basename $$F`; done
	mkdir $(VENV)/pkg/unsonic/docs
	cp -ar $(VENV)/docs/html $(VENV)/pkg/unsonic/docs
	cp -ar $(VENV)/docs/man $(VENV)/pkg/unsonic/docs

dist: sdist
sdist: venv build docs pkg-copy
	[ -d dist ] || mkdir dist
	(cd $(VENV)/pkg; $(PYTHON) setup.py sdist)
	cp -af $(VENV)/pkg/dist/* dist

clean:
	find unsonic test -name '__pycache__' -type d | xargs rm -rf
	find unsonic test -name '*.pyc' | xargs rm -f

devel-clean:
	rm -f $(VENV)/development.sqlite

# Only remove local files, not provided VIRTUAL_ENV var
dist-clean: clean
	rm -rf venv bin/unsonic bin/unsonic-server build dist unsonic.egg-info

tests-clean:
	rm -f $(VENV)/testing.sqlite $(VENV)/testing.sqlite.org

DOCKER_COMPOSE := docker-compose -f docker/docker-compose.yml
image:
	@$(DOCKER_COMPOSE) build

docker: image
	@test -n "${MUSIC_DIR}" || (echo "MUSIC_DIR volume directy required" && false)
	@$(DOCKER_COMPOSE) create --no-recreate

docker-sqlite: docker
	$(DOCKER_COMPOSE) up unsonic-sqlite

docker-postgres: docker
	@$(DOCKER_COMPOSE) up -d postgres
	@sleep 3
	@$(DOCKER_COMPOSE) up unsonic-postgres

docker-clean:
	-for cont in PostgreSql Unsonic-sqlite Unsonic-postgres; do \
        docker stop $$cont;\
        docker rm $$cont;\
    done
	-docker rmi -f unsonic

.PHONY: devel db pyramid paste sqlalchemy psycopg2 run test tests clean mishmash mishmash.egg
.PHONY: dist-clean devel-external docker docs pkg-copy venv build
