import os
from . import models, log, auth

# Used by pkg_resources and Pyramid to load the webapp
from .web import main


HERE = os.getcwd()
