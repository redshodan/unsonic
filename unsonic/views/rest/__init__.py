import os, types
import xml.etree.ElementTree as ET

from ...version import VERSION, PROTOCOL_VERSION, UNSONIC_PROTOCOL_VERSION


XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

commands = {}


class MissingParam(Exception):
    pass

class NotFound(Exception):
    pass


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
    E_NOT_FOUND = ("70", "Requsted data not found")
    
    def __init__(self, req):
        self.req = req
        self.params = {}

    def __call__(self):
        try:
            self.parseParams()
            return self.handleReq()
        except MissingParam, e:
            return self.makeResp(status=(Command.E_MISSING_PARAM, str(e)))
        except NotFound, e:
            return self.makeResp(status=(Command.E_NOT_FOUND, str(e)))

    def handleReq(self):
        raise Exception("Command must implement handleReq()")
        
    def makeBody(self, attrs, child, status):
        body = ET.Element("subsonic-response")
        attrs_ = {"status":"ok" if status is True else "failed",
                  "version":PROTOCOL_VERSION, "unsonic":UNSONIC_PROTOCOL_VERSION}
        attrs_.update(attrs)
        for key, value in attrs_.iteritems():
            body.set(key, value)
        if status is not True and status is not False:
            error = ET.Element("error")
            if isinstance(status[0], types.TupleType):
                error.set("code", status[0][0])
                error.set("message", "%s: %s" % (status[0][1], status[1]))
            else:
                error.set("code", status[0])
                error.set("message", status[1])
            body.append(error)
        if child is not None:
            body.append(child)
        return XML_HEADER + ET.tostring(body)

    def makeResp(self, attrs={}, child=None, status=True, body=None):
        if body is None:
            body = self.makeBody(attrs, child, status)
        elif isinstance(body, ET.Element):
            body = XML_HEADER + ET.tostring(body)
        resp = self.req.response
        resp.body = body
        resp.content_type = "text/xml"
        resp.charset = "UTF-8"
        return resp

    def parseParams(self):
        for name, values in self.param_defs.iteritems():
            if name in self.req.params:
                val = self.req.params[name]
                if "type" in values:
                    val = values["type"](val)
                self.params[name] = val
                if "values" in values and val not in values["values"]:
                    raise MissingParam("Invalid type for param: %s" % name)
            else:
                if "default" in values:
                    self.params[name] = values["default"]
                else:
                    self.params[name] = None
                if "required" in values and values["required"]:
                    raise MissingParam(name)


def addCmd(cmd):
    commands[cmd.name] = cmd


### Param type check functions
def bool_t(value):
    if value in ["True", "true"]:
        return True
    elif value in ["False", "false"]:
        return False
    else:
        raise MissingParam("Invalid type")

def positive_t(value):
    val = int(value)
    if val < 0:
        raise MissingParam("Invalid number, can not be negative")
    else:
        return val
        
def artist_t(value):
    if not value.startswith("ar-"):
        raise MissingParam("Invalid id")
    return int(value[3:])

def album_t(value):
    if not value.startswith("al-"):
        raise MissingParam("Invalid id")
    return int(value[3:])

def track_t(value):
    if not value.startswith("tr-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


### Utilities for wrangling data into xml form
def fillArtist(row, name="artist"):
    artist = ET.Element(name)
    artist.set("id", "ar-%d" % row.id)
    artist.set("name", row.name)
    # FIXME
    artist.set("coverArt", "ar-%d" % row.id)
    return artist

def fillAlbum(row, name="album"):
    album = ET.Element(name)
    album.set("id", "al-%d" % row.id)
    album.set("name", row.title)
    # FIXME
    album.set("coverArt", "al-%d" % row.id)
    if row.release_date:
        release = []
        for c in row.release_date:
            if c.isdigit():
                release.append(c)
            else:
                break
        album.set("created", "".join(release))
    if row.artist and row.artist.name:
        album.set("artist", row.artist.name)
    album.set("artistId", "al-%d" % row.id)
    return album

def fillSong(row, name="song"):
    song = ET.Element(name)
    song.set("id", "tr-%d" % row.id)
    if row.album_id:
        song.set("parent", "al-%d" % row.album_id)
    else:
        song.set("parent", "UNKNOWN")
    song.set("title", row.title)
    song.set("isDir", "false")
    album_name = "-"
    if row.album and row.album.title:
        album_name = row.album.title
    song.set("album", album_name)
    artist_name = "-"
    if row.artist and row.artist.name:
        artist_name = row.artist.name
    song.set("artist", artist_name)
    if row.track_num:
        song.set("track", str(row.track_num))
    if row.album and row.album.release_date:
        year = []
        for c in row.album.release_date:
            if c.isdigit():
                year.append(c)
            else:
                break
        song.set("year", "".join(year))
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
