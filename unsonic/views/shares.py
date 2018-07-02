from pyramid.response import FileResponse
from pyramid.renderers import render
from pyramid.security import Allow, Everyone, NO_PERMISSION_REQUIRED

from .rest import Command, NotFound
from ..models import Share, ShareEntry


class RouteContext(object):
    __acl__ = [(Allow, Everyone, NO_PERMISSION_REQUIRED)]

    def __init__(self, request):
        pass


# The /shares/{id} endpoint to retrieve a share
class Shares(Command):
    name = "shares"
    path = "/shares/{id}"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        share_uuid = self.req.matchdict["id"]
        row = session.query(Share).filter(Share.uuid == share_uuid).one_or_none()
        if not row:
            raise NotFound(f"Invalid share id: {share_uuid}")

        url_base = self.req.path_url.rstrip(self.req.path) + "/shares/%s.mp3"
        tracks = []
        for entry in row.entries:
            if entry.album_id:
                idx = 0
                for track in entry.album.tracks:
                    tracks.append([track,
                                   url_base % ("%s-%s" % (entry.uuid, idx))])
                    idx += 1
            elif entry.track_id:
                tracks.append([entry.track, url_base % entry.uuid])
            elif entry.playlist_id:
                idx = 0
                for track in entry.playlist.tracks:
                    tracks.append([track,
                                   url_base % ("%s-%s" % (entry.uuid, idx))])
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

        resp = self.req.response
        resp.text = result
        resp.content_type = "text/html"
        resp.charset = "UTF-8"
        return resp


# The /shares/{id}.mp3 endpoint to retrieve a shared media file
class SharesMP3(Command):
    name = "shares.mp3"
    path = "/shares/{id}.mp3"
    param_defs = {}
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

        path = None
        if row.album_id:
            if share_index < len(row.album.tracks):
                path = row.album.tracks[share_index].path
        elif row.track_id:
            path = row.track.path
        elif row.playlist_id:
            if share_index < len(row.playlist.tracks):
                path = row.playlist.tracks[share_index].path

        if not path:
            raise NotFound(f"Invalid share id: {full_share_uuid}")

        resp = FileResponse(path)
        resp.content_type = "audio/mp3"
        return resp
