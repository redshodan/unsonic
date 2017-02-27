import os

from pyramid.response import Response, FileResponse

from ... import web
from ...auth import Roles


def view(req):
    resp = req.response

    base = os.path.dirname(__file__)[:-8]
    if req.path == "/":
        resp.content_type = "text/html"
        path = "static/index.html"
    else:
        resp.content_type = "text/javascript"
        path = os.path.join("views", req.path[1:])
    fname = os.path.join(base, path)

    repls = {"rest": req.route_url("rest"),
             "home": req.route_url("home"),
             "user": req.authed_user.name.encode("utf-8")}
    body = open(fname).read()
    for key, val in repls.items():
        body = body.replace("%%%s%%" % str(key), str(val))

    resp.charset = "UTF-8"
    resp.text = body
    return resp


def index(request):
    here = os.path.dirname(__file__)
    index = os.path.join(here, 'index.html')
    return FileResponse(index, request=request)


def notfound(request):
    return Response('Not Found', status='404 Not Found')


def init(global_config, config):
    ui = web.UI
    if not ui:
        config.add_notfound_view(notfound)
    else:
        ui = os.path.abspath(ui)
        config.add_static_view('ui', ui, cache_max_age=3600,
                               factory="unsonic.views.RouteContext",
                               permission=Roles.USERS)
