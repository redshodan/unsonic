import argparse

from . import Command, register
from .. import models, auth
from ..models import User, initAlembic


@register
class AddUser(Command):
    NAME = "adduser"
    HELP = "Add a user to the database."


    def _initArgParser(self, parser):
        parser.add_argument("username", nargs=1, help="Username")
        parser.add_argument("password", nargs=1, help="Password")
        parser.add_argument("roles", nargs=argparse.REMAINDER,
                            help="Roles for the user")


    def _run(self, args=None):
        initAlembic()

        args = args or self.args

        if len(args.roles):
            for role in [auth.Roles.REST, auth.Roles.USERS]:
                if role not in args.roles:
                    args.roles.append(role)
        else:
            args.roles = auth.Roles.def_user_roles

        res = self.db_session.query(User).filter(User.name == args.username[0])
        if res.one_or_none():
            print("User '%s' already exists." % args.username[0])
            return -1
        else:
            ret = models.addUser(self.db_session, args.username[0],
                                 args.password[0], args.roles)
            if ret is True:
                print("Added user '%s'." % args.username[0])
                return 0
            else:
                print(ret)
                return -1
