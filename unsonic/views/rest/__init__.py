# flake8: noqa: E402

import os
import traceback
import json
import xmltodict
import logging
from collections import OrderedDict
from datetime import datetime
import xml.etree.ElementTree as ET
import pylast

from pyramid.security import Allow, Authenticated, DENY_ALL

from eyed3.core import Date as Eyed3Date
from nicfit.console.ansi import Fg

from ...log import log
from ...version import PROTOCOL_VERSION, UNSONIC_PROTOCOL_VERSION
from ...models import (Session, ArtistRating, AlbumRating, TrackRating,
                       Artist, Album, Track, PlayList, Share, Bookmark,
                       InternetRadio)
from ...auth import Roles
from ... import lastfm


XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

commands = {}


class RouteContext(object):
    __acl__ = [(Allow, Authenticated, Roles.REST), DENY_ALL]

    def __init__(self, request):
        pass


# Exceptions
from .. import NotFound
from .. import NoPerm
from .. import InternalError


class MissingParam(Exception):
    pass


class Command(object):
    E_GENERIC = ("0", "An unknown error occurred")
    E_MISSING_PARAM = ("10", "Missing a required parameter")
    E_VER_CLIENT = ("20", "Incompatible Subsonic REST protocol version. " +
                          "Client must upgrade.")
    E_VER_SERVER = ("30", "Incompatible Subsonic REST protocol version. " +
                          "Server must upgrade.")
    E_AUTH = ("40", "Username or password incorrect")
    E_PERM = ("50", "Permission denied for this operation")
    # 60, trial period over, intentionally skipped, cause screw that noise.
    E_NOT_FOUND = ("70", "Requested data not found")
    E_LASTFM = ("0", "LastFM error")

    def __init__(self, route, req, session=None):
        self.req = req
        self.route = route
        self.params = {}
        # For testing
        self.session = session

    def __call__(self):
        try:
            self.parseParams()
            if hasattr(self, "dbsess"):
                if self.session:
                    return self.handleReq(self.session)
                else:
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
        except NoPerm as e:
            return self.makeResp(status=(Command.E_PERM, str(e)))
        except pylast.WSError as e:
            return self.makeResp(status=(Command.E_LASTFM, str(e)))
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise

    def handleReq(self, session=None):
        raise Exception("Command must implement handleReq()")

    def makeBody(self, attrs, child, status):
        body = ET.Element("subsonic-response")
        attrs_ = {"status": "ok" if status is True else "failed",
                  "xmlns": "http://subsonic.org/restapi",
                  "version": PROTOCOL_VERSION,
                  "unsonic": UNSONIC_PROTOCOL_VERSION}
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

    def toDict(self, body):
        root = xmltodict.parse(body, attr_prefix="")

        def walker(d):
            if not isinstance(d, list) and not isinstance(d, OrderedDict):
                return
            for key, val in d.items():
                if isinstance(val, list):
                    for val2 in val:
                        walker(val2)
                elif isinstance(val, OrderedDict):
                    walker(val)
                elif val is None:
                    d[key] = OrderedDict()
                elif val == "false":
                    d[key] = False
                elif val == "true":
                    d[key] = True

        walker(root)
        return root

    def makeResp(self, attrs=None, child=None, status=True, body=None):
        attrs = attrs or {}
        if body is None:
            body = self.makeBody(attrs, child, status)
        elif isinstance(body, ET.Element):
            body = "%s%s" % (XML_HEADER, ET.tostring(body).decode("utf-8"))
        resp = self.req.response
        pretty = None
        if "f" in self.req.params:
            if self.req.params["f"] == "jsonp" and "callback" in self.req.params:
                dct = self.toDict(body)
                if log.isEnabledFor(logging.DEBUG):
                    pretty = "%s(%s)" % (self.req.params["callback"],
                                         json.dumps(dct, indent=3))
                else:
                    pretty = body
                txt = "%s(%s)" % (self.req.params["callback"], json.dumps(dct))
                resp.text = txt
                resp.content_type = "application/javascript"
            elif self.req.params["f"] == "json":
                dct = self.toDict(body)
                if log.isEnabledFor(logging.DEBUG):
                    pretty = json.dumps(dct, indent=3)
                else:
                    pretty = body
                resp.text = json.dumps(dct)
                resp.content_type = "application/json"
        if not pretty:
            pretty = body
            resp.text = body
            resp.content_type = "text/xml"
        resp.charset = "UTF-8"
        log.info("Response(%s): %s" % (self.name, Fg.blue(pretty)))
        return resp

    def makeBinaryResp(self, binary, mimetype, md5=None):
        resp = self.req.response
        resp.content_type = mimetype
        if md5:
            resp.content_md5 = md5
        resp.body = binary
        return resp

    def parseParams(self):
        mparams = self.req.params.mixed()
        for name, values in self.param_defs.items():
            if name in mparams:
                val = mparams[name]
                if "type" in values:
                    if "multi" in values:
                        if not isinstance(val, list):
                            val = [val]
                        lval = []
                        for v in val:
                            lval.append(values["type"](v))
                        val = lval
                    else:
                        # Be permissive about other protocol, but don't
                        # let it dork us up
                        if isinstance(val, list):
                            val = val[0]
                        val = values["type"](val)
                self.params[name] = val
                if "values" in values and val not in values["values"]:
                    raise MissingParam("Invalid type for param: %s" % name)
            else:
                if "default" in values:
                    self.params[name] = values["default"]
                else:
                    if "multi" in values:
                        self.params[name] = []
                    else:
                        self.params[name] = None
                if "required" in values and values["required"]:
                    raise MissingParam(name)


