from . import RestTestCase
from unsonic.views.rest.addchatmessage import AddChatMessage


class TestAddChatMessage(RestTestCase):
    def testAddChatMessage(self):
        cmd = self.buildCmd(AddChatMessage, {"message": "ignore me!"})
        resp = cmd()
        self.checkResp(cmd.req, resp)
