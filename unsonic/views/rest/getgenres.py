import xml.etree.ElementTree as ET

from . import Command, addCmd
from ...models import Session


class GetGenres(Command):
    name = "getGenres.view"
    param_defs = {}
    dbsess = True

    
    def handleReq(self, session):
        genres = ET.Element("genres")
        for row in session.query(Genre).order_by(Genre.name).all():
            genre = ET.Element("genre")
            genre.text = row.name.capitalize()
            genres.append(genre)
        return self.makeResp(child=genres)


addCmd(GetGenres)
