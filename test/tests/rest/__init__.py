import subprocess
import xml.etree.ElementTree as ET

from webob.multidict import MultiDict, NestedMultiDict
from pyramid import testing

from unsonic import models


def buildCmd(session, klass, params={}, username="test"):
    request = testing.DummyRequest()
    request.context = testing.DummyResource()
    md = MultiDict()
    for key, val in params.items():
        md.add(key, val)
    request.params = NestedMultiDict(md)
    request.authed_user = models.getUserByName(session, username)
    request.user_agent = "Test/1.0 (X11; Linux x86_64) Test/1.0 Test/1.0"
    cmd = klass(None, request, session=session)
    cmd.settings = {"mishmash.paths": "Music: test/music"}
    return cmd


def checkResp(req, resp, ok=True):
    sub_resp = ET.fromstring(resp.body)

    # Validate the response against the XSD
    p = subprocess.Popen(["xmllint", "--format", "--schema",
                          "test/xsd/unsonic-subsonic-api.xsd", "-"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, err = p.communicate(resp.body, timeout=15)
    if p.returncode:
        assert 0, out.decode("utf-8")

    # Validate the return type
    if ok is True:
        assert sub_resp.get("status") == "ok", resp.body
    else:
        assert sub_resp.get("status") == "failed", resp.body
        error = sub_resp.find("{http://subsonic.org/restapi}error")
        assert error.get("code") == ok[0], resp.body

    return sub_resp
