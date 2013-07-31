import xml.etree.ElementTree as ET

import unsonic


PROTOCOL_VERSION = "1.10.0"
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

commands = {}


class Command(object):
    def __init__(self, name, url_postfix=".view"):
        self.name = name
        self.url_postfix = url_postfix

    def handleReq(self, req):
        raise Exception("Command must implement handleReq()")
        
    def makeBody(self, attrs, child, status):
        body = ET.Element("subsonic-response")
        attrs_ = {"status":"ok" if status else "failed",
                  "version":PROTOCOL_VERSION}
        attrs_.update(attrs)
        for key, value in attrs_.iteritems():
            body.set(key, value)
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
