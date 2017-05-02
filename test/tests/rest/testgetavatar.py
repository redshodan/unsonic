from unsonic.views.rest.getavatar import GetAvatar
from unsonic.views.rest import Command
from unsonic.models import Image, User
from . import buildCmd, checkResp


def testGetAvatar(session, ptesting):
    cmd = buildCmd(session, GetAvatar, {"username": "test"})
    resp = cmd()
    image = session.query(Image).filter_by(id=3).one_or_none()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testGetAvatarNoAvatar(session, ptesting):
    cmd = buildCmd(session, GetAvatar, {"username": "admin"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testGetAvatarBadUser(session, ptesting):
    cmd = buildCmd(session, GetAvatar, {"username": "nosuchuser"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testGetAvatarNoID(session, ptesting):
    cmd = buildCmd(session, GetAvatar)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
