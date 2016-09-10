TOPDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VBIN=$(TOPDIR)/build/venv/bin
VLIB=$(TOPDIR)/build/venv/lib
PYTHON=$(VBIN)/python
PIP=$(VBIN)/pip
PY_LIB=$(VLIB)/python*/site-packages


all: venv bins external devel

bins: bin/unsonic bin/unsonic-db

bin/unsonic: bin/unsonic.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

bin/unsonic-db: bin/unsonic-db.in
	sed "s?/usr/bin/env python?${PYTHON}?" $< > $@
	chmod +x $@

venv: build/venv/bin/python
build/venv/bin/python:
	[ ! -d build ] && mkdir build
	virtualenv -p python3 build/venv

external: mishmash-build

mishmash-build: external/mishmash $(PY_LIB)/eyed3

external/mishmash:
	cd external; hg clone 'https://bitbucket.org/nicfit/mishmash' mishmash
	# cd external; hg clone 'https://bitbucket.org/redshodan/mishmash-music-server' mishmash

$(PY_LIB)/eyed3:
	cd external/mishmash; $(PIP) install -U -r requirements.txt
#	cd external/mishmash; $(PYTHON) setup.py build

devel: $(PY_LIB)/unsonic.egg-link paste-fix

$(PY_LIB)/unsonic.egg-link: build/venv/bin/python setup.py setup.cfg README.rst 
$(PY_LIB)/unsonic.egg-link: development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	touch $@

paste-fix: $(PY_LIB)/paste/translogger.py
$(PY_LIB)/paste/translogger.py:
	cd $(PY_LIB)/paste; for a in ../Paste-*.egg/paste/*; do ln -s $$a; done

db: devel-db
devel-db: build/development.sqlite
build/development.sqlite:
	bin/unsonic-db -c development.ini init
	bin/unsonic-db -c development.ini sync
	bin/unsonic-db -c development.ini adduser test test

run: devel-run
devel-run: bin/unsonic build/development.sqlite
	bin/unsonic development.ini --reload

stat:
	-hg stat
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; echo $${dir}; cd $${dir}; hg stat); done

in:
	-hg in
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; cd $${dir}; hg in); done

pull:
	-hg pull
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; cd $${dir}; hg pull); done

out:
	-hg out
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; cd $${dir}; hg out); done

push:
	-hg push
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; cd $${dir}; hg push); done

up:
	-hg up
	-@cd external; for dir in `find -maxdepth 1 -mindepth 1 -type d`; do \
        (echo; cd $${dir}; hg up); done

tests:
	PYTHONPATH=external/mishmash $(PYTHON) setup.py test

clean:
	find unsonic external -name '*.pyc' | xargs rm -f

dist-clean: clean
	rm -rf build unsonic.egg-info development.sqlite bin/unsonic bin/unsonic-db

.PHONY: devel db pyramid paste sqlalchemy psycopg2 run tests clean 
.PHONY: dist-clean external
