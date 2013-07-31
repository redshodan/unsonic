import xml.etree.ElementTree as ET

from ...version import VERSION


PROTOCOL_VERSION = "1.10.0"
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

commands = {}


class Command(object):
    E_GENERIC = ("0", "An unknown error occured")
    E_MISSING_PARAM = ("10", "Missing a required parameter")
    E_VER_CLIENT = ("20", "Incompatible Subsonic REST protocol version. " +
                          "Client must upgrade.")
    E_VER_SERVER = ("30", "Incompatible Subsonic REST protocol version. " +
                          "Server must upgrade.")
    E_AUTH = ("40", "Username or password incorrect")
    E_PERM = ("50", "Permission denied for this operation")
    # 60, trial period over, intentionally skipped, cause screw that noise.
    E_NOT_FOUND = ("60", "Requsted data not found")
    
    def __init__(self, name, url_postfix=".view"):
        self.name = name
        self.url_postfix = url_postfix

    def handleReq(self, req):
        raise Exception("Command must implement handleReq()")
        
    def makeBody(self, attrs, child, status):
        body = ET.Element("subsonic-response")
        attrs_ = {"status":"ok" if status is True else "failed",
                  "version":PROTOCOL_VERSION, "unsonic":VERSION}
        attrs_.update(attrs)
        for key, value in attrs_.iteritems():
            body.set(key, value)
        if status is not True and status is not False:
            error = ET.Element("error")
            error.set("code", status[0])
            error.set("message", status[1])
            body.append(error)
        if child is not None:
            body.append(child)
        return XML_HEADER + ET.tostring(body)

    def makeResp(self, req, attrs={}, child=None, status=True, body=None):
        if body is None:
            body = self.makeBody(attrs, child, status)
        elif isinstance(body, ET.Element):
            body = XML_HEADER + ET.tostring(body)
        resp = req.response
        resp.body = body
        resp.content_type = "text/xml"
        resp.charset = "UTF-8"
        return resp

    def getURL(self):
        return "/rest/%s%s" % (self.name, self.url_postfix)


def addCmd(cmd):
    commands[cmd.name] = cmd


from . import ping, getlicense
