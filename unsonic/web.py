import os
import sys
import time
from pkg_resources import load_entry_point

from pyramid.config import Configurator

import unsonic
from . import models, auth
from .views import rest, ui
from .config import HereConfig
from .translogger import ColorTransLogger


__requires__ = 'pyramid>=1.4.3'


NAME = "Unsonic"
UI = None
CONFIG_FILE = None
CONFIG = None
SETTINGS = None


def init(global_config, settings, dbinfo=None):
    global CONFIG_FILE, CONFIG, SETTINGS

    # Stash the global config bits
    CONFIG_FILE = global_config["__file__"]
    unsonic.HERE = global_config["here"]
    SETTINGS = settings
    CONFIG = HereConfig(CONFIG_FILE)
    CONFIG.read()

    # Setup models
    models.init(settings, True, db_info=dbinfo)
    models.load()

    install = "/".join(os.path.dirname(__file__).split("/")[:-1])
    global_config["install"] = install

    unsonic.log.resetupLogging(global_config["__file__"], global_config)


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    # log.setupMash()
    init(global_config, settings)

    # Pyramid framework
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600,)
    config.add_route('home', '/', factory="unsonic.views.RouteContext")
    config.add_view('unsonic.views.ui.view', route_name='home',
                    permission=auth.Roles.USERS)
    config.scan()

    global NAME, UI
    NAME = CONFIG.get("unsonic", "name")
    UI = CONFIG.get("unsonic", "ui")

    # Init auth
    auth.init(global_config, config)

    # Init ui
    ui.init(global_config, config)

    # Add the rest interfaces
    config.add_route("rest", "/rest", factory="unsonic.views.rest.RouteContext")
    for cmd in rest.commands.values():
        cmd.settings = settings
        config.add_route(cmd.name, "/rest/" + cmd.name,
                         factory="unsonic.views.rest.RouteContext")
        config.add_view(cmd, route_name=cmd.name, permission=auth.Roles.REST)
        # Clementine calls some API's with the wrong caps.. sigh
        name = cmd.name[0].upper() + cmd.name[1:]
        config.add_route(name, "/rest/" + name,
                         factory="unsonic.views.rest.RouteContext")
        config.add_view(cmd, route_name=name, permission=auth.Roles.REST)

    # Log requests
    app = config.make_wsgi_app()
    return ColorTransLogger(app, setup_console_handler=False)


# Wrapper around the pserve script to catch syntax and import errors
def webServe():
    if "--reload" in sys.argv:
        reload = True
    else:
        reload = False

    wait = 3
    while True:
        try:
            sys.exit(load_entry_point('pyramid>=1.4.3', 'console_scripts',
                                      'pserve')())
            break
        except IndentationError as e:
            if reload:
                print("Failed to (re)start unsonic:", e)
                print("Restarting in %d seconds..." % wait)
            else:
                raise
        except SyntaxError as e:
            if reload:
                print("Failed to (re)start unsonic:", e)
                print("Restarting in %d seconds..." % wait)
            else:
                raise
        except ImportError as e:
            if reload:
                print("Failed to (re)start unsonic:", e)
                print("Restarting in %d seconds..." % wait)
            else:
                raise
        time.sleep(wait)
