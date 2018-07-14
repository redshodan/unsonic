from pyramid.response import Response

from . import Command, registerCmd, getArtworkByID, NotFound


@registerCmd
class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}
    dbsess = True

    def handleReq(self, session):
        image, content_type = getArtworkByID(session, self.params["id"],
                                             self.req.authed_user.lastfm)
        if image is not None:
            return Response(content_type=content_type, body=image)
        else:
            raise NotFound()
