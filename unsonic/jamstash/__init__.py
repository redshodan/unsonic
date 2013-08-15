import os

from pyramid.response import FileResponse


def view(req):
    base = os.path.dirname(__file__)[:-8]
    fname = os.path.join(base, req.path[1:])

    repls = {"server":req.route_url("rest")}
    body = open(fname).read()
    for key, val in repls.iteritems():
        body = body.replace("%%%s%%" % key, val)

    resp = req.response
    resp.content_type = "text/javascript"
    resp.charset = "UTF-8"
    resp.body = body
    return resp


def index(request):
    here = os.path.dirname(__file__)
    index = os.path.join(here, 'index.html')
    return FileResponse(index, request=request)


def init(global_config, config):
    config.add_route('jamstash_index', '/jamstash/index.html')
    config.add_view('unsonic.jamstash.index', route_name='jamstash_index')
    config.add_route('jamstash_dir', '/jamstash/')
    config.add_view('unsonic.jamstash.index', route_name='jamstash_dir')

    for dir in ["images", "style"]:
        route = os.path.join("jamstash", dir)
        config.add_static_view(route, route, cache_max_age=3600)

    jamstash_root = os.path.join(global_config["here"], "unsonic/jamstash/")
    jamstash_js = os.path.join(jamstash_root, "js")        
    files = []
    for dirpath, dirnames, filenames in os.walk(jamstash_js):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    size = len(jamstash_root)
    for f in files:
        url_part = f[size:]
        config.add_route(url_part, "/jamstash/" + url_part,
                         factory="unsonic.views.RouteContext")
        config.add_view("unsonic.jamstash.view", route_name=url_part, permission="users",)
    
