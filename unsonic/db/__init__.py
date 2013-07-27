from __future__ import print_function

import sys
from pkg_resources import load_entry_point

import mishmash
from mishmash.commands import Command, makeCmdLineParser
from mishmash.database import DBInfo


def init():
    initPyramid()
    initMishMash()


# Setup the pyramid database
def initPyramid():
    global __requires__
    __requires__ = 'unsonic==0.0'
    load_entry_point('unsonic==0.0', 'console_scripts', 'initialize_unsonic_db')()


def initMishMash():
    makeCmdLineParser()
    # dbinfo = DBInfo("sqlite", "/tmp/unsonic.db")
    dbinfo = DBInfo(uri="sqlite:////tmp/unonsic.db")
    Command.cmds["init"].run(dbinfo)
    Command.cmds["sync"].run(dbinfo, ["/home/baron/src/unsonic/test/music"])
