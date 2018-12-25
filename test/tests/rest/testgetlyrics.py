from unsonic.views.rest import fillID
from unsonic.views.rest.getlyrics import GetLyrics
from . import buildCmd, checkResp
from unsonic.models import Track


def testGetLyrics(session):
    cmd = buildCmd(session, GetLyrics, {"artist": "Tool", "title": "Stinkfist"})
    checkResp(cmd.req, cmd(), ok504=True)


def testGetLyricsByID(session):
    row = session.query(Track).\
        filter_by(title="Harder, Better, Faster, Stronger").one_or_none()
    cmd = buildCmd(session, GetLyrics, {"id": fillID(row)})
    checkResp(cmd.req, cmd(), ok504=True)
