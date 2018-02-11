from . import Command, register
from unsonic.config import CONFIG, ConfigException


@register
class Config(Command):
    NAME = "config"
    HELP = "See/edit the Unsonic configuration."
    DESC = "A general interface for various configurable toggles."

    def _initArgParser(self, parser):
        parser.add_argument("-l", "--list", dest="list", action="store_true",
                            help="list the configurables available")
        parser.add_argument("-s", "--set", dest="set", metavar="KEY=VALUE",
                            help="set the named configurable to VALUE")
        parser.add_argument("-g", "--get", dest="get", metavar="KEY",
                            help="get the named configurable value")
        parser.add_argument("-d", "--del", dest="delete", metavar="KEY",
                            help="delete the named configurable value")
        parser.add_argument("username", nargs="?",
                            help=("user name for user specific configuration, "
                                  "leave empty for global configuration"))

    def _run(self, args=None):
        super()._run()

        try:
            return self._run2(args=args)
        except ConfigException as e:
            print(e)
            return -1

    def _run2(self, args=None):
        from unsonic.config import CONFIG

        args = args or self.args

        if args.list or (not args.set and not args.get and not args.delete):
            if args.username:
                print(f"User Configuration for: {args.username}")
                for row in CONFIG.getDbValue(self.db_session,
                                             username=args.username):
                    print(f"  {row.key} = {row.value}   modified={row.modified}")
            else:
                print("Global Configuration:")
                for row in CONFIG.getDbValue(self.db_session):
                    print(f"  {row.key} = {row.value}   modified={row.modified}")
            return 0
        elif args.set:
            words = args.set.split("=")
            if len(words) != 2:
                print("Invalid argument for --set. "
                      "Use like: --set lastfm.user=myname")
                return -1
            if args.username:
                CONFIG.setDbValue(self.db_session, words[0], words[1],
                                  username=args.username,)
                print(f"Set {words[0]} for {args.username}")
            else:
                CONFIG.setDbValue(self.db_session, words[0], words[1])
                print(f"Set {words[0]}")
            return 0
        elif args.get:
            if args.username:
                row = CONFIG.getDbValue(self.db_session, key=args.get,
                                        username=args.username)
                if row is None:
                    print(f"User configuration {args.get} not found")
                    return -1
                print(row.value)
            else:
                row = CONFIG.getDbValue(self.db_session, key=args.get)
                if row is None:
                    print(f"Global configuration {args.get} not found")
                    return -1
                print(row.value)
            return 0
        elif args.delete:
            if CONFIG.delDbValue(self.db_session, args.delete,
                                 username=args.username):
                print("Deleted")
                return 0
            else:
                if args.username:
                    print("Users configuration not found")
                else:
                    print("Global configuration not found")
                return -1
