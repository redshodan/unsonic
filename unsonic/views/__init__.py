import os

from pyramid.response import FileResponse
from pyramid.security import Allow, Authenticated, DENY_ALL

from ..auth import Roles

# TODO: find the actual ignored articles
DEFAULT_IGNORED_ARTICLES = ["The"]


class RouteContext(object):
    __acl__ = [(Allow, Authenticated, Roles.USERS), DENY_ALL]

    def __init__(self, request):
        pass


def faviconView(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, "..", "static", "favicon.ico")
    return FileResponse(icon, request=request)
