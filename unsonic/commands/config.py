from . import Command, register
from unsonic import models


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

        args = args or self.args

        if args.list or (not args.set and not args.get and not args.delete):
            if args.username:
                rows = models.getUserConfig(self.db_session, args.username)
                if rows is None:
                    print("User not found")
                    return
                print("User Configuration:")
                for row in rows:
                    print(f"  {row.key} = {row.value}   modified={row.modified}")
            else:
                print("Global Configuration:")
                for row in models.getGlobalConfig(self.db_session):
                    print(f"  {row.key} = {row.value}   modified={row.modified}")
            return
        elif args.set:
            words = args.set.split("=")
            if len(words) != 2:
                print("Invalid argument for --set. "
                      "Use like: --set lastfm.user=myname")
                return
            if args.username:
                models.setUserConfig(self.db_session, args.username,
                                     words[0], words[1])
                print(f"Set {words[0]} for {args.username}")
            else:
                models.setGlobalConfig(self.db_session, words[0], words[1])
                print(f"Set {words[0]}")
        elif args.get:
            if args.username:
                row = models.getUserConfig(self.db_session, args.username,
                                           key=args.get)
                if row is None:
                    print("Users configuration not found")
                    return
                print(row.value)
            else:
                row = models.getGlobalConfig(self.db_session, key=args.get)
                if row is None:
                    print("Global configuration not found")
                    return
                print(row.value)
            return
        elif args.delete:
            if args.username:
                if models.delUserConfig(self.db_session, args.username,
                                        key=args.delete):
                    print("Deleted")
                else:
                    print("Users configuration not found")
            else:
                if models.delGlobalConfig(self.db_session, key=args.delete):
                    print("Deleted")
                else:
                    print("Global configuration not found")
            return
