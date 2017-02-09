import datetime

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import Command, addCmd, bool_t, track_t, NotFound
from ...models import PlayCount, Track, dbinfo
from ...models import Scrobble as DBScrobble


class Scrobble(Command):
    name = "scrobble.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "time": {},
        "submission": {"default": bool_t},
        }
    dbsess = True


    def handleReq(self, session):
        if not self.params["submission"]:
            # User is listening, not scrobbling yet
            dbinfo.users[self.req.authed_user.name].listening = self.params["id"]
        else:
            # Check track id
            try:
                session.query(Track).options(subqueryload("*")).filter(
                    Track.id == self.params["id"]).one()
            except NoResultFound:
                raise NotFound("Track not found")

            # Inc play count
            try:
                pcount = session.query(PlayCount). \
                           options(subqueryload("*")). \
                           filter(PlayCount.track_id == self.params["id"],
                                  PlayCount.user_id ==
                                  self.req.authed_user.id).one()
                pcount.count = pcount.count + 1
            except NoResultFound:
                pcount = PlayCount(track_id=self.params["id"],
                                   user_id=self.req.authed_user.id,
                                   count=1)
                session.add(pcount)
            session.flush()

            # Local scrobble
            scrobble = DBScrobble(user_id=self.req.authed_user.id,
                                  track_id=self.params["id"],
                                  tstamp=datetime.datetime.now())
            session.add(scrobble)
        return self.makeResp()


addCmd(Scrobble)
