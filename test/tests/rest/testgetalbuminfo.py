import pytest

from unsonic.views.rest import fillID
from unsonic.views.rest.getalbuminfo import GetAlbumInfo
from unsonic.views.rest.getalbuminfo2 import GetAlbumInfo2
from unsonic.models import Track
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[GetAlbumInfo, GetAlbumInfo2])
def album_info(request):
    yield request.param


def testGetAlbumInfo(session, album_info):
    row = session.query(Track).\
        filter_by(title="Harder, Better, Faster, Stronger").one_or_none()
    cmd = buildCmd(session, album_info, {"id": fillID(row)})
    checkResp(cmd.req, cmd(), ok504=True)
