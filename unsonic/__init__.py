from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from . import rest


PROTOCOL_VERSION = "1.10.0"


from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    # Add the rest interfaces
    for cmd in rest.commands.itervalues():
        config.add_route(cmd.name, cmd.getURL())
        config.add_view(cmd.handleReq, route_name=cmd.name)
    return config.make_wsgi_app()
