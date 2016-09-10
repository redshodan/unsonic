import os, types, json, xmltodict
import xml.etree.ElementTree as ET

from pyramid.security import Allow, Authenticated, DENY_ALL

from ...log import log
from ...version import VERSION, PROTOCOL_VERSION, UNSONIC_PROTOCOL_VERSION
from ...models import Session, Roles, ArtistRating, AlbumRating, TrackRating


XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

commands = {}


class RouteContext(object):
    __acl__ = [ (Allow, Authenticated, Roles.REST), DENY_ALL ]
    
    def __init__(self, request):
        pass

class MissingParam(Exception):
    pass

class NotFound(Exception):
    pass

class InternalError(Exception):
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
            if hasattr(self, "dbsess"):
                with Session() as session:
                    return self.handleReq(session)
            else:
                return self.handleReq()
        except MissingParam as e:
            return self.makeResp(status=(Command.E_MISSING_PARAM, str(e)))
        except NotFound as e:
            return self.makeResp(status=(Command.E_NOT_FOUND, str(e)))
        except InternalError as e:
            return self.makeResp(status=(Command.E_GENERIC, str(e)))

    def handleReq(self, session=None):
        raise Exception("Command must implement handleReq()")
        
    def makeBody(self, attrs, child, status):
        body = ET.Element("subsonic-response")
        attrs_ = {"status":"ok" if status is True else "failed",
                  "version":PROTOCOL_VERSION, "unsonic":UNSONIC_PROTOCOL_VERSION}
        attrs_.update(attrs)
        for key, value in attrs_.items():
            body.set(key, value)
        if status is not True and status is not False:
            error = ET.Element("error")
            if isinstance(status[0], tuple):
                error.set("code", status[0][0])
                error.set("message", "%s: %s" % (status[0][1], status[1]))
            else:
                error.set("code", status[0])
                error.set("message", status[1])
            body.append(error)
        if child is not None:
            body.append(child)
        return "%s%s\n" % (XML_HEADER, ET.tostring(body).decode("utf-8"))


    def makeResp(self, attrs={}, child=None, status=True, body=None):
        if body is None:
            body = self.makeBody(attrs, child, status)
        elif isinstance(body, ET.Element):
            body = "%s%s" % (XML_HEADER, ET.tostring(body).decode("utf-8"))
        resp = self.req.response
        if "f" in self.req.params:
            if self.req.params["f"] == "jsonp" and "callback" in self.req.params:
                body = xmltodict.parse(body)
                txt = "%s(%s)" % (self.req.params["callback"], json.dumps(body))
                resp.text = txt
                resp.content_type = "application/javascript"
            elif self.req.params["f"] == "json":
                body = xmltodict.parse(body)
                resp.text = json.dumps(body)
                resp.content_type = "application/json"
        else:
            resp.text = body
            resp.content_type = "text/xml"
        resp.charset = "UTF-8"
        log.debug("Response(%s): %s" % (self.name, resp.body.decode("utf-8")))
        return resp

    def parseParams(self):
        for name, values in self.param_defs.items():
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
        
def playable_id_t(value):
    for prefix in ["ar-", "al-", "tr-"]:
        if value.startswith(prefix):
            break
    else:
        raise MissingParam("Invalid id")
    return value

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

def playlist_t(value):
    if not value.startswith("pl-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


### Utilities for wrangling data into xml form
def fillCoverArt(session, row, elem, name):
    if row.images is not None and len(row.images) > 0:
        elem.set("coverArt", "%s-%d" % (name, row.images[0].id))
        for art in row.images:
            sub = ET.Element("cover-art")
            sub.text = "%s-%d" % (name, art.id)
            elem.append(sub)

def fillArtist(session, row, name="artist"):
    artist = ET.Element(name)
    artist.set("id", "ar-%d" % row.id)
    artist.set("name", row.name)
    fillCoverArt(session, row, artist, "ar")
    return artist

def fillArtistUser(session, row, user, name="artist"):
    artist = fillArtist(session, row, name=name)
    rating = ArtistRating.get(session, row.id, user.id)
    if rating and rating.starred:
        artist.set("starred", rating.starred.isoformat())
    return artist

def fillAlbum(session, row, name="album"):
    album = ET.Element(name)
    album.set("id", "al-%d" % row.id)
    album.set("name", row.title)
    album.set("album", row.title)
    album.set("title", row.title)
    album.set("isDir", "true")
    if row.artist:
        album.set("parent", "ar-%s" % row.artist.id)
    fillCoverArt(session, row, album, "al")
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

def fillAlbumUser(session, row, user, name="album"):
    album = fillAlbum(session, row, name=name)
    rating = AlbumRating.get(session, row.id, user.id)
    if rating and rating.starred and not rating.pseudo_starred:
        album.set("starred", rating.starred.isoformat())
    return album

def fillSong(session, row, name="song"):
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
    # if row.genre_id is not None:
    #     song.set("genre", row.genre.name)
    if row.album is not None:
        fillCoverArt(session, row.album, song, "al")
    song.set("size", str(row.size_bytes))
    # FIXME
    song.set("contentType", "audio/mpeg")
    song.set("transcodedContentType", "audio/mpeg")
    suffix = os.path.basename(row.path).split(".")
    suffix = suffix[-1] if len(suffix) else None
    if not suffix:
        suffix = "mp3"
    song.set("suffix", suffix)
    song.set("transcodedSuffix", suffix)
    song.set("duration", str(row.time_secs))
    song.set("bitRate", str(row.bit_rate))
    song.set("path", os.path.join(artist_name, album_name, row.title))
    song.set("isVideo", "false")
    return song

def fillSongUser(session, row, user, name="song"):
    song = fillSong(session, row, name=name)
    rating = TrackRating.get(session, row.id, user.id)
    if rating and rating.starred:
        song.set("starred", rating.starred.isoformat())
    return song

def fillPlayList(session, row):
    playlist = ET.Element("playlist")
    playlist.set("id", "pl-%d" % row.id)
    playlist.set("name", row.name)
    playlist.set("comment", row.comment if row.comment else "")
    playlist.set("owner", row.owner.name)
    playlist.set("public", "true" if row.public else "false")
    playlist.set("created", row.created.isoformat())

    count = 0
    duration = 0
    for trow in row.tracks:
        count += 1
        duration += trow.track.time_secs
        playlist.set("songCount", str(count))
        playlist.set("duration", str(duration))
            
    for urow in row.users:
        auser = ET.Element("allowedUser")
        auser.text = urow.user.name
        playlist.append(auser)

    return playlist
