import pytest

from unsonic.views.rest.search2 import Search2
from unsonic.views.rest.search3 import Search3
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[Search2, Search3])
def search(request):
    yield request.param


@pytest.fixture(
    scope="function",
    # Passed as kwargs to check()
    params=[
        {"query": 'artist:"artist 1"', "tagname": "artist",
         "artist": "artist 1"},
        {"query": 'album:"album 1"', "tagname": "album", "album": "album 1"},
        {"query": 'title:"song 1"', "tagname": "song", "track": "song 1"},
        {"query": 'artist:"artist 2" AND album:"album 2"',
         "tagname": "album", "artist": "artist 2", "album": "album 2"},
        {"query": 'artist:"artist 2" AND album:"album 2" AND title:"song 3"',
         "tagname": "song", "artist": "artist 2", "album": "album 2",
         "track": "song 3"},
        {"query": 'artist:"artist 1" AND album:"album 1" AND track:"song 3"',
         "tagname": "song", "artist": "artist 1", "album": "album 1",
         "track": "song 3"},
        {"query":
         'artist:"artist 404" AND track:"song 3" OR ' +
         'artist:"Artist 1" AND track:"song 3"',
         "tagname": "song", "artist": "artist 1", "album": "album 1",
         "track": "song 3"},
        {"query":
         '(artist:"artist 404" AND track:"song 3") OR ' +
         '(artist:"Artist 1" AND track:"song 3")',
         "tagname": "song", "artist": "artist 1", "album": "album 1",
         "track": "song 3"},

        # FIXME: Teach check() to handle/check multiple results
        # {"query":
        #  '(artist:"artist 404" AND track:"song 3") OR title:"song 3"',
        #  "tagname": "song", "artist": "artist 1", "album": "album 1",
        #  "track": "song 3"},
        # {"query": '"song 3"',
        #  "tagname": "song", "artist": "artist 1", "album": "album 1",
        #  "track": "song 3"},
        # {"query":
        #  '(artist:"artist 404" AND track:"song 3") OR "song 3"',
        #  "tagname": "song", "artist": "artist 1", "album": "album 1",
        #  "track": "song 3"},
    ])
def query(request):
    yield request.param


def check(search, resp, query=None, tagname=None, artist=None, album=None,
          track=None):
    if search is Search2:
        result = resp.find("{http://subsonic.org/restapi}searchResult2")
    else:
        result = resp.find("{http://subsonic.org/restapi}searchResult3")
    tag = result.find("{http://subsonic.org/restapi}" + tagname)
    if artist:
        if tagname == "artist":
            assert tag.get("name") == artist
        else:
            assert tag.get("artist") == artist
    if album:
        if tagname == "album":
            if search is Search2:
                assert tag.get("title") == album
            else:
                assert tag.get("name") == album
        else:
            assert tag.get("album") == album
    if track:
        assert tag.get("title") == track


def testSearch(session, search, query):
    cmd = buildCmd(session, search, {"query": query["query"]})
    resp = checkResp(cmd.req, cmd())
    check(search, resp, **query)
