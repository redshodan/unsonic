import pytest

from unsonic.views.rest.search2 import Search2
from unsonic.views.rest.search3 import Search3
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[Search2, Search3])
def search(request):
    yield request.param


def testSearch(session, search):
    cmd = buildCmd(session, search, {"query": "song 1"})
    resp = checkResp(cmd.req, cmd())
    if search == Search2:
        res_name = "searchResult2"
    else:
        res_name = "searchResult3"
    result = resp.find("{http://subsonic.org/restapi}" + res_name)
    track = result.find("{http://subsonic.org/restapi}song")
    assert track.get("title") == "song 1"
