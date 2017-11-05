# flake8: noqa: F401

# Location information
import os
import sys
HERE = os.getcwd()
INSTALL = "/".join(os.path.dirname(__file__).split("/"))
CMD = os.path.abspath(sys.argv[0])
del os
del sys


# This needs to be very early in the import sequence so the monkeypatch
# works right.
from . import config

from . import models, log, auth


# Used by pkg_resources and Pyramid to load the webapp
from .web import main, webServe
