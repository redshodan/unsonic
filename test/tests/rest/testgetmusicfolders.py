from unsonic.views.rest.getmusicfolders import GetMusicFolders
from . import buildCmd, checkResp


def testBasic(session):
    cmd = buildCmd(session, GetMusicFolders)
    sub_resp = checkResp(cmd.req, cmd())
    folders = sub_resp.find("{http://subsonic.org/restapi}musicFolders")
    for folder in folders.iter("{http://subsonic.org/restapi}musicFolder"):
        assert folder.get("id").startswith("fl-")
        assert len(folder.get("name")) > 0
