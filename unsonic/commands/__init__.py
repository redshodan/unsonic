# flake8: noqa: F401

from nicfit.command import register
from mishmash.core import Command

from .adduser import AddUser
from .config import Config
from .deluser import DelUser
from .listusers import ListUsers
from .password import Password
from .serve import Serve