def registerCmd(cmd):
    commands[cmd.name] = cmd
    return cmd


def getArtworkByID(session, id, lf_client=None):
    from ...config import CONFIG

    num = int(id[3:])
    image = None
    lf_artist = None
    lf_album = None

    if id.startswith("tr-"):
        track = session.query(Track).filter_by(id=num).one_or_none()
        lf_artist = track.artist.name
        if track.album:
            lf_album = track.album.title
            if track.album.images:
                image = track.album.images[0]
    elif id.startswith("al-"):
        album = session.query(Album).filter_by(id=num).one_or_none()
        lf_artist = album.artist.name
        lf_album = album.title
        if album.images:
            image = album.images[0]
    elif id.startswith("ar-"):
        artist = session.query(Artist).filter_by(id=num).one_or_none()
        lf_artist = album.artist.name
        if artist.images:
            image = artist.images[0]

    # DB only
    if CONFIG.getDbValue(session, key="art.never_lastfm").value:
        if image:
            return image.data, image.mime_type
        else:
            return None, None

    # Prefer local over LastFM
    if not CONFIG.getDbValue(session, key="art.prefer_lastfm").value:
        if image:
            return image.data, image.mime_type

    # LastFM image lookup
    if not lf_client:
        lf_client = lastfm.getSystemClient()
    if lf_album:
        ret = lf_client.get_album(lf_artist, lf_album)
    else:
        ret = lf_client.get_artist(lf_artist)
    image_url = ret.get_cover_image(pylast.SIZE_EXTRA_LARGE)

    # Get it
    if image_url:
        return lastfm.getImage(lf_client, image_url)

    return None, None


# Param type check functions
def str_t(value):
    if not value or not len(value):
        raise MissingParam("Missing string parameter")
    return value


def int_t(value):
    try:
        return int(value)
    except ValueError:
        raise MissingParam("Invalid number parameter")


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


