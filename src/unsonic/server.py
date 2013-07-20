import argparse
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from . import rest


class Server(object):
    def __init__(self):
        pass

    def buildArgParser(self):
        parser = argparse.ArgumentParser(description="Run the Unsonic music server.")
        parser.add_argument("-i", "--ip", default="0.0.0.0",
                            help="the address to listen on (default: %(default)s)")
        parser.add_argument("-p", "--port", default="8080",
                            help="the port to listen on (default: %(default)s)")
        return parser

    def run(self):
        parser = self.buildArgParser()
        args = parser.parse_args()
        
        config = Configurator()
        for cmd in rest.commands.itervalues():
            config.add_route(cmd.name, cmd.getURL())
            config.add_view(cmd.handleReq, route_name=cmd.name)
        app = config.make_wsgi_app()
        server = make_server(args.ip, int(args.port), app)
        server.serve_forever()
