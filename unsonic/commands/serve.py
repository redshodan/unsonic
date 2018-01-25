import os
import sys
import argparse
import shutil

import unsonic
from . import Command, register


@register
class Serve(Command):
    NAME = "serve"
    HELP = "Run the Unsonic web interface."
    DESC = ("Run the Unsonic web interface using the Pyramid pserve script. "
            "This interface is HTTP only and can not do HTTPS. Please read the "
            "documentation for instructions on how to run Unsonic with HTTPS.")
    DB_NEEDED = False


    def _initArgParser(self, parser):
        parser.add_argument("pserve_args", nargs=argparse.REMAINDER,
                            help="pyramid pserve arguments. Put a '--' before "
                                 "any pserve arguments.")


    def run(self, args, config):
        super()._run()
        pargs = args.pserve_args

        if not config.filename:
            print("No config file specified. Must specify a config file.")
            sys.exit(-1)

        # unsonic-server is needed to keep the cmdline args for pserve for its
        # reload option with hupper, otherwise pserve/hupper gets confused.
        paths = [os.path.abspath(
                     os.path.join(*list(os.path.split(unsonic.CMD)[:-1]) +
                                  ["unsonic-server"])),
                 os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "../../", "bin/unsonic-server")),
                 shutil.which("unsonic-server")]
        for path in paths:
            if os.access(path, os.X_OK):
                break
        else:
            path = None
        if not path:
            print("Failed to find the unsonic-server command.")
            sys.exit(-1)

        argv = [path]
        if len(pargs) and pargs[0] == "--":
            pargs = pargs[1:]
        argv.extend(pargs)
        argv.append(str(config.filename))
        print(" ".join(argv))
        os.execv(path, argv)
