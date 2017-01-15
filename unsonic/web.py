import logging
import logging.config
from configparser import ConfigParser

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.paster import get_appsettings, setup_logging
from pyramid.response import FileResponse
from pyramid.view import view_config, forbidden_view_config

import unsonic
from . import log
from .views import rest, ui


NAME = "Unsonic"
CONFIG_FILE = None
CONFIG = None
SETTINGS = None


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application."""
    global CONFIG_FILE, CONFIG, SETTINGS
    from . import models, auth

    # log.setupMash()

    # Stash the global config bits
    CONFIG_FILE = global_config["__file__"]
    unsonic.HERE = global_config["here"]
    SETTINGS = settings
    CONFIG = ConfigParser()
    CONFIG.read(CONFIG_FILE)
    
    # Setup models
    models.init(settings, True)
    models.load()
    
    # Pyramid framework
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600,)
    config.add_route('home', '/', factory="unsonic.views.RouteContext")
    config.add_view('unsonic.views.ui.view', route_name='home',
                    permission=auth.Roles.USERS)
    config.scan()

    global NAME
    if "unsonic.name" in settings:
        NAME = settings["unsonic.name"]

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

    # Log requests
    app = config.make_wsgi_app()
    return TransLogger(app, setup_console_handler=False)
