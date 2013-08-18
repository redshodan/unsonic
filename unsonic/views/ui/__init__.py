import os

from pyramid.response import FileResponse

from ...models import Roles


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

    repls = {"rest":req.route_url("rest"),
             "home":req.route_url("home"),
             "user":req.authed_user.name.encode("utf-8")}
    print(req.authed_user.name, type(req.authed_user.name))
    print(repls)
    body = open(fname).read()
    for key, val in repls.iteritems():
        body = body.replace("%%%s%%" % key, val)

    resp.charset = "UTF-8"
    resp.body = body
    return resp


def index(request):
    here = os.path.dirname(__file__)
    index = os.path.join(here, 'index.html')
    return FileResponse(index, request=request)


def init(global_config, config):
    config.add_route("/ui/js/global.js", "/ui/js/global.js",
                     factory="unsonic.views.RouteContext")
    config.add_view("unsonic.views.ui.view", route_name="/ui/js/global.js",
                    permission=Roles.USERS)

    config.add_static_view('ui', 'unsonic.views:ui/', cache_max_age=3600,
                           factory="unsonic.views.RouteContext",
                           permission=Roles.USERS)
