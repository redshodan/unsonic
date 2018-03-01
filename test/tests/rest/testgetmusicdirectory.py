import unittest

from unsonic.views.rest.getmusicdirectory import GetMusicDirectory
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testArtistOneAlbum(session):
    aid = "ar-4"
    cmd = buildCmd(session, GetMusicDirectory, {"id": aid})
    sub_resp = checkResp(cmd.req, cmd())
    directory = sub_resp.find("{http://subsonic.org/restapi}directory")
    assert directory.get("id") == aid
    assert len(directory.get("name")) > 0
    assert directory.get("parent") == "fl-2"
    for child in directory.iter("{http://subsonic.org/restapi}child"):
        assert child.get("id").startswith("al-")
        assert len(child.get("title")) > 0
        assert len(child.get("artist")) > 0
        assert child.get("isDir") == "true"
        assert child.get("parent") == directory.get("id")


@unittest.skip("Find better way to map db items")
def testArtistNoAlbums(session):
    aid = "ar-2"
    cmd = buildCmd(session, GetMusicDirectory, {"id": aid})
    sub_resp = checkResp(cmd.req, cmd())
    directory = sub_resp.find("{http://subsonic.org/restapi}directory")
    assert directory.get("id") == aid
    assert len(directory.get("name")) > 0
    assert directory.get("parent") == "fl-2"
    child = directory.find("{http://subsonic.org/restapi}child")
    assert child.get("album") == "-"
    assert child.get("id").startswith("tr-")


@unittest.skip("Find better way to map db items")
def testAlbum(session):
    aid = "al-3"
    cmd = buildCmd(session, GetMusicDirectory, {"id": aid})
    sub_resp = checkResp(cmd.req, cmd())
    directory = sub_resp.find("{http://subsonic.org/restapi}directory")
    assert directory.get("id") == aid
    assert len(directory.get("name")) > 0
    assert directory.get("parent").startswith("ar-")
    for child in directory.iter("{http://subsonic.org/restapi}child"):
        assert child.get("id").startswith("tr-")
        assert len(child.get("title")) > 0
        assert len(child.get("artist")) > 0
        assert len(child.get("album")) > 0
        assert child.get("coverArt") == aid
        assert child.get("isDir") == "false"
        assert child.get("parent") == directory.get("id")


def testArtistNotFound(session):
    cmd = buildCmd(session, GetMusicDirectory, {"id": "ar-1000000000000"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testAlbumNotFound(session):
    cmd = buildCmd(session, GetMusicDirectory, {"id": "ar-1000000000000"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testBadID(session):
    cmd = buildCmd(session, GetMusicDirectory, {"id": "foobar"})
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)


def testNoID(session):
    cmd = buildCmd(session, GetMusicDirectory)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
