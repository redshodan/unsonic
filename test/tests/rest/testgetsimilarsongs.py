import pytest

from unsonic.views.rest.getsimilarsongs import GetSimilarSongs
from unsonic.views.rest.getsimilarsongs2 import GetSimilarSongs2
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[GetSimilarSongs, GetSimilarSongs2])
def similar(request):
    yield request.param


def testGetSimilarSongs(session, similar):
    cmd = buildCmd(session, similar, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
