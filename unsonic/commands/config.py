from . import Command, register


@register
class Config(Command):
    NAME = "config"
    HELP = "See/edit the Unsonic configuration."
    DESC = "A general interface for various configurable toggles."


    def _initArgParser(self, parser):
        parser.add_argument("-l", "--list", dest="list", action="store_true",
                            help="list the configurables available")
        parser.add_argument("-s", "--set", dest="set", metavar="KEY",
                            help="set the named configurable to VALUE")
        parser.add_argument("-g", "--get", dest="list", metavar="KEY",
                            help="get the named configurable value")
        parser.add_argument("VALUE", nargs="?",
                            help="value of the configurable")


    def _run(self, args=None):
        super()._run()

        args = args or self.args
