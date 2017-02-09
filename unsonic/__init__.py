# flake8: noqa: F401

# This needs to be very early in the import sequence so the monkeypatch
# works right.
from . import config

from . import models, log, auth


# Used by pkg_resources and Pyramid to load the webapp
from .web import main, webServe


import os
HERE = os.getcwd()
del os
