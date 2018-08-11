from unsonic.views.rest.getrandomsongs import GetRandomSongs
from . import buildCmd, checkResp


def validate(cmd, resp):
    sub_resp = checkResp(cmd.req, resp)
    songs = sub_resp.find("{http://subsonic.org/restapi}randomSongs")
    count = 0
    titles = []
    for song in songs.iter("{http://subsonic.org/restapi}song"):
        count += 1
        titles.append(song.get("title"))
        assert song.get("id").startswith("tr-")
        assert int(song.get("id")[3:]) > 0
        assert int(song.get("duration")) >= 0
        assert int(song.get("bitRate")) >= 0
    return count, titles


def testGetRandomSongs(session):
    cmd = buildCmd(session, GetRandomSongs)
    count, titles = validate(cmd, cmd())
    assert count == 10


def testGetRandomSongsSized(session):
    cmd = buildCmd(session, GetRandomSongs, {"size": "2"})
    count, titles = validate(cmd, cmd())
    assert count == 2


def testGetRandomSongs2Libs(session):
    cmd = buildCmd(session, GetRandomSongs, {"genre": "techno"})
    count, titles = validate(cmd, cmd())
    assert count == 5
