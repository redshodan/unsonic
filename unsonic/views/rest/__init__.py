import os
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

    def getParams(self, req, defs):
        ret = []
        for param, default in defs:
            if param in req.params:
                ret.append(req.params[param])
            else:
                ret.append(default)
        return ret
    
    def getURL(self):
        return "/rest/%s%s" % (self.name, self.url_postfix)


def addCmd(cmd):
    commands[cmd.name] = cmd


### Utilities for wrangling data into xml form
def fillArtist(row):
    artist = ET.Element("artist")
    artist.set("id", str(row.id))
    artist.set("name", row.name)
    # FIXME
    artist.set("coverArt", "ar-%d" % row.id)
    return artist

def fillAlbum(row):
    album = ET.Element("album")
    album.set("id", str(row.id))
    album.set("name", row.title)
    # FIXME
    album.set("coverArt", "al-%d" % row.id)
    album.set("created",
              str(row.release_date) if row.release_date else "")
    if row.artist and row.artist.name:
        album.set("artist", row.artist.name)
    album.set("artistId", str(row.artist_id))
    return album

def fillSong(row):
    song = ET.Element("song")
    song.set("id", str(row.id))
    song.set("parent", str(row.album_id))
    song.set("title", row.title)
    song.set("isDir", "false")
    album_name = ""
    if row.album and row.album.title:
        album_name = row.album.title
    song.set("album", album_name)
    artist_name = ""
    if row.artist and row.artist.name:
        artist_name = row.artist.name
    song.set("artist", artist_name)
    if row.track_num:
        song.set("track", str(row.track_num))
    if row.album and row.album.release_date:
        song.set("year", row.album.release_date.strftime("%Y"))
    # FIXME
    song.set("genre", "rock")
    # FIXME
    if row.album_id:
        song.set("coverArt", ("al-%d" % row.album_id))
    song.set("size", str(row.size_bytes))
    # FIXME
    song.set("contentType", "audio/mpeg")
    suffix = os.path.basename(row.path).split(".")
    suffix = suffix[-1] if len(suffix) else None
    if suffix:
        song.set("suffix", suffix)
    song.set("duration", str(row.time_secs))
    # FIXME
    song.set("bitRate", "128")
    song.set("path", os.path.join(artist_name, album_name, row.title))
    return song