def share_t(value):
    if not value.startswith("sh-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


def bookmark_t(value):
    if not value.startswith("bm-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


def iradio_t(value):
    if not value.startswith("ir-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


def folder_t(value):
    if not value.startswith("fl-"):
        raise MissingParam("Invalid id")
    return int(value[3:])


def datetime_t(tstamp):
    try:
        return datetime.utcfromtimestamp(int(tstamp) / 1000)
    except Exception:
        raise MissingParam(
            "Invalid type for param. '%s' is not a timestamp" % tstamp)


def year_t(year):
    try:
        return Eyed3Date(int(year), 1, 1)
    except Exception:
        raise MissingParam("Invalid type for param. '%s' is not a year" % year)


def bitrate_t(value):
    try:
        i = int(value)
    except ValueError:
        raise MissingParam("Invalid type for param. '%s' is not a number" %
                           value)
    if i in [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]:
        return i
    else:
        raise MissingParam("Invalid value for param. '%s' is not allowed" %
                           value)


def strDate(d):
    if d is None:
        return ""
    elif isinstance(d, Eyed3Date):
        return datetime(d.year if d.year else 0,
                        d.month if d.month else 0,
                        d.day if d.day else 0,
                        d.hour if d.hour else 0,
                        d.minute if d.minute else 0,
                        d.second if d.second else 0).isoformat()
    else:
        return d.isoformat()


# Utilities for wrangling data into xml form
def fillID(row):
    if isinstance(row, Artist):
        return f"ar-{row.id}"
    elif isinstance(row, Album):
        return f"al-{row.id}"
    elif isinstance(row, Track):
        return f"tr-{row.id}"
    elif isinstance(row, PlayList):
        return f"pl-{row.id}"
    elif isinstance(row, Share):
        return f"sh-{row.id}"
    elif isinstance(row, Bookmark):
        return f"bm-{row.id}"
    elif isinstance(row, InternetRadio):
        return f"ir-{row.id}"
    else:
        raise MissingParam(f"Unknown ID type: {type(row)}")


def fillCoverArt(session, row, elem, name):
    if row.images is not None and len(row.images) > 0:
        elem.set("coverArt", "%s-%d" % (name, row.images[0].id))
        for art in row.images:
            sub = ET.Element("cover-art")
            sub.text = "%s-%d" % (name, art.id)
            elem.append(sub)


def fillArtist(session, row, name="artist"):
    assert isinstance(row, Artist)
    artist = ET.Element(name)
    artist.set("id", fillID(row))
    artist.set("name", row.name)
    fillCoverArt(session, row, artist, "ar")
    return artist


def fillArtistUser(session, artist_row, rating_row, user, name="artist"):
    artist = fillArtist(session, artist_row, name=name)
    if not rating_row:
        rating_row = session.query(ArtistRating).\
            filter(ArtistRating.artist_id == artist_row.id,
                   ArtistRating.user_id == user.id).\
            one_or_none()
    if rating_row and rating_row.starred:
        artist.set("starred", rating_row.starred.isoformat())
    return artist


def fillAlbum(session, row, name="album"):
    assert isinstance(row, Album)
    album = ET.Element(name)
    album.set("id", fillID(row))
    album.set("album", row.title)
    album.set("title", row.title)
    album.set("isDir", "true")
    if row.artist:
        album.set("parent", "ar-%s" % row.artist.id)
    else:
        album.set("parent", "UNKNOWN")
    fillCoverArt(session, row, album, "al")
    if row.date_added:
        album.set("created", strDate(row.date_added))
    if row.artist and row.artist.name:
        album.set("artist", row.artist.name)
        album.set("artistId", "ar-%d" % row.artist.id)
    return album


def fillAlbumUser(session, album_row, rating_row, user, name="album"):
    album = fillAlbum(session, album_row, name=name)
    if not rating_row:
        rating_row = session.query(AlbumRating).\
            filter(AlbumRating.album_id == album_row.id,
                   AlbumRating.user_id == user.id).one_or_none()
    if rating_row and rating_row.starred and not rating_row.pseudo_starred:
        album.set("starred", rating_row.starred.isoformat())
    return album


def fillAlbumID3(session, row, user, append_tracks):
    assert isinstance(row, Album)
    album = ET.Element("album")
    album.set("id", fillID(row))
    album.set("name", row.title)
    fillCoverArt(session, row, album, "al")
    if row.date_added:
        album.set("created", strDate(row.date_added))
    if row.artist and row.artist.name:
        album.set("artist", row.artist.name)
        album.set("artistId", "ar-%d" % row.artist.id)
    if row.getBestDate():
        album.set("year", str(row.getBestDate().year))
    # TODO: what if more than one tag/genre? What to prefer?
    if len(row.tags):
        album.set("genre", row.tags[0].name)
    track_count = 0
    duration = 0
    for row in session.query(Track)           \
            .filter(Track.album_id == row.id) \
            .order_by(Track.media_num, Track.track_num).all():
        track_count += 1
        duration = duration + row.time_secs
        if append_tracks:
            track = fillTrackUser(session, row, None, user)
            album.append(track)
    album.set("songCount", str(track_count))
    album.set("duration", str(duration))
    return album


def fillTrack(session, row, name="song"):
    assert isinstance(row, Track)
    song = ET.Element(name)
    song.set("id", fillID(row))
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
    if row.album and row.album.getBestDate():
        song.set("year", str(row.album.getBestDate().year))
    # TODO: what if more than one tag/genre? What to prefer?
    if len(row.tags):
        song.set("genre", row.tags[0].name)
    if row.album is not None:
        fillCoverArt(session, row.album, song, "al")
    if row.media_num:
        song.set("discNumber", str(row.media_num))
    else:
        song.set("discNumber", "1")
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


def fillTrackUser(session, song_row, rating_row, user, name="song"):
    song = fillTrack(session, song_row, name=name)
    if not rating_row:
        rating_row = session.query(TrackRating).\
            filter(TrackRating.track_id == song_row.id,
                   TrackRating.user_id == user.id).one_or_none()
    if rating_row and rating_row.starred:
        song.set("starred", rating_row.starred.isoformat())
    return song


def fillPlayList(session, row):
    assert isinstance(row, PlayList)
    playlist = ET.Element("playlist")
    playlist.set("id", fillID(row))
    playlist.set("name", row.name)
    playlist.set("comment", row.comment if row.comment else "")
    playlist.set("owner", row.owner.name)
    playlist.set("public", "true" if row.public else "false")
    playlist.set("created", row.created.isoformat())
    playlist.set("changed", row.changed.isoformat())
    # FIXME: Join/walk the artist/album/track for art
    fillCoverArt(session, row, playlist, "pl")

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


def fillUser(session, row):
    user = ET.Element("user")
    user.set("username", row.name)
    user.set("email", row.email if row.email else "")
    # FIXME: fix this in the scrobbling branch
    user.set("scrobblingEnabled", "true" if row.scrobble_type else "false")
    for role in Roles.subsonic_roles:
        user.set("%sRole" % role,
                 "true" if role in row.roles else "false")
    return user


def fillShare(session, req, row):
    share = ET.Element("share")
    share.set("id", fillID(row))
    share.set("url", f"{req.path_url.rstrip(req.path)}/shares/{row.uuid}")
    share.set("description", row.description if row.description else "")
    share.set("username", row.user.name)
    share.set("created", strDate(row.created))
    share.set("lastVisited", strDate(row.last_visited))
    if row.expires:
        share.set("expires", strDate(row.expires))
    else:
        # Arbitrarily far date stand in for no expiration
        share.set("expires", "3000-01-01T00:00:00")
    share.set("visitCount", str(row.visit_count))
    for entry in row.entries:
        if entry.album_id:
            share.append(fillAlbum(session, entry.album, "entry"))
        elif entry.track_id:
            share.append(fillTrack(session, entry.track, "entry"))
        elif entry.playlist_id:
            for track in entry.playlist.tracks:
                share.append(fillTrack(session, track, "entry"))

    return share


def fillBookmark(session, row):
    bm = ET.Element("bookmark")
    bm.set("position", str(row.position))
    bm.set("username", row.user.name)
    bm.set("comment", row.comment if row.comment else "")
    bm.set("created", strDate(row.created))
    bm.set("changed", strDate(row.changed))
    bm.append(fillTrack(session, row.track, "entry"))
    return bm


def fillInternetRadio(session, row):
    ir = ET.Element("internetRadioStation")
    ir.set("id", fillID(row))
    ir.set("name", row.name)
    ir.set("streamUrl", row.stream_url)
    ir.set("homepageUrl", row.homepage_url if row.homepage_url else "")
    return ir
