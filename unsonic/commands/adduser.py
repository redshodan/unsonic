import argparse

from . import Command, register
from .. import models, auth
from ..models import User


@register
class AddUser(Command):
    NAME = "adduser"
    HELP = "Add a user to the database."
    DESC = "Adds a user to the database with the prefered roles."


    def _initArgParser(self, parser):
        parser.add_argument("-l", "--list-roles", dest="list_roles",
                            action="store_true", help="list the roles available")
        parser.add_argument("username", nargs="?", help="users name")
        parser.add_argument("password", nargs="?", help="users password")
        parser.add_argument("roles", nargs=argparse.REMAINDER,
                            help="users roles")


    def _run(self, args=None):
        super()._run()
        args = args or self.args

        if args.list_roles:
            print("Subsonic API roles: [" +
                  ", ".join(auth.Roles.subsonic_roles) + "]")
            print("Admin user roles: [" +
                  ", ".join(auth.Roles.admin_roles) + "]")
            print("Default user roles: [" +
                  ", ".join(auth.Roles.def_user_roles) + "]")
            return 0

        if not args.username or not args.password:
            print("Missing username or password arguments.")
            return -1

        if len(args.roles):
            for role in [auth.Roles.REST, auth.Roles.USERS]:
                if role not in args.roles:
                    args.roles.append(role)
        else:
            args.roles = auth.Roles.def_user_roles

        res = self.db_session.query(User).filter(User.name == args.username)
        if res.one_or_none():
            print("User '%s' already exists." % args.username)
            return -1
        else:
            ret = models.addUser(self.db_session, args.username,
                                 args.password, args.roles)
            if ret:
                print("Added user '%s'." % args.username)
                return 0
            else:
                print(ret)
                return -1
