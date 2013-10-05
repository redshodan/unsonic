import xml.etree.ElementTree as ET

from . import Command, addCmd
from ...models import DBSession, Genre


class GetGenres(Command):
    name = "getGenres.view"
    param_defs = {}
        
    def handleReq(self):
        genres = ET.Element("genres")
        for row in DBSession.query(Genre).order_by(Genre.name).all():
            genre = ET.Element("genre")
            genre.text = row.name.capitalize()
            genres.append(genre)
        return self.makeResp(child=genres)


addCmd(GetGenres)
