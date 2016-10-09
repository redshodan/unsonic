import transaction, datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import (Command, addCmd, InternalError, MissingParam, NoPerm, fillUser,
               bool_t)
from ...models import User, Role
from ...auth import Roles


class CreateUser(Command):
    name = "createUser.view"
    param_defs = {
        "username": {"required": True},
        "password": {"required": True},
        "email": {},
        # "ldapAuthenticated"  # Skipping
        "adminRole": {"type": bool_t},
        "settingsRole": {"type": bool_t},
        "streamRole": {"type": bool_t},
        "jukeboxRole": {"type": bool_t},
        "downloadRole": {"type": bool_t},
        "uploadRole": {"type": bool_t},
        "playlistRole": {"type": bool_t},
        "coverArtRole": {"type": bool_t},
        "commentRole": {"type": bool_t},
        "podcastRole": {"type": bool_t},
        "shareRole": {"type": bool_t},
        "videoConversionRole": {"type": bool_t},
        # "musicFolderI": {}, # TODO
        }
    dbsess = True
    role_names = {"adminRole": Roles.ADMIN, "settingsRole": Roles.SETTINGS,
                  "streamRole": Roles.STREAM, "jukeboxRole": Roles.JUKEBOX,
                  "downloadRole": Roles.DOWNLOAD, "uploadRole": Roles.UPLOAD,
                  "playlistRole": Roles.PLAYLIST, "coverArtRole": Roles.COVERART,
                  "commentRole": Roles.COMMENT, "podcastRole": Roles.PODCAST,
                  "shareRole": Roles.SHARE,
                  "videoConversionRole": Roles.VIDEOCONVERSION}


    def handleReq(self, session):
        if not self.req.authed_user.isAdmin():
            raise NoPerm("Can not create a user unless you are an admin")

        name = self.params["username"]
        user = session.query(User).filter(User.name == name).one_or_none()
        if user:
            raise InternalError("User '%s' already exists" % name)
        
        user = User(name=name,
                    password=self.params["password"],
                    email=self.params["email"])
        session.add(user)
        session.flush()

        for role, un_role in self.role_names.items():
            if self.params[role]:
                session.add(Role(user_id=user.id, name=un_role))
        session.add(Role(user_id=user.id, name=Roles.USERS))
        session.add(Role(user_id=user.id, name=Roles.REST))
        
        return self.makeResp()


addCmd(CreateUser)
