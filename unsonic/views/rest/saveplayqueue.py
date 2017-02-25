import datetime

from . import Command, registerCmd, positive_t, track_t
from ...models import User, PlayQueue


@registerCmd
class SavePlayQueue(Command):
    name = "savePlayQueue.view"
    param_defs = {
        "id": {"type": track_t, "multi": True},
        "current": {"type": track_t},
        "position": {"type": positive_t},
        }
    dbsess = True


    def handleReq(self, session):
        user = (session.query(User).
                filter(User.name == self.req.authed_user.name).one_or_none())
        # Delete the old playqueue
        session.query(PlayQueue).filter(PlayQueue.user_id == user.id).delete()
        # Update the user parts
        user.playqueue_cur = self.params["current"]
        if self.params["position"]:
            user.playqueue_pos = self.params["position"]
        else:
            user.playqueue_pos = 0
        if len(self.params["id"]):
            user.playqueue_mtime = datetime.datetime.now()
        else:
            user.playqueue_mtime = None
        user.playqueue_mby = self.req.user_agent
        session.add(user)
        # Create the playqueue entries
        for track_id in self.params["id"]:
            session.add(PlayQueue(user_id=user.id, track_id=track_id))
        # If no id's, then there is no playqueue and its already been deleted
        return self.makeResp()
