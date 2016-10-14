import unittest

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.ping import Ping
from ...views.rest import Command


class TestPing(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(Ping)
        resp = cmd()
        self.checkResp(cmd.req, resp)
