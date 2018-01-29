import os

import unsonic
from . import Command, register


###
### To system packagers (if there are any..)
###
### Feel free to disable this command as this stuff should be handled in the
### package. Just remove the import of install in this directories __init__.py.
###


@register
class Install(Command):
    NAME = "install"
    HELP = "Install the Unsonic service."
    DESC = "Install the Unsonic service. Requires root permissions."
    CFG_NEEDED = False
    DB_NEEDED = False


    def _initArgParser(self, parser):
        parser.add_argument("-u", "--user", default="unsonic",
                            help="User to run unsonic as. default: unsonic")
        parser.add_argument("-r", "--rundir", default="/var/lib/unsonic",
                            help=("Where unsonic's files are located. "
                                  "default: /var/lib/unsonic"))


    def run(self, args, config):
        super()._run()
        cmd = "/bin/bash %s %s %s %s %s" % (
            os.path.join(unsonic.INSTALL, "etc/install.sh"),
            unsonic.CMD, unsonic.INSTALL, args.user, args.rundir)

        os.system(cmd)
