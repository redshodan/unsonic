import unittest

from unsonic.views.rest.getindexes import GetIndexes
from . import buildCmd, checkResp


@unittest.skip("Fix the extra protocol bits")
def testBasic(session, ptesting):
    cmd = buildCmd(session, GetIndexes)
    sub_resp = checkResp(cmd.req, cmd())
    indexes = sub_resp.find("{http://subsonic.org/restapi}indexes")
    for index in indexes.iter("{http://subsonic.org/restapi}index"):
        index_name = index.get("name")
        for artist in index.iter("{http://subsonic.org/restapi}artist"):
            assert artist.get("id").startswith("ar-")
            assert len(artist.get("name")) > 0
            assert artist.get("name")[0].upper() == index_name
