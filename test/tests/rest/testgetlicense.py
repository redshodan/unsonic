from . import RestTestCase
from unsonic.views.rest.getlicense import GetLicense


class TestLicense(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetLicense)
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        license = sub_resp.find("{http://subsonic.org/restapi}license")
        self.assertTrue(len(license.get("licenseExpires")) > 0)
        self.assertEqual(license.get("email"), "foo@bar.com")
        self.assertEqual(license.get("valid"), "true")
