import sys
import argparse
import unsonic
import unsonic.commands         # noqa: F401
from unsonic import version, config
from nicfit import Command

import mishmash
from mishmash.__main__ import MishMash
from mishmash import __about__


VERSION = "unsonic (%s, protocol: %s, subsonic protocol: %s) mishmash (%s)" % \
          (version.VERSION, version.UNSONIC_PROTOCOL_VERSION,
           version.PROTOCOL_VERSION, __about__.__version__)
APP = None


class Unsonic(MishMash):

    def __init__(self):
        super().__init__(progname="unsonic")
        self.cfg_found = False
        self._orig_main_func = self._main_func
        self._main_func = self.mainWrapper


    def mainWrapper(self, args):
        # Handle mishmash commands which assume a default config
        # Unsonic commands are handled in the unsonic base command class
        need_cfg = False
        if (hasattr(self.args, "command_func") and
            hasattr(self.args.command_func, "__self__")):
            need_cfg = ("mishmash.commands" in
                        self.args.command_func.__self__.__module__)
        if not self.cfg_found and need_cfg:
            print("Could not find a standardly located config. "
                  "You must specify the config file with -c argument, "
                  "example: unsonic -c /etc/unsonic.ini ...")
            sys.exit(-1)

        return self._orig_main_func(args)


    # hack in the unsonic version
    def _addArguments(self, parser):
        super()._addArguments(parser)
        for index in range(len(parser._actions)):
            if isinstance(parser._actions[index], argparse._VersionAction):
                parser._actions[index].version = VERSION
                break


def buildApp():
    global APP
    if "web" in Command._all_commands:
        del Command._all_commands["web"]
    if mishmash.commands.web.Web.name in Command._all_commands:
        del Command._all_commands[mishmash.commands.web.Web.name]
    APP = Unsonic()
    return APP


def adjustCmdline(parser):
    path = config.findConfig(parser)
    if path is False:
        APP.cfg_found = False
    elif path is not True:
        # Append the found config file
        sys.argv = sys.argv[:1] + ["-c", path] + sys.argv[1:]
        APP.cfg_found = True
    else:
        # its already supplied, just carry on
        APP.cfg_found = True


def run(args=None):
    app = buildApp()
    adjustCmdline(app.arg_parser)
    return app.run(args)


def main(args=None):
    app = buildApp()
    adjustCmdline(app.arg_parser)
    return app.main(args)


if __name__ == "__main__":
    run()
