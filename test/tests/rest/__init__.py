import subprocess
import xml.etree.ElementTree as ET

from webob.multidict import MultiDict, NestedMultiDict
from pyramid import testing

from unsonic import models
from unsonic.models import Artist, Album, Track


def buildCmd(session, klass, params={}, username="test"):
    request = testing.DummyRequest()
    request.context = testing.DummyResource()
    if isinstance(params, dict):
        md = MultiDict()
        for key, val in params.items():
            md.add(key, val)
    elif isinstance(params, MultiDict):
        md = params
    else:
        raise Exception("Invalid params class type")
    request.params = NestedMultiDict(md)
    request.authed_user = models.getUserByName(session, username)
    request.user_agent = "Test/1.0 (X11; Linux x86_64) Test/1.0 Test/1.0"
    cmd = klass(None, request, session=session)
    cmd.settings = {"mishmash.paths": "Music: test/music"}
    return cmd


def checkResp(req, resp, ok=True, ok504=False):
    sub_resp = ET.fromstring(resp.body)

    # Validate the response against the XSD
    p = subprocess.Popen(["xmllint", "--format", "--schema",
                          "test/xsd/unsonic-subsonic-api.xsd", "-"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, err = p.communicate(resp.body, timeout=15)
    if p.returncode:
        assert 0, out.decode("utf-8")

    # If 504 is ok (lastfm failure) don't validate the resp at all
    if ok504 and resp.status.startswith("504 "):
        return False

    # Validate the return type
    if ok is True:
        assert sub_resp.get("status") == "ok", resp.body
        assert resp.status == "200 OK"
    else:
        assert sub_resp.get("status") == "failed", resp.body
        error = sub_resp.find("{http://subsonic.org/restapi}error")
        assert error.get("code") == ok[0], resp.body

    return sub_resp


def getRows(session, artist=None, album=None, track=None):
    ar_row = None
    al_row = None
    tr_row = None

    # Least to most dependent
    if artist:
        ar_row = session.query(Artist).\
            filter(Artist.name == artist).all()
    if album:
        q = session.query(Album).\
            filter(Album.title == album)
        if ar_row:
            q = q.filter(Album.artist_id == ar_row[0].id)
        al_row = q.all()
    if track:
        q = session.query(Track).\
            filter(Track.title == track)
        if ar_row:
            q = q.filter(Track.artist_id == ar_row[0].id)
        if al_row:
            q = q.filter(Track.album_id == al_row[0].id)
        tr_row = q.all()

    return ar_row, al_row, tr_row
