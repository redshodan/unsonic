import unittest

from pyramid import testing

from . import RestTestCase
from ...models import Session
from ...views.rest.addchatmessage import AddChatMessage
from ...views.rest import Command


class TestAddChatMessage(RestTestCase):
    def testAddChatMessage(self):
        cmd = self.buildCmd(AddChatMessage, {"message": "ignore me!"})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
