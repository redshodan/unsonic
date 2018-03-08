from unsonic.views.rest.getartists import GetArtists
from . import buildCmd, checkResp


def testBasic(session):
    cmd = buildCmd(session, GetArtists)
    sub_resp = checkResp(cmd.req, cmd())
    artists = sub_resp.find("{http://subsonic.org/restapi}artists")
    for index in artists.iter("{http://subsonic.org/restapi}index"):
        index_name = index.get("name")
        for artist in index.iter("{http://subsonic.org/restapi}artist"):
            assert artist.get("id").startswith("ar-")
            assert len(artist.get("name")) > 0
            assert artist.get("name")[0].upper() == index_name
            assert int(artist.get("albumCount")) >= 0
