from unsonic.views.rest.getchatmessages import GetChatMessages
from . import buildCmd, checkResp


# Empty command, since no messages implemented
def testGetChatMessages(session):
    cmd = buildCmd(session, GetChatMessages, {})
    checkResp(cmd.req, cmd())
