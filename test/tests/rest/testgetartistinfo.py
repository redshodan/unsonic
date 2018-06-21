import pytest

from unsonic.views.rest.getartistinfo import GetArtistInfo
from unsonic.views.rest.getartistinfo2 import GetArtistInfo2
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[GetArtistInfo, GetArtistInfo2])
def artist_info(request):
    yield request.param


def testGetArtistInfo(session, artist_info):
    cmd = buildCmd(session, artist_info, {"id": "ar-1"})
    checkResp(cmd.req, cmd())
