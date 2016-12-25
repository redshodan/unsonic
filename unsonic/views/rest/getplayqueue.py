import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import (Command, addCmd, InternalError, MissingParam, NoPerm, strDate,
               positive_t, track_t, fillTrackUser)
from ...models import User, PlayQueue


class GetPlayQueue(Command):
    name = "getPlayQueue.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        user = (session.query(User).\
                filter(User.name == self.req.authed_user.name).one_or_none())
        if not user.playqueue_mtime:
            return self.makeResp()
        playq = ET.Element("playQueue")
        playq.set("username", user.name)
        if user.playqueue_cur:
            playq.set("current", str(user.playqueue_cur))
        if user.playqueue_pos:
            playq.set("position", str(user.playqueue_pos))
        playq.set("changed", strDate(user.playqueue_mtime))
        playq.set("changedBy", user.playqueue_mby)

        for pq in user.playqueue:
            playq.append(fillTrackUser(session, pq.track, None,
                                       self.req.authed_user, "entry"))

        return self.makeResp(child=playq)


addCmd(GetPlayQueue)
