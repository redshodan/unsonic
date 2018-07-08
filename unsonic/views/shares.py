from pyramid.response import FileResponse, Response
from pyramid.renderers import render
from pyramid.security import Allow, Everyone, NO_PERMISSION_REQUIRED

from . import HTMLHandler, NotFound
from ..models import Share, ShareEntry, Image
from .rest import getArtworkByID


class RouteContext(object):
    __acl__ = [(Allow, Everyone, NO_PERMISSION_REQUIRED)]

    def __init__(self, request):
        pass


# The /shares/{id} endpoint to retrieve a share
class Shares(HTMLHandler):
    name = "shares"
    path = "/shares/{id}"
    dbsess = True


    def handleReq(self, session):
        share_uuid = self.req.matchdict["id"]
        row = session.query(Share).filter(Share.uuid == share_uuid).one_or_none()
        if not row:
            raise NotFound(f"Invalid share id: {share_uuid}")

        url_base = self.req.path_url.rstrip(self.req.path) + "/shares/"
        tracks = []
        for entry in row.entries:
            if entry.album_id:
                idx = 0
                for track in entry.album.tracks:
                    tracks.append([track,
                                   url_base + ("%s-%s.track" %
                                               (entry.uuid, idx)),
                                   url_base + ("%s.coverart" % entry.uuid)])
                    idx += 1
            elif entry.track_id:
                tracks.append([entry.track,
                               "%s%s.track" % (url_base, entry.uuid),
                               "%s%s.coverart" % (url_base, entry.uuid)])
            elif entry.playlist_id:
                idx = 0
                for track in entry.playlist.tracks:
                    tracks.append([track,
                                   url_base + ("%s-%s.track" %
                                               (entry.uuid, idx)),
                                   url_base + ("%s.coverart" % entry.uuid)])
                    idx += 1

        result = render("../templates/amplitude.mako",
                        {"attrs": {},
                         "description": row.description,
                         "created": row.created,
                         "last_visited": row.last_visited,
                         "expires": row.expires,
                         "visit_count": row.visit_count,
                         'tracks': tracks},
                        request=self.req)

        return self.makeResp(result)


# The /shares/{id}.track endpoint to retrieve a shared track
class SharesTrack(HTMLHandler):
    name = "shares.track"
    path = "/shares/{id}.track"
    dbsess = True


    def handleReq(self, session):
        full_share_uuid = self.req.matchdict["id"]

        if "-" in full_share_uuid:
            try:
                share_uuid, share_index = full_share_uuid.split("-")
                share_index = int(share_index)
            except:
                raise NotFound(f"Invalid share id: {full_share_uuid}")
        else:
            share_uuid = full_share_uuid
            share_index = 0

        row = session.query(ShareEntry).\
              filter(ShareEntry.uuid == share_uuid).one_or_none()
        if not row:
            raise NotFound(f"Invalid share id: {full_share_uuid}")

        if row.album_id:
            if share_index < len(row.album.tracks):
                path = row.album.tracks[share_index].path
        elif row.track_id:
            path = row.track.path
        elif row.playlist_id:
            if share_index < len(row.playlist.tracks):
                path = row.playlist.tracks[share_index].path
        else:
            raise NotFound(f"Invalid share id: {full_share_uuid}")

        resp = FileResponse(path)
        resp.content_type = "audio/mp3"
        return resp


# The /shares/{id}.coverart endpoint to retrieve a shared coverart picture
class SharesCoverart(HTMLHandler):
    name = "shares.coverart"
    path = "/shares/{id}.coverart"
    dbsess = True


    def handleReq(self, session):
        share_uuid = self.req.matchdict["id"]

        row = session.query(ShareEntry).\
              filter(ShareEntry.uuid == share_uuid).one_or_none()
        if not row:
            raise NotFound(f"Invalid share id: {share_uuid}")

        image = None
        if row.album_id:
            if row.album.images:
                image = row.album.images[0]
                mime_type = image.mime_type
                image = image.data
            else:
                image, mime_type = getArtworkByID(session,
                                                  "al-%d" % row.album_id)
        elif row.track_id:
            if row.track.album and row.track.album.images:
                image = row.track.album.images[0]
                mime_type = image.mime_type
                image = image.data
            else:
                image, mime_type = getArtworkByID(session,
                                                  "tr-%d" % row.track_id)
        elif row.playlist_id and row.playlist.images:
            image = row.playlist.images[0]
            mime_type = image.mime_type
            image = image.data
        else:
            return FileResponse("unsonic/static/headphones.png")

        return Response(content_type=mime_type, body=image)


# Order matters for the route matching
handlers = [SharesTrack, SharesCoverart, Shares]
