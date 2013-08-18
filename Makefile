VBIN=build/venv/bin
VLIB=build/venv/lib
PYTHON=$(VBIN)/python
PY_LIB=$(VLIB)/python*/site-packages


all: bins external devel

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

external: external/jamstash external/eyed3 external/mishmash

external/jamstash:
	cd external; hg clone 'https://redshodan@bitbucket.org/redshodan/jamstash-for-unsonic' jamstash

external/eyed3:
	cd external; hg clone 'https://redshodan@bitbucket.org/redshodan/eyed3-for-unsonic' eyed3
	cd external/eyed3; paver build

external/mishmash:
	cd external; hg clone 'https://redshodan@bitbucket.org/redshodan/mishmash-music-server' mishmash

devel: $(PY_LIB)/unsonic.egg-link 

$(PY_LIB)/unsonic.egg-link: build/venv/bin/python setup.py setup.cfg README.rst 
$(PY_LIB)/unsonic.egg-link: development.ini
$(PY_LIB)/unsonic.egg-link:
	$(PYTHON) setup.py develop
	touch $@

db: devel-db
devel-db: build/development.sqlite
build/development.sqlite: bin/unsonic-db development.ini
	bin/unsonic-db -c development.ini init
	bin/unsonic-db -c development.ini sync
	bin/unsonic-db -c development.ini adduser test test

run: devel-run
devel-run: bin/unsonic build/development.sqlite
	bin/unsonic development.ini --reload

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
	PYTHONPATH=external/eyed3/src/:external/mishmash/src $(PYTHON) setup.py test

clean:
	-find unsonic external -name '*.pyc' | xargs rm

dist-clean: clean
	rm -rf build unsonic.egg-info development.sqlite bin/unsonic bin/unsonic-db

.PHONY: devel db pyramid paste sqlalchemy psycopg2 eyed3 run tests clean 
.PHONY: dist-clean external
