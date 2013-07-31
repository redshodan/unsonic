from pyramid.config import Configurator
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config

from .views import rest


from mishmash.commands import makeCmdLineParser

from .models import DBSession, Base
from . import db


def initMishMash():
    makeCmdLineParser()

def loadMishMash(settings):
    return db.loadMishMash(settings)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # Setup mishmash
    initMishMash()
    mishmash_settings = get_appsettings(global_config["__file__"], name="mishmash")
    mash_db = loadMishMash(mishmash_settings)

    # Pyramid framework
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    
    # Add the rest interfaces
    for cmd in rest.commands.itervalues():
        cmd.mash_db = mash_db
        config.add_route(cmd.name, cmd.getURL())
        config.add_view(cmd.handleReq, route_name=cmd.name)

    return config.make_wsgi_app()
