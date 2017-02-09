from pyramid.security import Allow, Authenticated, DENY_ALL

from ..auth import Roles


class RouteContext(object):
    __acl__ = [(Allow, Authenticated, Roles.USERS), DENY_ALL]

    def __init__(self, request):
        pass
