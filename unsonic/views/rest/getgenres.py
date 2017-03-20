import xml.etree.ElementTree as ET

from . import Command, registerCmd
from ...models import Tag


@registerCmd
class GetGenres(Command):
    name = "getGenres.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        genres = ET.Element("genres")
        for row in session.query(Tag).order_by(Tag.name).all():
            genre = ET.Element("genre")
            genre.text = row.name.capitalize()
            # TODO: Make this more better sqlalchemy magic?
            genre.set("songCount",
                      str(session.connection().execute(
                          "SELECT COUNT(*) FROM track_tags WHERE tag_id = %d"
                          % row.id).fetchall()[0][0]))
            # TODO: Revist this when album_tags is populated by mishmash
            genre.set("albumCount",
                      str(session.connection().execute(
                          "SELECT COUNT(*) FROM album_tags WHERE tag_id = %d"
                          % row.id).fetchall()[0][0]))
            genres.append(genre)
        return self.makeResp(child=genres)
