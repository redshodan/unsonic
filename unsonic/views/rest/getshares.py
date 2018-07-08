import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillShare
from ...models import Share


@registerCmd
class GetShares(Command):
    name = "getShares.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        shares = ET.Element("shares")
        for share in session.query(Share).filter(
                Share.user_id == self.req.authed_user.id).all():
            shares.append(fillShare(session, self.req, share))

        return self.makeResp(child=shares)
