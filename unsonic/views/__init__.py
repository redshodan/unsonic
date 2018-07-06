import os
import traceback

from pyramid.response import FileResponse
from pyramid.renderers import render
from pyramid.security import Allow, Authenticated, DENY_ALL

from nicfit.console.ansi import Fg

from ..auth import Roles
from ..models import Session
from ..log import log


# TODO: find the actual ignored articles
DEFAULT_IGNORED_ARTICLES = ["The"]


class RouteContext(object):
    __acl__ = [(Allow, Authenticated, Roles.USERS), DENY_ALL]

    def __init__(self, request):
        pass


# Exceptions
class NoPerm(Exception):
    pass


class NotFound(Exception):
    pass


class InternalError(Exception):
    pass


def faviconView(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, "..", "static", "favicon.ico")
    return FileResponse(icon, request=request)


class HTMLHandler(object):
    def __init__(self, route, req, session=None):
        self.req = req
        self.route = route
        # For testing
        self.session = session

    def __call__(self):
        try:
            if hasattr(self, "dbsess"):
                if self.session:
                    return self.handleReq(self.session)
                else:
                    with Session() as session:
                        return self.handleReq(session)
            else:
                return self.handleReq()
        except NotFound as e:
            return self.makeResp(status=404, desc="File not found")
        except InternalError as e:
            return self.makeResp(status=500)
        except NoPerm as e:
            return self.makeResp(status=403, desc="Not allowed for this file")
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise

    def handleReq(self, session=None):
        raise Exception("Command must implement handleReq()")

    def makeResp(self, body=None, status=200, desc=None):
        resp = self.req.response
        resp.status = status
        if status != 200 and not body:
            resp.text = render("../templates/error.mako", {"desc": desc})
        resp.content_type = "text/html"
        if body:
            resp.text = body
        resp.charset = "UTF-8"
        log.debug("makeResponse(%s): %d: %s" % (self.name, status, desc))
        return resp

    def makeBinaryResp(self, binary, mimetype, md5=None, status=200):
        resp = self.req.response
        resp.status = status
        resp.content_type = mimetype
        if md5:
            resp.content_md5 = md5
        resp.body = binary
        log.debug("makeBinaryResponse(%s): %d" % (self.name, status))
        return resp
