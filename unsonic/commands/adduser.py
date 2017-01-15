import argparse

import mishmash.config
from mishmash.commands import command

from .. import models, auth
from ..models import User


@command.register
class AddUser(command.Command):
    NAME = "adduser"

    def __init__(self, subparsers=None):
        super().__init__("Add a user to the database.", subparsers)
        self.parser.add_argument("username", nargs=1, help="Username")
        self.parser.add_argument("password", nargs=1, help="Password")
        self.parser.add_argument("roles", nargs=argparse.REMAINDER,
                                 help="Roles for the user")


    def _run(self, args=None):
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
