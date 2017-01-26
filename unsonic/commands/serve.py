import os, argparse

from nicfit import command
from mishmash.core import Command


@command.register
class Serve(Command):
    NAME = "serve"
    HELP = "Run the unsonic web interface using the Pyramid pserve script."


    def __init__(self, subparsers=None):
        super().__init__(subparsers)


    def _initArgParser(self, parser):
        parser.add_argument("--reload", action="store_true",
                            help="Use auto-restart file monitor")
        parser.add_argument("pserve_args", nargs=argparse.REMAINDER,
                            help="Pyramid pserve arguments")


    def _run(self, args=None):
        args = args or self.args

        # unsonic-server is needed to keep the cmdline args for pserve for its
        # reload option with hupper, otherwise pserve/hupper gets confused.
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../",
                                            "bin/unsonic-server"))
        argv = [path]
        if args.reload:
            argv.append("--reload")
        argv.extend(args.pserve_args)
        argv.append(str(self.config.filename))
        os.execv(path, argv)
