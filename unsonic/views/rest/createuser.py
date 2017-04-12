from . import Command, registerCmd, InternalError, NoPerm, bool_t, bitrate_t
from ...models import User, Role
from ...auth import Roles


@registerCmd
class CreateUser(Command):
    name = "createUser.view"
    param_defs = {
        "username": {"required": True},
        "password": {"required": True},
        "email": {},
        "maxBitRate": {"type": bitrate_t, "default": 0},
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
        # "musicFolderId": {}, # TODO
        }
    dbsess = True
    role_names = {"adminRole": Roles.ADMIN, "settingsRole": Roles.SETTINGS,
                  "streamRole": Roles.STREAM, "jukeboxRole": Roles.JUKEBOX,
                  "downloadRole": Roles.DOWNLOAD, "uploadRole": Roles.UPLOAD,
                  "playlistRole": Roles.PLAYLIST, "coverArtRole": Roles.COVERART,
                  "commentRole": Roles.COMMENT, "podcastRole": Roles.PODCAST,
                  "shareRole": Roles.SHARE,
                  "videoConversionRole": Roles.VIDEOCONVERSION}


    def __init__(self, route, req, session=None):
        super().__init__(route, req, session=session)
        self.update = False


    def setUpdate(self, val):
        self.update = val


    def handleReq(self, session):
        if not self.req.authed_user.isAdmin():
            raise NoPerm("Can not create a user unless you are an admin")

        name = self.params["username"]
        user = session.query(User).filter(User.name == name).one_or_none()
        if user and not self.update:
            raise InternalError("User '%s' already exists" % name)
        if not user and self.update:
            raise InternalError("User '%s' does not exist" % name)

        if not self.update:
            user = User()
        user.name = name
        user.password = self.params["password"]
        user.email = self.params["email"]
        user.maxbitrate = self.params["maxBitRate"]
        session.add(user)
        session.flush()

        for role, un_role in self.role_names.items():
            if (self.params[role] and
                (session.query(Role).filter(Role.user_id == user.id).
                 filter(Role.name == un_role).one_or_none()) is None):
                session.add(Role(user_id=user.id, name=un_role))
            if self.params[role] is False:
                session.query(Role).filter(Role.user_id == user.id).\
                    filter(Role.name == un_role).delete()

        if not self.update:
            session.add(Role(user_id=user.id, name=Roles.USERS))
            session.add(Role(user_id=user.id, name=Roles.REST))

        return self.makeResp()
