import xml.etree.ElementTree as ET
from luqum.parser import parser as LQParser
from luqum.tree import (Group, BaseOperation, OrOperation, AndOperation,
                        UnknownOperation, SearchField, Term)
from sqlalchemy import func, and_

from . import (Command, registerCmd, MissingParam, NotFound, positive_t,
               fillArtist, fillAlbum, fillTrack, folder_t)
from ...models import Artist, Album, Track
from ...log import log


# This is reverse engineered from what dsub will send for queries.
# Rules:
# - All ops have a QueryContext
# - Group and AndOperation shares QueryContext
# - OrOperation have new QueryContext for each operand
#


class QueryContext():
    def __init__(self):
        self.artist = None
        self.album = None
        self.track = None
        self.any = None


    def __str__(self):
        return f"artist={self.artist} album={self.album} track={self.track} any={self.any}"


@registerCmd
class Search2(Command):
    name = "search2.view"
    param_defs = {
        "query": {"required": True},
        "artistCount": {"default": 20, "type": positive_t},
        "artistOffset": {"default": 0, "type": positive_t},
        "albumCount": {"default": 20, "type": positive_t},
        "albumOffset": {"default": 0, "type": positive_t},
        "songCount": {"default": 20, "type": positive_t},
        "songOffset": {"default": 0, "type": positive_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams()


    def setParams(self, search_param="searchResult2"):
        self.search_param = search_param


    def query(self, session, klass):
        if self.params["musicFolderId"]:
            return (session.query(klass).
                    filter(klass.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(klass)


    def extend(self, l, item):
        if isinstance(item, list):
            l.extend(item)
        else:
            l.append(item)
        return l


    def globQuery(self, obj, query, ilike=False):
        if query.startswith("*"):
            ilike = True
            query = f"%%{query[1:]}"
        if query.endswith("*"):
            ilike = True
            query = f"{query[:-1]}%%"
        if ilike:
            return obj.ilike(query)
        else:
            return obj == query


    def searchQueryContext(self, session, qctx):
        print(f"Searching on qctx: {qctx}")
        ar_count = self.params["artistCount"]
        ar_off = self.params["artistOffset"]
        al_count = self.params["albumCount"]
        al_off = self.params["albumOffset"]
        tr_count = self.params["songCount"]
        tr_off = self.params["songOffset"]

        artists = []
        albums = []
        tracks = []
        if qctx.artist:
            artists = self.query(session, Artist). \
                            filter(self.globQuery(func.lower(Artist.name),
                                                  qctx.artist.lower())). \
                            limit(ar_count). \
                            offset(ar_off).all()
            print(f"Artists: {artists}")
            if not len(artists):
                raise NotFound("No artist found")
        if qctx.album:
            q = self.query(session, Album). \
                            filter(self.globQuery(func.lower(Album.title),
                                                  qctx.album.lower()))
            if len(artists):
                q = q.filter(Album.artist_id == artists[0].id)
            albums = q.limit(al_count).offset(al_off).all()
            print(f"Albums: {albums}")
            if not len(albums):
                raise NotFound("No albums found")
        if qctx.track:
            q = self.query(session, Track). \
                            filter(self.globQuery(func.lower(Track.title),
                                                  qctx.track.lower()))
            if len(artists):
                q = q.filter(Track.artist_id == artists[0].id)
            if len(albums):
                q = q.filter(Track.album_id == albums[0].id)
            tracks = q.limit(tr_count).offset(tr_off).all()
            print(f"Tracks: {tracks}")
            if not len(tracks):
                raise NotFound("No tracks found")

        if len(tracks):
            return [fillTrack(session, t) for t in tracks]
        elif len(albums):
            return [fillAlbum(session, a) for a in albums]
        if len(artists):
            return [fillArtist(session, a) for a in artists]
        else:
            return []

    def searchAll(self, session, query):
        ar_count = self.params["artistCount"]
        ar_off = self.params["artistOffset"]
        al_count = self.params["albumCount"]
        al_off = self.params["albumOffset"]
        tr_count = self.params["songCount"]
        tr_off = self.params["songOffset"]

        # blast sub-string match queries
        results = []
        if ar_count:
            for row in self.query(session, Artist). \
                           filter(self.globQuery(func.lower(Artist.name),
                                                 query.lower(), True)). \
                           limit(ar_count). \
                           offset(ar_off):
                artist = fillArtist(session, row)
                results.append(artist)
        if al_count:
            for row in self.query(session, Album). \
                           filter(self.globQuery(func.lower(Album.title),
                                                 query.lower(), True)). \
                           limit(al_count). \
                           offset(al_off):
                album = fillAlbum(session, row)
                results.append(album)
        if tr_count:
            for row in self.query(session, Track). \
                           filter(self.globQuery(func.lower(Track.title),
                                                 query.lower(), True)). \
                           limit(tr_count). \
                           offset(tr_off):
                track = fillTrack(session, row)
                results.append(track)
        return results


    def parsePass1(self, t, qctx, parent):
        print("pass1 top", t)
        t.parent = parent
        t.qctx = qctx
        if isinstance(t, Group):
            # Share the qctx
            print("pass1 Group")
            for c in t.children:
                print("pass1 recursing")
                self.parsePass1(c, qctx, t)
        elif isinstance(t, BaseOperation):
            print("pass1 BaseOperation")
            newctx = isinstance(t, OrOperation)
            for c in t.children:
                print("pass1 recursing")
                self.parsePass1(c, QueryContext() if newctx else qctx, t)
        elif isinstance(t, SearchField):
            print("pass1 SearchField")
            if t.name == "artist":
                qctx.artist = t.expr.value.strip('"')
            elif t.name == "album":
                qctx.album = t.expr.value.strip('"')
            elif t.name == "title":
                qctx.track = t.expr.value.strip('"')
            else:
                raise MissingParam("Invalid search field: " + t.name)
        elif isinstance(t, Term):
            print("pass1 Term")
            qctx.any = t.value.strip('"')


    def parsePass2(self, t, session):
        print("pass2 top")
        results = []
        if isinstance(t, Group):
            print("pass2 Group")
            for c in t.children:
                print("pass2 recursing")
                self.extend(results, self.parsePass2(c, session))
            return results
        elif isinstance(t, BaseOperation):
            print("pass2 BaseOperation")
            for c in t.children:
                if isinstance(c, (Group, BaseOperation)):
                    print("pass2 recursing under op")
                    self.extend(results, self.parsePass2(c, session))
            if isinstance(t, (AndOperation, UnknownOperation)):
                print("pass2 AndOperation")
                self.extend(results, self.searchQueryContext(session, t.qctx))
                if None in results:
                    return None
                else:
                    print(f"AndOperation returning {results}")
                    return results
            elif isinstance(t, OrOperation):
                print("pass2 OrOperation")
                for r in results:
                    if r is not None:
                        return [r for r in results if r]
                else:
                    return None
            else:
                raise MissingParam("Invalid operation: " + repr(t))
        elif isinstance(t, SearchField):
            print("pass2 SearchField")
            return self.searchQueryContext(session, t.qctx)
        elif isinstance(t, Term):
            print("pass2 Term")
            return self.searchAll(session, t.value.strip('"'))
        else:
            print("pass2 invalid type", type(t), t)
            raise MissingParam(f"pass2 invalid type: {type(t)}")


    def handleReq(self, session):
        query = self.params["query"]
        parsed_result = None
        result = ET.Element(self.search_param)

        try:
            tree = LQParser.parse(query)
            print("*" * 40)
            print(query)
            print(repr(tree))

            self.parsePass1(tree, QueryContext(), None)
            parsed_result = self.parsePass2(tree, session)
            print("parsed_result", parsed_result)
        except (MissingParam, NotFound) as e:
            raise e
        except Exception as e:
            log.error(f"Failed to parse search query: {query}",
                      exc_info=e)
            raise MissingParam("Invalid search query")

        if parsed_result is not None:
            for tag in parsed_result:
                result.append(tag)
            return self.makeResp(child=result)
        else:
            raise NotFound("No results found")
