import unittest
import transaction

from pyramid import testing

from . import RestTestCase
from ...models import DBSession
from ...views.rest.getartist import GetArtist

class TestArtist(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetArtist)
        cmd.req.params["id"] = "ar-1"
        ret = cmd()
        print ret
        print dir(ret)
        print ret.body
