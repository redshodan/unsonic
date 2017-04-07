from unsonic.views.rest.getlicense import GetLicense
from . import buildCmd, checkResp


def testBasic(session, ptesting):
    cmd = buildCmd(session, GetLicense)
    sub_resp = checkResp(cmd.req, cmd())
    license = sub_resp.find("{http://subsonic.org/restapi}license")
    assert len(license.get("licenseExpires")) > 0
    assert license.get("email") == "foo@bar.com"
    assert license.get("valid") == "true"
