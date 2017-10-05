import argparse
import unsonic
import unsonic.commands         # noqa: F401
from unsonic import version
from nicfit import Command

import mishmash
from mishmash.__main__ import MishMash
from mishmash import __about__


VERSION = "unsonic (%s, protocol: %s, subsonic protocol: %s) mishmash (%s)" % \
          (version.VERSION, version.UNSONIC_PROTOCOL_VERSION,
           version.PROTOCOL_VERSION, __about__.__version__)


class Unsonic(MishMash):

    def __init__(self):
        super().__init__(progname="unsonic")


    # hack in the unsonic version
    def _addArguments(self, parser):
        super()._addArguments(parser)
        for index in range(len(parser._actions)):
            if isinstance(parser._actions[index], argparse._VersionAction):
                parser._actions[index].version = VERSION
                break


def buildApp():
    if "web" in Command._all_commands:
        del Command._all_commands["web"]
    if mishmash.commands.web.Web.name in Command._all_commands:
        del Command._all_commands[mishmash.commands.web.Web.name]
    return Unsonic()


def run(args=None):
    app = buildApp()
    return app.run(args)


def main(args=None):
    app = buildApp()
    return app.main(args)


if __name__ == "__main__":
    run()
