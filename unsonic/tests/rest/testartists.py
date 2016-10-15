import unittest

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.getartists import GetArtists
from ...views.rest import Command


class TestArtists(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetArtists)
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        artists = sub_resp.find("{http://subsonic.org/restapi}artists")
        for index in artists.iter("{http://subsonic.org/restapi}index"):
            index_name = index.get("name")
            for artist in index.iter("{http://subsonic.org/restapi}artist"):
                self.assertTrue(artist.get("id").startswith("ar-"))
                self.assertTrue(len(artist.get("name")) > 0)
                self.assertEqual(artist.get("name")[0].upper(), index_name)
                self.assertTrue(int(artist.get("albumCount")) >= 0)
