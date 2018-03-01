from unsonic.models import Track
from unsonic.views.rest.stream import Stream
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testStream(session):
    cmd = buildCmd(session, Stream, {"id": "tr-1"})
    resp = cmd()
    row = session.query(Track).filter(Track.id == 1).all()[0]
    fp = open(row.path, "rb")
    streamed = fp.read()
    fp.close()
    assert len(resp.body) == len(streamed)
    assert resp.body == streamed


def testStreamNoID(session):
    cmd = buildCmd(session, Stream)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
