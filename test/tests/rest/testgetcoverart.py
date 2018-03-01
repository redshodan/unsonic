from unsonic.views.rest.getcoverart import GetCoverArt
from unsonic.views.rest import Command
from unsonic.models import Image
from . import buildCmd, checkResp


def testBasic(session):
    cmd = buildCmd(session, GetCoverArt, {"id": "al-1"})
    resp = cmd()
    image = session.query(Image).filter_by(id=1).one_or_none()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testNoID(session):
    cmd = buildCmd(session, GetCoverArt)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
