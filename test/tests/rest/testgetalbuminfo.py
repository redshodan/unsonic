import pytest

from unsonic.views.rest.getalbuminfo import GetAlbumInfo
from unsonic.views.rest.getalbuminfo2 import GetAlbumInfo2
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[GetAlbumInfo, GetAlbumInfo2])
def album_info(request):
    yield request.param


def testGetAlbumInfo(session, album_info):
    cmd = buildCmd(session, album_info, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
