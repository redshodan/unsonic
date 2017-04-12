from unsonic.views.rest.addchatmessage import AddChatMessage
from . import buildCmd, checkResp


def testAddChatMessage(session, ptesting):
    cmd = buildCmd(session, AddChatMessage, {"message": "ignore me!"})
    checkResp(cmd.req, cmd())
