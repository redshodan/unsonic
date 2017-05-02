from unsonic.models import Track
from unsonic.views.rest.download import Download
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testDownload(session, ptesting):
    cmd = buildCmd(session, Download, {"id": "tr-1"})
    resp = cmd()
    row = session.query(Track).filter(Track.id == 1).all()[0]
    fp = open(row.path, "rb")
    streamed = fp.read()
    fp.close()
    assert len(resp.body) == len(streamed)
    assert resp.body == streamed


def testDownloadNoID(session, ptesting):
    cmd = buildCmd(session, Download)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
