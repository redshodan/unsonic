VBIN=build/venv/bin
VLIB=build/venv/lib
PYTHON=$(VBIN)/python
ifeq ($(shell [ -f $(PYTHON) ] && echo 1), 1)
PYTHON_VER=$(shell $(PYTHON) -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])')
else
# This probably wont work in all cases, but oh well. Fix it if your virtualenv 
# is not using the default python.
PYTHON_VER=$(shell python -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])')
endif
PYTHON_LIB=$(VLIB)/python$(PYTHON_VER)
PYTHON_SITE=$(PYTHON_LIB)/site-packages
PIP=$(VBIN)/pip
DEPS=$(PYTHON_SITE)/pyramid $(PYTHON_SITE)/sqlalchemy $(PYTHON_SITE)/psycopg2 $(PYTHON_SITE)/eyed3


all: deps

build:
	mkdir build

build/venv: build
	virtualenv build/venv

deps: pyramid sqlalchemy psycopg2 eyed3

pyramid: $(PYTHON_SITE)/pyramid
$(PYTHON_SITE)/pyramid: build/venv
	$(PIP) install pyramid
	touch $(PYTHON_SITE)/pyramid

sqlalchemy: $(PYTHON_SITE)/sqlalchemy
$(PYTHON_SITE)/sqlalchemy: build/venv
	$(PIP) install SQLAlchemy
	touch $(PYTHON_SITE)/sqlalchemy

psycopg2: $(PYTHON_SITE)/psycopg2
$(PYTHON_SITE)/psycopg2: build/venv
	$(PIP) install psycopg2
	touch $(PYTHON_SITE)/psycopg2

eyed3: $(PYTHON_SITE)/eyed3
$(PYTHON_SITE)/eyed3: build/venv
	$(PIP) install eyeD3
	touch $(PYTHON_SITE)/eyed3


devel: $(VBIN)/initialize_unsonic_db

$(VBIN)/initialize_unsonic_db: setup.py setup.cfg README.rst development.ini
$(VBIN)/initialize_unsonic_db: $(DEPS)
$(VBIN)/initialize_unsonic_db:
	$(PYTHON) setup.py develop
	touch $@

db: unsonic.sqlite
unsonic.sqlite: $(VBIN)/initialize_unsonic_db
	$(VBIN)/initialize_unsonic_db development.ini

run:
	$(VBIN)/pserve development.ini

clean:
	find unsonic -name '*.pyc' | xargs rm

dist-clean:
	rm -rf build unsonic.egg-info unsonic.sqlite
	find -name '*.pyc' | xargs rm

.PHONY: deps pyramid sqlalchemy psycopg2 eyed3
