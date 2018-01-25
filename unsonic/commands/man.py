import os
import glob

import unsonic
from . import Command, register


@register
class Man(Command):
    NAME = "man"
    HELP = "Show the manpages for Unsonic."
    DESC = HELP
    INSTALL = os.path.join(unsonic.INSTALL, "docs/man")
    CFG_NEEDED = False
    DB_NEEDED = False


    def _initArgParser(self, parser):
        parser.add_argument("-l", "--list", action="store_true",
                            help="List the man pages")
        parser.add_argument("page", nargs='?',
                            help="The man page to view, defaults to 'unsonic'")


    def run(self, args, config):
        super()._run()
        if args.list:
            files = glob.glob(os.path.join(self.INSTALL, "*.1"))
            files = [".".join(f.split(".")[:-1]) for f in files]
            files = "  ".join([os.path.basename(f) for f in files])
            print(files)
            return

        page = args.page if args.page else "unsonic"
        f = os.path.join(self.INSTALL, page) + ".1"
        if os.path.exists(f):
            os.system("man " + f)
        else:
            print("Invalid man page: " + page)
